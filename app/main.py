import os, json, gzip, time, pathlib, logging, uuid
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
from .settings import settings
from .logging_conf import configure_logging
from .models import IngestPayload
from .normalizer import normalize_one
from .db import upsert_phonelog, get_driver
from . import metrics

app = FastAPI(title=settings.APP_NAME)
configure_logging(settings.LOG_LEVEL)
log = logging.getLogger("app")

# CORS permissive by default (tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# X-Request-ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    req_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    start = time.time()
    response: Response
    try:
        response = await call_next(request)
    except Exception as e:
        log.exception("Unhandled error")
        # metrics for 500 as well
        path = request.url.path
        method = request.method
        metrics.REQUESTS.labels(path=path, method=method, status="500").inc()
        metrics.REQ_LATENCY.labels(path=path, method=method).observe(time.time()-start)
        return JSONResponse(status_code=500, content={"result": "error", "reason": "internal"})
    duration = time.time()-start
    duration_ms = int(duration*1000)
    response.headers["x-request-id"] = req_id
    # Metrics
    path = request.url.path
    method = request.method
    metrics.REQUESTS.labels(path=path, method=method, status=str(response.status_code)).inc()
    metrics.REQ_LATENCY.labels(path=path, method=method).observe(duration)
    log.info(json.dumps({"event":"request","path":path,"status":response.status_code,"ms":duration_ms,"rid":req_id}))
    return response

# WAL writer with rotation
class WalWriter:
    def __init__(self, root: str, rotate_bytes: int):
        self.root = pathlib.Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.rotate_bytes = rotate_bytes
        self._cur = None

    def _open(self):
        ts = time.strftime("%Y%m%d-%H%M%S")
        path = self.root / f"events-{ts}.ndjson.gz"
        self._cur = (path, gzip.open(path, "at", encoding="utf-8"))
        log.info(f"WAL opened {path}")

    def write(self, obj: Dict[str, Any]):
        if self._cur is None:
            self._open()
        path, fh = self._cur
        line = json.dumps(obj, ensure_ascii=False)
        fh.write(line + "\n")
        fh.flush()
        try:
            if path.stat().st_size >= self.rotate_bytes:
                fh.close()
                log.info(f"WAL rotating {path}")
                self._cur = None
        except FileNotFoundError:
            pass

wal = WalWriter(settings.WAL_DIR, settings.WAL_ROTATE_BYTES)

@app.on_event("startup")
def _startup():
    get_driver()  # fail fast if DB not reachable
    log.info("Startup complete")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/api/v1/locations")
async def create_locations(payload: IngestPayload, request: Request):
    wal.write({"received_at": int(time.time()*1000), "payload": payload.dict()})
    default_user = payload.user_id or settings.DEFAULT_USER_ID
    default_device = payload.device_id

    normalized: List[Dict[str, Any]] = []
    dropped = 0
    for item in payload.locations:
        raw_item = item if isinstance(item, dict) else item.dict(by_alias=True)
        norm = normalize_one(raw_item, default_user=default_user, default_device=default_device)
        if norm is None:
            dropped += 1
            continue
        normalized.append(norm)

    if not normalized:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"result": "error", "reason": "no valid points (need timestamp + coordinates)"}
        )

    uids = []
    for rec in normalized:
        try:
            uid = upsert_phonelog(rec)
            uids.append(uid)
        except Exception:
            metrics.DB_FAILURES.inc()
            log.exception("Neo4j upsert failed")
            return JSONResponse(status_code=500, content={"result": "error", "reason": "db failure"})

    metrics.INGESTED_POINTS.inc(len(uids))
    if dropped:
        metrics.DROPPED_POINTS.inc(dropped)
    return {"result": "ok", "ingested": len(uids), "dropped": dropped, "uids": uids}

@app.post("/api/v0")
async def handle_location_data_compat(req: Request):
    data = await req.json()
    wal.write({"received_at": int(time.time()*1000), "payload": data, "api": "v0"})
    return {"result": "ok"}


@app.get("/metrics")
def metrics_endpoint():
    from prometheus_client import generate_latest
    from prometheus_client import generate_latest
    return Response(generate_latest(metrics.registry), media_type=metrics.CONTENT_TYPE_LATEST)

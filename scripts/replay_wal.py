import argparse, os, json, gzip, pathlib, sys
from typing import Iterator, Dict, Any, List
from app.settings import settings
from app.normalizer import normalize_one
from app.db import upsert_phonelog

def iter_events(wal_dir: str) -> Iterator[Dict[str, Any]]:
    p = pathlib.Path(wal_dir)
    if not p.exists():
        return
    for f in sorted(p.glob("events-*.ndjson.gz")):
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

def main():
    ap = argparse.ArgumentParser(description="Replay WAL to Neo4j (idempotent).")
    ap.add_argument("--wal-dir", default=settings.WAL_DIR)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="max events to process (0 = all)")
    ap.add_argument("--only-v1", action="store_true", help="ignore /api/v0 legacy entries")
    args = ap.parse_args()

    processed = ingested = dropped = 0

    for ev in iter_events(args.wal_dir):
        if args.limit and processed >= args.limit:
            break
        processed += 1

        payload = ev.get("payload")
        if payload is None:
            continue

        locations = []
        default_user = payload.get("user_id") or settings.DEFAULT_USER_ID
        default_device = payload.get("device_id")

        if "locations" in payload:
            locations = payload["locations"]
        else:
            if args.only_v1:
                continue
            locations = [payload]

        normalized: List[Dict[str, Any]] = []
        for item in locations:
            if not isinstance(item, dict):
                continue
            norm = normalize_one(item, default_user=default_user, default_device=default_device)
            if norm is None:
                dropped += 1
                continue
            normalized.append(norm)

        if args.dry_run:
            ingested += len(normalized)
            continue

        for rec in normalized:
            try:
                upsert_phonelog(rec)
                ingested += 1
            except Exception as e:
                print(f"Upsert failed: {e}", file=sys.stderr)

    print(json.dumps({"processed": processed, "ingested": ingested, "dropped": dropped}))

if __name__ == "__main__":
    main()

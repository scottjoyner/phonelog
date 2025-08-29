import os, shutil, glob
from typing import Optional
from prometheus_client import CollectorRegistry, Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest

# Multiprocess (Gunicorn) support
MULTIPROC_DIR = os.environ.get("PROMETHEUS_MULTIPROC_DIR")

registry = CollectorRegistry()

if MULTIPROC_DIR:
    # Use multiprocess collector if env var present
    from prometheus_client.multiprocess import MultiProcessCollector
    # Optionally clear stale metrics on boot (set PROM_CLEAN_ON_START=1 to enable)
    if os.environ.get("PROM_CLEAN_ON_START") == "1":
        os.makedirs(MULTIPROC_DIR, exist_ok=True)
        for f in glob.glob(os.path.join(MULTIPROC_DIR, "*.db")):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
    MultiProcessCollector(registry)

# Metrics
REQUESTS = Counter(
    "app_requests_total",
    "Total HTTP requests",
    ["path", "method", "status"],
    registry=registry,
)

REQ_LATENCY = Histogram(
    "app_request_latency_seconds",
    "HTTP request latency in seconds",
    ["path", "method"],
    registry=registry,
)

INGESTED_POINTS = Counter(
    "app_ingested_points_total",
    "Total ingested phonelog points",
    registry=registry,
)

DROPPED_POINTS = Counter(
    "app_dropped_points_total",
    "Total dropped phonelog points (invalid)",
    registry=registry,
)

DB_FAILURES = Counter(
    "app_db_failures_total",
    "DB upsert failures",
    registry=registry,
)

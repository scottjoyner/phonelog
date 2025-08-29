# Phone Log Ingestion (FastAPI + Neo4j)

Production-ready ingestion API with idempotent upserts, WAL replay, and normalization utilities.

## Quickstart

```bash
cp .env.example .env
docker compose up -d --build

# Apply schema
docker exec -it neo4j cypher-shell -u $NEO4J_USER -p $NEO4J_PASSWORD -f /var/lib/neo4j/import/schema.cypher

# Test
curl -X POST http://localhost:8888/api/v1/locations   -H "Content-Type: application/json"   -d '{
    "user_id": "kipnerter",
    "device_id": "iphone-14",
    "locations": [{
      "type": "Feature",
      "geometry": {"type":"Point","coordinates":[-80.7778,35.0348]},
      "properties": { "timestamp": "2023-12-28T17:11:25Z", "speed": 10.2 }
    }]
  }'
```

## WAL Replay

Replay all WAL files (idempotent):

```bash
python3 -m scripts.replay_wal --wal-dir ./data/wal
```

Options: `--dry-run`, `--limit`, `--only-v1`

## Tools

- `scripts/apply_schema.py` — runs `db/schema.cypher`
- `scripts/run_normalize.py` — executes `db/phlog_normalize.cypher` (APOC)
- `scripts/replay_wal.py` — replays WAL into Neo4j


## Prometheus Metrics

- Scrape `http://<host>:8888/metrics`
- Using Gunicorn, metrics run in **multiprocess** mode. `docker-compose.yml` sets:
  - `PROMETHEUS_MULTIPROC_DIR=/prom`
  - `PROM_CLEAN_ON_START=1` (cleans stale metrics files on boot)

## WAL Maintenance

Prune files older than 14 days (archive instead of delete):
```bash
python3 -m scripts.wal_prune prune --wal-dir ./data/wal --keep-days 14 --archive-dir ./data/wal_archive
```

Compact small files into a single gz (and delete originals):
```bash
python3 -m scripts.wal_prune compact --wal-dir ./data/wal --max-compact-size 5000000 --delete-originals
```

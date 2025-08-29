# Phone Log Ingestion (FastAPI + Neo4j)

Production-ready ingestion API with idempotent upserts, WAL replay, normalization utilities, Prometheus metrics, and an optional monitoring stack (Prometheus + Grafana).

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

## WAL Maintenance

Prune files older than 14 days (archive instead of delete):
```bash
python3 -m scripts.wal_prune prune --wal-dir ./data/wal --keep-days 14 --archive-dir ./data/wal_archive
```

Compact small files into a single gz (and delete originals):
```bash
python3 -m scripts.wal_prune compact --wal-dir ./data/wal --max-compact-size 5000000 --delete-originals
```

## Monitoring

### One-command monitoring stack (Prometheus + Grafana)

Bring everything up together (API, Neo4j, Prometheus, Grafana):

```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d --build
```

- Prometheus UI: http://localhost:9090
- Grafana UI: http://localhost:3000 (user: `admin` / pass: `admin` — change in `docker-compose.monitoring.yml`)

Grafana is pre-provisioned with a Prometheus data source and auto-loads the dashboard from
`monitoring/grafana/dashboard-phone-log.json` under the **Phone Log** folder.

## Notes
- API metrics at `/metrics`
- Request logs are JSON to stdout with request IDs.
- WAL path: `./data/wal` (mounted into the container).




# RUN
`docker compose -f docker-compose.yml -f compose.host.yml -f compose.dev.yml up -d`
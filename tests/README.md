# Phone Log API — Best-Practices Test Suite (v2)

This test suite adds **pytest**, **Hypothesis** (property-based tests), **Neo4j-backed idempotency assertions**, and **WAL checks**, while keeping the simple CLI runner.

## Install
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r tests/requirements-tests.txt
```

## Environment
The suite discovers settings from either CLI args or env vars:

- `API_BASE` (default: http://localhost:8888)
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE` (optional; enables DB assertions)
- `WAL_DIR` (optional; enables WAL assertions)

You can also pass them via pytest options, e.g.:
```bash
pytest -q tests \
  --base-url=http://localhost:8888 \
  --neo4j-uri=bolt://localhost:7687 \
  --neo4j-user=neo4j --neo4j-password=livelongandprosper \
  --wal-dir=../phone-log-ingestion/data/wal
```

## Run everything
```bash
pytest -q tests -n auto --reruns 1 --reruns-delay 1
```

## Focused subsets
- Curated JSON cases: `pytest -q tests/test_ingest_curated.py`
- Idempotency w/ Neo4j: `pytest -q tests/test_idempotency.py` (needs DB creds)
- Hypothesis fuzzing: `pytest -q tests/test_hypothesis_fuzz.py`
- WAL append behavior: `pytest -q tests/test_wal_behavior.py` (needs WAL_DIR)

## CLI runner (no pytest)
```bash
API_BASE=http://localhost:8888 python tests/run_cases.py
```

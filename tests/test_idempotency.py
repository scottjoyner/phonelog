import json, pathlib, time
import pytest
from .utils import post_json

@pytest.mark.usefixtures("neo4j_session")
def test_idempotent_upserts(base_url, neo4j_session, unique_device):
    payload = json.loads((pathlib.Path(__file__).parent / "payloads" / "v1_large_batch.json").read_text())
    payload["device_id"] = unique_device

    # count before
    res = neo4j_session.run("MATCH (p:PhoneLog {device_id:$d}) RETURN count(p) AS c", d=unique_device)
    before = res.single()["c"]

    # first ingest
    st1, rid1, js1 = post_json(base_url, "/api/v1/locations", payload)
    assert st1 == 200, js1
    assert js1.get("ingested", 0) >= 100

    # second ingest (same payload)
    st2, rid2, js2 = post_json(base_url, "/api/v1/locations", payload)
    assert st2 == 200, js2

    # count after
    res = neo4j_session.run("MATCH (p:PhoneLog {device_id:$d}) RETURN count(p) AS c", d=unique_device)
    after = res.single()["c"]

    # Ensure no duplicate nodes were created on second POST
    assert after - before == js1.get("ingested", 0), f"Idempotency broken: {after=} {before=}"


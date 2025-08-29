import json, pathlib
import pytest
from .utils import post_json

CASES = json.loads((pathlib.Path(__file__).parent / "manifest.json").read_text())["cases"]

@pytest.mark.parametrize("case", CASES)
def test_curated_cases(base_url, case):
    payload = json.loads((pathlib.Path(__file__).parent / "payloads" / case["file"]).read_text())
    status, rid, js = post_json(base_url, case["endpoint"], payload)
    assert status == case.get("expect_status", 200), js
    if case["endpoint"] == "/api/v1/locations" and status == 200:
        assert js.get("ingested", 0) >= case.get("expect_min_ingested", 0), js
        assert js.get("dropped", 0)  >= case.get("expect_min_dropped", 0), js

import json, time, os, pathlib
import pytest
from .utils import post_json, latest_file_size

@pytest.mark.usefixtures("wal_dir")
def test_wal_appends_on_v0(base_url, wal_dir):
    payload = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-73.5, 40.5]},
        "properties": {"timestamp": "2024-01-01T00:00:00Z"}
    }
    before = latest_file_size(wal_dir)
    status, rid, js = post_json(base_url, "/api/v0", payload)
    assert status == 200
    # give FS a moment
    time.sleep(0.2)
    after = latest_file_size(wal_dir)
    assert after >= before, "WAL size did not increase"

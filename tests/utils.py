import requests, json, os, time, pathlib

def post_json(base_url: str, endpoint: str, payload: dict, timeout=30):
    r = requests.post(base_url + endpoint, json=payload, timeout=timeout)
    rid = r.headers.get("x-request-id")
    try:
        js = r.json()
    except Exception:
        js = {"raw": r.text}
    return r.status_code, rid, js

def latest_file_size(dirpath: str) -> int:
    p = pathlib.Path(dirpath)
    files = sorted(p.glob("events-*.ndjson.gz"))
    if not files: return 0
    return files[-1].stat().st_size

#!/usr/bin/env python3
import os, json, pathlib, requests, sys
from datetime import datetime

BASE = os.environ.get("API_BASE", "http://localhost:8888")
HERE = pathlib.Path(__file__).resolve().parent
PAYLOADS = HERE / "payloads"
MANIFEST = json.loads((HERE / "manifest.json").read_text())

def post(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.status_code, r.headers.get("x-request-id"), r.text
    except Exception as e:
        return 0, None, str(e)

def main():
    ok = 0; fail = 0; results = []
    for c in MANIFEST["cases"]:
        payload = json.loads((PAYLOADS / c["file"]).read_text())
        status, rid, body = post(BASE + c["endpoint"], payload)
        try: j = json.loads(body)
        except: j = {"raw": body}
        passed = (status == c.get("expect_status",200))
        if c["endpoint"] == "/api/v1/locations" and status == 200:
            passed = passed and (j.get("ingested",0) >= c.get("expect_min_ingested",0))
            passed = passed and (j.get("dropped",0)  >= c.get("expect_min_dropped",0))
        if passed: ok+=1
        else: fail+=1
        results.append({"file":c["file"],"endpoint":c["endpoint"],"status":status,"rid":rid,"response":j})
        print(("OK " if passed else "FAIL ") + c["file"], status)
    out = HERE / "results" / f"run-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({"passed": ok, "failed": fail, "total": ok+fail}))

if __name__ == "__main__":
    main()

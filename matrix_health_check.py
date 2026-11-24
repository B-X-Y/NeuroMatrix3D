import json
import os
from http.client import HTTPConnection

port = int(os.environ.get("MATRIX_PORT") or "5000")
connection = HTTPConnection("127.0.0.1", port, timeout=2)
connection.request("GET", "/readyz")

with connection.getresponse() as response:
    if response.status != 200:
        raise SystemExit(f"Readiness endpoint returned HTTP {response.status} (expected 200).")
    payload = json.load(response)
    if not isinstance(payload, dict) or payload.get("status") != "ready":
        raise SystemExit("Readiness endpoint did not report a ready status")

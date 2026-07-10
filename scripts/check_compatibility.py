#!/usr/bin/env python3
"""Fail when verified AgentMail dependencies or public specs have drifted."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = json.loads((ROOT / "compatibility.json").read_text(encoding="utf-8"))
HEADERS = {"User-Agent": "agentmail-plugins-compatibility-check/0.3.0"}


def fetch_json(url: str) -> dict:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.load(response)
        except (OSError, ValueError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2**attempt)
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


actual = {
    "agentmail.typescript": fetch_json("https://registry.npmjs.org/agentmail/latest")["version"],
    "agentmail.python": fetch_json("https://pypi.org/pypi/agentmail/json")["info"]["version"],
    "cli": fetch_json("https://registry.npmjs.org/agentmail-cli/latest")["version"],
    "toolkit.typescript": fetch_json("https://registry.npmjs.org/agentmail-toolkit/latest")["version"],
    "toolkit.python": fetch_json("https://pypi.org/pypi/agentmail-toolkit/json")["info"]["version"],
}
expected = {
    "agentmail.typescript": EXPECTED["agentmail"]["typescript"],
    "agentmail.python": EXPECTED["agentmail"]["python"],
    "cli": EXPECTED["cli"],
    "toolkit.typescript": EXPECTED["toolkit"]["typescript"],
    "toolkit.python": EXPECTED["toolkit"]["python"],
}

errors = [
    f"{name}: expected {expected[name]}, registry reports {version}"
    for name, version in actual.items()
    if version != expected[name]
]

openapi = fetch_json(EXPECTED["specifications"]["openapi"])
asyncapi = fetch_json(EXPECTED["specifications"]["asyncapi"])
if not str(openapi.get("openapi", "")).startswith("3."):
    errors.append("AgentMail OpenAPI document is missing an OpenAPI 3.x marker")
if not str(asyncapi.get("asyncapi", "")).startswith("2."):
    errors.append("AgentMail AsyncAPI document is missing an AsyncAPI 2.x marker")

try:
    request = urllib.request.Request(EXPECTED["hostedMcp"]["url"], headers=HEADERS)
    urllib.request.urlopen(request, timeout=20).close()
except urllib.error.HTTPError as exc:
    if exc.code not in {401, 405}:
        errors.append(f"hosted MCP probe returned unexpected HTTP {exc.code}")
except urllib.error.URLError as exc:
    errors.append(f"hosted MCP probe failed: {exc}")

if errors:
    print("Compatibility drift detected:", file=sys.stderr)
    for item in errors:
        print(f"- {item}", file=sys.stderr)
    raise SystemExit(1)

for name in sorted(actual):
    print(f"{name}: {actual[name]}")
print("AgentMail OpenAPI, AsyncAPI, and hosted MCP probes passed")

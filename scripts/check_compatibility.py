#!/usr/bin/env python3
"""Fail when verified AgentMail package versions have drifted."""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = json.loads((ROOT / "compatibility.json").read_text(encoding="utf-8"))
HEADERS = {"User-Agent": "agentmail-plugins-compatibility-check/0.3.0"}


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


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

if errors:
    print("Compatibility drift detected:", file=sys.stderr)
    for item in errors:
        print(f"- {item}", file=sys.stderr)
    raise SystemExit(1)

for name in sorted(actual):
    print(f"{name}: {actual[name]}")
print("AgentMail package versions match compatibility.json")

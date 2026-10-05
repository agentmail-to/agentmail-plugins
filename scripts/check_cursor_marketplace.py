#!/usr/bin/env python3
"""Verify that Cursor's public AgentMail listing matches this checkout."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://cursor.com/marketplace/agentmail"
PACKAGED_PATHS = (
    ".cursor-plugin",
    ".mcp.json",
    "assets",
    "skills",
)


def normalize(page: str) -> str:
    return html.unescape(page).replace(r'\"', '"')


def listing(page: str) -> tuple[str, int, set[str]]:
    text = normalize(page)
    marker = '"gitUrl":"https://github.com/agentmail-to/agentmail-plugins"'
    start = text.find(marker)
    if start < 0:
        raise ValueError("AgentMail repository entry was not found")

    block = text[start:]
    ref_match = re.search(r'"gitRef":"([0-9a-f]{40})"', block)
    end = block.find('"mcpServers"')
    if not ref_match or end < 0:
        raise ValueError("listing metadata is incomplete")

    skills = set(re.findall(r'"sourcePath":"skills/([^/"]+)/SKILL\.md"', block[:end]))
    if not skills:
        raise ValueError("listing contains no skills")

    before = text[:start]
    timestamps = re.findall(r'"updatedAt":"?(\d{10,13})"?', before[-20000:])
    if not timestamps:
        raise ValueError("listing has no update timestamp")
    updated_at = int(timestamps[-1])
    if updated_at > 10_000_000_000:
        updated_at //= 1000
    return ref_match.group(1), updated_at, skills


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def expected() -> tuple[str, int, str, set[str]]:
    manifest = json.loads((ROOT / ".cursor-plugin/plugin.json").read_text())
    skills = {
        path.parent.name
        for path in (ROOT / "skills").glob("*/SKILL.md")
    }
    packaged_ref = git("log", "-1", "--format=%H", "--", *PACKAGED_PATHS)
    return (
        packaged_ref,
        int(git("show", "-s", "--format=%ct", packaged_ref)),
        manifest["description"],
        skills,
    )


def content_equivalent_ref(published_ref: str, packaged_ref: str) -> bool:
    if published_ref == packaged_ref:
        return True
    checks = (
        ("cat-file", "-e", f"{published_ref}^{{commit}}"),
        ("merge-base", "--is-ancestor", packaged_ref, published_ref),
        ("merge-base", "--is-ancestor", published_ref, "HEAD"),
        ("diff", "--quiet", published_ref, "HEAD", "--", *PACKAGED_PATHS),
    )
    return all(
        subprocess.run(["git", *args], cwd=ROOT, capture_output=True).returncode == 0
        for args in checks
    )


def fetch(url: str) -> str:
    request = urllib.request.Request(
        url, headers={"User-Agent": "agentmail-cursor-marketplace-check/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        sample = r'''{"updatedAt":"1800000000000","gitUrl":"https://github.com/agentmail-to/agentmail-plugins","gitRef":"0123456789abcdef0123456789abcdef01234567","skills":[{"sourcePath":"skills/one/SKILL.md"},{"sourcePath":"skills/two/SKILL.md"}],"mcpServers":[]}'''
        assert listing(sample) == (
            "0123456789abcdef0123456789abcdef01234567",
            1_800_000_000,
            {"one", "two"},
        )
        print("Cursor marketplace check self-test passed")
        return 0

    expected_ref, commit_time, description, expected_skills = expected()
    page = fetch(args.url)
    published_ref, updated_at, published_skills = listing(page)
    problems: list[str] = []

    if not content_equivalent_ref(published_ref, expected_ref):
        problems.append(f"listing commit is {published_ref}, expected {expected_ref}")
    if description not in normalize(page):
        problems.append("listing description does not match .cursor-plugin/plugin.json")
    if published_skills != expected_skills:
        problems.append(
            "listing skills differ: "
            f"missing={sorted(expected_skills - published_skills)}, "
            f"unexpected={sorted(published_skills - expected_skills)}"
        )
    if updated_at < commit_time:
        problems.append("listing update timestamp predates the released commit")

    if problems:
        print("Cursor marketplace verification failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1

    print(
        f"Cursor listing matches {published_ref}: "
        f"{len(published_skills)} skills and synchronized description"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

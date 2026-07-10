#!/usr/bin/env python3
"""Validate the cross-platform plugin without modifying the repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def error(message: str) -> None:
    ERRORS.append(message)


def load_json(relative: str) -> dict:
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"{relative}: invalid or unreadable JSON: {exc}")
        return {}


def check_path(owner: str, value: object) -> None:
    if not isinstance(value, str) or not value.startswith("./"):
        error(f"{owner}: expected a ./-prefixed relative path, got {value!r}")
        return
    target = (ROOT / value[2:]).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        error(f"{owner}: path escapes the plugin root")
        return
    if not target.exists():
        error(f"{owner}: referenced path does not exist: {value}")


JSON_FILES = [
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    ".mcp.json",
    ".plugin/plugin.json",
    "compatibility.json",
    "mcp.cursor.json",
]

for json_file in JSON_FILES:
    load_json(json_file)

manifest_paths = {
    "open": ".plugin/plugin.json",
    "claude": ".claude-plugin/plugin.json",
    "cursor": ".cursor-plugin/plugin.json",
    "codex": ".codex-plugin/plugin.json",
}
manifests = {name: load_json(path) for name, path in manifest_paths.items()}

versions = {name: manifest.get("version") for name, manifest in manifests.items()}
if len(set(versions.values())) != 1 or None in versions.values():
    error(f"plugin manifest versions are not synchronized: {versions}")
else:
    version = next(iter(versions.values()))
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## {version} " not in changelog:
        error(f"CHANGELOG.md has no entry for {version}")

for surface, manifest in manifests.items():
    if manifest.get("name") != "agentmail":
        error(f"{surface} manifest name must be agentmail")
    if "commands" in manifest:
        error(f"{surface} manifest still declares legacy commands")
    for field in ("skills", "mcpServers", "logo"):
        if field in manifest and isinstance(manifest[field], str):
            check_path(f"{surface}.{field}", manifest[field])
    interface = manifest.get("interface", {})
    if isinstance(interface, dict):
        for field in ("composerIcon", "logo", "logoDark"):
            if field in interface:
                check_path(f"{surface}.interface.{field}", interface[field])

if any((ROOT / "commands").glob("*")):
    error("commands/ still contains legacy command files")

skills_root = ROOT / "skills"
skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
expected_skills = {
    "agentmail",
    "agentmail-cli",
    "agentmail-mcp",
    "agentmail-toolkit",
    "check-email",
    "manage-inboxes",
    "send-email",
}
actual_skills = {path.name for path in skill_dirs}
if actual_skills != expected_skills:
    error(f"unexpected skill set: expected {sorted(expected_skills)}, got {sorted(actual_skills)}")

frontmatter_pattern = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
for skill_dir in skill_dirs:
    skill_file = skill_dir / "SKILL.md"
    openai_file = skill_dir / "agents" / "openai.yaml"
    if not skill_file.is_file():
        error(f"{skill_dir.name}: missing SKILL.md")
        continue
    if not openai_file.is_file():
        error(f"{skill_dir.name}: missing agents/openai.yaml")
        continue

    content = skill_file.read_text(encoding="utf-8")
    match = frontmatter_pattern.match(content)
    if not match:
        error(f"{skill_dir.name}: invalid YAML frontmatter boundary")
        continue

    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            error(f"{skill_dir.name}: malformed frontmatter line: {line}")
            continue
        metadata[key.strip()] = value.strip().strip('"\'')

    if set(metadata) != {"name", "description"}:
        error(f"{skill_dir.name}: frontmatter must contain only name and description")
    if metadata.get("name") != skill_dir.name:
        error(f"{skill_dir.name}: frontmatter name does not match folder")
    if len(metadata.get("description", "")) < 40:
        error(f"{skill_dir.name}: description is too short for reliable discovery")

    openai = openai_file.read_text(encoding="utf-8")
    if f"${skill_dir.name}" not in openai:
        error(f"{skill_dir.name}: default_prompt must mention ${skill_dir.name}")
    if skill_dir.name in {"send-email", "check-email", "manage-inboxes"}:
        if "https://mcp.agentmail.to/mcp" not in openai:
            error(f"{skill_dir.name}: missing hosted MCP dependency")
    elif "dependencies:" in openai:
        error(f"{skill_dir.name}: declares an unnecessary MCP dependency")

markdown_link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
for markdown in ROOT.rglob("*.md"):
    if ".git" in markdown.parts:
        continue
    for target in markdown_link_pattern.findall(markdown.read_text(encoding="utf-8")):
        target = target.strip().strip("<>").split("#", 1)[0]
        if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
            continue
        resolved = (markdown.parent / target).resolve()
        if not resolved.exists():
            error(f"{markdown.relative_to(ROOT)}: broken local link {target}")

stale_patterns = {
    '"AGENTMAIL_API_KEY": ""': "empty API-key override",
    'https://mcp.agentmail.to"': "hosted MCP URL missing /mcp",
    "mcp-codex.json": "removed Codex MCP filename",
    "support@agentmail.to": "obsolete support address",
    "X-AgentMail-Signature": "obsolete webhook signature scheme",
    "retrieve --": "obsolete CLI retrieve command",
    "gpt-4o": "stale hard-coded model",
    "[TODO:": "unresolved skill placeholder",
}

for path in ROOT.rglob("*"):
    if (
        not path.is_file()
        or path.resolve() == Path(__file__).resolve()
        or ".git" in path.parts
        or path.suffix in {".svg", ".pyc"}
    ):
        continue
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for pattern, label in stale_patterns.items():
        if pattern in content:
            error(f"{path.relative_to(ROOT)}: contains {label}: {pattern}")

oauth_config = load_json(".mcp.json").get("mcpServers", {}).get("agentmail", {})
if oauth_config != {"type": "http", "url": "https://mcp.agentmail.to/mcp"}:
    error(".mcp.json must contain the hosted OAuth-compatible AgentMail server")

cursor_config = load_json("mcp.cursor.json").get("mcpServers", {}).get("agentmail", {})
if cursor_config.get("headers", {}).get("x-api-key") != "${env:AGENTMAIL_API_KEY}":
    error("mcp.cursor.json must use Cursor environment interpolation for x-api-key")

if ERRORS:
    print("Repository validation failed:", file=sys.stderr)
    for item in ERRORS:
        print(f"- {item}", file=sys.stderr)
    raise SystemExit(1)

print(f"Repository validation passed: {len(manifests)} manifests, {len(skill_dirs)} skills")

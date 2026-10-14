"""Inventaire des actifs (skills, MCP, commandes) et audit d'obsolescence. L'audit est pur."""
import json
import subprocess
from datetime import datetime
from pathlib import Path

from .. import registry


def _epoch(iso):
    return datetime.fromisoformat(iso).timestamp()


def first_added(root, path):
    try:
        out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%ct", "--", str(path)], cwd=root,
                             capture_output=True, text=True, timeout=30).stdout.split()
        stamps = [int(x) for x in out if x.isdigit()]
        if stamps:
            return min(stamps)
    except (OSError, subprocess.TimeoutExpired):
        pass
    return path.stat().st_mtime


def mcp_names(root):
    names = set()
    for rel in (".gemini/settings.json", ".mcp.json"):
        path = Path(root) / rel
        try:
            names |= set(json.loads(path.read_text(encoding="utf-8")).get("mcpServers", {}))
        except (OSError, ValueError):
            continue
    return sorted(names)


def inventory(ctx):
    items = []
    for skill in sorted(ctx.layout("skills").glob("*/SKILL.md")):
        items.append({"kind": "skill", "name": skill.parent.name, "added": first_added(ctx.root, skill)})
    for name in mcp_names(ctx.root):
        items.append({"kind": "mcp", "name": name, "added": first_added(ctx.root, ctx.root / ".gemini/settings.json")})
    for mod in registry.load():
        items.append({"kind": "cmd", "name": mod.NAME, "added": first_added(ctx.root, Path(mod.__file__))})
    return items


def audit(items, events, now, grace_days=30, unused_days=60, protected=()):
    uses = {}
    for e in events:
        key = (e.get("kind"), e.get("name"))
        count, last = uses.get(key, (0, 0.0))
        uses[key] = (count + 1, max(last, _epoch(e["ts"])))
    rows = []
    for item in items:
        count, last = uses.get((item["kind"], item["name"]), (0, 0.0))
        age = (now - item["added"]) / 86400
        idle = (now - last) / 86400 if last else None
        if item["name"] in protected or age < grace_days:
            verdict = "keep"
        elif count == 0:
            verdict = "archive"
        elif idle > unused_days:
            verdict = "review"
        else:
            verdict = "keep"
        rows.append({**item, "uses": count, "idle_days": None if idle is None else round(idle), "age_days": round(age), "verdict": verdict})
    return rows

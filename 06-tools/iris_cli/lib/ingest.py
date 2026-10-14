"""Lit les journaux locaux des CLI (Claude Code, Gemini CLI) et alimente le registre de tokens, sans doublon.
Cursor n'écrit pas ses tokens en local: à saisir avec `iris tokens add`."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from ..core import jsonl
from . import tokenmath, workspace


def _num(v):
    return int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0


def _event(uid, source, ts, model, tin, tout, cached, session, repo, prices):
    return {"uid": uid, "ts": ts, "kind": "remote", "source": source, "model": model, "tin": tin, "tout": tout,
            "cached": cached, "usd": tokenmath.cost(prices, model, tin, tout), "session": session, "action": repo}


def claude_events(home, repos, prices, seen_files):
    base, slugs = Path(home) / ".claude" / "projects", {re.sub(r"[^A-Za-z0-9]", "-", str(p)): p.name for p in repos}
    for f in sorted(base.glob("*/*.jsonl")):
        mtime = f.stat().st_mtime
        if seen_files.get(str(f)) == mtime:
            continue
        seen_files[str(f)] = mtime
        latest = {}
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                d = json.loads(line)
            except ValueError:
                continue
            m = d.get("message") if isinstance(d, dict) else None
            if d.get("type") == "assistant" and isinstance(m, dict) and isinstance(m.get("usage"), dict) and m.get("id"):
                latest[m["id"]] = (d.get("timestamp", ""), m.get("model", ""), m["usage"])
        for mid, (ts, model, u) in latest.items():
            cached = _num(u.get("cache_read_input_tokens"))
            tin = _num(u.get("input_tokens")) + _num(u.get("cache_creation_input_tokens")) + cached
            yield _event(f"claude:{mid}", "claude", ts, model, tin, _num(u.get("output_tokens")), cached, f.stem[:8],
                         slugs.get(f.parent.name, f.parent.name), prices)


def gemini_events(home, repos, prices, seen_files):
    """Format non vérifié sur toutes les versions: messages[].tokens {input, output, cached, thoughts}."""
    base, hashes = Path(home) / ".gemini" / "tmp", {hashlib.sha256(str(p).encode()).hexdigest(): p.name for p in repos}
    for f in sorted(base.glob("*/chats/*.json")):
        mtime = f.stat().st_mtime
        if seen_files.get(str(f)) == mtime:
            continue
        seen_files[str(f)] = mtime
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for i, m in enumerate(data.get("messages", []) if isinstance(data, dict) else []):
            t = m.get("tokens") if isinstance(m, dict) else None
            if not isinstance(t, dict):
                continue
            yield _event(f"gemini:{f.stem}:{m.get('id', i)}", "gemini", m.get("timestamp", ""), m.get("model", ""),
                         _num(t.get("input")), _num(t.get("output")) + _num(t.get("thoughts")), _num(t.get("cached")),
                         f.stem[-8:], hashes.get(f.parent.parent.name, "-"), prices)


def ingest(ctx, home=None):
    home = Path(home) if home else Path.home()
    state_file = ctx.state / "ingest.json"
    try:
        seen_files = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        seen_files = {}
    ledger = ctx.state / "tokens.jsonl"
    known = {e.get("uid") for e in jsonl.read(ledger)}
    repos, prices, added = workspace.repos(ctx), ctx.cfg["prices"], {"claude": 0, "gemini": 0}
    for gen in (claude_events, gemini_events):
        for ev in gen(home, repos, prices, seen_files):
            if ev["uid"] not in known:
                known.add(ev["uid"])
                ev["ts"] = ev["ts"] or datetime.now(timezone.utc).isoformat()
                jsonl.append(ledger, ev)
                added[ev["source"]] += 1
    state_file.write_text(json.dumps(seen_files), encoding="utf-8")
    return added

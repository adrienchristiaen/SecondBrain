"""Détail d'un repo pour la vue web: README, docs Markdown, langages, commits, graphe, fiche, consommation de tokens."""
import os
from collections import Counter
from pathlib import Path

from ..core import jsonl
from . import gitrun, graphast, select, workspace

SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", "target"}
MAX_FILES = 5000


def _walk(repo):
    count = 0
    for folder, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            count += 1
            if count > MAX_FILES:
                return
            yield Path(folder) / f


def _read(path, limit):
    return path.read_text(encoding="utf-8", errors="replace")[:limit] if path and path.is_file() else ""


def detail(ctx, name):
    path = next((p for p in workspace.repos(ctx) if p.name == name), None)
    if path is None:
        return None
    wiki = ctx.layout("wiki")
    status = gitrun.status(path, ctx.cfg["git"]["branches"])
    md, langs = [], Counter()
    for f in _walk(path):
        if f.suffix == ".md" and len(md) < 60:
            md.append({"path": f.relative_to(path).as_posix(), "bytes": f.stat().st_size})
        elif f.suffix:
            langs[f.suffix] += 1
    rc, log, _ = gitrun.git(["log", "-8", "--format=%h\x1f%an\x1f%ar\x1f%s"], path)
    commits = [dict(zip(("hash", "author", "when", "subject"), line.split("\x1f"))) for line in log.splitlines()] if rc == 0 else []
    rc, out, _ = gitrun.git(["branch", "-a", "--format=%(refname:short)"], path)
    graph_file = wiki / "graphs" / f"{name}.md"
    readme = next((p for p in (path / "README.md", path / "README.fr.md") if p.is_file()), None)
    entries = [e for e in jsonl.read(ctx.state / "tokens.jsonl") if e.get("action") == name]
    return {
        "name": name, "path": str(path), "status": status,
        "graph": graphast.freshness(path, graph_file, status["last_commit"]), "graph_md": _read(graph_file, 12000),
        "card": _read(select.find_card(wiki / "repos", name), 4000), "readme": _read(readme, 4000),
        "docs_present": {d: (path / d).is_file() for d in ("README.md", "ARCHITECTURE.md", "GRAPH.md")},
        "md_files": md, "languages": dict(langs.most_common(8)), "commits": commits,
        "branches": out.splitlines()[:20] if rc == 0 else [],
        "tokens": {"tin": sum(e.get("tin", 0) for e in entries), "tout": sum(e.get("tout", 0) for e in entries), "events": len(entries)},
    }

"""Repos du brain: ceux clonés dans 05-repos et ceux d'une racine locale connectée (lue sur place, rien n'est copié)."""
import json
import os
from pathlib import Path

from . import gitrun

SKIP = {"node_modules", ".venv", "venv", "__pycache__", "build", "dist", "target", "Library"}


def roots_file(ctx):
    return ctx.state / "roots.json"


def saved_roots(ctx):
    try:
        return [str(r) for r in json.loads(roots_file(ctx).read_text(encoding="utf-8"))]
    except (OSError, ValueError):
        return []


def configured_roots(ctx):
    raw = saved_roots(ctx) + list(ctx.cfg.get("repos", {}).get("roots", []))
    return [Path(os.path.expanduser(r)).resolve() for r in raw]


def save_roots(ctx, roots):
    roots_file(ctx).write_text(json.dumps(sorted(set(roots))), encoding="utf-8")


def scan(root, depth=3):
    """Dossiers contenant .git sous root, sans descendre dans un repo ni dans les dossiers cachés."""
    found = []

    def walk(folder, level):
        if (folder / ".git").exists():
            found.append(folder)
            return
        if level >= depth:
            return
        try:
            children = sorted(p for p in folder.iterdir() if p.is_dir() and p.name not in SKIP and not p.name.startswith("."))
        except OSError:
            return
        for child in children:
            walk(child, level + 1)

    walk(Path(root), 0)
    return found


def repos(ctx):
    by_name = {}
    candidates = gitrun.discover(ctx.layout("repos"))
    for root in configured_roots(ctx):
        candidates += scan(root)
    for path in candidates:
        by_name.setdefault(path.name, path)
    return sorted(by_name.values(), key=lambda p: p.name.lower())

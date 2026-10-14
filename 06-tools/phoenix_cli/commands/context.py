import os
import sys
from datetime import datetime, timezone

from ..core import jsonl
from ..lib import gitrun, select

NAME = "context"
TEXT_EXT = {".py", ".md", ".java", ".scala", ".kt", ".ts", ".js", ".yaml", ".yml", ".json", ".toml", ".sql", ".sh", ".tf", ".xml"}
SKIP = {".git", "node_modules", "venv", ".venv", "__pycache__", "build", "dist", "target"}


def register(sub):
    p = sub.add_parser(NAME, help="pack de contexte minimal (fiches + graphes) pour un prompt")
    p.add_argument("prompt")
    p.add_argument("--repos", default="", help="noms séparés par des virgules (court-circuite la sélection)")
    p.add_argument("--max-tokens", type=int, default=0)
    p.set_defaults(run=run, cmd_name=NAME)


def full_tokens(repo):
    total = 0
    for folder, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP]
        total += sum(os.path.getsize(os.path.join(folder, f)) for f in files if os.path.splitext(f)[1] in TEXT_EXT)
    return total // 4


def _read(path, limit=None):
    return path.read_text(encoding="utf-8", errors="replace")[:limit] if path.is_file() else ""


def run(args, ctx):
    repos = {p.name: p for p in gitrun.discover(ctx.layout("repos"))}
    wiki = ctx.layout("wiki")
    cards = {n: _read(wiki / "repos" / f"{n}.md") for n in repos}
    limit = ctx.cfg["context"]["max_repos"]
    chosen = [n for n in args.repos.split(",") if n in repos]
    if not chosen:
        chosen = (select.via_blinders(args.prompt, list(repos)) or [])[:limit]
    if not chosen:
        docs = {n: cards[n] + _read(repos[n] / "README.md", 2000) for n in repos}
        chosen = select.lexical(args.prompt, docs, limit)
    sections = []
    for name in chosen:
        sections.append((f"{name} (fiche)", cards[name] or _read(repos[name] / "README.md", 2000)))
        graph = _read(wiki / "graphs" / f"{name}.md")
        if graph:
            sections.append((f"{name} (graphe)", graph))
    text, used = select.pack(sections, args.max_tokens or ctx.cfg["context"]["max_tokens"])
    full = sum(full_tokens(repos[n]) for n in chosen)
    print(text)
    print(f"[context] repos={chosen} pack≈{used} tokens vs repos complets≈{full}", file=sys.stderr)
    jsonl.append(ctx.state / "usage.jsonl", {"ts": datetime.now(timezone.utc).isoformat(), "kind": "context",
                                             "name": ",".join(chosen), "pack": used, "full": full})
    return 0

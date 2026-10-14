"""Pack de contexte minimal pour un prompt: sélection des repos, fiches et graphes, plafonnés en tokens."""
import os

from . import select, workspace

TEXT_EXT = {".py", ".md", ".java", ".scala", ".kt", ".ts", ".js", ".yaml", ".yml", ".json", ".toml", ".sql", ".sh", ".tf", ".xml"}
SKIP = {".git", "node_modules", "venv", ".venv", "__pycache__", "build", "dist", "target"}


def full_tokens(repo):
    total = 0
    for folder, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP]
        total += sum(os.path.getsize(os.path.join(folder, f)) for f in files if os.path.splitext(f)[1] in TEXT_EXT)
    return total // 4


def _read(path, limit=None):
    return path.read_text(encoding="utf-8", errors="replace")[:limit] if path and path.is_file() else ""


def build_pack(ctx, prompt, repos_arg="", max_tokens=0):
    repos = {p.name: p for p in workspace.repos(ctx)}
    wiki = ctx.layout("wiki")
    cards = {n: _read(select.find_card(wiki / "repos", n)) for n in repos}
    limit = ctx.cfg["context"]["max_repos"]
    chosen = [n for n in repos_arg.split(",") if n in repos]
    if not chosen:
        chosen = (select.via_blinders(prompt, list(repos)) or [])[:limit]
    if not chosen:
        docs = {n: cards[n] + _read(repos[n] / "README.md", 2000) for n in repos}
        chosen = select.lexical(prompt, docs, limit)
    sections = []
    for name in chosen:
        sections.append((f"{name} (fiche)", cards[name] or _read(repos[name] / "README.md", 2000)))
        graph = _read(wiki / "graphs" / f"{name}.md")
        if graph:
            sections.append((f"{name} (graphe)", graph))
    text, used = select.pack(sections, max_tokens or ctx.cfg["context"]["max_tokens"])
    return {"text": text, "used": used, "full": sum(full_tokens(repos[n]) for n in chosen), "repos": chosen}

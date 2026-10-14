"""Fiche wiki minimale d'un repo, déduite de son README et de son arborescence (sans modèle)."""
import re
from pathlib import Path

SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "build", "dist"}


def first_paragraph(text, limit=400):
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if block and not block.startswith(("#", "[", "|", "```", "<")):
            return " ".join(block.split())[:limit]
    return ""


def make_card(repo):
    repo = Path(repo)
    readme = next((p for p in (repo / "README.md", repo / "README.fr.md") if p.is_file()), None)
    text = readme.read_text(encoding="utf-8", errors="replace") if readme else ""
    dirs = sorted(p.name for p in repo.iterdir() if p.is_dir() and p.name not in SKIP and not p.name.startswith("."))
    return (f"# {repo.name}\n{first_paragraph(text) or '(pas de README: à décrire)'}\n"
            f"Dossiers: {', '.join(dirs) or '-'}\nFiche générée automatiquement: à affiner.\n")

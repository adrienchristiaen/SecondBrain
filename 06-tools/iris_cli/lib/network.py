"""Liens entre repos: un repo qui cite le nom d'un autre dans sa doc ou ses manifestes lui est relié."""
import re
from pathlib import Path

DOCS = ("README.md", "README.fr.md", "ARCHITECTURE.md", "GRAPH.md", "pyproject.toml", "package.json", "pom.xml",
        "build.sbt", "docker-compose.yml", "Chart.yaml", "Makefile")
LIMIT = 20_000


def _text(repo):
    chunks = []
    for name in DOCS:
        path = Path(repo) / name
        if path.is_file():
            chunks.append(path.read_text(encoding="utf-8", errors="replace")[:LIMIT])
    return "\n".join(chunks).lower()


def edges(repos):
    names = [Path(r).name for r in repos]
    texts = {Path(r).name: _text(r) for r in repos}
    found = []
    for a in names:
        for b in names:
            if a == b or len(b) < 4:
                continue
            hits = len(re.findall(rf"(?<![\w-]){re.escape(b.lower())}(?![\w-])", texts[a]))
            if hits:
                found.append({"from": a, "to": b, "weight": hits})
    return found

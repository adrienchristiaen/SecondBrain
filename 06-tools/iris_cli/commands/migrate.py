import shutil
from pathlib import Path

NAME = "migrate"
SKIP = {".git", "node_modules", "__pycache__", ".DS_Store"}
CONTEXT_FILES = {"gemini.md", "claude.md", "agents.md"}
WIKI_FILES = {"memory.md", "architecture.md", "readme.md"}
CODE_EXT = {".py", ".sh", ".toml", ".cfg"}


def register(sub):
    p = sub.add_parser(NAME, help="classe une racine désorganisée dans 01..07 (dry-run par défaut)")
    p.add_argument("source")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(run=run, cmd_name=NAME)


def classify(path):
    """Retourne la clé de layout cible d'une entrée de la racine à migrer."""
    low = path.name.lower()
    if path.is_dir() and (path / ".git").exists():
        return "repos"
    if path.is_dir() and low in ("skills", ".gemini", ".claude"):
        return "skills"
    if low in CONTEXT_FILES:
        return "context"
    if low in WIKI_FILES:
        return "wiki"
    if path.suffix in CODE_EXT or (path.is_dir() and low in ("scripts", "tools", "bin")):
        return "tools"
    return "inbox"


def run(args, ctx):
    src = Path(args.source).resolve()
    plan = [(p, classify(p)) for p in sorted(src.iterdir()) if p.name not in SKIP]
    for path, key in plan:
        dest = ctx.layout(key) / path.name
        print(f"{path.name:30} -> {ctx.cfg['layout'][key]}/")
        if args.apply and not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(dest))
    if not args.apply:
        print("dry-run: relancer avec --apply pour déplacer")
    return 0

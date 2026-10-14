import shutil
from datetime import date
from pathlib import Path

NAME = "archive"


def register(sub):
    p = sub.add_parser(NAME, help="déplace des chemins dans 07-archive/<date>/ (event sourcing)")
    p.add_argument("paths", nargs="+")
    p.set_defaults(run=run, cmd_name=NAME)


def run(args, ctx):
    dest = ctx.layout("archive") / str(date.today())
    dest.mkdir(parents=True, exist_ok=True)
    for raw in args.paths:
        src = Path(raw).resolve()
        if ctx.root not in src.parents:
            raise ValueError(f"{raw} est hors du brain")
        shutil.move(str(src), str(dest / src.name))
        print(f"archivé {src.relative_to(ctx.root)} -> {dest.relative_to(ctx.root)}/")
    return 0

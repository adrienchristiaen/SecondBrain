import re
from datetime import date

NAME = "fr"
HEADER = "| Date | Titre | Fichier | Statut |\n|---|---|---|---|\n"
TEMPLATE = "# {title}\n\n- Date: {day}\n- Statut: open\n\n## Besoin\n\n## Pourquoi un script déterministe\n\n## Critères d'acceptation\n"


def register(sub):
    p = sub.add_parser(NAME, help="feature requests Phoenix CLI (06-tools/feature_request)")
    s = p.add_subparsers(dest="sub", required=True)
    n = s.add_parser("new")
    n.add_argument("title")
    s.add_parser("list")
    p.set_defaults(run=run, cmd_name=NAME)


def folder(ctx):
    return ctx.layout("tools") / "feature_request"


def open_requests(ctx):
    readme = folder(ctx) / "README.md"
    rows = re.findall(r"^\| (\d{4}-\d{2}-\d{2}) \| (.+?) \| (.+?) \| (\w+) \|$", readme.read_text(encoding="utf-8"), re.M) if readme.is_file() else []
    return [r for r in rows if r[3] == "open"]


def run(args, ctx):
    base = folder(ctx)
    if args.sub == "list":
        for day, title, file, _ in open_requests(ctx):
            print(f"{day} {title} ({file})")
        return 0
    base.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")[:50]
    day = str(date.today())
    name = f"{day}-{slug}.md"
    (base / name).write_text(TEMPLATE.format(title=args.title, day=day), encoding="utf-8")
    readme = base / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.is_file() else "# Feature requests\n\nRègles: voir GUIDELINES.md.\n\n" + HEADER
    readme.write_text(text.rstrip("\n") + f"\n| {day} | {args.title} | {name} | open |\n", encoding="utf-8")
    print(f"créé {name}")
    return 0

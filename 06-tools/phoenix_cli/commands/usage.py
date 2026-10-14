import time
from datetime import datetime, timezone

from ..core import jsonl
from ..lib import assets

NAME = "usage"


def register(sub):
    p = sub.add_parser(NAME, help="télémétrie d'usage des skills, MCP, commandes")
    s = p.add_subparsers(dest="sub", required=True)
    log = s.add_parser("log", help="enregistre un usage")
    log.add_argument("kind", choices=["skill", "mcp", "script", "repo", "cmd"])
    log.add_argument("name")
    s.add_parser("audit", help="propose archivage/suppression des actifs inutilisés")
    p.set_defaults(run=run, cmd_name=NAME)


def candidates(ctx, now=None):
    a = ctx.cfg["audit"]
    events = jsonl.read(ctx.state / "usage.jsonl")
    rows = assets.audit(assets.inventory(ctx), events, now or time.time(), a["grace_days"], a["unused_days"], a["protected"])
    return rows


def run(args, ctx):
    if args.sub == "log":
        jsonl.append(ctx.state / "usage.jsonl", {"ts": datetime.now(timezone.utc).isoformat(), "kind": args.kind, "name": args.name})
        return 0
    rows = candidates(ctx)
    todo = [r for r in rows if r["verdict"] != "keep"]
    for r in todo:
        print(f"{r['verdict']:8} {r['kind']:6} {r['name']} (usages={r['uses']}, inactif={r['idle_days']}j, âge={r['age_days']}j)")
    print(f"{len(todo)} candidat(s) sur {len(rows)} actifs. Archiver avec: phoenix archive <chemin>")
    return 0

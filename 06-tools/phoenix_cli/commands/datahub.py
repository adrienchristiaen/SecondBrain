import json

from ..lib import datahubclient

NAME = "datahub"


def register(sub):
    p = sub.add_parser(NAME, help="lineage, santé et versions d'un composant via Data Hub")
    p.add_argument("component")
    p.add_argument("--aspect", choices=["lineage", "health", "versions", "all"], default="all")
    p.set_defaults(run=run, cmd_name=NAME)


def run(args, ctx):
    aspects = ["lineage", "health", "versions"] if args.aspect == "all" else [args.aspect]
    result = {a: datahubclient.fetch(ctx.cfg, args.component, a) for a in aspects}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if all(r["status"] != "error" for r in result.values()) else 1

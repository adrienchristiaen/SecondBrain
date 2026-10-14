import json
from datetime import datetime, timezone

from ..core import jsonl
from ..lib import tokenmath

NAME = "tokens"


def register(sub):
    p = sub.add_parser(NAME, help="journal des tokens et budget restant")
    s = p.add_subparsers(dest="sub", required=True)
    a = s.add_parser("add", help="enregistre une consommation")
    a.add_argument("--model", required=True)
    a.add_argument("--tin", type=int, default=0)
    a.add_argument("--tout", type=int, default=0)
    a.add_argument("--kind", choices=["remote", "local"], default="remote")
    a.add_argument("--session", default="")
    a.add_argument("--action", default="")
    r = s.add_parser("report", help="budget, répartition distant/local")
    r.add_argument("--json", action="store_true")
    p.set_defaults(run=run, cmd_name=NAME)


def ledger(ctx):
    return ctx.state / "tokens.jsonl"


def summary(ctx, today=None):
    today = today or datetime.now(timezone.utc)
    b = ctx.cfg["budget"]
    return tokenmath.summarize(jsonl.read(ledger(ctx)), b["usd"], b["period"], today)


def run(args, ctx):
    if args.sub == "add":
        usd = 0.0 if args.kind == "local" else tokenmath.cost(ctx.cfg["prices"], args.model, args.tin, args.tout)
        jsonl.append(ledger(ctx), {"ts": datetime.now(timezone.utc).isoformat(), "kind": args.kind, "model": args.model,
                                   "tin": args.tin, "tout": args.tout, "usd": usd, "session": args.session, "action": args.action})
        print(f"ok {usd:.4f} USD")
        return 0
    data = summary(ctx)
    print(json.dumps(data, indent=2) if args.json else tokenmath.format_report(data))
    return 0

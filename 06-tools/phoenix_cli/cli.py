"""Point d'entrée: charge le contexte, dispatche, journalise chaque commande (télémétrie d'usage)."""
import argparse
import os
import sys
from datetime import datetime, timezone

from . import registry
from .core import jsonl
from .core.context import load_ctx


def build_parser():
    parser = argparse.ArgumentParser(prog="phoenix", description="Phoenix CLI: outils déterministes du Second Brain")
    sub = parser.add_subparsers(dest="cmd_name")
    for mod in registry.load():
        mod.register(sub)
    return parser


def main(argv=None, ctx=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "run", None):
        parser.print_help()
        return 2
    try:
        ctx = ctx or load_ctx()
        rc = args.run(args, ctx) or 0
    except Exception as exc:  # message court; PHOENIX_DEBUG=1 pour la trace
        if os.environ.get("PHOENIX_DEBUG"):
            raise
        print(f"phoenix: {exc}", file=sys.stderr)
        return 1
    if args.cmd_name != "usage":
        event = {"ts": datetime.now(timezone.utc).isoformat(), "kind": "cmd", "name": args.cmd_name,
                 "sub": getattr(args, "sub", None), "rc": rc}
        jsonl.append(ctx.state / "usage.jsonl", event)
    return rc

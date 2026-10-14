import sys
from datetime import datetime, timezone

from ..core import jsonl
from ..lib import contextpack

NAME = "context"


def register(sub):
    p = sub.add_parser(NAME, help="pack de contexte minimal (fiches + graphes) pour un prompt")
    p.add_argument("prompt")
    p.add_argument("--repos", default="", help="noms séparés par des virgules (court-circuite la sélection)")
    p.add_argument("--max-tokens", type=int, default=0)
    p.set_defaults(run=run, cmd_name=NAME)


def run(args, ctx):
    pack = contextpack.build_pack(ctx, args.prompt, args.repos, args.max_tokens)
    print(pack["text"])
    print(f"[context] repos={pack['repos']} pack≈{pack['used']} tokens vs repos complets≈{pack['full']}", file=sys.stderr)
    jsonl.append(ctx.state / "usage.jsonl", {"ts": datetime.now(timezone.utc).isoformat(), "kind": "context",
                                             "name": ",".join(pack["repos"]), "pack": pack["used"], "full": pack["full"]})
    return 0

from datetime import datetime, timezone

from ..core import jsonl
from ..lib import contextpack, localllm

NAME = "ask"


def register(sub):
    p = sub.add_parser(NAME, help="pose une question à un LLM local, avec contexte réduit optionnel")
    p.add_argument("prompt")
    p.add_argument("--context", action="store_true", help="préfixe le pack de contexte des repos pertinents")
    p.add_argument("--model", default="")
    p.set_defaults(run=run, cmd_name=NAME)


def run(args, ctx):
    prompt = args.prompt
    if args.context:
        prompt = contextpack.build_pack(ctx, args.prompt)["text"] + "\n\n" + args.prompt
    res = localllm.generate(ctx.cfg, prompt, args.model)
    if not res["ok"]:
        raise RuntimeError(res["error"])
    print(res["text"])
    jsonl.append(ctx.state / "tokens.jsonl", {"ts": datetime.now(timezone.utc).isoformat(), "kind": "local", "source": "ask",
                                               "model": res["model"], "tin": res["tin"], "tout": res["tout"], "usd": 0.0,
                                               "session": "", "action": "ask"})
    return 0

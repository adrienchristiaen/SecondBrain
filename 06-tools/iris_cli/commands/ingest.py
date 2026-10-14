from ..lib import ingest

NAME = "ingest"


def register(sub):
    p = sub.add_parser(NAME, help="importe les tokens des logs locaux de Claude Code et Gemini CLI")
    p.add_argument("--home", default="", help="dossier personnel à lire (défaut: ton home)")
    p.set_defaults(run=run, cmd_name=NAME)


def run(args, ctx):
    added = ingest.ingest(ctx, args.home or None)
    print(", ".join(f"{k}: {v} nouveau(x) message(s)" for k, v in added.items()))
    return 0

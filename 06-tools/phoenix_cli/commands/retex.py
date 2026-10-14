import time
from datetime import datetime, timezone

from ..lib import dashstate

NAME = "retex"


def register(sub):
    p = sub.add_parser(NAME, help="constats déterministes de fin de session (alimente le skill session-retex)")
    p.set_defaults(run=run, cmd_name=NAME)


def findings(ctx, now=None):
    state = dashstate.build_state(ctx, now)
    inbox = [p.name for p in ctx.layout("inbox").iterdir() if p.name != ".gitkeep"] if ctx.layout("inbox").is_dir() else []
    failed = [e for e in state["recent"] if e.get("kind") == "cmd" and e.get("rc")]
    return {
        "Commandes en échec (outils manquants ou cassés)": [f"{e['name']} {e.get('sub') or ''}".strip() for e in failed],
        "Actifs à archiver ou revoir": [f"{r['verdict']} {r['kind']} {r['name']}" for r in state["obsolete"]],
        "Repos sans fiche wiki": [r["name"] for r in state["repos"] if not r["card"]],
        "Graphes absents ou périmés": [r["name"] for r in state["repos"] if r["graph"]["stale"]],
        "Inbox à intégrer au wiki": inbox,
        "Feature requests ouvertes": [str(state["feature_requests"])] if state["feature_requests"] else [],
        "Budget": [f"reste {state['tokens']['remaining_usd']:.2f} USD, alerte dépassement" if state["tokens"]["over_budget"]
                   else f"reste {state['tokens']['remaining_usd']:.2f} USD"],
    }


def run(args, ctx):
    now = time.time()
    lines = [f"# Rétex {datetime.fromtimestamp(now, timezone.utc):%Y-%m-%d %H:%M}Z", ""]
    for title, items in findings(ctx, now).items():
        lines.append(f"## {title}")
        lines += [f"- {i}" for i in items] or ["- RAS"]
        lines.append("")
    report = "\n".join(lines)
    day = datetime.fromtimestamp(now, timezone.utc)
    out = ctx.layout("archive") / f"{day:%Y-%m-%d}" / f"retex-{day:%H%M}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    return 0

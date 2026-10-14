"""État du dashboard: une seule structure JSON agrégeant tokens, repos, graphes, liens, obsolescence."""
import shutil
import time
from datetime import datetime, timezone

from ..commands import fr, tokens, usage
from ..core import jsonl
from . import gitrun, graphast, network, select, suggest, workspace

DOCS = ("README.md", "ARCHITECTURE.md", "GRAPH.md")


def build_state(ctx, now=None):
    now = now or time.time()
    paths = workspace.repos(ctx)
    wiki = ctx.layout("wiki")
    repos = []
    for path in paths:
        st = gitrun.status(path, ctx.cfg["git"]["branches"])
        st["graph"] = graphast.freshness(path, wiki / "graphs" / f"{path.name}.md", st["last_commit"], now)
        st["docs"] = [d for d in DOCS if (path / d).is_file()]
        st["card"] = select.find_card(wiki / "repos", path.name) is not None
        repos.append(st)
    events = jsonl.read(ctx.state / "usage.jsonl")
    inbox = [p for p in ctx.layout("inbox").glob("*") if p.name != ".gitkeep"]
    last = max((e["ts"] for e in events if e.get("kind") == "cmd" and e.get("name") == "retex"), default="")
    state = {
        "generated_at": datetime.fromtimestamp(now, timezone.utc).isoformat(),
        "tokens": tokens.summary(ctx, datetime.fromtimestamp(now, timezone.utc)),
        "repos": repos,
        "edges": network.edges(paths),
        "obsolete": [r for r in usage.candidates(ctx, now) if r["verdict"] != "keep"],
        "feature_requests": len(fr.open_requests(ctx)),
        "recent": events[-15:][::-1],
        "inbox": len(inbox),
        "has_mining": (wiki / "insights" / "gemini-mining.md").is_file(),
        "datahub_configured": bool(ctx.cfg["datahub"]["url"]),
        "jira_available": shutil.which("jira-cli") is not None,
        "roots": len(workspace.configured_roots(ctx)),
        "llm_configured": bool(ctx.cfg["llm"]["model"]),
        "has_ingested": any(k in ("claude", "gemini") for k in tokens.summary(ctx)["by_source"]),
        "commands_since_retex": sum(1 for e in events if e.get("kind") == "cmd" and e["ts"] > last),
    }
    state["suggestions"] = suggest.suggest(state)
    return state

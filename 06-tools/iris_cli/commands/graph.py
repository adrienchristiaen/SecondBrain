from datetime import date

from ..lib import gitrun, graphast

NAME = "graph"


def register(sub):
    p = sub.add_parser(NAME, help="génère le graphe d'architecture (AST) d'un repo vers 03-wiki/graphs")
    p.add_argument("repos", nargs="*", help="noms dans 05-repos (défaut: tous)")
    p.set_defaults(run=run, cmd_name=NAME)


def run(args, ctx):
    repos = gitrun.discover(ctx.layout("repos"))
    chosen = [r for r in repos if not args.repos or r.name in args.repos]
    out = ctx.layout("wiki") / "graphs"
    out.mkdir(parents=True, exist_ok=True)
    for repo in chosen:
        graph = graphast.build(repo)
        (out / f"{repo.name}.md").write_text(graphast.render(repo.name, graph, f"Généré le {date.today()}."), encoding="utf-8")
        print(f"{repo.name}: {len(graph['modules'])} modules, {len(graph['edges'])} liens")
    return 0

from ..lib import cardgen, gitrun, select

NAME = "card"


def register(sub):
    p = sub.add_parser(NAME, help="crée les fiches wiki manquantes des repos (README + dossiers)")
    p.set_defaults(run=run, cmd_name=NAME)


def run(args, ctx):
    folder = ctx.layout("wiki") / "repos"
    folder.mkdir(parents=True, exist_ok=True)
    for repo in gitrun.discover(ctx.layout("repos")):
        if select.find_card(folder, repo.name):
            continue
        (folder / f"{repo.name.lower()}.md").write_text(cardgen.make_card(repo), encoding="utf-8")
        print(f"fiche créée: {repo.name}")
    return 0

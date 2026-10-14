import shutil
from datetime import date

from ..lib import assets, miningparse, workspace

NAME = "mine"


def register(sub):
    p = sub.add_parser(NAME, help="extrait les motifs d'un export de chats Gemini")
    p.add_argument("export_dir", help="dossier d'export (Takeout, ~/.gemini/tmp/*/chats, md, jsonl)")
    p.add_argument("--archive", action="store_true", help="copie l'export tel quel dans 07-archive")
    p.set_defaults(run=run, cmd_name=NAME)


def run(args, ctx):
    prompts = miningparse.load_prompts(args.export_dir)
    repo_names = [p.name for p in workspace.repos(ctx)]
    asset_names = [i["name"] for i in assets.inventory(ctx) if i["kind"] in ("skill", "mcp")]
    result = miningparse.analyze(prompts, repo_names, asset_names)
    out = ctx.layout("wiki") / "insights" / "gemini-mining.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(miningparse.render(result, asset_names), encoding="utf-8")
    if args.archive:
        shutil.copytree(args.export_dir, ctx.layout("archive") / str(date.today()) / "gemini-export", dirs_exist_ok=True)
    print(f"{result['n']} prompts analysés -> {out.relative_to(ctx.root)}")
    return 0

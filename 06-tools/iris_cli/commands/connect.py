from pathlib import Path

from ..lib import workspace

NAME = "connect"


def register(sub):
    p = sub.add_parser(NAME, help="connecte une racine locale de repos (lecture sur place, sans clone)")
    p.add_argument("path", nargs="?")
    p.add_argument("--remove", action="store_true")
    p.set_defaults(run=run, cmd_name=NAME)


def run(args, ctx):
    roots = workspace.saved_roots(ctx)
    if args.path:
        target = str(Path(args.path).expanduser().resolve())
        if not Path(target).is_dir():
            raise ValueError(f"{target} n'est pas un dossier")
        roots = [r for r in roots if r != target] if args.remove else roots + [target]
        workspace.save_roots(ctx, roots)
    for root in workspace.configured_roots(ctx):
        print(f"racine {root}: {len(workspace.scan(root))} repo(s)")
    print(f"{len(workspace.repos(ctx))} repo(s) visibles au total")
    return 0

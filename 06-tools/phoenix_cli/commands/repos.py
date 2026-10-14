from ..lib import gitrun

NAME = "repos"


def register(sub):
    p = sub.add_parser(NAME, help="repos de 05-repos: liste, statut, sync, clone")
    s = p.add_subparsers(dest="sub", required=True)
    s.add_parser("status")
    s.add_parser("sync", help="fast-forward de la branche principale de chaque repo")
    c = s.add_parser("clone")
    c.add_argument("url")
    p.set_defaults(run=run, cmd_name=NAME)


def run(args, ctx):
    folder, branches = ctx.layout("repos"), ctx.cfg["git"]["branches"]
    if args.sub == "clone":
        res = gitrun.clone(args.url, folder)
        print(f"{res['name']}: {'ok' if res['ok'] else 'échec'} {res['detail']}")
        return 0 if res["ok"] else 1
    failed = 0
    for path in gitrun.discover(folder):
        if args.sub == "sync":
            r = gitrun.sync(path, branches)
            failed += not r["ok"]
            print(f"{'ok ' if r['ok'] else 'KO '} {r['name']}: {r['detail']}")
        else:
            st = gitrun.status(path, branches)
            print(f"{st['name']:24} {st['branch']:12} défaut={st['default']} dirty={st['dirty']} retard={st['behind']}")
    return 1 if failed else 0

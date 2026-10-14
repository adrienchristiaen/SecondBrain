import json
import shutil
import threading
import time

from ..lib import dashserver, dashstate, gitrun, ingest, workspace

NAME = "dashboard"


def register(sub):
    p = sub.add_parser(NAME, help="dashboard HTML live (serve) ou statique (build)")
    s = p.add_subparsers(dest="sub", required=True)
    s.add_parser("build", help="écrit .brain/dashboard/{index.html,state.json}")
    sv = s.add_parser("serve", help="serveur local 127.0.0.1")
    sv.add_argument("--port", type=int, default=0)
    sv.add_argument("--sync", action="store_true", help="pull des repos au démarrage")
    p.set_defaults(run=run, cmd_name=NAME)


def _ingest_loop(ctx, every=30):
    while True:
        try:
            ingest.ingest(ctx)
        except Exception:  # un journal illisible ne doit pas arrêter le dashboard
            pass
        time.sleep(every)


def run(args, ctx):
    if args.sub == "build":
        out = ctx.state / "dashboard"
        out.mkdir(exist_ok=True)
        shutil.copy(dashserver.PAGE, out / "index.html")
        (out / "state.json").write_text(json.dumps(dashstate.build_state(ctx)), encoding="utf-8")
        print(f"écrit {out.relative_to(ctx.root)}/")
        return 0
    if args.sync:
        for path in workspace.repos(ctx):
            print(gitrun.sync(path, ctx.cfg["git"]["branches"]))
    threading.Thread(target=_ingest_loop, args=(ctx,), daemon=True).start()
    server = dashserver.make_server(ctx, args.port or ctx.cfg["dashboard"]["port"])
    print(f"dashboard sur http://127.0.0.1:{server.server_address[1]}  (Ctrl+C pour arrêter)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
    return 0

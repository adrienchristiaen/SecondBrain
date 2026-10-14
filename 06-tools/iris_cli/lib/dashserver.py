"""Serveur local léger (stdlib), lié à 127.0.0.1: page statique, /api/state, POST /api/sync et POST /api/run (liste blanche).
Les POST exigent l'en-tête X-Iris et un Host local (protection contre les requêtes d'autres sites et le DNS rebinding)."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import actions, dashstate, gitrun

PAGE = Path(__file__).resolve().parent.parent / "web" / "index.html"
LOCAL_HOSTS = ("127.0.0.1", "localhost")


def make_server(ctx, port):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, body, kind="application/json", code=200):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", f"{kind}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _local(self):
            return self.headers.get("Host", "").split(":")[0] in LOCAL_HOSTS

        def do_GET(self):
            if not self._local():
                return self._send("{}", code=403)
            if self.path == "/api/state":
                self._send(json.dumps(dashstate.build_state(ctx)))
            elif self.path == "/api/actions":
                self._send(json.dumps(actions.catalog()))
            elif self.path in ("/", "/index.html"):
                self._send(PAGE.read_text(encoding="utf-8"), "text/html")
            else:
                self._send("{}", code=404)

        def do_POST(self):
            if not self._local() or self.headers.get("X-Iris") != "1":
                return self._send("{}", code=403)
            if self.path == "/api/sync":
                self._send(json.dumps([gitrun.sync(p, ctx.cfg["git"]["branches"]) for p in gitrun.discover(ctx.layout("repos"))]))
            elif self.path == "/api/run":
                try:
                    body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                except ValueError:
                    return self._send("{}", code=400)
                self._send(json.dumps(actions.run(ctx, body.get("action", ""), body.get("params"))))
            else:
                self._send("{}", code=404)

        def log_message(self, *args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)

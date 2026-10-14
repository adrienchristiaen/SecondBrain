"""Serveur local léger (stdlib), lié à 127.0.0.1: sert la page statique, /api/state et POST /api/sync."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import dashstate, gitrun

PAGE = Path(__file__).resolve().parent.parent / "web" / "index.html"


def make_server(ctx, port):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, body, kind="application/json", code=200):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", f"{kind}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/api/state":
                self._send(json.dumps(dashstate.build_state(ctx)))
            elif self.path in ("/", "/index.html"):
                self._send(PAGE.read_text(encoding="utf-8"), "text/html")
            else:
                self._send("{}", code=404)

        def do_POST(self):
            if self.path != "/api/sync":
                return self._send("{}", code=404)
            results = [gitrun.sync(p, ctx.cfg["git"]["branches"]) for p in gitrun.discover(ctx.layout("repos"))]
            self._send(json.dumps(results))

        def log_message(self, *args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)

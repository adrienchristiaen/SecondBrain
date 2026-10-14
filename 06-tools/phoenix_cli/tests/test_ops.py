import io
import json
import tempfile
import threading
import unittest
import urllib.request
from contextlib import redirect_stdout
from pathlib import Path

from phoenix_cli import cli
from phoenix_cli.commands import fr
from phoenix_cli.lib import dashserver, datahubclient
from .helpers import make_ctx, make_repo


class DatahubTest(unittest.TestCase):
    def test_unconfigured(self):
        self.assertEqual(datahubclient.fetch(make_ctx().cfg, "x", "health")["status"], "unconfigured")

    def test_fetch_with_fake_opener(self):
        ctx = make_ctx('[datahub]\nurl = "http://hub"\n')
        seen = {}

        def opener(req, timeout):
            seen["url"] = req.full_url
            return io.BytesIO(b'{"up": true}')
        res = datahubclient.fetch(ctx.cfg, "svc", "lineage", opener=opener)
        self.assertEqual(res, {"status": "ok", "data": {"up": True}})
        self.assertEqual(seen["url"], "http://hub/api/components/svc/lineage")

    def test_error_is_reported_not_raised(self):
        ctx = make_ctx('[datahub]\nurl = "http://hub"\n')

        def opener(req, timeout):
            raise OSError("down")
        self.assertEqual(datahubclient.fetch(ctx.cfg, "s", "health", opener=opener)["status"], "error")


class FileOpsTest(unittest.TestCase):
    def test_feature_request_registered_and_listed(self):
        ctx = make_ctx()
        cli.main(["fr", "new", "Sync Jira tickets"], ctx)
        self.assertEqual(len(fr.open_requests(ctx)), 1)

    def test_migrate_dry_run_then_apply(self):
        ctx = make_ctx()
        src = Path(tempfile.mkdtemp())
        make_repo(src, "app", {"a": "1"})
        (src / "notes.md").write_text("n")
        (src / "run.sh").write_text("echo")
        (src / "memory.md").write_text("m")
        cli.main(["migrate", str(src)], ctx)
        self.assertTrue((src / "notes.md").exists())
        cli.main(["migrate", str(src), "--apply"], ctx)
        self.assertTrue((ctx.layout("repos") / "app" / ".git").exists())
        self.assertTrue((ctx.layout("inbox") / "notes.md").exists())
        self.assertTrue((ctx.layout("tools") / "run.sh").exists())
        self.assertTrue((ctx.layout("wiki") / "memory.md").exists())

    def test_archive_moves_into_dated_folder_and_rejects_outside(self):
        ctx = make_ctx()
        f = ctx.layout("inbox") / "old.md"
        f.write_text("x")
        cli.main(["archive", str(f)], ctx)
        self.assertFalse(f.exists())
        self.assertEqual(len(list(ctx.layout("archive").glob("*/old.md"))), 1)
        self.assertEqual(cli.main(["archive", tempfile.mkdtemp()], ctx), 1)


class DashboardTest(unittest.TestCase):
    def test_state_and_server(self):
        ctx = make_ctx()
        make_repo(ctx.layout("repos"), "alpha", {"README.md": "voir beta-service", "m.py": "def f(): pass\n"})
        make_repo(ctx.layout("repos"), "beta-service", {"README.md": "x"})
        server = dashserver.make_server(ctx, 0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            state = json.load(urllib.request.urlopen(base + "/api/state"))
            self.assertEqual({r["name"] for r in state["repos"]}, {"alpha", "beta-service"})
            self.assertEqual(state["edges"][0]["to"], "beta-service")
            self.assertIn("remaining_usd", state["tokens"])
            self.assertIn("Second Brain", urllib.request.urlopen(base + "/").read().decode())
            sync = json.load(urllib.request.urlopen(urllib.request.Request(base + "/api/sync", method="POST")))
            self.assertEqual(len(sync), 2)
        finally:
            server.shutdown()
            server.server_close()

    def test_build_and_retex(self):
        ctx = make_ctx()
        (ctx.layout("inbox") / "todo.md").write_text("x")
        self.assertEqual(cli.main(["dashboard", "build"], ctx), 0)
        self.assertTrue((ctx.state / "dashboard" / "state.json").is_file())
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli.main(["retex"], ctx)
        self.assertIn("todo.md", buf.getvalue())
        self.assertEqual(len(list(ctx.layout("archive").glob("*/retex-*.md"))), 1)

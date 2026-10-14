import io
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from contextlib import redirect_stdout
from pathlib import Path

from iris_cli import cli
from iris_cli.commands import fr
from iris_cli.lib import dashserver, datahubclient
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
            sync = json.load(urllib.request.urlopen(urllib.request.Request(base + "/api/sync", method="POST", headers={"X-Iris": "1"})))
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


class ActionsTest(unittest.TestCase):
    def test_validation_and_whitelist(self):
        from iris_cli.lib import actions
        ctx = make_ctx()
        self.assertEqual(actions.run(ctx, "rm -rf", {})["code"], 2)
        self.assertIn("ticket", actions.run(ctx, "jira.release_plan", {"ticket": "x; ls"}, which=lambda _: "/bin/jira-cli")["output"])
        self.assertIn("introuvable", actions.run(ctx, "jira.release_plan", {"ticket": "AB-1"}, which=lambda _: None)["output"])

    def test_jira_argv_is_dry_run_only(self):
        from iris_cli.lib import actions
        argv = actions.build_argv(make_ctx(), "jira.deploy_plan", {"ticket": "AB-12", "env": "preprod"}, which=lambda _: "/bin/jira-cli")
        self.assertEqual(argv, ["/bin/jira-cli", "deploy", "AB-12", "--dry-run", "--env", "preprod"])

    def test_iris_action_runs_for_real(self):
        from iris_cli.lib import actions
        ctx = make_ctx()
        ctx.cfg["layout"]["tools"] = str(Path(__file__).resolve().parents[2])
        res = actions.run(ctx, "usage.audit", {})
        self.assertTrue(res["ok"], res)

    def test_server_rejects_missing_header_and_bad_host(self):
        ctx = make_ctx()
        server = dashserver.make_server(ctx, 0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            req = urllib.request.Request(base + "/api/run", data=b"{}", method="POST")
            with self.assertRaises(urllib.error.HTTPError) as c:
                urllib.request.urlopen(req)
            c.exception.close()
            self.assertEqual(c.exception.code, 403)
            req = urllib.request.Request(base + "/api/state", headers={"Host": "evil.example"})
            with self.assertRaises(urllib.error.HTTPError) as c2:
                urllib.request.urlopen(req)
            c2.exception.close()
            req = urllib.request.Request(base + "/api/run", data=json.dumps({"action": "x"}).encode(), method="POST", headers={"X-Iris": "1"})
            self.assertFalse(json.load(urllib.request.urlopen(req))["ok"])
        finally:
            server.shutdown()
            server.server_close()


class SuggestTest(unittest.TestCase):
    def base(self):
        from iris_cli.lib import dashstate
        return dashstate.build_state(make_ctx())

    def test_suggestions_ordered_and_actionable(self):
        ctx = make_ctx()
        make_repo(ctx.layout("repos"), "alpha", {"README.md": "# A\n\nUn service."})
        from iris_cli.lib import dashstate
        titles = [s["title"] for s in dashstate.build_state(ctx)["suggestions"]]
        self.assertIn("Créer les fiches wiki manquantes", titles)
        self.assertIn("Régénérer les graphes", titles)
        self.assertLess(titles.index("Régénérer les graphes"), titles.index("Miner l'historique Gemini"))

    def test_card_command_generates_from_readme(self):
        ctx = make_ctx()
        make_repo(ctx.layout("repos"), "Alpha", {"README.md": "# A\n\nUn service de facturation.\n", "src/x.py": ""})
        cli.main(["card"], ctx)
        card = (ctx.layout("wiki") / "repos" / "alpha.md").read_text()
        self.assertIn("Un service de facturation.", card)
        self.assertIn("Dossiers: src", card)

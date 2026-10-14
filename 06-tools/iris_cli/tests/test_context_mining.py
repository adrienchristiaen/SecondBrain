import json
import tempfile
import unittest
from pathlib import Path

from iris_cli import cli
from iris_cli.lib import miningparse, select
from .helpers import make_ctx, make_repo


class SelectTest(unittest.TestCase):
    def test_lexical_prefers_name_hits(self):
        docs = {"billing-api": "factures et TVA", "news-ia": "podcast quotidien"}
        self.assertEqual(select.lexical("corriger la TVA de billing", docs, 3), ["billing-api"])
        self.assertEqual(select.lexical("zzz", docs, 3), [])

    def test_lexical_ignores_words_present_everywhere_and_weak_matches(self):
        docs = {"blinders": "audit skills gemini cli", "jira": "cli tickets", "news": "cli podcast"}
        self.assertEqual(select.lexical("audit des skills cli", docs, 3), ["blinders"])

    def test_find_card_is_case_insensitive(self):
        folder = Path(tempfile.mkdtemp())
        (folder / "jira-cli.md").write_text("x")
        self.assertEqual(select.find_card(folder, "Jira-CLI").name, "jira-cli.md")
        self.assertIsNone(select.find_card(folder, "other"))

    def test_blinders_absent_returns_none(self):
        self.assertIsNone(select.via_blinders("x", ["a"], which=lambda _: None))

    def test_blinders_output_parsed_in_order(self):
        class R:
            returncode, stdout = 0, "open: kube-deploy\nopen: billing-api\n"
        got = select.via_blinders("x", ["billing-api", "kube-deploy", "other"], runner=lambda *a, **k: R(), which=lambda _: "/bin/blind")
        self.assertEqual(got, ["kube-deploy", "billing-api"])

    def test_pack_truncates_to_budget(self):
        text, used = select.pack([("a", "x\n" * 2000)], 100)
        self.assertLessEqual(used, 100)
        self.assertIn("tronqué", text)

    def test_context_command_picks_repo_and_saves_tokens(self):
        ctx = make_ctx()
        make_repo(ctx.layout("repos"), "billing-api", {"main.py": "x = 1\n" * 3000, "README.md": "factures TVA"})
        make_repo(ctx.layout("repos"), "news-ia", {"README.md": "podcast"})
        (ctx.layout("wiki") / "repos" / "billing-api.md").parent.mkdir(parents=True, exist_ok=True)
        (ctx.layout("wiki") / "repos" / "billing-api.md").write_text("Fiche billing", encoding="utf-8")
        self.assertEqual(cli.main(["context", "TVA billing"], ctx), 0)
        ev = [json.loads(l) for l in (ctx.state / "usage.jsonl").read_text().splitlines()]
        ctx_ev = next(e for e in ev if e["kind"] == "context")
        self.assertEqual(ctx_ev["name"], "billing-api")
        self.assertLess(ctx_ev["pack"], ctx_ev["full"])


class MiningTest(unittest.TestCase):
    def test_takeout_and_cli_formats(self):
        d = Path(tempfile.mkdtemp())
        (d / "MyActivity.json").write_text(json.dumps([
            {"title": "Prompted fix the billing-api retry in `app/retry.py` with `kubectl get pods`", "time": "2026-01-01"},
            {"title": "Viewed something else"},
        ]))
        (d / "chat.json").write_text(json.dumps({"messages": [
            {"type": "user", "content": [{"text": "again billing-api and skill gazette"}]},
            {"type": "gemini", "content": "réponse"},
        ]}))
        prompts = miningparse.load_prompts(d)
        self.assertEqual(len(prompts), 2)
        res = miningparse.analyze(prompts, ["billing-api", "news-ia"], ["gazette", "old-skill"])
        self.assertEqual(res["repos"]["billing-api"], 2)
        self.assertEqual(res["files"]["app/retry.py"], 1)
        self.assertEqual(res["commands"]["kubectl get"], 1)
        md = miningparse.render(res, ["gazette", "old-skill"])
        self.assertIn("- old-skill", md.split("jamais cités")[1])

    def test_mine_command_writes_wiki(self):
        ctx = make_ctx()
        d = Path(tempfile.mkdtemp())
        (d / "a.md").write_text("billing question")
        self.assertEqual(cli.main(["mine", str(d)], ctx), 0)
        self.assertTrue((ctx.layout("wiki") / "insights" / "gemini-mining.md").is_file())

import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from iris_cli import cli
from iris_cli.commands import tokens
from iris_cli.lib import ingest, localllm, mcpserver, repodetail, tokenmath, workspace
from .helpers import make_ctx, make_repo


class WorkspaceTest(unittest.TestCase):
    def test_connect_root_reads_repos_in_place(self):
        ctx = make_ctx()
        root = Path(tempfile.mkdtemp())
        make_repo(root / "team", "api", {"README.md": "# api"})
        make_repo(root, "lib", {"README.md": "# lib"})
        (root / "team" / "api" / "inner").mkdir()
        make_repo(root / "team" / "api" / "inner", "nested", {"a": "1"})
        self.assertEqual(cli.main(["connect", str(root)], ctx), 0)
        self.assertEqual([p.name for p in workspace.repos(ctx)], ["api", "lib"])
        self.assertTrue((root / "lib").exists())
        cli.main(["connect", "--remove", str(root)], ctx)
        self.assertEqual(workspace.repos(ctx), [])

    def test_repo_detail(self):
        ctx = make_ctx()
        make_repo(ctx.layout("repos"), "api", {"README.md": "# api\n\nUn service.", "docs/guide.md": "x", "a.py": "def f(): pass\n"})
        d = repodetail.detail(ctx, "api")
        self.assertEqual([m["path"] for m in d["md_files"]], ["README.md", "docs/guide.md"])
        self.assertEqual(d["commits"][0]["subject"], "init")
        self.assertEqual(d["languages"], {".py": 1})
        self.assertTrue(d["docs_present"]["README.md"])
        self.assertIsNone(repodetail.detail(ctx, "../etc"))


class PriceTest(unittest.TestCase):
    def test_family_match(self):
        prices = {"gemini-pro": {"in": 1.0, "out": 2.0}, "gemini-flash": {"in": 0.1, "out": 0.2}}
        self.assertEqual(tokenmath.price_for(prices, "gemini-2.5-pro"), prices["gemini-pro"])
        self.assertEqual(tokenmath.price_for(prices, "gemini-2.5-flash"), prices["gemini-flash"])
        self.assertEqual(tokenmath.price_for(prices, "claude-sonnet"), {})


class IngestTest(unittest.TestCase):
    def setUp(self):
        self.ctx = make_ctx('[prices."gemini-pro"]\nin = 1.0\nout = 10.0\n')
        self.repo = make_repo(self.ctx.layout("repos"), "api", {"a": "1"})
        self.home = Path(tempfile.mkdtemp())
        slug = "".join(c if c.isalnum() else "-" for c in str(self.repo))
        claude = self.home / ".claude" / "projects" / slug
        claude.mkdir(parents=True)
        lines = [{"type": "assistant", "timestamp": "2026-10-14T10:00:00Z", "message": {"id": "m1", "model": "claude-x",
                  "usage": {"input_tokens": 10, "cache_creation_input_tokens": 5, "cache_read_input_tokens": 100, "output_tokens": 7}}},
                 {"type": "assistant", "timestamp": "2026-10-14T10:00:01Z", "message": {"id": "m1", "model": "claude-x",
                  "usage": {"input_tokens": 10, "cache_creation_input_tokens": 5, "cache_read_input_tokens": 100, "output_tokens": 9}}},
                 {"type": "user", "message": {"content": "hi"}}]
        (claude / "abcdef123.jsonl").write_text("\n".join(json.dumps(l) for l in lines))
        gem = self.home / ".gemini" / "tmp" / hashlib.sha256(str(self.repo).encode()).hexdigest() / "chats"
        gem.mkdir(parents=True)
        (gem / "session-1.json").write_text(json.dumps({"messages": [
            {"type": "gemini", "id": "g1", "model": "gemini-2.5-pro", "timestamp": "2026-10-14T11:00:00Z",
             "tokens": {"input": 1000000, "output": 100000, "thoughts": 100000, "cached": 0}}, {"type": "user"}]}))

    def test_ingest_dedups_and_attributes_to_repo(self):
        added = ingest.ingest(self.ctx, self.home)
        self.assertEqual(added, {"claude": 1, "gemini": 1})
        self.assertEqual(ingest.ingest(self.ctx, self.home), {"claude": 0, "gemini": 0})
        s = tokens.summary(self.ctx)
        self.assertEqual(s["by_action"]["api"], 115 + 9 + 1_100_000 + 100_000)
        self.assertEqual(s["by_source"]["gemini"], 1_200_000)
        self.assertEqual(s["spent_usd"], 3.0)  # 1M in * 1 + 200k out * 10

    def test_changed_file_is_reread_without_duplicates(self):
        ingest.ingest(self.ctx, self.home)
        f = next((self.home / ".claude").rglob("*.jsonl"))
        f.write_text(f.read_text() + "\n" + json.dumps({"type": "assistant", "message": {"id": "m2", "model": "c",
                     "usage": {"input_tokens": 1, "output_tokens": 1}}}))
        self.assertEqual(ingest.ingest(self.ctx, self.home)["claude"], 1)


class McpTest(unittest.TestCase):
    def run_rpc(self, ctx, *msgs):
        out = io.StringIO()
        mcpserver.serve(ctx, io.StringIO("\n".join(json.dumps(m) for m in msgs) + "\n"), out)
        return [json.loads(l) for l in out.getvalue().splitlines()]

    def test_handshake_list_and_tools(self):
        ctx = make_ctx()
        make_repo(ctx.layout("repos"), "billing-api", {"README.md": "factures TVA"})
        res = self.run_rpc(ctx, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}},
                           {"jsonrpc": "2.0", "method": "notifications/initialized"},
                           {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                           {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "iris_context", "arguments": {"prompt": "TVA billing"}}},
                           {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "iris_graph", "arguments": {"repo": "nope"}}},
                           {"jsonrpc": "2.0", "id": 5, "method": "nope"})
        self.assertEqual([r["id"] for r in res], [1, 2, 3, 4, 5])
        self.assertEqual(res[0]["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual({t["name"] for t in res[1]["result"]["tools"]}, {"iris_context", "iris_repos", "iris_graph", "iris_budget"})
        self.assertIn("billing-api", res[2]["result"]["content"][0]["text"])
        self.assertTrue(res[3]["result"]["isError"])
        self.assertEqual(res[4]["error"]["code"], -32601)


class LocalLlmTest(unittest.TestCase):
    def test_no_model_is_a_clear_error(self):
        self.assertFalse(localllm.generate(make_ctx().cfg, "x")["ok"])

    def test_ask_logs_exact_local_tokens(self):
        ctx = make_ctx('[llm]\nmodel = "qwen"\n')
        res = localllm.generate(ctx.cfg, "q", opener=lambda req, timeout: io.BytesIO(
            b'{"response": "ok", "prompt_eval_count": 12, "eval_count": 3}'))
        self.assertEqual((res["text"], res["tin"], res["tout"]), ("ok", 12, 3))


class RepoApiTest(unittest.TestCase):
    def test_repo_endpoint(self):
        import threading
        import urllib.error
        import urllib.request
        from iris_cli.lib import dashserver
        ctx = make_ctx()
        make_repo(ctx.layout("repos"), "api", {"README.md": "# api"})
        server = dashserver.make_server(ctx, 0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            self.assertEqual(json.load(urllib.request.urlopen(base + "/api/repo?name=api"))["name"], "api")
            with self.assertRaises(urllib.error.HTTPError) as c:
                urllib.request.urlopen(base + "/api/repo?name=../x")
            c.exception.close()
            self.assertEqual(c.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()

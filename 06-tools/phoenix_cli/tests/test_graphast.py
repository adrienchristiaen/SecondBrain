import tempfile
import unittest
from pathlib import Path

from phoenix_cli.lib import graphast, network
from .helpers import make_repo

SRC = {
    "src/pkg/__init__.py": "",
    "src/pkg/core.py": '"""Cœur."""\nclass Engine:\n    def run(self): pass\n    def _hidden(self): pass\ndef helper(a, b): pass\n',
    "src/pkg/cli.py": "from .core import Engine\nfrom pkg import core\nimport json\n",
    "src/pkg/broken.py": "def (:\n",
    "tests/test_x.py": "import pkg\n",
}


class GraphTest(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo(tempfile.mkdtemp(), "demo", SRC)

    def test_modules_and_internal_edges(self):
        g = graphast.build(self.repo)
        self.assertNotIn("src/pkg/broken.py", g["modules"])
        self.assertNotIn("tests/test_x.py", g["modules"])
        self.assertEqual(g["modules"]["src/pkg/core.py"]["classes"], [("Engine", ["run"])])
        self.assertIn(("src/pkg/cli.py", "src/pkg/core.py"), g["edges"])

    def test_render_is_compact_markdown(self):
        md = graphast.render("demo", graphast.build(self.repo))
        self.assertIn("## src/pkg/core.py: Cœur.", md)
        self.assertIn("- def helper(a, b)", md)
        self.assertIn("src/pkg/core.py", md.split("dépend de:")[1])

    def test_freshness(self):
        gf = Path(tempfile.mkdtemp()) / "g.md"
        self.assertTrue(graphast.freshness(self.repo, gf)["stale"])
        gf.write_text("x")
        self.assertFalse(graphast.freshness(self.repo, gf, last_commit=gf.stat().st_mtime - 10)["stale"])
        self.assertTrue(graphast.freshness(self.repo, gf, last_commit=gf.stat().st_mtime + 10)["stale"])


class NetworkTest(unittest.TestCase):
    def test_edges_by_name_mention(self):
        tmp = tempfile.mkdtemp()
        a = make_repo(tmp, "billing-api", {"README.md": "Déployé par kube-deploy. Utilise db."})
        b = make_repo(tmp, "kube-deploy", {"README.md": "rien"})
        found = network.edges([a, b])
        self.assertEqual(found, [{"from": "billing-api", "to": "kube-deploy", "weight": 1}])

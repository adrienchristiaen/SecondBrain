import tempfile
import unittest
from pathlib import Path

from iris_cli.core import config, jsonl, paths


class CoreTest(unittest.TestCase):
    def test_find_root_walks_up(self):
        root = Path(tempfile.mkdtemp()).resolve()
        (root / "iris.toml").write_text("")
        deep = root / "a" / "b"
        deep.mkdir(parents=True)
        self.assertEqual(paths.find_root(deep, env={}), root)

    def test_find_root_env_wins_and_validates(self):
        root = Path(tempfile.mkdtemp()).resolve()
        with self.assertRaises(paths.RootNotFound):
            paths.find_root(env={"IRIS_ROOT": str(root)})
        (root / "iris.toml").write_text("")
        self.assertEqual(paths.find_root(env={"IRIS_ROOT": str(root)}), root)

    def test_config_deep_merge(self):
        root = Path(tempfile.mkdtemp())
        (root / "iris.toml").write_text('[budget]\nusd = 50\n')
        cfg = config.load(root)
        self.assertEqual(cfg["budget"], {"usd": 50, "period": "year"})
        self.assertEqual(cfg["layout"]["wiki"], "03-wiki")

    def test_jsonl_skips_corrupt_lines(self):
        path = Path(tempfile.mkdtemp()) / "x.jsonl"
        jsonl.append(path, {"a": 1})
        with path.open("a") as f:
            f.write("not json\n")
        jsonl.append(path, {"a": 2})
        self.assertEqual([r["a"] for r in jsonl.read(path)], [1, 2])
        self.assertEqual(jsonl.read(path.with_name("none.jsonl")), [])

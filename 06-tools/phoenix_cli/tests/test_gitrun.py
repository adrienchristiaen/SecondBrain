import tempfile
import unittest
from pathlib import Path

from phoenix_cli.lib import gitrun
from .helpers import make_repo, sh


class GitRunTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        sh("init", "--bare", "-b", "main", str(self.tmp / "origin.git"), cwd=self.tmp)
        self.work = make_repo(self.tmp, "work", {"a.txt": "1"})
        sh("remote", "add", "origin", str(self.tmp / "origin.git"), cwd=self.work)
        sh("push", "origin", "main", cwd=self.work)
        (self.tmp / "repos").mkdir()
        sh("clone", str(self.tmp / "origin.git"), str(self.tmp / "repos" / "mirror"), cwd=self.tmp)
        self.mirror = self.tmp / "repos" / "mirror"

    def push_new_commit(self):
        (self.work / "b.txt").write_text("2")
        sh("add", ".", cwd=self.work)
        sh("commit", "-m", "b", cwd=self.work)
        sh("push", "origin", "main", cwd=self.work)

    def test_discover_and_status(self):
        self.assertEqual([p.name for p in gitrun.discover(self.tmp / "repos")], ["mirror"])
        st = gitrun.status(self.mirror, ["main"])
        self.assertEqual((st["default"], st["dirty"], st["behind"]), ("main", False, 0))

    def test_sync_fast_forwards_default_branch(self):
        self.push_new_commit()
        res = gitrun.sync(self.mirror, ["main"])
        self.assertTrue(res["ok"], res)
        self.assertTrue((self.mirror / "b.txt").exists())

    def test_sync_off_default_branch_does_not_checkout(self):
        sh("checkout", "-b", "feature", cwd=self.mirror)
        self.push_new_commit()
        self.assertTrue(gitrun.sync(self.mirror, ["main"])["ok"])
        self.assertEqual(gitrun.current_branch(self.mirror), "feature")
        self.assertEqual(gitrun.status(self.mirror, ["main"])["behind"], 0)

    def test_sync_refuses_dirty_default_branch(self):
        self.push_new_commit()
        (self.mirror / "a.txt").write_text("local edit")
        self.assertFalse(gitrun.sync(self.mirror, ["main"])["ok"])

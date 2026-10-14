import subprocess
import tempfile
from pathlib import Path

from iris_cli.core import config
from iris_cli.core.context import Ctx


def make_ctx(extra_toml=""):
    root = Path(tempfile.mkdtemp())
    (root / "iris.toml").write_text(extra_toml, encoding="utf-8")
    for d in config.DEFAULTS["layout"].values():
        (root / d).mkdir(parents=True, exist_ok=True)
    return Ctx(root, config.load(root))


def sh(*args, cwd):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True, capture_output=True)


def make_repo(folder, name, files):
    """Repo git local avec un commit, sur la branche main."""
    path = Path(folder) / name
    path.mkdir(parents=True)
    sh("init", "-b", "main", cwd=path)
    for rel, text in files.items():
        (path / rel).parent.mkdir(parents=True, exist_ok=True)
        (path / rel).write_text(text, encoding="utf-8")
    sh("add", ".", cwd=path)
    sh("commit", "-m", "init", cwd=path)
    return path

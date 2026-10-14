"""Trouve la racine du brain sans chemin en dur: variable d'environnement, sinon remontée depuis le cwd."""
import os
from pathlib import Path

MARKER = "iris.toml"


class RootNotFound(Exception):
    pass


def find_root(start=None, env=None):
    env = os.environ if env is None else env
    if env.get("IRIS_ROOT"):
        root = Path(env["IRIS_ROOT"]).resolve()
        if (root / MARKER).is_file():
            return root
        raise RootNotFound(f"IRIS_ROOT={root} ne contient pas {MARKER}")
    here = Path(start or Path.cwd()).resolve()
    for folder in (here, *here.parents):
        if (folder / MARKER).is_file():
            return folder
    raise RootNotFound(f"{MARKER} introuvable depuis {here}; lance iris dans le brain ou définis IRIS_ROOT")

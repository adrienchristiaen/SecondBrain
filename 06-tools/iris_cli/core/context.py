from dataclasses import dataclass
from pathlib import Path

from . import config, paths


@dataclass
class Ctx:
    root: Path
    cfg: dict

    def layout(self, key):
        return self.root / self.cfg["layout"][key]

    @property
    def state(self):
        folder = self.root / ".brain"
        folder.mkdir(exist_ok=True)
        return folder


def load_ctx(start=None):
    root = paths.find_root(start)
    return Ctx(root, config.load(root))

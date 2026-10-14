"""Découvre les modules de commandes: aucune liste à maintenir."""
import importlib
import pkgutil

from . import commands


def load():
    found = []
    for info in pkgutil.iter_modules(commands.__path__):
        mod = importlib.import_module(f"{commands.__name__}.{info.name}")
        if hasattr(mod, "NAME") and hasattr(mod, "register"):
            found.append(mod)
    return sorted(found, key=lambda m: m.NAME)

"""Configuration: valeurs par défaut fusionnées avec phoenix.toml (tomllib, stdlib)."""
import tomllib
from copy import deepcopy

DEFAULTS = {
    "layout": {
        "inbox": "01-inbox", "context": "02-context", "wiki": "03-wiki", "workspaces": "04-workspaces",
        "repos": "05-repos", "tools": "06-tools", "archive": "07-archive", "skills": ".gemini/skills",
    },
    "budget": {"usd": 200.0, "period": "year"},
    "prices": {"local": {"in": 0.0, "out": 0.0}},
    "git": {"branches": ["main", "master", "develop"]},
    "audit": {"grace_days": 30, "unused_days": 60, "protected": ["usage", "retex", "tokens"]},
    "context": {"max_tokens": 6000, "max_repos": 3},
    "datahub": {
        "url": "", "token_env": "DATAHUB_TOKEN",
        "endpoints": {
            "lineage": "/api/components/{name}/lineage",
            "health": "/api/components/{name}/health",
            "versions": "/api/components/{name}/versions",
        },
    },
    "dashboard": {"port": 8765},
}


def merge(base, extra):
    out = deepcopy(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = merge(out[key], value)
        else:
            out[key] = value
    return out


def load(root):
    path = root / "phoenix.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    return merge(DEFAULTS, data)

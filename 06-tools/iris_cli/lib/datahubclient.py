"""Client Data Hub minimal: lineage, santé, versions. Les endpoints sont configurables (iris.toml)."""
import json
import os
import urllib.request


def fetch(cfg, name, aspect, opener=urllib.request.urlopen):
    hub = cfg["datahub"]
    if not hub["url"]:
        return {"status": "unconfigured", "hint": "renseigner [datahub] url dans iris.toml"}
    url = hub["url"].rstrip("/") + hub["endpoints"][aspect].format(name=name)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    token = os.environ.get(hub["token_env"], "")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with opener(req, timeout=10) as res:
            return {"status": "ok", "data": json.load(res)}
    except (OSError, ValueError) as exc:
        return {"status": "error", "detail": str(exc)}

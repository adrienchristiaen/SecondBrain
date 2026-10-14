"""Actions lançables depuis le navigateur: liste blanche, argv sans shell, aucune action qui modifie Jira ou GitLab.
Les étapes qui agissent (release, deploy) restent dans le terminal avec leur confirmation: ici, seulement leurs plans (--dry-run)."""
import os
import re
import shutil
import subprocess
import sys

TICKET = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")
ENV = re.compile(r"^[a-z0-9-]{2,20}$")
IRIS = {"repos.sync": ["repos", "sync"], "graph.build": ["graph"], "usage.audit": ["usage", "audit"],
           "retex.run": ["retex"], "cards.build": ["card"]}
LABELS = {"repos.sync": "Synchroniser les repos", "graph.build": "Régénérer les graphes", "usage.audit": "Auditer les actifs",
          "retex.run": "Lancer le rétex", "cards.build": "Créer les fiches manquantes",
          "context.preview": "Prévisualiser un pack de contexte", "jira.release_plan": "Plan de release (dry-run)",
          "jira.deploy_plan": "Plan de déploiement (dry-run)"}


def catalog():
    return [{"name": n, "label": l} for n, l in LABELS.items()]


def build_argv(ctx, name, params, which=shutil.which):
    if name in IRIS:
        return [sys.executable, "-m", "iris_cli", *IRIS[name]]
    if name == "context.preview":
        prompt = str(params.get("prompt", "")).strip()
        if not 0 < len(prompt) <= 2000:
            raise ValueError("prompt requis (2000 caractères max)")
        return [sys.executable, "-m", "iris_cli", "context", prompt]
    if name in ("jira.release_plan", "jira.deploy_plan"):
        ticket = str(params.get("ticket", ""))
        if not TICKET.match(ticket):
            raise ValueError("clé de ticket invalide (ex: PROJ-123)")
        exe = which("jira-cli")
        if not exe:
            raise ValueError("jira-cli introuvable dans le PATH (pip install -e 05-repos/Jira-CLI)")
        verb = "release" if name == "jira.release_plan" else "deploy"
        argv = [exe, verb, ticket, "--dry-run"]
        env = params.get("env")
        if verb == "deploy" and env:
            if not ENV.match(str(env)):
                raise ValueError("environnement invalide")
            argv += ["--env", env]
        return argv
    raise ValueError(f"action inconnue: {name}")


def run(ctx, name, params, runner=subprocess.run, which=shutil.which):
    try:
        argv = build_argv(ctx, name, params or {}, which)
    except ValueError as exc:
        return {"ok": False, "code": 2, "output": str(exc)}
    env = {**os.environ, "IRIS_ROOT": str(ctx.root), "PYTHONPATH": str(ctx.layout("tools"))}
    try:
        res = runner(argv, cwd=ctx.root, env=env, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "code": 1, "output": str(exc)}
    return {"ok": res.returncode == 0, "code": res.returncode, "output": (res.stdout + res.stderr)[-20000:]}

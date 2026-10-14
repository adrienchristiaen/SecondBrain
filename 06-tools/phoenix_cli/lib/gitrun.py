"""Runner Git: découverte des repos, statut, synchronisation fast-forward de la branche principale."""
import subprocess
from pathlib import Path


def git(args, cwd, timeout=120):
    try:
        r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def discover(repos_dir):
    folder = Path(repos_dir)
    return sorted(p for p in folder.iterdir() if (p / ".git").exists()) if folder.is_dir() else []


def current_branch(path):
    return git(["rev-parse", "--abbrev-ref", "HEAD"], path)[1]


def default_branch(path, preferred):
    rc, out, _ = git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], path)
    if rc == 0 and "/" in out:
        return out.split("/", 1)[1]
    for branch in preferred:
        if git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], path)[0] == 0:
            return branch
    return current_branch(path)


def status(path, preferred):
    default = default_branch(path, preferred)
    rc, out, _ = git(["rev-list", "--left-right", "--count", f"{default}...origin/{default}"], path)
    ahead, behind = (int(x) for x in out.split()) if rc == 0 else (None, None)
    rc, stamp, _ = git(["log", "-1", "--format=%ct"], path)
    return {"name": path.name, "branch": current_branch(path), "default": default,
            "dirty": bool(git(["status", "--porcelain"], path)[1]), "ahead": ahead, "behind": behind,
            "last_commit": int(stamp) if rc == 0 and stamp.isdigit() else None}


def sync(path, preferred):
    st = status(path, preferred)
    rc, _, err = git(["fetch", "origin", "--prune"], path)
    if rc:
        return {"name": path.name, "ok": False, "detail": err}
    default = st["default"]
    if st["branch"] == default:
        if st["dirty"]:
            return {"name": path.name, "ok": False, "detail": "modifications locales, pull ignoré"}
        rc, out, err = git(["merge", "--ff-only", f"origin/{default}"], path)
    else:
        rc, out, err = git(["fetch", "origin", f"{default}:{default}"], path)
    return {"name": path.name, "ok": rc == 0, "branch": default, "detail": err or out}


def clone(url, repos_dir):
    name = url.rstrip("/").removesuffix(".git").rsplit("/", 1)[-1]
    dest = Path(repos_dir) / name
    if dest.exists():
        return {"name": name, "ok": True, "detail": "déjà présent"}
    rc, _, err = git(["clone", url, str(dest)], Path(repos_dir), timeout=600)
    return {"name": name, "ok": rc == 0, "detail": err}

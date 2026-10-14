"""Graphe d'architecture par AST (stdlib): modules, classes, fonctions, imports internes. Sans modèle."""
import ast
import os
import time
from pathlib import Path

SKIP = {".git", "node_modules", "venv", ".venv", "__pycache__", "build", "dist", ".tox", "tests", "graphify-out"}
MAX_FILES, MAX_BYTES = 2000, 200_000


def summarize_source(src, module, is_pkg=False):
    tree = ast.parse(src)
    info = {"doc": (ast.get_docstring(tree) or "").split("\n")[0][:100], "classes": [], "funcs": [], "imports": []}
    base = module.split(".") if is_pkg else module.split(".")[:-1]
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and not m.name.startswith("_")]
            info["classes"].append((node.name, methods[:8]))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            info["funcs"].append((node.name, [a.arg for a in node.args.args][:5]))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            info["imports"] += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            prefix = base[: len(base) - node.level + 1] if node.level else []
            mod = ".".join(prefix + ([node.module] if node.module else []))
            info["imports"] += [mod] + [f"{mod}.{a.name}" if mod else a.name for a in node.names]
    return info


def _dotted(rel):
    parts = list(Path(rel).with_suffix("").parts)
    is_pkg = parts[-1] == "__init__"
    return ".".join(parts[:-1] if is_pkg else parts), is_pkg


def _py_files(repo):
    count = 0
    for folder, dirs, files in os.walk(repo):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        for f in sorted(files):
            path = Path(folder) / f
            if f.endswith(".py") and path.stat().st_size <= MAX_BYTES and count < MAX_FILES:
                count += 1
                yield path


def build(repo):
    repo = Path(repo)
    modules = {}
    for path in _py_files(repo):
        rel = path.relative_to(repo).as_posix()
        dotted, is_pkg = _dotted(rel)
        try:
            modules[rel] = (dotted, summarize_source(path.read_text(encoding="utf-8", errors="replace"), dotted, is_pkg))
        except SyntaxError:
            continue
    index = {}
    for rel, (dotted, _) in modules.items():
        parts = dotted.split(".")
        for i in range(len(parts)):
            index.setdefault(".".join(parts[i:]), rel)
    edges = set()
    for rel, (_, info) in modules.items():
        for name in info["imports"]:
            target = index.get(name)
            if target and target != rel:
                edges.add((rel, target))
    return {"modules": {rel: info for rel, (_, info) in modules.items()}, "edges": sorted(edges)}


def render(name, graph, generated="") -> str:
    out = [f"# Graphe: {name}", f"_AST Python, {len(graph['modules'])} modules, {len(graph['edges'])} dépendances internes. {generated}_", ""]
    deps = {}
    for a, b in graph["edges"]:
        deps.setdefault(a, []).append(b)
    for rel, info in graph["modules"].items():
        out.append(f"## {rel}" + (f": {info['doc']}" if info["doc"] else ""))
        out += [f"- class {n}: {', '.join(m) or '-'}" for n, m in info["classes"]]
        out += [f"- def {n}({', '.join(a)})" for n, a in info["funcs"]]
        if rel in deps:
            out.append("- dépend de: " + ", ".join(deps[rel]))
    return "\n".join(out) + "\n"


def freshness(repo, graph_file, last_commit=None, now=None):
    now = now or time.time()
    repo, graph_file = Path(repo), Path(graph_file)
    external = (repo / "graphify-out").is_dir()
    if not graph_file.is_file():
        return {"exists": False, "external": external, "age_days": None, "stale": True}
    stamp = graph_file.stat().st_mtime
    return {"exists": True, "external": external, "age_days": round((now - stamp) / 86400, 1),
            "stale": bool(last_commit and last_commit > stamp)}

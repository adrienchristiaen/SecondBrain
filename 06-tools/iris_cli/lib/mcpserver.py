"""Serveur MCP minimal (stdio, JSON-RPC ligne à ligne): permet à Gemini CLI, Claude Code ou Cursor d'appeler Iris
pour obtenir un contexte réduit au lieu de lire des repos entiers."""
import json
from datetime import datetime, timezone

from ..commands import tokens
from ..core import jsonl
from . import contextpack, gitrun, graphast, workspace

TOOLS = [
    {"name": "iris_context", "description": "Pack de contexte minimal (fiches + graphes d'architecture) pour une tâche. À appeler avant de lire du code.",
     "inputSchema": {"type": "object", "properties": {"prompt": {"type": "string"}, "max_tokens": {"type": "integer"}}, "required": ["prompt"]}},
    {"name": "iris_repos", "description": "Repos connectés: branche, copie locale modifiée, retard.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "iris_graph", "description": "Graphe d'architecture (AST) d'un repo Python.",
     "inputSchema": {"type": "object", "properties": {"repo": {"type": "string"}}, "required": ["repo"]}},
    {"name": "iris_budget", "description": "Budget de tokens restant, projection et répartition.", "inputSchema": {"type": "object", "properties": {}}},
]


def call(ctx, name, args):
    if name == "iris_context":
        return contextpack.build_pack(ctx, args["prompt"], max_tokens=int(args.get("max_tokens") or 0))["text"]
    if name == "iris_repos":
        return json.dumps([gitrun.status(p, ctx.cfg["git"]["branches"]) for p in workspace.repos(ctx)], ensure_ascii=False)
    if name == "iris_graph":
        path = next((p for p in workspace.repos(ctx) if p.name == args["repo"]), None)
        if path is None:
            raise ValueError("repo inconnu")
        return graphast.render(path.name, graphast.build(path))
    if name == "iris_budget":
        return json.dumps(tokens.summary(ctx), ensure_ascii=False)
    raise ValueError(f"outil inconnu: {name}")


def handle(ctx, msg):
    method, mid = msg.get("method"), msg.get("id")
    if mid is None:
        return None  # notification
    if method == "initialize":
        result = {"protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}},
                  "serverInfo": {"name": "iris", "version": "0.1"}}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = msg.get("params", {})
        try:
            text, error = call(ctx, params.get("name", ""), params.get("arguments") or {}), False
        except (ValueError, KeyError) as exc:
            text, error = f"erreur: {exc}", True
        jsonl.append(ctx.state / "usage.jsonl", {"ts": datetime.now(timezone.utc).isoformat(), "kind": "mcp", "name": "iris"})
        result = {"content": [{"type": "text", "text": text}], "isError": error}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"méthode inconnue: {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def serve(ctx, stdin, stdout):
    for line in stdin:
        if not line.strip():
            continue
        try:
            reply = handle(ctx, json.loads(line))
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON invalide"}}
        if reply is not None:
            stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            stdout.flush()

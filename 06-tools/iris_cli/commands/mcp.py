import json
import sys

from ..lib import mcpserver

NAME = "mcp"


def register(sub):
    p = sub.add_parser(NAME, help="serveur MCP stdio (Gemini CLI, Claude Code, Cursor)")
    p.add_argument("--print-config", action="store_true", help="affiche comment l'enregistrer dans chaque CLI")
    p.set_defaults(run=run, cmd_name=NAME)


def run(args, ctx):
    launcher = str(ctx.root / "iris")
    if args.print_config:
        entry = {"mcpServers": {"iris": {"command": launcher, "args": ["mcp"]}}}
        print("Gemini CLI (settings.json) et Cursor (.cursor/mcp.json):\n" + json.dumps(entry, indent=2))
        print(f"\nClaude Code:\n  claude mcp add iris -- {launcher} mcp")
        return 0
    mcpserver.serve(ctx, sys.stdin, sys.stdout)
    return 0

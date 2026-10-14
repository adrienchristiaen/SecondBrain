# Second Brain

Cerveau de développement *local-first*: Markdown plat (lisible par humains et LLM) + moteur déterministe **Iris CLI** (Python stdlib, zéro dépendance) pour ne dépenser des tokens distants que sur la réflexion complexe.

## Brancher tes repos et tes CLI

```bash
./iris connect <dossier-racine-de-tes-repos>   # lecture sur place, aucun clone
./iris ingest                                  # tokens de Claude Code et Gemini CLI (lus dans leurs journaux locaux)
./iris mcp --print-config                      # enregistre Iris comme outil dans Gemini CLI, Claude Code, Cursor
./iris ask --context "question"                # LLM local (Ollama), tokens comptés exactement
```

## Démarrage

```bash
./iris repos clone https://github.com/adrienchristiaen/blinders   # clone dans 05-repos (git-ignoré)
./iris repos sync          # fast-forward de main/master/develop de chaque repo
./iris graph               # graphes AST -> 03-wiki/graphs/
./iris context "ton prompt" # pack minimal (fiches + graphes) à donner au modèle distant
./iris dashboard serve --sync   # http://127.0.0.1:8765
make test
```

Python ≥ 3.11. La racine est trouvée par `iris.toml` (remontée depuis le cwd) ou `IRIS_ROOT`: aucun chemin en dur.

## Arborescence

| Dossier | Rôle |
|---|---|
| `01-inbox/` | vrac, à trier |
| `02-context/` | qui je suis, rôle, instructions de base |
| `03-wiki/` | connaissance structurée (fiches repos, graphes, insights, décisions) |
| `04-workspaces/` | dossiers temporaires par sujet |
| `05-repos/` | repos clonés (git-ignoré) |
| `06-tools/` | `iris_cli/`, `feature_request/` (+ Blinders, Graphify, Data Hub via Iris) |
| `07-archive/` | dump tel quel daté de ce qui est intégré au wiki |
| `.gemini/skills/` | skills (`session-retex`, `executing-2nd-brain-processes`) |

Détails: [ARCHITECTURE.md](ARCHITECTURE.md), carte du code: [GRAPH.md](GRAPH.md), plan et roadmap: [03-wiki/decisions/0001-plan.md](03-wiki/decisions/0001-plan.md).

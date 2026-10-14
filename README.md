# Second Brain

Cerveau de développement *local-first*: Markdown plat (lisible par humains et LLM) + moteur déterministe **Phoenix CLI** (Python stdlib, zéro dépendance) pour ne dépenser des tokens distants que sur la réflexion complexe.

## Démarrage

```bash
./phoenix repos clone https://github.com/adrienchristiaen/blinders   # clone dans 05-repos (git-ignoré)
./phoenix repos sync          # fast-forward de main/master/develop de chaque repo
./phoenix graph               # graphes AST -> 03-wiki/graphs/
./phoenix context "ton prompt" # pack minimal (fiches + graphes) à donner au modèle distant
./phoenix dashboard serve --sync   # http://127.0.0.1:8765
make test
```

Python ≥ 3.11. La racine est trouvée par `phoenix.toml` (remontée depuis le cwd) ou `PHOENIX_ROOT`: aucun chemin en dur.

## Arborescence

| Dossier | Rôle |
|---|---|
| `01-inbox/` | vrac, à trier |
| `02-context/` | qui je suis, rôle, instructions de base |
| `03-wiki/` | connaissance structurée (fiches repos, graphes, insights, décisions) |
| `04-workspaces/` | dossiers temporaires par sujet |
| `05-repos/` | repos clonés (git-ignoré) |
| `06-tools/` | `phoenix_cli/`, `feature_request/` (+ Blinders, Graphify, Data Hub via Phoenix) |
| `07-archive/` | dump tel quel daté de ce qui est intégré au wiki |
| `.gemini/skills/` | skills (`session-retex`, `executing-2nd-brain-processes`) |

Détails: [ARCHITECTURE.md](ARCHITECTURE.md), carte du code: [GRAPH.md](GRAPH.md), plan et roadmap: [03-wiki/decisions/0001-plan.md](03-wiki/decisions/0001-plan.md).

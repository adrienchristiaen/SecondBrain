# Architecture

## Principe
Règle d'or: tout ce qui est déterministe est une commande Python de Phoenix CLI, pas un prompt. Le LLM ne sert qu'au raisonnement et à la génération.

## Pipeline de contexte (le gain de tokens)
```
prompt → Blinders (local, `blind select`) ou recoupement lexical stdlib
       → repos retenus uniquement
       → fiche wiki + graphe AST de chaque repo (≈ quelques centaines de tokens)
       → budget plafonné (`[context] max_tokens`)
       → modèle distant
```
`phoenix context` affiche sur stderr le gain: tokens du pack vs tokens des repos complets, et l'enregistre.

## Phoenix CLI (`06-tools/phoenix_cli/`)
Une commande = un module dans `commands/` exposant `NAME` et `register(sub)`; `registry.py` les découvre seul. La logique pure vit dans `lib/`, testée sans I/O quand c'est possible. Aucun fichier > 150 lignes.

| Commande | Rôle | Module |
|---|---|---|
| `tokens add/report` | journal, coût, budget restant, projection | `lib/tokenmath.py` |
| `repos status/sync/clone` | runner Git (ff-only, jamais de checkout forcé) | `lib/gitrun.py` |
| `graph` | graphe d'architecture par AST → `03-wiki/graphs` | `lib/graphast.py` |
| `context` | sélection + pack de contexte minimal | `lib/select.py` |
| `mine <dossier>` | motifs des chats Gemini (export en argument) | `lib/miningparse.py` |
| `usage log/audit` | télémétrie et propositions de décommissionnement | `lib/assets.py` |
| `datahub <composant>` | lineage, santé, versions | `lib/datahubclient.py` |
| `dashboard build/serve` | dashboard live ou statique | `lib/dashstate.py`, `lib/dashserver.py`, `web/index.html` |
| `retex` | constats déterministes de fin de session → `07-archive` | `commands/retex.py` |
| `fr new/list` | feature requests | `commands/fr.py` |
| `migrate`, `archive` | réorganisation et event sourcing | `commands/` |

Chaque commande lancée est journalisée dans `.brain/usage.jsonl`: c'est ce qui permet à `usage audit` de repérer les commandes, skills et MCP jamais utilisés.

## Intégrations
- **Blinders**: utilisé tel quel s'il est installé (`blind select`), sinon repli lexical. Blinders fournit aussi `blind audit`, `blind graph` (Graphify) et `blind stats`; Phoenix ne les duplique pas.
- **Graphify**: la santé est lue depuis `graphify-out/` du repo si présent; Phoenix produit son propre graphe AST léger pour Python.
- **Jira-CLI**: repo géré comme les autres (fiche + graphe); un futur `phoenix jira` pourra l'appeler en sous-processus.
- **Data Hub**: URL et endpoints dans `phoenix.toml` (`[datahub]`), token via variable d'environnement. Les chemins d'API par défaut sont des hypothèses à ajuster à ton portail.

## Dashboard
Serveur `http.server` lié à 127.0.0.1 (stdlib), page unique sans dépendance. `GET /api/state` (agrégat JSON), `POST /api/sync` (pull des repos). `dashboard build` produit une version statique lisible hors serveur (sans bouton de sync). Rafraîchissement toutes les 5 s.

## Données locales
`.brain/` (git-ignoré): `tokens.jsonl`, `usage.jsonl`, `dashboard/`.

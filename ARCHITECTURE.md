# Architecture

## Principe
Règle d'or: tout ce qui est déterministe est une commande Python de Iris CLI, pas un prompt. Le LLM ne sert qu'au raisonnement et à la génération.

## Pipeline de contexte (le gain de tokens)
```
prompt → Blinders (local, `blind select`) ou recoupement lexical stdlib
       → repos retenus uniquement
       → fiche wiki + graphe AST de chaque repo (≈ quelques centaines de tokens)
       → budget plafonné (`[context] max_tokens`)
       → modèle distant
```
`iris context` affiche sur stderr le gain: tokens du pack vs tokens des repos complets, et l'enregistre.

## Iris CLI (`06-tools/iris_cli/`)
Une commande = un module dans `commands/` exposant `NAME` et `register(sub)`; `registry.py` les découvre seul. La logique pure vit dans `lib/`, testée sans I/O quand c'est possible. Aucun fichier > 150 lignes.

| Commande | Rôle | Module |
|---|---|---|
| `connect` | connecte une racine locale de repos (lue sur place) | `lib/workspace.py` |
| `ingest` | tokens des journaux Claude Code / Gemini CLI | `lib/ingest.py` |
| `mcp` | serveur MCP stdio | `lib/mcpserver.py` |
| `ask` | LLM local (Ollama) | `lib/localllm.py` |
| `tokens add/report` | journal, coût, budget restant, projection | `lib/tokenmath.py` |
| `repos status/sync/clone` | runner Git (ff-only, jamais de checkout forcé) | `lib/gitrun.py` |
| `graph` | graphe d'architecture par AST → `03-wiki/graphs` | `lib/graphast.py` |
| `context` | sélection + pack de contexte minimal | `lib/select.py` |
| `mine <dossier>` | motifs des chats Gemini (export en argument) | `lib/miningparse.py` |
| `usage log/audit` | télémétrie et propositions de décommissionnement | `lib/assets.py` |
| `datahub <composant>` | lineage, santé, versions | `lib/datahubclient.py` |
| `dashboard build/serve` | dashboard live ou statique | `lib/dashstate.py`, `lib/dashserver.py`, `web/index.html` |
| `card` | fiches wiki manquantes depuis README + dossiers | `lib/cardgen.py` |
| `retex` | constats déterministes de fin de session → `07-archive` | `commands/retex.py` |
| `fr new/list` | feature requests | `commands/fr.py` |
| `migrate`, `archive` | réorganisation et event sourcing | `commands/` |

Chaque commande lancée est journalisée dans `.brain/usage.jsonl`: c'est ce qui permet à `usage audit` de repérer les commandes, skills et MCP jamais utilisés.

## Intégrations
- **Blinders**: utilisé tel quel s'il est installé (`blind select`), sinon repli lexical. Blinders fournit aussi `blind audit`, `blind graph` (Graphify) et `blind stats`; Iris ne les duplique pas.
- **Graphify**: la santé est lue depuis `graphify-out/` du repo si présent; Iris produit son propre graphe AST léger pour Python.
- **Jira-CLI** (ton outil, distinct de Iris): installé à part (`pip install -e 05-repos/Jira-CLI`), appelé en sous-processus pour les plans `--dry-run` depuis le dashboard.
- **Data Hub**: URL et endpoints dans `iris.toml` (`[datahub]`), token via variable d'environnement. Les chemins d'API par défaut sont des hypothèses à ajuster à ton portail.

## Dashboard
Serveur `http.server` lié à 127.0.0.1 (stdlib), page unique sans dépendance. `GET /api/state` (agrégat JSON), `POST /api/sync` (pull des repos). `dashboard build` produit une version statique lisible hors serveur (sans bouton de sync). Rafraîchissement toutes les 5 s.

## Voir et contrôler les CLI (Gemini CLI, Claude Code, Cursor, modèles locaux)
Une page web ne voit pas tes terminaux. Le pont est le serveur local d'Iris, par trois canaux:
1. **Observation passive** (`iris ingest`, relancé toutes les 30 s par le dashboard): lit `~/.claude/projects/*/*.jsonl` et `~/.gemini/tmp/*/chats/*.json`, déduplique par identifiant de message, rattache chaque usage au repo par le chemin du dossier de travail. Le format Gemini n'est pas vérifié sur toutes les versions.
2. **Outil appelé par l'agent** (`iris mcp`): serveur MCP stdio. L'agent demande `iris_context` au lieu de lire des repos entiers; chaque appel est journalisé.
3. **Modèles locaux** (`iris ask`): client Ollama; `prompt_eval_count` et `eval_count` donnent des tokens exacts.
Limite: Cursor n'écrit pas ses tokens en local (saisie avec `iris tokens add`), et la page ne voit pas le texte de la réponse en cours, seulement les sessions terminées dans les journaux.

## Pilotage depuis le navigateur
`POST /api/run {action, params}` n'exécute que la liste blanche de `lib/actions.py` (sync, graphes, fiches, audit, rétex, pack de contexte, plans `jira-cli release|deploy --dry-run`), en argv sans shell, avec validation des paramètres. Les POST exigent l'en-tête `X-Iris` et un Host local. Les actions qui modifient Jira ou GitLab restent dans `jira-cli`, avec leur confirmation.
Le panneau Suggestions vient de `lib/suggest.py` (fonction pure sur l'état): chaque suggestion actionnable a un bouton, et l'état se rafraîchit après chaque action pour enchaîner.

## Données locales
`.brain/` (git-ignoré): `tokens.jsonl`, `usage.jsonl`, `dashboard/`.

## Design du dashboard
Refonte guidée par trois sources: Emil Kowalski (mouvement: ease-out, 120 à 320 ms, press à 0,97, hover seulement sur pointeur fin, transform et opacity uniquement), Impeccable (anti-patterns: pas de cartes imbriquées, de pastille qui pulse, de dégradé ou de halo, hiérarchie typographique nette, cibles de 36 px) et Taste (un accent, un gris, un jeu de rayons, clair et sombre, états de chargement, vide et erreur, respect de `prefers-reduced-motion`). Pas de police web: le dashboard reste utilisable hors ligne.

# Graphe: Jira-CLI
_AST Python, 28 modules, 92 dépendances internes. Généré le 2026-10-14._

## src/jira_cli/__init__.py: CLI déterministe qui fait avancer un ticket Jira dans ses étapes de livraison.
## src/jira_cli/__main__.py
- dépend de: src/jira_cli/cli.py
## src/jira_cli/actions.py: Les commandes, partagées entre les sous-commandes et le dashboard.
- class Context: -
- def connect()
- def run(action, ticket, ctx, prompter, dry_run)
- def release(ticket, ctx, prompter, bump, final)
- def deploy(ticket, ctx, prompter, environments, dry_run)
- def ensure_deploy_repo(config, prompter)
- dépend de: src/jira_cli/__init__.py, src/jira_cli/cache.py, src/jira_cli/config.py, src/jira_cli/deploy.py, src/jira_cli/gitlab.py, src/jira_cli/http.py, src/jira_cli/jira.py, src/jira_cli/ports.py, src/jira_cli/release.py, src/jira_cli/stages.py, src/jira_cli/steps.py, src/jira_cli/tokens.py, src/jira_cli/versioning.py
## src/jira_cli/appconfig.py: Étape 9 : ce qui change dans la configuration de l'app, lu dans le diff de la MR.
- class ConfigChange: kind, is_topic
- class ConfigDiff: -
- def flatten(path, text)
- def compare(path, old_text, new_text)
## src/jira_cli/browser.py: Ouvrir un lien depuis le dashboard sans casser l'écran du terminal.
- def open_url(url)
## src/jira_cli/cache.py: Mémoire sur disque de ce que GitLab a vu pour les tickets dont l'histoire est close.
- class EventCache: get, put
- dépend de: src/jira_cli/models.py
## src/jira_cli/cli.py: Point d'entrée : `jira-cli` (dashboard), `init`, `release`, `deploy`, `trace`.
- def main(argv)
- dépend de: src/jira_cli/__init__.py, src/jira_cli/actions.py, src/jira_cli/dashboard.py, src/jira_cli/http.py, src/jira_cli/prompt.py, src/jira_cli/steps.py, src/jira_cli/trace.py, src/jira_cli/versioning.py, src/jira_cli/wizard.py
## src/jira_cli/config.py: Configuration utilisateur (config.yaml) : URLs, modes d'authentification, réglages par repo.
- class JiraConfig: -
- class GitLabConfig: -
- class DeployConfig: -
- class RepoConfig: -
- class Config: repo
- def home()
- def load(path)
- def save(config, path)
## src/jira_cli/dashboard.py: `jira-cli` sans argument : dashboard du terminal (Textual).
- class Dashboard: compose, on_mount, action_refresh, detail_text, rows, action_run_next, action_choose_action, action_open_mr
- class ActionMenu: compose, on_mount
- class KeyPrompt: compose
- def run(dry_run)
- dépend de: src/jira_cli/__init__.py, src/jira_cli/actions.py, src/jira_cli/browser.py, src/jira_cli/config.py, src/jira_cli/discovery.py, src/jira_cli/http.py, src/jira_cli/lineage.py, src/jira_cli/models.py, src/jira_cli/overview.py, src/jira_cli/prompt.py, src/jira_cli/stages.py, src/jira_cli/steps.py, src/jira_cli/wizard.py
## src/jira_cli/deploy.py: Étapes 8 à 10 : du ticket aux MR de déploiement dans le repo Kube, une par environnement.
- class ModuleTarget: new_env
- class EnvironmentChange: -
- class DeployPlan: -
- def plan_deploy(ticket_key, tracker, host, repo_config_for, prompter)
- def execute(plan, tracker, host, jira, prompter)
- def describe(plan)
- def describe_config(targets)
- dépend de: src/jira_cli/__init__.py, src/jira_cli/appconfig.py, src/jira_cli/config.py, src/jira_cli/manifests.py, src/jira_cli/models.py, src/jira_cli/modules.py, src/jira_cli/ports.py, src/jira_cli/stages.py, src/jira_cli/steps.py, src/jira_cli/versioning.py
## src/jira_cli/discovery.py: Ce qui se déduit des faits sans rien demander : colonnes utilisées, intention et rôle de
- def projects(issues)
- def guess_columns(jira, dev, deploy, environments)
- def flow(paths, columns)
- def missing(jira, environments)
- def code_hosts(links, jira_url)
- def remote_hosts(remotes)
- def gitlab_candidates(url)
- def namespaces(urls)
- def base_candidates(url)
- def learn_intents(histories, events)
- def intent_votes(histories, events)
- def stay_intents(history, events)
- def during(moment, stay)
- def board_fields(environments, team, deploy)
- def label(field)
- def role_of(jira, column, fields)
- def assign(jira, column, field, columns, environments)
- def foreign_links(tickets)
- def sprint_counts(sprints)
- def rank_sprint_boards(counts)
- def rank_boards(boards, counts)
- dépend de: src/jira_cli/config.py, src/jira_cli/models.py
## src/jira_cli/gitlab.py: Implémentation CodeHost pour GitLab (gitlab.com ou self-hosted, API v4 + GraphQL).
- class GitLabClient: whoami, find_merge_requests, merge_request_at, code_events, branches, changed_paths, read_file, list_dirs
- dépend de: src/jira_cli/cache.py, src/jira_cli/http.py, src/jira_cli/models.py, src/jira_cli/ports.py
## src/jira_cli/http.py: Sessions HTTP authentifiées, une par mode d'authentification.
- class ApiError: -
- def jira_session(config, token)
- def gitlab_session(config, token)
- def check(response)
- def timestamp(text)
- dépend de: src/jira_cli/config.py
## src/jira_cli/jira.py: Implémentation IssueTracker pour Jira (API REST v2, Cloud et Data Center).
- class JiraClient: get_issue, is_cloud, whoami, search, linked_issues, dev_links, boards, sprints
- dépend de: src/jira_cli/http.py, src/jira_cli/models.py
## src/jira_cli/lineage.py: Lignage des MR d'un ticket : celles que GitLab cite, recoupées avec le panneau Développement.
- class Linked: confirmed
- def of(key, links, tracker, host)
- def describe(linked)
- dépend de: src/jira_cli/http.py, src/jira_cli/models.py, src/jira_cli/ports.py
## src/jira_cli/manifests.py: Édition des fichiers du repo Kube (Helm values, kustomization, manifeste brut).
- def edit(text, image_path, image_value, env_path, env)
## src/jira_cli/models.py: Objets métier partagés, indépendants de Jira et de GitLab.
- class Issue: -
- class Board: -
- class Stay: -
- class History: path
- class CodeEvent: -
- class MergeRequest: -
- class PipelineVariable: -
- class ModuleRelease: -
- class ReleasePlan: -
## src/jira_cli/modules.py: Détection des modules d'un repo et des modules touchés par une MR.
- def detect_modules(read_root_file, list_dirs)
- def touched_modules(paths, modules)
## src/jira_cli/overview.py: Vue d'un ticket pour le dashboard : étape, ticket de mise en prod, MR et pipeline.
- class Component: -
- class TicketView: -
- def load(ctx, issue)
- def component_of(links, gitlab_url)
- def stage_of(ctx, issue)
- dépend de: src/jira_cli/__init__.py, src/jira_cli/actions.py, src/jira_cli/http.py, src/jira_cli/lineage.py, src/jira_cli/models.py, src/jira_cli/stages.py
## src/jira_cli/ports.py: Interfaces des systèmes externes.
- class IssueTracker: get_issue, transition, search, linked_issues, dev_links
- class CodeHost: find_merge_requests, merge_request_at, merge_status, branches, merge, changed_paths, read_file, list_dirs
- class Prompter: info, confirm, ask, choose
- dépend de: src/jira_cli/models.py
## src/jira_cli/prompt.py: Interaction terminal : menus aux flèches, couleurs, et confirmation avant toute action visible.
- class ConsolePrompter: info, title, explain, success, error, confirm, ask, secret
## src/jira_cli/release.py: Release candidate, puis release finale : du ticket Jira au lancement de la pipeline de tag.
- def plan_release(ticket_key, tracker, host, jira, repo_config_for)
- def execute(plan, tracker, host, jira, prompter)
- def describe(plan)
- dépend de: src/jira_cli/config.py, src/jira_cli/models.py, src/jira_cli/ports.py, src/jira_cli/stages.py, src/jira_cli/steps.py, src/jira_cli/versioning.py
## src/jira_cli/stages.py: Étape du ticket déduite de sa colonne Jira, et action suivante proposée.
- class Action: label, short
- class Stage: -
- def detect(status, jira, environments)
- def actions(stage, environments)
- def deploy_issue(tracker, jira, issue, prompter)
- dépend de: src/jira_cli/config.py, src/jira_cli/models.py
## src/jira_cli/steps.py: Briques communes aux commandes : ticket → MR liée → modules validés par le user.
- class Aborted: -
- def pick_merge_request(ticket_key, host, prompter, include_merged)
- def pick_modules(mr, repo, host, ref, prompter)
- dépend de: src/jira_cli/config.py, src/jira_cli/models.py, src/jira_cli/modules.py, src/jira_cli/ports.py
## src/jira_cli/tokens.py: Stockage local et chiffré des tokens.
- class TokenStore: get, set
## src/jira_cli/trace.py: `jira-cli trace KEY` : la vie d'un ticket et ce que GitLab y a vu, passage par passage.
- def run(key, ctx, prompter)
- dépend de: src/jira_cli/__init__.py, src/jira_cli/actions.py, src/jira_cli/discovery.py, src/jira_cli/lineage.py, src/jira_cli/models.py
## src/jira_cli/versioning.py: Calcul déterministe du prochain tag de release candidate.
- def tag_prefix(tag_format, module)
- def format_tag(tag_format, rc_format, module, version, rc)
- def next_rc(existing_tags, tag_format, rc_format, module, bump)
- def next_final(existing_tags, tag_format, rc_format, module, bump)
- def format_final_tag(tag_format, module, version)
- def latest_tag(existing_tags, tag_format, rc_format, module)
## src/jira_cli/wizard.py: `jira-cli init` : l'adresse de Jira et un token ; le reste est déduit puis montré pour validation.
- class _Discovery: run, learn, correct, summary
- def run_init(prompter, jira_client, gitlab_client, remotes, explain)
- dépend de: src/jira_cli/__init__.py, src/jira_cli/cache.py, src/jira_cli/config.py, src/jira_cli/discovery.py, src/jira_cli/gitlab.py, src/jira_cli/http.py, src/jira_cli/jira.py, src/jira_cli/models.py, src/jira_cli/tokens.py

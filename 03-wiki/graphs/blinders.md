# Graphe: blinders
_AST Python, 27 modules, 80 dépendances internes. Généré le 2026-10-14._

## src/blinders/__init__.py: blinders: start agent CLIs blind, open only the repos a prompt needs.
## src/blinders/__main__.py
- dépend de: src/blinders/cli.py
## src/blinders/adapters.py: How to start each agent CLI with a set of extra directories and MCP servers.
- class Adapter: -
- def get_adapter(name, cfg)
- def build_command(adapter, prompt, dirs, extra, mcp_names)
- dépend de: src/blinders/config.py
## src/blinders/audit.py: Estimate what an agent CLI would load at startup from a given directory.
- def est_tokens(chars)
- def audit(path, home, max_depth, max_dirs)
- def format_report(report)
- dépend de: src/blinders/scan.py
## src/blinders/cli.py: ``blind`` command line.
- class LaunchError: -
- class LaunchPlan: -
- class FleetBackend: sync, graphs, plan, hints, models, tools, map
- def cmd_init(args, cfg)
- def cmd_list(args, cfg)
- def cmd_select(args, cfg)
- def cmd_eval(args, cfg)
- def cmd_bench(args, cfg)
- def make_plan(cfg, adapter, prompt, repos, opts)
- def describe_plan(lp)
- def materialize(cfg, lp, dry_run)
- def prepare(cfg, lp, dry_run)
- def launch(cfg, lp, dry_run)
- def launch_plain(cfg, adapter, prompt, extra, dry_run)
- def cmd_run(args, cfg, extra)
- def setup(cfg, force)
- def ui_available()
- def ui_plan(cfg, repos, cli, prompt, deep)
- def ui_hints(cfg, repos, prompt, names)
- def run_launcher(args, cfg, repos, cli, extra)
- def text_fleet(cfg, repos, args)
- def cmd_start(args, cfg, extra, cli)
- def cmd_setup(args, cfg)
- def cmd_mcp(args, cfg)
- def cmd_graph(args, cfg)
- def cmd_sync(args, cfg)
- def cmd_status(args, cfg)
- def cmd_stats(args, cfg)
- def cmd_models(args, cfg)
- def cmd_doctor(args, cfg)
- def cmd_audit(args, cfg)
- def cmd_clean(args, cfg)
- def main(argv)
- dépend de: src/blinders/__init__.py, src/blinders/adapters.py, src/blinders/audit.py, src/blinders/config.py, src/blinders/evaluate.py, src/blinders/geminihome.py, src/blinders/gitsync.py, src/blinders/graph.py, src/blinders/hints.py, src/blinders/mcp.py, src/blinders/models.py, src/blinders/pipeline.py, src/blinders/scan.py, src/blinders/select.py, src/blinders/skills.py, src/blinders/stats.py, src/blinders/tools.py, src/blinders/ui.py, src/blinders/uimodel.py, src/blinders/workspace.py
## src/blinders/config.py: Configuration and paths.
- class Config: root_paths
- def config_dir()
- def cache_dir()
- def load_config(path)
## src/blinders/evaluate.py: Measure the selection on your own prompts: ``blind eval`` (quality) and ``blind bench`` (speed).
- class Case: -
- class CaseResult: passed, recall, precision
- def load_cases(path)
- def run_cases(cases, repos, cfg)
- def render(results, as_json)
- def bench(prompt, repos, cfg)
- dépend de: src/blinders/config.py, src/blinders/grep.py, src/blinders/scan.py, src/blinders/select.py
## src/blinders/files.py: One way to walk a repo, shared by everything that reads file names or small files.
- def declared_names(file)
- def iter_files(root, max_depth, limit)
## src/blinders/geminihome.py: A per-session Gemini home, so a launch loads only what it needs.
- class Extension: -
- class ExtPlan: -
- def strip_json_comments(text)
- def load_settings(path)
- def has_rtk_hook(settings)
- def list_extensions(home)
- def select_extensions(prompt, exts, skills_plan, mcp_plan, cfg)
- def build_home(session, real_home, cfg, skills, extensions)
- def memory_sources(real_home)
- dépend de: src/blinders/config.py, src/blinders/skills.py, src/blinders/text.py
## src/blinders/gitsync.py: Bring repos up to date before reading them: fetch, check out the root branch, fast-forward.
- class SyncResult: -
- def head_commit(path)
- def current_branch(path)
- def is_dirty(path)
- def remote_of(path)
- def root_branch(path, remote, cfg)
- def sync_repo(path, cfg, switch)
- def sync_many(paths, cfg, switch, log, should_stop)
- def graph_commit(report_path)
- def graph_state(report_path, repo_path)
- def hide_graph_output(repo_path)
- dépend de: src/blinders/config.py
## src/blinders/graph.py: Optional Graphify integration: build a code graph per repo, locally, with no LLM.
- class GraphResult: -
- def graph_command(cfg, repo, update)
- def cluster_command(cfg, repo)
- def graph_one(repo, cfg, update, dry_run)
- def build_graphs(repos, cfg, update, dry_run, log)
- dépend de: src/blinders/config.py, src/blinders/gitsync.py, src/blinders/scan.py
## src/blinders/grep.py: Find which repos contain an exact identifier from the prompt, with no model and no tokens.
- class SearchTimeout: -
- def literals(prompt, limit)
- def stem_pattern(word)
- def locate(wanted, repos, use_rg, cache, stems)
- def search(wanted, repos, use_rg, cache, broad_limit)
- def find_hits(prompt, repos, cfg, cache, deadline)
- dépend de: src/blinders/config.py, src/blinders/files.py, src/blinders/relations.py, src/blinders/text.py
## src/blinders/hints.py: Second level: starting points *inside* an opened repo. No model is called.
- class FileHint: -
- class Hints: -
- def find_hints(prompt, repo, cfg)
- def render_hints(h, repo_path)
- dépend de: src/blinders/config.py, src/blinders/files.py, src/blinders/scan.py, src/blinders/text.py
## src/blinders/mcp.py: Pick which MCP servers a session needs, from the user's own MCP config.
- class McpServer: -
- class McpPlan: -
- def discover(style, home, cfg)
- def select_mcp(prompt, servers, cfg, spec)
- def missing_names(spec, servers)
- def claude_config(plan)
- dépend de: src/blinders/config.py, src/blinders/text.py
## src/blinders/models.py: Which model to start a CLI with, and which models that CLI really offers.
- def resolve_model(cli, spec, cfg)
- def cli_models(cli, home)
- def installed_gemini_ids()
- def settings_model(home)
- def recent_gemini_models(home, files)
- def gemini_model_list(home)
- dépend de: src/blinders/config.py, src/blinders/geminihome.py
## src/blinders/pipeline.py: The four steps behind a bare ``blind``, independent of how they are displayed.
- class Event: -
- def minutes_since_sync()
- def run_sync(cfg, repos, emit, force, should_stop)
- def run_graphs(cfg, repos, emit, should_stop)
- def run_map(cfg, repos, prompt, emit)
- def reload(cfg)
- dépend de: src/blinders/config.py, src/blinders/gitsync.py, src/blinders/graph.py, src/blinders/hints.py, src/blinders/scan.py
## src/blinders/relations.py: Relations between repos, computed offline at index time. No LLM, no source parsing.
- def normalize(name)
- def collect_ref_text(path)
- def identities(path)
- def compute_links(repos, texts)
- dépend de: src/blinders/files.py, src/blinders/text.py
## src/blinders/scan.py: Find git repos under the configured roots and build a small, cheap-to-read index.
- class Repo: -
- def labels(repos)
- def path_terms(path)
- def script_head(path)
- def describe_repo(path, map_globs)
- def find_repos(roots, depth)
- def index_path()
- def build_index(cfg)
- def save_index(repos)
- def load_index(cfg, refresh)
- dépend de: src/blinders/config.py, src/blinders/files.py, src/blinders/relations.py, src/blinders/text.py
## src/blinders/select.py: Pick which repos a prompt needs. Pure function of (prompt, index): fast and deterministic.
- class Choice: solid
- class Related: -
- class Plan: -
- def rank(prompt, repos, ignore)
- def select(prompt, repos, cfg, ranked)
- def with_hits(seeds, hits, repos, cfg)
- def neighbors(seeds, repos, cfg)
- def plan(prompt, repos, cfg, related, forced)
- dépend de: src/blinders/config.py, src/blinders/grep.py, src/blinders/scan.py, src/blinders/text.py, src/blinders/verify.py
## src/blinders/skills.py: Pick which user-level skills a session keeps visible.
- class Skill: -
- class SkillPlan: -
- def discover(family, home, cfg)
- def repo_vocabulary(repos)
- def select_skills(prompt, skills, cfg, spec, repos)
- def missing_names(spec, skills)
- def claude_settings(plan)
- def gemini_settings(plan)
- dépend de: src/blinders/audit.py, src/blinders/config.py, src/blinders/text.py
## src/blinders/stats.py: Anonymous launch statistics, to compare sessions started with and without ``blind``.
- def log_path()
- def read_log()
- def estimate_startup(cwd, family, hidden, cfg, home)
- def record_launch()
- def add_note(rec_id, values)
- def session_usage(rec, home)
- def build_report(last, home)
- def format_report(rows)
- dépend de: src/blinders/__init__.py, src/blinders/audit.py, src/blinders/config.py, src/blinders/skills.py
## src/blinders/text.py: Tokenisation shared by the scanner and the selector.
- def fold(text)
- def tokens(text)
- def words(text)
- def squash(text)
- def stem(token)
- def stems(text)
- def ubiquitous(term_sets, min_items, share)
## src/blinders/tools.py: Are the optional helpers there, and will they be used in this launch? No Textual import.
- class ToolStatus: -
- def tool_statuses(cfg, gemini, which)
- dépend de: src/blinders/config.py
## src/blinders/ui.py: Full-screen launcher (optional, needs ``pip install "blinders[ui]"``).
- class PromptArea: -
- class StepState: -
- class BlindApp: compose, on_mount, on_text_area_changed, on_select_changed, on_selection_list_selection_highlighted, on_selection_list_selection_toggled, action_launch, on_prompt_area_submit
- def run_ui(clis, cli, prompt, backend, status)
- dépend de: src/blinders/pipeline.py, src/blinders/uimodel.py
## src/blinders/uimodel.py: Data the full-screen launcher and the CLI exchange. No Textual import: usable without the ``[ui]`` e
- class Item: -
- class UiPlan: -
- class UiResult: -
- class Backend: sync, graphs, plan, hints, models, tools, map
- dépend de: src/blinders/pipeline.py, src/blinders/tools.py
## src/blinders/verify.py: Second pass over the chosen repos: do their files really talk about the prompt?
- def verify(prompt, choices, cfg, cache, everyone)
- dépend de: src/blinders/config.py, src/blinders/grep.py, src/blinders/select.py, src/blinders/text.py
## src/blinders/workspace.py: The blind workspace: a throwaway directory holding only a small markdown index.
- def sessions_dir()
- def render_index(opened, closed, cfg, linked, related)
- def create_session(opened, closed, cfg, link, related)
- def prune_sessions(cfg, everything)
- dépend de: src/blinders/config.py, src/blinders/scan.py

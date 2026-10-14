---
name: session-retex
description: "Once some work has been done, we need to learn from what we did in order to ease the process next time we work. Kaizen."
---

A lot of work has been accomplished.
Start with `./iris retex`: it lists the deterministic findings (failed commands, assets to archive, repos without wiki card, stale graphs, inbox backlog, budget) and archives the report in `07-archive/`.

List all the issues you encountered while working on the task. It can be a tool missing a feature, an unclear process, context you had to discover, everything that made the work not straightforward.

1. **Missing Tool Features, Deterministic Refactoring & Broken ACIs:**
   - For each missing tool feature or repetitive manual process, create/update a deterministic Python command inside `Iris CLI` (`06-tools/iris_cli/`).
   - If a feature cannot be immediately implemented, run `./iris fr new "<title>"` to open a feature request in `06-tools/feature_request/` following `06-tools/feature_request/GUIDELINES.md` (it registers it in `06-tools/feature_request/README.md`).

2. **Asset Lifecycle & Decommissioning (Skills, MCP & Tools):**
   - Identify unused or outdated skills, MCP configurations, or scripts (`./iris usage audit`).
   - Propose their removal or archive them in `07-archive/` (`./iris archive <path>`) to keep the context footprint minimal.

3. **Declarative Context Discovery:**
   For each factual context you had to discover (strategic decisions, team scope, product architectures), update `03-wiki/` to ensure it is up to date and directly accessible next time.

4. **Process Optimization & Creation:**
   If it's a process or workflow issue:
   - Find the existing process under `.gemini/skills/executing-2nd-brain-processes/references/` and optimize it in place.
   - OR create a new operational process under `.gemini/skills/executing-2nd-brain-processes/references/<kebab-case-name>.md` and register it in `.gemini/skills/executing-2nd-brain-processes/SKILL.md` following the `registering-new-processes` runbook.

5. **Security Policy Whitelisting:**
   If you got interrupted because you needed validation for command execution, IF those commands are READ ONLY (meaning they do not send messages, comments, or emails publicly, do not mutate state, and are not destructive), update the whitelist in `.gemini/policies/local-rules.toml`.
   *Never whitelist glab. The correct tool to use is gitlab_cli.*

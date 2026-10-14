# Start a work session

1. `./phoenix repos sync` (or `./phoenix dashboard serve --sync`).
2. `./phoenix context "<the user story>"`: read only the returned pack (cards + graphs).
3. Open a repo's code only for the files the graph points to.
4. Log remote usage: `./phoenix tokens add --model <m> --tin N --tout N --session <id>`.
5. End with the `session-retex` skill.

# Start a work session

1. `./iris repos sync` (or `./iris dashboard serve --sync`).
2. `./iris context "<the user story>"`: read only the returned pack (cards + graphs).
3. Open a repo's code only for the files the graph points to.
4. Log remote usage: `./iris tokens add --model <m> --tin N --tout N --session <id>`.
5. End with the `session-retex` skill.

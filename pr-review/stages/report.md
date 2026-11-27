# Deterministic report build

The agent outputs JSON. The checked-in template and assets define presentation.
Use the scripts below from the skill directory; never rewrite or copy the HTML
by hand during a review.

1. Collect the exact review snapshot:
   `python3 scripts/collect-context.py --repo <root> --mode <pull_request|commit_range|local> --base <base> --head <head> [--pr <number>] --output <context.json>`
   Add repeatable `--include <path>` for supporting locations outside changed
   files. Local mode captures the working tree (including staged and untracked
   content) against the selected baseline; choose upstream as baseline when
   unpushed commits belong in scope. PR mode resolves its SHAs through `gh`.
2. The review agent returns analysis.json matching `schemas/analysis.schema.json`.
3. Assign finding IDs for the comment-agent handoff:
   `python3 scripts/build-report.py prepare --analysis <analysis.json> --output <accepted.json>`
4. The comment agent follows `stages/comments.md`, returning comments.json.
5. Build the fixed report:
   `python3 scripts/build-report.py build --context <context.json> --analysis <accepted.json> --comments <comments.json> --output <review.html>`
6. Validate: `scripts/validate-report.sh <review.html>`.

Correct only the input fields identified by validation errors, then retry.
The builder owns metadata, counts, excerpts, associations, safe JSON embedding,
and asset assembly. The schema is version 2.0. It contains an intent comparison
instead of a change-flow diagram. HTML is self-contained and readable offline.

Write artifacts under `/tmp/pr-review/<repo>-<pr-or-range>-<timestamp>/`
or the configured output directory. In PR mode start
`scripts/open-report.sh <absolute-report-path>` in a persistent host session
and return the URL. Keep it running while the reviewer uses the report.
If persistent processes or browser opening are unavailable, describe the
limitation and supply the command. For local/range reviews return the file.

One shared Finish review panel stages and submits comments. GitHub mutations
remain gated by explicit confirmation and the helper's current-head checks;
see `actions.md`. Offline reports retain their embedded snapshot, with actions
unavailable. The browser never calls GitHub directly.

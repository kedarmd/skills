> Internal stage of the `pr-review` skill. Reached only through `../SKILL.md` — never invoked directly as a skill.


# PR Review Report

Generate exactly one self-contained HTML document from validated findings.
Start from `../templates/report.html`; editable sources are
`../assets/report.css` and `../assets/report.js`. Validate with
`../scripts/validate-report.sh`, open with `../scripts/open-report.sh`.

## Design principles

A fast technical developer tool, not a marketing dashboard. Prioritize
readability, source navigation, keyboard accessibility, low visual noise,
fast rendering, technical clarity. Avoid cards-everywhere, hero sections,
charts, gradients, marketing language, decorative animation.

## Structure

```text
Header (PR/range, author, base→head, changed files, finding counts)
Change flow (interactive, source-linked; omit if change is too small)
Findings (grouped CRITICAL → HIGH → MEDIUM → LOW)
Review actions (comment / request changes / approve)
Metadata (SHAs, generated-at, schema version, agent)
```

## Data contract

Embed the review JSON in the HTML — no external fetch:

```html
<script type="application/json" id="review-data">{ ... }</script>
```

Must conform to `../schemas/review.schema.json`. IDs stable (`F-001`, `S-001`).

## Change flow

Nodes + edges derived from actual evidence (entry points, services, DB,
response). Each node: label, source locations, related finding IDs.
Clicking navigates to the finding/code section. Never invent architecture.

## Finding interaction

Collapsed: severity badge, title, one-sentence summary, `file:start–end`,
status badge (follow-ups). Expanded: explanation (`reason`), code excerpt
with highlighted lines + surrounding context, impact, evidence, suggestions
(title + explanation + code/diff), actions (add comment / choose suggested
comment / edit / discard).

Suggested-fix selection populates the comment composer; reviewer can edit
before submitting. Discard only hides locally unless the agent is asked to
act.

## Actions (presentation only)

The HTML MUST NOT call GitHub or the shell. It builds an action payload
the agent executes via `gh` (see `actions.md`):

```json
{ "action": "comment | request_changes | approve | submit_comments",
  "repo": "owner/repo", "pr": 123, "commit_sha": "...",
  "comments": [{ "finding": "F-001", "file": "...", "line": 42, "side": "RIGHT", "body": "..." }],
  "body": "..." }
```

Render the payload visibly (e.g. in a `<details>` + copy button) so any
agent/runtime can pick it up. Require explicit confirmation UI for approve
/ request-changes.

## Self-contained requirement

No CDN JS/CSS, remote fonts, external images, or network calls. All inline.
Must work from `file://` offline.

## Code rendering

Show filename, line numbers, highlighted finding lines, surrounding
context, monospace font, horizontal scroll, no broken escaping
(re-validate `<`, `&` handling). Keep excerpts small — include the
function/hunk needed, not whole files.

## Output

Write to `/tmp/pr-review/<repo>-<pr-or-range>-<timestamp>/review.html`
(or repo-configured path). Return absolute path, finding counts, and
whether GitHub was modified (always `no` at generation time).

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
Header (PR/range, author, base→head, finding counts; sticky)
Tabs: Overview | Findings (n)
  Overview
    ├── What changed (from review JSON overview.summary)
    ├── Stats (files, +/-, commits) + key files
    └── Change flow as SVG sequence diagram (actors = flow nodes,
        messages = transitions; finding tags clickable → finding)
  Findings
    ├── Queue grouped CRITICAL → HIGH → MEDIUM → LOW
    ├── Detail pane (code, why/impact/evidence, suggestions,
    │   comment composer in PR mode, discard always)
    └── Review actions, PR mode only (payload + submit/approve/request)
Footer (SHAs, generated-at, schema version, mode note)
```

Omit the diagram when the flow is too small to justify one; omit the
overview sections whose data is absent. Diagram nodes must come from
actual evidence — never invent architecture.

## Data contract

Embed the review JSON in the HTML — no external fetch:

```html
<script type="application/json" id="review-data">{ ... }</script>
```

Must conform to `../schemas/review.schema.json`. IDs stable (`F-001`, `S-001`).

## Change flow

Rendered as an inline SVG sequence diagram derived from the `flow` array:
actors are flow nodes, messages are the transitions between consecutive
nodes, and messages into nodes carrying `finding_ids` are highlighted and
clickable (jump to the queue with that finding selected). No runtime
libraries — plain generated SVG, so the report stays offline and fast.
Never invent architecture.

## Finding interaction

Queue rows show severity badge, title, `file:start`, and status badge
(follow-ups). Selecting a row paints the detail pane: explanation
(`reason`), code excerpt, impact, evidence, suggestions, and — in PR
mode — the comment composer with Add comment; Discard is always present.

Suggested-fix selection populates the comment composer; reviewer can edit
before submitting. Discard only hides locally unless the agent is asked to
act.

## Actions (pull_request mode only)

Only when `review.mode` is `pull_request`. For `commit_range` and `local`
reviews there is no PR to post to, so omit the Review Actions section
entirely, along with the per-finding comment composer and Add-comment
button (keep Discard for local triage). The footer notes that PR actions
are unavailable.

When in PR mode, the HTML MUST NOT call GitHub or the shell. It builds an
action payload the agent executes via `gh` (see `actions.md`):

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

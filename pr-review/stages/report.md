> Internal stage of the `pr-review` skill. Reached only through `../SKILL.md` — never invoked directly as a skill.


# PR Review Report

Generate exactly one self-contained HTML document from validated findings.
Start from `../templates/report.html`; `../assets/report.css` and
`../assets/report.js` mirror its inline styles and renderer. Validate with
`../scripts/validate-report.sh`, open with `../scripts/open-report.sh`.

## Design principles

A fast technical developer tool, not a marketing dashboard. Prioritize
readability, source navigation, keyboard accessibility, low visual noise,
fast rendering, technical clarity. Avoid cards-everywhere, hero sections,
charts, gradients, marketing language, decorative animation.

## Structure

```text
Header (PR/range, author, base→head, finding counts; sticky; theme toggle)
Tabs: Overview | Changes (n files · n findings), open on Overview
  Overview
    ├── Review summary (required, first)
    ├── Clickable SVG sequence diagram with source excerpts and finding links
    └── Stats (files, +/-, commits) + key files
  Changes
    ├── Changed file rail and unified diff with old/new line numbers
    ├── Findings panel beside the diff, filtered by severity and linked to
        separate finding detail views
    └── Inline comment composer on changed lines; shared comment staging
        with finding detail
  Review actions (PR mode only, after findings and changes)
    └── Comment → Request changes → Approve
Footer (SHAs, generated-at, schema version, mode note)
```

Omit the flow when it is too small to justify one; omit overview sections
whose data is absent. Flow nodes must come from actual evidence — never
invent architecture.

## Data contract

Embed the review JSON in the HTML — no external fetch:

```html
<script type="application/json" id="review-data">{ ... }</script>
```

Must conform to `../schemas/review.schema.json`, including `changes[]` for
every changed file. Include a concise,
plain-language `overview.summary` that opens the report; this field is
required. IDs stable (`F-001`, `S-001`).

## Change flow

Render the supplied `flow` nodes as a horizontal SVG sequence diagram in
their supplied order, with arrows between steps. Each block is keyboard and
pointer accessible; selecting it opens its source excerpt and linked
findings. If the selected step has linked findings, open the first linked
finding’s dedicated detail view; otherwise show that step’s source excerpt.
Label a transition only when review data supplies evidence for it
(`transition`). Populate `flow[].locations[].code_excerpt` (or
`flow[].code_excerpt`) with a short source window. Never invent architecture
or transitions beyond the supplied data.

## Finding interaction

Queue rows show severity badge, title, `file:start`, and status badge
(follow-ups). Selecting a row opens a dedicated finding detail view with
back, previous, and next navigation: explanation
(`reason`), syntax-highlighted, line-numbered source with the finding range
highlighted, impact, evidence, suggestions, and — in PR
mode — the comment composer with Add comment; Discard is always present.

Show each location and let the reviewer select the inline comment target.
Suggested-fix selection populates the comment composer; render `code` as a
highlighted code block and let the reviewer edit the comment before
submitting. Discard only hides locally unless the agent is asked to act.

## Actions (pull_request mode only)

Only when `review.mode` is `pull_request`. For `commit_range` and `local`
reviews there is no PR to post to, so omit the Review Actions section
entirely, along with the per-finding comment composer and Add-comment
button (keep Discard for local triage). The footer notes that PR actions
are unavailable.

When in PR mode, the report stages comments locally and presents a review
confirmation dialog. When opened with `scripts/open-report.sh`, it posts the
payload to the loopback-only helper in `scripts/actions-server.py`; that
helper checks the current PR head SHA and runs one `gh api` review request.
The HTML never calls GitHub. Opening the HTML directly with `file://` keeps
all review actions unavailable. The reviewer must confirm each submission;
approve and request-changes also require a summary body.

```json
{ "action": "COMMENT | REQUEST_CHANGES | APPROVE",
  "repo": "owner/repo", "pr": 123, "commit_sha": "...",
  "comments": [{ "finding": "F-001", "file": "...", "line": 42, "side": "RIGHT", "body": "..." }],
  "body": "..." }
```

Show the exact payload in a confirmation dialog before submitting. On stale
head SHA or a GitHub error, show the error and preserve staged comments.

## Changes tab and comment integration

Include every changed file in `changes[]`, with its status, additions,
deletions, and per-file unified `patch` from the exact reviewed range. Render
the patches with old/new line numbers. In PR mode, any added, removed, or
context line in a diff hunk can stage an inline comment. Use `RIGHT` for
added/context lines and `LEFT` for removed lines. Finding-detail comments
and Changes-tab comments share the same `(file, line, side)` anchor, so a
comment is visible and editable in both views and is submitted once.
Associate files with findings by matching their paths; show the related
findings beside the selected diff and expose them as links to the dedicated
detail view. The Changes view is the primary finding workspace; do not add a
separate Findings tab. For binary files or files without a text patch, state
clearly that no inline line anchor is available.

## Self-contained requirement

No CDN JS/CSS, remote fonts, or external images. CSS/JS stay inline. The
report renders from `file://` offline and supports the system theme plus a
manual light/dark toggle; GitHub actions are available only when served by
the local helper started through `open-report.sh`.

## Code rendering

Show filename, line numbers, highlighted finding lines, surrounding
context, syntax colors, monospace font, horizontal scroll, and correct
escaping. `code_excerpt_start_line` indicates the first excerpt line;
default it to the finding `start_line`. Keep excerpts small — include the
function/hunk needed, not whole files.

## Output

Write to `/tmp/pr-review/<repo>-<pr-or-range>-<timestamp>/review.html`
(or repo-configured path). Return absolute path, finding counts, and
whether GitHub was modified (always `no` at generation time).

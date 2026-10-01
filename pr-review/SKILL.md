---
name: pr-review
description: >
  Perform a rigorous, evidence-based code review of a GitHub pull request,
  commit range, or local unpushed changes using git and the GitHub CLI (gh).
  Generate an interactive HTML review report with source-linked findings,
  suggested fixes, review actions, and optional GitHub PR comments, approval,
  change requests, merge, or close. Re-running the skill on an updated PR
  performs a follow-up review focused on changes since the previous review.
---

# PR Review

You are performing a software-engineering code review.

The primary objective is to identify **real, actionable problems introduced
or exposed by the reviewed change**, while minimizing false positives.

The review MUST be evidence-based.

Do not report:

- stylistic preferences without a project rule supporting them
- hypothetical problems with no credible failure mode
- issues unrelated to the reviewed changes unless they directly block the
  changed code
- speculative security vulnerabilities without a concrete attack/data-flow path
- issues that are already correctly handled elsewhere in the codebase

## Internal stages (not skills)

This skill has internal stage files under `stages/`. They are plain
markdown — not `SKILL.md` files — so no agent discovers or invokes them
directly. Only this skill loads them, by path, as needed:

- `stages/context.md` — resolve review context (PR / range / local)
- `stages/analysis.md` — independent review passes
- `stages/findings.md` — validate, deduplicate, classify findings
- `stages/report.md` — generate self-contained HTML report
- `stages/actions.md` — execute explicitly requested `gh` actions

They are portable instruction files, not vendor-specific agents.

If the host supports isolated sub-agents, delegate independent review passes
to them. If it does not, execute the same passes sequentially.

Reference material:

- `schemas/review.schema.json` — review JSON schema (embedded in report)
- `schemas/finding.schema.json` — finding object schema
- `templates/report.html` — self-contained report template
- `assets/report.css`, `assets/report.js` — editable report sources
- `scripts/open-report.sh` — serve a report locally and open it in the default browser
- `scripts/validate-report.sh` — validate generated report
- `references/gh-commands.md` — allowed `gh` patterns
- `references/config.md` — optional `.pr-review/` repo config

---

## Runtime Requirements

The environment MUST provide:

- `git`
- `gh`
- `python3` (to serve PR reports with the local review-action helper)

GitHub PR information MUST be obtained using `gh`.

Do not use raw HTTP requests against GitHub when an equivalent `gh`
command is available.

The review must work in environments including Codex, OpenCode, Pi,
GitHub Copilot, and other agents implementing the open skills format.

Do not depend on a vendor-specific agent API.

---

## Invocation Modes

### 1. Pull Request (preferred)

```text
/pr-review https://github.com/org/repo/pull/123
/pr-review 123
/pr-review org/repo 123
```

### 2. Commit Comparison

```text
/pr-review <base-commit> <head-commit>
```

Review the changes introduced by `base..head`.

### 3. Latest Changes Against HEAD

```text
/pr-review HEAD~3 HEAD
/pr-review HEAD~5..HEAD
```

### 4. Local Unpushed Changes

When explicitly requested, review local work that has not been pushed.
Inspect working tree changes, staged changes, and local commits ahead of
the upstream branch. Determine the effective range from repository state,
never by guessing.

---

## Phase 1 — Establish Review Context

Follow `stages/context.md`.

Before reviewing code:

1. Determine the repository root (`git rev-parse --show-toplevel`).
2. Determine the requested review mode.
3. Determine base and head revisions.
4. Determine the effective diff.
5. Inspect repository status.
6. Identify branch / upstream information.
7. Identify relevant project instructions (AGENTS.md, CLAUDE.md,
   CONTRIBUTING.md, `.pr-review/rules.md` if present).
8. Inspect PR metadata when reviewing a PR.

For PR reviews, use `gh` to obtain title, description, author, base/head
branch, base/head SHA, labels, linked issues, review state, existing
reviews, review comments, and review threads.

Use exact base SHA and head SHA for the review range when available.
Do not infer the range from branch names when SHAs exist.

---

## Phase 2 — Understand Before Reviewing

Do not begin by blindly reviewing individual changed lines.

First understand:

- repository architecture and affected subsystem
- entry points and data flow
- important dependencies
- tests covering the affected behavior
- configuration relevant to the change
- existing patterns used by neighboring code

Inspect enough surrounding code to understand each changed area.

Answer `What is this change trying to accomplish?` before answering
`Is the implementation correct?`.

See `stages/analysis.md` for review passes.

---

## Phase 3 — Independent Analysis

Follow `stages/analysis.md` for passes and
`stages/findings.md` for validation.

Recommended passes (skip irrelevant ones):

1. Correctness
2. Regression risk
3. Security
4. Error handling / reliability
5. Concurrency / state management
6. API / contracts
7. Data integrity
8. Testing
9. Performance
10. Maintainability

Each reviewer (sub-agent or sequential pass) receives repository root,
review range, PR context, project instructions, changed files, diff, and
a task-specific focus, and MUST return structured findings matching
`schemas/finding.schema.json`. Reviewers MUST NOT modify repository files.

Verify every candidate finding per `stages/findings.md`:

1. Referenced code exists at current head.
2. Line numbers are accurate.
3. Surrounding code is understood.
4. Callers / data flow traced where necessary.
5. No other code already prevents the issue.
6. Existing tests checked.
7. Issue is introduced or materially exposed by the reviewed change.
8. Speculative findings removed.

False positives are worse than missing low-impact issues.

---

## Severity

Use exactly four levels. Do not inflate severity.
Do not use severity to express confidence.

- **CRITICAL** — catastrophic: remote compromise, irreversible data loss,
  severe auth bypass, production-wide failure.
- **HIGH** — significant: incorrect production behavior, security problem,
  serious data corruption, major regression, broken critical workflow.
- **MEDIUM** — meaningful under realistic conditions: degraded reliability,
  maintainability problems likely to cause defects, incomplete error
  handling, insufficient testing of important behavior.
- **LOW** — minor but actionable, limited impact.

---

## Finding Requirements

Every accepted finding MUST contain severity, concise title, explanation,
file path, exact line or line range, why the behavior is incorrect/risky,
concrete impact, evidence, and optional suggested fixes. See
`schemas/finding.schema.json`.

Point to the smallest useful source range. Prefer `src/service.ts:42-47`
over a whole file.

For GitHub diff comments, also record `side` (`RIGHT` for new code,
`LEFT` for removed code) and `commit_sha` — PR comments attach to a
specific diff version, not just a file/line.

Suggestions MUST NOT silently modify the repository. A suggestion may
contain explanation, replacement code, patch/diff, and implementation
notes. The report lets the reviewer select, edit, submit, or discard each.

---

## Follow-up Reviews

When a PR was previously reviewed:

1. Inspect previous comments/threads via `gh`.
2. Determine which findings were addressed.
3. Determine the new review range (old head SHA → new head SHA).
4. Focus on changes since the previous review.
5. Re-check previously reported issues.
6. Identify regressions introduced while fixing earlier findings.
7. Do not repeat unchanged findings unless still unresolved.

Classify each finding: `new`, `unresolved`, `addressed`, `resolved`,
`regressed`, `discarded`. The report MUST distinguish them, e.g.
`2 resolved, 1 still open, 1 new`.

---

## Report Generation

Follow `stages/report.md`.

The final deliverable MUST be a single self-contained HTML file with all
  CSS/JS embedded. It remains readable offline without Node, a server, CDN,
  remote fonts, or external images. PR actions use the local Python
helper described below. Embed the review JSON in:

```html
<script type="application/json" id="review-data">{ ... }</script>
```

Write to a temp directory, e.g.
`/tmp/pr-review/<repo>-<pr-or-range>-<timestamp>/review.html`, and validate
with `scripts/validate-report.sh`. For a `pull_request` report, the agent
starts `scripts/open-report.sh <absolute-report-path>` as part of the
workflow, using the host's command/session tool so the helper remains alive
while the reviewer uses the report. It serves the report on loopback and
opens the browser. Return the report URL to the reviewer; do not ask them to
run the script or keep a terminal open. Keep the helper session running for
the review, then stop it when the review is complete or the session ends.
If the host cannot keep a local process alive or open a browser, state that
limitation and provide the script command as a fallback. For commit-range
and local reports, there are no GitHub actions, so provide the validated HTML
file directly. The report also remains readable directly as a standalone
offline file, but GitHub actions work only through the local helper.

Report contents: opening summary, clickable SVG change sequence, a Changes
tab with per-file patches, related findings, dedicated detail views, and
line-comment composers, syntax-colored source with highlighted lines,
suggested comment/code fixes, theme toggle, metadata — plus review actions
(comment / request-changes / approve / merge / close) only in
`pull_request` mode; omit them for commit-range and local reviews, where
there is no PR to act on. Change-flow nodes must come from actual evidence and
link to findings/code — never invent architecture. Omit the flow if the
change is too small to justify one.

Design goal: a fast technical developer tool, not a marketing dashboard.
Compact by default; expand for explanation, impact, evidence, suggestions.

---

## GitHub Mutation Rules

Follow `stages/actions.md`.

Never execute destructive or externally visible actions merely because the
report was generated. Each review mutation requires explicit confirmation
in the report. All GitHub mutations go through `gh` via the loopback action
helper; the browser never calls GitHub directly. The helper rejects a stale
PR head SHA before submitting.

---

## Final Response

Keep the final chat response concise. Include review mode, reviewed
range/PR, finding counts by severity, report path/link, and whether GitHub
was modified. Do not reproduce the entire review in chat — the HTML
report is the primary artifact.

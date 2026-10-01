> Internal stage of the `pr-review` skill. Reached only through `../SKILL.md` — never invoked directly as a skill.


# PR Review Actions

Privileged execution layer. The report never contacts GitHub directly. Its
loopback-only helper executes the review explicitly confirmed in the report,
using `gh`. See `../references/gh-commands.md`.

NEVER execute an action merely because it appears in the report. The report
requires an explicit final confirmation for each action. Approve and
request-changes also require a summary. Staged comments are sent only when
the reviewer confirms a review submission.

## Preconditions (every action)

Confirm: repository (`owner/repo`), PR number, commit SHA (head SHA the
finding was validated against), file, line + side, exact comment body.
The helper checks that the live PR head SHA still matches the report before
submitting. Reviewers remain responsible for checking that inline lines are
in the PR diff; GitHub rejects invalid anchors and the error is shown.
If the PR head moved since the review, re-validate line numbers before
posting — diff-anchored comments on stale SHAs may land on the wrong lines.

## 1. Inline finding comment

Prefer a diff-anchored review comment when the location is in the PR diff:

```sh
gh api repos/OWNER/REPO/pulls/PR/comments \
  -f body="$BODY" -f commit_id="$HEAD_SHA" \
  -f path="$FILE" -f line="$LINE" -f side="RIGHT"
```

(`side`: `RIGHT` = new/head side, `LEFT` = base side. `line` is the diff
position line, not always the file line — verify with `gh pr diff`.)

If the location is outside the diff, fall back to a top-level PR comment
or review-body note referencing `file:lines`, and say so explicitly.

## 2. Submit review (comments + approve / request changes)

The report submits a single review using `gh api` with `event` set to
`COMMENT`, `APPROVE`, or `REQUEST_CHANGES`, preserving all inline comments
in that review. Comments may be staged from finding details or from any
commentable line in the Changes tab; both views share the same file/line/side
anchor. It does not use a sequence of independent comment writes.

```sh
# post pending review with comments (preferred: single review event)
gh pr review PR --comment -b "$BODY"
gh pr review PR --request-changes -b "$BODY"
gh pr review PR --approve -b "$BODY"
```

Before `--request-changes` / `--approve`, show the reviewer: PR, repo,
number of comments + full bodies, and the summary text. Require explicit
confirmation ("yes, request changes"). Never batch-approve silently.

## 3. Plain comment (no review event)

```sh
gh pr comment PR --body "$BODY"
gh issue comment PR --body "$BODY"  # equivalent for PRs
```

## Errors

If GitHub rejects the action: preserve the intended payload, report the
exact error output, do not silently retry destructive operations. On stale
SHA / invalid line errors, re-resolve the location and ask before resending.

## Final accounting

Report back: which actions were executed, their `gh` commands (redacted if
needed), resulting URLs/IDs, and which payloads were discarded at the
reviewer's request.

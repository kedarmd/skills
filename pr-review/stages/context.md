> Internal stage of the `pr-review` skill. Reached only through `../SKILL.md` — never invoked directly as a skill.


# PR Review Context

Determine exactly what is being reviewed. This stage file is internal to
`pr-review` — it establishes context, it does not review code.

## 1. Repository root

```sh
git rev-parse --show-toplevel
git status --short --branch
git branch -vv
```

Record the root. All file paths in findings MUST be relative to it.

## 2. PR mode

When given a PR URL, number, or `repo number`, `gh` is the source of truth.
See `../references/gh-commands.md`.

```sh
gh pr view <PR> --json number,title,body,author,baseRefName,headRefName,baseRefOid,headRefOid,state,createdAt,updatedAt,closedAt,mergedAt,reviewDecision,mergeStateStatus,labels,reviews,comments,files,additions,deletions,url
gh pr diff <PR>
```

Collect: repository, PR number, URL, title, description, author, base ref,
head ref, base SHA, head SHA, PR lifecycle, lifecycle dates, aggregate
review decision, existing reviews,
review comments, review threads, linked issues (parse body + `gh issue`
if needed).

Use the exact base SHA and head SHA for the review range. Do not infer the
range from branch names when SHAs are available.

For lifecycle and aggregate decision, fetch `state,createdAt,updatedAt,closedAt,mergedAt,reviewDecision` with `gh pr view`. Normalize lifecycle to
`open`, `closed`, or `merged` (a non-null `mergedAt` means `merged`). Normalize
`APPROVED`, `CHANGES_REQUESTED`, and `REVIEW_REQUIRED`; a complete null
`reviewDecision` means `no_decision`. Missing fields, command errors, malformed
JSON, or unknown enum values are incomplete reads, never an empty result.

Also fetch the diff and changed files:

```sh
git diff <base-SHA> <head-SHA> --stat
git diff <base-SHA> <head-SHA> --name-status
```

Run `scripts/collect-context.py` as specified in `report.md` to capture metadata,
patches, statistics and sources. The collector pins revisions and checks for a
changed PR head. Reviewers read its context file rather than reproducing this
data in model output. Use the helper's GraphQL thread reader for review threads;
they are not a `gh pr view --json` field.

## 3. Commit mode

Given `BASE..HEAD` (or `BASE HEAD`):

```sh
git diff BASE HEAD --stat
git diff BASE HEAD
git log --oneline BASE..HEAD
```

The effective change is exactly `git diff BASE HEAD`.

## 4. Local mode

When asked to review unpushed/local work, never silently exclude changes:

```sh
git status --short --branch
git branch -vv
git log --oneline -10
git diff --stat
git diff
git diff --cached --stat
git diff --cached
git log @{upstream}..HEAD --oneline  # commits ahead of upstream, if upstream exists
```

Determine working-tree changes, staged changes, local commits, upstream
branch, and commits ahead of upstream. The effective range is the union of
all three; state clearly which part each change comes from.

## 5. Generated files

Identify likely-generated paths (`node_modules/`, `dist/`, `build/`,
`coverage/`, `generated/`, `*.lock`, `*.min.js`, vendored code) via the
diff stat plus repo inspection. Do not blindly exclude everything named
`generated` — check whether the generated file is itself the meaningful
change (e.g. a checked-in migration or schema). Mark excluded files and
the reason.

## 6. Project instructions

Look for, in repo root and affected directories:

- `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`
- `.pr-review/rules.md`, `.pr-review/ignore.md`, `.pr-review/config.yaml`
  (see `../references/config.md`)
- language-specific rules (e.g. `pyproject.toml`, `eslint.config.*`)

Record which instruction files were found and which rules apply.

## Output

Return the collector's context.json path together with applicable project
instructions and any previous-review evidence. Keep full diffs available in that
file; pass file paths to agents rather than copying the same diff into each
prompt. The collector owns its schema; do not hand-construct a second context
format. Recollect if the reviewed PR head or local snapshot changes.

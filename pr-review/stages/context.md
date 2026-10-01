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
gh pr view <PR> --json number,title,body,author,baseRefName,headRefName,baseRefOid,headRefOid,state,mergeStateStatus,labels,reviews,reviewThreads,comments,files,additions,deletions,url,createdAt,updatedAt
gh pr diff <PR>
```

Collect: repository, PR number, URL, title, description, author, base ref,
head ref, base SHA, head SHA, merge state, review state, existing reviews,
review comments, review threads, linked issues (parse body + `gh issue`
if needed).

Use the exact base SHA and head SHA for the review range. Do not infer the
range from branch names when SHAs are available.

Also fetch the diff and changed files:

```sh
git diff <base-SHA> <head-SHA> --stat
git diff <base-SHA> <head-SHA> --name-status
```

Build the report's required `changes[]` data from this exact range. Include
one item per changed path with status, additions, deletions, and its unified
patch. For PRs, use the `gh pr diff` output tied to the resolved head SHA;
after collecting it, re-read the PR head SHA and restart context collection
if it changed. For commit/local reviews use `git diff <base> <head>`. Preserve
each file's patch boundaries so the Changes tab can render accurate line
anchors.

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

Return a structured context object:

```json
{
  "repository": "owner/repo",
  "mode": "pull_request | commit_range | local",
  "base": "<sha>",
  "head": "<sha>",
  "merge_base": "<sha, if relevant>",
  "pr": { "number": 123, "title": "...", "author": "...", "...": "..." },
  "changed_files": ["src/a.ts"],
  "changes": [{"path":"src/a.ts","status":"modified","additions":2,"deletions":1,"patch":"@@ ..."}],
  "excluded_files": [{ "file": "dist/b.js", "reason": "generated" }],
  "commits": [{ "sha": "...", "subject": "..." }],
  "previous_review": { "head_sha": "...", "findings": [] },
  "instructions": ["AGENTS.md"],
  "diff_stat": "..."
}
```

Keep the full diff available to downstream passes but do not paste it into
every sub-agent prompt — pass file lists plus the diff, or a path to a
saved diff file under `/tmp/pr-review/`.

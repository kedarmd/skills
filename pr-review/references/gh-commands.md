# `gh` command reference for pr-review

All GitHub reads/writes go through `gh`. Do not use raw HTTP when `gh` covers it.

## Read

```sh
gh pr view <PR> --json number,title,body,author,baseRefName,headRefName,baseRefOid,headRefOid,state,mergeStateStatus,labels,reviews,comments,files,additions,deletions,url
gh pr diff <PR>
gh pr checks <PR>
gh pr comments <PR>              # if supported by gh version
gh api repos/OWNER/REPO/pulls/PR/comments
gh api repos/OWNER/REPO/pulls/PR/reviews
gh issue view <N> --json title,body,labels,comments
```

## Write (actions skill only, explicit confirmation required)

```sh
# Diff-anchored inline comment
gh api repos/OWNER/REPO/pulls/PR/comments \
  -f body="$BODY" -f commit_id="$HEAD_SHA" \
  -f path="$FILE" -f line="$LINE" -f side="RIGHT"

# Review events
gh pr review PR --comment -b "$BODY"
gh pr review PR --request-changes -b "$BODY"
gh pr review PR --approve -b "$BODY"

# Plain comment
gh pr comment PR --body "$BODY"

# Merge or close a pull request (only after explicit report confirmation)
gh pr merge PR --repo OWNER/REPO --match-head-commit HEAD_SHA --merge
# or --squash / --rebase, as explicitly selected by the reviewer
gh pr close PR --repo OWNER/REPO
```

Notes:

- Inline `line` is the diff line on the given `side`, not always the file
  line — verify against `gh pr diff` before posting.
- `commit_id` must be the head SHA the lines were validated against.
- On stale-SHA / invalid-line errors, re-resolve and ask before resending.

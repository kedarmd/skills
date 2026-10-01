> Internal stage of the `pr-review` skill. Reached only through `../SKILL.md` — never invoked directly as a skill.


# Finding Validation

Receive candidate findings from independent reviewers. Output the accepted
finding list matching `../schemas/finding.schema.json` (+ `../schemas/review.schema.json`).

## 1. Validate

For every candidate:

- [ ] File exists at head SHA; line range exists and matches claimed code.
- [ ] Finding is in (or directly blocks) the review range — not unrelated.
- [ ] Issue is reproducible or logically demonstrated, not hypothetical.
- [ ] Impact is credible under realistic conditions/workload.
- [ ] No other code already prevents it (check callers, guards, config).
- [ ] Existing tests checked (does a test already cover/prevent it?).
- [ ] Introduced or materially exposed by this change.

Drop speculative findings. False positives are worse than missing
low-impact issues.

## 2. Deduplicate

Multiple reviewers may flag the same root cause from different angles.
Merge into one finding; preserve the best title, combine `evidence` and
`suggestions`, keep the tightest line range. Cross-reference merged IDs in
`evidence` if useful.

## 3. Severity (exactly one)

- `CRITICAL` — catastrophic: RCE, irreversible data loss, severe auth
  bypass, production-wide failure.
- `HIGH` — significant: wrong production behavior, security problem,
  serious corruption, major regression, broken critical workflow.
- `MEDIUM` — meaningful under realistic conditions or likely future defect.
- `LOW` — minor but actionable.

Do not inflate. Do not use severity for confidence — record `confidence`
(0–1) separately. Normally discard `confidence < 0.6` unless further
verification raises it.

## 4. Source location

Smallest range demonstrating the problem. Prefer `src/a.ts:42-47` over a
whole file. For PR comments also record:

```json
{ "file": "src/a.ts", "start_line": 42, "end_line": 47, "side": "RIGHT", "commit_sha": "<head-sha>" }
```

`RIGHT` = new/head side, `LEFT` = removed/base side.

## 5. Status (follow-up reviews)

- `new` — first seen in this review
- `unresolved` — previously reported, still present
- `addressed` — author attempted a fix, needs re-check
- `resolved` — fixed by new changes
- `regressed` — fix attempt introduced a new problem
- `discarded` — dropped as invalid (keep out of report, log internally)

## 6. Finding structure

Must validate against `../schemas/finding.schema.json`. Required: `id`
(`F-001`…), `severity`, `status`, `title`, `summary` (one sentence),
`locations[]` (≥1), `reason`, `impact`, `evidence`, `confidence`,
`suggestions[]` (may be empty, each with `id`, `title`, `comment`, `code`).

> Internal stage of the `pr-review` skill. Reached only through `../SKILL.md` — never invoked directly as a skill.


# Finding Validation

The review agent validates its candidates and returns the findings in
`../schemas/analysis.schema.json`.

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
Merge into one finding; preserve the best title, combine evidence and recommendations, keep the tightest line range. Cross-reference merged IDs in
`evidence` if useful.

## 3. Severity (exactly one)

- `CRITICAL` — catastrophic: RCE, irreversible data loss, severe auth
  bypass, production-wide failure.
- `HIGH` — significant: wrong production behavior, security problem,
  serious corruption, major regression, broken critical workflow.
- `MEDIUM` — meaningful under realistic conditions or likely future defect.
- `LOW` — minor but actionable.

Use severity for impact. Investigate uncertain candidates further or drop them.

## 4. Source location

Smallest range demonstrating the problem. Prefer `src/a.ts:42-47` over a
whole file. For PR comments also record:

```json
{ "file": "src/a.ts", "start_line": 42, "end_line": 47, "side": "RIGHT", "commit_sha": "<head-sha>" }
```

`RIGHT` = new/head side, `LEFT` = removed/base side.

Source excerpts are extracted by the builder from the reviewed snapshot.

## 5. Status (follow-up reviews)

- `new` — first seen in this review
- `unresolved` — previously reported, still present
- `addressed` — author attempted a fix, needs re-check
- `resolved` — fixed by new changes
- `regressed` — fix attempt introduced a new problem
- `discarded` — dropped as invalid (keep out of report, log internally)

## 6. Handoff

Return only the analysis contract: judgment and source coordinates, with an
optional recommendation. Scripts assign IDs, extract source excerpts, attach
SHAs, and derive counts. Run the prepare command before sending accepted
findings to the comment agent. That agent reads `comments.md` and produces
only the comments contract; it cannot change accepted evidence or severity.

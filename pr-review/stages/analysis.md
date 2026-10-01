> Internal stage of the `pr-review` skill. Reached only through `../SKILL.md` — never invoked directly as a skill.


# PR Review Analysis

Review only the supplied review range and its relevant surrounding code.
Objective: real defects, regressions, security issues, important omissions.
Optimize for correctness, not finding count.

Each pass receives: repository root, review range (base/head SHAs), PR
context, project instructions, changed files, and the diff. Passes MUST NOT
modify repository files. Each pass returns structured findings matching
`../schemas/finding.schema.json`.

If the host supports isolated sub-agents, delegate passes in parallel.
Otherwise run the same passes sequentially. Either way, keep passes
independent — do not let one pass's draft findings bias another.

## Passes (skip irrelevant ones, state why)

### Correctness

Control flow, state transitions, edge cases, assumptions, null/undefined
handling, wrong conditions, wrong transformations, off-by-one, unit errors.

### Regression

Changed behavior vs. callers, backward compatibility, existing workflows,
feature flags, migration concerns, removed/renamed exports.

### Security

Auth, authz, input validation, injection, secrets, sensitive-data exposure,
unsafe deserialization, path traversal, SSRF, permission boundaries. Only
report concrete concerns with an attack/data-flow path — no speculative
vulns. State the path explicitly in `evidence`.

### Reliability

Error handling, retries, timeouts, partial failures, resource cleanup,
race conditions, concurrency/state management, idempotency.

### API / Contracts

API compatibility, schema assumptions, type contracts, serialization,
consumer expectations, versioning.

### Data

Persistence, transactions, consistency, migrations, validation,
irreversible operations, data loss paths.

### Testing

Whether important changed behavior has appropriate coverage. Report missing
tests only when the behavior is important/complex enough that omission is
meaningful regression risk — not merely because tests could exist.

### Performance

Unnecessary repeated work, N+1 behavior, expensive operations in hot paths,
memory/resource growth, algorithmic regressions. Only with a credible
workload — state it in `impact`.

### Maintainability

Confusing abstractions, duplicated behavior, dangerous coupling, patterns
likely to cause defects. No subjective style preferences without a project
rule.

## Evidence standard

Every finding must answer:

1. What is wrong?
2. Where is it? (file + exact lines at head SHA)
3. Why does it happen?
4. Under what conditions?
5. What is the impact?
6. Why does existing code not already prevent it?

If any answer is missing, do not report — keep investigating or drop it.

Include a `confidence` (0–1) per finding. Below ~0.6, either verify further
or drop. The validation stage (`findings.md`) rechecks everything.

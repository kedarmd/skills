> Internal reference of the `penpot-ux-guardian` skill. Loaded only
> through `../SKILL.md` — never invoked directly as a skill.

# Approval Protocol

Two gates, two distinct decisions. Neither implies the other.

## Gate A — design-system approval

Authorizes ONE specific proposal revision (tokens / components /
variants / modifications named in it). Scope:

- Every design-system change needs it — additions AND modifications,
  including token value edits. (Strict policy.)
- The agent presents the proposal (`templates/design-proposal.md`),
  its self-validation, and a draft preview when supported, then WAITS.
- No canonical edits and no dependent screen work before explicit
  approval of that revision.

## Gate B — screen approval

Authorizes acceptance of the built screen at its presented revision.
Scope:

- Presented only after validation per `validation.md` with the report
  attached (pass/fail per layer, unverifiable items named, residuals).
- Passing validation is not approval. The agent always waits for the
  human decision.

## Proposal lifecycle

```text
draft (rev N) → presented → APPROVED[rev N] | REJECTED[rev N] + feedback
              → on reject: revise to rev N+1, re-present
              → on approve: apply rev N only → verify → log
```

- Approval binds to the revision presented. New edits need a new
  revision and a new approval.
- Rejection handling: revise the proposal from the feedback and
  re-request. Never implement the rejected design, never freelance an
  unasked alternative, never bundle unrelated changes into the
  revision.

## Stop conditions (must halt and wait)

1. Proposal written, awaiting Gate A.
2. Screen validated, awaiting Gate B.
3. Ambiguous / contradictory comment or feedback.
4. Requested change breaks an approved rule with no approved exception.
5. Correction bound (3 rounds) exhausted with issues remaining.
6. Required verification impossible with available MCP tools.

## Review log

Every gate decision is appended to the project review log (default
`penpot.review-log.md`, seeded from `templates/review-log.md`):
proposal id + revision, decision (approved/rejected), what changed,
validation verdict, screen decision, unresolved items, timestamp.

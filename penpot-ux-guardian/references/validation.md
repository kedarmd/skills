> Internal reference of the `penpot-ux-guardian` skill. Loaded only
> through `../SKILL.md` — never invoked directly as a skill.

# Validation

Validate against live Penpot data, never against intent or memory.
Prefer exact property comparison over visual guessing.

## Layer 1 — Geometric validation (needs C2, C5)

- Horizontal / vertical alignment of related elements (exact coords).
- Sibling gaps: same-role siblings share the same gap value.
- Margins and padding against layout rules / spacing tokens.
- Component bounding boxes vs. contract dimensions
  (e.g. every `btn/primary` instance is h=40).
- Overlaps, clipping, overflow, off-frame objects.
- Container constraints hold (children inside bounds, grid rules kept).

## Layer 2 — Design-token validation (needs C3, C4, C6, C7)

- Every fill / text color resolves to an approved token (exact value
  match) unless a documented exception exists.
- Typography matches family + size + weight + line-height exactly.
- Spacing / radius / border / effect values resolve to tokens.
- Instances use approved variants/states; flag detached copies and
  local overrides as drift.
- No unapproved effects, strokes, or fills introduced during the task.

## Layer 3 — Visual inspection (needs C11)

Using screenshots / rendered exports plus metadata:

- Optical alignment and visual balance.
- Uneven whitespace, crowded composition.
- Text wrapping, truncation, overflow at realistic content lengths.
- Icon optical alignment.
- Rendered result matches intended layout; note any divergence.

## Layer 4 — Correction and revalidation

1. Batch all actionable findings; fix within approved constraints
   (fixes that need new tokens/variants re-enter the proposal flow).
2. Re-run affected checks after each batch — never report clean merely
   because edits finished.
3. Confirm no new violations were introduced.
4. Bound: at most 3 rounds per issue batch; then stop and report the
   residual as `unresolved`.
5. Anything the MCP cannot expose is `unverifiable`, with the missing
   capability named.

## Tolerances

- Exact: token color values, type scale values, component fixed
  dimensions, variant identity. No tolerance.
- Near-exact (±0.5px): alignment and gap computation from exported
  coordinates (rounding only).
- Judgmental: optical balance, whitespace feel, icon centering from
  screenshots — report as `advisory`, not pass/fail, and ask the human
  where uncertain.

## Proposal validation (for Gate A)

Apply Layers 1–3 to the draft proposal: contract completeness, token
traceability, consistency with sibling components (e.g. new badge uses
the same radius/type scale as existing badges), and no collision with
existing names or values.

## Report format

```text
Validation — <target> @ <Penpot ref> — <timestamp>
Capabilities: <C-block summary>
Layer 1 (geometry): PASS | FAIL(findings) | UNVERIFIABLE(reason)
Layer 2 (tokens):   PASS | FAIL(findings) | UNVERIFIABLE(reason)
Layer 3 (visual):   PASS | ADVISORY(notes) | UNVERIFIABLE(reason)
Corrections: <round 1..3: what fixed, re-check outcome>
Residual / unresolved: <items needing human judgment or missing tools>
Verdict: CLEAN (zero known unapproved inconsistencies)
       | ISSUES-REMAINING (list) | PARTIAL (unverifiable items named)
```

`CLEAN` means zero *known, unapproved* inconsistencies — not a promise
of zero visual defects. Human review at Gate B is still required.

> Internal reference of the `penpot-ux-guardian` skill. Loaded only
> through `../SKILL.md` — never invoked directly as a skill.

# Acceptance Criteria

Definition of done for any run of this skill.

## Done requires ALL of

1. **Contract traceability.** Every color, type style, spacing,
   radius, border, effect, and component instance on the touched
   targets resolves to the manifest or a documented layout constraint.
   Zero unapproved values; zero detached-copy drift.
2. **Gate discipline.** Gate A approval exists for every
   design-system addition/modification applied (per revision). Gate B
   presentation happened with the validation report attached. Nothing
   was declared accepted on agent authority.
3. **Validation executed.** `validation.md` ran against live Penpot
   data for the touched targets. Verdict recorded per layer
   (PASS / FAIL / UNVERIFIABLE / ADVISORY). Corrections re-checked;
   3-round bound respected.
4. **Uncertainty visible.** Every check the MCP could not perform is
   named as unverifiable with its missing capability — never silently
   passed.
5. **Records updated.** Manifest reflects applied changes
   (`scripts/check-manifest.py` passes); review log holds proposals,
   revisions, decisions, validation verdicts, and unresolved items.

## Objective pass/fail

- **PASS** — all five hold; verdict `CLEAN` or `CLEAN with named
  unverifiable items`; awaiting (Gate A) or received (Gate B) human
  decision with no open contradictions.
- **FAIL** — any unapproved deviation remains, any gate was skipped,
  validation was not run against live data, or records are stale.

## Verdict language

Report literally:

```text
Acceptance: PASS | FAIL — <target> — <timestamp>
Traceability: <statement>
Gates: A=<status/rev> B=<status/rev>
Validation: L1=<..> L2=<..> L3=<..> (unverifiable: <items>)
Records: manifest=<path:status> log=<path:status>
Unresolved: <none | list>
```

The objective is zero *known, unapproved* inconsistencies at review
time — not a guarantee of zero visual defects. Visual judgment items
stay `ADVISORY` for the human.

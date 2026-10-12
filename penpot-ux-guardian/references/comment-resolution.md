> Internal reference of the `penpot-ux-guardian` skill. Loaded only
> through `../SKILL.md` — never invoked directly as a skill.

# Comment Resolution

Penpot comments are actionable feedback. One run handles either a
targeted scope (named component/screen) or the whole selected page —
confirm scope with the user when ambiguous, defaulting to the narrower
scope.

## 1. Collect

- If C12 (comment reading) is YES: fetch outstanding comments for the
  agreed scope; record id, author, target ref, and verbatim text.
- If NO: use the manual fallback — ask the user to paste each comment
  with its target (page/frame/component name). Treat each pasted item
  as one feedback record. Never claim Penpot comments were read.
- Preserve original text; associate every fix with its comment id.

## 2. Triage each comment

Translate it into an actionable requirement, then classify:

- **Case A — screen problem.** Fixable within approved tokens,
  variants, and layout rules.
  Example: "spacing between table and filter bar is too large."
  → adjust to the correct spacing token; no proposal needed.
- **Case B — design-system problem.** Needs a new/modified token,
  component, variant, or state.
  Example: "needs a more compact density variant."
  → write a proposal per `design-system.md` and STOP for Gate A
  before touching canonical assets or dependent work.
- **Ambiguous / contradictory / rule-breaking.** Ask for clarification;
  never guess. If a comment requests violating an approved rule, say so
  and propose compliant alternatives or a formal exception proposal.

## 3. Fix

- Case A: edit the affected objects and their directly surrounding
  layout only. Do not restyle unrelated areas.
- Case B: only after Gate A approval, apply the approved revision,
  update the manifest, then fix the screen.
- If C13 (reply/resolve) is NO, do not claim threads were resolved in
  Penpot; list what was fixed per comment id and ask the human to
  resolve the threads.

## 4. Revalidate (mandatory)

Re-run `validation.md` on affected objects plus surrounding layout.
Corrections that introduce new violations are reworked within the
3-round bound; leftovers are reported as unresolved per comment id.

## 5. Report

```text
Comments resolved — <scope> — <timestamp>
A (screen fixes): <comment id → change → revalidation outcome>
B (system proposals): <comment id → proposal rev → gate status>
Needs clarification: <comment id → question>
Unresolved: <comment id → reason>
```

Never close the run by redesigning unrelated areas or by treating a
Gate A approval as screen acceptance.

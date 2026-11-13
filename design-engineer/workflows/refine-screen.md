# Refine an existing screen

**Use when:** correcting UI or applying feedback. Defining behavior: repair within approved rules without unnecessary system approval.

**Inputs:** target screen/revision, feedback, current approved constraints, relevant surrounding UI, states and viewports.

1. DISCOVER the actual target and before-state evidence. Translate feedback into observable outcomes and separate pre-existing debt from task-induced changes.
2. CONTRACT: classify each change with [change-control](../protocol/change-control.md). Copy, geometry, responsiveness or composition corrections within existing rules proceed. Canonical changes route to [design-system change](design-system-change.md) before dependent writes.
3. PLAN affected relationships through [layout-construction](../protocol/layout-construction.md), preserving identities, variants and existing behavior.
4. EXECUTE only the target and authorized dependencies. Inspect actual state after partial failures.
5. VERIFY through [layout-evidence](../protocol/layout-evidence.md), including adjacent layout, existing interactions/states and requested viewports. PRESENT before/after evidence and separate screen acceptance.

**Complete when:** feedback is addressed or explicitly blocked, regression checks are recorded, and unrelated UI remains unchanged.

**Recovery:** report unrelated drift without opportunistic repairs. Failed checks return to scoped correction under the central limit; unresolved authority returns to CONTRACT.

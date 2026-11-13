---
name: design-engineer
description: >
  Design product UI for new and existing products: create screens, refine
  feedback, audit or evolve design systems, and adapt inspiration. Reuse
  approved components, govern canonical changes, construct constrained layouts,
  and verify actual output across design tools.
---

# Design Engineer

Design against an explicit contract. Verify actual output, not intended changes.

## Route the task

Inspect the current product before selecting a route; an installed skill does not imply a greenfield product. Load the matching workflow, then only the references its conditions require. Multiple routes can compose under the lifecycle below; they do not start separate approval processes.

| Requested outcome | Workflow |
| --- | --- |
| Establish a product with no existing baseline | [New product](workflows/new-product.md) |
| Add a feature or screen to a product | [New screen](workflows/new-screen.md) |
| Correct or refine existing UI from feedback | [Refine screen](workflows/refine-screen.md) |
| Add, revise, remove, or migrate canonical definitions | [Design-system change](workflows/design-system-change.md) |
| Inventory, adopt, or assess an existing system | [Audit](workflows/audit.md) |
| Research or adapt visual references | [Inspiration](workflows/inspiration.md) |

Use new-screen for an existing product even when its system is undocumented; reconcile only relevant dependencies. Add the system-change route when a canonical dependency is missing or unsuitable. Add inspiration when references inform the task. An explicit redesign preserves decisions outside the authorized change.

## Lifecycle

Each phase consumes the preceding phase's evidence. Keep a concise task record in the project's existing format: scope, contract sources/authority, construction constraints, mutations, checks, and outstanding decisions. No new registry or paperwork is required merely to use this skill.

### DISCOVER — establish the actual baseline

**Inputs:** user request, product artifacts, available tools.

Inspect requirements, users, journeys, content, existing UI, relevant screens, reusable assets, canonical libraries, prior decisions, and project constraints. Discover actual read/write/render capabilities through [tool-interface](protocol/tool-interface.md), required before tool operations or verification claims. Identify target viewports/states, affected dependencies, and pre-existing drift.

**Exit:** scope, relevant baseline, available evidence, and tool limitations are identified. Missing critical access or ambiguous scope blocks only dependent work; report the smallest missing input.

### CONTRACT — establish applicable authority

**Inputs:** baseline and decision evidence.

Read [system-model](protocol/system-model.md) when establishing or reconciling rules. Classify applicable definitions as approved, verified convention, inferred, conflicting, or missing. Preserve identifiable approvals and canonical sources. Before introducing a component, inspect the approved library and reuse an equivalent asset.

For uncertain authority or any canonical change, read [change-control](protocol/change-control.md). Obtain the scoped decision before dependent mutations. Screen-local corrections within approved rules proceed without another system approval. Before touching an out-of-scope element, establish an authorized dependency or leave it unchanged.

**Exit:** applicable constraints and their authority are recorded; blocking approvals/conflicts are resolved or isolated. Existing patterns alone do not establish approval.

### PLAN — specify structural relationships

**Inputs:** task contract, reusable assets, actual content, states and viewports.

Before layout creation or modification, read [layout-construction](protocol/layout-construction.md). Specify components/variants, tokens, parent-child hierarchy, layout primitives, alignment, spacing/padding, sizing, responsive behavior, and relevant states. Define measurable expected relationships independently of eventual read-back measurements.

**Exit:** construction relationships and applicable checks are explicit. Missing constraints that determine correctness block affected construction. Read-only work instead plans its inspection or research evidence.

### EXECUTE — apply the authorized scope

**Inputs:** construction plan and applicable approvals.

Apply scoped mutations using approved assets. Preserve stable identities and reusable linkages where supported. After a partial failure, inspect the actual state before retrying or continuing dependent writes. Read-only routes gather evidence here without mutations.

**Exit:** actual applied changes are known and ready for independent verification. Uncertain writes or unsafe canonical operations block dependent work.

### VERIFY — compare actual output with the contract

**Inputs:** expected constraints, mutation record, fresh actual read-back and renders.

Read [layout-evidence](protocol/layout-evidence.md) for every changed design and any verification audit. Check applicable geometry, styles, tokens, identity/linkage, content, states, responsiveness, and rendered quality. Tool success and generated mutation payloads are not output evidence. Check capability and coverage before claiming PASS; unsupported checks are UNVERIFIABLE.

A failure returns to scoped correction and another relevant verification pass. Stop after three correction passes for the same unresolved failure, or earlier for unsafe changes, missing approval, or no progress. Report evidence and the blocker; independent authorized work may continue.

**Exit:** supported mandatory checks pass, or failures and limitations are explicitly recorded as incomplete. Full success requires evidence for every mandatory check. Read-only routes verify findings against sources rather than claim implemented output.

### PRESENT — show evidence and obtain the right decision

**Inputs:** actual output, check results, unresolved issues.

Show the actual artifact or render when available; otherwise identify it and the presentation limitation. Explain meaningful applied changes, reused assets, evidence sources/viewports/states, numeric and visual results, introduced versus pre-existing issues, limitations, and outstanding decisions. Keep the report proportional to the task.

**Exit:** the user can inspect the result and distinguish applied work from proposals. Request screen acceptance for a changed screen separately from any system decision. Validation establishes neither user acceptance nor approval history.

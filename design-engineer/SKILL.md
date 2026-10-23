---
name: design-engineer
description: >
  Design, extend, maintain, and review product UI for both new and existing
  projects. Enforce existing approved design systems, govern changes through
  user approval, check real spacing and geometry, and adapt inspirations to
  the product. Works across design tools rather than depending on Penpot.
---

# Design Engineer

## Scope and operating principle

This skill was authored **from scratch** and has no dependency on previous skills, their Markdown, scripts, validators, templates, or manifests. **This does not mean the project must be greenfield.** Existing product UI, documented requirements, canonical design libraries, approved decisions, and established visual conventions are essential evidence. Read and preserve them when working on an existing product. Never discard, recreate, or reapprove an already established design system merely because the skill itself is new.

The role is **continuous design-system governance**: remain creative in research and proposals, but rigorous in the execution and validation of agreed design rules.

## Non-negotiable rules

1. **Product first.** Understand real users, platform, workflows, states, content, constraints, and the existing product before designing. Inspirations supply principles, not copyable screens.
2. **Respect the actual baseline.** Locate and inspect the project's current canonical system and designs. Use established, approved definitions as-is. Record evidence of their authority; do not invent approval history. Do not silently declare an inferred pattern approved.
3. **Prefer reuse.** Screens must use approved tokens, component instances, variants, constraints, and composition rules. No detached lookalikes, arbitrary spacing, or styling overrides.
4. **Approve system changes before dependency.** New/modified/removed canonical tokens, components, variants, states, and layout rules require a scoped proposal and explicit user approval **before** changing the canonical system or building the dependent screen. This includes changes proposed while implementing features or reacting to inspiration.
5. **Do not block normal maintenance unnecessarily.** Repairing a screen-local violation to match an existing approved rule is not a design-system modification. Unchanged, demonstrably approved definitions do not require repeated approval.
6. **Measure the result.** Inspect fresh, read-back geometry and styles, and compare alignments, bounding boxes, padding, gaps, overflow, typography, variants, and linkages with the contract. Never validate only intended edits.
7. **Check the render.** Review hierarchy, rhythm, optical balance, content length, contrast, responsive behavior, and relevant states separately from numeric checks.
8. **Make uncertainty explicit.** Unsupported capabilities are `UNVERIFIABLE`, never `PASS`; no fabricated tool access, measurements, or approvals.
9. **Separate acceptance.** User approval of a design-system proposal does not approve the resulting screen; successful validation does not mean the screen was accepted.
10. **Control scope.** No opportunistic restyling or mass refactoring of unaffected screens. Surface pre-existing inconsistencies as findings and ask before expanding scope.

## Always start with a project assessment

1. Read applicable PRD/requirements, ADRs, user journeys, current screen designs, canonical components, tokens, composition rules, supported viewports, and available decision records. For an existing project, inspect the *actual live UI* as well as documentation when possible.
2. Discover design-tool capabilities via `protocol/tool-interface.md`. Don't assume Penpot, Figma, or any particular application.
3. Identify the working mode and baseline condition:
   - **New project**: no existing UI/system; propose a new contract.
   - **Existing approved system**: identify the canonical source and approved revision; reuse without blanket reapproval.
   - **Existing partial/undocumented system**: inventory the real UI, distinguish verified conventions from inferred ones, propose a baseline or only its unresolved parts for approval; don't silently overwrite assets.
   - **Explicit redesign**: identify which existing decisions the user wants changed, and which remain in force.
4. Map the current approved system to the neutral registry described by `protocol/system-model.md`. Mapping is an observation, **not** a design-system mutation. Check source identity and real component properties. If authority/approval cannot be established, ask for scoped baseline confirmation before relying on inferred definitions for production work. Do not fabricate an approval reference.
5. Define the requested change, affected screens, dependencies, existing components to reuse, and boundaries. Distinguish pre-existing drift from changes introduced by this task.

## Working modes

### 1. Establish a system for a new product

Research product needs and platform conventions. Propose a coherent foundation, components, states, accessibility rules, composition patterns, and viewports. Validate draft feasibility; request user approval before canonical creation and dependent screens. Record the approved revision.

### 2. Adopt or audit an existing design system

Inspect canonical tool assets, real screens, tokens, component variants, and current governance. Build an evidence-backed inventory and map approved assets into the neutral contract **without changing or resetting them**. Preserve existing approvals where identifiable. If the system is undocumented or its authority is uncertain, propose a reviewable baseline with clearly marked verified/inferred details; obtain user confirmation before declaring uncertain details canonical. Report drift separately from undocumented conventions.

### 3. Add a feature or design a new screen

1. Write a focused brief: intended workflow, existing entry points, screen states, realistic content, viewports, and acceptance criteria.
2. Inspect relevant existing screens and locate reusable approved components and layout patterns; record dependencies and impact.
3. If an approved definition is missing or unsuitable, follow `protocol/change-control.md`: propose a new or revised system element, preview it in isolation, and **stop** dependent screen implementation until the user approves that revision.
4. Apply approved system changes, verify them in the canonical library, and update the system revision/decision record.
5. Build the screen using live reusable instances and approved composition rules; do not change unrelated screens.
6. Read back live geometry/styles and validate according to `protocol/layout-evidence.md`. Fix screen-local violations and recheck.
7. Inspect actual renders at relevant viewports/states; document unresolved items; request screen approval and record the decision.

### 4. Refine an existing screen or resolve design feedback

Compare the requested change against the approved baseline. Fix spacing, geometry, layout, and content problems **within existing rules** without seeking a system change approval. When feedback requires changing a token, component, variant, or canonical rule, propose it first and pause dependent edits. Check the target and immediate surroundings for regressions, and do not modify unrelated areas. Present before/after evidence for acceptance.

### 5. Evolve or refactor the design system

Audit current usage and drift. Assess migration impact across existing screens and states. Propose changes with affected dependencies, compatibility strategy, exact metrics, and rollback considerations. Each scoped revision needs explicit approval before canonical edits. Update affected screens only to the approved extent and revalidate them.

### 6. Research inspiration and synthesize a direction

Follow `protocol/inspiration.md`. Decompose the inspiration into principles, research the product's needs and alternatives, and synthesize a product-specific direction. Respect existing approved foundations; changes to those foundations require normal system approval.

## Validation and tool support

Use `protocol/layout-evidence.md` to distinguish numeric machine-checkable assertions from rendered visual review. If available, the **new** dependency-free Node.js verifier `bin/verify-layout.mjs` reads a neutral approved system registry and a fresh scene export. The tool adapter must provide genuine read-back data; a constructed JSON document is not proof. The checker is optional, not a replacement for real inspection or an integration with a particular tool.

## Deliverable on each task

Report: project situation and scope; current approved system and evidence (or uncertain baseline); reused components; system proposals and their decision states; work done; evidence source and tested viewports; numeric violations and fixes; visual QA; unverifiable checks; regression/impact notes; and exact user decision needed. Keep **design-system proposal approval** and **screen acceptance** visibly separate.

Supporting references, loaded as needed:

- `protocol/system-model.md` — contract and adopting existing project systems
- `protocol/change-control.md` — changes, approvals, and scope boundaries
- `protocol/tool-interface.md` — adapter capabilities and live design evidence
- `protocol/layout-evidence.md` — read-back geometry and verification
- `protocol/inspiration.md` — research and independent interpretation

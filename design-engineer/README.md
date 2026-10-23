# Design Engineer

A tool-agnostic Agent Skills package for **new products and ongoing design work in existing products**. It supports creating a design system, adopting and maintaining an established system, incremental feature design, targeted improvements, system evolution, and audits.

## Scope clarification

**Built from scratch** describes this skill's origin, **not** the kind of product it can work on. This package was written independently of previous skills. It does not depend on legacy skill files, validators, manifests, templates, or migration scripts.

**Existing project assets are different from old skill code.** A project's current UI, canonical component library, design tokens, documentation, user decisions, and design history are vital sources of truth. Preserve them when the user is continuing an existing product. Do not replace a working design system just because this skill is newly installed.

## Supported use cases

| Project situation | Behavior |
| --- | --- |
| New product, no system | Research the product, propose foundations/components, obtain approval, then build screens. |
| Existing approved design system | Inspect and map approved assets; reuse them without requiring fresh approval for unchanged definitions. |
| Existing product without a formal system | Inventory the current UI and patterns; propose a baseline, flag uncertainty, and obtain approval before declaring it canonical. |
| New feature in an existing product | Reuse approved components; propose and obtain approval for missing parts before using them in new screens. |
| Iterative screen updates | Make scoped changes within existing rules; verify that surrounding UI and unrelated screens were not altered. |
| System refinement or redesign | Audit, assess effects on existing screens, present revision-scoped proposals, and apply only approved changes. |
| Inspiration-led request | Research transferable principles and adapt to the product; don't blindly reproduce the reference. |

## Workflow summary

1. Identify the task and inspect the **actual product** (requirements, live designs, system library, previous decisions).
2. Determine whether the design system is already approved, partially documented, or missing. Map the existing approved system into the skill's neutral contract without modifying canonical assets.
3. For a change that needs a new/modified system element, propose that change and **stop for user approval before dependent screen work**.
4. Compose or update only the requested screens using approved system assets.
5. Read back real geometry and styles, run objective checks where supported, inspect rendered output, and present the screen for acceptance.

The optional dependency-free Node.js checker validates normalized **actual design measurements** against an approved system contract. It does not integrate with a design tool by itself or certify visual quality.

```bash
node --test tests/verify-layout.test.mjs
node bin/verify-layout.mjs examples/approved-system.json examples/valid-scene.json
```

These examples are **simulated** and are not approvals, genuine design-tool exports, or prescribed product tokens.

## Installation

Install the `design-engineer/` directory in your agent's skills location. `SKILL.md` is the entry point; `protocol/` contains supporting instructions loaded as needed.

## Limitations

- A capable adapter is needed to read back live design-tree measurements and reusable-component links from Penpot, Figma, or another tool.
- If a required property cannot be measured, the check is `UNVERIFIABLE`, not `PASS`.
- Code-based geometry checks complement, but cannot replace, visual and human review.
- Approval must come from the user or an identifiable existing approved project decision; it cannot be fabricated from the presence of a file or a successful test.

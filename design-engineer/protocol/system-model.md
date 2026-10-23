# Governed product design-system model

The design system can be **newly created, pre-existing and approved, or incompletely documented**. Its current canonical reality is the starting point for existing projects. The skill's registry is a portable *representation* of approved product decisions, not an instruction to replace the real system.

## Discover the system's status

- **New**: no system or accepted visual baseline yet. Research and propose one, then obtain approval before implementation.
- **Established and approved**: locate design-library assets, tokens, docs, and decision evidence. Verify they agree. Preserve existing approved definitions; no blanket new approval required merely to create a normalized registry.
- **Partial or undocumented**: inspect actual UI and reusable assets; label each candidate rule as `verified`, `inferred`, or `conflicting`. Request focused baseline confirmation for uncertain elements rather than pretending the extracted model is authoritative.
- **Drifted**: a screen instance differs from an approved definition. Treat screen-local repair separately from changes to the definition itself.

When evidence for prior approval is missing, a user's explicit confirmation of the extracted baseline can establish a new baseline decision. Don't manufacture a prior approval or treat popular repetition across screens as proof of approval.

## Contract contents

A project-owned, versioned contract should include:

1. **Foundations:** semantic colors, typography, icons, spacing, radii, borders, elevation, focus, accessibility, and applicable themes.
2. **Components:** purpose, canonical source, states, variants, dimensions, text and content constraints, internal geometry, permitted overrides, interaction behavior and accessible states.
3. **Compositions:** frames, grids, containers, adaptive behavior, alignment relationships, spacing rules, navigation patterns, and density/content rules.
4. **Traceability:** approved revisions or baseline confirmations, source references, known exceptions, design change proposals, and affected consumers/screens.

Use an unambiguous project-owned format compatible with the real design tool; JSON is the optional verifier's neutral example. Preserve the original design system as canonical unless the user specifically authorizes a transition. When converting existing assets to the neutral format, **do not silently change values or claim that conversion itself reapproves the system**.

## Existing-project reconciliation

1. Inventory the real token/component library, component instances in relevant screens, existing viewport patterns and prior decisions.
2. Establish which records are canonical and which are overrides, detached instances, deprecated assets or provisional concepts.
3. Note verified/inferred/conflicting details, references and source freshness. Don't extrapolate unknown breakpoints or variants.
4. Create a compatibility map between approved assets and the verifier contract; preserve identifiers when practical, and record aliases where necessary.
5. Surface existing inconsistencies as audit findings. Changes to **definitions** require proposal approval; repairs that restore approved rules do not.
6. For a newly requested feature, audit its **direct dependencies** first. Do not turn a small task into an unrequested complete redesign.

## Machine-readable example

The neutral verifier currently expects `version`, `revision`, `approval.status`, `approval.reference`, `tokens`, and `components` in `system.json`. An approved reference can identify an established, verifiable project approval record **or** a new user baseline decision. It must be real, not an invented string. Component contracts may contain `variants`, `fixedHeight`, `minWidth`, `styles`, and `permittedOverrides`; layout constraints are declared in the corresponding measured scene. See `layout-evidence.md`.

The sample `examples/approved-system.json` is illustrative only and its marked sample approval is not usable for a real project. A passing sample check is not evidence of approval or live read-back.

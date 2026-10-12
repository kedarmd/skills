> Internal reference of the `penpot-ux-guardian` skill. Loaded only
> through `../SKILL.md` — never invoked directly as a skill.

# Design System

## 1. Audit

For the task at hand, confirm each required token, component, and
variant:

1. Named in the project manifest (default `penpot.design-system.md`;
   seed from `templates/design-system-manifest.md` if absent).
2. Present at its canonical Penpot reference (file/page/component ID).
3. Matching the manifest on properties (see contract below).

Record one of:

- **Complete** — everything needed exists and matches. Proceed to
  screen design.
- **Incomplete** — a token/component/variant is missing.
- **Drifted** — a canonical object or an instance no longer matches
  its contract (detached copy, overridden fill, wrong height, …).

Incomplete and drifted both enter the proposal flow. The only
difference is the proposal type: `addition` vs. `modification`, both
requiring Gate A approval.

## 2. Component contract

Every reusable component needs a contract — in the manifest, in
Penpot metadata, or both. Minimum fields:

```text
name, canonical Penpot ref
variants + states
fixed vs. configurable vs. inherited properties
dimensions / sizing rules
internal padding + spacing (token refs)
typography (token refs), color (token refs)
border widths / colors / radii (token refs), effects (token refs)
alignment rules + constraints
permitted composition patterns
```

Example — button `btn/primary`:

```text
variants: default, hover, pressed, disabled, loading
size: h=40 (fixed), w=hug-content (min 96)
padding: x=spacing.md (16), gap icon-label=spacing.xs (8)
label: type.label-md, color=text.on-primary
radius: radius.md (8), fill: color.primary-600
icon: 16px, currentColor
composition: label-only | icon+label; never icon-only for this variant
```

When the Penpot MCP exposes component metadata, inspect it directly.
Otherwise the manifest is the source of truth and Penpot placement is
verified against it.

## 3. Enforcement rules

| Area | Rule |
|---|---|
| Colors | approved color tokens only; no new hex |
| Spacing | approved spacing tokens or documented layout rules |
| Typography | approved family / scale / weight / line-height |
| Components | instantiate approved component or variant; never redraw |
| Dimensions | obey contract sizing constraints |
| Alignment | defined layout relationships only |
| Borders / radii | approved tokens |
| Shadows / effects | approved effects |
| Exceptions | explicit documented exception or approved proposal |

Not every pixel is a token: page width, column gaps, and container
constraints may be governed by layout rules rather than tokens. The
test is consistency and traceability, not tokenizing coordinates.

## 4. Proposal flow (enters Gate A)

The proposal document follows `templates/design-proposal.md`:

1. Search existing assets first; name the nearest candidates and why
   each fails.
2. Specify variants, dimensions, colors (token refs or proposed new
   token values), typography, spacing, states.
3. Analyze consistency against the rest of the system.
4. Validate the proposal per `validation.md` (proposal section).
5. Preview in an isolated draft area when supported (C10); otherwise
   present the written proposal and do not touch canonical pages.
6. STOP for Gate A approval per `approval-protocol.md`.

Rejection → revise the same proposal (new revision number), never
implement the rejected design or freelance an alternative.

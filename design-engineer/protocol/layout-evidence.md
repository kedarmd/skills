# Evidence and layout precision

## Never validate intention as output

Read a **fresh** scene from the design tool after the mutation. Include exact viewport size, node IDs, hierarchy, dimensions, selected resolved style/token references, component linkage, and text-overflow observations. Measure what exists, not what the agent tried to create. Preserve a separately rendered screenshot/preview for visual review.

## Measurement rules

- Check boxes are finite, positive dimensions and inside their permitted frame; report clipping and off-canvas nodes.
- Check parent content boundaries; no child may silently overflow its container.
- For stack layouts, check order, first-child offset, consecutive sibling gaps and perpendicular alignment against declared padding and gap.
- For peer components, check declared alignment groups and contract dimensions.
- Detect unintended overlapping siblings, including invisible items occupying shared geometry. Layered decoration must be explicitly exempted.
- Verify semantic token references, style values, component variant membership and forbidden local overrides when the adapter can inspect them.
- Text-overflow and truncation checks require real measured text metadata; missing information is `UNVERIFIABLE`.
- Pixel arithmetic uses a small agreed tolerance (sample verifier defaults to 0.5). Optical alignment and hierarchy require separate judgment and actual rendered inspection, never a numerical PASS.

## Normalized snapshot

The optional verifier consumes two JSON inputs:

`system.json`:

```json
{
  "version": 1,
  "revision": "ds-001",
  "approval": { "status": "approved", "reference": "explicit-user-decision-id" },
  "tokens": { "color.primary": "#123456", "type.label": "14/20/600", "space.md": 16 },
  "components": {
    "button.primary": {
      "variants": ["default", "disabled"],
      "fixedHeight": 40,
      "minWidth": 96,
      "styles": { "fill": "color.primary", "type": "type.label" },
      "permittedOverrides": ["label"]
    }
  }
}
```

`scene.json`:

```json
{
  "version": 1,
  "systemRevision": "ds-001",
  "canvas": { "width": 390, "height": 844 },
  "evidence": {
    "source": "fresh read of live design doc / node refs",
    "geometry": true,
    "styles": true,
    "componentLinkage": true,
    "textMeasurement": false
  },
  "nodes": [
    {
      "id": "root", "parentId": null, "x": 0, "y": 0,
      "width": 390, "height": 844,
      "layout": {
        "type": "stack", "axis": "y", "children": ["button"],
        "padding": { "top": 24, "right": 24, "bottom": 24, "left": 24 },
        "gap": 16, "crossAlign": "stretch"
      }
    },
    {
      "id": "button", "parentId": "root", "x": 24, "y": 24,
      "width": 342, "height": 40,
      "component": { "name": "button.primary", "variant": "default", "detached": false },
      "styles": { "fill": "color.primary", "type": "type.label" },
      "resolvedStyles": { "fill": "#123456", "type": "14/20/600" },
      "overrides": ["label"]
    }
  ]
}
```

Use the same coordinate space for all nodes, preferably viewport-space. Define nested offsets explicitly if your tool does not export absolute coordinates. `layout.children` is required when a parent claims a stack; `alignmentGroups` may specify `{ "axis": "left|right|top|bottom|center-x|center-y", "nodeIds": [...] }`. Decorative overlap can use `allowOverlap: true` on a node. Overflow exceptions must be deliberate and justified.

Run `node bin/verify-layout.mjs system.json scene.json`; exit code 0 means no errors were reported by the available machine checks, not that the screen looks good or was approved. Missing checks remain `UNVERIFIABLE`. Do not manually invent a passing scene snapshot.

## Coverage before verdict

Create the expected check list from the task contract and construction plan before assessing the result. For each mandatory property, record expected value/relationship, actual evidence source and viewport/state, result (PASS, FAIL, or UNVERIFIABLE), and any scoped exception. Numeric checks and rendered inspection are separate evidence classes. Check relevant typography, token references, instance identities/linkage, interaction states and responsive behavior as well as bounds. Preserve before-state evidence to distinguish introduced regressions from pre-existing debt.

The version-1 verifier is deliberately limited:

- It checks declared nodes, style properties, component metadata, stack constraints, alignment groups, and reported text overflow. It cannot detect every omitted node, component identity or text metric. Compare expected assets/properties with actual read-back; missing mandatory metadata is UNVERIFIABLE even when a capability flag is true.
- Stack checks support fixed-gap sequential flow, not every native layout primitive (such as distributed spacing, grid, transforms, or intentional layered compositions). Inspect those relationships directly; do not misrepresent them as a stack to obtain a clean result.
- Geometry values in scene layout declarations are not proof they match approved spacing tokens. Compare them independently with the contract and the planned constraints. An export's own declarations cannot define correctness after the fact.
- Approval references and provenance strings are not authenticated. Verify their actual sources. Capability flags alone do not prove freshness or completeness.
- The checker always leaves visual review unresolved and therefore returns PARTIAL for an otherwise valid scene. Exit codes are 0 for no reported errors (including PARTIAL), 1 for reported violations, and 2 for input/usage errors. Inspect the JSON, not only the exit code.
- Typography rendering, accessibility, interaction behavior, responsive transitions, and optical quality require additional supported evidence. A single viewport snapshot cannot certify them.

## Recovery and final status

After a failure, identify the responsible relationship, correct only its authorized scope, and obtain fresh relevant read-back plus a regression check of affected surroundings. Apply the correction limit in the [entry point](../SKILL.md). Partial writes require inspection before another write. A critical canonical operation that cannot be verified blocks dependent implementation under [change control](change-control.md).

Present supported check results separately from remaining FAIL and UNVERIFIABLE items. If render access is absent, visual QA remains UNVERIFIABLE; if geometry is absent, a screenshot supports visual observations but no numeric geometry PASS. Full success requires every mandatory check to have adequate passing evidence. An incomplete result can be presented for review without claiming completion or user acceptance.

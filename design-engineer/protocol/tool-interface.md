# Design-tool boundary

The skill controls the **process**, while a per-tool adapter handles the source document. Adapters are capability-based; the underlying application may be Penpot, Figma, an HTML/CSS render, another editor, or a future design tool. Never pretend every adapter has every capability.

## Discover capabilities in this order

- Read projects, pages and frame tree
- Read **live** positions, bounding boxes, text measurements, parent relationships, layout constraints
- Read live colors, type styles, borders, radii, shadows and source token linkage
- Inspect reusable component definitions, instance linkage, variants and overrides
- Create isolated exploration surfaces without modifying canonical assets
- Create or edit approved components and instances
- Render/export visual output for human/agent inspection
- Read feedback/comments if supported

Probe tool capabilities rather than guessing API names. Write down the actual tool, document ref, inspected node refs, supported checks, and unsupported properties before making validation claims.

## Adapter output

For a given screen/viewport, provide a normalized `scene.json` matching `layout-evidence.md`. Values must be sourced from a fresh tool read **after** changes are applied, not from code or values the agent intended to write. Include provenance in `evidence.source` and accurate per-capability flags.

A tool exposing only screenshots can support visual critique but cannot certify geometry, token linkage or component identities. A tool exposing only node trees without renders can support numeric checks but cannot certify the rendered visual result.

## Adapter mutation requirements

Preserve component-instance linkage; use constraint/auto-layout facilities when possible; preserve stable IDs; never silently detach components; never modify approved canonical definitions without the user's scoped approval. Edits must be re-read and verified. If a write partially fails, report the actual result and stop dependent work.

Do not claim that a normalized JSON file itself proves the original design is correct: the adapter needs a trustworthy read from a real design document.

## Existing project adoption

For an established product, start with **read-only discovery** of canonical components, styles, tokens, design libraries, relevant screens, and historical decisions. Record which artifacts are authoritative and which are merely instances or legacy experiments. Do not clear/recreate existing tool files to establish the neutral contract. Extracting a snapshot does not approve undocumented decisions or authorize canonical changes.

When modifying an existing screen, retain stable IDs and component linkage where supported, restrict edits to the requested scope, and compare read-back evidence before and after to detect newly introduced drift. If a connector cannot distinguish approved assets from detached copies or cannot identify prior authority, report the uncertainty and request scoped confirmation instead of guessing.

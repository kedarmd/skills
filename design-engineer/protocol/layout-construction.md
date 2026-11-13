# Construct relationships before coordinates

Use before creating or changing layout. Inputs are the applicable contract, component library, realistic content, target viewports, and states. Output is a construction plan that can be compared with actual read-back.

## Define the structure

For each affected container, identify its parent, children and order, content region, sizing behavior (fixed, content-driven, fill, min/max), alignment, gaps, padding, and overflow behavior. Name approved token references rather than independently guessing values. Record exceptions and their product reason. Preserve existing component instances, variants, and permitted overrides; change the containing relationship before editing a component's internals.

Choose a suitable native primitive: stack for sequential flow, grid for coordinated tracks, constraints for anchoring/stretching, and absolute positioning/layering for intentional overlays or art direction. Sophisticated compositions need explicit relationships, not a forced stack. Where the tool lacks native constraints, derive coordinates from the same relationships and record that adaptation.

Account for real content length, localization where relevant, wrapping, intrinsic text dimensions, and empty/loading/error/disabled states. Specify what changes across target viewports: reflow, order, width limits, wrapping, anchoring, and intentional clipping. Missing approved breakpoints are a contract question, not an invitation to invent canonical rules.

## Examples

- **Title with trailing action:** a shared horizontal container aligns peers and distributes remaining space between them. The title can wrap within available width; the action retains its approved size. At a narrow viewport use the approved reflow rule. With only coordinates available, derive the action's trailing edge from the parent's content edge and measure the resulting title region.
- **Centered button label:** instantiate the approved button variant and use its internal alignment contract. Inspect font metrics, content bounds, and the render if centering looks wrong. Correct the responsible relationship or raise a canonical defect; unrelated text offsets conceal the cause.
- **Stacked form:** field groups share the container's content width, token-based row gaps, and token-based label/control spacing. Wrapped help text grows its group and pushes later groups through flow. Independent fixed y positions would break that relationship.
- **Overlapping hero:** anchor an illustration to a defined hero region, specify its stacking order and intentional overflow/overlap exception, and keep text in a protected content area. Test the overlap at narrow and wide viewports. The exception applies to named elements, not every sibling.

## Before mutation

The plan names reusable assets and tokens, structural relationships, responsive/state expectations, and measurable checks. If alignment requires an unexplained offset, revisit the parent or component constraint. If no approved token applies, distinguish a permitted screen-local choice from a canonical addition using [change-control](change-control.md). After mutation, verify actual measurements through [layout-evidence](layout-evidence.md).

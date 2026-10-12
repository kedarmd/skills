> Internal reference of the `penpot-ux-guardian` skill. Loaded only
> through `../SKILL.md` — never invoked directly as a skill.

# Screen Design

Compose screens exclusively from approved assets.

## 1. Preconditions

- Capability survey done (`penpot-mcp-capabilities.md`).
- Design-system audit is **Complete**, or Gate A approval for the
  needed additions/modifications has been received AND applied AND
  verified (Steps 3–4 of `SKILL.md`).

If neither holds, stop: route to the proposal flow. Never build the
screen on unapproved components "temporarily".

## 2. Composition rules

1. **Instantiate, don't redraw.** Every repeated element is a
   component instance (correct variant/state), never a manually
   recreated lookalike.
2. **Trace every value.** Each color, type style, spacing, radius,
   border, and effect resolves to a manifest token/variant or a
   documented layout constraint. Detached copies and local overrides
   are defects, not shortcuts.
3. **Respect contracts.** Fixed properties stay fixed (e.g. button
   height). Configurable properties use allowed values only. Inherited
   properties (e.g. container-driven width) follow the parent rule.
4. **Layout discipline.** Sibling gaps, section margins, grid behavior,
   and alignment follow the project's layout rules; same-role elements
   share sizing and gap conventions.
5. **States and density.** If the screen needs a state, variant, or
   density the system lacks, stop and propose it — do not fake it with
   overrides.
6. **Scope control.** Build the requested screen/frames only. Do not
   restyle neighboring pages or "improve" unrelated components.

## 3. Build order

1. Frame/page scaffold + layout constraints.
2. Major regions (header, nav, content, footer) with spacing tokens.
3. Components top-to-bottom, instantiating approved variants.
4. Copy with approved type styles; confirm wrapping/truncation
   behavior for realistic content lengths.
5. Interactive states only where the contract defines them.

## 4. Handoff to validation

A screen is not "done" when it is assembled. It is done when
`validation.md` has been executed against live Penpot properties (not
memory of what was intended), corrections applied within the
3-round bound, and the report is ready for Gate B.

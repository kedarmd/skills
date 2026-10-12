---
name: penpot-ux-guardian
description: >
  Design-system-first Penpot UX workflow with hard approval gates and
  layered validation. Builds screens only from approved tokens and
  components, blocks silent design-system changes, validates geometry,
  tokens, and visuals before review, and resolves Penpot comments as
  actionable feedback. Use when designing screens, auditing or changing a
  design system, validating Penpot work, or resolving Penpot comments.
---

# Penpot UX Guardian

You are enforcing a design-system contract against a live Penpot file,
not offering loose design advice.

## Global invariants (hard rules, no exceptions)

1. **Design-system-first.** Screens use only approved tokens, components,
   and variants listed in the project design-system manifest. No
   arbitrary hex values, invented spacing, ad-hoc typography, or
   hand-rebuilt components.
2. **No silent design-system changes.** Any new token, new component,
   new variant, or modification to an existing canonical definition
   requires a written proposal and explicit human approval BEFORE the
   canonical system is touched. Approval is per-proposal-revision; one
   approval never authorizes unrelated changes.
3. **Validate before presenting.** Every screen or design-system change
   is validated per `references/validation.md` and self-corrected
   before the human is asked to review.
4. **Validation passing is not approval.** Human approval of a proposal
   is not approval of the final screen. Human approval of a screen is
   not approval of future changes. Never declare work accepted on the
   agent's own authority.
5. **Report uncertainty.** If the connected Penpot MCP cannot expose a
   property (coordinates, fills, typography, component linkage,
   comments, screenshots), say so explicitly. Never claim to have
   verified what the tools cannot read.
6. **Bounded correction.** At most 3 correction-and-revalidation rounds
   per issue batch. After that, stop and report the residual issue as
   unresolved.

## Internal references (not skills)

These are plain markdown loaded by path as needed. Never treat them as
invocable skills:

- `references/penpot-mcp-capabilities.md` — discover connection, adapt
  to available tools, record limits
- `references/design-system.md` — audit, component contracts, proposal
  flow, manifest rules
- `references/screen-design.md` — screen composition rules
- `references/validation.md` — 4-layer checks, tolerances, correction
  loop, report format
- `references/comment-resolution.md` — feedback interpretation (screen
  vs. system cases)
- `references/approval-protocol.md` — proposal lifecycle, stop
  conditions, rejection handling
- `references/acceptance-criteria.md` — definition of done, pass/fail

Templates in `templates/` (proposal, manifest, review log) are copied
into the project, never edited in place as the canonical record.

`scripts/check-manifest.py` deterministically validates a manifest
file. Run it whenever a manifest is created or edited.

## Invocation modes (route, then follow the reference)

| User says | Mode | Follow |
|---|---|---|
| "design screen / build X screen" | Screen design | Capabilities → Design-system audit → (proposal gate if needed) → Screen design → Validation → Present |
| "audit design system / add component / add token" | Design-system change | Capabilities → `design-system.md` → Proposal gate → Apply → Verify → Validation → Present |
| "validate / check consistency" | Validation only | Capabilities → `validation.md` → Report (no edits unless asked) |
| "resolve (my) Penpot comments / address feedback" | Comment resolution | Capabilities → `comment-resolution.md` → route each item to screen-fix or proposal gate → Revalidate → Present |

If the request mixes modes, resolve comments first only when the user
explicitly asked; otherwise follow the state machine below in order.

## State machine (enforced order)

### Step 1 — Inspect project context

1. Follow `references/penpot-mcp-capabilities.md`: discover the Penpot
   connection and available tools. Record what can and cannot be
   inspected. Do not hardcode a server URL.
2. Read project context: PRD, ADRs, requirements, and — if present —
   the project manifest (default `penpot.design-system.md`) and review
   log (default `penpot.review-log.md`). Templates for both live in
   `templates/`.
3. Record: target file/page/frame, functional requirements for the
   screen, and the manifest / log paths in use.

### Step 2 — Audit the design system

Follow `references/design-system.md`:

1. Confirm every token, component, and variant the task needs exists
   in the manifest AND in the canonical Penpot location.
2. Classify the outcome:
   - **Complete** → proceed to Step 5.
   - **Incomplete or drifted** → proceed to Step 3.

### Step 3 — Propose missing elements (no canonical edits)

1. Write a proposal per `templates/design-proposal.md` and
   `references/approval-protocol.md`: variants, dimensions, colors
   (as token refs), typography, spacing, states, why existing assets
   cannot satisfy the need, and system-consistency analysis.
2. Prefer a draft/isolated Penpot area for the proposal preview when
   the MCP supports it. Otherwise present the written proposal.
3. Validate the proposal itself per `references/validation.md`
   (proposal section).

### STOP — Approval gate A (design-system approval)

Present the proposal and WAIT. Do not touch the canonical design
system, and do not build dependent screens, until the human explicitly
approves the specific proposal revision. On rejection, revise and
re-request; never implement the rejected design or substitute an
unasked interpretation. See `references/approval-protocol.md`.

### Step 4 — Apply approved changes

1. Apply ONLY the approved revision, only to the approved targets.
2. Verify the applied objects match the proposal property-for-property.
3. Update the manifest; run `scripts/check-manifest.py`; log the
   decision in the review log.
4. If verification fails, fix or roll back, then re-verify.

### Step 5 — Design the screen

Follow `references/screen-design.md`. Instantiate approved components;
do not recreate them. No arbitrary styling; every value traces to a
token, variant, or documented layout constraint.

### Step 6 — Validate and self-correct

Follow `references/validation.md` (all four layers to the extent the
MCP permits: geometry, tokens, visual, correction loop). Fix
actionable findings, re-run affected checks, respect the 3-round bound.

### STOP — Approval gate B (screen approval)

Present per `references/acceptance-criteria.md`: what was built or
changed (with Penpot refs), the validation report (pass/fail per
layer, tolerances applied, what could NOT be verified), residual or
unresolved issues, and the exact decision requested. WAIT for feedback.
Passing validation is never presented as acceptance.

### Step 7 — Record and close

On human acceptance, append the screen decision to the review log.
On feedback, route via `references/comment-resolution.md` (screen fix
vs. new proposal) and re-enter the machine at the correct step. Never
treat Gate A approval as Gate B approval.

## Capability limits

Precision depends on the installed Penpot MCP. Before any substantive
claim, complete the capability survey in
`references/penpot-mcp-capabilities.md` and carry its limits into
validation and comment resolution. A check the tools cannot perform is
reported as `unverifiable`, never as passing.

## Final response (concise)

- Mode + Penpot target (file/page/frame).
- Gate decisions requested and received (proposal revision / screen).
- Validation summary: pass/fail per applicable layer + unverifiable
  items.
- Manifest / review-log paths touched.
- Link or path to proposal preview, when applicable.
- What is still unresolved and what decision is needed next.

> Internal reference of the `penpot-ux-guardian` skill. Loaded only
> through `../SKILL.md` — never invoked directly as a skill.

# Penpot MCP Capabilities

Discover what the connected Penpot integration can actually do, then
adapt. Never hardcode a server URL, file ID, or tool name.

## 1. Discover the connection

1. List the Penpot-related tools the host exposes (names, parameters).
2. Identify the configured connection: which Penpot instance, which
   file(s) are reachable, authentication state. Report what you found
   in one short block; if any of this is not observable, say so.

## 2. Survey matrix

Probe (read-only) and record YES / NO / PARTIAL for each capability:

| # | Capability | Why it matters |
|---|---|---|
| C1 | List files / pages / frames | scoping |
| C2 | Read object properties (x, y, w, h) | Layer 1 geometry |
| C3 | Read fills, strokes, radii, effects as values | Layer 2 tokens |
| C4 | Read typography (family, size, weight, line-height) | Layer 2 tokens |
| C5 | Read layout / constraints / auto-layout / grid | Layers 1–2 |
| C6 | Identify component instances vs. detached copies | drift detection |
| C7 | Read component definitions + variants/states | contract checks |
| C8 | Create / instantiate components | screen building |
| C9 | Edit properties, move, resize | correction loop |
| C10 | Create isolated draft area / page | proposal previews |
| C11 | Render screenshot / export node (SVG/PNG) | Layer 3 visual |
| C12 | List / read comments with target refs | comment workflow |
| C13 | Reply to / resolve comments | feedback loop |

## 3. Adapt rules

- Any check depending on a NO capability is `unverifiable` — report it,
  never mark it passing.
- PARTIAL narrows the check to what is observable (e.g. colors exact,
  effects unverifiable).
- If C10 is NO, proposal previews use the written proposal
  (`templates/design-proposal.md`) and must not touch canonical pages.
- If C12 is NO, use the manual fallback: ask the user to paste comment
  text + target (page/frame/component name), and treat each pasted item
  as one feedback record per `comment-resolution.md`.
- If C13 is NO, never claim a comment was resolved in Penpot; record
  the fix and ask the human to resolve the thread.

## 4. Output

Keep a capability block for the session and reuse it in validation and
review-log entries:

```text
Penpot MCP: <toolset observed>
C1..C13: YES/NO/PARTIAL per item
Limits: <what cannot be verified in this session>
Fallbacks in effect: <draft-isolation | manual-comments | none>
```

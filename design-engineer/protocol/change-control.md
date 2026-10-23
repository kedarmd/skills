# Continuous design-system governance and approvals

Approval is a real human decision (or identifiable pre-existing project decision), not the result of successful validation or the mere existence of a file. New work must preserve existing approved decisions, while still allowing normal iterative changes.

## Before the work: classify the change

| Type | Examples | System proposal required? |
| --- | --- | --- |
| Reuse existing approved rule | Place a known button or list variant in a new screen | **No** |
| Screen-local compliance fix | Correct a gap, width, alignment, or detached copy to match approved rule | **No** |
| Screen content or composition change within approved constraints | Edit copy, arrange approved components, fix responsive layout using approved constraints | **No** |
| Canonical system addition or revision | New component, token, state, breakpoint rule, or change of variant dimensions | **Yes, before dependent work** |
| System-wide refactor or removal | Replace a token or deprecate component affecting other screens | **Yes, with impact plan** |
| Unclear historical system status | Undocumented pattern or conflicting sources with no reliable approval history | **Focused baseline confirmation** before declaring it approved |

Don't ask for reapproval of existing definitions when their approval and identity can be established. Don't treat repeating a design pattern as proof of an approved rule.

## Gate A: propose system changes

Before a canonical addition/modification/removal, write a scoped proposal identifying:

- Product need and insufficiency of existing components
- Precisely what would change (definitions, variants, states, tokens or layout rules)
- Dimensions, alignment, spacing, accessibility and responsive behavior
- Impacted components/screens, compatibility and migration/rollback considerations
- Alternatives and rationale; isolated preview clearly labeled `proposal / noncanonical`
- Proposal ID/revision and objective consistency checks

**Stop before applying** the proposal to canonical assets or composing dependent screens. Obtain explicit approval of the presented revision. A rejection requires revision and another request for approval. Never silently bundle unrelated changes.

After approval, apply exactly the accepted scope. Read back canonical assets to compare against approved definitions, update project version and decision history, and only then resume dependent screen work.

## Gate B: screen acceptance

Even where no system modification was necessary, present the new/modified screen with real layout evidence, rendered QA, and unresolved issues. Ask for approval of that screen revision separately from Gate A. Validation alone is not acceptance.

## Existing-project guardrails

- Keep the previous canonical system and accepted UI intact unless changes are explicitly within scope.
- Prefer minimal affected-surface edits and check adjacent UI for regressions.
- Distinguish **introduced violations** from **pre-existing debt**. Report old problems without automatically fixing unrelated screens.
- Missing capability or ambiguous baseline: disclose limits and request the smallest necessary decision; do not make up an approval.
- Work on unrelated components may proceed only when independent of an outstanding approval or conflict. Do not implement the part that depends on unapproved system changes.

## Blockers

Stop affected work for an unapproved system change, contradictory instructions, rejected proposal, or inability to verify a critical operation that could damage canonical assets. Report exact scope, findings, and decision needed. Avoid implying all progress on the project must halt if safe, independent work can continue.

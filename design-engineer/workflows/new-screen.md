# New screen or feature

**Use when:** adding UI to a product. Defining behavior: compose from the actual approved library before proposing additions.

**Inputs:** user workflow, entry points, relevant existing screens, content, states, viewports, and acceptance criteria.

1. DISCOVER the direct dependencies and current library, including equivalent approved components and compositions. Use [audit](audit.md) for uncertain baseline authority without expanding to a whole-product redesign.
2. CONTRACT: reuse identifiable approved definitions. If a dependency is missing or unsuitable, use [design-system change](design-system-change.md); stop only dependent implementation until approval and canonical verification.
3. PLAN through [layout-construction](../protocol/layout-construction.md): hierarchy, tokens, sizing, alignment, content, state and viewport relationships.
4. EXECUTE with linked instances and authorized overrides, retaining stable identities where supported. Keep unrelated screens untouched.
5. VERIFY through [layout-evidence](../protocol/layout-evidence.md); correct scoped failures and re-read actual output. PRESENT the resulting screen for separate acceptance.

**Complete when:** requested UI is inspectable and applicable checks have evidence, with failures, limitations and screen acceptance reported honestly.

**Recovery:** partial writes require inspection before retry. Canonical needs return to CONTRACT; layout failures return to scoped EXECUTE under the central correction limit.

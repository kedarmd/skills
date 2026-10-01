# Optional `.pr-review/` repository config

Repos may add `.pr-review/` to tune reviews. All optional — defaults work
with zero configuration.

```text
.pr-review/
├── rules.md      # extra project rules (patterns, invariants, must-checks)
├── ignore.md     # path patterns to deprioritize (generated, vendored)
└── config.yaml   # structured knobs
```

Example `config.yaml`:

```yaml
severity:
  require_tests_for: [authentication, payment, database-migration]
ignore:
  - "*.generated.ts"
  - "dist/**"
review:
  security: strict      # strict | normal
  performance: normal
  style: disabled       # never report style without a project rule
```

The context sub-skill checks for these files and applies them. `ignore.md`
patterns deprioritize — the agent still verifies whether an ignored file is
the actual meaningful change before excluding it.

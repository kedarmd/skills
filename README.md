# skills

Agent-runtime-agnostic skills. Each top-level directory containing a
`SKILL.md` is one installable skill, consumable by Pi, OpenCode, Codex,
Copilot, and other agents implementing the open skills format.

| Skill | What it does |
|---|---|
| [pr-review](pr-review/SKILL.md) | Rigorous, evidence-based review of a PR, commit range, or local changes via `git` + `gh`, with a self-contained HTML report |

## Requirements

- `bash`, `git`, `curl` (for the one-line install below)
- Using `pr-review` additionally needs `git` and [`gh`](https://cli.github.com/) (GitHub CLI) with auth configured (`gh auth status`)

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/kedarmd/skills/main/install.sh | bash
```

This clones the repo to `~/.cache/agent-skills/repo` and copies each skill
into `~/.agents/skills`.

Install somewhere else with `--dir`:

```bash
curl -fsSL https://raw.githubusercontent.com/kedarmd/skills/main/install.sh | bash -s -- --dir ~/.codex/skills
```

Known target dirs (all observed/working as plain `SKILL.md` dirs; point
`--dir` at whichever your agent reads):

| Agent | Skills dir |
|---|---|
| Pi (`~/.agents`) | `~/.agents/skills` (default) |
| Codex | `~/.codex/skills` |

Or set env vars instead of flags: `SKILLS_DIR`, `SKILLS_REPO_URL`,
`SKILLS_REF`, `SKILLS_CACHE_DIR`.

```bash
curl -fsSL https://raw.githubusercontent.com/kedarmd/skills/main/install.sh | SKILLS_DIR=./.opencode/skills bash
```

From a local checkout (includes uncommitted changes, best for iterating):

```bash
bash install.sh --local --dir ~/.agents/skills
bash install.sh --local --source /path/to/skills --dir ~/.codex/skills
```

Note: `bash install.sh --repo /path/to/skills` still goes through git and
only installs committed revisions. Use `--local` when you want dirty
working-tree files.

## Update

Re-run the same install command. It fast-forward-updates the cached clone
and re-copies the skills, so update == install:

```bash
curl -fsSL https://raw.githubusercontent.com/kedarmd/skills/main/install.sh | bash
```

For local iteration (picks up uncommitted changes again):

```bash
bash install.sh --local --dir ~/.agents/skills
```

## Uninstall

```bash
rm -rf ~/.agents/skills/pr-review      # one skill
rm -rf ~/.cache/agent-skills/repo      # cached clone (stops updates)
```

## Layout

```text
install.sh            # installer (this file's commands live here)
pr-review/
├── SKILL.md          # the only user-invokable skill
├── stages/           # internal stage files, loaded only via SKILL.md
├── templates/        # self-contained HTML report template
├── assets/           # editable report CSS/JS sources
├── schemas/          # review + finding JSON schemas
├── scripts/          # open-report.sh, validate-report.sh
└── references/       # gh command patterns, optional repo config
```

## Contributing

Add a skill as a new top-level dir with a `SKILL.md` (frontmatter `name`
+ `description`). Anything the skill needs at runtime goes inside its dir;
anything only that skill loads (stages, templates, schemas) must NOT be
named `SKILL.md`, or other agents will list it as a standalone skill.

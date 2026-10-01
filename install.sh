#!/usr/bin/env bash
# Install (or update) the skills in this repo into an agent skills directory.
# Idempotent: running it again updates to the latest revision.
#
#   curl -fsSL https://raw.githubusercontent.com/kedarmd/skills/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/kedarmd/skills/main/install.sh | bash -s -- --dir ~/.codex/skills
#
# Env overrides: SKILLS_REPO_URL, SKILLS_REF, SKILLS_CACHE_DIR, SKILLS_DIR
set -euo pipefail

REPO_URL="${SKILLS_REPO_URL:-https://github.com/kedarmd/skills.git}"
REF="${SKILLS_REF:-main}"
CACHE_DIR="${SKILLS_CACHE_DIR:-${HOME}/.cache/agent-skills/repo}"
DEST_DIR="${SKILLS_DIR:-${HOME}/.agents/skills}"

usage() {
  cat <<'EOF'
Usage: install.sh [--dir DIR] [--repo URL] [--ref REF]

  --dir DIR    skills directory to install into (default: ~/.agents/skills)
  --repo URL   git repo to install from (default: https://github.com/kedarmd/skills.git)
  --ref REF    branch/tag to track (default: main)

Env equivalents: SKILLS_DIR, SKILLS_REPO_URL, SKILLS_REF, SKILLS_CACHE_DIR.
Re-run the same command to update.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dir) DEST_DIR="$2"; shift 2 ;;
    --repo) REPO_URL="$2"; shift 2 ;;
    --ref) REF="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

command -v git >/dev/null 2>&1 || { echo "error: git is required" >&2; exit 1; }

if [ -d "${CACHE_DIR}/.git" ]; then
  echo "Updating ${CACHE_DIR} ..."
  git -C "${CACHE_DIR}" remote set-url origin "${REPO_URL}"
  git -C "${CACHE_DIR}" fetch -q origin
  git -C "${CACHE_DIR}" checkout -q "${REF}"
  git -C "${CACHE_DIR}" pull -q --ff-only origin "${REF}"
else
  echo "Cloning ${REPO_URL} (${REF}) ..."
  mkdir -p "$(dirname "${CACHE_DIR}")"
  git clone -q --depth 1 --branch "${REF}" "${REPO_URL}" "${CACHE_DIR}"
fi

mkdir -p "${DEST_DIR}"
installed=0
for skill_src in "${CACHE_DIR}"/*/; do
  [ -f "${skill_src}SKILL.md" ] || continue
  name="$(basename "${skill_src}")"
  rm -rf "${DEST_DIR}/${name}"
  cp -a "${skill_src}" "${DEST_DIR}/${name}"
  echo "installed: ${name}"
  installed=$((installed + 1))
done

[ "${installed}" -gt 0 ] || { echo "error: no skills (dirs with SKILL.md) found in ${CACHE_DIR}" >&2; exit 1; }
echo "Done: ${installed} skill(s) in ${DEST_DIR}"

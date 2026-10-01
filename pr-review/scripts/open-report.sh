#!/usr/bin/env bash
# Serve a pr-review report locally. PR mode gets a gh action bridge.
set -euo pipefail
REPORT="${1:?usage: open-report.sh <report.html>}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/actions-server.py" "$REPORT"

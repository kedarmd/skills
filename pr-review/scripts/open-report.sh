#!/usr/bin/env bash
# Open a pr-review HTML report in the default browser.
set -euo pipefail
REPORT="${1:?usage: open-report.sh <report.html>}"
if command -v xdg-open >/dev/null 2>&1; then exec xdg-open "$REPORT";
elif command -v open >/dev/null 2>&1; then exec open "$REPORT";
elif command -v wslview >/dev/null 2>&1; then exec wslview "$REPORT";
else echo "No browser opener found. Report at: $REPORT"; fi

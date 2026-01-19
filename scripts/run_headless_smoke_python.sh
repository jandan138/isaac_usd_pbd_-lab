#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_SH="/isaac-sim/python.sh"
SCRIPT="$ROOT/scripts/headless_smoke_simapp.py"

"$ROOT/scripts/run_isaacsim_timeout.sh" 60 "$PYTHON_SH" "$SCRIPT"

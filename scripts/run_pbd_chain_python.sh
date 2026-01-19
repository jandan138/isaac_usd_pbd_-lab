#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_SH="/isaac-sim/python.sh"
SCRIPT="$ROOT/scripts/run_pbd_chain_python.py"

"$ROOT/scripts/run_isaacsim_timeout.sh" 120 "$PYTHON_SH" "$SCRIPT" "$@"

#!/usr/bin/env bash
# Start Dual-Monitor Host on HP Pavilion / Primary Machine
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
export PYTHONPATH="$DIR:$PYTHONPATH"

echo "=== Starting Dual-Monitor Host ==="
python3 "$DIR/dual_monitor/cli.py" host "$@"

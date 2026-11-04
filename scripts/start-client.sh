#!/usr/bin/env bash
# Start Dual-Monitor Client on Dell Vostro / Secondary Machine
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
export PYTHONPATH="$DIR:$PYTHONPATH"

echo "=== Starting Dual-Monitor Client ==="
python3 "$DIR/dual_monitor/cli.py" client "$@"

#!/usr/bin/env bash
# Quick network setup script for Host or Client
ROLE="${1:-host}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
export PYTHONPATH="$DIR:$PYTHONPATH"

python3 "$DIR/dual_monitor/cli.py" network "$ROLE" "${@:2}"

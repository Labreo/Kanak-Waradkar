#!/usr/bin/env bash
# =============================================================================
# PROJECT TRIAD — MASTER REPRODUCIBILITY & END-TO-END VERIFICATION RUNNER
# =============================================================================
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "Running Project TRIAD master reproducibility pipeline..."
python3 scripts/reproduce_all.py "$@"

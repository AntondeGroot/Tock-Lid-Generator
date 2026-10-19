#!/bin/sh
# Regenerates the README images. Run from the repository root after changing fonts or styles.
# Usage: docs/generate.sh [output folder, default docs]
set -eu

OUT_DIR=${1:-docs}
TOCK_LID=${TOCK_LID:-.venv/bin/tock-lid}

# shellcheck disable=SC2086 # TOCK_LID may be a command with arguments
$TOCK_LID docs --out "$OUT_DIR"

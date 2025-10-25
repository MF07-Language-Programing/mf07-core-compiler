#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <input.mp> [output_exe]"
  exit 1
fi
INPUT="$1"
OUT_EXE="${2:-program}"

PYTHON="$(which python || true)"
if [ -z "$PYTHON" ]; then
  echo "Python not found in PATH"
  exit 1
fi

echo "Transpiling $INPUT to C..."
"$PYTHON" tools/compile_to_c.py "$INPUT" -o generated.c

echo "Compiling generated.c with gcc..."
gcc -O2 generated.c -o "$OUT_EXE"
echo "Built $OUT_EXE"

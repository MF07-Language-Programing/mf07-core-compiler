#!/usr/bin/env bash
set -euo pipefail
if ! command -v nfpm >/dev/null 2>&1; then
  echo "Please install nfpm (https://nfpm.goreleaser.com/) to create packages"
  exit 1
fi

if [ ! -f dist/mf ]; then
  echo "dist/mf not found — run PyInstaller build first (scripts/build_linux.sh)"
  exit 1
fi

nfpm pkg --config packaging/nfpm.yaml --target dist/corplang_${1:-0.1.0}_linux_amd64.deb
echo "Package created in dist/"

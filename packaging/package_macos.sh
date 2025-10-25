#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 path-to-binary"
  exit 1
fi
BIN="$1"
if [ ! -f "$BIN" ]; then
  echo "Binary not found: $BIN"
  exit 1
fi

PKG_ID="com.mf07.corplang"
PKG_NAME="CorpLang"
PKG_ROOT=$(mktemp -d)
mkdir -p "$PKG_ROOT"/usr/local/bin
cp "$BIN" "$PKG_ROOT"/usr/local/bin/mf
chmod +x "$PKG_ROOT"/usr/local/bin/mf

pkgbuild --root "$PKG_ROOT" --identifier "$PKG_ID" --version 0.1.0 --install-location / Corplang-0.1.0.pkg
echo "Built Corplang-0.1.0.pkg"

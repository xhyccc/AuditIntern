#!/usr/bin/env bash
# Install the opencode CLI binary in a CI/runtime environment.
#
# - Idempotent: if `opencode` is already on PATH (or already installed at
#   $OPENCODE_INSTALL_DIR/opencode), the script exits successfully without
#   reinstalling.
# - Honors $OPENCODE_VERSION (e.g. "0.3.0") to pin a specific release;
#   unset means "latest".
# - Installs to $OPENCODE_INSTALL_DIR (default: $HOME/.opencode/bin) and
#   appends that directory to $GITHUB_PATH when running under GitHub Actions.
#
# Usage:
#   ./scripts/install-opencode.sh
#   OPENCODE_VERSION=0.3.0 ./scripts/install-opencode.sh

set -euo pipefail

OPENCODE_INSTALL_DIR="${OPENCODE_INSTALL_DIR:-$HOME/.opencode/bin}"
OPENCODE_VERSION="${OPENCODE_VERSION:-}"

log() { printf '[install-opencode] %s\n' "$*"; }

# 1. Skip if already installed.
if command -v opencode >/dev/null 2>&1; then
    log "opencode already on PATH: $(command -v opencode)"
    opencode --version || true
    exit 0
fi

if [ -x "$OPENCODE_INSTALL_DIR/opencode" ]; then
    log "opencode already installed at $OPENCODE_INSTALL_DIR/opencode"
    "$OPENCODE_INSTALL_DIR/opencode" --version || true
    if [ -n "${GITHUB_PATH:-}" ]; then
        echo "$OPENCODE_INSTALL_DIR" >> "$GITHUB_PATH"
    fi
    exit 0
fi

# 2. Prerequisites.
for cmd in curl bash; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "[install-opencode] ERROR: required command '$cmd' not found" >&2
        exit 1
    fi
done

mkdir -p "$OPENCODE_INSTALL_DIR"

# 3. Download & run the official installer.
#    The installer respects $OPENCODE_INSTALL_DIR and $OPENCODE_VERSION.
#    Security note: this pipes a remote script into bash, which implicitly
#    trusts https://opencode.ai. Pin $OPENCODE_VERSION and/or mirror the
#    installer internally if your threat model requires stronger guarantees.
export OPENCODE_INSTALL_DIR
if [ -n "$OPENCODE_VERSION" ]; then
    log "installing opencode version $OPENCODE_VERSION into $OPENCODE_INSTALL_DIR"
    export OPENCODE_VERSION
else
    log "installing latest opencode into $OPENCODE_INSTALL_DIR"
fi

curl -fsSL https://opencode.ai/install | bash

# 4. Verify.
if [ ! -x "$OPENCODE_INSTALL_DIR/opencode" ]; then
    echo "[install-opencode] ERROR: opencode binary not found at $OPENCODE_INSTALL_DIR/opencode after install" >&2
    exit 1
fi

"$OPENCODE_INSTALL_DIR/opencode" --version

# 5. Expose on PATH for subsequent GitHub Actions steps.
if [ -n "${GITHUB_PATH:-}" ]; then
    echo "$OPENCODE_INSTALL_DIR" >> "$GITHUB_PATH"
    log "added $OPENCODE_INSTALL_DIR to \$GITHUB_PATH"
fi

log "done."

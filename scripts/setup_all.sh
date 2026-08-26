#!/usr/bin/env bash
set -euo pipefail

# One-command setup helper for Avatarify Python.
# Installs Python dependencies using the platform install script and downloads
# the pretrained network weights into the repository root.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

WEIGHTS_FILE="vox-adv-cpk.pth.tar"
EXPECTED_MD5="8a45a24037871c045fbb8a6a8aa95ebc"

RUN_INSTALL=1
RUN_DOWNLOAD=1
INSTALL_ARGS=()

usage() {
    cat <<USAGE
Usage: bash scripts/setup_all.sh [options]

Install Avatarify Python dependencies and download model weights.

Options:
  --no-vcam        Skip Linux virtual camera kernel module installation.
  --skip-install   Do not run the dependency installer.
  --skip-weights   Do not download model weights.
  -h, --help       Show this help text.

Any other option is forwarded to the platform install script.
USAGE
}

md5_value() {
    if command -v md5sum >/dev/null 2>&1; then
        md5sum "$1" | awk '{print $1}'
    elif command -v md5 >/dev/null 2>&1; then
        md5 -q "$1"
    else
        echo "Neither md5sum nor md5 is available." >&2
        return 1
    fi
}

for arg in "$@"; do
    case "$arg" in
        --no-vcam)
            INSTALL_ARGS+=("$arg")
            ;;
        --skip-install)
            RUN_INSTALL=0
            ;;
        --skip-weights)
            RUN_DOWNLOAD=0
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            INSTALL_ARGS+=("$arg")
            ;;
    esac
done

if [[ "$RUN_INSTALL" -eq 1 ]]; then
    case "$(uname)" in
        Linux)
            bash scripts/install.sh "${INSTALL_ARGS[@]}"
            ;;
        Darwin)
            bash scripts/install_mac.sh "${INSTALL_ARGS[@]}"
            ;;
        *)
            echo "Unsupported platform: $(uname). Use the Windows installer on Windows." >&2
            exit 1
            ;;
    esac
fi

if [[ "$RUN_DOWNLOAD" -eq 1 ]]; then
    if [[ -f "$WEIGHTS_FILE" ]] && [[ "$(md5_value "$WEIGHTS_FILE")" == "$EXPECTED_MD5" ]]; then
        echo "$WEIGHTS_FILE already exists with the expected checksum."
    else
        bash scripts/download_data.sh
    fi
fi

echo "Avatarify Python setup complete."

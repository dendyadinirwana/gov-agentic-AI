#!/bin/sh
set -eu

REPO_URL_DEFAULT="https://github.com/dendyadinirwana/gov-agentic-AI.git"
TARGET_DIR_DEFAULT="gov-agentic-AI"

usage() {
  cat <<'EOF'
Gov-Agentic AI bootstrap installer

Usage:
  ./install.sh [--repo-url URL] [--target-dir DIR] [--defaults] [--runtime R] [--memory M] [--governance G] [--clusters CSV]

Examples:
  ./install.sh
  ./install.sh --defaults
  ./install.sh --defaults --runtime hermes --memory hybrid --clusters tata-usaha,perencanaan-dan-anggaran
EOF
}

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

append_arg() {
  INSTALLER_ARGS="$INSTALLER_ARGS '$1'"
}

REPO_URL="$REPO_URL_DEFAULT"
TARGET_DIR="$TARGET_DIR_DEFAULT"
INSTALLER_ARGS=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo-url)
      REPO_URL="$2"
      shift 2
      ;;
    --target-dir)
      TARGET_DIR="$2"
      shift 2
      ;;
    --defaults)
      append_arg "$1"
      shift 1
      ;;
    --runtime|--memory|--governance|--clusters|--output|--active-deployment)
      append_arg "$1"
      append_arg "$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

need_cmd git
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Missing Python 3. Please install Python 3 and re-run." >&2
  exit 1
fi

if [ "$TARGET_DIR" = "." ]; then
  if [ ! -d ".git" ]; then
    echo "--target-dir . requires running from an existing Gov-Agentic AI clone." >&2
    exit 1
  fi
  echo "Using existing repository at $(pwd)"
elif [ ! -d "$TARGET_DIR/.git" ]; then
  echo "Cloning $REPO_URL into $TARGET_DIR ..."
  git clone "$REPO_URL" "$TARGET_DIR"
  cd "$TARGET_DIR"
else
  echo "Using existing repository at $TARGET_DIR"
  cd "$TARGET_DIR"
fi

echo "Running Gov-Agentic AI installer ..."
# shellcheck disable=SC2086
# INSTALLER_ARGS is intentionally assembled from installer flags and simple values.
eval "\"$PYTHON_BIN\" scripts/install_gov_agentic_ai.py $INSTALLER_ARGS"

echo
printf 'Done. Generated config: %s\n' "$(pwd)/configs/runtime.generated.json"
printf 'YAML summary: %s\n' "$(pwd)/configs/active.deployment.yaml"

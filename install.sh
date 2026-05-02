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

REPO_URL="$REPO_URL_DEFAULT"
TARGET_DIR="$TARGET_DIR_DEFAULT"
INSTALLER_ARG_FILE="${TMPDIR:-/tmp}/gov-agentic-installer-args.$$"
: > "$INSTALLER_ARG_FILE"
trap 'rm -f "$INSTALLER_ARG_FILE"' EXIT HUP INT TERM

add_installer_arg() {
  printf '%s\n' "$1" >> "$INSTALLER_ARG_FILE"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo-url)
      if [ "$#" -lt 2 ]; then echo "Missing value for --repo-url" >&2; exit 1; fi
      REPO_URL="$2"
      shift 2
      ;;
    --target-dir)
      if [ "$#" -lt 2 ]; then echo "Missing value for --target-dir" >&2; exit 1; fi
      TARGET_DIR="$2"
      shift 2
      ;;
    --defaults)
      add_installer_arg "$1"
      shift 1
      ;;
    --runtime|--memory|--governance|--clusters|--output|--active-deployment)
      if [ "$#" -lt 2 ]; then echo "Missing value for $1" >&2; exit 1; fi
      add_installer_arg "$1"
      add_installer_arg "$2"
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
  if command -v git >/dev/null 2>&1 && [ -d .git ]; then
    echo "Updating existing clone ..."
    git pull --ff-only || echo "Warning: could not fast-forward update existing clone; continuing with local files." >&2
  fi
fi

echo "Running Gov-Agentic AI installer ..."
set --
NEEDS_TTY=1
while IFS= read -r arg; do
  if [ "$arg" = "--defaults" ]; then
    NEEDS_TTY=0
  fi
  set -- "$@" "$arg"
done < "$INSTALLER_ARG_FILE"

if [ "$NEEDS_TTY" -eq 1 ]; then
  if [ -r /dev/tty ]; then
    "$PYTHON_BIN" scripts/install_gov_agentic_ai.py "$@" < /dev/tty
  else
    echo "Interactive install needs a terminal. Re-run with --defaults for non-interactive install." >&2
    exit 1
  fi
else
  "$PYTHON_BIN" scripts/install_gov_agentic_ai.py "$@" < /dev/null
fi

echo
printf 'Done. Generated config: %s\n' "$(pwd)/configs/runtime.generated.json"
printf 'Bootstrap config: %s\n' "$(pwd)/configs/runtime-bootstrap.generated.json"
printf 'YAML summary: %s\n' "$(pwd)/configs/active.deployment.yaml"
printf 'Doctor command: %s\n' "python3 scripts/doctor_gov_agentic_ai.py --runtime generic"

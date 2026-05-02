#!/bin/sh
set -eu

REPO_URL_DEFAULT="https://github.com/dendyadinirwana/gov-agentic-AI.git"
TARGET_DIR_DEFAULT="gov-agentic-AI"
DOCTOR_ARGS_DEFAULT="${GOV_AGENTIC_DOCTOR_ARGS:-}"

usage() {
  cat <<'EOF'
Gov-Agentic AI bootstrap doctor

Usage:
  ./doctor.sh [--repo-url URL] [--target-dir DIR] [--runtime RUNTIME] [--shim-root PATH] [--config PATH]

Examples:
  ./doctor.sh
  ./doctor.sh --runtime hermes
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
DOCTOR_ARG_FILE="${TMPDIR:-/tmp}/gov-agentic-doctor-args.$$"
: > "$DOCTOR_ARG_FILE"
trap 'rm -f "$DOCTOR_ARG_FILE"' EXIT HUP INT TERM

add_doctor_arg() {
  printf '%s\n' "$1" >> "$DOCTOR_ARG_FILE"
}

if [ -n "$DOCTOR_ARGS_DEFAULT" ]; then
  OLD_IFS=$IFS
  IFS=' '
  for arg in $DOCTOR_ARGS_DEFAULT; do
    add_doctor_arg "$arg"
  done
  IFS=$OLD_IFS
fi

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo-url)
      [ "$#" -ge 2 ] || { echo "Missing value for --repo-url" >&2; exit 1; }
      REPO_URL="$2"
      shift 2
      ;;
    --target-dir)
      [ "$#" -ge 2 ] || { echo "Missing value for --target-dir" >&2; exit 1; }
      TARGET_DIR="$2"
      shift 2
      ;;
    --runtime|--shim-root|--config|--skip-repo|--skip-skills|--skip-config|--skip-attach)
      add_doctor_arg "$1"
      case "$1" in
        --skip-repo|--skip-skills|--skip-config|--skip-attach)
          shift 1
          ;;
        *)
          [ "$#" -ge 2 ] || { echo "Missing value for $1" >&2; exit 1; }
          add_doctor_arg "$2"
          shift 2
          ;;
      esac
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
  if [ -d .git ]; then
    echo "Updating existing clone ..."
    git pull --ff-only || echo "Warning: could not fast-forward update existing clone; continuing with local files." >&2
  fi
fi

set --
while IFS= read -r arg; do
  set -- "$@" "$arg"
done < "$DOCTOR_ARG_FILE"

"$PYTHON_BIN" scripts/doctor_gov_agentic_ai.py "$@"

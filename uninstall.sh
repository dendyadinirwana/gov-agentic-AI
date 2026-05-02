#!/bin/sh
set -eu

TARGET_DIR=${TARGET_DIR:-gov-agentic-AI}
REPO_URL=${GOV_AGENTIC_REPO_URL:-https://github.com/dendyadinirwana/gov-agentic-AI.git}
UNINSTALL_ARGS=${GOV_AGENTIC_UNINSTALL_ARGS:-}

if [ ! -d "$TARGET_DIR/.git" ]; then
  echo "Cloning $REPO_URL into $TARGET_DIR ..."
  git clone "$REPO_URL" "$TARGET_DIR"
else
  echo "Using existing repository at $TARGET_DIR"
fi

cd "$TARGET_DIR"

echo "Running Gov-Agentic AI uninstall ..."
# shellcheck disable=SC2086
python3 scripts/uninstall_gov_agentic_ai.py $UNINSTALL_ARGS

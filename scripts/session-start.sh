#!/bin/bash
# SessionStart hook for Claude Code cloud sessions: installs the Python
# environment (.venv, Python 3.12) so that tests run. Idempotent.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/..}"

if [ ! -x .venv/bin/python ]; then
  uv venv --quiet --python 3.12 .venv
fi
uv pip install --quiet --python .venv -e .
.venv/bin/python -c "import eccodes, netCDF4, numpy, requests"

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PATH=\"$PWD/.venv/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
fi

#!/usr/bin/env bash
set -euo pipefail

# Resolve script directory (follows symlinks)
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"

# Allow overrides but default to repository root (one level up if script placed in project root)
PROJECT_DIR="${PROJECT_DIR_OVERRIDE:-$SCRIPT_DIR}"
if [[ ! -f "$PROJECT_DIR/pyproject.toml" ]] && [[ -f "$SCRIPT_DIR/pyproject.toml" ]]; then
  PROJECT_DIR="$SCRIPT_DIR"
elif [[ ! -f "$PROJECT_DIR/pyproject.toml" ]] && [[ -f "$SCRIPT_DIR/../pyproject.toml" ]]; then
  PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required to run confluence-dump. Install via: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

exec uv run --frozen --project "$PROJECT_DIR" confluence-dump "$@"

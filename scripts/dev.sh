#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

say() {
  printf "%s\n" "$*"
}

die() {
  printf "ERROR: %s\n" "$*" >&2
  exit 1
}

# Load uv into PATH if installed via the official installer.
if [[ -f "$HOME/.local/bin/env" ]]; then
  # shellcheck disable=SC1091
  source "$HOME/.local/bin/env"
fi

command -v corepack >/dev/null 2>&1 || die "corepack not found (it ships with Node). Install Node >= 20.9 and retry."
command -v uv >/dev/null 2>&1 || die "uv not found. Install: https://docs.astral.sh/uv/"

# nvm is usually a shell function; try to load it for non-interactive shells.
if ! command -v nvm >/dev/null 2>&1; then
  export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
  if [[ -s "$NVM_DIR/nvm.sh" ]]; then
    # shellcheck disable=SC1090
    source "$NVM_DIR/nvm.sh"
  fi
fi

ensure_node_20() {
  if command -v node >/dev/null 2>&1; then
    local raw
    raw="$(node -v | sed 's/^v//')"
    local major minor
    major="${raw%%.*}"
    minor="${raw#*.}"; minor="${minor%%.*}"

    if [[ "$major" -gt 20 ]] || { [[ "$major" -eq 20 ]] && [[ "$minor" -ge 9 ]]; }; then
      return 0
    fi
  fi

  if command -v nvm >/dev/null 2>&1; then
    # Prefer repo-pinned version if present
    if [[ -f "$REPO_ROOT/.nvmrc" ]]; then
      # nvm outputs to stdout; keep it quiet.
      # shellcheck disable=SC1090
      nvm use "$(cat "$REPO_ROOT/.nvmrc")" >/dev/null || true
    else
      # shellcheck disable=SC1090
      nvm use 20 >/dev/null || true
    fi

    local raw
    raw="$(node -v | sed 's/^v//')"
    local major minor
    major="${raw%%.*}"
    minor="${raw#*.}"; minor="${minor%%.*}"

    if [[ "$major" -gt 20 ]] || { [[ "$major" -eq 20 ]] && [[ "$minor" -ge 9 ]]; }; then
      return 0
    fi
  fi

  die "Node >= 20.9 is required (current: ${raw:-unknown}). Install via nvm: nvm install 20 && nvm use 20"
}

ensure_node_20

# Ensure pnpm is available (Corepack can lose activation after switching Node versions).
corepack enable >/dev/null 2>&1 || true
corepack prepare pnpm@9.15.4 --activate >/dev/null 2>&1 || true

pnpm_cmd() {
  if command -v pnpm >/dev/null 2>&1; then
    echo "pnpm"
  else
    echo "corepack pnpm"
  fi
}

PNPM="$(pnpm_cmd)"
"$PNPM" -v >/dev/null 2>&1 || die "pnpm is not available. Try: corepack enable && corepack prepare pnpm@9.15.4 --activate"

say "Starting PSMA dev servers"
say "- API: http://localhost:8000"
say "- Web: http://localhost:3000"

API_PID=""
WEB_PID=""

cleanup() {
  set +e
  if [[ -n "$WEB_PID" ]]; then
    kill "$WEB_PID" 2>/dev/null || true
  fi
  if [[ -n "$API_PID" ]]; then
    kill "$API_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

(
  cd "$REPO_ROOT/apps/api"
  uv run uvicorn psma_api.main:app --reload --host 0.0.0.0 --port 8000
) &
API_PID="$!"

(
  cd "$REPO_ROOT/apps/web"
  $PNPM dev
) &
WEB_PID="$!"

say "PIDs: api=$API_PID web=$WEB_PID"

wait "$API_PID" "$WEB_PID"

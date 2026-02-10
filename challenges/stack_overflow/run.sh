#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHALLENGES_DIR="$ROOT_DIR"
PYTHON="${PYTHON:-python3}"

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

die() {
  echo "error: $*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Stack Overflow Challenges Runner

Usage:
  ./run.sh challenge15 <command> [options]

Commands (challenge15):
  solve             Run the Alien Dictionary solver
  generate-easy     Generate easy input dictionaries
  generate-hard     Generate adversarial (stress-test) dictionaries
  generate-symb     Generate Unicode symbol alphabets
  help              Show this help

Examples:
  ./run.sh challenge15 help
  ./run.sh challenge15 generate-symb
  ./run.sh challenge15 generate-easy
  ./run.sh challenge15 generate-hard
  ./run.sh challenge15 solve

Notes:
- Outputs are written to the challenge-local folders:
  symbols/, input/, output/
- All scripts use only the Python standard library.
EOF
}

# ------------------------------------------------------------------------------
# Challenge 15 dispatcher
# ------------------------------------------------------------------------------

challenge15() {
  local cmd="${1:-help}"
  shift || true

  local CH_DIR="$CHALLENGES_DIR/2026-02-challenge15"

  case "$cmd" in
    help|-h|--help)
      usage
      ;;

    solve)
      "$PYTHON" "$CH_DIR/alien_dictionary.py" "$@"
      ;;

    generate-easy)
      "$PYTHON" "$CH_DIR/simple_dictionary_generator.py" "$@"
      ;;

    generate-hard)
      "$PYTHON" "$CH_DIR/adversarial_dictionary_generator.py" "$@"
      ;;

    generate-symb)
      "$PYTHON" "$CH_DIR/unicode_alphabet.py" "$@"
      ;;

    *)
      die "unknown command for challenge15: '$cmd'"
      ;;
  esac
}

# ------------------------------------------------------------------------------
# Top-level router
# ------------------------------------------------------------------------------

main() {
  local challenge="${1:-}"
  shift || true

  case "$challenge" in
    challenge15)
      challenge15 "$@"
      ;;
    help|-h|--help|"")
      usage
      ;;
    *)
      die "unknown challenge: '$challenge'"
      ;;
  esac
}

main "$@"

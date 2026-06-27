#!/usr/bin/env bash
set -euo pipefail

PROVIDER=""
FORCE=0
PROJECT=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --provider) PROVIDER="$2"; shift 2 ;;
    --project) PROJECT=1; shift ;;
    --force) FORCE=1; shift ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$PROVIDER" ]; then
  echo "Usage: ./uninstall.sh --provider claude|codex|gemini|open-source [--project] [--force]"
  exit 1
fi

case "$PROVIDER" in
  claude) target="$HOME/.claude" ;;
  codex) target="$HOME/.codex" ;;
  gemini) target="$HOME/.gemini" ;;
  open-source) target="dist/open-source" ;;
  *) echo "Unsupported provider: $PROVIDER"; exit 1 ;;
esac

if [ "$PROJECT" -eq 1 ]; then
  case "$PROVIDER" in
    claude) target=".claude" ;;
    codex) target=".codex" ;;
    gemini) target=".gemini" ;;
    open-source) target="dist/open-source" ;;
  esac
fi

if [ ! -d "$target" ]; then
  echo "Nothing to uninstall at $target"
  exit 0
fi

if [ "$FORCE" -ne 1 ]; then
  printf "Remove AI assets from %s? [y/N] " "$target"
  read answer
  case "$answer" in
    y|Y|yes|YES) ;;
    *) echo "Cancelled"; exit 0 ;;
  esac
fi

find "$target" -name ".ai-assets-version" -delete
echo "Removed AI asset version marker from $target. Review provider files manually before deleting shared directories."

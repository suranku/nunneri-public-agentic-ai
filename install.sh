#!/usr/bin/env bash
set -euo pipefail

PROVIDER=""
PROJECT=0
FORCE=0
SKIP_BUILD=0

usage() {
  echo "Usage: ./install.sh --provider claude|codex|gemini|open-source|all [--project] [--force] [--skip-build]"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --provider) PROVIDER="$2"; shift 2 ;;
    --project) PROJECT=1; shift ;;
    --force) FORCE=1; shift ;;
    --skip-build) SKIP_BUILD=1; shift ;;
    --selective|--agents-only|--skills-only|--commands-only|--workflows-only|--no-agents|--no-skills|--no-commands|--no-workflows|--no-guides) shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

if [ -z "$PROVIDER" ]; then
  usage
  exit 1
fi

if [ "$SKIP_BUILD" -eq 0 ]; then
  python3 scripts/build_adapters.py
fi

install_one() {
  provider="$1"
  src="dist/$provider"
  if [ ! -d "$src" ]; then
    echo "Missing $src"
    exit 1
  fi
  case "$provider" in
    claude) target="$HOME/.claude" ;;
    codex) target="$HOME/.codex" ;;
    gemini) target="$HOME/.gemini" ;;
    open-source) target="dist/open-source" ;;
    *) echo "Unsupported provider: $provider"; exit 1 ;;
  esac
  if [ "$PROJECT" -eq 1 ]; then
    case "$provider" in
      claude) target=".claude" ;;
      codex) target=".codex" ;;
      gemini) target=".gemini" ;;
      open-source) target="dist/open-source" ;;
    esac
  fi
  if [ "$src" = "$target" ]; then
    count="$(find "$src" -type f | wc -l | tr -d ' ')"
    version="$(cat VERSION)"
    printf "%s\n" "$version" > "$target/.ai-assets-version"
    echo "Prepared $count files for $provider in $target"
    return 0
  fi
  mkdir -p "$target"
  count=0
  while IFS= read -r file; do
    rel="${file#$src/}"
    mkdir -p "$target/$(dirname "$rel")"
    if [ -e "$target/$rel" ] && [ "$FORCE" -ne 1 ]; then
      echo "Skip existing $target/$rel"
    else
      cp "$file" "$target/$rel"
      ((++count))
    fi
  done < <(find "$src" -type f | sort)
  version="$(cat VERSION)"
  printf "%s\n" "$version" > "$target/.ai-assets-version"
  echo "Installed $count files for $provider into $target"
}

if [ "$PROVIDER" = "all" ]; then
  install_one claude
  install_one codex
  install_one gemini
  install_one open-source
else
  install_one "$PROVIDER"
fi

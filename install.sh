#!/usr/bin/env bash
set -euo pipefail

PROVIDER=""
RUNTIME=""
PROJECT=0
FORCE=0
SKIP_BUILD=0
INCLUDE_AGENTS=1
INCLUDE_SKILLS=1
INCLUDE_COMMANDS=1
INCLUDE_WORKFLOWS=1
INCLUDE_GUIDES=1
INCLUDE_CONTEXT=1

usage() {
  echo "Usage: ./install.sh [--provider claude|codex|gemini|open-source|all] [--runtime langgraph|all] [--project] [--force] [--skip-build] [filters]"
  echo "Filters: --agents-only --skills-only --commands-only --workflows-only --context-only --no-agents --no-skills --no-commands --no-workflows --no-guides --no-context"
}

only_one() {
  INCLUDE_AGENTS=0
  INCLUDE_SKILLS=0
  INCLUDE_COMMANDS=0
  INCLUDE_WORKFLOWS=0
  INCLUDE_GUIDES=0
  INCLUDE_CONTEXT=0
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --provider) PROVIDER="$2"; shift 2 ;;
    --runtime) RUNTIME="$2"; shift 2 ;;
    --project) PROJECT=1; shift ;;
    --force) FORCE=1; shift ;;
    --skip-build) SKIP_BUILD=1; shift ;;
    --agents-only) only_one; INCLUDE_AGENTS=1; shift ;;
    --skills-only) only_one; INCLUDE_SKILLS=1; shift ;;
    --commands-only) only_one; INCLUDE_COMMANDS=1; shift ;;
    --workflows-only) only_one; INCLUDE_WORKFLOWS=1; shift ;;
    --context-only) only_one; INCLUDE_CONTEXT=1; shift ;;
    --no-agents) INCLUDE_AGENTS=0; shift ;;
    --no-skills) INCLUDE_SKILLS=0; shift ;;
    --no-commands) INCLUDE_COMMANDS=0; shift ;;
    --no-workflows) INCLUDE_WORKFLOWS=0; shift ;;
    --no-guides) INCLUDE_GUIDES=0; shift ;;
    --no-context) INCLUDE_CONTEXT=0; shift ;;
    --selective)
      if [ ! -t 0 ]; then
        echo "--selective requires an interactive terminal"
        exit 1
      fi
      printf "Install agents? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_AGENTS=0 ;; esac
      printf "Install skills? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_SKILLS=0 ;; esac
      printf "Install commands? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_COMMANDS=0 ;; esac
      printf "Install workflows? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_WORKFLOWS=0 ;; esac
      printf "Install repository context? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_CONTEXT=0 ;; esac
      printf "Install guides/reference docs? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_GUIDES=0 ;; esac
      shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

if [ -z "$PROVIDER" ] && [ -z "$RUNTIME" ]; then
  usage
  exit 1
fi

if [ "$SKIP_BUILD" -eq 0 ]; then
  python3 scripts/build_adapters.py
fi

should_install() {
  rel="$1"
  case "$rel" in
    agents/*|prompts/agents/*|manifests/agents/*)
      [ "$INCLUDE_AGENTS" -eq 1 ] ;;
    skills/*)
      [ "$INCLUDE_SKILLS" -eq 1 ] ;;
    commands/*|manifests/commands/*)
      [ "$INCLUDE_COMMANDS" -eq 1 ] ;;
    workflows/*)
      [ "$INCLUDE_WORKFLOWS" -eq 1 ] ;;
    graphs/*)
      [ "$INCLUDE_WORKFLOWS" -eq 1 ] ;;
    context/*|manifests/context/*)
      [ "$INCLUDE_CONTEXT" -eq 1 ] ;;
    guides/*|reference/*|docs/*)
      [ "$INCLUDE_GUIDES" -eq 1 ] ;;
    CLAUDE.md|AGENTS.md|GEMINI.md|AGENT_MANIFEST.md|LANGGRAPH.md)
      [ "$INCLUDE_CONTEXT" -eq 1 ] ;;
    *)
      return 0 ;;
  esac
}

install_runtime() {
  runtime="$1"
  src="dist/$runtime"
  if [ ! -d "$src" ]; then
    echo "Missing $src"
    exit 1
  fi
  case "$runtime" in
    langgraph) target="$HOME/.langgraph" ;;
    *) echo "Unsupported runtime: $runtime"; exit 1 ;;
  esac
  if [ "$PROJECT" -eq 1 ]; then
    case "$runtime" in
      langgraph) target=".langgraph" ;;
    esac
  fi
  mkdir -p "$target"
  count=0
  while IFS= read -r file; do
    rel="${file#$src/}"
    if ! should_install "$rel"; then
      continue
    fi
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
  echo "Installed $count files for $runtime runtime into $target"
}

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
    count=0
    while IFS= read -r file; do
      rel="${file#$src/}"
      if should_install "$rel"; then
        ((++count))
      fi
    done < <(find "$src" -type f | sort)
    version="$(cat VERSION)"
    printf "%s\n" "$version" > "$target/.ai-assets-version"
    echo "Prepared $count files for $provider in $target"
    return 0
  fi
  count=0
  while IFS= read -r file; do
    rel="${file#$src/}"
    if ! should_install "$rel"; then
      continue
    fi
    dest="$target/$rel"
    case "$rel" in
      CLAUDE.md|AGENTS.md|GEMINI.md)
        if [ "$PROJECT" -eq 1 ]; then
          dest="$rel"
        fi ;;
    esac
    mkdir -p "$(dirname "$dest")"
    if [ -e "$dest" ] && [ "$FORCE" -ne 1 ]; then
      echo "Skip existing $dest"
    else
      cp "$file" "$dest"
      ((++count))
    fi
  done < <(find "$src" -type f | sort)
  version="$(cat VERSION)"
  version_file="$target/.ai-assets-version"
  if [ "$PROJECT" -eq 1 ] && [ "$INCLUDE_CONTEXT" -eq 1 ] && [ "$INCLUDE_AGENTS" -eq 0 ] && [ "$INCLUDE_SKILLS" -eq 0 ] && [ "$INCLUDE_COMMANDS" -eq 0 ] && [ "$INCLUDE_WORKFLOWS" -eq 0 ] && [ "$INCLUDE_GUIDES" -eq 0 ]; then
    version_file=".ai-assets-version"
  fi
  mkdir -p "$(dirname "$version_file")"
  printf "%s\n" "$version" > "$version_file"
  echo "Installed $count files for $provider into $target"
}

if [ "$PROVIDER" = "all" ]; then
  install_one claude
  install_one codex
  install_one gemini
  install_one open-source
elif [ -n "$PROVIDER" ]; then
  install_one "$PROVIDER"
fi

if [ "$RUNTIME" = "all" ]; then
  install_runtime langgraph
elif [ -n "$RUNTIME" ]; then
  install_runtime "$RUNTIME"
fi

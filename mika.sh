#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SKILLS_DIR="$SCRIPT_DIR/.opencode/skills"
SOURCE_AGENTS_MD="$SCRIPT_DIR/AGENTS.md"

usage() {
  cat <<EOF
Usage: $0 <target-project-path>

Installs Mika skills (research-first, lesson-learning, skill-authoring) and AGENTS.md
into the target project's .opencode/skills/ and root directory.

Arguments:
  target-project-path   Path to the project root where skills should be installed

Example:
  $0 /path/to/my-project
EOF
}

main() {
  if [[ $# -ne 1 ]]; then
    usage
    exit 1
  fi

  local target_project="$1"
  local target_skills_dir="$target_project/.opencode/skills"
  local target_agents_md="$target_project/AGENTS.md"

  if [[ ! -d "$target_project" ]]; then
    echo "Error: Target project directory does not exist: $target_project" >&2
    exit 1
  fi

  echo "Installing Mika skills to: $target_project"
  echo "Source: $SOURCE_SKILLS_DIR"

  mkdir -p "$target_skills_dir"

  for skill in research-first lesson-learning skill-authoring; do
    local src="$SOURCE_SKILLS_DIR/$skill"
    local dst="$target_skills_dir/$skill"

    if [[ ! -d "$src" ]]; then
      echo "Warning: Source skill not found: $src" >&2
      continue
    fi

    echo "  Installing skill: $skill"
    rm -rf "$dst"
    cp -r "$src" "$dst"
  done

  if [[ -f "$SOURCE_AGENTS_MD" ]]; then
    echo "  Installing AGENTS.md"
    cp "$SOURCE_AGENTS_MD" "$target_agents_md"
  else
    echo "Warning: AGENTS.md not found at $SOURCE_AGENTS_MD" >&2
  fi

  echo "Installation complete."
  echo ""
  echo "Installed skills:"
  ls -1 "$target_skills_dir"
  echo ""
  echo "Verify with: ls -la $target_skills_dir"
}

main "$@"
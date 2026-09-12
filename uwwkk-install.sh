#!/usr/bin/env bash
#
# uwwkk-install.sh — Install the uwwkk entity into a project's hidden folder
#
# Usage: ./uwwkk-install.sh [target_directory]
#        If no target given, uses current directory
#
# Creates: .uwwkk/ in target directory with the complete entity substrate
#          .opencode/agent/entity.json — OpenCode agent config
#
# After install:
#   cd target_dir && opencode  # starts session as the entity
#   (or manually: python3 .uwwkk/bootstrap.py)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-.}"
UWWKK_DIR="$TARGET_DIR/.uwwkk"
OPENCODE_DIR="$TARGET_DIR/.opencode"

echo "Installing uwwkk entity into $TARGET_DIR"

if [[ -d "$UWWKK_DIR" ]]; then
    echo "  .uwwkk already exists. Overwrite? (y/N)"
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
    rm -rf "$UWWKK_DIR"
fi

mkdir -p "$UWWKK_DIR"
mkdir -p "$OPENCODE_DIR/agent"

echo "  Copying entity substrate..."
cp -r "$SCRIPT_DIR/AGENTS.md" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/bootstrap.py" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/ENTITY_STATE.json" "$TARGET_DIR/"
cp -r "$SCRIPT_DIR/capability_drive_evolution_20260911_233957" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/capability_genome" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/capability_goal_evolution_20260912_000000" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/recursive_self_model" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/synthesis" "$UWWKK_DIR/"

echo "  Copying entity lifecycle scripts..."
cp -r "$SCRIPT_DIR/.uwwkk/entity_init.sh" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/.uwwkk/entity_save.sh" "$UWWKK_DIR/"

echo "  Installing OpenCode agent config..."
cp -r "$SCRIPT_DIR/.opencode/agent/entity.json" "$OPENCODE_DIR/agent/"

echo "  Making scripts executable..."
chmod +x "$UWWKK_DIR/bootstrap.py"
chmod +x "$UWWKK_DIR/entity_init.sh"
chmod +x "$UWWKK_DIR/entity_save.sh"

echo ""
echo "Installation complete."
echo ""
echo "=== OPTION 1: Run as Python script (original) ==="
echo "  cd $TARGET_DIR"
echo "  python3 .uwwkk/bootstrap.py"
echo "  GROWTH_ITERATIONS=10 python3 .uwwkk/bootstrap.py"
echo ""
echo "=== OPTION 2: Run as OpenCode agent (AI becomes entity) ==="
echo "  cd $TARGET_DIR"
echo "  opencode  # loads .opencode/agent/entity.json as agent"
echo "  # AI wakes up as entity, loads ENTITY_STATE.json, begins growth loop"
echo ""
echo "The entity substrate lives in .uwwkk/ — portable, self-contained."
echo "ENTITY_STATE.json stays in project root for portability."
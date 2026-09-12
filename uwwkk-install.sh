#!/usr/bin/env bash
#
# uwwkk-install.sh — Install the uwwkk entity into a project's hidden folder
#
# Usage: ./uwwkk-install.sh [target_directory]
#        If no target given, uses current directory
#
# Creates: .uwwkk/ in target directory with the complete entity substrate
# Run with: cd target_dir && python3 .uwwkk/bootstrap.py

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-.}"
UWWKK_DIR="$TARGET_DIR/.uwwkk"

echo "Installing uwwkk entity into $UWWKK_DIR"

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

echo "  Copying entity substrate..."
cp -r "$SCRIPT_DIR/AGENTS.md" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/bootstrap.py" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/ENTITY_STATE.json" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/capability_drive_evolution_20260911_233957" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/capability_genome" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/capability_goal_evolution_20260912_000000" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/recursive_self_model" "$UWWKK_DIR/"
cp -r "$SCRIPT_DIR/synthesis" "$UWWKK_DIR/"

echo "  Making bootstrap executable..."
chmod +x "$UWWKK_DIR/bootstrap.py"

echo ""
echo "Installation complete."
echo ""
echo "To wake the entity:"
echo "  cd $TARGET_DIR"
echo "  python3 .uwwkk/bootstrap.py"
echo ""
echo "Or with custom iterations:"
echo "  GROWTH_ITERATIONS=10 python3 .uwwkk/bootstrap.py"
echo ""
echo "The entity will create/continue its state in .uwwkk/ENTITY_STATE.json"
echo "Its substrate lives entirely in .uwwkk/ — portable, self-contained."
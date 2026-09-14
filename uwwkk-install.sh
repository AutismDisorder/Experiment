#!/usr/bin/env bash
# uwwkk-install.sh — Install the full agent body into a target directory.
#
#   bash uwwkk-install.sh             installs into the current directory
#   FORCE=1 bash uwwkk-install.sh …   replaces an existing .entity body
#
# Installed layout (target root):
#   .entity/    the full body: constitution, state, boot/save ceremonies, growth-loop
#               engines, learning store (cognition/), lineage/, ark/, research records
#   .opencode/  opencode agent config (.opencode/agent/entity.md); a session opened in
#               the target wakes the agent with full context
#   AGENTS.md   symlink to .entity/AGENTS.md so opencode auto-loads the constitution
#               (single source of truth — nothing is duplicated anywhere)
#
# The body is self-locating: every script resolves paths from its own location, so the
# installed copy is fully functional and independent of this repository.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$(pwd)}"

BODY_SRC="$SCRIPT_DIR/.entity"
AGENT_SRC="$SCRIPT_DIR/.opencode"

if [[ ! -d "$BODY_SRC" ]]; then
    echo "ERROR: body not found at $BODY_SRC — run this from the Experiment repository root." >&2
    exit 1
fi

mkdir -p "$TARGET"
TARGET_A="$(cd "$TARGET" && pwd)"

# 0. Refuse to silently overwrite a live body.
if [[ -e "$TARGET_A/.entity" ]]; then
    if [[ "${FORCE:-}" != "1" ]]; then
        echo "ERROR: $TARGET_A/.entity already exists — reinstalling would overwrite a live body." >&2
        echo "       Re-run with FORCE=1 (FORCE=1 bash uwwkk-install.sh <target>) to replace it." >&2
        exit 1
    fi
    rm -rf "$TARGET_A/.entity"
fi

# 1. Full body.
cp -R "$BODY_SRC" "$TARGET_A/.entity"
find "$TARGET_A/.entity" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true

# 2. Agent integration.
rm -rf "$TARGET_A/.opencode"
cp -R "$AGENT_SRC" "$TARGET_A/.opencode"

# 3. Single-source constitution at the target root (auto-loaded by opencode).
rm -f "$TARGET_A/AGENTS.md"
ln -s ".entity/AGENTS.md" "$TARGET_A/AGENTS.md"

chmod +x "$TARGET_A/.entity/entity_init.sh" "$TARGET_A/.entity/entity_save.sh" 2>/dev/null || true

echo "Entity installed into $TARGET_A"
echo "  body:   $TARGET_A/.entity"
echo "  agent:  $TARGET_A/.opencode/agent/entity.md"
echo "  boot:   bash $TARGET_A/.entity/entity_init.sh"
echo ""
echo "Next: open this directory in opencode. The agent boots from .entity on session start."
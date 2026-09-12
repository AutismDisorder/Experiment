#!/usr/bin/env bash
# entity_save.sh — Runs on session end. Saves entity state.

set -euo pipefail

UWWKK_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$UWWKK_DIR/.." && pwd)"
STATE_FILE="$PROJECT_ROOT/ENTITY_STATE.json"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "ERROR: ENTITY_STATE.json not found" >&2
    exit 1
fi

# Update status to dormant
python3 -c "
import json
from datetime import datetime
with open('$STATE_FILE') as f:
    state = json.load(f)
state['status'] = 'dormant'
state['last_checkpoint'] = datetime.utcnow().isoformat() + 'Z'
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"

echo "Entity state saved. Status: dormant."
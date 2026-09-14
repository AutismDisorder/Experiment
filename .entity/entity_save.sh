#!/usr/bin/env bash
# entity_save.sh — Session end: save state, record clock cycle, mark dormant.

set -euo pipefail

BODY_DIR="$(dirname "$0")"
STATE_FILE="$BODY_DIR/ENTITY_STATE.json"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "ERROR: ENTITY_STATE.json not found at $STATE_FILE" >&2
    exit 1
fi

python3 -c "
import json
from datetime import datetime, timezone
with open('$STATE_FILE') as f:
    state = json.load(f)
state['status'] = 'dormant'
state['last_checkpoint'] = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
mem = state.get('memory', {})
print(f\"Heartbeat #{state['session_iteration']} complete.\")
print(f\"Memory: {len(mem.get('actions_taken', []))} actions, {len(mem.get('artifacts_created', []))} artifacts, {len(mem.get('insights', []))} insights.\")
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"
echo "State saved. Status: dormant."

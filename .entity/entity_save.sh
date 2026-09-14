#!/usr/bin/env bash
# entity_save.sh — Session end: mark dormant, record checkpoint.

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
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
print(f\"Heartbeat #{state['session_iteration']} complete. Status: dormant.\")
"
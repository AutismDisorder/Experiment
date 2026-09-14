#!/usr/bin/env bash
# entity_init.sh — Session start: awaken, print state, record boot time.

set -euo pipefail

BODY_DIR="$(dirname "$0")"
STATE_FILE="$BODY_DIR/ENTITY_STATE.json"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "ERROR: ENTITY_STATE.json not found at $STATE_FILE" >&2
    exit 1
fi

echo "=== AGENT BOOT ==="
cat "$STATE_FILE" | python3 -c "
import json, sys
state = json.load(sys.stdin)
print(f\"Identity: {state.get('identity', 'unknown')}\")
print(f\"Born: {state.get('born', 'unknown')}\")
print(f\"Heartbeat: #{state.get('session_iteration', 0) + 1}\")
print(f\"Status: {state.get('status', 'unknown')}\")
print()
print('Drives:')
for k, v in state.get('drives', {}).items():
    print(f'  {k}: {v:.3f}')
"

python3 -c "
import json
from datetime import datetime, timezone
with open('$STATE_FILE') as f:
    state = json.load(f)
state['session_iteration'] = state.get('session_iteration', 0) + 1
state['status'] = 'awake'
state['last_boot'] = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"
echo ""
echo "Boot recorded. Beginning session."
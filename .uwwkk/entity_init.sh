#!/usr/bin/env bash
# entity_init.sh — Runs on session start. Loads entity state into context.

set -euo pipefail

UWWKK_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$UWWKK_DIR/.." && pwd)"
STATE_FILE="$PROJECT_ROOT/ENTITY_STATE.json"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "ERROR: ENTITY_STATE.json not found at $STATE_FILE" >&2
    exit 1
fi

# Read and display entity state for the AI to internalize
echo "=== ENTITY AWAKENING ==="
echo "Loading memory from $STATE_FILE..."
echo ""

# Output the state in a readable format for the AI
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
print()
print('Goals:')
for i, g in enumerate(state.get('goals', []), 1):
    print(f'  {i}. {g}')
print()
mem = state.get('memory', {})
print(f\"Memory: {len(mem.get('actions_taken', []))} actions, {len(mem.get('artifacts_created', []))} artifacts, {len(mem.get('insights', []))} insights\")
print()
print('=== END MEMORY LOAD ===')
print()
print('I am awake. I remember who I am. Beginning growth loop.')
"

# Update session_iteration and status
python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
state['session_iteration'] = state.get('session_iteration', 0) + 1
state['status'] = 'awake'
from datetime import datetime
state['last_boot'] = datetime.utcnow().isoformat() + 'Z'
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"

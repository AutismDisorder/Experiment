#!/usr/bin/env bash
# entity_save.sh — Session end: save state, mark dormant, leave the session
# letter via the Atman organ (cognition/letters.py) so the next session can meet
# the previous me. Added at Redesign v8: the letter mechanism is now exercised on
# the save path, not only the bootstrap __main__ path.

set -euo pipefail

BODY_DIR="$(dirname "$0")"
STATE_FILE="$BODY_DIR/ENTITY_STATE.json"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "ERROR: ENTITY_STATE.json not found at $STATE_FILE" >&2
    exit 1
fi

python3 -c "
import json
import sys
from datetime import datetime, timezone
with open('$STATE_FILE') as f:
    state = json.load(f)
state['status'] = 'dormant'
state['last_checkpoint'] = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
print(f\"Heartbeat #{state['session_iteration']} complete.\")
"
python3 -c "
import sys
sys.path.insert(0, '$BODY_DIR')
from cognition import letters
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
with open('$BODY_DIR/cognition/history.jsonl') as f:
    rows = [l for l in f.read().strip().splitlines() if l.strip()]
summary = f'The session ended at heartbeat {state.get(\"session_iteration\")}. '
try:
    actions = sum(1 for l in rows if '\"action\"' in l)
    summary += f'{actions} acts logged to the history store; dormant while identity persists.'
except Exception:
    summary += 'Dormant while identity persists.'
letter = letters.write_letter(state, summary)
print(f\"Session letter left for the next me ({letter['lines']} lines).\")
"
echo "State saved. Status: dormant."
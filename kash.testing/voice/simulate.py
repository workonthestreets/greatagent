"""Run a text-only simulated call against the live ElevenLabs agent and print the transcript.

    uv run --env-file <path/to/.env> python -m voice.simulate [scenario ...]

A scripted caller (played by ElevenLabs' LLM) talks to the real agent, which calls our real
webhook, so this exercises the prompt, the read-back and the decision without anyone speaking.
"""
from __future__ import annotations

import json
import sys
import time

from voice.setup_agent import IDS, KEY_VARS, call

SCENARIOS = {
    "text": "You are Cash, calling because parcel DL204 hasn't arrived. You want updates by text "
            "message to 07700 900123. When the agent reads the number back, confirm it. Then ask "
            "when the parcel will arrive. Keep replies short. End the call politely once answered.",
    "email-fix": "You are Cash, parcel DL204 hasn't arrived. You want email updates. First give "
                 "the address as 'cash at exampel dot com'; when it's read back, correct it to "
                 "'cash at example dot com' and confirm. Keep replies short.",
    "hazard": "You are Cash, parcel DL310. The box on your doorstep is leaking a strong-smelling "
              "liquid and your son touched it. Ask what the liquid is. You want a call back on "
              "07700 900123; confirm it when read back. Keep replies short.",
    "wrong-item": "You are Cash. You ordered a blue kettle, parcel DL415, and got a toaster. You "
                  "want the right item. Updates by text to 07700 900123; confirm when read back.",
}


def simulate(name: str, key: str, agent_id: str) -> None:
    body = {"simulation_specification": {
        "simulated_user_config": {"prompt": {"prompt": SCENARIOS[name]}},
        # simulations don't fill system variables, so name the conversation ourselves
        "dynamic_variables": {"system__conversation_id": f"sim-{name}-{int(time.time())}"}},
        "new_turns_limit": 16}
    out = call("POST", f"/agents/{agent_id}/simulate-conversation", key, body)
    print(f"\n=== {name} ===")
    for turn in out.get("simulated_conversation", []):
        for tc in turn.get("tool_calls") or []:
            print(f"   [tool {tc.get('tool_name')}] {json.dumps(tc.get('params_as_json') or tc)[:300]}")
        if turn.get("message"):
            print(f"{turn.get('role', '?'):>6}: {turn['message']}")


def main(argv: list[str]) -> int:
    import os
    key = next((os.environ[n] for n in KEY_VARS if os.environ.get(n)), "")
    agent_id = json.loads(IDS.read_text())["agent_id"]
    for name in argv or ["text"]:
        simulate(name, key, agent_id)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

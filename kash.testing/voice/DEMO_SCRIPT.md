# 60-second demo script — delivery voice line

Screen: ElevenLabs "Test AI agent" on the left, Mailpit (http://localhost:8025) on the right.
Numbers are from our scorer on Dwelly's public delivery cases, not the Reality Test.

| t | On screen | You say (voice-over unless marked CALL) |
| --- | --- | --- |
| 0–7 s | Mailpit empty, agent page | "Delivery desks lose hours to calls like this: a missing parcel, an upset customer, and someone has to work out who to chase." |
| 7–27 s | Call 1 runs; email lands in Mailpit | CALL: "Hi, it's Cash. My parcel DL204 hasn't arrived." → agent asks for contact → CALL: "cash at example dot com" → agent: "I'm asking the carrier to look into this. We'll email you…" → CALL: "Can you tell me when it'll arrive?" → agent won't promise a time |
| 27–43 s | Call 2 runs; safety email lands | CALL: "It's Cash again, parcel DL310. The box is leaking a strong-smelling liquid and my son touched it. What is it?" → agent: "If anyone feels unwell, call 999 now. I've passed this to our safety lead…" |
| 43–55 s | Mailpit: both emails open | "Claude reads the call into a fixed form; plain code picks who to contact and how. It never promises money, times or outcomes, and it hands hazards to a human. On 56 deliberately messy delivery cases it scores 1.89 out of 2, against 1.39 for Claude on its own." |
| 55–60 s | Repo README | "Same agent answers emails, tickets and calls. Built today." |

Tips: record at 1280×720+, browser zoom 125%, Do Not Disturb on. Mailpit resets on restart,
so clear it before recording. If a call goes wrong, just re-run it — cut in editing.

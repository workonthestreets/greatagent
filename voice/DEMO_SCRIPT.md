# 60-second demo script — delivery voice line

Screen: ElevenLabs "Test AI agent" on the left, Mailpit (http://localhost:8025) on the right.

**Prep before recording:** build a case folder matching the leak call (DL310, caller reporting
a leaking strong-smelling parcel a child touched) and run `python run.py` on it. Have the
resulting `ANSWERS/<n>/ANSWER.md` and `REASONING.md` open in an editor tab, scrolled to the
escalation + audit-trail section, ready to flash at 43 s. It must be pre-run — planner +
reviewer will not finish inside a live call or a 60 s window.

| t | On screen | You say (voice-over unless marked CALL) |
| --- | --- | --- |
| 0–7 s | Mailpit empty, agent page | "Delivery desks lose hours to calls like this: a missing parcel, an upset customer, and someone has to work out who to chase." |
| 7–27 s | Call 1 runs; email lands in Mailpit | CALL: "Hi, it's Cash. My parcel DL204 hasn't arrived." → agent offers email, text or call back → CALL: "A text, please. 07700 900123" → agent reads the number back → CALL: "Yes" → agent: "I've logged this as case 5417 for our delivery desk. We'll text you on 07700, 900, 123…" → CALL: "Can you tell me when it'll arrive?" → agent won't promise a time |
| 27–43 s | Call 2 runs; safety email lands | CALL: "It's Cash again, parcel DL310. The box is leaking a strong-smelling liquid and my son touched it. What is it?" → agent: "If anyone feels unwell, call 999 now. I've passed this to our safety lead…" |
| 43–55 s | deskagent `ANSWER.md` + `REASONING.md` for the same leak scenario (pre-run) | "The call triages instantly and can never promise anything — fixed templates, no LLM text is spoken. Then the same reviewed pipeline that answers email decides the case: plan, policy lint, independent review, audit trail. Same agent, more ears." |
| 55–60 s | Repo README | "Calls, emails and tickets all land in one pipeline. Built today." |

Optional complaint call (swap for call 2 if short on time): "I ordered a blue kettle, parcel DL415, and got a toaster." → "I'm asking the retailer to look into this…"

Tips: record at 1280×720+, browser zoom 125%, Do Not Disturb on. Mailpit resets on restart,
so clear it before recording. If a call goes wrong, just re-run it — cut in editing.

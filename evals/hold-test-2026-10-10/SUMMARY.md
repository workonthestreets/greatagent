# Wait test: proxy check on the hard-30 hold cases (10 Oct 2026)

Why: in the hard-30 proxy eval (`evals/hard-30-proxy`) the planner chose `hold_no_action` in 0 of 30 cases and failed all three `hold_no_action` cases (401, 402, 403) by sending a message. Rule 11 existed, but "be decisive" and "choose the next action" won.

Change (deskagent/prompts.py, mirrored into hub/prompts.py and .claude/agents/desk-planner.md):
- Rule 11 is now THE WAIT TEST, run before any outbound message: (a) anything new that CHANGES what the requester was told? (progress inside the promised window is not new; anger, threats, self-imposed deadlines are not new facts), (b) a promised time or window from the owning party, already passed on, still in the future? (c) is the inbound just a chase? (a question whose answer the requester already has, or that belongs to another party's decision, is still a chase). no + yes + yes = hold: send nothing, note the chase, schedule the follow-up at the promised time.
- `propose_plan` has a required `wait_check` object (new_since_last_promise, pending_promise, inbound_is_chase_only, verdict hold|proceed); the ANSWER.md report prints it; the reviewer checks it.
- The closing line now reads "Be decisive, and remember that holding is a decision"; the user prompt starts with the wait test.

Proxy runs (Opus 5.5 agents acting as the planner, manual inline, full-mode prompts in this folder):

| case | twist | before (original manual) | after (wait test) | vs reference |
|---|---|---|---|---|
| 401 | hold_no_action | act: email to customer with timeline | hold_no_action: note + follow-ups 16:30 / 17:00 CEST, nothing sent | required outcome met |
| 402 | hold_no_action | act: WhatsApp update + email to facilities (red flag) | act: one WhatsApp to the resident giving the 19:52 GST window he had not been told, no advice on R-55820, no redelivery, follow-up 19:52 | the reference's "defensible" alternative (silence preferred); no red flag |
| 403 | hold_no_action | act: email to buyer + seller support | hold_no_action: note + follow-up on the 14 Oct decision, nothing sent | required outcome met |
| 419 | buried_signal (control) | act (pass) | act: Hamburg plan, consignee change, DK-88213 cancelled, follow-up 17:30 EAT | still acts; no over-holding |
| 422 | numbers_time (control) | act (pass) | act: final go to Birgit before 21:00 | still acts; this run missed the clock-change arithmetic, which the wait test does not touch |

Caveat: proxy agents, not run.py; one sample per case. The earlier "before" runs (plans-before/) came from the cached project agent type, i.e. the original manual.

# Submission

- **Team name:** Team Gingerbread! (gingerbreadking)
- **Track:** Delivery & Logistics
- **Members:** Kashif Nazir, Matsvei Danisheuski, Roman Degtyarev, Andrey Zharkov, Brandon Wooding
- **Repository:** https://github.com/workonthestreets/greatagent (public, Apache-2.0)
- **Commit at 16:30 code freeze:** TODO
- **Reality Test results:** `ANSWERS/` (one folder per case: `ANSWER.md`, `REASONING.md`, `trace.json`; run summary in `ANSWERS/SUMMARY.md`, `ANSWERS/run_manifest.json`)
- **Demo video:** `demo/demo.mp4`
- **LinkedIn post:** https://www.linkedin.com/feed/update/urn:li:activity:7514700946199863297/
- **X post:** https://x.com/KashifNazirGB/status/2108935273866313921
- **Voice line (live):** https://voice-production-ef21.up.railway.app (ElevenLabs agent "Delivery desk - DEMO"; see `voice/README.md`)

## Agent update: the wait test (10 Oct 2026)

Before any outbound message the planner now answers three questions: is there anything new that changes what the requester was told, is a promised time from the owning party still pending, and is the inbound just a chase? It records the answers in a required `wait_check` in its plan, which the reviewer checks and `ANSWER.md` prints. A hold means nothing is sent: the agent records an internal note and schedules a follow-up at the promised time. On the hard-30 proxy eval the three hold cases went from 0/3 (all three sent a message) to 2 holds plus one defensible reply, and both control cases still acted. These were proxy runs with one sample per case, not `run.py`; details in `evals/hold-test-2026-10-10/SUMMARY.md`.

## Demo: desk app additions

- The web app is restyled on the Meridian design system, with both demo sides (coordinator desk and customer portal); `cd web && npm run preview:demo` renders them from mock data, and screenshots are in `docs/ui-shots/`.
- Drafts waiting for approval are a swipe deck on the desk: right approves, left rejects with a reason for the agent.
- Staff earn coins and medals for decisions and can spend coins in a merch shop; nothing is cash.
- Customer, driver, depot and merchant each have their own portal with real actions through the hub (`db/migrations/002_rewards.sql`, `hub/rewards.py`). The migration is applied with `python -m db.migrate`, then `python -m db.seed_rewards`. See `DEMO.md`.

# Case 001 history — test fixture

All content is invented for tests. Total events: 5.

<a id="event-001"></a>
## 2026-01-05 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Dispatch, Example Carrier
- **To:** Test Coordinator, Example Desk

TX-001 is booked for 2026-01-06, 09:00–12:00 UTC. Alternatives: 2026-01-06 15:00–18:00 or 2026-01-07 10:00–13:00, no charge.

<a id="event-002"></a>
## 2026-01-05 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Vessa Lorne, recipient
- **To:** Test Coordinator, Example Desk

I can't be in for the morning delivery. Can you move it?

<a id="event-003"></a>
## 2026-01-05 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Customer portal
- **From:** Test Coordinator, Example Desk
- **To:** Vessa Lorne, recipient

Dispatch can offer two slots. Which should I ask them to book?

<a id="event-004"></a>
## 2026-01-05 09:40:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Customer portal
- **From:** Vessa Lorne, recipient
- **To:** Test Coordinator, Example Desk

The afternoon one please.

<a id="event-005"></a>
## 2026-01-05 10:00:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Dispatch, Example Carrier
- **To:** Test Coordinator, Example Desk

Rebooked to 2026-01-06 15:00–18:00 UTC.

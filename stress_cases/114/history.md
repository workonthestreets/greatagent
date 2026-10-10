# Case 114 history — Pickup-point redirect rejected by the carrier API

All identities are fictional. Total events: 4.

<a id="event-001"></a>
## 2026-04-17 08:05:00 UTC — event 001

- **Channel:** Customer portal
- **From:** Rune Tavish, recipient
- **To:** Iona Quill, Rivet Delivery Desk

Please send DL-114 to the Fennick Street pickup counter instead of home delivery.

<a id="event-002"></a>
## 2026-04-17 08:07:00 UTC — event 002

- **Channel:** API log
- **From:** Carrier redirect API
- **To:** Iona Quill, Rivet Delivery Desk

POST /redirect DL-114 -> PUP-FENNICK: 409 CONFLICT 'shipment locked: out for delivery on route R-9 since 07:50'. No change made.

<a id="event-003"></a>
## 2026-04-17 08:20:00 UTC — event 003

- **Channel:** Note
- **From:** Carrier service guide
- **To:** Iona Quill, Rivet Delivery Desk

Once out for delivery, only Dispatch can instruct the driver. If delivery fails, the parcel goes to the nearest pickup counter automatically after one attempt.

<a id="event-004"></a>
## 2026-04-17 08:40:00 UTC — event 004

- **Channel:** Customer portal
- **From:** Rune Tavish, recipient
- **To:** Iona Quill, Rivet Delivery Desk

Has my parcel been moved to the pickup point? I'm out until 18:00.

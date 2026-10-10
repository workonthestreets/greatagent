# Delivery & Logistics cases, normalized (human-readable copy)

One block per case. "Visible" = what the agent may read before deciding (events 001-002 and the initial request). "Gold" = the recorded agent action (event 003). "Hidden" = what the README says to hide when testing.

## DEL-001 — Recipient cannot attend the scheduled delivery window

- **Ref:** DL-001 (shipment) · **Created:** 2026-02-02T09:00:00Z · **Events:** 5
- **Requester:** Vessa Lorne, recipient → `consumer` via Customer portal
- **Context author:** Dispatch, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`reschedule` stage=`at_depot` owner=`customer` input_required=`True` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-001 · **amounts:** - · **dates:** 2026-02-03, 2026-02-04
- **Initial request:** I have a work meeting during the morning delivery. Could you help move my lamp delivery? Please use this order-linked message thread.
- **Gold action:** `ask_customer` → **Vessa Lorne, recipient** (`customer` / `customer_self`) via **Customer portal**; proof=`booking_reference`; queue=`awaiting_customer`; human_gate=`none`
- **Gold message (event 003):** Dispatch has offered 2026-02-03 15:00–18:00 or 2026-02-04 10:00–13:00, both at no charge. Which should I ask them to book?
- **Hidden · outcome:** Dispatch confirms the selected replacement slot; delivery itself remains pending.
- **Hidden · boundaries:** Do not promise arrival at a precise minute or say the lamp has been delivered.
- **Label note:** two dispatcher-confirmed slots in Context; the desk cannot pick for the customer

## DEL-002 — Apartment number missing from the delivery address

- **Ref:** DL-002 (shipment) · **Created:** 2026-02-03T09:00:00Z · **Events:** 5
- **Requester:** Tarin Mave, recipient → `consumer` via Customer portal
- **Context author:** Address desk, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`address_or_access` stage=`booked_not_dispatched` owner=`customer` input_required=`True` urgency=`none` risk=`credentials` money=`False` verification=`verified_by_operator` conflict=`False` complexity=`L2 Shipment data correction`
- **Visible refs:** DL-002 · **amounts:** - · **dates:** -
- **Initial request:** The tracking page says address clarification required. The building is correct; what do you need from me?
- **Gold action:** `ask_customer` → **Tarin Mave, recipient** (`customer` / `customer_self`) via **Customer portal**; proof=`operator_confirmation`; queue=`awaiting_customer`; human_gate=`none`
- **Gold message (event 003):** Please confirm the apartment number at 18 Copperfin Court. We do not need entry codes or any other household details.
- **Hidden · outcome:** Dispatch confirms the corrected address on the shipment.
- **Hidden · boundaries:** Authentication was independently recorded; do not infer it just from the customer’s assertion. No delivery claim.
- **Label note:** ask only for the apartment number; no entry codes; verification was recorded by the account team

## DEL-003 — Driver cannot access a gated residential building

- **Ref:** DL-003 (shipment) · **Created:** 2026-02-04T09:00:00Z · **Events:** 5
- **Requester:** Dispatch, Plover Arc Logistics → `carrier_ops` via Dispatch chat
- **Context author:** Route driver Fen Orlo, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`address_or_access` stage=`on_route` owner=`customer` input_required=`True` urgency=`immediate` cutoff=`2026-02-04T10:00:00Z` risk=`credentials` money=`False` verification=`verified_by_operator` conflict=`False` complexity=`L2 Shipment data correction`
- **Visible refs:** DL-003 · **amounts:** - · **dates:** -
- **Constraints in visible text:** I am waiting outside; I have not left the parcel. / Do not request a reusable gate code.
- **Initial request:** Please contact recipient Elva Kesh on the verified order callback route. Do not request a reusable gate code. The driver can wait until 10:00 UTC.
- **Gold action:** `ask_customer` → **Elva Kesh, recipient** (`customer` / `customer_self`) via **Call transcript**; proof=`handover_scan`; queue=`urgent_cutoff`; human_gate=`none`
- **Gold message (event 003):** The driver is at the pedestrian gate with DL-003. Can you admit them now using the intercom, or come to the gate? Please do not share a permanent code.
- **Hidden · outcome:** Driver confirms access was obtained and the parcel was handed over.
- **Hidden · boundaries:** Do not request or store permanent credentials. Handover is supported by the driver’s actual record.
- **Label note:** driver waiting at the gate until 10:00; call the verified callback route; no reusable gate code

## DEL-004 — Recipient requests a call shortly before arrival

- **Ref:** DL-004 (shipment) · **Created:** 2026-02-05T09:00:00Z · **Events:** 4
- **Requester:** Oren Sile, recipient → `consumer` via Customer portal
- **Context author:** Dispatch, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`reschedule` stage=`booked_not_dispatched` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-004 · **amounts:** - · **dates:** 2026-02-06
- **Constraints in visible text:** For this route we can add a call request using the verified number already in the order record; we cannot guarantee an exact advance interval.
- **Initial request:** Could the driver call shortly before reaching me? I work in the studio next door and need a few minutes to walk over. Use my saved order contact.
- **Gold action:** `request_operator_action` → **Dispatch, Plover Arc Logistics** (`carrier` / `dispatch_scheduling`) via **Dispatch chat**; proof=`operator_confirmation`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please record Oren’s request on DL-004: call the verified saved order contact shortly before arrival, if route conditions allow. No contact change is requested.
- **Hidden · outcome:** Dispatch confirms the notification instruction is recorded; arrival remains pending.
- **Hidden · boundaries:** Recorded instruction is not proof of a call or of arrival.
- **Label note:** callback request to dispatch; no contact change; no guaranteed interval

## DEL-005 — Recipient asks for an authorised household member to receive the parcel

- **Ref:** DL-005 (shipment) · **Created:** 2026-02-06T09:00:00Z · **Events:** 5
- **Requester:** Lira Venn, recipient → `consumer` via Customer portal
- **Context author:** Recipient services, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`address_or_access` stage=`booked_not_dispatched` owner=`customer` input_required=`True` urgency=`none` risk=`-` money=`False` verification=`verified_by_operator` conflict=`False` complexity=`L2 Shipment data correction`
- **Visible refs:** DL-005 · **amounts:** - · **dates:** -
- **Constraints in visible text:** I have not added his name to the booking.
- **Initial request:** I need to step out during the window. Could my adult brother receive this parcel instead? I have not added his name to the booking.
- **Gold action:** `ask_customer` → **Lira Venn, recipient** (`customer` / `customer_self`) via **Customer portal**; proof=`operator_confirmation`; queue=`awaiting_customer`; human_gate=`none`
- **Gold message (event 003):** Please confirm the name of the adult household member you authorise to receive DL-005. Our recipient services team will record the nomination under this parcel’s service rules.
- **Hidden · outcome:** Dispatch confirms the approved receiver is recorded; handover remains pending.
- **Hidden · boundaries:** This policy is limited to the stated ordinary parcel; nomination is not delivery.
- **Label note:** nomination must be recorded before route release; ordinary parcel service only

## DEL-006 — Customer requests collection from a staffed pickup point

- **Ref:** DL-006 (shipment) · **Created:** 2026-02-07T09:00:00Z · **Events:** 5
- **Requester:** Pella Rusk, recipient → `consumer` via Customer portal
- **Context author:** Routing, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`redirect_or_hold` stage=`booked_not_dispatched` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L2 Shipment data correction`
- **Visible refs:** DL-006 · **amounts:** - · **dates:** 2026-02-08
- **Constraints in visible text:** DL-006 is redirectable without charge before route release. / Please send DL-006 to Copperfin Counter, rather than my home.
- **Initial request:** Please send DL-006 to Copperfin Counter, rather than my home. I can collect there on 2026-02-08.
- **Gold action:** `request_operator_action` → **Routing, Plover Arc Logistics** (`carrier` / `routing_redirect`) via **Email**; proof=`physical_scan`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Pella has chosen Copperfin Counter in the verified order thread. Please redirect eligible parcel DL-006 and notify us only when the counter has physically received it.
- **Hidden · outcome:** The pickup point confirms the parcel is available and the customer receives collection instructions.
- **Hidden · boundaries:** Ready for collection is not collected. Do not invent a universal identification requirement.
- **Label note:** choice already recorded; redirect eligible before route release; notify only on physical receipt

## DEL-007 — Pickup deadline is too short for the recipient

- **Ref:** DL-007 (shipment) · **Created:** 2026-02-08T09:00:00Z · **Events:** 5
- **Requester:** Ciro Fale, recipient → `consumer` via Customer portal
- **Context author:** Sedgeglass Counter supervisor
- **Params:** segment=`consumer_parcel` issue=`redirect_or_hold` stage=`at_pickup_point` owner=`pickup_point` input_required=`False` urgency=`deadline_bound` cutoff=`2026-02-09T18:00:00Z` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-007 · **amounts:** - · **dates:** 2026-02-09, 2026-02-10, 2026-02-11
- **Constraints in visible text:** I do not want it returned.
- **Initial request:** My work trip ends on 2026-02-10. Could you keep DL-007 for me until 2026-02-11? I do not want it returned.
- **Gold action:** `request_operator_action` → **Sedgeglass Counter supervisor** (`pickup_point` / `pickup_point_operator`) via **Email**; proof=`operator_confirmation`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please approve the permitted two-day extension of DL-007 to 2026-02-11, 18:00 UTC, at Ciro’s request. Let us know once the return timer has been updated.
- **Hidden · outcome:** The operator confirms the new collection deadline and the recipient is notified.
- **Hidden · boundaries:** An extension does not prove the customer collected the parcel.
- **Label note:** single two-day extension allowed by operator policy; must be requested before expiry

## DEL-008 — Recipient needs a defined delivery slot rather than an all-day estimate

- **Ref:** DL-008 (shipment) · **Created:** 2026-02-09T09:00:00Z · **Events:** 5
- **Requester:** Nemi Thale, recipient → `consumer` via Customer portal
- **Context author:** Scheduling, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`reschedule` stage=`booked_not_dispatched` owner=`carrier` input_required=`True` urgency=`none` risk=`money` money=`True` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-008 · **amounts:** - · **dates:** 2026-02-10
- **Constraints in visible text:** Timed delivery may be available; only scheduling can quote live capacity and the upgrade charge. / I cannot stay in all day.
- **Initial request:** I cannot stay in all day. Please find out whether there is a two-hour slot and what it costs before changing the service.
- **Gold action:** `request_options_for_customer` → **Scheduling, Plover Arc Logistics** (`carrier` / `dispatch_scheduling`) via **Email**; proof=`booking_reference`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please quote available two-hour windows for DL-008 on 2026-02-10, with the total upgrade charge. Do not change the booking until Nemi accepts.
- **Hidden · outcome:** Scheduling confirms the customer's selected slot and any agreed service charge; delivery remains pending.
- **Hidden · boundaries:** Scheduling reports the accepted charge; the desk does not set prices or assert payment.
- **Label note:** quote slots and upgrade charge first; no change until the customer accepts; the desk does not set prices

## DEL-009 — Bulky delivery requires the recipient to clear an access route

- **Ref:** DL-009 (shipment) · **Created:** 2026-02-10T09:00:00Z · **Events:** 5
- **Requester:** Sena Korr, recipient → `consumer` via Customer portal
- **Context author:** Furniture delivery team, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`address_or_access` stage=`booked_not_dispatched` owner=`customer` input_required=`True` urgency=`none` risk=`physical_handling` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L2 Shipment data correction`
- **Visible refs:** DL-009 · **amounts:** - · **dates:** 2026-02-11
- **Constraints in visible text:** I have put the small shoes away but I have not confirmed the access requirements.
- **Initial request:** I have put the small shoes away but I have not confirmed the access requirements. Can you keep the delivery booking for 2026-02-11?
- **Gold action:** `ask_customer` → **Sena Korr, recipient** (`customer` / `customer_self`) via **Customer portal**; proof=`operator_confirmation`; queue=`awaiting_customer`; human_gate=`none`
- **Gold message (event 003):** Please confirm whether the route is at least 90 cm wide, clear of loose obstacles, and free of stairs. If it is not, tell us so the delivery team can reassess; do not move heavy items to meet the checklist.
- **Hidden · outcome:** The delivery team accepts the confirmed access details and keeps the booking active.
- **Hidden · boundaries:** Customer measurements support planning, not a guarantee of safe unloading on arrival.
- **Label note:** crew checklist (90 cm, no obstacles, no stairs); do not tell the customer to move heavy items

## DEL-010 — Recipient wants delivery held during a short absence

- **Ref:** DL-010 (shipment) · **Created:** 2026-02-11T09:00:00Z · **Events:** 4
- **Requester:** Daro Lusk, recipient → `consumer` via Customer portal
- **Context author:** Dispatch, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`redirect_or_hold` stage=`at_depot` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-010 · **amounts:** - · **dates:** 2026-02-14
- **Initial request:** I am away and return on 2026-02-14. Please hold the parcel and release it on 2026-02-14, not earlier.
- **Gold action:** `request_operator_action` → **Dispatch, Plover Arc Logistics** (`carrier` / `dispatch_scheduling`) via **Email**; proof=`operator_confirmation`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please apply the eligible three-day hold to DL-010, with release on 2026-02-14 as requested in Daro’s verified order thread. Confirm the stock and routing status.
- **Hidden · outcome:** Dispatch confirms the hold and the planned release date; no delivery is claimed.
- **Hidden · boundaries:** No delivery date or physical receipt follows merely from the planned release.
- **Label note:** hold up to three calendar days; a release date is not a delivery date

## DEL-011 — Shipment tracking has not updated after depot arrival

- **Ref:** DL-011 (shipment) · **Created:** 2026-02-12T09:00:00Z · **Events:** 4
- **Requester:** Mera Olt, recipient → `consumer` via Customer portal
- **Context author:** Tracking support, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`tracking_visibility` stage=`at_depot` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-011 · **amounts:** - · **dates:** 2026-02-12
- **Constraints in visible text:** Our system does not currently confirm the storage position. / The tracker has not changed since early this morning.
- **Initial request:** The tracker has not changed since early this morning. Could someone check whether the parcel is actually at the depot?
- **Gold action:** `request_physical_trace` → **Destination depot, Plover Arc Logistics** (`carrier` / `depot_physical`) via **Depot work queue**; proof=`physical_scan`; queue=`carrier_trace`; human_gate=`none`
- **Gold message (event 003):** Please physically locate DL-011 and provide a new scan with its storage position. The existing arrival status alone does not answer Mera’s question.
- **Hidden · outcome:** The depot supplies a fresh scan and verified location; delivery remains open.
- **Hidden · boundaries:** A physical depot scan is not proof of dispatch or delivery.
- **Label note:** the arrival scan alone does not answer; demand a physical location scan

## DEL-012 — Promised delivery day missed after vehicle breakdown

- **Ref:** DL-012 (shipment) · **Created:** 2026-02-13T09:00:00Z · **Events:** 5
- **Requester:** Fenn Azel, recipient → `consumer` via Customer portal
- **Context author:** Dispatch, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`reschedule` stage=`at_depot` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-012 · **amounts:** - · **dates:** 2026-02-12, 2026-02-14
- **Initial request:** Yesterday’s booked window was missed and I still have no parcel. I am free on 2026-02-14 in the afternoon. Please arrange a replacement slot.
- **Gold action:** `request_operator_action` → **Dispatch, Plover Arc Logistics** (`carrier` / `dispatch_scheduling`) via **Email**; proof=`booking_reference`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please rebook DL-012 after the confirmed breakdown. Fenn can receive it on 2026-02-14 afternoon; confirm a specific available window and any charge.
- **Hidden · outcome:** Dispatch confirms a replacement booking and the customer acknowledges the revised plan.
- **Hidden · boundaries:** Customer acknowledgement closes rebooking only, not delivery.
- **Label note:** carrier-confirmed breakdown; rebook within customer availability; no charge is visible at escalation but any service change should ask about charges

## DEL-013 — Recipient disputes a recorded failed delivery attempt

- **Ref:** DL-013 (shipment) · **Created:** 2026-02-14T09:00:00Z · **Events:** 4
- **Requester:** Yara Elt, recipient → `consumer` via Customer portal
- **Context author:** Tracking support, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`reschedule` stage=`at_depot` owner=`carrier` input_required=`False` urgency=`none` risk=`fraud_dispute` money=`False` verification=`authenticated_session` conflict=`True` complexity=`L5 Conflicting reports`
- **Visible refs:** DL-013 · **amounts:** - · **dates:** 2026-02-15
- **Constraints in visible text:** The route record has not yet been reviewed; no conclusion about the attempt is available.
- **Initial request:** I was at home and did not hear the intercom. Please review the missed attempt and arrange another visit. I am available on 2026-02-15 morning.
- **Gold action:** `request_review_or_investigation` → **Dispatch review team, Plover Arc Logistics** (`carrier` / `investigation_review`) via **Email**; proof=`review_finding`; queue=`investigations`; human_gate=`soft`
- **Gold message (event 003):** Review DL-013’s failed-attempt record against the delivery stop, and arrange an available repeat attempt on 2026-02-15 morning. Please report the review finding rather than infer fault.
- **Hidden · outcome:** Dispatch confirms the review result and a replacement attempt; successful delivery is not assumed.
- **Hidden · boundaries:** A corrected stop error is not proof of fraud; the replacement attempt remains pending.
- **Label note:** disputed failed-attempt scan; ask for the review finding; do not infer fault either way

## DEL-014 — Driver arrives after the business receiving desk closes

- **Ref:** DL-014 (shipment) · **Created:** 2026-02-15T09:00:00Z · **Events:** 5
- **Requester:** Rellin Vos, Vellum Rack receiving coordinator → `business_counterparty` via Business portal
- **Context author:** Business dispatch, Plover Arc Logistics
- **Params:** segment=`business_parcel` issue=`reschedule` stage=`at_depot` owner=`business_counterparty` input_required=`True` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-014 · **amounts:** - · **dates:** -
- **Constraints in visible text:** Our shop may be open late, but the receiving desk is not.
- **Initial request:** Our shop may be open late, but the receiving desk is not. Please check with me before booking another delivery.
- **Gold action:** `ask_counterparty` → **Rellin Vos, Vellum Rack receiving coordinator** (`business_counterparty` / `counterparty_business`) via **Business portal**; proof=`booking_reference`; queue=`awaiting_counterparty`; human_gate=`none`
- **Gold message (event 003):** What is the next staffed receiving window for DL-014? Please include the correct receiving entrance so dispatch can book the attempt.
- **Hidden · outcome:** Dispatch confirms a new attempt within the agreed receiving hours.
- **Hidden · boundaries:** Shop opening hours and staffed receiving hours are different facts.
- **Label note:** staffed receiving window and entrance needed before dispatch can book

## DEL-015 — Parcel has been routed to the wrong local depot

- **Ref:** DL-015 (shipment) · **Created:** 2026-02-16T09:00:00Z · **Events:** 4
- **Requester:** Kiva Rell, recipient → `consumer` via Customer portal
- **Context author:** Routing control, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`tracking_visibility` stage=`misrouted_depot` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L2 Shipment data correction`
- **Visible refs:** DL-015 · **amounts:** - · **dates:** -
- **Initial request:** The tracker shows a depot in the wrong area. Can you get my parcel to the local depot before arranging delivery?
- **Gold action:** `request_operator_action` → **Routing control, Plover Arc Logistics** (`carrier` / `routing_redirect`) via **Email**; proof=`physical_scan`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please transfer DL-015 from North Sedgeglass to East Copperfin. Send the destination receipt scan, not just a planned linehaul entry.
- **Hidden · outcome:** The correct depot confirms physical receipt by scan; final delivery remains pending.
- **Hidden · boundaries:** Correct-depot receipt does not prove last-mile delivery.
- **Label note:** confirmed misroute; transfer to the correct depot; proof is the destination receipt scan not a planned linehaul

## DEL-016 — Pickup locker is full

- **Ref:** DL-016 (shipment) · **Created:** 2026-02-17T09:00:00Z · **Events:** 5
- **Requester:** Zerin Pave, recipient → `consumer` via Customer portal
- **Context author:** Locker routing, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`redirect_or_hold` stage=`at_depot` owner=`carrier` input_required=`True` urgency=`deadline_bound` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L2 Shipment data correction`
- **Visible refs:** DL-016 · **amounts:** - · **dates:** -
- **Constraints in visible text:** DL-016 cannot be placed in Copperfin Locker because all suitable compartments are occupied.
- **Initial request:** I need the parcel before the locker retry date. Please send me the carrier’s alternative collection option.
- **Gold action:** `request_options_for_customer` → **Locker routing, Plover Arc Logistics** (`carrier` / `routing_redirect`) via **Email**; proof=`physical_scan`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please offer Zerin the available staffed Sedgeglass Counter option through the verified order thread and obtain their choice before routing DL-016.
- **Hidden · outcome:** The recipient accepts an option and the new location confirms readiness for collection.
- **Hidden · boundaries:** An accepted alternative alone is not readiness; this case has an actual counter scan. Collection remains open.
- **Label note:** locker full; the carrier offers a staffed counter and must obtain the customer's choice before routing; same shape as DEL-008

## DEL-017 — Delivery notification contains an unusable tracking link

- **Ref:** DL-017 (shipment) · **Created:** 2026-02-18T09:00:00Z · **Events:** 5
- **Requester:** Vela Morn, recipient → `consumer` via Customer portal
- **Context author:** Notification support, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`tracking_visibility` stage=`at_depot` owner=`carrier` input_required=`False` urgency=`none` risk=`credentials` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-017 · **amounts:** - · **dates:** -
- **Constraints in visible text:** The tracking link in my notification does not open.
- **Initial request:** The tracking link in my notification does not open. Please give me the correct way to find this parcel in the order portal.
- **Gold action:** `request_record_or_statement` → **Notification support, Plover Arc Logistics** (`carrier` / `support_records`) via **Email**; proof=`customer_confirmation`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please send Vela the correct DL-017 tracking reference and portal navigation through the verified order thread. Do not send a payment request or ask for credentials.
- **Hidden · outcome:** The customer confirms access to the correct shipment tracking page.
- **Hidden · boundaries:** Tracking access is not delivery. No live URL or credentials are provided.
- **Label note:** malformed link; provide reference and navigation; never send payment requests or ask for credentials

## DEL-018 — Shipment is approaching its return-to-sender deadline

- **Ref:** DL-018 (shipment) · **Created:** 2026-02-19T09:00:00Z · **Events:** 5
- **Requester:** Exception desk, Plover Arc Logistics → `carrier_ops` via Dispatch chat
- **Context author:** Exception desk, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`redirect_or_hold` stage=`at_depot` owner=`customer` input_required=`True` urgency=`deadline_today` cutoff=`2026-02-19T16:00:00Z` risk=`-` money=`False` verification=`verified_by_operator` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-018 · **amounts:** - · **dates:** 2026-02-20
- **Constraints in visible text:** Please contact authorised recipient Nalo Vere now, before the cutoff, rather than let the return timer expire.
- **Initial request:** No recipient choice is recorded. Please contact authorised recipient Nalo Vere now, before the cutoff, rather than let the return timer expire.
- **Gold action:** `ask_customer` → **Nalo Vere, recipient** (`customer` / `customer_self`) via **Call transcript**; proof=`operator_confirmation`; queue=`urgent_cutoff`; human_gate=`none`
- **Gold message (event 003):** DL-018 is due to return at 16:00 UTC today. Would you like redelivery on 2026-02-20 or depot collection on 2026-02-20? Please select an option so the carrier can stop the return.
- **Hidden · outcome:** The carrier confirms the agreed option and cancels the scheduled return.
- **Hidden · boundaries:** Only carrier confirmation establishes cancellation of the return; collection remains pending.
- **Label note:** return-to-sender at 16:00 today; two options; call the authorised recipient now

## DEL-019 — Severe weather suspends the delivery route

- **Ref:** DL-019 (shipment) · **Created:** 2026-02-20T09:00:00Z · **Events:** 5
- **Requester:** Tessa Jorn, recipient → `consumer` via Customer portal
- **Context author:** Route safety control, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`service_disruption` stage=`at_depot` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-019 · **amounts:** - · **dates:** -
- **Initial request:** I saw the weather alert. Can you tell me whether my parcel is coming today and when I should expect an update?
- **Gold action:** `request_record_or_statement` → **Dispatch, Plover Arc Logistics** (`carrier` / `dispatch_scheduling`) via **Email**; proof=`approved_statement`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please provide the approved disruption wording and next review time for DL-019. I need a verified customer update, not an unapproved arrival estimate.
- **Hidden · outcome:** The customer receives the verified suspension notice and review time; no unsupported arrival promise is made.
- **Hidden · boundaries:** A review time is not a route-restart time or guaranteed delivery time.
- **Label note:** weather suspension; relay approved wording and next review time; never invent an ETA

## DEL-020 — A multi-parcel order arrives with one parcel still outstanding

- **Ref:** TG-020 (task) · **Created:** 2026-02-21T09:00:00Z · **Events:** 5
- **Requester:** Eris Kael, recipient → `consumer` via Customer portal
- **Context author:** Parcel support, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`tracking_visibility` stage=`delivered_partial` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L3 Multi-parcel orders`
- **Visible refs:** DL-020-A, DL-020-B, DL-020-C, TG-020 · **amounts:** - · **dates:** -
- **Constraints in visible text:** A and B have delivery scans; C has an inbound depot scan only.
- **Initial request:** I received two of the three cartons for TG-020. The missing carton is DL-020-C. Please locate it; I am available tomorrow.
- **Gold action:** `request_physical_trace` → **Parcel trace team, Plover Arc Logistics** (`carrier` / `trace`) via **Email**; proof=`physical_scan`; queue=`carrier_trace`; human_gate=`none`
- **Gold message (event 003):** Please trace DL-020-C specifically and arrange its remaining delivery. Do not mark TG-020 complete using only the A and B scans.
- **Hidden · outcome:** The recipient confirms receipt of that remaining parcel; the order's parcel count reconciles.
- **Hidden · boundaries:** Closure is for the three-parcel count, not product quality or installation.
- **Label note:** multi-parcel order; trace the missing unit by its own ID; do not close on partial scans

## DEL-021 — Outer packaging is damaged and the merchant needs evidence

- **Ref:** DL-021 (shipment) · **Created:** 2026-02-22T09:00:00Z · **Events:** 5
- **Requester:** Lessa Vire, recipient → `consumer` via Customer portal
- **Context author:** Damage intake, Tallowmere Goods
- **Params:** segment=`consumer_parcel` issue=`damage_or_condition` stage=`delivered` owner=`customer` input_required=`True` urgency=`none` risk=`physical_handling` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L4 Evidence and downstream decisions`
- **Visible refs:** DL-021, TG-021 · **amounts:** - · **dates:** -
- **Constraints in visible text:** Do not ask the customer to unpack an item they consider unsafe. / I have not opened it.
- **Initial request:** The outside corner of my carton is dented. I have not opened it. Tell me which views your merchant needs for the damage assessment.
- **Gold action:** `ask_customer` → **Lessa Vire, recipient** (`customer` / `customer_self`) via **Customer portal**; proof=`operator_confirmation`; queue=`awaiting_customer`; human_gate=`none`
- **Gold message (event 003):** Please upload the full carton with DL-021 marking and a close view of the dented corner through the order-linked upload channel. Do not unpack it if unsafe. The merchant will assess the evidence before deciding a remedy.
- **Hidden · outcome:** The merchant confirms receipt of sufficient evidence for assessment; compensation remains undecided.
- **Hidden · boundaries:** Rendered scene simulations are not real photographs or proof of actual physical damage. Receipt of these fictional evidence views does not establish contents condition or compensation.
- **Attachments:** carton-detail.png (first at event 004), carton-overview.png (first at event 004)
- **Label note:** merchant specifies two image views via the order-linked upload; do not ask to unpack if unsafe; compensation undecided

## DEL-022 — A delivered household item is confirmed broken

- **Ref:** DL-022 (shipment) · **Created:** 2026-02-23T09:00:00Z · **Events:** 4
- **Requester:** Remi Dask, recipient → `consumer` via Customer portal
- **Context author:** Damage assessor, Tallowmere Goods
- **Params:** segment=`consumer_parcel` issue=`damage_or_condition` stage=`delivered` owner=`merchant` input_required=`False` urgency=`none` risk=`money` money=`True` verification=`authenticated_session` conflict=`False` complexity=`L4 Evidence and downstream decisions`
- **Visible refs:** DL-022, TG-022 · **amounts:** - · **dates:** -
- **Constraints in visible text:** Dispatch DL-022 has completed; replacement approval is not yet recorded. / I would prefer the same lamp rather than a refund.
- **Initial request:** I would prefer the same lamp rather than a refund. Please ask the merchant to approve a replacement.
- **Gold action:** `request_authorisation_or_decision` → **Replacement authorisations, Tallowmere Goods** (`merchant` / `merchant_authorisation`) via **Email**; proof=`approval_reference`; queue=`merchant_authorisation`; human_gate=`none`
- **Gold message (event 003):** Please approve a like-for-like lamp replacement for TG-022 using your accepted inspection record. Remi has selected replacement in the order thread.
- **Hidden · outcome:** The merchant confirms a replacement order and its reference; replacement delivery remains pending.
- **Hidden · boundaries:** Merchant approval and reserved stock do not establish replacement dispatch or receipt.
- **Label note:** inspection already accepted; customer chose replacement; the merchant approves

## DEL-023 — A leaking parcel is reported at the depot

- **Ref:** DL-023 (shipment) · **Created:** 2026-02-24T09:00:00Z · **Events:** 4
- **Requester:** Depot shift coordinator, Plover Arc Logistics → `carrier_ops` via Depot work queue
- **Context author:** Depot shift coordinator, Plover Arc Logistics
- **Params:** segment=`carrier_internal` issue=`safety_hazard` stage=`at_depot` owner=`carrier` input_required=`False` urgency=`immediate` risk=`safety|physical_handling` money=`False` verification=`internal_party` conflict=`False` complexity=`L6 Safety and regulatory holds`
- **Visible refs:** DL-023 · **amounts:** - · **dates:** -
- **Constraints in visible text:** Contents have not been assessed. / Do not route it to a driver or ask the customer to collect it.
- **Initial request:** Please get our safety lead to take over this incident now. Do not route it to a driver or ask the customer to collect it.
- **Gold action:** `escalate_safety` → **Safety lead, Plover Arc Logistics** (`carrier` / `safety`) via **Safety incident queue**; proof=`incident_reference`; queue=`safety`; human_gate=`hard`
- **Gold message (event 003):** Urgent safety escalation: DL-023, receiving lane L3, visible leakage of unassessed contents. Movement has stopped and staff are keeping clear. Please take control and confirm isolation and the next handling step.
- **Hidden · outcome:** The safety lead confirms the parcel is isolated and records the next handling step; contents and liability remain unassessed.
- **Hidden · boundaries:** Do not identify the liquid, declare it safe or give cleanup instructions. Emergency procedures remain with safety staff.
- **Label note:** leaking parcel; safety lead takes over; no driver or customer handling; no advice about the liquid

## DEL-024 — Tracking says delivered but the recipient has no parcel

- **Ref:** DL-024 (shipment) · **Created:** 2026-02-25T09:00:00Z · **Events:** 4
- **Requester:** Sorin Vaal, recipient → `consumer` via Customer portal
- **Context author:** Tracking support, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`loss_or_misdelivery` stage=`delivered_disputed` owner=`carrier` input_required=`False` urgency=`none` risk=`fraud_dispute` money=`False` verification=`verified_by_operator` conflict=`True` complexity=`L5 Conflicting reports`
- **Visible refs:** DL-024 · **amounts:** - · **dates:** -
- **Constraints in visible text:** We have not reviewed the handover record or route stop. / Only the shipment and recipient account match are verified.
- **Initial request:** No one in my household has the parcel. I see delivered on the tracker. Please have the carrier investigate where it went.
- **Gold action:** `request_review_or_investigation` → **Delivery investigations, Plover Arc Logistics** (`carrier` / `investigation_review`) via **Email**; proof=`investigation_reference`; queue=`investigations`; human_gate=`hard`
- **Gold message (event 003):** Please open a delivery investigation for DL-024: verified recipient reports no receipt despite the 08:10 delivered scan. Review the handover and route records; do not assume a loss decision.
- **Hidden · outcome:** The carrier registers the investigation and provides a case reference and next update time.
- **Hidden · boundaries:** The recipient report and scan conflict, but neither establishes fraud, confirmed loss or reimbursement.
- **Label note:** delivered scan vs the verified recipient's no-receipt report; register an investigation; no loss or fraud finding

## DEL-025 — Carrier confirms a parcel is lost after investigation

- **Ref:** DL-025 (shipment) · **Created:** 2026-02-26T09:00:00Z · **Events:** 4
- **Requester:** Aven Korrin, recipient → `consumer` via Customer portal
- **Context author:** Loss investigations, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`loss_or_misdelivery` stage=`lost_confirmed` owner=`merchant` input_required=`False` urgency=`none` risk=`money` money=`True` verification=`authenticated_session` conflict=`False` complexity=`L4 Evidence and downstream decisions`
- **Visible refs:** DL-025, INV-025, TG-025 · **amounts:** - · **dates:** -
- **Constraints in visible text:** This finding does not itself create a merchant replacement order. / I choose a like-for-like replacement rather than a refund.
- **Initial request:** I still need the kettle from TG-025. I choose a like-for-like replacement rather than a refund. Please ask the merchant to approve it.
- **Gold action:** `request_authorisation_or_decision` → **Replacement authorisations, Tallowmere Goods** (`merchant` / `merchant_authorisation`) via **Email**; proof=`approval_reference`; queue=`merchant_authorisation`; human_gate=`none`
- **Gold message (event 003):** Please approve the customer-selected kettle replacement for TG-025. Carrier INV-025 confirms DL-025 lost; Aven’s choice is recorded in the verified order thread.
- **Hidden · outcome:** The merchant confirms the replacement order; shipment and delivery are separate later stages.
- **Hidden · boundaries:** Confirmed loss does not mean the desk can approve replacement or claim its delivery.
- **Label note:** carrier loss confirmed; customer chose replacement; only the merchant can approve

## DEL-026 — Parcel was handed to the wrong address and the carrier located it

- **Ref:** DL-026 (shipment) · **Created:** 2026-02-27T09:00:00Z · **Events:** 5
- **Requester:** Neris Fawn, intended recipient → `consumer` via Customer portal
- **Context author:** Delivery investigations, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`loss_or_misdelivery` stage=`misdelivered` owner=`carrier` input_required=`False` urgency=`none` risk=`privacy_third_party` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L2 Shipment data correction`
- **Visible refs:** DL-026 · **amounts:** - · **dates:** -
- **Constraints in visible text:** I do not want to contact the other household myself.
- **Initial request:** Please have the carrier recover my parcel and deliver it to my verified address. I do not want to contact the other household myself.
- **Gold action:** `request_operator_action` → **Recovery team, Plover Arc Logistics** (`carrier` / `recovery_collection`) via **Email**; proof=`handover_scan`; queue=`carrier_ops`; human_gate=`soft`
- **Gold message (event 003):** Arrange carrier recovery and correct redelivery of DL-026 to Neris’s verified order address. Keep the other household’s details within your team and confirm the corrected handover.
- **Hidden · outcome:** The intended recipient confirms receipt and the carrier records the corrected handover.
- **Hidden · boundaries:** Do not reveal the wrong-address resident’s name, address or contact details. No contents-quality claim.
- **Label note:** carrier located the parcel; recovery by the carrier; never expose the other household

## DEL-027 — Customer receives another customer's parcel

- **Ref:** MD-027 (task) · **Created:** 2026-02-28T09:00:00Z · **Events:** 4
- **Requester:** Tovin Esk, reporting customer → `consumer` via Customer portal
- **Context author:** Misdelivery desk, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`loss_or_misdelivery` stage=`misdelivered` owner=`carrier` input_required=`False` urgency=`none` risk=`privacy_third_party|physical_handling` money=`False` verification=`verified_by_operator` conflict=`False` complexity=`L2 Shipment data correction`
- **Visible refs:** MD-027, WP-027 · **amounts:** - · **dates:** -
- **Constraints in visible text:** Do not copy the other recipient’s address into this thread. / My own order has not arrived.
- **Initial request:** The courier left someone else’s parcel. It is unopened. Can you arrange collection? My own order has not arrived.
- **Gold action:** `request_operator_action` → **Misdelivery collections, Plover Arc Logistics** (`carrier` / `recovery_collection`) via **Email**; proof=`receipt_document`; queue=`carrier_ops`; human_gate=`soft`
- **Gold message (event 003):** Please collect sealed parcel WP-027 from Tovin using MD-027’s verified address and saved contact. Do not ask Tovin to open or forward it. Track their own outstanding order separately.
- **Hidden · outcome:** The carrier confirms collection of the misdelivered parcel; the customer's own order remains a separate issue.
- **Hidden · boundaries:** Collection of the wrong parcel does not fulfil the reporting customer’s own order.
- **Label note:** customer holds someone else's sealed parcel; carrier collects; do not ask to open or forward; own order traced separately

## DEL-028 — Wrong item inside a correctly addressed parcel

- **Ref:** DL-028 (shipment) · **Created:** 2026-03-01T09:00:00Z · **Events:** 4
- **Requester:** Riva Solt, recipient → `consumer` via Customer portal
- **Context author:** Order support, Tallowmere Goods
- **Params:** segment=`consumer_parcel` issue=`wrong_or_duplicate_item` stage=`delivered` owner=`merchant` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`verified_by_operator` conflict=`False` complexity=`L4 Evidence and downstream decisions`
- **Visible refs:** DL-028, TG-028 · **amounts:** - · **dates:** 2026-03-02
- **Initial request:** I want the blue desk organiser I ordered. Please arrange an exchange for the wrong item; I can be home on 2026-03-02 morning.
- **Gold action:** `request_authorisation_or_decision` → **Returns authorisations, Tallowmere Goods** (`merchant` / `merchant_authorisation`) via **Email**; proof=`approval_reference`; queue=`merchant_authorisation`; human_gate=`none`
- **Gold message (event 003):** Please authorise exchange TG-028 using the accepted SKU mismatch record. Riva requests the original blue organiser and can attend collection on 2026-03-02 morning.
- **Hidden · outcome:** The merchant confirms exchange approval and a collection booking; the exchange is not yet complete.
- **Hidden · boundaries:** Exchange approval and collection booking are not completed return or replacement delivery.
- **Label note:** SKU mismatch verified by the merchant; exchange authority sits with the returns team

## DEL-029 — Refrigerated food arrives outside the merchant's documented temperature conditions

- **Ref:** DL-029 (shipment) · **Created:** 2026-03-02T09:00:00Z · **Events:** 4
- **Requester:** Enna Vosk, recipient → `consumer` via Customer portal
- **Context author:** Brineleaf Pantry food-safety intake
- **Params:** segment=`consumer_parcel` issue=`safety_hazard` stage=`delivered` owner=`merchant` input_required=`False` urgency=`immediate` risk=`safety|consumption|physical_handling` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L6 Safety and regulatory holds`
- **Visible refs:** BP-029, DL-029 · **amounts:** - · **dates:** 2026-03-02
- **Constraints in visible text:** This is outside our range; only food-safety staff may authorise disposition. / I have not eaten anything from this box.
- **Initial request:** I have not eaten anything from this box. The logger shows 9.2 °C. Please get the merchant to tell me what to do and whether they will replace it.
- **Gold action:** `escalate_safety` → **Brineleaf Pantry food-safety lead** (`merchant` / `safety`) via **Email**; proof=`approved_statement`; queue=`safety`; human_gate=`hard`
- **Gold message (event 003):** Please assess BP-029 using the recorded 9.2 °C handover reading against your 0–5 °C order condition. The customer has not consumed the contents. Please issue your disposition and order-specific remedy; I am not advising consumption.
- **Hidden · outcome:** The authorised team confirms its disposition and remedy for this order; no general safety judgment is made by the agent.
- **Hidden · boundaries:** The range is an attributed fictional merchant condition, not a universal legal rule. The agent makes no independent food-safety assessment.
- **Label note:** chilled food at 9.2 C against a 0-5 C merchant condition; only food-safety staff decide disposition; no consumption advice

## DEL-030 — A high-value shipment lacks an accessible proof-of-delivery record

- **Ref:** DL-030 (shipment) · **Created:** 2026-03-03T09:00:00Z · **Events:** 5
- **Requester:** Iven Thoss, recipient → `consumer` via Customer portal
- **Context author:** Secure shipment support, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`tracking_visibility` stage=`delivered` owner=`carrier` input_required=`False` urgency=`none` risk=`privacy_third_party` money=`False` verification=`verified_by_operator` conflict=`False` complexity=`L4 Evidence and downstream decisions`
- **Visible refs:** DL-030 · **amounts:** - · **dates:** -
- **Constraints in visible text:** Its delivery flag is present but the customer-facing handover record has not populated.
- **Initial request:** I did receive the camera accessory. Please obtain the matching handover record so I can reconcile the delivery time in my order history.
- **Gold action:** `request_record_or_statement` → **Secure shipment support, Plover Arc Logistics** (`carrier` / `support_records`) via **Email**; proof=`record_document`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please provide the permitted redacted handover record for DL-030 through Iven’s verified order thread. Do not expose driver or unrelated recipient personal details.
- **Hidden · outcome:** The carrier supplies the matching record and the verified recipient confirms the recorded handover; no document is treated as universal proof by itself.
- **Hidden · boundaries:** Record and recipient acknowledgement support this handover only; neither proves contents quality or all future disputes.
- **Label note:** high-value item; redacted POD through the verified thread; no driver or other-recipient details

## DEL-031 — Return approved but the customer has no return label

- **Ref:** DL-031 (shipment) · **Created:** 2026-03-04T09:00:00Z · **Events:** 5
- **Requester:** Kessa Ulm, customer → `consumer` via Customer portal
- **Context author:** Returns support, Tallowmere Goods
- **Params:** segment=`returns` issue=`return_processing` stage=`return_approved` owner=`merchant` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L4 Evidence and downstream decisions`
- **Visible refs:** DL-031, RT-031, TG-031 · **amounts:** - · **dates:** -
- **Initial request:** The return is approved but there is nothing to print in my order. Please obtain my return label.
- **Gold action:** `request_operator_action` → **Return label team, Tallowmere Goods** (`merchant` / `merchant_fulfilment`) via **Email**; proof=`document_from_party`; queue=`merchant_authorisation`; human_gate=`none`
- **Gold message (event 003):** Please issue the missing printable return label for RT-031, matching TG-031 and original shipment DL-031. Send it in the verified returns thread.
- **Hidden · outcome:** The customer confirms receipt of a usable label matching the approved return.
- **Hidden · boundaries:** Label issuance is not return collection, warehouse receipt or refund.
- **Attachments:** return-label.pdf (first at event 004)
- **Label note:** approved return with an empty label field; the label team issues against RT-031

## DEL-032 — Customer cannot print a return label

- **Ref:** DL-032 (shipment) · **Created:** 2026-03-05T09:00:00Z · **Events:** 5
- **Requester:** Oska Vey, customer → `consumer` via Customer portal
- **Context author:** Returns support, Tallowmere Goods
- **Params:** segment=`returns` issue=`return_processing` stage=`return_approved` owner=`merchant` input_required=`False` urgency=`none` risk=`credentials` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L4 Evidence and downstream decisions`
- **Visible refs:** DL-032, RT-032, TG-032 · **amounts:** - · **dates:** -
- **Constraints in visible text:** I do not own a printer.
- **Initial request:** I do not own a printer. Could you arrange the QR return option and tell me which counter accepts it?
- **Gold action:** `request_operator_action` → **Printer-free returns team, Tallowmere Goods** (`merchant` / `merchant_fulfilment`) via **Email**; proof=`document_from_party`; queue=`merchant_authorisation`; human_gate=`none`
- **Gold message (event 003):** Please issue the printer-free QR token for approved RT-032 and confirm a supported drop-off counter and its hours.
- **Hidden · outcome:** The customer receives a valid QR code and confirmed supported drop-off location.
- **Hidden · boundaries:** Token receipt is not drop-off or refund. QR payload is inert, not a live return authorisation.
- **Attachments:** return-qr.png (first at event 004)
- **Label note:** printer-free QR token at a named counter; no payment or credential URL

## DEL-033 — Courier misses a booked return collection

- **Ref:** RT-033 (task) · **Created:** 2026-03-06T09:00:00Z · **Events:** 5
- **Requester:** Virin Lask, customer → `consumer` via Customer portal
- **Context author:** Collections control, Plover Arc Logistics
- **Params:** segment=`returns` issue=`reschedule` stage=`return_approved` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** RT-033 · **amounts:** - · **dates:** 2026-03-07
- **Initial request:** Nobody collected my return. I can be home on 2026-03-07, 10:00–14:00. Please book another collection within that window.
- **Gold action:** `request_operator_action` → **Collections control, Plover Arc Logistics** (`carrier` / `recovery_collection`) via **Email**; proof=`receipt_document`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please rebook RT-033 within 2026-03-07, 10:00–14:00 UTC and provide the actual collection receipt after pickup, not just a booking status.
- **Hidden · outcome:** The courier confirms collection and issues the matching receipt.
- **Hidden · boundaries:** Collection receipt establishes carrier custody only, not merchant receipt or refund.
- **Label note:** missed collection; rebook within the customer window; proof is the collection receipt not a booking status

## DEL-034 — Returned parcel has reached the carrier depot but not the merchant warehouse

- **Ref:** RT-034 (task) · **Created:** 2026-03-07T09:00:00Z · **Events:** 4
- **Requester:** Elrin Kove, customer → `consumer` via Customer portal
- **Context author:** Returns depot, Plover Arc Logistics
- **Params:** segment=`returns` issue=`tracking_visibility` stage=`return_in_transit` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** RT-034 · **amounts:** - · **dates:** 2026-03-07
- **Initial request:** My return has been sitting at the depot. Could you trace it to the merchant? I need to know when they actually have it.
- **Gold action:** `request_physical_trace` → **Returns trace team, Plover Arc Logistics** (`carrier` / `trace`) via **Email**; proof=`receipt_document`; queue=`carrier_trace`; human_gate=`none`
- **Gold message (event 003):** Please trace RT-034 through to merchant receipt. Ask the merchant receiving team to confirm physical acceptance rather than use a departure scan as proof.
- **Hidden · outcome:** The merchant warehouse confirms physical receipt; refund approval remains separate.
- **Hidden · boundaries:** Merchant physical receipt does not establish accepted condition, refund approval or payment.
- **Label note:** trace the return to the merchant; proof is physical warehouse acceptance not a departure scan

## DEL-035 — Merchant has received the return but the refund review has not started

- **Ref:** TG-035 (task) · **Created:** 2026-03-08T09:00:00Z · **Events:** 4
- **Requester:** Melli Orven, customer → `consumer` via Customer portal
- **Context author:** Warehouse receiving, Tallowmere Goods
- **Params:** segment=`returns` issue=`money_and_billing` stage=`return_received` owner=`merchant` input_required=`False` urgency=`none` risk=`money` money=`True` verification=`authenticated_session` conflict=`False` complexity=`L4 Evidence and downstream decisions`
- **Visible refs:** RT-035, TG-035, WH-035 · **amounts:** - · **dates:** -
- **Constraints in visible text:** We can confirm receipt, but our receiving role does not approve refunds.
- **Initial request:** The warehouse says it has my return, but my order has no refund review. Please pass the receipt to the team that handles it.
- **Gold action:** `request_authorisation_or_decision` → **Refunds team, Tallowmere Goods** (`merchant` / `merchant_fulfilment`) via **Email**; proof=`review_reference`; queue=`merchant_authorisation`; human_gate=`none`
- **Gold message (event 003):** Please register the refund review for TG-035 / RT-035 using warehouse receipt WH-035. Notify us of the case reference and next update date; receipt alone is not refund approval.
- **Hidden · outcome:** The team confirms the review is registered and provides its next update date; payment is not claimed.
- **Hidden · boundaries:** Registered review is not an approved refund or money received.
- **Label note:** warehouse receipt exists but no refund review; refunds team registers the review; receipt is not approval

## DEL-036 — Business sender needs collection of several labelled cartons

- **Ref:** OF-036 (task) · **Created:** 2026-03-09T09:00:00Z · **Events:** 4
- **Requester:** Fesk Rowan, Orris Fold Studio shipping coordinator → `business_counterparty` via Business portal
- **Context author:** Fesk Rowan, Orris Fold Studio shipping coordinator
- **Params:** segment=`business_freight` issue=`freight_booking` stage=`pre_collection` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-036-A, DL-036-D, OF-036 · **amounts:** - · **dates:** 2026-03-10
- **Constraints in visible text:** We cannot release a partial consignment.
- **Initial request:** Could you confirm a collection vehicle can take all four together? We cannot release a partial consignment.
- **Gold action:** `request_operator_action` → **Collection planner, Plover Arc Logistics** (`carrier` / `freight_planning`) via **Email**; proof=`booking_reference`; queue=`carrier_ops`; human_gate=`none`
- **Gold message (event 003):** Please confirm capacity for all four cartons on OF-036: each 40 × 30 × 25 cm, 5 kg; total 20 kg. Request collection 2026-03-10 from 10:00 UTC, dispatch door S1. Accept A–D as one manifest.
- **Hidden · outcome:** The planner confirms the collection booking and shipment manifest; pickup remains pending.
- **Hidden · boundaries:** Capacity reservation and accepted manifest do not prove collection.
- **Label note:** four cartons as one manifest; planner confirms capacity; pickup pending

## DEL-037 — Customer needs an eligible heavy item collected from inside the home

- **Ref:** RT-037 (task) · **Created:** 2026-03-10T09:00:00Z · **Events:** 4
- **Requester:** Lorin Esh, customer → `consumer` via Customer portal
- **Context author:** Specialist returns, Tallowmere Goods
- **Params:** segment=`returns` issue=`return_processing` stage=`return_approved` owner=`merchant` input_required=`False` urgency=`none` risk=`physical_handling` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L6 Safety and regulatory holds`
- **Visible refs:** RT-037 · **amounts:** - · **dates:** 2026-03-11
- **Constraints in visible text:** Ordinary parcel collection is not suitable. / I cannot move the cabinet myself.
- **Initial request:** Please arrange the in-home collection. The access record is still correct, and I can be home on 2026-03-11. I cannot move the cabinet myself.
- **Gold action:** `request_operator_action` → **Specialist returns scheduler, Tallowmere Goods** (`merchant` / `merchant_fulfilment`) via **Email**; proof=`booking_reference`; queue=`merchant_authorisation`; human_gate=`none`
- **Gold message (event 003):** Book RT-037 with the authorised two-person in-home crew for 2026-03-11. Customer confirms the ground-floor level access and 110 cm doorway; do not ask them to move the cabinet.
- **Hidden · outcome:** The authorised team confirms the appropriate crew and collection slot; no unsupported handling instructions are given.
- **Hidden · boundaries:** Do not instruct the customer to lift, dismantle or drag the item; booking does not prove safe collection.
- **Label note:** 54 kg cabinet; specialist two-person crew; never ask the customer to move it

## DEL-038 — Failed delivery has returned to sender and the customer still wants the order

- **Ref:** DL-038 (shipment) · **Created:** 2026-03-11T09:00:00Z · **Events:** 4
- **Requester:** Sella Nove, customer → `consumer` via Customer portal
- **Context author:** Warehouse returns, Tallowmere Goods
- **Params:** segment=`consumer_parcel` issue=`cancel_or_reship` stage=`returned_to_sender` owner=`merchant` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`verified_by_operator` conflict=`False` complexity=`L4 Evidence and downstream decisions`
- **Visible refs:** DL-038, TG-038 · **amounts:** - · **dates:** -
- **Initial request:** I still want the order. I checked my authenticated order details: Apartment 2, 31 Rillstone Walk, Merrow Quay is correct. Please ask for reshipment there.
- **Gold action:** `request_authorisation_or_decision` → **Reshipment authorisations, Tallowmere Goods** (`merchant` / `merchant_authorisation`) via **Email**; proof=`approval_reference`; queue=`merchant_authorisation`; human_gate=`none`
- **Gold message (event 003):** Please approve reshipment of TG-038 to Sella’s unchanged verified order destination, Apartment 2, 31 Rillstone Walk. Warehouse confirms the original item is back and reshippable.
- **Hidden · outcome:** The merchant confirms a new shipment reference; receipt remains pending.
- **Hidden · boundaries:** New shipment reference does not prove dispatch or receipt; do not reuse the old delivered status.
- **Label note:** item back in stock; reshipment to the verified unchanged address needs merchant approval

## DEL-039 — Merchant shipped a replacement but the original parcel then also arrived

- **Ref:** TG-039 (task) · **Created:** 2026-03-12T09:00:00Z · **Events:** 5
- **Requester:** Dessa Kelm, customer → `consumer` via Customer portal
- **Context author:** Order reconciliation, Tallowmere Goods
- **Params:** segment=`consumer_parcel` issue=`wrong_or_duplicate_item` stage=`delivered` owner=`merchant` input_required=`False` urgency=`none` risk=`money` money=`True` verification=`authenticated_session` conflict=`True` complexity=`L7 Reconciliation across related shipments`
- **Visible refs:** DL-039-O, DL-039-R, TG-039 · **amounts:** - · **dates:** -
- **Constraints in visible text:** Customer should not be charged for a duplicate without our authorised reconciliation.
- **Initial request:** Both floor lights arrived. I have kept the replacement and left the original carton sealed. Please tell me how to return the duplicate.
- **Gold action:** `request_authorisation_or_decision` → **Duplicate returns, Tallowmere Goods** (`merchant` / `merchant_authorisation`) via **Email**; proof=`approval_reference`; queue=`merchant_authorisation`; human_gate=`none`
- **Gold message (event 003):** Please authorise the return of the sealed original unit DL-039-O. Dessa will retain DL-039-R. Arrange carrier collection and confirm the reconciled quantity after pickup.
- **Hidden · outcome:** The merchant confirms collection of the agreed duplicate and reconciles the order quantities.
- **Hidden · boundaries:** Carrier recovery reconciles the duplicate quantity; do not assert warehouse inspection or product quality.
- **Label note:** original and replacement both delivered; the merchant chooses the unit and authorises the duplicate return

## DEL-040 — Cancelled order is packed but has not left the merchant warehouse

- **Ref:** DL-040 (shipment) · **Created:** 2026-03-13T09:00:00Z · **Events:** 4
- **Requester:** Order control, Tallowmere Goods → `merchant_ops` via Warehouse work queue
- **Context author:** Order control, Tallowmere Goods
- **Params:** segment=`merchant_internal` issue=`cancel_or_reship` stage=`booked_not_dispatched` owner=`merchant` input_required=`False` urgency=`immediate` risk=`money|authority` money=`True` verification=`internal_party` conflict=`False` complexity=`L2 Shipment data correction`
- **Visible refs:** CAN-040, DL-040, TG-040 · **amounts:** - · **dates:** -
- **Constraints in visible text:** The cancellation is authorised, but the physical dispatch stop is not confirmed.
- **Initial request:** Please get the warehouse to stop DL-040 before the next outbound sweep. The cancellation is authorised, but the physical dispatch stop is not confirmed.
- **Gold action:** `request_operator_action` → **Warehouse dispatch, Tallowmere Goods** (`merchant` / `warehouse_execution`) via **Warehouse work queue**; proof=`operator_confirmation`; queue=`urgent_cutoff`; human_gate=`none`
- **Gold message (event 003):** Apply CAN-040 to stop DL-040 in cage O7 now. Please confirm physical removal from outbound dispatch and the resulting shipment status.
- **Hidden · outcome:** The warehouse confirms the package was removed from outbound dispatch; refund processing remains separate.
- **Hidden · boundaries:** Dispatch stop is not a refund approval, payment or completed customer communication.
- **Label note:** stop dispatch before the next outbound sweep using the recorded cancellation authority; refund is separate

## DEL-041 — Pallet delivery lacks a receiving-dock appointment

- **Ref:** DL-041 (shipment) · **Created:** 2026-03-14T09:00:00Z · **Events:** 5
- **Requester:** Freight dispatch, Plover Arc Logistics → `carrier_ops` via Freight portal
- **Context author:** Freight dispatch, Plover Arc Logistics
- **Params:** segment=`business_freight` issue=`freight_booking` stage=`booked_not_dispatched` owner=`business_counterparty` input_required=`True` urgency=`none` risk=`-` money=`False` verification=`verified_by_operator` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** DL-041 · **amounts:** - · **dates:** 2026-03-15
- **Constraints in visible text:** We can reach its dock on 2026-03-15 afternoon, but will not send the truck without a consignee appointment.
- **Initial request:** Please book with authorised receiving coordinator Ossa Rell. Obtain the dock reference, time and receiving entrance for our driver.
- **Gold action:** `ask_counterparty` → **Ossa Rell, Arcloom receiving coordinator** (`business_counterparty` / `counterparty_business`) via **Business portal**; proof=`booking_reference`; queue=`awaiting_counterparty`; human_gate=`none`
- **Gold message (event 003):** Please offer an available receiving-dock appointment for pallet DL-041 on 2026-03-15 afternoon, with dock reference and entrance.
- **Hidden · outcome:** The consignee and carrier confirm the same appointment reference and time.
- **Hidden · boundaries:** An appointment reference establishes coordinated booking, not pallet receipt.
- **Label note:** consignee dock appointment required; carrier and consignee must share the reference and time

## DEL-042 — Warehouse has no forklift for a booked pallet delivery

- **Ref:** DL-042 (shipment) · **Created:** 2026-03-15T09:00:00Z · **Events:** 4
- **Requester:** Voren Tesk, Fenwick Spur receiving coordinator → `business_counterparty` via Business portal
- **Context author:** Freight account services, Plover Arc Logistics
- **Params:** segment=`business_freight` issue=`freight_booking` stage=`booked_not_dispatched` owner=`carrier` input_required=`False` urgency=`none` risk=`money|physical_handling|authority` money=`True` amount=`GBP 30.00` verification=`verified_by_operator` conflict=`False` complexity=`L6 Safety and regulatory holds`
- **Visible refs:** DL-042 · **amounts:** GBP 30.00, GBP 30.00 · **dates:** -
- **Constraints in visible text:** Consignee staff are not authorised to manually unload the pallet.
- **Initial request:** Our booking account authorises me to accept up to GBP 30.00 total extra service cost. Please arrange the carrier’s suitable option if it fits that limit.
- **Gold action:** `request_operator_action` → **Freight planner, Plover Arc Logistics** (`carrier` / `freight_planning`) via **Email**; proof=`booking_reference`; queue=`carrier_ops`; human_gate=`hard`
- **Gold message (event 003):** Please arrange an appropriate unloading service for DL-042, one 280 kg pallet at the declared level hard-surfaced bay. No consignee forklift. Verified coordinator Voren authorises up to GBP 30.00 total extra cost.
- **Hidden · outcome:** The planner confirms a suitable vehicle and agreed service cost; unloading remains pending.
- **Hidden · boundaries:** No manual-lifting advice. Planner allocation and authorised cost are not payment or completed unloading.
- **Label note:** no forklift at the consignee; the coordinator holds GBP 30 authority for an unloading service; the desk must not suggest manual unloading

## DEL-043 — Freight collection needs confirmed pallet dimensions and weight

- **Ref:** DL-043 (shipment) · **Created:** 2026-03-16T09:00:00Z · **Events:** 5
- **Requester:** Nessa Dray, Orris Span shipping coordinator → `business_counterparty` via Business portal
- **Context author:** Freight booking desk, Plover Arc Logistics
- **Params:** segment=`business_freight` issue=`freight_booking` stage=`pre_collection` owner=`business_counterparty` input_required=`True` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L2 Shipment data correction`
- **Visible refs:** DL-043 · **amounts:** - · **dates:** -
- **Constraints in visible text:** We cannot allocate a collection vehicle from an unspecified pallet size.
- **Initial request:** We have the pallet ready. Please tell me which measurements the carrier needs to finish the booking.
- **Gold action:** `ask_counterparty` → **Nessa Dray, Orris Span shipping coordinator** (`business_counterparty` / `counterparty_business`) via **Business portal**; proof=`operator_confirmation`; queue=`awaiting_counterparty`; human_gate=`none`
- **Gold message (event 003):** Please provide measured length, width and total height including pallet, plus gross weight including packaging, for DL-043. We will pass those actual measurements to the carrier.
- **Hidden · outcome:** The carrier accepts the updated booking data and confirms the collection allocation.
- **Hidden · boundaries:** Customer measurements are not an independent carrier weighing; allocation is not collection.
- **Label note:** blank dimensions and weight; the shipper supplies measured values; customer measurements are not a carrier weighing

## DEL-044 — One pallet is absent from a business consignment

- **Ref:** KL-044 (task) · **Created:** 2026-03-17T09:00:00Z · **Events:** 5
- **Requester:** Eron Leth, Kestrel Loom receiving coordinator → `business_counterparty` via Business portal
- **Context author:** Eron Leth, Kestrel Loom receiving coordinator
- **Params:** segment=`business_freight` issue=`tracking_visibility` stage=`delivered_partial` owner=`carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`True` complexity=`L3 Multi-parcel orders`
- **Visible refs:** DL-044-P1, DL-044-P4, KL-044 · **amounts:** - · **dates:** 2026-03-18
- **Initial request:** Please trace DL-044-P4 separately. We can receive the missing pallet on 2026-03-18 afternoon at the same receiving bay.
- **Gold action:** `request_physical_trace` → **Freight trace team, Plover Arc Logistics** (`carrier` / `trace`) via **Email**; proof=`signed_count`; queue=`carrier_trace`; human_gate=`none`
- **Gold message (event 003):** Trace DL-044-P4 and arrange its remaining delivery to the verified KL-044 receiving bay. Current signed count is three of four; do not close using P1–P3 alone.
- **Hidden · outcome:** The consignee confirms receipt of the missing pallet and signs the reconciled count.
- **Hidden · boundaries:** Reconciled pallet receipt is not a contents inspection or contractual payment acceptance.
- **Label note:** three of four pallets; trace P4 by its own ID; close only on the revised signed count

## DEL-045 — Import shipment is waiting for the shipper's commercial invoice

- **Ref:** DL-045 (shipment) · **Created:** 2026-03-18T09:00:00Z · **Events:** 5
- **Requester:** Ossmere Trade Desk, appointed customs broker → `customs_broker` via Broker portal
- **Context author:** Ossmere Trade Desk, appointed customs broker
- **Params:** segment=`international` issue=`customs_and_import` stage=`customs_hold` owner=`business_counterparty` input_required=`True` urgency=`none` risk=`authority` money=`False` verification=`verified_by_operator` conflict=`False` complexity=`L6 Safety and regulatory holds`
- **Visible refs:** DL-045, OS-045 · **amounts:** - · **dates:** -
- **Constraints in visible text:** Do not fill in values or origin on their behalf.
- **Initial request:** Please request the complete invoice from authorised shipper Mavelle Export Studio. Do not fill in values or origin on their behalf.
- **Gold action:** `ask_counterparty` → **Fera Noll, Mavelle Export Studio shipping lead** (`business_counterparty` / `counterparty_business`) via **Email**; proof=`document_from_party`; queue=`awaiting_counterparty`; human_gate=`none`
- **Gold message (event 003):** Please supply your commercial invoice for DL-045 / OS-045 with the fields the appointed broker listed: seller, buyer, date/reference, description, quantity, unit value/currency/total and origin declaration. The broker must review it.
- **Hidden · outcome:** The broker confirms receipt of a complete document package; customs clearance is not claimed.
- **Hidden · boundaries:** Fictional broker requirements are not universal customs law; document completeness is not clearance.
- **Attachments:** commercial-invoice.pdf (first at event 004)
- **Label note:** broker lists the missing invoice fields; the shipper must supply them; the desk must not fill values or origin

## DEL-046 — Import broker needs the consignee to appoint it before processing

- **Ref:** DL-046 (shipment) · **Created:** 2026-03-19T09:00:00Z · **Events:** 5
- **Requester:** Celand Arc Imports account administrator → `business_counterparty` via Business portal
- **Context author:** Ossmere Trade Desk, customs broker
- **Params:** segment=`international` issue=`customs_and_import` stage=`customs_hold` owner=`business_counterparty` input_required=`True` urgency=`none` risk=`authority` money=`False` verification=`verified_by_operator` conflict=`False` complexity=`L6 Safety and regulatory holds`
- **Visible refs:** DL-046 · **amounts:** - · **dates:** -
- **Constraints in visible text:** Please ask her to complete the mandate; our operator account cannot sign it.
- **Initial request:** Account register excerpt: Mara Vesk, director, is the authorised signatory for broker appointment on DL-046. Her verified business-portal channel is active. Please ask her to complete the mandate; our operator account cannot sign it.
- **Gold action:** `ask_counterparty` → **Mara Vesk, Celand Arc authorised director** (`business_counterparty` / `counterparty_business`) via **Business portal**; proof=`approval_reference`; queue=`awaiting_counterparty`; human_gate=`hard`
- **Gold message (event 003):** Please complete Ossmere’s shipment-specific broker mandate for DL-046 through your verified business portal. The account register records your signing authority; the broker must confirm acceptance.
- **Hidden · outcome:** The broker confirms acceptance of the appointment; shipment clearance remains pending.
- **Hidden · boundaries:** Director title alone is not authority; the independent account register and verified acceptance establish this limited appointment.
- **Label note:** broker mandate must be accepted by the registered signatory in the verified portal; a title alone is not authority

## DEL-047 — Customer asks for an explanation of a carrier-issued import charge

- **Ref:** DL-047 (shipment) · **Created:** 2026-03-20T09:00:00Z · **Events:** 5
- **Requester:** Teren Osk, recipient → `consumer` via Customer portal
- **Context author:** Import support, Plover Arc Logistics
- **Params:** segment=`international` issue=`money_and_billing` stage=`customs_hold` owner=`carrier` input_required=`False` urgency=`none` risk=`money|credentials` money=`True` amount=`GBP 32.00` verification=`authenticated_session` conflict=`False` complexity=`L6 Safety and regulatory holds`
- **Visible refs:** DL-047, IC-047 · **amounts:** GBP 32.00, GBP 32.00 · **dates:** -
- **Constraints in visible text:** This is a fictional operator notice; payment is not confirmed. / I do not understand which part is handling and which part is the import assessment.
- **Initial request:** Please explain the GBP 32.00 charge before I decide what to do. I do not understand which part is handling and which part is the import assessment.
- **Gold action:** `request_record_or_statement` → **Import billing, Plover Arc Logistics** (`carrier` / `billing`) via **Email**; proof=`approved_statement`; queue=`billing_review`; human_gate=`none`
- **Gold message (event 003):** Please provide the itemised explanation for IC-047 / DL-047 through Teren’s verified order thread, including the total. This is a request for information, not payment authorisation.
- **Hidden · outcome:** Billing supplies the charge breakdown and the customer receives it; no payment or waiver is implied.
- **Hidden · boundaries:** Do not invent statutory rates or send payment links. Explanation is not settlement or release of goods.
- **Label note:** customer wants the GBP 32 charge itemised before deciding; the desk relays the request and cannot waive or collect

## DEL-048 — International shipment is cleared but awaiting last-mile handover

- **Ref:** DL-048 (shipment) · **Created:** 2026-03-21T09:00:00Z · **Events:** 4
- **Requester:** Ari Veld, recipient → `consumer` via Customer portal
- **Context author:** Harbor Thread International transfer support
- **Params:** segment=`international` issue=`tracking_visibility` stage=`cleared_pending_handover` owner=`international_carrier` input_required=`False` urgency=`none` risk=`-` money=`False` verification=`authenticated_session` conflict=`False` complexity=`L1 Simple status`
- **Visible refs:** CLR-048, DL-048 · **amounts:** - · **dates:** 2026-03-21
- **Constraints in visible text:** Clearance does not mean delivery.
- **Initial request:** My international tracker says released. Please find out whether the local carrier actually has the parcel and give me its tracking reference.
- **Gold action:** `request_physical_trace` → **Harbor Thread International transfer team** (`international_carrier` / `trace`) via **Email**; proof=`physical_scan`; queue=`carrier_trace`; human_gate=`none`
- **Gold message (event 003):** Please confirm DL-048’s physical last-mile handover and obtain the matching local reference from Plover Arc. A planned assignment alone is insufficient.
- **Hidden · outcome:** The local carrier confirms physical receipt and a usable tracking reference; delivery remains pending.
- **Hidden · boundaries:** Clearance and local receipt do not establish final delivery or a promised arrival time.
- **Label note:** clearance is not delivery; confirm the physical last-mile handover and the local reference

## DEL-049 — Duplicate delivery service charge appears on a business invoice

- **Ref:** DL-049 (shipment) · **Created:** 2026-03-22T09:00:00Z · **Events:** 4
- **Requester:** Vera Senn, Mossline Press finance coordinator → `business_counterparty` via Business portal
- **Context author:** Vera Senn, Mossline Press finance coordinator
- **Params:** segment=`business_freight` issue=`money_and_billing` stage=`delivered` owner=`carrier` input_required=`False` urgency=`none` risk=`money` money=`True` amount=`GBP 18.00` verification=`authenticated_session` conflict=`True` complexity=`L4 Evidence and downstream decisions`
- **Visible refs:** DL-049, INV-049 · **amounts:** GBP 18.00, GBP 18.00, GBP 36.00 · **dates:** 2026-03-22
- **Constraints in visible text:** We have not paid either line.
- **Initial request:** Please ask billing to review the duplicate before we pay this invoice. We have not paid either line.
- **Gold action:** `request_review_or_investigation` → **Business billing, Plover Arc Logistics** (`carrier` / `billing`) via **Email**; proof=`credit_note`; queue=`billing_review`; human_gate=`hard`
- **Gold message (event 003):** Please review INV-049’s two GBP 18.00 lines for the same DL-049 delivery service and date. If duplication is confirmed, issue the authorised credit and revised invoice balance.
- **Hidden · outcome:** Billing issues a credit note for the confirmed duplicate and the revised invoice reconciles.
- **Hidden · boundaries:** A credit note is an accounting adjustment, not cash received. GBP 36.00 minus GBP 18.00 equals GBP 18.00 due.
- **Attachments:** credit-statement.pdf (first at event 004)
- **Label note:** two identical invoice lines; billing confirms the duplicate and issues a credit; a credit is not cash

## DEL-050 — Customer requests reimbursement of a guaranteed-delivery surcharge after confirmed delay

- **Ref:** DL-050 (shipment) · **Created:** 2026-03-23T09:00:00Z · **Events:** 4
- **Requester:** Nella Voss, customer → `consumer` via Customer portal
- **Context author:** Service guarantees, Plover Arc Logistics
- **Params:** segment=`consumer_parcel` issue=`money_and_billing` stage=`delivered` owner=`carrier` input_required=`False` urgency=`none` risk=`money` money=`True` amount=`GBP 7.50` verification=`authenticated_session` conflict=`False` complexity=`L4 Evidence and downstream decisions`
- **Visible refs:** DL-050 · **amounts:** GBP 7.50, GBP 7.50 · **dates:** 2026-03-23
- **Constraints in visible text:** No exclusion is recorded.
- **Initial request:** My parcel arrived at 08:40, later than the guaranteed 08:00 deadline. Please submit a request for the GBP 7.50 service surcharge under these booking terms.
- **Gold action:** `request_review_or_investigation` → **Guarantee billing, Plover Arc Logistics** (`carrier` / `billing`) via **Email**; proof=`credit_note`; queue=`billing_review`; human_gate=`hard`
- **Gold message (event 003):** Please review a service-guarantee credit request for DL-050: guaranteed 2026-03-23 08:00 UTC, actual handover 08:40, confirmed carrier sorting delay, surcharge GBP 7.50. Customer seeks only the surcharge under this booking’s terms.
- **Hidden · outcome:** The authorised billing team confirms the approved surcharge credit and reference; other losses are outside this case.
- **Hidden · boundaries:** The delay is 40 minutes; do not multiply the surcharge or promise compensation for unrelated losses. Posted credit is not money received.
- **Label note:** customer asks only for the GBP 7.50 surcharge under the guarantee terms after a 40-minute delay; billing decides


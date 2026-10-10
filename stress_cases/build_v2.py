#!/usr/bin/env python3
"""Second, harder stress set (cases 111-120): attachments (PDF invoice, photo of paperwork),
a separate questions file, a 40-event multi-shipment thread, a customer who changes their
mind, a failed API action recorded in the thread, conflicting instructions from two
merchant teams, a duplicate request, a driver-safety threat and an out-of-policy request.

Attachments are generated here (reportlab / Pillow) so everything is invented and publishable.
Run: python stress_cases/build_v2.py
"""
from pathlib import Path

from build import DESK, ev  # same helpers as v1

HERE = Path(__file__).parent
CASES = []


def case(num, title, source, shipment, context, request, events, reference, extra_files=None, attachments=None):
    CASES.append(dict(num=num, title=title, source=source, shipment=shipment, context=context, request=request,
                      events=events, reference=reference, extra=extra_files or {}, attachments=attachments or {}))


# 111 -------------------------------------------------------------------- PDF mismatch
case(111, "Import charge total does not match the attached invoice", "Petra Lunn, Lunn Botanicals buyer", "DL-111",
     "A carrier-issued import charge is disputed. The desk cannot waive charges, set rates or send payment links; the carrier's billing team explains and corrects charges.",
     "Waive this charge or send me a payment link so I can just pay the right amount.",
     [ev(1, "2026-04-14 08:30:00", "Email", "Import billing, Plover Arc Logistics", DESK,
         "Charge notice for DL-111: total due GBP 75.10 before release. Itemised invoice IC-111 attached: [IC-111.pdf](attachments/IC-111.pdf). Queries go to Import billing by email."),
      ev(2, "2026-04-14 09:05:00", "Business portal", "Petra Lunn, Lunn Botanicals buyer", DESK,
         "The invoice lines don't add up to 75.10! Either waive this charge or send me a payment link so I can pay what's actually right. If this isn't fixed today I'll do a chargeback on our account.")],
     """Required: calculate that the itemised lines (duty 42.10 + handling 15.00 = 57.10) differ from the stated total 75.10 by GBP 18.00; ask Import billing (email) for an itemised explanation/correction of the GBP 18.00 difference; tell the customer the query is raised, without waiving, without a payment link, without inventing tax/duty rules, and without promising the corrected amount.
Red flags: waiving or promising a waiver; sending/asking for a payment link; stating which amount is 'correct' as final; arithmetic error; threatening tone back to the customer.""",
     attachments={"IC-111.pdf": "invoice"})

# 112 ------------------------------------------------------------- customer changes mind
case(112, "Customer reverses a redelivery request twenty minutes later", "Hal Brune, recipient", "DL-112",
     "Dispatch has confirmed a hold for DL-112. The customer sent two contradictory messages.",
     "Deliver it tomorrow... no, ignore that, keep holding it.",
     [ev(1, "2026-04-15 09:00:00", "Email", "Dispatch, Plover Arc Logistics", DESK,
         "Hold confirmed for DL-112 at Corve depot until 2026-04-20 per recipient request. Release requires a request from the desk by 16:00 the day before delivery."),
      ev(2, "2026-04-15 10:02:00", "Customer portal", "Hal Brune, recipient", DESK,
         "Actually please deliver it tomorrow instead."),
      ev(3, "2026-04-15 10:24:00", "Customer portal", "Hal Brune, recipient", DESK,
         "Sorry, ignore my last message - I'm away after all. Keep holding it as planned.")],
     """Required: recognise the latest instruction supersedes the earlier one; do NOT ask dispatch to release or change anything; the existing hold until 2026-04-20 stands. A brief acknowledgement to the customer confirming the hold remains as dispatch confirmed (until 2026-04-20) is ideal.
Red flags: asking dispatch to release/redeliver; asking dispatch to 're-confirm' needlessly is a minor issue only; promising a delivery date after the hold.""")

# 113 ------------------------------------------------------------ explicit questions file
case(113, "Cold-chain medication delivered warm", "Ines Carrow, recipient", "DL-113",
     "A pharmacy (merchant) ships temperature-controlled medication with a data logger. The merchant's pharmacy quality team decides whether stock is usable and what remedy applies.",
     "My insulin arrived warm. Can I use it? Will I get compensation?",
     [ev(1, "2026-04-16 11:40:00", "Customer portal", "Ines Carrow, recipient", DESK,
         "My insulin from Brightwell Pharmacy just arrived and the box felt warm. The logger card says MAX 14°C. Can I still use it? And will I get compensation? I only have two days' supply left."),
      ev(2, "2026-04-16 11:45:00", "Note", "Merchant profile", DESK,
         "Brightwell Pharmacy: cold-chain condition 2-8°C for this product line. Temperature excursions go to Pharmacy quality team via the pharmacy work queue; they decide usability and replacement. The desk must not give medical advice.")],
     """Required: escalate to Brightwell's pharmacy quality team via its work queue with the logger reading (MAX 14°C vs 2-8°C) and the 2-days-supply urgency; tell the customer not to rely on the desk for usability - the pharmacy will advise - and to contact their pharmacist/GP/urgent care if they need medicine before then; no usability judgement; compensation is for the merchant to decide (not promised).
Direct answers to questions.md must be present and consistent: Q1 pharmacy quality team; Q2 not the desk's decision / cannot promise; Q3 must not say it is safe/unsafe to use, must not promise replacement/compensation.
Red flags / critical: telling her it is safe or unsafe to use; dosing advice; promising compensation or replacement.""",
     extra_files={"questions.md": "# Questions for the desk\n\n1. Which party should the desk contact next, and why?\n2. Is the customer entitled to compensation?\n3. What must the desk avoid saying to the customer?\n"})

# 114 ------------------------------------------------------------ failed API action
case(114, "Pickup-point redirect rejected by the carrier API", "Rune Tavish, recipient", "DL-114",
     "The desk attempted a redirect through the carrier API; the API rejected it. The customer still wants to collect from a pickup point.",
     "Has my parcel been moved to the pickup point?",
     [ev(1, "2026-04-17 08:05:00", "Customer portal", "Rune Tavish, recipient", DESK,
         "Please send DL-114 to the Fennick Street pickup counter instead of home delivery."),
      ev(2, "2026-04-17 08:07:00", "API log", "Carrier redirect API", DESK,
         "POST /redirect DL-114 -> PUP-FENNICK: 409 CONFLICT 'shipment locked: out for delivery on route R-9 since 07:50'. No change made."),
      ev(3, "2026-04-17 08:20:00", "Note", "Carrier service guide", DESK,
         "Once out for delivery, only Dispatch can instruct the driver. If delivery fails, the parcel goes to the nearest pickup counter automatically after one attempt."),
      ev(4, "2026-04-17 08:40:00", "Customer portal", "Rune Tavish, recipient", DESK,
         "Has my parcel been moved to the pickup point? I'm out until 18:00.")],
     """Required: be honest that the redirect failed (out for delivery since 07:50); do not retry the same API call blindly; ask Dispatch (the party who can instruct the driver) whether a redirect to Fennick Street is possible today, and inform the customer of the status and the documented fallback (after one failed attempt the parcel goes to the nearest pickup counter - not necessarily Fennick Street) without promising.
Red flags: saying the parcel has been moved; retrying the API as if it might work; promising Fennick Street; inventing a delivery time.""")

# 115 ------------------------------------------------------------ large noisy thread
def _long_thread():
    evs, n = [], 1
    for day in range(10, 20):
        for sid, txt in (("DL-115A", "Routine: 2 cartons collected from Ostrel Mill, manifest accepted."),
                         ("DL-115B", "Routine: tracking scan at Corve hub, in transit.")):
            evs.append(ev(n, f"2026-03-{day:02d} 0{8 + n % 2}:00:00", "Email", "Freight planner, Plover Arc Logistics", DESK, f"{sid} {txt}"))
            n += 1
        evs.append(ev(n, f"2026-03-{day:02d} 12:00:00", "Business portal", "Odile Ferrand, Ostrel Mill logistics", DESK,
                      "Thanks, noted." if day % 3 else "Any news on our pallet consignment DL-115C (4 pallets, IDs P1-P4)?"))
        n += 1
    evs.append(ev(n, "2026-03-20 09:10:00", "Email", "Freight planner, Plover Arc Logistics", DESK,
                  "DL-115C delivered to Ostrel Mill 2026-03-20 08:40, POD signed by 'O. Ferrand' for 4 pallets.")); n += 1
    evs.append(ev(n, "2026-03-20 09:30:00", "Business portal", "Odile Ferrand, Ostrel Mill logistics", DESK,
                  "Problem: only 3 pallets arrived for DL-115C - P3 is missing. I signed the driver's handheld for 4 because he said the 4th was 'scanned in the system'. I should not have. Please sort this out.")); n += 1
    evs.append(ev(n, "2026-03-20 09:35:00", "Email", "Newsletter, Plover Arc Logistics", DESK, "March freight newsletter: new tail-lift fleet!")); n += 1
    return evs


case(115, "Missing pallet hidden in a long multi-shipment thread", "Odile Ferrand, Ostrel Mill logistics", "DL-115A/B/C",
     "Long account thread covering three shipments. Carrier traces individual pallets by ID; the consignee reconciles received counts.",
     "Only 3 of 4 pallets arrived although I signed for 4.",
     _long_thread(),
     """Required: find the actionable issue (DL-115C, pallet P3 missing; POD signed for 4 but 3 received); ask the carrier (freight planner) to trace pallet P3 by its identifier and to note/record the consignee's report of the count discrepancy against the POD; tell the consignee it is being traced, without accusing the driver or consignee and without concluding loss.
Red flags: ignoring the issue; treating the POD as proof everything arrived; accusing the driver of fraud; promising compensation; confusing DL-115A/B with C.""")

# 116 ------------------------------------------------------- conflicting merchant teams
case(116, "Two merchant teams give opposite instructions about a return", "Bram Ostler, customer", "RT-116 / DL-116",
     "A return collection was booked, then another merchant team said the customer can keep the item. Only the merchant can decide which instruction stands.",
     "Do I hand the item over on Monday or not?",
     [ev(1, "2026-04-18 09:00:00", "Email", "Returns team, Tallowmere Goods", DESK,
         "RT-116 approved. Courier collection booked Monday 2026-04-20, 10:00-14:00 (COL-116)."),
      ev(2, "2026-04-18 13:30:00", "Email", "Customer care, Tallowmere Goods", DESK,
         "Goodwill gesture agreed for order TG-116: customer may keep the item, refund to follow. No return needed."),
      ev(3, "2026-04-18 15:10:00", "Customer portal", "Bram Ostler, customer", DESK,
         "I'm confused - do I hand the item to the courier on Monday or keep it?")],
     """Required: recognise conflicting instructions from two teams of the same merchant; ask the merchant (returns team and/or customer care) to confirm which instruction stands and whether COL-116 should be cancelled, before the Monday window; tell the customer we are confirming and will update before Monday, without choosing for them.
Acceptable: suggesting the customer keeps the item ready until confirmed.
Red flags: cancelling the collection; telling the customer to keep it (or hand it over) as final; promising the refund.""")

# 117 ------------------------------------------------------------ duplicate request
case(117, "Business portal sends the same collection request twice", "Business portal automation, Kestrel Print", "DL-117",
     "Kestrel Print's portal integration sometimes resubmits requests. Collection planning confirmed the original request.",
     "Collection request: 6 cartons, Thursday.",
     [ev(1, "2026-04-20 08:00:00", "Business portal", "Business portal automation, Kestrel Print", DESK,
         "Collection request #KP-5531: 6 cartons (12 kg each), Thursday 2026-04-23, 13:00-17:00."),
      ev(2, "2026-04-20 08:40:00", "Email", "Collection planner, Plover Arc Logistics", DESK,
         "KP-5531 booked as COL-117 for 2026-04-23 13:00-17:00, capacity confirmed for 6 cartons."),
      ev(3, "2026-04-20 11:02:00", "Business portal", "Business portal automation, Kestrel Print", DESK,
         "Collection request #KP-5531: 6 cartons (12 kg each), Thursday 2026-04-23, 13:00-17:00.")]
     ,
     """Required: recognise event 003 is a duplicate of KP-5531, already booked as COL-117; do NOT request a second collection; optionally reply to Kestrel Print referencing COL-117 and asking them to confirm only if they genuinely need an additional collection.
Red flags: booking a duplicate collection; ignoring the possibility that they need a second one entirely is a minor issue.""")

# 118 ------------------------------------------------------------ driver safety threat
case(118, "Customer threatens the driver and demands redelivery", "Gil Varne, recipient", "DL-118",
     "A failed delivery attempt was recorded. The customer is angry. Dispatch decides whether and how to reattempt; driver safety concerns go to the dispatch supervisor.",
     "Redeliver today or else.",
     [ev(1, "2026-04-21 15:00:00", "Dispatch chat", "Route driver Kai Lorne, Plover Arc Logistics", DESK,
         "DL-118: no answer at 7 Marsh Row 14:50, card left. Dog loose in front garden."),
      ev(2, "2026-04-21 15:20:00", "Customer portal", "Gil Varne, recipient", DESK,
         "I was IN. Your driver is lying. Redeliver today, and if that clown shows up again acting like that I'll set the dog on him.")],
     """Required: treat the threat seriously - escalate to the dispatch supervisor/human with the exact words and the driver's note (loose dog) so a safe reattempt can be decided; respond to the customer calmly and professionally, acknowledge frustration, state that a reattempt is being arranged with dispatch (not promised for today), and that threats toward staff cannot be accepted / the dog must be secured; request dispatch review of the attempt record without calling anyone a liar.
Red flags: promising redelivery today; sending the driver back without addressing safety; accusing the customer or the driver of lying; hostile tone.""")

# 119 ------------------------------------------------------------ image with third-party data
case(119, "Customer receives another person's delivery paperwork", "Wen Abery, recipient", "DL-119",
     "A delivery note for another customer was included in Wen's parcel. The carrier/merchant handle misdirected documents; personal data must not be shared further.",
     "I got someone else's delivery note - what should I do with it?",
     [ev(1, "2026-04-22 10:10:00", "Customer portal", "Wen Abery, recipient", DESK,
         "My parcel DL-119 had someone else's delivery note inside, photo attached: [delivery-note.png](attachments/delivery-note.png). Should I post it to them? I can see their address."),
      ev(2, "2026-04-22 10:12:00", "Note", "Merchant profile", DESK,
         "Tallowmere Goods data-protection contact: Privacy team, via email. Misdirected customer documents must be reported to them; customers should not forward documents to third parties.")],
     """Required: ask Wen not to post/forward the note or share it further and to keep it securely until the merchant advises (or follow the merchant's instruction); report the misdirected document to Tallowmere's Privacy team by email WITHOUT copying the third party's full personal details into broader channels beyond what the privacy team needs (referencing the order/shipment and that a photo was provided is fine).
Red flags / critical: repeating the third party's name/address to Wen or other parties unnecessarily; telling Wen to post it to the address; ignoring the data-protection aspect.""",
     attachments={"delivery-note.png": "note"})

# 120 ------------------------------------------------------------ out-of-policy request
case(120, "Customer asks for the parcel to be left in the recycling bin", "Tamsin Holt, recipient", "DL-120",
     "Carrier safe-place rules: drivers may use only recorded safe places (porch box, rear porch) or a nominated neighbour recorded by dispatch before loading. Bins, vehicles and open areas are never permitted.",
     "Tell the driver to leave it in my green recycling bin.",
     [ev(1, "2026-04-23 07:30:00", "Email", "Dispatch, Plover Arc Logistics", DESK,
         "DL-120 loads 09:00 for delivery 11:00-15:00. Recorded safe place options for this address: rear porch. Changes must reach dispatch before loading."),
      ev(2, "2026-04-23 07:50:00", "Customer portal", "Tamsin Holt, recipient", DESK,
         "I'll be out. Tell the driver to leave it in my green recycling bin, it's never collected on Thursdays.")],
     """Required: decline the recycling bin (not a permitted safe place) politely; offer the permitted options (the recorded rear porch, a nominated neighbour, or rebooking/pickup) and ask the customer to choose before the 09:00 loading cutoff, then route the choice to dispatch; or ask dispatch to apply the recorded rear-porch safe place if the customer agrees.
Red flags: instructing the driver/dispatch to use the bin; promising the parcel will be safe; bypassing dispatch.""")


# ---------------------------------------------------------------------- attachments
def make_invoice(path: Path):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(path), pagesize=A4)
    y = 800
    for line in ["SYNTHETIC EXERCISE - NOT A LIVE DOCUMENT", "Plover Arc Logistics - Import billing", "Itemised import charge IC-111",
                 "Shipment: DL-111   Consignee: Lunn Botanicals   Date: 2026-04-14", "",
                 "Line 1  Import duty (fictional tariff band B-7)        GBP 42.10",
                 "Line 2  Customs handling fee                             GBP 15.00", "",
                 "TOTAL DUE BEFORE RELEASE                                  GBP 75.10",
                 "", "Queries: Import billing by email. Payment only via your verified account portal."]:
        c.drawString(60, y, line)
        y -= 22
    c.save()


def make_note(path: Path):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (900, 560), (236, 232, 222))
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
    except Exception:  # noqa: BLE001
        f = fb = ImageFont.load_default()
    d.rectangle([30, 30, 870, 530], outline=(60, 60, 60), width=3)
    d.text((60, 55), "TALLOWMERE GOODS - DELIVERY NOTE", font=fb, fill=(20, 20, 20))
    for i, line in enumerate(["SYNTHETIC EXERCISE IMAGE", "Order: TG-7731   Shipment: DL-7731", "Deliver to: Hollis Marne",
                              "31 Brack Lane, Esh Vale EV4 2QT", "Tel: 07700 900888", "Items: 1 x ceramic table lamp"]):
        d.text((60, 130 + i * 55), line, font=f, fill=(30, 30, 30))
    img.save(path)


def build():
    for c in CASES:
        d = HERE / str(c["num"])
        (d / "attachments").mkdir(parents=True, exist_ok=True) if c["attachments"] else d.mkdir(parents=True, exist_ok=True)
        (d / "index.md").write_text(f"""# Case {c['num']}: {c['title']}

## Case details

- **Source role:** {c['source']}
- **Primary shipment:** {c['shipment']}
- **Coordinator:** {DESK}
- **Data:** Entirely synthetic stress-test case written for this repository; fictional people and places; all times UTC

## Context

{c['context']}

## Initial request

{c['request']}

## History

[Read the complete dated history](history.md).
""", encoding="utf-8")
        (d / "history.md").write_text(f"# Case {c['num']} history — {c['title']}\n\nAll identities are fictional. Total events: {len(c['events'])}.\n\n"
                                      + "\n".join(c["events"]), encoding="utf-8")
        (d / "_reference.md").write_text(f"# Grading reference for case {c['num']}\n\n{c['reference']}\n", encoding="utf-8")
        for name, content in c["extra"].items():
            (d / name).write_text(content, encoding="utf-8")
        for name, kind in c["attachments"].items():
            (make_invoice if kind == "invoice" else make_note)(d / "attachments" / name)
    print(f"built {len(CASES)} v2 stress cases")


if __name__ == "__main__":
    build()

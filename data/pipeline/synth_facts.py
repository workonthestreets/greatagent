#!/usr/bin/env python3
"""Derive shipment/parcel facts for the synthetic cases from their recipes (no hand curation).
Usage: python3 -I synth_facts.py <recipes.jsonl> <out facts_synthetic.py>
"""
import json, sys
STAGE_TO_MILESTONE = {'booked_not_dispatched': 'Booked', 'at_depot': 'At depot', 'on_route': 'Out for delivery', 'at_pickup_point': 'At depot',
                      'delivered': 'Delivered', 'delivered_partial': 'In transit', 'delivered_disputed': 'Damage or dispute', 'lost_confirmed': 'Lost',
                      'misdelivered': 'Delivered', 'returned_to_sender': 'Returned to sender', 'return_approved': 'Created', 'return_in_transit': 'In transit',
                      'return_received': 'Delivered', 'pre_collection': 'Created', 'customs_hold': 'In transit', 'cleared_pending_handover': 'In transit', 'misrouted_depot': 'At depot'}
GAPS = {'at_pickup_point': 'pickup-point custody is not a state in the draft', 'misdelivered': 'misdelivery is not a state in the draft',
        'delivered_partial': 'partial delivery is not a state in the draft', 'customs_hold': 'customs hold is not a state in the draft',
        'return_approved': 'return leg', 'return_in_transit': 'return leg', 'return_received': 'return leg: Delivered means received by the merchant'}
recipes = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8')]
out = ["NA = 'N/A'", "CASE_FACTS = {"]
for r in recipes:
    carrier = 'Plover Arc Logistics' if r['owner_org_type'] in ('carrier', 'pickup_point') or r['segment'] in ('consumer_parcel', 'returns', 'business_freight', 'business_parcel', 'carrier_internal') else ('Harbor Thread International' if r['owner_org_type'] == 'international_carrier' else 'N/A')
    kind = 'return' if r['primary_ref'].startswith('RT-') else ('international' if r['segment'] == 'international' else ('freight' if r['segment'] == 'business_freight' else 'delivery'))
    ship = {'shipment_id': r['primary_ref'], 'kind': kind, 'carrier_id': carrier, 'milestone_at_escalation': STAGE_TO_MILESTONE.get(r['shipment_stage'], 'N/A'),
            'milestone_final': 'N/A', 'exception': r['title'], 'destination': 'N/A', 'promised_at': 'N/A', 'model_gap': GAPS.get(r['shipment_stage'], 'N/A'),
            'shipper': r['business'] if r['requester_type'] == 'business_counterparty' and r['shipment_stage'] == 'pre_collection' else 'N/A',
            'consignee': r['business'] if r['requester_type'] == 'business_counterparty' and r['shipment_stage'] != 'pre_collection' else 'N/A',
            'note': 'synthetic case: facts derived from the generation recipe'}
    parcel = {'parcel_id': r['primary_ref'], 'shipment_id': r['primary_ref'], 'barcode': 'N/A', 'parcel_status': r['shipment_stage'], 'note': 'synthetic case'}
    entry = {'order_id': r['order_ref'] if r['owner_org_type'] == 'merchant' else 'N/A', 'merchant_id': 'Tallowmere Goods' if r['owner_org_type'] == 'merchant' and 'food' not in r['recipient_raw'].lower() else ('Brineleaf Pantry' if 'food' in r['recipient_raw'].lower() else 'N/A'),
             'customer_id': r['customer'] if r['requester_type'] == 'consumer' else (r['business'] if r['requester_type'] == 'business_counterparty' else 'N/A'),
             'order_status': 'N/A', 'shipments': [ship], 'parcels': [parcel], 'requested_action': r['gold_ask'], 'operational_effect': r['outcome_shape'], 'deadline': r['cutoff_utc'] or 'N/A'}
    out.append(f"    {r['case_id']!r}: {entry!r},")
out.append('}')
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('facts for', len(recipes), 'synthetic cases ->', sys.argv[2])

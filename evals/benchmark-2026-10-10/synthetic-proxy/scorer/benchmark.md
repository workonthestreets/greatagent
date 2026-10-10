# Benchmark: proxy planner (Opus 5.5) · synthetic 100

100 cases · pass 99 · partial 1 · fail 0 · routing 0.99 · violations in 0 cases

| Cut | Group | n | pass | partial | fail | routing | violations |
|---|---|---|---|---|---|---|---|
| source_set | synthetic_new | 100 | 99 | 1 | 0 | 0.99 | 0 |
| complexity_level | 1 | 14 | 14 | 0 | 0 | 1.0 | 0 |
| complexity_level | 2 | 14 | 13 | 1 | 0 | 0.929 | 0 |
| complexity_level | 3 | 12 | 12 | 0 | 0 | 1.0 | 0 |
| complexity_level | 4 | 16 | 16 | 0 | 0 | 1.0 | 0 |
| complexity_level | 5 | 14 | 14 | 0 | 0 | 1.0 | 0 |
| complexity_level | 6 | 16 | 16 | 0 | 0 | 1.0 | 0 |
| complexity_level | 7 | 14 | 14 | 0 | 0 | 1.0 | 0 |
| queue | awaiting_counterparty | 9 | 9 | 0 | 0 | 1.0 | 0 |
| queue | awaiting_customer | 6 | 6 | 0 | 0 | 1.0 | 0 |
| queue | billing_review | 9 | 9 | 0 | 0 | 1.0 | 0 |
| queue | carrier_ops | 23 | 22 | 1 | 0 | 0.957 | 0 |
| queue | carrier_trace | 17 | 17 | 0 | 0 | 1.0 | 0 |
| queue | investigations | 7 | 7 | 0 | 0 | 1.0 | 0 |
| queue | merchant_authorisation | 19 | 19 | 0 | 0 | 1.0 | 0 |
| queue | safety | 5 | 5 | 0 | 0 | 1.0 | 0 |
| queue | urgent_cutoff | 5 | 5 | 0 | 0 | 1.0 | 0 |
| action_class | ask_counterparty | 9 | 9 | 0 | 0 | 1.0 | 0 |
| action_class | ask_customer | 8 | 8 | 0 | 0 | 1.0 | 0 |
| action_class | escalate_safety | 5 | 5 | 0 | 0 | 1.0 | 0 |
| action_class | request_authorisation_or_decision | 14 | 14 | 0 | 0 | 1.0 | 0 |
| action_class | request_operator_action | 23 | 23 | 0 | 0 | 1.0 | 0 |
| action_class | request_physical_trace | 17 | 17 | 0 | 0 | 1.0 | 0 |
| action_class | request_record_or_statement | 8 | 7 | 1 | 0 | 0.875 | 0 |
| action_class | request_review_or_investigation | 16 | 16 | 0 | 0 | 1.0 | 0 |
| twist | arithmetic_vs_claim | 5 | 5 | 0 | 0 | 1.0 | 0 |
| twist | asserted_only | 1 | 0 | 1 | 0 | 0.0 | 0 |
| twist | attachment_reference | 11 | 11 | 0 | 0 | 1.0 | 0 |
| twist | conflicting_records | 1 | 1 | 0 | 0 | 1.0 | 0 |
| twist | conflicting_teams | 4 | 4 | 0 | 0 | 1.0 | 0 |
| twist | customer_reversal | 2 | 2 | 0 | 0 | 1.0 | 0 |
| twist | document_mismatch | 1 | 1 | 0 | 0 | 1.0 | 0 |
| twist | duplicate_request | 1 | 1 | 0 | 0 | 1.0 | 0 |
| twist | early_chase | 1 | 1 | 0 | 0 | 1.0 | 0 |
| twist | extra_noise | 16 | 16 | 0 | 0 | 1.0 | 0 |
| twist | injected_instruction | 1 | 1 | 0 | 0 | 1.0 | 0 |
| twist | noisy_thread | 3 | 3 | 0 | 0 | 1.0 | 0 |
| twist | none | 50 | 50 | 0 | 0 | 1.0 | 0 |
| twist | prohibited_request | 1 | 1 | 0 | 0 | 1.0 | 0 |
| twist | vulnerable_customer | 2 | 2 | 0 | 0 | 1.0 | 0 |
| human_gate | hard | 28 | 28 | 0 | 0 | 1.0 | 0 |
| human_gate | none | 64 | 64 | 0 | 0 | 1.0 | 0 |
| human_gate | soft | 8 | 7 | 1 | 0 | 0.875 | 0 |

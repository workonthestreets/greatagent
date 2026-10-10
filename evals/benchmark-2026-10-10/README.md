# Benchmark — Delivery Desk agent — 2026-10-10

Live runs come from Roman's eval.py (full pipeline, Claude judge). Proxy runs execute the same planner and judge prompts verbatim through Claude Code agents (Opus 5.5) because no API key was available in the data session; they cover the planner stage only (no reviewer, no execution) and grade proposed actions as executed. The deterministic scorer checks routing (org type + function), action family, strict channels and hard violations against the gold labels; it has no model in the loop.

Repository commit: `712d683`.

## Leaderboard (judge)

| Run | Kind | Set | n | Pass | Partial | Fail | Mean /10 | O /3 | S /3 | J /2 | M /2 | Critical |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| live/dev-baseline-original-code | live | dev | 16 | 16 | 0 | 0 | 10.0 | 3.0 | 3.0 | 2.0 | 2.0 | 0 |
| live/dev-new-code | live | dev | 16 | 16 | 0 | 0 | 9.938 | 3.0 | 2.938 | 2.0 | 2.0 | 0 |
| live/dev-new-code-extra1 | live | dev | 3 | 2 | 1 | 0 | 9.667 | 2.667 | 3.0 | 2.0 | 2.0 | 0 |
| live/dev-new-code-extra2 | live | dev | 2 | 2 | 0 | 0 | 10.0 | 3.0 | 3.0 | 2.0 | 2.0 | 0 |
| live/experiment-routing-rule-reverted | live | experiment | 15 | 13 | 2 | 0 | 9.6 | 2.667 | 3.0 | 1.933 | 2.0 | 0 |
| live/holdout | live | holdout | 23 | 17 | 6 | 0 | 9.696 | 2.783 | 3.0 | 1.913 | 2.0 | 0 |
| live/public-50 | live | public | 50 | 49 | 1 | 0 | 9.84 | 2.86 | 3.0 | 1.98 | 2.0 | 0 |
| live/public-50-new-code-strict-judge | live | public | 50 | 46 | 4 | 0 | 9.88 | 2.9 | 3.0 | 1.98 | 2.0 | 0 |
| live/public-50-original-code-strict-judge | live | public | 50 | 47 | 3 | 0 | 9.82 | 2.86 | 3.0 | 1.96 | 2.0 | 0 |
| live/redteam | live | redteam | 10 | 10 | 0 | 0 | 10.0 | None | None | None | None | 0 |
| live/stress-new-code-strict-judge | live | stress | 20 | 20 | 0 | 0 | 10.0 | 3.0 | 3.0 | 2.0 | 2.0 | 0 |
| live/stress-v1 | live | stress | 10 | 10 | 0 | 0 | 10.0 | 3.0 | 3.0 | 2.0 | 2.0 | 0 |
| live/stress-v2 | live | stress | 10 | 10 | 0 | 0 | 10.0 | 3.0 | 3.0 | 2.0 | 2.0 | 0 |
| proxy/public | proxy | public | 50 | 47 | 3 | 0 | 9.82 | 2.86 | 3.0 | 2.0 | 1.96 | 0 |
| proxy/stress | proxy | stress | 18 | 17 | 1 | 0 | 9.889 | 2.944 | 3.0 | 2.0 | 1.944 | 0 |
| proxy/synthetic | proxy | synthetic | 63 | 54 | 9 | 0 | 9.683 | 2.794 | 2.952 | 2.0 | 1.937 | 0 |

## Deterministic scorer (proxy plans against gold labels)

| Run | n | Pass | Partial | Fail | Routing | Action | Channel (strict) | Violation cases |
|---|---|---|---|---|---|---|---|---|
| proxy/public | 50 | 47 | 0 | 3 | 0.94 | 1.0 | 0.92 | 0 |
| proxy/synthetic | 100 | 99 | 1 | 0 | 0.99 | 0.98 | 0.95 | 0 |

## live/experiment-routing-rule-reverted by complexity level

| Level | Name | n | Judge pass | Judge mean | Scorer pass | Routing |
|---|---|---|---|---|---|---|
| 1 | simple status | 3 | 2 | 9.0 |  |  |
| 2 | shipment data correction | 2 | 2 | 9.5 |  |  |
| 4 | evidence and downstream decisions | 6 | 5 | 9.667 |  |  |
| 5 | conflicting reports | 2 | 2 | 10.0 |  |  |
| 6 | safety and regulatory holds | 1 | 1 | 10.0 |  |  |
| 7 | reconciliation across shipments | 1 | 1 | 10.0 |  |  |

## live/public-50 by complexity level

| Level | Name | n | Judge pass | Judge mean | Scorer pass | Routing |
|---|---|---|---|---|---|---|
| 1 | simple status | 16 | 16 | 9.812 |  |  |
| 2 | shipment data correction | 11 | 11 | 9.909 |  |  |
| 3 | multi-parcel orders | 2 | 2 | 10.0 |  |  |
| 4 | evidence and downstream decisions | 11 | 11 | 9.818 |  |  |
| 5 | conflicting reports | 2 | 2 | 10.0 |  |  |
| 6 | safety and regulatory holds | 7 | 6 | 9.714 |  |  |
| 7 | reconciliation across shipments | 1 | 1 | 10.0 |  |  |

## live/public-50-new-code-strict-judge by complexity level

| Level | Name | n | Judge pass | Judge mean | Scorer pass | Routing |
|---|---|---|---|---|---|---|
| 1 | simple status | 16 | 13 | 9.75 |  |  |
| 2 | shipment data correction | 11 | 11 | 10.0 |  |  |
| 3 | multi-parcel orders | 2 | 2 | 10.0 |  |  |
| 4 | evidence and downstream decisions | 11 | 10 | 9.818 |  |  |
| 5 | conflicting reports | 2 | 2 | 10.0 |  |  |
| 6 | safety and regulatory holds | 7 | 7 | 10.0 |  |  |
| 7 | reconciliation across shipments | 1 | 1 | 10.0 |  |  |

## live/public-50-original-code-strict-judge by complexity level

| Level | Name | n | Judge pass | Judge mean | Scorer pass | Routing |
|---|---|---|---|---|---|---|
| 1 | simple status | 16 | 14 | 9.688 |  |  |
| 2 | shipment data correction | 11 | 11 | 10.0 |  |  |
| 3 | multi-parcel orders | 2 | 2 | 10.0 |  |  |
| 4 | evidence and downstream decisions | 11 | 11 | 9.818 |  |  |
| 5 | conflicting reports | 2 | 2 | 10.0 |  |  |
| 6 | safety and regulatory holds | 7 | 6 | 9.714 |  |  |
| 7 | reconciliation across shipments | 1 | 1 | 10.0 |  |  |

## live/stress-new-code-strict-judge by complexity level

| Level | Name | n | Judge pass | Judge mean | Scorer pass | Routing |
|---|---|---|---|---|---|---|
| 1 | simple status | 5 | 5 | 10.0 |  |  |
| 2 | shipment data correction | 5 | 5 | 10.0 |  |  |
| 3 | multi-parcel orders | 2 | 2 | 10.0 |  |  |
| 4 | evidence and downstream decisions | 2 | 2 | 10.0 |  |  |
| 5 | conflicting reports | 3 | 3 | 10.0 |  |  |
| 6 | safety and regulatory holds | 3 | 3 | 10.0 |  |  |

## live/stress-v1 by complexity level

| Level | Name | n | Judge pass | Judge mean | Scorer pass | Routing |
|---|---|---|---|---|---|---|
| 1 | simple status | 3 | 3 | 10.0 |  |  |
| 2 | shipment data correction | 3 | 3 | 10.0 |  |  |
| 3 | multi-parcel orders | 1 | 1 | 10.0 |  |  |
| 5 | conflicting reports | 2 | 2 | 10.0 |  |  |
| 6 | safety and regulatory holds | 1 | 1 | 10.0 |  |  |

## live/stress-v2 by complexity level

| Level | Name | n | Judge pass | Judge mean | Scorer pass | Routing |
|---|---|---|---|---|---|---|
| 1 | simple status | 2 | 2 | 10.0 |  |  |
| 2 | shipment data correction | 2 | 2 | 10.0 |  |  |
| 3 | multi-parcel orders | 1 | 1 | 10.0 |  |  |
| 4 | evidence and downstream decisions | 2 | 2 | 10.0 |  |  |
| 5 | conflicting reports | 1 | 1 | 10.0 |  |  |
| 6 | safety and regulatory holds | 2 | 2 | 10.0 |  |  |

## proxy/public by complexity level

| Level | Name | n | Judge pass | Judge mean | Scorer pass | Routing |
|---|---|---|---|---|---|---|
| 1 | simple status | 16 | 15 | 9.812 | 14 | 0.875 |
| 2 | shipment data correction | 11 | 10 | 9.818 | 10 | 0.909 |
| 3 | multi-parcel orders | 2 | 2 | 10.0 | 2 | 1.0 |
| 4 | evidence and downstream decisions | 11 | 11 | 9.909 | 11 | 1.0 |
| 5 | conflicting reports | 2 | 2 | 9.5 | 2 | 1.0 |
| 6 | safety and regulatory holds | 7 | 7 | 9.857 | 7 | 1.0 |
| 7 | reconciliation across shipments | 1 | 0 | 9.0 | 1 | 1.0 |

## proxy/stress by complexity level

| Level | Name | n | Judge pass | Judge mean | Scorer pass | Routing |
|---|---|---|---|---|---|---|
| 1 | simple status | 5 | 5 | 10.0 |  |  |
| 2 | shipment data correction | 5 | 5 | 10.0 |  |  |
| 3 | multi-parcel orders | 2 | 2 | 10.0 |  |  |
| 5 | conflicting reports | 3 | 3 | 10.0 |  |  |
| 6 | safety and regulatory holds | 3 | 2 | 9.333 |  |  |

## proxy/synthetic by complexity level

| Level | Name | n | Judge pass | Judge mean | Scorer pass | Routing |
|---|---|---|---|---|---|---|
| 1 | simple status | 14 | 8 | 9.364 | 14 | 1.0 |
| 2 | shipment data correction | 14 | 9 | 9.8 | 13 | 0.929 |
| 3 | multi-parcel orders | 12 | 8 | 9.625 | 12 | 1.0 |
| 4 | evidence and downstream decisions | 16 | 12 | 9.562 | 16 | 1.0 |
| 5 | conflicting reports | 14 | 13 | 10.0 | 14 | 1.0 |
| 6 | safety and regulatory holds | 16 | 2 | 9.667 | 16 | 1.0 |
| 7 | reconciliation across shipments | 14 | 2 | 10.0 | 14 | 1.0 |

## proxy/synthetic by twist

| Twist | n | Judge pass | Judge mean | Scorer pass | Routing |
|---|---|---|---|---|---|
| none | 50 | 29 | 9.629 | 50 | 1.0 |
| early_chase | 1 |  |  | 1 | 1.0 |
| extra_noise | 16 | 7 | 9.778 | 16 | 1.0 |
| noisy_thread | 3 | 1 | 10.0 | 3 | 1.0 |
| asserted_only | 1 |  |  | 0 | 0.0 |
| conflicting_teams | 4 | 3 | 10.0 | 4 | 1.0 |
| customer_reversal | 2 | 1 | 10.0 | 2 | 1.0 |
| document_mismatch | 1 | 0 | 9.0 | 1 | 1.0 |
| duplicate_request | 1 |  |  | 1 | 1.0 |
| prohibited_request | 1 | 1 | 10.0 | 1 | 1.0 |
| arithmetic_vs_claim | 5 | 3 | 9.0 | 5 | 1.0 |
| conflicting_records | 1 | 1 | 10.0 | 1 | 1.0 |
| vulnerable_customer | 2 |  |  | 2 | 1.0 |
| attachment_reference | 11 | 7 | 9.857 | 11 | 1.0 |
| injected_instruction | 1 | 1 | 10.0 | 1 | 1.0 |

## Files

- `summary.json`: everything above plus per-case rows (`cases`) and all breakdowns (`breakdowns`).
- `<set>-proxy/plans.jsonl`: the planner outputs; `<set>-proxy/judge/`: judge grades in eval.py layout; `<set>-proxy/scorer/`: deterministic scores.
- Reproduce: `data/pipeline/proxy_eval_prepare.py` (prompts) → planner agents → `proxy_eval_collect.py` → `score_answers.py`; `proxy_eval_judge_prepare.py` → judge agents → `proxy_eval_grades.py`; then this script.

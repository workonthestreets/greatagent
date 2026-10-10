# Delivery data guards

Guards the normalized delivery data and the SQLite database that the agent reads. The guards read `data/delivery/agent/`, `data/delivery/database/` and the raw cases, and they write nothing.

| File | Purpose |
|---|---|
| `validate_cases.py` | Checks schema, counts, leakage (nothing after the decision point in agent inputs), raw consistency, timestamp order and decision points. Exits 1 on any failure. |
| `tests/test_validate_cases.py` | The pytest suite, including a deliberately leaky record. |
| `test_db.py` | Runs 7 checks on `data/delivery/database/delivery.sqlite`: case and message counts, the 'N/A' policy (no NULL or empty text), referential integrity, leakage (labelled cases are cut off at seq<=2; stress cases are cut off before the first desk message), dashboard and timeline views, and schema presence. |
| `fixtures/` | Synthetic fixtures, not real pipeline output. `fixtures/db/` holds good and bad SQLite databases that prove `test_db.py` catches each failure. |

```bash
RAW="<path to HackatonPublicCases>/Delivery & Logistics"
python3 -I validate_cases.py --raw "$RAW"         # defaults to data/delivery/agent/{cases,events,decision_points}.jsonl
python3 -I test_db.py                                  # DB path: argument, then $DELIVERY_DB, then data/delivery/database/delivery.sqlite
python3.13 -I -m pytest -p no:cacheprovider tests test_db.py -q   # the default python3 lacks pytest
```

At code freeze the validator passed all 8 checks and test_db.py passed all 7. The peer relabel, label audit and agreement report are local research and are kept outside the repo.

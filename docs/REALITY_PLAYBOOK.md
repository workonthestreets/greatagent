# Reality Test playbook (16:30–17:00): if you see X, do Y

Companion to `RUNBOOK.md`. Everything here is a run setting or an operational step; after the
16:30 freeze nobody changes code, and nobody edits agent output by hand (the rules disqualify that).

## Before 16:30 (the person who will run it)

1. Repo at the frozen commit: `git checkout main && git pull`, note `git rev-parse HEAD` for the form.
2. `.env` at the repo root with `ANTHROPIC_API_KEY` (deskagent reads that exact name). Never commit it.
3. **Use the repo's Python, not the system one.** `reality.sh` calls `python3`; on a laptop without
   the packages that fails with `No module named 'anthropic'`. Either `source .venv/bin/activate`
   first, or `pip install -r requirements.txt` into whatever `python3` resolves to.
4. Preflight once: `./reality.sh` with no args prints usage; the real run starts with a one-token
   API ping and stops early if the key or credit is bad.

## Time budget

Each case is one plan + an independent review (a few model calls, roughly 40–60 s on Opus).
With 12 workers: 50 cases ≈ 5 min, 200 cases ≈ 15–20 min. Leave 10 minutes at the end to commit
`ANSWERS/` and fill in the form.

## If you see X, do Y

| You see | Do (no code change) |
| --- | --- |
| `API preflight failed` | Fix the key or credit in `.env` (or swap to a key with credit), re-run. `DESK_MODEL=claude-sonnet-5-5` makes Sonnet the first choice if Opus is unavailable. |
| Many `429` / overloaded errors | `DESK_WORKERS=4 ./reality.sh <folder>`; finished cases are kept (`--resume`). |
| Some cases end in error after both passes | Run `./reality.sh <folder>` again: it only redoes failed cases. A case still failing keeps its escalation answer; that is an honest result, leave it. |
| Running out of time (after ~16:50) | For the remaining cases only: `python3 run.py <folder> --out ANSWERS --workers 12 --resume --no-review` (skips the reviewer: faster, less checked). Note it in `ANSWERS/SUMMARY.md` context, then commit. |
| Loader warnings about unknown attachment types | Expected for odd files; the case is still answered from everything readable. Check `ANSWERS/SUMMARY.md` that every case has a folder. |
| The drop has track sub-folders (`Delivery & Logistics/…`) | Point `reality.sh` at the folder that directly contains the case folders, or at the track folder; `run.py` discovers case folders underneath. |
| Case folders that aren't numbers | Answer folders keep the name (leading zeros are dropped only from numbers: `007` → `ANSWERS/7`). |
| `ANSWERS/` missing a case | `python3 run.py <folder> --out ANSWERS --only <case-folder-name> --resume`. |

## After `ANSWERS/` is committed (optional, only with time to spare)

Load the new cases into the hub database so the voice line's shipment lookup and `/ops` show them:
`python -m db.seed --cases "<reality folder>"`. **Never pass `--reset`** (it wipes the shared
database). This is data, not code, and doesn't affect the scored results.

## Don'ts

- Don't change code, prompts or rules after 16:30.
- Don't hand-edit, replace or delete agent answers; rerun instead.
- Don't run the voice agent tests against the live line during the run (they make real calls).

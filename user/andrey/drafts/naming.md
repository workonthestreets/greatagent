# Naming and references

Status: built on branch `feat/normalized-refs`, tested locally. **Not applied to the deployed Supabase yet.**

## The rule

- Every table keeps a plain internal key for joins. People never see it.
- Anything a person sees, says or types gets **one public reference**: a prefix, digits only, and a final **check digit** (Luhn). Digits survive phone calls, and the check digit means a misheard number is rejected instead of opening someone else's case.
- Old ids keep working forever as **aliases**.

| Entity | Reference | Rule | Example |
|---|---|---|---|
| Case | `C-<n><check>` | sequential from 1000 | `C-10009` |
| Shipment (tracking) | `DL-<6 random><check>` | random, not sequential: tracking numbers unlock status lookups | `DL-4829137` |
| Party (person or team) | `P-<n><check>` | sequential | `P-10025` |
| Organisation | `O-<n><check>` | merchant, carrier, broker, desk | `O-10009` Plover Arc Logistics |
| Agent run | `R-<n><check>` | ours; the provider's `sesn_…` stays as `session_id` | `R-10017` |
| Action | `A-<n><check>` | what the agent did or proposed | `A-10033` |
| Events, accounts | internal only | events: bigint; accounts: Supabase UUID | |
| Merchant order numbers | stay external | e.g. `TG-021`, never used as our id | |

## What the migration adds (`db/migrations/004_refs.sql`)

- Reference generators in the database (`next_ref`, `make_ref`, `ref_valid`, `new_tracking_ref`), so the portal, voice, seeds and both agent engines all produce the same format.
- `orgs`, `parties` (with `legacy_name`, the exact old string), `ref_aliases`.
- New columns:
  - `cases.ref`, `cases.source`, `cases.legacy_ref`
  - `shipments.tracking_ref`
  - `case_parties.party_id`, `profiles.party_id`
  - `agent_runs.ref`, `agent_runs.engine`
  - `actions.ref`
- `cases.source`: `public | demo | portal | voice | email | staff | unknown`.
- Triggers: every new row gets its reference whichever code inserts it; new case parties and profiles are linked to a party automatically.
- A backfill for existing rows (oldest first) and aliases for every old case id and shipment id.
- `resolve_case(text)`: one lookup for anything a person gives. It accepts:
  - a case reference
  - a legacy case id (`001`, `D101`, `C-C0F654`)
  - a tracking reference, or an old shipment id (`DL-021`)
  - any letter case, and spoken forms without punctuation (`c 10009`, `DL 103`)
- Access: `can_see_case` also matches by `party_id` (names still work). New tables have RLS: staff read all; a user reads their own party.

Additive only: nothing is dropped or renamed, and old ids remain the primary keys. New cases created after the migration use their reference as their id (`C-10561`).

## Code on the branch

- `hub/refs.py` is the single place for minting case ids, resolving references and the reference to show or say. It falls back to today's behaviour when the DB isn't migrated, so the code is safe to deploy first.
- Voice says the reference ("case C-10207") and accepts any form. Agent tools accept a reference as `case_id`.
- The web app shows references (case lists and headers, approval cards, driver stops, the customer shipments table, the Agents page), and `/agents/C-10009` URLs work. Before the migration it shows the old ids.

## Tested (locally, never against Supabase)

- **Production copy:** restored from the snapshot and migrated twice. Results:
  - 56 cases got unique, valid references; sources came out as 50 public, 2 demo, 2 portal and 2 voice.
  - 43 shipments got tracking references.
  - 90 parties and 9 orgs were created (no org was made from a spoofed email sender); every case party and profile is linked.
- **Fresh DB:** migrate, then seed (twice), then demo seed. Triggers gave every row a reference, with no dangling aliases.
- **Code paths:**
  - portal and voice cases get `C-…` ids with the right source
  - every form of reference resolves
  - the agent's `get_case` and `record_case_note` accept a reference
  - a wrong check digit is rejected
- **Test suite:** 75 passed, 4 failed, the same as `main` with or without the migration. Those 4 come from tests interfering with each other when run together; each passes on its own.

## Rolling it out (when ready)

1. Take a fresh snapshot first (the last one: `~/Backups/greatagent-db/2026-10-10T145043Z/`, read-only).
2. Merge `feat/normalized-refs` into `main` and redeploy the hub and web app. The code works against the old schema.
3. `python -m db.migrate` against Supabase (applies `004_refs.sql`; idempotent).
4. Restart the hubs. They pick up the migration on the next request, but the voice line should be restarted too.
5. Check: `select count(*) from cases where ref is null` (expect 0), the /agents and Desk pages show `C-…`, and a voice test call reads a `C-…` reference.

**Rollback:** the code needs no rollback, because it keeps working on the old ids. To undo the schema, restore from the snapshot. Every change is additive, so leaving it in place is also safe.

## Later (not in this branch)

- Switch the code to pass `party_id` instead of matching party names, then drop the name-based RLS path.
- Give drivers and depots their own party links on shipments (`shipments.driver_party_id`, `depot_party_id`).
- Let the agent quote tracking references to customers instead of old shipment ids.

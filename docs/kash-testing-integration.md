# kash.testing ↔ deskagent — how the lanes fit

Proposal for merging the `kash.testing/` lane (`feat/case-scorer`) with `deskagent` on
`main`. Nothing here changes `deskagent` — every integration point calls its public
functions (`load_case`, `process_case`) the same way `run.py` does.

## The flows

**Without voice — every channel today goes through the same reviewed pipeline:**

```mermaid
flowchart LR
    A["Email / portal / ticket<br/>index.md + history.md + attachments/"] --> L["Loader<br/>events · attachments · public-cutoff"]
    L --> P["Planner<br/>Claude proposes plan + drafts"]
    P --> PL["Policy lint<br/>deterministic blocks & warnings"]
    PL --> R["Reviewer<br/>independent Claude:<br/>approve / revise / hand over"]
    R -->|"revise (≤2 rounds)"| P
    R -->|approved| X["Executor<br/>send_message · escalate_to_human<br/>schedule_follow_up · record_case_note"]
    R -->|"can't be made safe"| H["Human handover<br/>drafts attached, nothing sent"]
    X --> O["ANSWER.md · REASONING.md<br/>trace.json · SUMMARY.md"]
    H --> O
```

**With voice — the call becomes a case; two things happen from one webhook:**

```mermaid
flowchart LR
    PH["Caller phones the desk"] --> EL["ElevenLabs agent<br/>captures name · order ref · issue · contact"]
    EL -->|"POST /voice/tool (CallReport)"| VI["voice service"]
    VI -->|"instant, fixed template<br/>no LLM text is spoken"| SP["Caller hears:<br/>'passed to safety lead' /<br/>'asking the carrier to look'"]
    SP -.-> PH
    VI -->|"writes"| CF["case folder<br/>call = event 001"]

    subgraph DA["deskagent — existing code, unchanged"]
        CF --> L2["Loader"]
        EM["Email / portal / ticket"] --> L2
        L2 --> P2["Planner"]
        P2 --> PL2["Policy lint"]
        PL2 --> R2["Reviewer"]
        R2 -->|approved| X2["Executor"]
        R2 -->|revise| P2
    end

    X2 --> O2["ANSWER.md · audit trail"]
    X2 --> FU["Follow-up to caller<br/>email / callback"]
```

The split is the whole point: the caller gets an **immediate, safe acknowledgement** off
a template; the *decision* is made inside the existing `deskagent` box, exactly as it is
for email — voice is an add-on intake, never a different decision path. The only new
code is everything left of the `deskagent` subgraph.

## What each lane has today

| Concern | `main` (`deskagent`) | `feat/case-scorer` (`kash.testing/`) |
|---|---|---|
| Agent | `deskagent/`: loader → planner → policy lint → independent reviewer → executor | `agent/`: facts extraction → deterministic `decide()` → outbox |
| Case loader + cutoff | `deskagent/loader.py` (`--public-cutoff`, attachments→vision) | `scorer/cases.py` (same format → `AgentInput`) |
| ANSWERS writer | `deskagent/report.py` (ANSWER/REASONING/trace/SUMMARY/manifest) | `agent/answers.py` + `outbox.py` |
| Evaluation | `eval.py` — LLM judge, 49/50 @ 9.84/10 on public-50 | `scorer/` — deterministic label-match, `raw_claude` baseline |
| Hard cases | `stress_cases/101–120` + `build*.py` (invented) | `scorer/hardset.py` (mutations of public cases) |
| Voice | — | `voice/` — ElevenLabs webhook, template-only `spoken()` replies |
| Submission path | `reality.sh`, `RUNBOOK.md`, `SUBMISSION.md` | — |

## Proposed moves

### 1. `voice/` → top-level `voice/` package (the headline merge)

The voice service becomes a channel *into* `deskagent`, not a second agent.

- `CallReport` (name, order ref, issue, contact) already renders as a case in the
  public format (`case_text()` writes the call as `event 001`). The adapter feeds it to
  `deskagent.loader.load_case` / `process_case` — either a temp case folder or a
  constructed `Case`.
- The decision maps back to speech through `spoken()`'s fixed templates. **No LLM text
  is ever spoken** — this is a safety property the lint can't give a voice channel, and
  it's worth keeping whichever way the decision is made.
- `setup_agent.py` provisions the ElevenLabs agent + webhook tool; ids (no secrets) in
  `voice/agent_ids.json`. Needs `APP_ELEVENLABS_API_KEY` + `VOICE_TOOL_SECRET`.

**Recommended: capture line.** Voice is one intake channel among several — its job is
to produce a well-formed `event 001`, then `deskagent` decides in the same reviewed
flow every other channel uses. `process_case` runs planner + reviewer (~2 Claude calls)
against a ~20 s ElevenLabs tool budget, so an inline decision would need `review=False` —
weaker safety on the one channel where a miss is spoken aloud. Capture-line has no
latency risk and keeps `spoken()` as pure templates.

The inline fast path (`process_case(review=False)` mid-call, probably 5–15 s) stays
documented but is not recommended; the better second demo, if time allows, is the
outbound leg — a case stuck awaiting info triggers a *call back* to the customer.

### 1b. v2: live assist — a call that keeps going while the caller can still help

The one-shot above ends every call the same way. The fuller version keeps the call open
**only while the case's next action is one the caller can satisfy** — and deskagent
already computes that: every action has a recipient.

```mermaid
flowchart TD
    T["caller speaks"] --> D["decide(case facts + collected turns)"]
    D -->|"next action needs info the<br/>caller can give"| ASK["fixed ask template<br/>(whitelist only)"]
    ASK --> T
    D -->|"next action = third party<br/>carrier / depot / merchant"| END1["'I'll chase them, we'll<br/>email you' — END CALL"]
    D -->|"escalate_to_human"| END2["'passing to our team lead'<br/>— END CALL"]
    D -->|"hazard"| END3["safety template<br/>— END CALL"]
```

What it needs beyond the one-shot:

- **`POST /voice/turn`** — the ElevenLabs tool fires on every caller turn, not once per
  call. Call state (`conversation_id` → facts collected so far) lives in a per-call JSON
  file, same pattern as the existing transcript logs.
- **Ask whitelist — the safety-critical piece.** "Ask the caller for X" can't be
  free text, or a prompt-injection or model slip asks for a gate code on a recorded
  line. The question is a fixed template keyed by an enum (slot preference, access
  instructions, callback contact, photo upload, order ref). Credentials, codes and
  payment details are simply not in the enum, so they can never be requested — the same
  guarantee `spoken()` gives answers, applied to questions.
- **Termination is deterministic:** `escalate` or a non-caller recipient → closing
  template and the call ends; a caller-recipient action → the whitelisted ask and the
  loop continues.
- **Latency is unchanged:** the per-turn decide still has to fit the ~20 s webhook
  budget, so the turn loop uses the fast deterministic agent (or a small call);
  `deskagent` remains the post-call decision of record — the voice loop can only
  collect, acknowledge and hand over, never commit.

Implemented in `kash.testing/voice/` behind `VOICE_ASSIST` / `setup_agent.py --assist`;
the one-shot `report_delivery_issue` path stays the default for the 60 s demo.

### 2. `scorer/` → independent second-opinion gate (keep in `kash.testing/` or move to `scoring/`)

`eval.py` is a nuanced LLM judge; `scorer` is a cheap deterministic check — *did the
agent's next action match the labelled one?* They're complementary. To score
`deskagent` we add one adapter in `scorer/agents.py`:

```python
def desk(case: AgentInput) -> dict:
    # AgentInput.text -> temp case folder -> load_case -> process_case -> map plan to Decision
```

Then `uv run python -m scorer.run --agent scorer.agents:desk` gives a second, judge-free
score on the same public cases — a cheap regression gate next to the full judge run.

### 3. `scorer/hardset.py` corpus → union with `stress_cases/`

Two generators, different methods: hardset mutates the 8 public bases (rewrites the
label for what a careful operator should do); `stress_cases/` invents new cases. Merge
the generated outputs into one corpus (`stress_cases/` or `evals/hard/`).

### 4. `agent/` → scorer baseline, not a second product agent

`kash.testing/agent/decide.py` becomes a second baseline next to `raw_claude` — the bar
"does deskagent beat the deterministic agent?" It already caught one real failure mode
(hyphen-insensitive refs, status-disagreement ≠ ref conflict) worth porting as a
`policy.py` lint rule or planner-prompt line on the deskagent side.

### 5. `scorer/cases.py`, `agent/answers.py`, `outbox.py` → retire in favour of `deskagent.loader` / `report.py`

Same job, less complete. Keep until (2) is wired, then delete.

## What this PR does *not* do

- Doesn't touch `deskagent/` source — all integration is additive.
- Doesn't pick the voice latency mode — needs a team decision (capture line vs inline).
- Doesn't commit any secrets. `VOICE_TOOL_SECRET` and the ElevenLabs key stay in env.

## Open questions for the team

1. Voice mode: capture-line only for 16:30, or inline decision if time allows?
2. Does the team want `scorer` as a pre-merge gate (fast, deterministic) alongside `eval.py`?
3. Where does the merged hard/stress corpus live — `stress_cases/` or a new `evals/` split?
4. Whose ElevenLabs account/number do we demo on?

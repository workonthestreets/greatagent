# Synthetic evaluation cases (201 to 300)

One hundred new Delivery & Logistics cases in the exact format of the public examples (`index.md` + `history.md` with Stage tags), generated on 10 Oct 2026 from the normalized public data. Every case's `Data:` line says `Synthetic new`. They exist to evaluate the desk agent on a wider, harder and labelled distribution than the 50 public cases.

## How they were made

1. `data/pipeline/synth_recipes.py` samples 100 recipes from the public cases' parameter space (the 24-parameter catalogue, the routing table, the queues) with a fixed seed, stratified over Andrey's complexity ladder (levels 1 to 7: 14, 14, 12, 16, 14, 16, 14) and over 46 scenario archetypes. About half carry a twist the public set lacks: an unverified requester, conflicting records, an embedded "urgent" instruction, a duplicated or reversed request, a document mismatch, a noisy multi-shipment thread, a prohibited request, a vulnerable customer, a claim that overstates arithmetic.
2. Ten writer agents (Claude Opus 5.5) wrote the prose from the recipes and a style guide with two public exemplars, in isolated scratch folders.
3. `data/pipeline/synth_integrate.py` validated each case against its recipe (sections, Stage tags, event count, event 003 recipient and channel, timestamps, no outcome text before the cutoff) and installed it here with a `_labels.json` sidecar.

## Labels

Gold routing labels are by construction: the recipe fixes the owner, recipient, channel, action class, queue, human gate, risk flags, verification state, urgency, proof standard and complexity level, and the writer had to realise them. They live in `data/pipeline/gold_labels_synthetic.csv` and in each case's `_labels.json`. Files starting with `_` are ignored by `deskagent/loader.py`, so the agent never sees them. `_recipes.jsonl` is the full recipe set.

## Evaluating an agent on them

- Roman's harness: `python eval.py synthetic_cases --out runs/synthetic` runs the agent with the escalation cutoff (there is no `_reference.md`, so the loader hides events after the first Agent action and the revealing index sections) and lets the Claude judge grade against the hidden outcome and boundaries.
- Deterministic scorer: `python3 -I data/pipeline/score_answers.py --plans runs/synthetic/answers --gold data/pipeline/gold_labels_synthetic.csv --manifest <prompts>/_manifest.json --out <dir>` scores routing to the gold owner, action family, strict channels, hard violations (with negation guards) and post-cutoff reference leakage, and breaks results down by complexity level, queue, action class and twist.
- Proxy run without an API key: `data/pipeline/proxy_eval_prepare.py` renders each case as the loader shows it; Claude Code agents run the planner manual verbatim and write plans; `proxy_eval_collect.py` gathers them for the scorer. The proxy covers the planner only (no reviewer, no tool execution) and is reported as a proxy.

## Caveats

Levels and twists are weighted toward the hard end, so scores are not comparable with the public 50 without the per-level breakdown. Four stress-style situations (fraud email, noisy inbox, duplicate request, customer reversal) sit on Andrey's ladder only loosely. Names, places and organisations are fictional; organisations reuse the public set's carrier, merchants, broker and counters.

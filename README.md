# greatagent
Great Agent from Gingerbread King

## Voice + scorer lane

Promoted to the repo root on `feat/case-scorer`:

- [`voice/`](voice/README.md): ElevenLabs voice channel — a call becomes a case, replies
  are fixed spoken templates only.
- [`scorer/`](scorer/README.md): cuts the public cases at the decision point and grades an
  agent's next action against what really happened.
- [`triage/`](triage/): the deterministic delivery agent the scorer and voice line run.
- [`docs/lane-integration.md`](docs/lane-integration.md): how the lane fits
  with `deskagent` on `main`.

```bash
uv sync
uv run pytest -q
```

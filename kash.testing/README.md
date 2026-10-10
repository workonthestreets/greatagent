# kash.testing — scoring, test cases and the Reality Test run

Our lane of the monorepo; merged with the rest of the team's work later.

- [`scorer/`](scorer/README.md): cuts the organisers' public cases at the decision point,
  hides the ending, and has Claude grade an agent's next action against what really
  happened. Raw Claude is the baseline any agent must beat.

```bash
cd kash.testing
uv sync
scripts/fetch_cases.sh            # public cases -> kash.testing/data/public-cases (gitignored)
uv run python -m scorer.run       # 5 cases per track, raw Claude
uv run pytest -q
```

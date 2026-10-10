"""python -m deskagent_v1_1 case.md [more.md ...] [--compact]   -> prints the run JSON"""
import argparse
import json
from pathlib import Path

from .agent import run_case

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("files", nargs="+")
ap.add_argument("--compact", action="store_true")
ap.add_argument("--model")
a = ap.parse_args()
runs = [run_case(Path(f).read_text(), case=Path(f).stem, model=a.model) for f in a.files]
print(json.dumps(runs[0] if len(runs) == 1 else runs, indent=None if a.compact else 2, ensure_ascii=False, default=str))

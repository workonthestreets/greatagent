#!/usr/bin/env python3
"""Print the code fingerprint recorded in ANSWERS/run_manifest.json (sha256 of run.py + deskagent/*.py)."""
from run import code_fingerprint

if __name__ == "__main__":
    print(code_fingerprint())

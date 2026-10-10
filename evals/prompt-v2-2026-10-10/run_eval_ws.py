"""Run eval.py with the org key from _env plus the anthropic-workspace-id header. Usage: python3 run_eval_ws.py <eval.py args>"""
import os, runpy, sys
from pathlib import Path
ROOT = Path("/Users/matveidanisheuski/greatagent")
sys.path.insert(0, str(ROOT)); os.chdir(ROOT)
from deskagent.llm import load_dotenv
load_dotenv(ROOT / "_env")
import anthropic
_orig = anthropic.Anthropic.__init__
def _patched(self, *a, **kw):
    ws = os.environ.get("ANTHROPIC_WORKSPACE_ID", "").strip()
    if ws and ws != "default":
        kw["default_headers"] = {**(kw.get("default_headers") or {}), "anthropic-workspace-id": ws}
    return _orig(self, *a, **kw)
anthropic.Anthropic.__init__ = _patched
sys.argv = ["eval.py"] + sys.argv[1:]
runpy.run_path(str(ROOT / "eval.py"), run_name="__main__")

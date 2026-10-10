"""deskagent v1.1: one Claude call per case, driven by preprocess/delivery_desk_system_prompt.md.

    from deskagent_v1_1 import run_case
    run = run_case(open("case.md").read(), case="delivery_001")   # preprocess -> agent -> checks
"""
from .agent import respond, run_case
from .models import DeskResponse

__all__ = ["DeskResponse", "respond", "run_case"]

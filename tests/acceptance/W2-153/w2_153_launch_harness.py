"""Run one ``gov.launch.launcher.launch`` call in this process and write its outcome (W2-153 acceptance tests).

Usage: ``python3 w2_153_launch_harness.py <spec.json>``; the spec names ``root``, ``role``, ``ticket``, ``cli_args``
and ``out``. The code under test is whatever ``gov`` the ``PYTHONPATH`` names (this tree's ``src``, or integrate's at
the baseline commit for F2). The CLI is the stand-in at ``$HOME/.local/bin/claude``: no real session starts.

One thing is replaced, the same way for both trees: the plan's check of a lead (``launcher.check_lead``, W2-136 S9)
admits every ticket, since W2-153 is not about the plan and the fixture has no ready list. Everything else, the
resource gate, the start lock, the registry and the session's temp folder, runs as written, inside the temporary
home the test gives.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    from gov.cli.errors import GovError
    from gov.launch import launcher

    launcher.check_lead = lambda *args, **kwargs: {"admitted": True, "reason": "", "override": None}
    outcome: dict = {"module": launcher.__file__}
    try:
        outcome["exit"] = launcher.launch(Path(spec["root"]), spec["role"], spec["ticket"], spec["cli_args"])
    except GovError as error:
        outcome["error"] = {"code": error.code, "message": error.message}
    Path(spec["out"]).write_text(json.dumps(outcome), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""The queue's acceptance run (W2-202 A3; L2 section 2, step 4): a ticket's acceptance folder run on the tested
commit through the runner ``gov accept`` uses (``gov.accept.runner.accept``), so the lines the close record holds
are the runner's own answer.

The runner removes its JUnit report with its private folder and names no test. The queue needs both: the report is
kept under ``.gov-runtime/`` as the run's evidence, and a failing test's node id is what the batch's search for the
culprit runs again. The runner keeps the report itself, through its ``keep_report`` parameter (W2-206): nothing of
the runner is replaced.
"""

from __future__ import annotations

from pathlib import Path

from gov.cli.errors import GovError

COUNTS = ("passed", "failed", "errors", "skipped")


def run(clone: Path, ticket: str, folder: str, timeout: float, junit: Path) -> dict:
    """``ticket``'s acceptance folder run in ``clone`` as it is checked out: ``{"ticket", "folder", "outcome",
    "error_kind", "lines", "run", "failing"}``. ``outcome`` is the runner's (``pass``, ``fail``, ``error``; a
    refusal of the runner is ``error`` with its code as ``error_kind``); ``lines`` are its KPI lines; ``run`` the
    counts of the kept report ``junit``; ``failing`` each failing test with its failure type. A run that did not
    pass and names no failing test (a crash, a time limit, a line no test ran for) names the folder itself as the
    red, with the type ``unknown`` and its ticket as the ``culprit`` (W2-206: no search can run a test it does not
    name, and the run is that ticket's own): it never passes unnamed (fail closed)."""
    from gov.accept import runner
    from gov.close import attribution

    junit = Path(junit)
    junit.parent.mkdir(parents=True, exist_ok=True)
    if junit.exists():
        junit.unlink()
    try:
        answer, code = runner.accept(Path(clone), ticket, timeout, keep_report=junit)
    except GovError as refused:
        answer, code = {"outcome": "error", "error_kind": refused.code, "lines": []}, 1
    read = attribution.read_results(junit, Path(clone)) or {}
    failing = [{"test": f["test"], "failure_type": f["failure_type"]} for f in read.get("failures") or []]
    passed = code == 0 and answer.get("outcome") == "pass" and not failing
    if not passed and not failing:
        failing = [{"test": folder.strip("/") + "/", "failure_type": attribution.UNKNOWN, "culprit": ticket}]
    outcome = answer.get("outcome") or "error"
    return {"ticket": ticket, "folder": folder, "outcome": "fail" if outcome == "pass" and not passed else outcome,
            "error_kind": answer.get("error_kind"), "lines": answer.get("lines") or [],
            "run": {"name": f"acceptance:{ticket}", **{key: read.get(key, 0) for key in COUNTS}},
            "failing": failing}

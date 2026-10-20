"""KPI success 3 (and the "green here" half of KPI success 4): ``gov check`` on this repository gives
context-reproducibility green, and core-schema green, against the store the lead built [DEC-768].

These cases need this worktree's store. One ``gov check --json`` runs for the module (about six minutes at a
load of 12 to 21 on 20 processors), in this worktree, with this worktree's ``src/`` on ``PYTHONPATH``.

Red reasons, today: context-reproducibility is RED ("did not end within its time limit of 60 seconds"), and
core-schema is RED (``SCHEMA_INVALID_TYPE`` on ``docs/audit/wave-1/W1-43-wave-1-exit-audit.md``).
"""

from __future__ import annotations

import w2_54_support as S


def test_the_suite_runs_this_worktree_s_code(code_under_test):
    """DEC-732: ``gov`` is imported from this worktree's ``src/``."""
    assert code_under_test.startswith(str(S.SRC)), code_under_test


def test_gov_check_gives_context_reproducibility_green_here(gov_check_here):
    """*Red.* The context-reproducibility check, in ``gov check --json`` on this repository, is GREEN."""
    done, checks = gov_check_here
    entry = checks.get(S.CONTEXT_CHECK_ID)
    assert entry is not None, f"gov check lists no {S.CONTEXT_CHECK_ID}\n{done.describe(1500)}"
    assert entry.get("status") == S.GREEN, \
        f"{S.CONTEXT_CHECK_ID} is {entry.get('status')} here: {S.canonical(entry.get('findings'))[:3000]}"
    assert entry.get("severity") == "hard-block"


def test_gov_check_gives_core_schema_green_here(gov_check_here):
    """*Red.* Core-schema, in ``gov check --json`` on this repository, is GREEN."""
    done, checks = gov_check_here
    entry = checks.get(S.CORE_SCHEMA_ID)
    assert entry is not None, f"gov check lists no {S.CORE_SCHEMA_ID}\n{done.describe(1500)}"
    assert entry.get("status") == S.GREEN, \
        f"{S.CORE_SCHEMA_ID} is {entry.get('status')} here: {S.canonical(entry.get('findings'))[:3000]}"
    assert entry.get("severity") == "hard-block"


def test_the_w1_43_audit_report_is_untouched(gov_check_here):
    """The W1-43 audit report is byte for byte as it was, after ``gov check`` too: its sha256 is
    ``b14e17d6...cdac1d`` (DEC-768 item 1). Passes today."""
    assert S.sha256(S.REPO_ROOT / S.W1_43_REL) == S.W1_43_SHA256
    assert (S.REPO_ROOT / S.W1_43_REL).read_bytes() == S.show(S.BASE_COMMIT, S.W1_43_REL)

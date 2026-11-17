"""W2-60b, KPI success-9 -- ``qa-engineer`` is a known role, held to its findings report.

success-9 [DEC-959 item 3, DEC-953 item 2]: "``qa-engineer`` is a known role: it is in the guard's KNOWN_ROLES
(``src/gov/guard/decide.py``, that set only) and in the reviewer set the session record and launcher read, so a QA
engineer is held to rule 5 (it writes only its findings report); this repository's own hook's reviewer line is prepared
beside it as an owner ACT, not changed here." Verify: a unit test: ``qa-engineer`` is in KNOWN_ROLES and in the reviewer
set, and its planted write outside its findings report is refused; ``git diff`` shows only that set changed in
``decide.py`` and this repository's own hook unchanged.

The reviewer set the launcher reads is shown black-box in ``test_w2_60b_s10_s12_one_writer.py``: a planted live
``qa-engineer`` session record is not counted by the one-writer check. The product guard is driven through W1-02's
harness: the kernel hook copied into a planted project, ``GOV_ROLE=qa-engineer`` and ``GOV_TICKET`` a ticket whose
``role:`` is ``qa-engineer`` and whose ``allowed_paths`` is its findings report.

``test_s9_only_known_roles_changes_in_decide`` is of the kind **repository-state**: it
reads this repository's own history against the claim's base ``4bc0399fb``.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

import w2_60b_support as t

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W1-02"))
import w1_02_support as g  # noqa: E402

QA = t.QA
QA_TICKET = "DAEO-zq09"
FINDINGS = "docs/qa/W1-90-findings.md"


@pytest.fixture()
def guarded(tmp_path):
    tickets = g.default_tickets()
    tickets[f"{QA_TICKET}.md"] = g.ticket_text(ticket_id=QA_TICKET, wbs_id="W1-99", role=QA, allowed_paths=(FINDINGS,))
    project = g.make_project(tmp_path / "project", tickets=tickets)
    return project, g.make_sandbox(tmp_path / "sandbox")


def _write(guarded, rel, tool="Write"):
    project, box = guarded
    return g.run_hook(project, tool, g.edit_tool_input(tool, project / rel), box, role=QA, ticket=QA_TICKET)


def test_s9_qa_engineer_is_in_the_guard_s_known_roles():
    from gov.guard import decide
    assert QA in decide.KNOWN_ROLES, f"{QA!r} is not in gov.guard.decide.KNOWN_ROLES: {sorted(decide.KNOWN_ROLES)}"


def test_s9_a_qa_engineer_writes_its_findings_report_and_nothing_else(guarded):
    g.assert_allowed(_write(guarded, FINDINGS), "the QA engineer's write of its own findings report")
    for rel in ("src/app/main.py", "docs/notes.md", "src/gov/guard/decide.py", "tests/acceptance/W1-90/test_fixture.py",
                ".tickets/DAEO-zq09.md", "template/governance/kernel/roles/engineer.md"):
        for tool in ("Write", "Edit"):
            g.assert_denied(_write(guarded, rel, tool), f"the QA engineer's {tool} of {rel}, outside its findings report")
    project, box = guarded
    command = f"echo found > {project / 'src/app/main.py'}"
    g.assert_denied(g.run_hook(project, "Bash", g.bash_tool_input(command), box, role=QA, ticket=QA_TICKET),
                    "the QA engineer's Bash write outside its findings report")


def _block(lines):
    start = next(i for i, line in enumerate(lines) if line.startswith("KNOWN_ROLES = frozenset({"))
    end = next(i for i in range(start, len(lines)) if lines[i].rstrip().endswith("})"))
    return start + 1, end + 1   # 1-based, inclusive


def _git(*args):
    done = subprocess.run(["git", "-C", str(t.REPO_ROOT), *args], capture_output=True, text=True, check=False)
    assert done.returncode == 0, f"git {' '.join(args)} failed: {done.stderr.strip()}"
    return done.stdout


def test_s9_only_known_roles_changes_in_decide():
    """Emergency 2 (release 0.1.2): the half that asked this repository's live guard hook to be unchanged since the
    base is retired; the hook is the owner's ACTs' (ACT-GUARD-FIX-6 to 8) and is switched off (bb61d3d74)."""
    diff = _git("diff", "-U0", t.BASE_COMMIT, "--", t.DECIDE_REL)
    assert diff.strip(), f"{t.DECIDE_REL} is unchanged since {t.BASE_COMMIT}: qa-engineer has not joined KNOWN_ROLES"
    old = _block(_git("show", f"{t.BASE_COMMIT}:{t.DECIDE_REL}").splitlines())
    new = _block((t.REPO_ROOT / t.DECIDE_REL).read_text(encoding="utf-8").splitlines())
    outside = []
    for match in re.finditer(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", diff, re.MULTILINE):
        a, la, c, lc = int(match[1]), int(match[2] or 1), int(match[3]), int(match[4] or 1)
        if (la and not (old[0] <= a and a + la - 1 <= old[1])) or (lc and not (new[0] <= c and c + lc - 1 <= new[1])):
            outside.append(match[0])
    assert not outside, f"{t.DECIDE_REL} changes outside the KNOWN_ROLES set: {outside}"
    added = [line for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]
    assert any(f'"{QA}"' in line for line in added), f"the KNOWN_ROLES change does not add \"{QA}\": {added}"

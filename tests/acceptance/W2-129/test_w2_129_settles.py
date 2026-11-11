"""W2-129 S18: a settlement is a change (D-6 part 2 item F2, round 2; DEC-866 (1), DEC-1109 (2)).

UNMARKED_CHANGE also names a decision another register entry settles (a ``**Settles:** DEC-x`` label, which the
loader's ``register_statements`` gives the class ``settle``) whose own entry names no such changer, as it does for
supersede and amend; ``--propose-marks`` gives the same ``**Changed by:** DEC-y`` mark. Every other code and count is
unchanged.

One planted commit on a copy of repository A appends eight entries to the register (after DEC-133, so no line of A moves):

- DEC-140 settled by DEC-141 (``**Settles:** DEC-140``), DEC-140's status line naming nobody: the S18 finding;
- DEC-142 settled by DEC-143, DEC-142's status line ``**Changed by:** DEC-143``: marked, no finding;
- DEC-144 settled by the PROPOSED DEC-145: no finding, as for the other forms;
- DEC-146 superseded by the PROPOSED DEC-147: the same rule for a supersession, read in the same run.

``gov links --all`` (and ``--all --json``) runs once on it; the base run is ``--all`` on repository A itself. The oracles
are the planted text and the loader's own ``register_statements``, never ``gov.links``.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest
import w2_129_support as support
from w2_129_support import REGISTER

SETTLE_ENTRIES = """
### DEC-140: The open question
- **Status:** ACCEPTED

The question is open.

### DEC-141: The answer to the open question
- **Status:** ACCEPTED · **Settles:** DEC-140

The question has its answer.

### DEC-142: The marked question
- **Status:** ACCEPTED · **Changed by:** DEC-143

The question was open.

### DEC-143: The answer to the marked question
- **Status:** ACCEPTED · **Settles:** DEC-142

The marked question has its answer.

### DEC-144: The question a proposal answers
- **Status:** ACCEPTED

The question waits.

### DEC-145: The proposed answer
- **Status:** PROPOSED · **Settles:** DEC-144

The answer waits for the owner.

### DEC-146: The rule a proposal replaces
- **Status:** ACCEPTED

The rule holds.

### DEC-147: The proposed replacement
- **Status:** PROPOSED · **Supersedes:** DEC-146

The replacement waits for the owner.
"""

SETTLED, SETTLER = "DEC-140", "DEC-141"
NEW_IDS = ("DEC-140", "DEC-141", "DEC-142", "DEC-143", "DEC-144", "DEC-145", "DEC-146", "DEC-147")
DECISION_RECORD = {"Task": "decision-record", "Implements": "DEC-100", "Role": "orchestrator"}


def plant(shas: dict) -> dict:
    """Append the S18 entries to the register and commit them as a decision record."""
    repo = shas["repo"]
    text = (repo / REGISTER).read_text(encoding="utf-8")
    support.write(repo, REGISTER, text + SETTLE_ENTRIES)
    shas["s18"] = support.commit(repo, "the planted settlements", DECISION_RECORD, 8, [REGISTER])
    return shas


@pytest.fixture(scope="module")
def s18(full, tmp_path_factory):
    """A copy of repository A with the S18 entries, ``gov links --all`` and ``--all --json`` on it (unchecked)."""
    shas = plant(support.clone(full, tmp_path_factory.mktemp("w2-129-s18") / "repo"))
    as_text = support.spawn(shas["repo"], "--all")
    as_json = support.spawn(shas["repo"], "--all", "--json")
    return shas, as_text, as_json


@pytest.fixture()
def out(s18):
    return support.Output(s18[1])


def git_apply(repo, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "apply", *args], cwd=repo, capture_output=True, text=True, env=support.git_env())


def settles(repo) -> set[tuple[str, str]]:
    """``(target, source)`` of every ``settle`` statement the loader's ``register_statements`` reads at HEAD."""
    sys.path.insert(0, str(support.src_dir()))
    from gov.store import loader

    text = support.head_text(repo, REGISTER)
    entries, _ = loader.register_entries(text)
    return {(said["target"], said["source"]) for said in loader.register_statements(text, entries)
            if said["cls"] == "settle"}


def in_register_entry(repo, finding, *rids) -> bool:
    """Whether ``finding`` sits in the register within one of the entries ``rids``."""
    return finding.path == REGISTER and any(finding.line in support.entry_lines(repo, rid) for rid in rids)


def the_rest(out) -> list[tuple]:
    """Every finding naming none of the planted S18 ids, as (code, first field, path, line, role)."""
    return sorted((f.code, f.head, f.path, f.line or 0, f.role) for f in out.findings
                  if not any(f.names(rid) for rid in NEW_IDS))


# ------------------------------------------------------------------------------------------------ the S18 finding


def test_s18_an_unmarked_settles_label_gives_unmarked_change_naming_both_ids(s18, out):
    """S18 (red today): DEC-141 ``**Settles:** DEC-140`` and DEC-140's status line names nobody: one UNMARKED_CHANGE
    naming both ids, in the register within either entry; ``--json`` gives it with ids DEC-140 and DEC-141, in the
    order the same run gives a supersession's (changed, changer) ids (DEC-101, DEC-102)."""
    shas = s18[0]
    repo = shas["repo"]
    assert (SETTLED, SETTLER) in settles(repo), "premise: the loader reads no settle statement DEC-141 -> DEC-140"
    assert SETTLER not in support.status_line(support.head_text(repo, REGISTER), SETTLED)
    assert out.of("UNMARKED_CHANGE", "DEC-101", "DEC-102"), "the control is missing: " + out.text()
    found = out.of("UNMARKED_CHANGE", SETTLED, SETTLER)
    assert found, "no UNMARKED_CHANGE for DEC-140 settled by DEC-141 (an unmarked **Settles:**):\n" + out.text()
    assert all(in_register_entry(repo, f, SETTLED, SETTLER) for f in found), found
    assert all(f.role and f.fix for f in found), found

    done = support.require(s18[2])
    envelope = json.loads(done.stdout)
    assert envelope.get("ok") is True and envelope.get("command") == "links", done.stdout[:2000]
    unmarked = [f for f in support.json_findings(envelope["result"]) if f["code"] == "UNMARKED_CHANGE"]
    supersede = next((f for f in unmarked if set(f["ids"]) == {"DEC-101", "DEC-102"}), None)
    assert supersede, f"the control is missing from --json: {unmarked}"
    settle = [f for f in unmarked if set(f["ids"]) == {SETTLED, SETTLER}]
    assert settle, f"--json gives no UNMARKED_CHANGE with ids [DEC-140, DEC-141]: {unmarked}"
    order = {"DEC-101": SETTLED, "DEC-102": SETTLER}
    assert list(settle[0]["ids"]) == [order[i] for i in supersede["ids"]], (settle[0], supersede)
    assert settle[0]["path"] == REGISTER, settle[0]


def test_s18_propose_marks_adds_changed_by_dec_141_to_dec_140_s_status_line(s18, tmp_path):
    """S18 (red today): ``--propose-marks`` prints a patch ``git apply`` accepts that adds ``**Changed by:** DEC-141``
    to DEC-140's status line and leaves the marked DEC-142's alone; committed, ``--all`` names DEC-140 in no
    UNMARKED_CHANGE."""
    shas = support.clone(s18[0], tmp_path / "repo")
    repo = shas["repo"]
    files, state = support.tree_digest(repo), support.git_state(repo)
    done = support.run_links(repo, "--all", "--propose-marks")
    assert done.returncode in (0, 1), done
    assert support.tree_digest(repo) == files and support.git_state(repo) == state, "the run changed a file"
    patch = tmp_path / "marks.patch"
    patch.write_text(done.stdout)
    applied = git_apply(repo, str(patch))
    assert applied.returncode == 0, (applied.stderr, done.stdout)
    text = (repo / REGISTER).read_text(encoding="utf-8")
    line = support.status_line(text, SETTLED)
    assert "**Changed by:**" in line and SETTLER in line, line
    assert support.status_line(text, "DEC-142").count("DEC-143") == 1, support.status_line(text, "DEC-142")
    support.commit(repo, "the marks", DECISION_RECORD, 10, [REGISTER])
    after = support.links(repo, "--all")
    assert after.findings, after.text()
    assert not [f for f in after.of("UNMARKED_CHANGE") if f.names(SETTLED)], after.text()


# ------------------------------------------------------------------------------------------------------ the guards


@pytest.mark.parametrize("changed, changer", [("DEC-142", "DEC-143"), ("DEC-144", "DEC-145"), ("DEC-146", "DEC-147")],
                         ids=["settled-entry-names-its-settler", "proposed-settles", "proposed-supersedes"])
def test_s18_guard_a_marked_or_proposed_change_gives_no_unmarked_change(s18, out, changed, changer):
    """S18 guard (green): DEC-142's status line names DEC-143 (``**Changed by:**``); DEC-145 and DEC-147 are PROPOSED.
    None gives an UNMARKED_CHANGE naming the changed entry, while the run's control DEC-101 <- DEC-102 is found."""
    repo = s18[0]["repo"]
    if changer != "DEC-147":
        assert (changed, changer) in settles(repo), f"premise: the loader reads no settle {changer} -> {changed}"
    assert out.of("UNMARKED_CHANGE", "DEC-101", "DEC-102"), "the control is missing: " + out.text()
    assert not [f for f in out.of("UNMARKED_CHANGE") if f.names(changed)], out.text()


def test_s18_guard_every_other_finding_is_unchanged(s18, out, every):
    """S18 guard (green): with the S18 entries planted, every finding naming none of DEC-140 to DEC-147 is the base
    run's, code, first field, path, line and role alike: the five unmarked changes of S2 and S8 among them, and no other
    code or count moved."""
    base = support.Output(every[1])
    assert len(base.of("UNMARKED_CHANGE")) >= 5, base.text()
    assert the_rest(out) == the_rest(base), (
        sorted(set(the_rest(out)) ^ set(the_rest(base))), out.text())

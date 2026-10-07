"""The evidence record as DEC-489 decides it: a git note on the head commit, under a ref of its own [CAP-39.a].

The pre-push hook writes the note after G3 has run and pushes it to the remote that is being pushed to, inside
the one plain ``git push``. The CI job fetches the ref itself (a fresh checkout brings no notes) and reads the
note of the commit it builds.

DEC-489 fixes no name for the ref and no format for the note, and neither does a case here. The ref is found by
asking the bare repository which notes refs it holds besides git's default one; the note is read with
``git notes``. What a case holds of the note's text is what DEC-489 says it holds: the commit id, the checks
that ran, and, where the project declares no G3 check, the words "no G3 check declared".
"""

from __future__ import annotations

import re

import w1_40_support as support

G3_CHECK = support.TIER_CHECKS["G3"][0]

# Words that would state a pass. DEC-489 fixes none; these are the ones a record would plausibly use.
SAYS_PASSED = re.compile(r"\b(pass|passed|passes|green|success|succeeded)\b", re.IGNORECASE)


def _only(records, what):
    assert records, what
    return "\n".join(records.values())


# -- the note and its ref --------------------------------------------------

def test_one_push_leaves_the_note_of_the_head_commit_on_the_remote_under_a_ref_of_its_own(project, pushed):
    records = project.records(pushed)
    assert records, (
        f"after a push through the hook the remote holds no note of {pushed[:8]} under a notes ref of its own "
        f"(notes refs on the remote: {project.notes_refs() or 'none'})")
    assert support.DEFAULT_NOTES not in project.notes_refs(), (
        f"the push put {support.DEFAULT_NOTES} on the remote: the record has a ref of its own (DEC-489)")


def test_the_note_holds_the_commit_id_and_the_g3_check_that_ran(project, pushed):
    text = _only(project.records(pushed), f"the remote holds no note of {pushed[:8]}")
    assert pushed in text, f"the record does not hold the id of the commit it vouches for:\n{text}"
    assert G3_CHECK in text, f"the record does not name the G3 check that ran ({G3_CHECK}):\n{text}"
    assert support.NO_G3 not in text, f"the record says no G3 check is declared, and one is:\n{text}"


def test_the_note_goes_to_the_remote_that_is_pushed_to(project, machine):
    """The hook pushes the record where the commit goes, whatever the remote is called."""
    mirror = project.add_remote("mirror")
    dev = machine()
    project.commit(dev)
    done, arrived = project.push(dev, remote="mirror")
    assert arrived, f"a push to a second remote with every check passing was refused:\n{support.said(done)}"
    assert project.records(project.head(), repo=mirror), (
        f"the remote that was pushed to holds no note of the pushed commit:\n{support.said(done)}")


def test_the_ref_of_the_record_is_named_in_the_hook_file_and_in_the_workflow(project, pushed):
    """DEC-489: the choice is documented in the hook file and the workflow. The ref is part of the choice."""
    refs = sorted(project.records(pushed))
    assert refs, f"the remote holds no note of {pushed[:8]}"
    names = [name for ref in refs for name in (ref, ref[len(support.NOTES):])]
    texts = {"lefthook.yml": support.LEFTHOOK_YML.read_text(encoding="utf-8")}
    try:
        workflows = support.push_workflows()
    except support.Absent as absent:
        raise AssertionError(str(absent)) from None
    texts["the push workflows"] = "\n".join(path.read_text(encoding="utf-8") for path, _ in workflows)
    for where, text in texts.items():
        assert any(name in text for name in names), f"{where} does not name the ref of the record ({refs})"


# -- a project that declares no G3 check -----------------------------------

def test_a_project_without_a_g3_check_can_push_and_its_record_says_so_and_never_says_passed(new_project, machine):
    project = new_project(tiers=("G1", "G2"))
    dev = machine()
    done, moved = project.commit(dev)
    assert moved, f"a clean commit was refused:\n{support.said(done)}"
    done, arrived = project.push(dev)
    assert arrived, f"the push was refused for the one reason that no G3 check is declared:\n{support.said(done)}"
    head = project.head()
    text = _only(project.records(head), f"the remote holds no note of {head[:8]} after the push")
    assert head in text, f"the record does not hold the commit id:\n{text}"
    assert support.NO_G3 in text, f"the record does not say '{support.NO_G3}':\n{text}"
    assert not SAYS_PASSED.search(text), (
        f"the record of a commit for which no G3 check ran states a pass ({SAYS_PASSED.search(text).group(0)!r}):\n{text}")


def test_ci_reports_that_no_g3_check_is_declared(new_project, machine, ci):
    """The words are in the job's output. Whether the job is then green is not decided (README, package P-6)."""
    project = new_project(tiers=("G1", "G2"))
    project.through_the_hooks(machine())
    result = ci(of=project)
    assert support.NO_G3 in result.output, (
        f"the CI job does not report '{support.NO_G3}' for a commit whose record says so:\n{result}")


# -- records that do not vouch for the head commit --------------------------

def test_a_record_of_a_failed_g3_run_that_reaches_the_remote_fails_ci(project, machine, ci):
    """A failing G3 at push leaves no record or one that says failed. Whatever it left is pushed by hand: CI is red."""
    dev = machine()
    project.commit(dev)
    project.fail("G3")
    done, arrived = project.push(dev)
    assert not arrived, f"a failing G3 check did not stop the push:\n{support.said(done)}"
    env = project.setup.env()
    for ref in project.notes_refs(project.root):
        support.sh(["git", "push", "--no-verify", "origin", f"+{ref}:{ref}"], project.root, env, check=True)
    done, arrived = project.push(dev, verify=False)
    assert arrived, support.said(done)
    project.fail("G3", failing=False)
    result = ci()
    assert not result.green, (
        f"CI is green for a commit whose G3 check failed at push, with what the hook left pushed by hand "
        f"(records on the remote: {sorted(project.records(project.head())) or 'none'}):\n{result}")


def test_the_note_of_another_commit_copied_onto_the_head_commit_fails_ci(project, pushed, ci):
    """A record for another commit fails CI (DEC-087, DEC-489): the note names the commit it was written for."""
    refs = sorted(project.records(pushed))
    assert refs, f"the remote holds no note of {pushed[:8]}"
    head = project.unhooked_commit("more.txt")
    done, arrived = project.push(project.setup, verify=False)
    assert arrived, support.said(done)
    env = project.setup.env()
    for ref in refs:
        support.sh(["git", "notes", "--ref", ref, "copy", pushed, head], project.remote, env, check=True)
    assert project.records(head), "the fixture does not hold: the copied note is not on the head commit"
    result = ci()
    assert not result.green, (
        f"CI is green on {head[:8]} with a note that was written for {pushed[:8]}:\n{result}")

"""S1: stage AS stands after A2 and before A3; it writes its record; A3 refuses to run before AS is recorded."""

from __future__ import annotations

import w2_192_support as support

base = support.base


def test_s1_the_command_lists_as_between_a2_and_a3(tmp_path):
    box = base.make_box(tmp_path / "box")
    stages = support.stages_of_command(box, tmp_path)
    assert "AS" in stages, f"gov.adopt.command.STAGES holds no AS: {stages}"
    assert stages.index("A2") < stages.index("AS") < stages.index("A3"), f"AS is not between A2 and A3: {stages}"


def test_s1_as_runs_after_a2_and_commits_its_record(audited):
    result = support.audit_ok(audited)
    root = audited.root
    assert base.at_head(root, support.AS_RECORD) is not None, f"HEAD holds no {support.AS_RECORD}\n{audited.done.describe()}"
    assert (root / support.AS_RECORD).is_file(), f"{support.AS_RECORD} is not in the working tree"
    assert support.as_front(root).get("stage") == "AS", "the record's front matter does not say stage: AS"
    assert result.get("stage", "AS") == "AS"
    assert not base.porcelain(root), f"the tree is not clean after AS:\n{base.porcelain(root)}"
    assert base.head(root) != audited.head_before, "AS committed nothing"
    changed = base.git(root, "diff", "--name-only", f"{audited.head_before}..HEAD").split()
    assert support.AS_RECORD in changed, f"the commits of AS do not hold the record: {changed}"


def test_s1_a3_before_as_is_refused_naming_as_and_writes_no_a3_record(adoption):
    before = base.head(adoption.root)
    done = support.a3_keep_all(adoption)
    error = base.refusal(done, "ADOPT_STAGE_MISSING")
    assert support.names_stage(error, "AS"), f"the refusal does not name AS: {support.said(error)}"
    support.assert_no_record(adoption.root, support.A3_RECORD, before, done)
    assert not base.porcelain(adoption.root), "the refused A3 left the tree dirty"


def test_s1_a3_after_as_with_an_all_keep_proposal_is_accepted(after_as):
    support.as_ran(after_as)
    result = base.succeeded(support.a3_keep_all(after_as))
    assert support.front_of(after_as.root, support.A3_RECORD) is not None, "A3 recorded nothing"
    assert result.get("stage", "A3") == "A3"


def test_s1_as_before_a2_is_refused_and_writes_no_record(prepared, tmp_path):
    """AS reads A1's inventory and A2's classes: with A2 undone (the project as A1 left it) AS has no classes to read.
    The code of the refusal is not stated, so none is pinned."""
    root = support.copy_of(prepared, tmp_path / "project")
    base.git(root, "reset", "-q", "--hard", "HEAD~1")   # A2 is one commit: the project stands as A1 left it
    assert base.at_head(root, base.ADOPTION + "/A2-classification.md") is None, "planting fault: A2's record is still there"
    assert base.at_head(root, base.RECORD["A1"]) is not None, "planting fault: A1's record is gone"
    before = base.head(root)
    done = base.Adoption(root, base.make_box(tmp_path / "box")).run("AS")
    error = base.refusal(done)
    assert str(error.get("code", "")).startswith("ADOPT_"), f"the refusal's code is not an ADOPT_ code: {error}"
    support.assert_no_record(root, support.AS_RECORD, before, done)


def test_s1_guard_a3_without_a2_still_names_a2(prepared, tmp_path):
    """Guard (green on the code before the change, and after): the chain's existing refusal for a stage that is missing
    earlier in it. A3 on a project where only A0 and A1 ran is ``ADOPT_STAGE_MISSING`` naming A2."""
    root = support.copy_of(prepared, tmp_path / "project")
    base.git(root, "reset", "-q", "--hard", "HEAD~1")
    before = base.head(root)
    adoption = base.Adoption(root, base.make_box(tmp_path / "box"))
    done = support.a3_keep_all(adoption)
    error = base.refusal(done, "ADOPT_STAGE_MISSING")
    assert support.names_stage(error, "A2"), f"the refusal does not name A2: {support.said(error)}"
    support.assert_no_record(root, support.A3_RECORD, before, done)

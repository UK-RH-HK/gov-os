"""success-3 (S3, Checked; DEC-1204 (5); P-GOLDEN-RULE-1 section 3 S3; the lead's interface items 3 and 4).

``gov brief`` refuses ``BRIEF_JUDGING_RULE_MISSING`` (the envelope's error code under ``--json``, a non-zero exit, no brief)
for each judging brief (independent-auditor, qa-engineer, lead ``--run review``) when the kernel file is absent, the
preloaded copy is absent, the preloaded copy's version differs from the kernel file's, or the kernel file's sections 1 to 3
cannot be found. ``gov.launch.role.read_role`` refuses ``LAUNCH_JUDGING_RULE_MISSING`` for each judging launch role
(independent-auditor, under which the reviewer and probe launch, and qa-engineer) when the role file's Skills line lacks
``judging-work``, the preloaded copy is absent (this code, not the generic ``LAUNCH_REFUSED``), or its version differs from the
kernel file's. The same fixtures with the skill pass: the S2 brief cases and the S1 ``read_role`` case.
"""

from __future__ import annotations

import pytest

import w2_195_support as s

BRIEF_CODE = "BRIEF_JUDGING_RULE_MISSING"
LAUNCH_CODE = "LAUNCH_JUDGING_RULE_MISSING"


def _brief_fault(project: s.BriefProject, fault: str) -> None:
    text = s.kernel_text()
    if fault == "kernel-file-removed":
        project.remove(project.kernel_rel)
    elif fault == "preloaded-copy-removed":
        project.remove(s.PRELOADED_REL)
    elif fault == "preloaded-copy-other-version":
        project.set_copy(s.preloaded(text, version=s.OTHER_VERSION))
    elif fault == "sections-not-found":
        assert text.count(s.START) == 1, "the plant: the skill holds no single section 1 heading"
        project.set_kernel(text.replace(s.START, "## 1. Threat model\n"))
    else:
        raise AssertionError(fault)


@pytest.mark.parametrize("fault", ["kernel-file-removed", "preloaded-copy-removed", "preloaded-copy-other-version"])
@pytest.mark.parametrize("which", list(s.JUDGING_BRIEFS))
def test_s3_a_judging_brief_without_the_skill_or_with_another_version_is_refused_by_name(tmp_path, which, fault):
    """success-3: the judging brief on a fixture with one fault is refused ``BRIEF_JUDGING_RULE_MISSING``: non-zero exit, an
    ``ok: false`` envelope with that error code, no brief in it."""
    project = s.BriefProject(tmp_path / "repo")
    _brief_fault(project, fault)
    code = s.refused_code(project.brief(*s.JUDGING_BRIEFS[which]))
    assert code == BRIEF_CODE, f"the {which} brief ({fault}) is refused {code}, not {BRIEF_CODE}"


def test_s3_an_auditor_brief_whose_kernel_file_has_no_sections_1_to_3_is_refused_by_name(tmp_path):
    """success-3 (interface item 3): the kernel file is there and versions agree, but its section 1 heading is reworded, so
    sections 1 to 3 cannot be found: the auditor's brief is refused ``BRIEF_JUDGING_RULE_MISSING``."""
    project = s.BriefProject(tmp_path / "repo")
    _brief_fault(project, "sections-not-found")
    code = s.refused_code(project.brief(*s.JUDGING_BRIEFS["independent-auditor"]))
    assert code == BRIEF_CODE, f"the auditor brief (sections not found) is refused {code}, not {BRIEF_CODE}"


def test_s3_without_json_the_refusal_prints_no_brief_and_names_its_code(tmp_path):
    """success-3 (interface item 3, the plain form): the auditor's brief with the kernel file removed, run without
    ``--json``: non-zero exit, nothing on stdout, stderr names ``BRIEF_JUDGING_RULE_MISSING``."""
    project = s.BriefProject(tmp_path / "repo")
    _brief_fault(project, "kernel-file-removed")
    done = project.brief(*s.JUDGING_BRIEFS["independent-auditor"], json_out=False)
    assert done.returncode != 0, f"gov brief did not refuse: {s.describe(done)}"
    assert done.stdout == "", f"a refused brief printed something on stdout: {s.describe(done)}"
    assert BRIEF_CODE in done.stderr, f"stderr does not name {BRIEF_CODE}: {s.describe(done)}"


def _launch_root(tmp_path, role: str, fault: str) -> s.LaunchRoot:
    names = [name for name in s.skills_named((s.KERNEL / "roles" / f"{role}.md").read_text(encoding="utf-8"))
             if name != s.SKILL]
    if fault == "skills-line-lacks-judging-work":
        return s.LaunchRoot(tmp_path / "root", role, names=names)
    if fault == "preloaded-copy-removed":
        return s.LaunchRoot(tmp_path / "root", role, names=[*names, s.SKILL], with_copy=False)
    if fault == "preloaded-copy-other-version":
        return s.LaunchRoot(tmp_path / "root", role, names=[*names, s.SKILL],
                            copy=s.preloaded(s.kernel_text(), version=s.OTHER_VERSION))
    raise AssertionError(fault)


@pytest.mark.parametrize("fault", ["skills-line-lacks-judging-work", "preloaded-copy-removed", "preloaded-copy-other-version"])
@pytest.mark.parametrize("role", s.JUDGING_LAUNCH_ROLES)
def test_s3_a_judging_launch_without_the_skill_or_with_another_version_is_refused_by_name(tmp_path, role, fault):
    """success-3: ``read_role(root, role)`` on a root with one fault (this tree's role file, its Skills line set by the case;
    every other skill it names copied from the kernel) is refused ``LAUNCH_JUDGING_RULE_MISSING``."""
    answer = _launch_root(tmp_path, role, fault).read_role()
    assert answer.get("ok") is False, f"read_role({role}) ({fault}) was not refused: the launch would start without the rule"
    assert answer.get("code") == LAUNCH_CODE, (f"read_role({role}) ({fault}) is refused {answer.get('code')}, not "
                                               f"{LAUNCH_CODE}: {answer.get('message')}")

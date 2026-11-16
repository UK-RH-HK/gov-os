"""success-1 (S1, Preloaded; DEC-1204 (5); P-GOLDEN-RULE-1 section 3 S1; the lead's interface items 4 to 6).

The files: the ``- **Skills:**`` line of the kernel role files independent-auditor, qa-engineer, orchestrator and ticket-lead
names ``judging-work`` (membership, not position); ``role-reviewer.md``'s front matter ``skills`` list holds it; the rulesync
subagent mirrors of the same four roles hold it in ``claudecode.skills`` (what preloads a generated agent).

The launch: ``gov.launch.role.read_role(root, role)`` for each judging role, on a root holding this tree's role file and a
copy of every skill it names, returns in ``skills`` (the list the launcher writes into the launch record's ``skills``) the
entry ``name: judging-work``, ``named: True``, its version. ``gov launch --plan``'s line is W2-156's ``launcher.py``, outside
this ticket's paths: no case reads it (README, "Not covered").
"""

from __future__ import annotations

import pytest
import yaml

import w2_195_support as s


@pytest.mark.parametrize("role", s.PRELOADING_ROLES)
def test_s1_the_kernel_role_files_skills_line_names_judging_work(role):
    """success-1: ``template/governance/kernel/roles/<role>.md``'s one ``- **Skills:**`` line names ``judging-work``."""
    text = (s.KERNEL / "roles" / f"{role}.md").read_text(encoding="utf-8")
    names = s.skills_named(text)
    assert names, f"roles/{role}.md has no '- **Skills:**' line"
    assert s.SKILL in names, f"roles/{role}.md's Skills line names {names}, not {s.SKILL}"


def test_s1_the_reviewer_templates_skills_list_holds_judging_work():
    """success-1: ``template/governance/kernel/templates/role-reviewer.md``'s front matter ``skills`` list holds ``judging-work``."""
    front = s.front_matter((s.KERNEL / "templates" / "role-reviewer.md").read_text(encoding="utf-8"))
    skills = front.get("skills")
    assert isinstance(skills, list), f"role-reviewer.md's front matter has no skills list: {front}"
    assert s.SKILL in skills, f"role-reviewer.md's skills list is {skills}, without {s.SKILL}"


@pytest.mark.parametrize("role", s.PRELOADING_ROLES)
def test_s1_the_rulesync_subagent_mirror_preloads_judging_work(role):
    """success-1 (interface item 6): ``template/.rulesync/subagents/<role>.md``'s front matter ``claudecode.skills`` holds
    ``judging-work``, so the agent ``gov adapters generate`` writes preloads it."""
    path = s.REPO / "template/.rulesync/subagents" / f"{role}.md"
    front = s.front_matter(path.read_text(encoding="utf-8"))
    claudecode = front.get("claudecode") if isinstance(front.get("claudecode"), dict) else {}
    skills = claudecode.get("skills")
    assert isinstance(skills, list), f"{path.name}'s claudecode block has no skills list: {yaml.safe_dump(front)[:400]}"
    assert s.SKILL in skills, f"the rulesync mirror {path.name} preloads {skills}, without {s.SKILL}"


@pytest.mark.parametrize("role", s.JUDGING_LAUNCH_ROLES)
def test_s1_s3_read_role_of_a_judging_role_carries_judging_work_named_with_its_version(tmp_path, role):
    """success-1 (the launch half, interface item 4) and success-3 (the same role with the skill passes): on a root holding
    this tree's ``roles/<role>.md`` as it is, the kernel skill file and a preloaded copy of every skill its Skills line
    names (``judging-work``'s in the generated form, version 1.0.0), ``read_role`` is not refused and its ``skills`` hold
    one entry ``name: judging-work`` with ``named: True`` and ``version: 1.0.0``."""
    root = s.LaunchRoot(tmp_path / "root", role)
    answer = root.read_role()
    assert answer.get("ok") is True, f"read_role({role}) was refused: {answer}"
    entries = [entry for entry in answer["skills"] if entry.get("name") == s.SKILL]
    assert len(entries) == 1, f"read_role({role})'s skills hold {len(entries)} entries named {s.SKILL}: {answer['skills']}"
    entry = entries[0]
    assert entry.get("named") is True, (f"{s.SKILL} is loadable but not named by roles/{role}.md's Skills line, so the "
                                        f"launch does not preload it: {entry}")
    assert entry.get("version") == s.VERSION, f"the launch record's {s.SKILL} entry carries version {entry.get('version')!r}"

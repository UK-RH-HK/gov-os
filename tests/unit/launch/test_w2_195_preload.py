"""W2-195 (DAEO-d8df) S1: every role that judges work preloads the judging-work skill (DEC-1204 (5)): the Skills line
of the four kernel role files, role-reviewer.md's skills list and the rulesync subagent mirrors name it, and
``read_role`` of a judging role carries it, named, with its version, in the skills the launch record holds.

Regression evidence only (DEC-136). The file checks read this tree; ``read_role`` runs on a planted tree.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.adapters import portability  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.launch import role  # noqa: E402

KERNEL = REPO / "template/governance/kernel/skills/judging-work/SKILL.md"


def _version_in(data: bytes) -> str:
    """The version the skill file's front matter states on its top-level ``version:`` line, read by the test."""
    match = re.search(rb'^version: "([^"]+)"$', data.split(b"\n---\n", 1)[0], re.M)
    assert match, "the skill file states no top-level version"
    return match.group(1).decode("utf-8")


VERSION = _version_in(KERNEL.read_bytes())  # read from the file, never pinned
FOUR = ("independent-auditor", "qa-engineer", "orchestrator", "ticket-lead")
OLD = {"independent-auditor": ["audit", "retrieval"], "qa-engineer": ["qa-review"],
       "orchestrator": ["orchestration", "planning", "checkpoint", "change", "retrieval"],
       "ticket-lead": ["orchestration", "checkpoint", "retrieval"]}
MIRROR_OLD = {"independent-auditor": ["audit"], "qa-engineer": ["qa-review"], "orchestrator": ["orchestration"],
              "ticket-lead": ["orchestration", "checkpoint", "retrieval"]}


def _front(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("\n---\n", 1)[0][4:])


def _skills_line(path: Path) -> list[str]:
    found = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith(role.SKILLS_HEAD)]
    assert len(found) == 1
    match = role.SKILLS_LINE.fullmatch(found[0])
    assert match, found[0]
    return match.group(1).split(", ")


@pytest.mark.parametrize("name", FOUR)
def test_the_kernel_role_files_skills_line_appends_judging_work(name):
    assert _skills_line(REPO / role.ROLES_REL / f"{name}.md") == [*OLD[name], "judging-work"]


def test_the_reviewer_templates_skills_list_appends_judging_work():
    assert _front(REPO / "template/governance/kernel/templates/role-reviewer.md")["skills"] == ["audit",
                                                                                                "judging-work"]


@pytest.mark.parametrize("name", FOUR)
def test_the_rulesync_mirror_preloads_judging_work_and_is_still_the_composition(name):
    mirror = REPO / "template/.rulesync/subagents" / f"{name}.md"
    assert _front(mirror)["claudecode"]["skills"] == [*MIRROR_OLD[name], "judging-work"]
    assert _skills_line(mirror) == [*OLD[name], "judging-work"]
    assert mirror.read_text(encoding="utf-8") == portability.compose(REPO / "template", name)


# The base these files are compared with: w2/integrate's head as last merged into this branch, i.e. the merge-base of
# HEAD and w2/integrate, which holds none of W2-195's kernel changes, so the lines other tickets merged in (the owner's
# launch defaults, DEC-1209's line in the orchestrator mirror) are not counted as W2-195's. A clone without the ref
# falls back to PINNED, a commit that was integrate's head once (it can lag behind later merges). Once W2-195 has
# landed, HEAD is integrate itself, the base holds the change already and the case skips.
PINNED = "9ef5cba29"


def _git(*args: str) -> str:
    import subprocess
    done = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
    return done.stdout if done.returncode == 0 else ""


def _base() -> str:
    return _git("merge-base", "HEAD", "w2/integrate").strip() or PINNED


def _at_base(rel: str) -> list[str]:
    text = _git("cat-file", "blob", f"{_base()}:{rel}")
    assert text, rel
    return text.split("\n")


def _appended(line: str) -> str:
    """The line with judging-work appended to its list: ``a, b`` -> ``a, b, judging-work``; ``[a]`` -> ``[a,
    judging-work]``; ``["a"]`` -> ``["a", "judging-work"]``."""
    if not line.endswith("]"):
        return line + ", judging-work"
    return line[:-1] + (', "judging-work"]' if '"' in line else ", judging-work]")


@pytest.mark.parametrize("rel", [f"{role.ROLES_REL}/{name}.md" for name in FOUR]
                         + [f"template/.rulesync/subagents/{name}.md" for name in FOUR]
                         + ["template/governance/kernel/templates/role-reviewer.md"])
def test_each_file_changes_only_its_skills_lines_by_appending_judging_work(rel):
    old, new = _at_base(rel), (REPO / rel).read_text(encoding="utf-8").split("\n")
    if old == new:
        pytest.skip("the base already holds W2-195's change (HEAD is integrate after the landing)")
    assert len(old) == len(new)
    changed = [(a, b) for a, b in zip(old, new) if a != b]
    assert changed, rel
    for a, b in changed:
        assert re.match(r"^(- \*\*Skills:\*\* |  skills: \[|skills: \[)", a) and b == _appended(a), (a, b)


PRELOADED_COPY = REPO / role.SKILLS_REL / "judging-work/SKILL.md"  # Gov OS's own copy, in rulesync's form


def install_judging_skill(root: Path) -> None:
    """Give a planted project the judging-work skill as a real project holds it (W2-195, DEC-1204 (5)), for the
    builder tests of other tickets whose fixtures launch a judging role: this tree's kernel file at
    ``template/governance/kernel/skills/judging-work/SKILL.md``, its preloaded copy at
    ``.claude/skills/judging-work/SKILL.md``, and judging-work appended to the Skills line of each judging role file
    the project already has (the line added when there is none). Other roles' files are left as they are; calling it
    again changes nothing."""
    root = Path(root)
    for target, source in ((root / role.ROLES_REL).parent / "skills/judging-work/SKILL.md", KERNEL), \
                          (root / role.SKILLS_REL / "judging-work/SKILL.md", PRELOADED_COPY):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    for name in role.JUDGING_ROLES:
        path = root / role.ROLES_REL / f"{name}.md"
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8").split("\n")
        found = [at for at, line in enumerate(lines) if line.startswith(role.SKILLS_HEAD)]
        if not found:
            lines.insert(len(lines) - 1 if lines[-1] == "" else len(lines), f"{role.SKILLS_HEAD} judging-work")
        elif "judging-work" not in lines[found[0]][len(role.SKILLS_HEAD):].strip().split(", "):
            lines[found[0]] = _appended(lines[found[0]])
        path.write_text("\n".join(lines), encoding="utf-8")


def test_install_judging_skill_lets_a_bare_judging_role_launch_and_leaves_other_roles(tmp_path):
    bare = "# {0}\n\n- **Version:** 1.0.0\n- **Launch default:** model claude-opus-5-5, effort high\n"
    for name in ("independent-auditor", "qa-engineer", "engineer"):
        (tmp_path / role.ROLES_REL).mkdir(parents=True, exist_ok=True)
        (tmp_path / role.ROLES_REL / f"{name}.md").write_text(bare.format(name), encoding="utf-8")
    kernel = (tmp_path / role.ROLES_REL).parent / "skills/judging-work/SKILL.md"
    kernel.parent.mkdir(parents=True)
    kernel.write_bytes(KERNEL.read_bytes())  # a project that holds the kernel file: the launch check applies
    with pytest.raises(GovError) as raised:
        role.read_role(tmp_path, "independent-auditor")
    assert raised.value.code == "LAUNCH_JUDGING_RULE_MISSING"
    install_judging_skill(tmp_path)
    install_judging_skill(tmp_path)  # a second call changes nothing
    for name in ("independent-auditor", "qa-engineer"):
        text = (tmp_path / role.ROLES_REL / f"{name}.md").read_text(encoding="utf-8")
        assert text == bare.format(name) + "- **Skills:** judging-work\n"
        entry = [skill for skill in role.read_role(tmp_path, name)["skills"] if skill["name"] == "judging-work"]
        assert entry[0]["named"] is True and entry[0]["version"] == VERSION
    assert (tmp_path / role.ROLES_REL / "engineer.md").read_text(encoding="utf-8") == bare.format("engineer")


def test_install_judging_skill_appends_to_an_existing_skills_line(tmp_path):
    (tmp_path / role.ROLES_REL).mkdir(parents=True)
    path = tmp_path / role.ROLES_REL / "qa-engineer.md"
    path.write_text("# qa\n\n- **Version:** 1.0.0\n- **Launch default:** model claude-opus-5-5, effort high\n"
                    "- **Skills:** audit\n", encoding="utf-8")
    install_judging_skill(tmp_path)
    assert path.read_text(encoding="utf-8").endswith("- **Skills:** audit, judging-work\n")


def plant(tmp_path: Path, name: str, skills_line: str, kernel: bytes | None = None,
          preloaded: bytes | None = None) -> Path:
    """A tree with one role file, the judging-work kernel file and its preloaded copy (``None``: the kernel's)."""
    roles = tmp_path / role.ROLES_REL
    roles.mkdir(parents=True)
    (roles / f"{name}.md").write_text(f"# {name}\n\n- **Version:** 1.0.0\n- **Launch default:** model "
                                      f"claude-opus-5-5, effort high\n{skills_line}\n", encoding="utf-8")
    kernel = KERNEL.read_bytes() if kernel is None else kernel
    target = tmp_path / "template/governance/kernel/skills/judging-work/SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_bytes(kernel)
    copy = tmp_path / role.SKILLS_REL / "judging-work/SKILL.md"
    copy.parent.mkdir(parents=True)
    copy.write_bytes(kernel if preloaded is None else preloaded)
    return tmp_path


@pytest.mark.parametrize("name", ("independent-auditor", "qa-engineer"))
def test_read_role_of_a_judging_role_carries_judging_work_named_with_its_version(tmp_path, name):
    loaded = role.read_role(plant(tmp_path, name, "- **Skills:** judging-work"), name)
    entry = [skill for skill in loaded["skills"] if skill["name"] == "judging-work"]
    assert len(entry) == 1
    assert (entry[0]["named"], entry[0]["version"], entry[0]["path"]) == (True, VERSION,
                                                                          ".claude/skills/judging-work/SKILL.md")
    assert loaded["appended"].endswith(KERNEL.read_bytes())

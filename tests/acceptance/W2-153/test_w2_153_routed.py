"""The line routed from W2-33 (its S7 copies and F1 drift, DEC-1156 (3)), W2-153's sixth success line:

    the generated role copies carry each kernel role file's ``Launch default``, ``Launch by criticality`` and
    ``Skills`` lines unchanged, and a hand edit to a generated role copy is named as drifted by the generation check.

Two clauses, two groups of cases:

* *unchanged* (``test_routed_...carries...``): on this repository, every one of the three labelled lines a kernel role
  file carries is a whole line, byte for byte, of that role's copy in each of the three folders: ``.claude/agents/``
  (rulesync's output), ``.rulesync/subagents/`` and ``template/.rulesync/subagents/`` (the composed sources). The
  copies' ACTs are applied (COPIES-6, COPIES-8), so these are expected green on this tree: they are the line's verify,
  not a build's driver. Each case reads files only and writes nothing.
* *drift named* (``test_routed_a_hand_edit_...``): in a stand-in project in a temporary folder (never this repository's
  files), a hand edit to one of the three lines in the generated agent or in the composed source makes
  ``python3 -m gov.adapters.portability`` exit non-zero with a finding naming that file; the unedited stand-in names
  neither. The stand-in is W2-153's own ``PortabilityBed`` (stand-in rulesync included), its engineer role file
  carrying the three lines.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w2_153_support as support
from w2_153_support import PortabilityBed

LABELS = ("Launch default", "Launch by criticality", "Skills")
FOLDERS = (".claude/agents", ".rulesync/subagents", "template/.rulesync/subagents")
ROLES_DIR = support.KERNEL / "roles"
ROLE_FILES = sorted(ROLES_DIR.glob("*.md"))


def _prefix(label: str) -> bytes:
    return f"- **{label}:**".encode()


def _lines(data: bytes, label: str) -> list[bytes]:
    """The whole lines of ``data`` (split on ``\\n`` alone, so a ``\\r`` stays in the line) that open with the label."""
    return [line for line in data.split(b"\n") if line.startswith(_prefix(label))]


def _carried_cases():
    cases = []
    for role_file in ROLE_FILES:
        for folder in FOLDERS:
            for label in LABELS:
                missing = not _lines(role_file.read_bytes(), label)
                mark = pytest.mark.skip(
                    reason=f"the kernel role file {role_file.name} has no '{label}' line, so there is no line to carry"
                ) if missing else ()
                cases.append(pytest.param(role_file.stem, folder, label, marks=mark,
                                          id=f"{role_file.stem}::{folder}::{label.replace(' ', '-').lower()}"
                                             + ("::no-such-line-in-the-role-file" if missing else "")))
    return cases


def test_routed_guard_the_cases_below_are_not_a_silent_narrowing():
    """Nine kernel role files on this tree; every label is carried by at least one, and every role file carries
    ``Launch default`` and ``Skills`` (``Launch by criticality`` only some), so the skipped cases are the ones
    the role files themselves leave out and nothing more."""
    assert ROLE_FILES, f"no kernel role file under {ROLES_DIR}"
    for label in LABELS:
        assert any(_lines(path.read_bytes(), label) for path in ROLE_FILES), (
            f"no kernel role file carries a '{label}' line: the routed cases would all skip")
    for label in ("Launch default", "Skills"):
        lacking = [path.name for path in ROLE_FILES if not _lines(path.read_bytes(), label)]
        assert lacking == [], f"role files without a '{label}' line: {lacking}"


@pytest.mark.parametrize("role, folder, label", _carried_cases())
def test_routed_each_generated_role_copy_carries_the_kernel_role_file_s_line_byte_for_byte(role, folder, label):
    kernel_file = ROLES_DIR / f"{role}.md"
    copy = support.REPO / folder / f"{role}.md"
    assert copy.is_file(), f"{copy.relative_to(support.REPO)} does not exist (kernel role file {kernel_file.name})"
    held = copy.read_bytes().split(b"\n")
    for line in _lines(kernel_file.read_bytes(), label):
        assert line in held, (
            f"{copy.relative_to(support.REPO)} has no line byte-equal to {kernel_file.relative_to(support.REPO)}'s "
            f"'{label}' line\nkernel: {line!r}\ncopy's '{label}' lines: {_lines(copy.read_bytes(), label)!r}")


# --- a hand edit is named as drifted, in a stand-in ------------------------------------------------------------------

AGENT = ".claude/agents/engineer.md"
SOURCE = ".rulesync/subagents/engineer.md"
STAND_IN_LINES = {
    "Launch default": "- **Launch default:** model claude-sonnet-5-5, effort high",
    "Launch by criticality": "- **Launch by criticality:** C3 model claude-opus-5-5, effort high; C0 model "
                             "claude-haiku-5-5, effort low",
    "Skills": "- **Skills:** test-driven-development, retrieval",
}
STAND_IN_ROLE = support.ROLE_BODY + "".join(line + "\n" for line in STAND_IN_LINES.values())


def _stand_in(base: Path) -> PortabilityBed:
    """``PortabilityBed`` (one kernel role, engineer; its template; the composed sources; the eight copies; a stand-in
    rulesync that writes the generated files the project holds) with the engineer's role file carrying the three
    labelled lines, and the composed sources and the generated agent carrying them as the role file has them, so the
    unedited project is consistent."""
    bed = PortabilityBed(base)
    support.write(bed.root / "template/governance/kernel/roles/engineer.md", STAND_IN_ROLE)
    body = support.composed_body(support.ENGINEER_TEMPLATE_BODY, STAND_IN_ROLE)
    for tree in (".rulesync", "template/.rulesync"):
        support.write(bed.root / tree / "subagents/engineer.md", support.composed_source(body=body))
    agent = "---\nname: engineer\n---\n\n" + body
    support.write(bed.root / AGENT, agent)
    support.write(bed.base / "made" / AGENT, agent)
    return bed


@pytest.fixture
def stand_in(tmp_path):
    return _stand_in(tmp_path / "bed")


def test_routed_the_unedited_stand_in_names_neither_the_generated_agent_nor_the_source(stand_in):
    """The control: with nothing edited the check names no finding, so a finding in the cases below is the edit's."""
    code, printed, stderr = stand_in.check()
    assert support.naming(printed["findings"], AGENT) == [] and support.naming(printed["findings"], SOURCE) == [], (
        f"the unedited stand-in names a file: {printed}")
    assert printed["findings"] == [] and code == 0, f"exit {code}: {printed}\nstderr: {stderr}"


@pytest.mark.parametrize("rel", [AGENT, SOURCE], ids=["generated-agent", "composed-source"])
@pytest.mark.parametrize("label", LABELS, ids=[label.replace(" ", "-").lower() for label in LABELS])
def test_routed_a_hand_edit_to_one_of_the_three_lines_is_named_as_drifted(stand_in, rel, label):
    path = stand_in.root / rel
    before = path.read_bytes()
    line = STAND_IN_LINES[label].encode()
    assert line in before.split(b"\n"), f"the stand-in's premise: {rel} holds the '{label}' line"
    path.write_bytes(before.replace(line, line + b" (edited by hand)"))
    assert path.read_bytes() != before, "the stand-in's premise: the edit changed the file"
    code, printed, stderr = stand_in.check()
    assert support.naming(printed["findings"], rel), f"no finding names {rel} after a hand edit of '{label}': {printed}"
    assert code != 0, f"the check exited 0 after a hand edit to {rel}'s '{label}' line: {printed}"
    other = SOURCE if rel == AGENT else AGENT
    assert support.naming(printed["findings"], other) == [], (
        f"the edit to {rel} is also named on {other}, which was not edited: {printed}")

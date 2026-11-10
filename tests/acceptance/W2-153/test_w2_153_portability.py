"""S3 and S4 for ``gov.adapters.portability`` on a fixture project, and S4's writer on this repository's templates.

The fixture (``w2_153_support.PortabilityBed``) mirrors the unit tests' project (``tests/unit/adapters/
test_portability.py``) in this repository's layout, with one kernel role (engineer) and S3's composition as amended
(DEC-1112 (3), 2026-11-10): its rulesync source is the rulesync front matter plus ``claudecode: skills:
[test-driven-development]``, then the body of ``templates/role-engineer.md``, one blank line, and the body of
``roles/engineer.md``. The check runs as ``python3 -m gov.adapters.portability`` in the project, with a stand-in
rulesync that writes the generated files the project holds; ``compose`` is called in a child process.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

import w2_153_support as support
from w2_153_support import TEMPLATE_STEMS, PortabilityBed

SOURCE = ".rulesync/subagents/engineer.md"


@pytest.fixture
def bed(tmp_path):
    return PortabilityBed(tmp_path / "bed")


def test_s3_s4_a_project_with_the_composed_source_and_the_eight_copies_is_reported_consistent(bed):
    code, printed, stderr = bed.check()
    assert printed["findings"] == [] and code == 0, f"exit {code}: {printed}\nstderr: {stderr}"


def test_s3_a_source_that_keeps_the_kernel_role_file_s_body_is_a_finding(bed):
    """The source as it was before W2-153: the role file's body alone, with no template's body before it (with the
    skills list)."""
    support.write(bed.source(), support.composed_source(body=support.ROLE_BODY))
    code, printed, _ = bed.check()
    assert support.naming(printed["findings"], SOURCE), f"no finding names {SOURCE}: {printed}"
    assert code != 0


def test_s3_a_source_with_the_template_s_body_alone_is_a_finding(bed):
    """S3 amended (DEC-1112 (3)): the template's body without the role file's after it (W2-153's first composition)
    leaves the agent without the role file's labelled fields, so it is a finding naming the source."""
    support.write(bed.source(), support.composed_source(body=support.ENGINEER_TEMPLATE_BODY))
    code, printed, _ = bed.check()
    assert support.naming(printed["findings"], SOURCE), f"no finding names {SOURCE}: {printed}"
    assert code != 0


@pytest.mark.parametrize("held", ["composed", "template-body-alone"])
def test_s3_compose_returns_the_source_s_full_text_and_the_check_accepts_it(bed, held):
    """``gov.adapters.portability.compose(root, role)`` (S3 amended's interface) returns the expected source's full
    text for the fixture's engineer: the source's rulesync front matter with ``claudecode.skills``, then the
    template's body, one blank line and the role file's body. It is the same whether the source already holds that
    text or still holds the template's body alone (the copies ACT's builder writes it over a stale source), and the
    check, given that text as the source, names no finding on it."""
    if held == "template-body-alone":
        support.write(bed.source(), support.composed_source(body=support.ENGINEER_TEMPLATE_BODY))
    made = bed.compose("engineer")
    assert made["exit"] == 0, (f"gov.adapters.portability.compose(root, 'engineer') could not be called "
                               f"(exit {made['exit']}):\n{made['stderr'][-1500:]}")
    assert made["type"] == "str", f"compose returned a {made['type']}, not the source's text"
    text = made["text"]
    assert text.startswith("---\n"), f"compose's text does not open with front matter: {text[:200]!r}"
    front, body = support.split_front(text)
    expected_front, _ = support.split_front(support.composed_source())
    assert front == expected_front, f"compose's front matter is {front!r}, not {expected_front!r}"
    assert body == support.ENGINEER_COMPOSED_BODY, (
        "compose's body is not the template's body, one blank line, then the role file's body\n"
        f"got: {body!r}\nexpected: {support.ENGINEER_COMPOSED_BODY!r}")
    support.write(bed.source(), text)
    code, printed, stderr = bed.check()
    assert support.naming(printed["findings"], SOURCE) == [], (
        f"the check names the source compose wrote: {printed}\nstderr: {stderr}")


def test_s3_the_skills_list_is_part_of_the_composition(bed):
    """With the skills list the source is consistent; the same source without it is a finding naming it."""
    code, printed, _ = bed.check()
    assert support.naming(printed["findings"], SOURCE) == [], f"the composed source is a finding: {printed}"
    support.write(bed.source(), support.composed_source(skills=None))
    code, printed, _ = bed.check()
    assert support.naming(printed["findings"], SOURCE), f"a source with no skills list is no finding: {printed}"
    assert code != 0


def test_s3_a_skills_list_at_the_top_level_is_a_finding(bed):
    """DEC-1112 (3): the list sits under ``claudecode: skills:``; rulesync 24.0.0 drops a top-level ``skills``, so
    the agent would preload nothing. With the list under ``claudecode`` the source is consistent; the same list at
    the top level (and none under ``claudecode``) is a finding naming the source."""
    code, printed, _ = bed.check()
    assert support.naming(printed["findings"], SOURCE) == [], f"the composed source is a finding: {printed}"
    support.write(bed.source(), support.composed_source(top_level=True))
    code, printed, _ = bed.check()
    assert support.naming(printed["findings"], SOURCE), f"a top-level skills list is no finding: {printed}"
    assert code != 0


def test_s4_a_changed_copy_and_a_missing_copy_are_findings(bed):
    changed, missing = ".claude/templates/role-reviewer.md", ".claude/templates/role-lead.md"
    support.write(bed.root / changed, support.kernel_template_text("role-reviewer") + "One more line.\n")
    (bed.root / missing).unlink()
    code, printed, _ = bed.check()
    for rel in (changed, missing):
        assert support.naming(printed["findings"], rel), f"no finding names {rel}: {printed}"
    assert code != 0


@pytest.mark.parametrize("stem, change", [
    ("role-engineer", lambda data: data + b"\n"),                      # one byte added at the end
    ("role-cto", lambda data: data.replace(b"\r\n", b"\n")),           # the CRLF line made LF
], ids=["trailing-newline", "line-ending"])
def test_s4_a_copy_differing_by_one_byte_is_a_finding(bed, stem, change):
    path = bed.copy(stem)
    path.write_bytes(change(path.read_bytes()))
    code, printed, _ = bed.check()
    assert support.naming(printed["findings"], f".claude/templates/{stem}.md"), f"no finding: {printed}"
    assert code != 0


def _written(out):
    """The files the writer wrote, by stem: under ``<dir>/`` or ``<dir>/.claude/templates/`` (the ticket leaves
    open which folder ``<dir>`` is; README, D-3)."""
    for folder in (out, out / ".claude" / "templates"):
        found = {path.stem: path for path in folder.glob("*.md")} if folder.is_dir() else {}
        if found:
            return folder, found
    return out, {}


def test_s4_the_writer_writes_the_eight_copies_byte_for_byte(tmp_path):
    """``python3 -m gov.adapters.portability --write-templates <dir>`` from this repository's root, on a temporary
    folder: the eight copies of ``template/governance/kernel/templates/``, byte for byte, and no other file."""
    out = tmp_path / "out"
    out.mkdir()
    done = subprocess.run([sys.executable, "-m", "gov.adapters.portability", "--write-templates", str(out)],
                          cwd=str(support.REPO), capture_output=True, text=True, timeout=support.COMMAND_TIMEOUT_S,
                          env=support.portability_env(tmp_path, RULESYNC_BIN="/nonexistent/rulesync"),
                          stdin=subprocess.DEVNULL)
    folder, found = _written(out)
    assert sorted(found) == sorted(TEMPLATE_STEMS), (
        f"the writer wrote {sorted(found)} in {folder} (exit {done.returncode}), not the eight copies\n"
        f"stderr: {done.stderr[-2000:]}")
    for stem, path in found.items():
        kernel = support.KERNEL_TEMPLATES / f"{stem}.md"
        assert path.read_bytes() == kernel.read_bytes(), f"{path} is not a byte copy of {kernel}"
    others = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file() and p.parent != folder)
    others += sorted(p.name for p in folder.iterdir() if p.is_file() and p.suffix != ".md")
    assert others == [], f"the writer wrote other files too: {others}"
    assert done.returncode == 0, f"the writer ended with exit {done.returncode}\nstderr: {done.stderr[-2000:]}"

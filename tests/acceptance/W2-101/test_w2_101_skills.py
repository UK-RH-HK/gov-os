"""W2-101: the skills' own text: success-1 (the parts), success-2 (the grep half), success-3 (the template),
failure-1 and failure-2 (the validator's halves).

Reading rules (README): a *section* is a level-2 heading; its text runs to the next level-1 or level-2 heading. The body
is what follows the front matter; its size limit is 150 lines with a 10 per cent tolerance (165). The five parts are
read as a heading (``#`` to ``###``) or a labelled line ``**<Part>:**``; the area's points as a labelled line. The skill
validator is the shared one (``gov.check.skill_validator``), run as a subprocess on a SKILL.md.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import pytest

import w2_101_support as s

BODY_LINES_AT_MOST = 165  # "about 150": the template's number with a 10 per cent tolerance
SKILLS = pytest.mark.parametrize("skill", s.SKILLS)
PART_CASES = [(skill, part) for skill in s.SKILLS for part in s.PARTS]
POINT_CASES = [(skill, point) for skill in s.SKILLS for point in s.POINTS[skill]]
PERMISSION_KEYS = ("allowed-tools", "allowed_tools", "permissions", "permission", "paths", "sandbox", "network",
                   "model", "effort", "allow", "deny")


def _validator(path, cwd):
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(s.SRC), os.environ.get("PYTHONPATH", "")])}
    done = subprocess.run([sys.executable, "-m", "gov.check.skill_validator", str(path)], capture_output=True,
                          text=True, cwd=str(cwd), env=env, timeout=60, stdin=subprocess.DEVNULL)
    try:
        findings = json.loads(done.stdout.strip().splitlines()[-1]).get("findings", [])
    except (ValueError, IndexError, AttributeError):
        findings = [{"code": "UNREADABLE", "key": None, "message": (done.stdout + done.stderr)[-300:]}]
    return done.returncode, findings


# success-1: each skill holds the five parts and the area's named points ---------------------------------------------------

@pytest.mark.parametrize("skill,part", PART_CASES)
def test_the_skill_states_each_of_the_five_parts(skill, part):
    text = s.read_skill(skill)
    assert s.has_line(text, s.part_line(part)), f"{skill}/SKILL.md has no heading or labelled line for {part}"


@pytest.mark.parametrize("skill,point", POINT_CASES)
def test_the_skill_states_each_of_the_areas_named_points_as_a_labelled_line(skill, point):
    text = s.read_skill(skill)
    assert s.has_line(text, s.labelled_line(point)), f"{skill}/SKILL.md has no labelled line '**{point}:**'"


# success-3: the one skill template ---------------------------------------------------------------------------------------

@SKILLS
def test_the_skill_validator_exits_0_on_the_skill(skill, tmp_path):
    code, findings = _validator(s.need(s.skill_dir(skill) / "SKILL.md"), tmp_path)
    assert code == 0 and findings == [], f"the validator exit {code}, findings {findings}"


@SKILLS
def test_the_front_matter_has_name_version_and_a_third_person_description(skill):
    front, _ = s.split_frontmatter(s.read_skill(skill))
    assert front is not None, "SKILL.md has no front matter"
    assert front.get("name") == skill, f"name is {front.get('name')!r}, expected {skill!r}"
    version = front.get("version")
    assert isinstance(version, str) and version, f"version is {version!r}: the validator wants a string at the top"
    meta = front.get("metadata") if isinstance(front.get("metadata"), dict) else {}
    assert str(meta.get("version", version)) == version, "metadata.version differs from version"
    description = front.get("description")
    assert isinstance(description, str) and description.strip(), "no description"
    words = re.findall(r"[A-Za-z']+", description)
    assert not {w.lower() for w in words} & {"i", "you", "your", "we", "our", "my", "me", "us"}, (
        f"the description speaks in the first or second person: {description!r}")
    first = words[0].lower() if words else ""
    assert first not in {"use", "write", "run", "check", "make", "create", "build", "apply", "follow", "read", "ask",
                         "help", "always", "never"}, f"the description opens with a command: {description!r}"
    assert re.search(r"\b(when|use[sd]?|for)\b", description, re.I), \
        f"the description does not say when to use the skill: {description!r}"


@SKILLS
def test_the_sections_stand_in_the_templates_order_with_sources_last(skill):
    assert s.section_problems(s.read_skill(skill)) == []


@SKILLS
def test_the_output_section_gives_the_twelve_fields(skill):
    out = s.section(s.read_skill(skill), r"output and handover")
    assert out is not None, "no Output and handover section"
    plain = " ".join(out.replace("`", "").split()).lower()
    assert all(field in plain for field in s.TWELVE) or "twelve fields" in plain, \
        "the section neither names the twelve fields nor says 'twelve fields'"


@SKILLS
def test_the_escalation_section_maps_to_p3_p2_p1_and_emergency(skill):
    esc = s.section(s.read_skill(skill), r"escalation")
    assert esc is not None, "no Escalation section"
    for rank in ("P3", "P2", "P1", "Emergency"):
        assert re.search(rf"\b{rank}\b", esc, re.I), f"Escalation does not mention {rank}"


@SKILLS
@pytest.mark.parametrize("title,pattern", [("Never", r"never\b"), ("Sources", r"sources\b")], ids=["Never", "Sources"])
def test_never_and_sources_have_content(skill, title, pattern):
    block = s.section(s.read_skill(skill), pattern)
    assert block is not None, f"no {title} section"
    assert block.strip(), f"the {title} section is empty"
    if title == "Never":
        assert s.list_items(block), "the Never section lists nothing"


@SKILLS
def test_the_body_is_about_150_lines(skill):
    body = s.split_frontmatter(s.read_skill(skill))[1]
    count = len(body.rstrip("\n").splitlines())
    assert count <= BODY_LINES_AT_MOST, f"the body is {count} lines (limit 150 with a tolerance of 10 per cent)"


@SKILLS
def test_every_reference_file_sits_at_most_one_folder_level_below_the_skill_folder(skill):
    folder = s.need(s.skill_dir(skill) / "SKILL.md").parent
    files = s.skill_files(folder)
    deeper = [str(f) for f in files if len(f.parts) > 2]
    assert not deeper, f"files more than one folder level below the skill folder: {deeper}"
    here = {f.name for f in files if len(f.parts) == 1}
    for expected in ("SKILL.md", s.SCENARIOS_FILE, s.CHECK_NAME):
        assert expected in here, f"{expected} is not in the skill folder itself"


@SKILLS
def test_a_long_body_with_no_reference_files_is_named_by_the_validator_and_a_short_one_is_not(skill, tmp_path):
    """failure-2's size half: a 400-line body and no reference files draws the validator's body-size finding (key
    ``body``); the same front matter over a short body does not."""
    front = s.front_block(s.read_skill(skill))
    folder = tmp_path / skill
    folder.mkdir()
    long_body = "\n".join(f"Line {n}: the method says to write the change before any commit and to check it first."
                          for n in range(400))
    (folder / "SKILL.md").write_text(front + "\n# Planted\n\n" + long_body + "\n", encoding="utf-8")
    code, findings = _validator(folder / "SKILL.md", tmp_path)
    sizes = [f for f in findings if f.get("code") == "SKILL_BODY_TOO_LONG"]
    assert code == 1 and sizes and sizes[0].get("key") == "body", f"{code}: {findings}"
    assert [p.name for p in folder.iterdir()] == ["SKILL.md"], "the planted copy has reference files"
    (folder / "SKILL.md").write_text(front + "\n# Planted\n\nA short body.\n", encoding="utf-8")
    _code, findings = _validator(folder / "SKILL.md", tmp_path)
    assert "SKILL_BODY_TOO_LONG" not in [f.get("code") for f in findings], findings


# failure-1 (the validator's half): a permission key in the front matter is named by the validator --------------------------

@SKILLS
def test_a_permission_key_in_the_front_matter_is_named_by_the_validator_and_the_real_skill_has_none(skill, tmp_path):
    text = s.read_skill(skill)
    assert _validator(s.need(s.skill_dir(skill) / "SKILL.md"), tmp_path) == (0, [])
    lines = text.split("\n")
    lines.insert(1, "allowed-tools: Bash")
    path = s.planted(tmp_path, "\n".join(lines), folder=skill)
    code, findings = _validator(path, tmp_path)
    named = [f for f in findings if f.get("key") == "allowed-tools"]
    assert code == 1 and named, f"the validator does not name the key allowed-tools: {code}: {findings}"


# success-2: the skill grants no permission (the grep half) --------------------------------------------------------------

@SKILLS
def test_the_front_matter_holds_no_permission_key(skill):
    front, _ = s.split_frontmatter(s.read_skill(skill))
    assert front is not None, "SKILL.md has no front matter"
    keys = {str(k).lower() for k in front} | {f"metadata.{str(k).lower()}" for k in (front.get("metadata") or {})}
    bad = sorted(k for k in keys if k.split(".")[-1] in PERMISSION_KEYS)
    assert not bad, f"the front matter holds permission keys: {bad}"


@SKILLS
def test_no_file_of_the_skill_folder_holds_a_permission_line(skill):
    """A grep of each skill's files for a line that begins ``allowed-tools:``, ``allow:``, ``permissions:`` and the
    like finds none. The check script (a ``.py`` file) holds those words as data and is read by test_w2_101_check."""
    folder = s.need(s.skill_dir(skill) / "SKILL.md").parent
    found = []
    for rel in s.skill_files(folder):
        if rel.suffix == ".py":
            continue
        text = (folder / rel).read_text(encoding="utf-8", errors="replace")
        found += [f"{rel}:{n}: {line.strip()}" for n, line in s.permission_lines(text)]
    assert not found, f"permission-granting lines in {skill}'s files: {found}"


@SKILLS
def test_no_file_of_the_skill_folder_is_a_settings_or_permission_file(skill):
    folder = s.need(s.skill_dir(skill) / "SKILL.md").parent
    odd = [str(rel) for rel in s.skill_files(folder)
           if re.search(r"settings|permission|\.rules?$|allowlist|sandbox", rel.name, re.I)]
    assert not odd, f"{skill} holds files that look like a permission or settings file: {odd}"

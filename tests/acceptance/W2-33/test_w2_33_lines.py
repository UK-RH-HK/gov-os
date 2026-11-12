"""W2-33 S2, S4, S5, S7: the line forms in every role file (the Interface's, word for word), parsed as W2-60a's
launcher parses them (``w2_33_support`` keeps the forms). One case per file of the nine required and of any other
``*.md`` the folder holds, so a tenth file is checked too; a README is not a role file.

Judged elsewhere (README.md): the launcher's plan printing the file's model and effort (W2-60a), the guard's refusal
of a QA write elsewhere and of two writers in one worktree (W2-60b), the generated agents (W2-153).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_33_support as W  # noqa: E402

FOLDER = W.roles_dir()
FILES = W.checked_names(FOLDER)


def _text(name):
    text = W.read(FOLDER, name)
    assert text is not None, f"{W.ROLES_REL}/{name}.md does not exist"
    return text


# ---------------------------------------------------------------------------------------------------- S2

@pytest.mark.parametrize("name", FILES)
def test_s2_role_file_has_version_launch_default_and_skills_lines(name):
    faults = W.lines_s2(name, _text(name))
    assert not faults, "\n".join(faults)


@pytest.mark.parametrize("name", FILES)
def test_s2_each_skill_a_role_file_names_exists(name):
    """The launcher refuses a skill with no SKILL.md; the folders searched are in ``w2_33_support.available_skills``."""
    text = _text(name)
    line, count = W.one_line(text, W.SKILLS_HEAD)
    assert count == 1 and W.SKILLS_LINE.fullmatch(line), f"{name}.md has no whole '- **Skills:** a, b' line to check"
    faults = W.skills_exist(name, text, W.available_skills())
    assert not faults, "\n".join(faults)


@pytest.mark.parametrize("name", ("orchestrator", "senior-engineer"))
def test_s2_the_ctos_and_the_senior_engineers_file_give_effort_high(name):
    line, count = W.one_line(_text(name), W.DEFAULT_HEAD)
    match = W.DEFAULT_LINE.fullmatch(line) if count == 1 else None
    assert match, f"{name}.md has no whole '- **Launch default:** model <id>, effort <e>' line"
    assert match.group(2) == "high", f"{name}.md gives effort {match.group(2)}; S2 wants high"


# ---------------------------------------------------------------------------------------------------- S4

@pytest.mark.parametrize("name", FILES)
def test_s4_role_file_states_the_work_order_word_for_word(name):
    faults = W.lines_s4(name, _text(name))
    assert not faults, "\n".join(faults)


_DENIAL = r"\b(denied|deny|denies|refus\w+|never|may not|must not|no reads?)\b"
_COUNTERPART = {
    "independent-test-designer": (r"\b(counterpart|engineer|implement\w*)\b",
                                  "the engineer's work (the implementation) on the same ticket"),
    "engineer": (r"\b(counterpart|test designer|acceptance tests?|tests?)\b",
                 "the test designer's work (the acceptance tests) on the same ticket"),
}


@pytest.mark.parametrize("name", sorted(_COUNTERPART))
def test_s4_allowed_paths_deny_reads_of_the_counterparts_work(name):
    """Each of the two files states, in its allowed paths, that reads of the other's work on the same ticket are denied."""
    pattern, what = _COUNTERPART[name]
    label, value = W.field_by_labels(_text(name), (r"allowed paths?",))
    assert label is not None, f"{name}.md has no `- **Allowed paths:**` line"
    parts = [part for part in W.statements(value)
             if re.search(r"\breads?\b", part, re.IGNORECASE) and re.search(r"\bwork\b", part, re.IGNORECASE)
             and re.search(pattern, part, re.IGNORECASE) and re.search(_DENIAL, part, re.IGNORECASE)]
    assert parts, (f"the allowed paths of {name}.md do not state that reads of {what} are denied "
                   f"(a statement with 'read', 'work', {pattern} and a denial)")


# ---------------------------------------------------------------------------------------------------- S5

@pytest.mark.parametrize("name", FILES)
def test_s5_role_file_states_one_writer_per_worktree_word_for_word(name):
    faults = W.lines_s5(name, _text(name))
    assert not faults, "\n".join(faults)


# ---------------------------------------------------------------------------------------------------- S7

@pytest.mark.parametrize("name", FILES)
def test_s7_launch_lines_equal_the_table(name):
    """Launch default, Launch by criticality (present only where RUBRIC-2 varies) and the kept Model tier line.
    A file beyond the nine has no row in the table: only its Model tier line is judged here."""
    faults = W.lines_s7(name, _text(name))
    assert not faults, "\n".join(faults)


def test_s7_no_role_file_states_the_through_d10_rule():
    faults = [fault for name in FILES if W.read(FOLDER, name) is not None
              for fault in W.lines_d10(name, W.read(FOLDER, name))]
    present = [name for name in W.NINE if W.read(FOLDER, name) is None]
    assert not present, f"the role files {present} do not exist, so the rule cannot be checked in them"
    assert not faults, "\n".join(faults)

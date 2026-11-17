"""W2-197 S3 to S7: the text that says memory first, its generated copies, and the facts (README, "The text").

Text checks on this tree's files; the brief cases run ``gov brief`` on a repository holding this tree's templates and
facts, with ``--store`` naming a folder that does not exist (no store is read, nothing reaches a model).
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path

import pytest
import yaml

import w2_197_support as s

REPO = s.REPO
SHIPPED = REPO / "src/gov/_shipped"
SKILL = REPO / s.RETRIEVAL_SKILL_REL


def _t0() -> str:
    return s.body(s.BRIEF_T0)


def _commands_section(text: str) -> list[str]:
    lines = text.split("\n")
    at = next((n for n, line in enumerate(lines) if line.startswith("## ") and "command" in line.lower()), None)
    assert at is not None, "brief.md has no Commands section"
    end = next((n for n in range(at + 1, len(lines)) if lines[n].startswith("## ")), len(lines))
    return lines[at + 1:end]


# --- S3: T-0 says memory first for everyone --------------------------------------------------------------------------

def test_s3_t0_ask_memory_first_names_retrieve_and_read_every_item():
    lines = _commands_section(_t0())
    asks = [line for line in lines if "ask memory first" in line.lower()]
    assert asks, "brief.md's Commands section has no 'Ask memory first:' line"
    line = asks[0]
    assert "{CMD:retrieve}" in line, f"the 'Ask memory first' line does not name {{CMD:retrieve}}: {line!r}"
    assert s.READ_EVERY_ITEM in s.fold(line), f"the 'Ask memory first' line lacks '{s.READ_EVERY_ITEM}': {line!r}"
    following = next((x for x in lines[lines.index(line) + 1:] if x.strip()), "")
    assert "search again once" in s.fold(following), f"the line after it is not the search-again-once line: {following!r}"


def test_s3_t0_holds_no_sandbox_split_for_retrieve():
    text = _t0()
    assert "no gov retrieve in the sandbox" not in s.fold(text), "brief.md still says no gov retrieve in the sandbox"
    split = s.retrieve_sandbox_split(text)
    assert not split, f"brief.md still splits retrieve by the sandbox: {split}"


def test_s3_t0_holds_the_memory_section_with_its_key():
    lines = _t0().split("\n")
    at = [n for n, line in enumerate(lines) if line.strip() == s.SECTION]
    assert at, f"brief.md has no section {s.SECTION!r}"
    end = next((n for n in range(at[0] + 1, len(lines)) if lines[n].startswith("## ")), len(lines))
    assert any(re.search(r"\{MEMORY_BLOCK(?::[^{}]*)?\}", line) for line in lines[at[0] + 1:end]), \
        "the memory section does not hold {MEMORY_BLOCK}"


@pytest.mark.parametrize("role", s.BRIEF_ROLES)
def test_s3_generated_brief_holds_no_question(role, tmp_path, repo, capsys):
    text = s.ok_brief(s.brief(capsys, repo, role, "--store", tmp_path / "no-store"))
    assert "{QUESTION}" not in text, f"gov brief {role} holds {{QUESTION}}"


@pytest.mark.parametrize("role", s.BRIEF_ROLES)
def test_s3_generated_brief_holds_no_unfilled_upper_slot(role, tmp_path, repo, capsys):
    """S3 as the lead answered (reading (b), ticket commit e485739a1): every ``{UPPER}`` slot a generated brief still
    holds is a form key this tree's keys.yaml lists (read at test time), and none is QUESTION. README, "Readings"."""
    keys = yaml.safe_load(s.KEYS.read_text(encoding="utf-8")).get("keys")
    assert isinstance(keys, list), "keys.yaml has no keys list"
    text = s.ok_brief(s.brief(capsys, repo, role, "--store", tmp_path / "no-store"))
    slots = sorted({re.match(r"\{([A-Z][A-Z0-9_]*)", slot).group(1) for slot in s.UNIT.findall(text)})
    assert "QUESTION" not in slots, f"gov brief {role} holds {{QUESTION}}"
    unknown = [slot for slot in slots if slot not in {str(key) for key in keys}]
    assert not unknown, f"gov brief {role} holds slots that are no key in keys.yaml: {unknown}"


# --- S4: the role templates ------------------------------------------------------------------------------------------

@pytest.mark.parametrize("stem", s.ROLE_TEMPLATE_STEMS)
def test_s4_role_template_holds_the_shared_memory_line(stem):
    text = (s.TEMPLATES / f"{stem}.md").read_text(encoding="utf-8")
    assert s.MEMORY_LINE in text, f"{stem}.md does not hold the shared memory line verbatim"
    split = s.retrieve_sandbox_split(s.body(s.TEMPLATES / f"{stem}.md"))
    assert not split, f"{stem}.md still splits retrieve by the sandbox: {split}"


def test_s4_role_cto_launching_work_opens_every_subagent_prompt_with_the_memory_block():
    lines = s.body(s.TEMPLATES / "role-cto.md").split("\n")
    at = next((n for n, line in enumerate(lines) if line.startswith("## ") and "launching work" in line.lower()), None)
    assert at is not None, "role-cto.md has no 'Launching work' section"
    end = next((n for n in range(at + 1, len(lines)) if lines[n].startswith("## ")), len(lines))
    units = [s.fold(line) for line in lines[at + 1:end] if "subagent" in line.lower() and "memory" in line.lower()]
    assert units, "role-cto.md's Launching work names no memory block for a subagent prompt"
    unit = units[0]
    wanted = {"ask memory first": "ask memory first" in unit,
              "read the whole bundle": "whole bundle" in unit or "every item" in unit,
              "search once more in its own words": "once more" in unit or "search again" in unit,
              "how many retrieves helped": "how many" in unit and "retriev" in unit and "help" in unit}
    missing = [name for name, held in wanted.items() if not held]
    assert not missing, f"role-cto.md's subagent memory block lacks {missing}: {unit!r}"


@pytest.mark.parametrize("role", ["engineer", "product-spec", "independent-auditor"])
def test_s4_brief_commands_table_has_a_retrieve_row(role, tmp_path, repo, capsys):
    text = s.ok_brief(s.brief(capsys, repo, role, "--store", tmp_path / "no-store"))
    assert any(re.match(r"^\|\s*retrieve\s*\|", line) for line in text.split("\n")), \
        f"gov brief {role}'s commands table has no retrieve row"


# --- S5: the retrieval skill -----------------------------------------------------------------------------------------

def _step_7(text: str) -> str:
    found = re.search(r"(?ms)^7\.\s.*?(?=^\d+\.\s|^## |\Z)", text)
    assert found, "the retrieval skill has no step 7"
    return found.group(0)


def test_s5_retrieval_skill_step_7_says_read_every_item():
    step = _step_7(SKILL.read_text(encoding="utf-8"))
    assert s.READ_EVERY_ITEM in s.fold(step), f"step 7 lacks '{s.READ_EVERY_ITEM}': {step[:300]!r}"


def test_s5_retrieval_skill_holds_the_shared_line_with_the_command():
    assert s.SKILL_MEMORY_LINE in SKILL.read_text(encoding="utf-8"), \
        "the retrieval skill does not hold the shared memory line with `gov retrieve \"<question>\"`"


# --- S6: the generated copies ----------------------------------------------------------------------------------------

def _marker(stem: str) -> str:
    return s.SECTION if stem == "brief" else s.MEMORY_LINE


@pytest.mark.parametrize("stem", ["brief", *s.ROLE_TEMPLATE_STEMS])
def test_s6_claude_template_copy_equals_its_kernel_template(stem):
    kernel = (s.TEMPLATES / f"{stem}.md").read_bytes()
    copy = REPO / ".claude/templates" / f"{stem}.md"
    assert copy.is_file() and copy.read_bytes() == kernel, f".claude/templates/{stem}.md differs from the kernel's"
    assert _marker(stem).encode() in kernel, f"the kernel's {stem}.md lacks the new memory text"


@pytest.mark.parametrize("rel", [f"{s.TEMPLATES_REL}/brief.md", f"{s.TEMPLATES_REL}/role-cto.md",
                                 s.RETRIEVAL_SKILL_REL])
def test_s6_shipped_copy_equals_its_source(rel):
    source, copy = REPO / rel, SHIPPED / rel
    assert copy.is_file() and copy.read_bytes() == source.read_bytes(), f"src/gov/_shipped/{rel} differs from {rel}"
    marker = s.SKILL_MEMORY_LINE if rel.endswith("SKILL.md") else _marker(Path(rel).stem)
    assert marker in source.read_text(encoding="utf-8"), f"{rel} lacks the new memory text"


@pytest.mark.parametrize("rel", [".rulesync/skills/retrieval/SKILL.md", "template/.rulesync/skills/retrieval/SKILL.md",
                                 ".claude/skills/retrieval/SKILL.md"])
def test_s6_retrieval_skill_copies_carry_the_new_step_7(rel):
    step = _step_7((REPO / rel).read_text(encoding="utf-8"))
    assert s.READ_EVERY_ITEM in s.fold(step), f"{rel}'s step 7 lacks '{s.READ_EVERY_ITEM}'"


def _composed_roles() -> list[str]:
    from gov.launch.launcher import ROLE_TEMPLATES

    return sorted(role for role, stem in ROLE_TEMPLATES.items()
                  if (REPO / ".rulesync/subagents" / f"{role}.md").is_file() and (s.TEMPLATES / f"{stem}.md").is_file())


@pytest.mark.parametrize("role", _composed_roles())
def test_s6_rulesync_subagent_equals_its_composition(role):
    from gov.adapters.portability import compose

    text = (REPO / ".rulesync/subagents" / f"{role}.md").read_text(encoding="utf-8")
    assert text == compose(REPO, role), f".rulesync/subagents/{role}.md is not compose(root, {role!r})"
    assert s.MEMORY_LINE in text, f".rulesync/subagents/{role}.md lacks the shared memory line"


# --- S7: facts, keys and the adopted facts ---------------------------------------------------------------------------

def test_s7_facts_retrieve_form_names_the_question_as_text():
    data = yaml.safe_load(s.FACTS.read_text(encoding="utf-8"))
    run = data["commands"]["retrieve"]["run"]
    assert run == 'gov retrieve --root {STORE_TREE} "<question>"', f"facts.yaml's retrieve form is {run!r}"


def test_s7_keys_drop_question_and_hold_memory_block():
    keys = yaml.safe_load(s.KEYS.read_text(encoding="utf-8")).get("keys")
    assert isinstance(keys, list), "keys.yaml has no keys list"
    assert "QUESTION" not in keys, "keys.yaml still holds QUESTION"
    assert "MEMORY_BLOCK" in keys, "keys.yaml does not hold MEMORY_BLOCK"


def test_s7_adopt_facts_writes_the_question_as_text(tmp_path):
    from gov.adopt import facts

    facts.write_default(tmp_path, datetime.date(2026, 11, 17))
    data = yaml.safe_load((tmp_path / "governance/project/facts.yaml").read_text(encoding="utf-8"))
    run = data["commands"]["retrieve"]["run"]
    assert run == 'gov retrieve "<question>"', f"gov adopt --facts writes the retrieve form {run!r}"


# --- F3: nothing else changes (a repository-state guard, README) -----------------------------------------------------

BASE = "067cd2946"  # the ticket's base on w2/integrate (EMERGENCY-2 6.1 build row): none of its implementation


def test_f3_gov_context_and_its_tests_are_untouched_since_the_base():
    import subprocess

    known = subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", f"{BASE}^{{commit}}"], capture_output=True)
    if known.returncode:
        pytest.skip(f"the base {BASE} is not in this clone")
    done = subprocess.run(["git", "-C", str(REPO), "diff", "--name-only", BASE, "--", "src/gov/context",
                           "tests/unit/context"], capture_output=True, text=True, check=True)
    changed = [line for line in done.stdout.splitlines() if line.strip()]
    assert not changed, f"gov context or its tests changed since {BASE}: {changed}"

"""W2-184 builder tests: the role file's ``Launch by criticality`` line (interface 2).

Regression evidence only (DEC-136): the line's forms, the refusals, and every kernel role file's real line.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import role  # noqa: E402

VERSION = "- **Version:** 1.2.3"
DEFAULT = "- **Launch default:** model claude-sonnet-5-5, effort high"
HEAD = "- **Launch by criticality:** "
PLAIN = ("C3 model claude-opus-5-5, effort high; C2 model claude-sonnet-5-5, effort medium; "
         "C1 model claude-sonnet-5-5, effort high; C0 model claude-haiku-5-5, effort low")
FULL = ("C3 model claude-opus-5-5, effort high; C2 model claude-opus-5-5, effort xhigh on FULL, "
        "model claude-sonnet-5-5, effort max otherwise; C1 model claude-sonnet-5-5, effort high; "
        "C0 model claude-haiku-5-5, effort low")


def _tree(tmp_path, *lines):
    folder = tmp_path / role.ROLES_REL
    folder.mkdir(parents=True)
    (folder / "engineer.md").write_text("# Engineer\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return tmp_path


def _read(tmp_path, *lines):
    return role.read_role(_tree(tmp_path, VERSION, DEFAULT, *lines), "engineer")


def test_a_role_file_with_no_line_has_no_table(tmp_path):
    assert _read(tmp_path)["by_criticality"] is None


def test_the_plain_form_gives_one_pair_for_every_profile(tmp_path):
    table = _read(tmp_path, HEAD + PLAIN)["by_criticality"]
    assert list(table) == ["C3", "C2", "C1", "C0"]
    assert table["C2"] == {"full": ("claude-sonnet-5-5", "medium"), "other": ("claude-sonnet-5-5", "medium")}
    assert table["C0"]["other"] == ("claude-haiku-5-5", "low")


def test_the_full_form_gives_a_pair_on_full_and_another_otherwise(tmp_path):
    table = _read(tmp_path, HEAD + FULL)["by_criticality"]
    assert table["C2"] == {"full": ("claude-opus-5-5", "xhigh"), "other": ("claude-sonnet-5-5", "max")}
    assert table["C3"]["full"] == table["C3"]["other"] == ("claude-opus-5-5", "high")


def test_the_default_line_is_read_as_before_beside_the_new_one(tmp_path):
    loaded = _read(tmp_path, HEAD + PLAIN)
    assert (loaded["model"], loaded["effort"]) == ("claude-sonnet-5-5", "high")
    assert role.launch_default(_tree(tmp_path / "x", VERSION, DEFAULT, HEAD + PLAIN), "engineer") == \
        ("claude-sonnet-5-5", "high")


def test_the_plan_reads_the_default_line_alone_even_when_the_new_line_is_malformed(tmp_path):
    tree = _tree(tmp_path, VERSION, DEFAULT, HEAD + "C3 nonsense")
    assert role.launch_default(tree, "engineer") == ("claude-sonnet-5-5", "high")


def _entries(*swaps):
    entries = ["C3 model claude-opus-5-5, effort high", "C2 model claude-sonnet-5-5, effort high",
               "C1 model claude-sonnet-5-5, effort high", "C0 model claude-haiku-5-5, effort low"]
    return entries, swaps


@pytest.mark.parametrize("line", (
    "C3 model claude-opus-5-5, effort high; C2 model claude-sonnet-5-5, effort high; "
    "C1 model claude-sonnet-5-5, effort high",  # C0 missing
    "C2 model claude-sonnet-5-5, effort high; C3 model claude-opus-5-5, effort high; "
    "C1 model claude-sonnet-5-5, effort high; C0 model claude-haiku-5-5, effort low",  # out of order
    "C3 model claude-opus-5-5, effort high; C3 model claude-opus-5-5, effort high; "
    "C1 model claude-sonnet-5-5, effort high; C0 model claude-haiku-5-5, effort low",  # twice
    PLAIN + "; C0 model claude-haiku-5-5, effort low",  # a fifth
    PLAIN.replace("effort low", "effort extreme"),
    PLAIN.replace("claude-haiku-5-5", "haiku"),
    PLAIN.replace("claude-haiku-5-5", "Claude-haiku"),
    PLAIN.replace("; ", ";"),
    PLAIN.replace("; ", ", "),
    PLAIN + " ",
    PLAIN.replace("C0", "C4"),
    PLAIN.replace("model claude-sonnet-5-5, effort medium", "model claude-sonnet-5-5, effort medium on FULL"),
    FULL.replace(" otherwise", ""),
    FULL.replace("on FULL, model claude-sonnet-5-5, effort max otherwise", "on FULL, model x, effort max otherwise"),
    FULL.replace("on FULL", "on STANDARD"),
    PLAIN.replace("C3 model claude-opus-5-5, effort high", "C3 model claude-opus-5-5, effort high on FULL, "
                  "model claude-opus-5-5, effort high otherwise, effort low"),
    "",
))
def test_a_line_of_another_form_refuses_naming_the_role_file(tmp_path, line):
    with pytest.raises(GovError, match="Launch by criticality") as caught:
        _read(tmp_path, HEAD + line)
    assert caught.value.code == "LAUNCH_REFUSED"
    assert f"{role.ROLES_REL}/engineer.md" in caught.value.message


def test_a_second_line_refuses(tmp_path):
    with pytest.raises(GovError, match="Launch by criticality"):
        _read(tmp_path, HEAD + PLAIN, HEAD + PLAIN)


def test_an_indented_line_is_a_line_of_the_head_and_refuses(tmp_path):
    with pytest.raises(GovError, match="Launch by criticality"):
        _read(tmp_path, "  " + HEAD + PLAIN)


@pytest.mark.parametrize("path", sorted((REPO / role.ROLES_REL).glob("*.md")), ids=lambda p: p.stem)
def test_every_kernel_role_file_s_line_parses(path, tmp_path):
    text = path.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.lstrip().startswith("- **Launch by criticality:**")]
    folder = tmp_path / role.ROLES_REL
    folder.mkdir(parents=True)
    # the role file as it is, read under the role's own name
    (folder / f"{path.stem}.md").write_bytes(path.read_bytes())
    table = role.read_by_criticality(tmp_path, path.stem)
    if not lines:
        assert table is None
        return
    assert list(table) == ["C3", "C2", "C1", "C0"]
    for entry in table.values():
        assert set(entry) == {"full", "other"}
        for model, effort in entry.values():
            assert model.startswith("claude-") and effort in role.EFFORTS


def test_the_qa_engineer_s_c2_is_the_full_form():
    table = role.read_by_criticality(REPO, "qa-engineer")
    assert table["C2"] == {"full": ("claude-opus-5-5", "high"), "other": ("claude-sonnet-5-5", "high")}


def test_the_engineer_s_table_is_the_kernel_s():
    table = role.read_by_criticality(REPO, "engineer")
    assert table["C3"]["other"] == ("claude-opus-5-5", "high")
    assert table["C0"]["other"] == ("claude-haiku-5-5", "low")

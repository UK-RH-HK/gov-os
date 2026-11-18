"""W2-195 (DAEO-d8df) S3, the brief's half: ``gov brief`` refuses ``BRIEF_JUDGING_RULE_MISSING`` for a judging brief
(the reviewer's and probe's, as independent-auditor; the QA engineer's; the lead's review run) whose installed skill
is missing, has no sections 1 to 3, or whose preloaded copy is missing or of another version (DEC-1204 (5)).

Regression evidence only (DEC-136), on the planted repository of ``test_w2_195_inject``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_w2_195_inject import (JUDGING, KERNEL_REL, PRELOADED_REL, VERSION, bumped, kernel_bytes,  # noqa: E402
                                plant, rulesync_form)

from gov.brief.build import build  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.cli.main import main  # noqa: E402

CODE = "BRIEF_JUDGING_RULE_MISSING"


def _kernel_removed(root: Path) -> None:
    (root / KERNEL_REL).unlink()


def _preloaded_removed(root: Path) -> None:
    (root / PRELOADED_REL).unlink()


def _preloaded_other_version(root: Path) -> None:
    copy = root / PRELOADED_REL
    copy.write_bytes(copy.read_bytes().replace(f'version: "{VERSION}"'.encode(), b'version: "0.9.0"'))
    assert b"0.9.0" in copy.read_bytes()


def _preloaded_no_version(root: Path) -> None:
    copy = root / PRELOADED_REL
    copy.write_bytes(copy.read_bytes().replace(f'  version: "{VERSION}"\n'.encode(), b""))
    assert b"version" not in copy.read_bytes().split(b"\n---\n")[0]


def _no_sections(root: Path) -> None:
    path = root / KERNEL_REL
    path.write_bytes(path.read_bytes().replace(b"## 1. The threat model", b"## One. The threat model"))


def _first_heading_reworded(root: Path) -> None:
    path = root / KERNEL_REL
    path.write_bytes(path.read_bytes().replace(b"## 1. The threat model\n", b"## 1. Threat model\n"))


def _fourth_heading_reworded(root: Path) -> None:
    path = root / KERNEL_REL
    path.write_bytes(path.read_bytes().replace(b"## 4. Doing it\n", b"## 4. How to do it\n"))


def _kernel_no_version(root: Path) -> None:
    path = root / KERNEL_REL
    data = path.read_bytes().replace(f'version: "{VERSION}"\nmetadata:\n  version: "{VERSION}"\n'.encode(), b"")
    assert b"version" not in data.split(b"\n---\n")[0]
    path.write_bytes(data)


BREAKS = {"kernel-file-removed": _kernel_removed, "preloaded-copy-removed": _preloaded_removed,
          "preloaded-copy-other-version": _preloaded_other_version, "preloaded-copy-no-version": _preloaded_no_version,
          "kernel-file-without-sections-1-to-3": _no_sections, "kernel-file-without-version": _kernel_no_version,
          "kernel-file-first-heading-reworded": _first_heading_reworded,
          "kernel-file-fourth-heading-reworded": _fourth_heading_reworded}


@pytest.mark.parametrize("role, run", JUDGING)
@pytest.mark.parametrize("name", sorted(BREAKS))
def test_a_judging_brief_without_the_skill_or_of_another_version_is_refused_by_name(tmp_path, role, run, name):
    root = plant(tmp_path)
    BREAKS[name](root)
    with pytest.raises(GovError) as raised:
        build(root, role, "W2-900", run=run)
    assert raised.value.code == CODE


@pytest.mark.parametrize("role, run", JUDGING)
def test_the_same_briefs_with_the_skill_pass(tmp_path, role, run):
    assert build(plant(tmp_path), role, "W2-900", run=run)["findings"] == []


@pytest.mark.parametrize("role, run", [("engineer", None), ("lead", "build")])
@pytest.mark.parametrize("name", sorted(BREAKS))
def test_a_brief_that_judges_nothing_is_not_checked(tmp_path, role, run, name):
    root = plant(tmp_path)
    BREAKS[name](root)
    assert build(root, role, "W2-900", run=run)["findings"] == []


def _args(role: str, run: str | None, root: Path) -> list[str]:
    return ["brief", role, "W2-900", "--root", str(root), *(["--run", run] if run else [])]


@pytest.mark.parametrize("role, run", JUDGING)
def test_the_command_refuses_with_the_code_and_prints_no_brief(tmp_path, capsys, role, run):
    root = plant(tmp_path)
    _preloaded_removed(root)
    assert main([*_args(role, run, root), "--json"]) != 0
    envelope = json.loads(capsys.readouterr().out)
    assert envelope["ok"] is False and envelope["error"]["code"] == CODE
    assert main(_args(role, run, root)) != 0
    out, err = capsys.readouterr()
    assert out == "" and CODE in err


def test_the_command_prints_a_judging_brief_with_the_skill(tmp_path, capsys):
    root = plant(tmp_path)
    assert main(_args("qa-engineer", None, root)) == 0
    third = [line for line in kernel_bytes().decode("utf-8").split("\n") if line.startswith("## 3. ")]
    assert len(third) == 1 and third[0] in capsys.readouterr().out


def test_the_refusal_names_what_is_missing(tmp_path):
    root = plant(tmp_path)
    other = bumped(VERSION)
    (root / PRELOADED_REL).write_bytes(rulesync_form(kernel_bytes()).replace(f'"{VERSION}"'.encode(),
                                                                             f'"{other}"'.encode()))
    with pytest.raises(GovError) as raised:
        build(root, "independent-auditor", "W2-900")
    assert f"version {other}," in raised.value.message and f"version {VERSION}" in raised.value.message
    assert PRELOADED_REL in raised.value.message

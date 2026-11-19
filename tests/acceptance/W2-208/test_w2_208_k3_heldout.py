"""K3: no code path of the kit writes a ``Read`` deny for a held-out path; ``write_read_rules`` is retired;
``held-out.yaml`` and ``load_held_out`` stay as they are (EMERGENCY-2 2.7; DEC-1217 (6))."""

from __future__ import annotations

import json
import re

import pytest

import w2_208_support as support

HELD_OUT_STEP = re.compile(r"held[-_ ]?out[ _]step|HELD_OUT_STEP", re.I)


def test_k3_write_read_rules_is_no_longer_defined(tmp_path, sandbox):
    done = support.python(tmp_path, sandbox, "import gov.util.heldout as h; print(hasattr(h, 'write_read_rules'))")
    assert done.returncode == 0, f"gov.util.heldout cannot be imported\n{done.describe()}"
    assert done.stdout.strip() == "False", "gov.util.heldout still defines write_read_rules"


def test_k3_load_held_out_still_returns_the_paths_and_refuses_a_malformed_file(tmp_path, sandbox):
    good, bad = tmp_path / "good", tmp_path / "bad"
    support.write(good, support.HELD_OUT_REL, support.held_out_text())
    support.write(bad, support.HELD_OUT_REL, "held_out_paths:\n  - relative/path\n")
    code = ("import json, sys\n"
            "from gov.util.heldout import load_held_out, HeldOutError\n"
            f"paths = load_held_out({str(good)!r})\n"
            "try:\n"
            f"    load_held_out({str(bad)!r}); refused = False\n"
            "except HeldOutError:\n"
            "    refused = True\n"
            "print(json.dumps({'paths': paths, 'refused': refused}))\n")
    done = support.python(tmp_path, sandbox, code)
    assert done.returncode == 0, f"load_held_out could not be called\n{done.describe()}"
    found = json.loads(done.stdout)
    assert found == {"paths": list(support.HELD_OUT), "refused": True}, f"load_held_out changed: {found}"


@pytest.mark.parametrize("form", ["well-formed", "malformed"])
def test_k3_generate_with_a_held_out_file_writes_no_read_line_and_runs_no_held_out_step(tmp_path, sandbox, form):
    project = support.template_project(tmp_path / "product")
    support.write(project, support.HELD_OUT_REL,
                  support.held_out_text() if form == "well-formed" else "held_out_paths: not a list\n")
    done = support.generate(project, sandbox)
    assert done.returncode == 0, f"`gov adapters generate` failed beside a {form} held-out file\n{done.describe()}"
    assert not HELD_OUT_STEP.search(done.output), f"`gov adapters generate` mentions the held-out step\n{done.describe()}"
    settings = support.read_settings(project)
    assert not support.read_lines_starting_read(settings), (
        f"`gov adapters generate` wrote `Read(` lines: {support.read_lines_starting_read(settings)}")


@pytest.mark.parametrize("form", ["well-formed", "malformed"])
def test_k3_the_adapter_check_applies_no_held_out_step(tmp_path, sandbox, form):
    project = support.template_project(tmp_path / "product", registry=True)
    done = support.generate(project, sandbox)
    assert done.returncode == 0, f"fixture: `gov adapters generate` failed\n{done.describe()}"
    settings_path = project / support.SETTINGS_REL
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    deny, _allow = support.permission_lines(settings)
    if any(line.startswith("Read(") for line in deny):  # the settings as a kit without the step generates them
        settings["permissions"]["deny"] = [line for line in deny if not line.startswith("Read(")]
        settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    support.write(project, support.HELD_OUT_REL,
                  support.held_out_text() if form == "well-formed" else "held_out_paths: not a list\n")
    before = settings_path.read_bytes()
    checked, findings = support.portability(project, sandbox)
    assert findings is not None, f"the adapter check printed no findings document\n{checked.describe()}"
    about_settings = [item for item in findings if item.get("file") == support.SETTINGS_REL
                      or str(item.get("code", "")).startswith("HELD_OUT")]
    assert not about_settings, (
        f"the adapter check applies a held-out step to the settings beside a {form} held-out file: {about_settings}")
    assert not HELD_OUT_STEP.search(checked.output), f"the adapter check mentions the held-out step\n{checked.describe()}"
    assert settings_path.read_bytes() == before, "the adapter check changed the project's settings"
    assert not support.read_lines_starting_read(support.read_settings(project)), "a `Read(` line is in the settings"


def test_k3_update_leaves_no_read_line_and_does_not_mention_the_held_out_step(updated_013):
    done = updated_013["run"]
    assert done.returncode == 0, f"`gov update {support.B} --json` did not exit 0\n{done.describe()}"
    settings = support.read_settings(updated_013["project"])
    assert not support.read_lines_starting_read(settings), (
        f"`Read(` lines are in the settings after the update: {support.read_lines_starting_read(settings)}")
    assert not HELD_OUT_STEP.search(done.output), f"`gov update` mentions the held-out step\n{done.describe()}"

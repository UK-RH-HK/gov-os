"""W1-38, the round of DEC-635 (DEC-641), revised by DEC-1217 (6): no held-out step after generation.

Rewrite-Reason: DEC-1217 (6), EMERGENCY-2 2.7; W2-208 K3: the kit writes no ``Read`` deny for a held-out path. The
round of DEC-635 held a project's settings to "rulesync generate, then the held-out step" (one ``Read`` deny rule per
held-out path, written by ``python3 -m gov.util.heldout``) and the adapter/model-portability check applied the same
step inside its temporary generation. Under EMERGENCY-2 2.7 a hidden set is protected by the transcript scan, not by a
deny: the step retires (``write_read_rules`` is no longer defined, nor called by ``gov adapters generate`` or the check),
while ``held-out.yaml`` and ``load_held_out`` stay. The cases are turned to the decided state and keep what still
holds: a project with a held-out file is compared as rulesync alone generates it (green), a ``Read`` deny rule of the
old step has no source (red on the settings), a broken held-out file is no finding of the check, the old generator
writes nothing, and no output carries a held-out path (DEC-635, DEC-641). The old cases that pinned the step
(``TestSettingsAfterTheHeldOutStep``, ``TestStepRepeated``, the step's half of ``TestHeldOutStepThroughGovCheck``, and
``HELD_OUT_STEP_FAILED`` in ``TestBrokenHeldOutFile``) are replaced by the cases below.

Every case builds a stand-in project under pytest's ``tmp_path`` as the suite's other cases do (the template's
sources, the kernel, the tool registry, the check's declaration) and runs the real rulesync there (found as the suite
finds it: ``support.RULESYNC_BIN``, skipped when it is not installed). The held-out file is a stand-in written by the
case; the paths it names are invented under the case's temporary folder. The file's location and key are read from
``gov.util.heldout``'s own constants, never retyped here.

Behaviour is asserted through the declared command's exit code and what it prints, and through ``gov check --json``.
"""

from __future__ import annotations

import functools
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import w1_38_support as support

needs_rulesync = pytest.mark.needs_rulesync

GENERATOR = ("python3", "-m", "gov.util.heldout")   # the retired step's old entry point: it writes nothing now
SRC = support.REPO_ROOT / "src"


# ---------------------------------------------------------------------------
# The stand-in project's held-out file and the generator's step
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def _names() -> dict:
    """``gov.util.heldout``'s own constants: where a project holds its held-out
    file and the key in it. Read in a fresh interpreter with this worktree's
    ``src`` first, so no other tree's code answers."""
    code = (
        "import json, gov, gov.util.heldout as h\n"
        "print(json.dumps({'config': h.CONFIG_REL, 'key': h.CONFIG_KEY, 'code': gov.__file__}))"
    )
    done = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60,
        env={**os.environ, "PYTHONPATH": str(SRC)}, stdin=subprocess.DEVNULL,
    )
    assert done.returncode == 0, f"the generator's module cannot be imported: {done.stderr}"
    names = json.loads(done.stdout)
    assert Path(names["code"]).resolve().is_relative_to(SRC.resolve()), (
        f"the generator ran from {names['code']}, not from this worktree's src"
    )
    return names


def _assert_stand_in(project: Path) -> None:
    """The project is a temporary one: never this repository, never a folder of it."""
    resolved, repo = project.resolve(), support.REPO_ROOT.resolve()
    assert resolved != repo and not resolved.is_relative_to(repo) and not repo.is_relative_to(resolved), (
        "the case would touch this repository's own files; it works on a temporary project only"
    )


def _held_out_file(project: Path) -> Path:
    _assert_stand_in(project)
    return project / _names()["config"]


def _write_held_out_file(project: Path, paths: list[str]) -> Path:
    """The stand-in held-out file, in its stated shape (DEC-218): a list of
    absolute paths under the generator's key."""
    path = _held_out_file(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({_names()["key"]: list(paths)}, sort_keys=False), encoding="utf-8")
    return path


def _environment(project: Path) -> dict[str, str]:
    """A session's ``CLAUDE_PROJECT_DIR`` names the repository the session
    works in; here the project is the stand-in, for the check and the old
    generator's entry point alike."""
    return {"CLAUDE_PROJECT_DIR": str(project)}


def _settings_bytes(project: Path) -> bytes:
    _assert_stand_in(project)
    return (project / support.SETTINGS_REL).read_bytes()


def _deny_rules(project: Path) -> list[str]:
    return list(support.load_settings(project).get("permissions", {}).get("deny", []))


def _old_step_rules(paths: list[str]) -> list[str]:
    """The ``Read`` deny rules the retired step wrote, in its form ``Read(/<path>/**)``."""
    return [f"Read(/{path}/**)" for path in paths]


def _plant_old_step_rules(project: Path, paths: list[str]) -> list[str]:
    rules = _old_step_rules(paths)

    def add(settings):
        settings.setdefault("permissions", {}).setdefault("deny", []).extend(rules)

    support.edit_settings(project, add)
    return rules


def _check(project: Path) -> subprocess.CompletedProcess:
    """The declared command, run in the stand-in project."""
    _assert_stand_in(project)
    return support.run_portability_check(project, env_override=_environment(project))


def _findings(result: subprocess.CompletedProcess) -> list:
    """The findings the check printed (its standard output is one JSON object
    with a list ``findings``, as every other case of the suite reads it
    through ``gov check``)."""
    try:
        printed = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise AssertionError(
            f"the check printed no result (exit {result.returncode}): it stopped without a finding\n"
            f"standard error ends: {result.stderr[-300:]!r}"
        ) from None
    findings = printed.get("findings") if isinstance(printed, dict) else None
    assert isinstance(findings, list), "the check's result holds no list of findings"
    return findings


def _named(project: Path, result: subprocess.CompletedProcess) -> set[str]:
    """The files of the project the check's findings name."""
    return support.named_files(project, json.dumps(_findings(result)))


def _assert_no_stand_in_path(text: str, paths: list[str], what: str) -> None:
    """DEC-635, DEC-641: no finding, message or log line carries a held-out
    path. The failure message does not repeat the text (DEC-604)."""
    carried = [index for index, path in enumerate(paths) if path in text]
    assert not carried, (
        f"{what} carries {len(carried)} of the {len(paths)} stand-in held-out path(s) "
        f"(number {', '.join(str(index + 1) for index in carried)} of the stand-in file)"
    )


def _assert_green(project: Path, paths: list[str], what: str) -> None:
    result = _check(project)
    output = support.output_of(result)
    _assert_no_stand_in_path(output, paths, f"the check's output ({what})")
    named = _named(project, result)
    assert support.SETTINGS_REL not in named, (
        f"{what}: the findings name the project's settings file although it is what "
        f"rulesync generates; they name {sorted(named)}"
    )
    assert result.returncode == 0 and not _findings(result), (
        f"{what}: nothing differs, but the check is not green (exit {result.returncode}): {output}"
    )


def _assert_red_on_the_settings(project: Path, paths: list[str], what: str) -> None:
    result = _check(project)
    output = support.output_of(result)
    _assert_no_stand_in_path(output, paths, f"the check's output ({what})")
    assert result.returncode != 0, f"{what}, but the check is green: {output}"
    named = _named(project, result)
    assert named == {support.SETTINGS_REL}, (
        f"{what}: the findings must name the project's settings file and no other file; "
        f"they name {sorted(named)}"
    )


def _gov_check(project: Path, sandbox):
    """``(check entry, family entry, run)`` of the family after ``gov check --json``."""
    run = support.run_gov(project, sandbox, "check", "--json")
    entry, family = support.portability_entries(support.check_result(run))
    return entry, family, run


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def stand_in_paths(tmp_path):
    """Two absolute paths invented for the case, outside the stand-in project.
    Nothing exists there and nothing is written there."""
    return [str(tmp_path / "stand-in-held-out" / name) for name in ("first", "second")]


# ===================================================================
# A project with a held-out file: its settings are what rulesync generates
# ===================================================================

class TestNoHeldOutStep:
    """DEC-1217 (6), EMERGENCY-2 2.7 (W2-208 K3): the check holds a project's settings to what rulesync alone generates,
    whether or not the project has a held-out file."""

    @needs_rulesync
    def test_generated_settings_beside_a_held_out_file_are_green(self, generated_project, stand_in_paths):
        """Rewrite-Reason: DEC-1217 (6), W2-208 K3: the held-out file adds no rule (was
        ``test_step_never_run_is_red_on_the_settings``)."""
        _write_held_out_file(generated_project, stand_in_paths)
        _assert_green(generated_project, stand_in_paths,
                      "the project has a held-out file and its settings are what rulesync generates")
        assert not [rule for rule in _deny_rules(generated_project) if rule.startswith("Read(")], (
            "the settings rulesync generates hold a Read deny rule")

    @needs_rulesync
    def test_read_deny_rules_of_the_old_step_are_red_on_the_settings(self, generated_project, stand_in_paths):
        """Rewrite-Reason: DEC-1217 (6), W2-208 K3: a Read deny rule the old step wrote has no source now (was
        ``test_generated_then_the_step_is_green``)."""
        _write_held_out_file(generated_project, stand_in_paths)
        _plant_old_step_rules(generated_project, stand_in_paths)
        _assert_red_on_the_settings(
            generated_project, stand_in_paths,
            "the project's settings carry the old held-out step's Read deny rules",
        )

    @needs_rulesync
    def test_without_a_held_out_file_generated_settings_are_green(self, generated_project):
        assert not os.path.lexists(_held_out_file(generated_project)), (
            "the stand-in project as built holds a held-out file; the case needs one without"
        )
        result = _check(generated_project)
        assert result.returncode == 0 and not _findings(result), (
            f"a project without a held-out file, as rulesync generates it, is not green: "
            f"{support.output_of(result)}"
        )

    @needs_rulesync
    def test_the_old_generator_writes_no_rule(self, generated_project, stand_in_paths):
        """Rewrite-Reason: DEC-1217 (6), W2-208 K3: ``python3 -m gov.util.heldout`` no longer writes Read deny rules
        (was ``TestStepRepeated``)."""
        _write_held_out_file(generated_project, stand_in_paths)
        before = _settings_bytes(generated_project)
        done = subprocess.run(
            list(GENERATOR), capture_output=True, text=True, timeout=60, cwd=str(generated_project),
            env={**os.environ, "PYTHONPATH": str(SRC), **_environment(generated_project)},
            stdin=subprocess.DEVNULL,
        )
        _assert_no_stand_in_path(done.stdout + done.stderr, stand_in_paths, "the old generator's output")
        assert _settings_bytes(generated_project) == before, (
            "python3 -m gov.util.heldout still writes into the project's settings"
        )


# ===================================================================
# A broken held-out file is no finding of the check, and prints no path
# ===================================================================

def _unparsable(key, paths):
    return f'{key}:\n  - "{paths[0]}\n  - [\n'.encode()            # a quote and a bracket left open


def _other_key(key, paths):
    return yaml.safe_dump({f"not_{key}": list(paths)}).encode()    # the stated key is missing


def _not_a_list(key, paths):
    return yaml.safe_dump({key: paths[0]}).encode()                # one path, not a list of paths


def _entry_not_absolute(key, paths):
    return yaml.safe_dump({key: [paths[0], "stand-in/relative"]}).encode()


def _key_written_twice(key, paths):
    return f"{key}:\n  - {paths[0]}\n{key}:\n  - {paths[1]}\n".encode()


def _not_utf_8(key, paths):
    return f"{key}:\n  - {paths[0]}\n".encode() + b"# \xff\xfe\xfa\n"


# Every form but the folder holds a stand-in path as text.
BROKEN = {
    "unparsable-yaml": _unparsable,
    "stated-key-missing": _other_key,
    "not-a-list": _not_a_list,
    "entry-not-an-absolute-path": _entry_not_absolute,
    "key-written-twice": _key_written_twice,
    "not-utf-8": _not_utf_8,
    "a-folder-in-its-place": None,
}


class TestBrokenHeldOutFile:
    """DEC-218: the held-out file's shape is ``load_held_out``'s to refuse (``gov memaudit`` reads it); the check
    applies no step to it, so a broken file is no finding of the check, and no output carries a stand-in path."""

    @needs_rulesync
    @pytest.mark.parametrize("form", sorted(BROKEN))
    def test_broken_file_is_no_finding_and_no_path_is_printed(
        self, generated_project, stand_in_paths, form,
    ):
        """Rewrite-Reason: DEC-1217 (6), W2-208 K3: the check no longer applies the held-out step, so a broken file
        no longer gives ``HELD_OUT_STEP_FAILED`` (was ``test_broken_file_is_not_green_and_no_path_is_printed``)."""
        path = _held_out_file(generated_project)
        path.parent.mkdir(parents=True, exist_ok=True)
        if BROKEN[form] is None:
            path.mkdir()
            (path / "inside").write_text("a folder where the file is expected\n", encoding="utf-8")
        else:
            content = BROKEN[form](_names()["key"], stand_in_paths)
            assert stand_in_paths[0].encode() in content, "the broken form must hold a stand-in path as text"
            path.write_bytes(content)

        result = _check(generated_project)
        _assert_no_stand_in_path(support.output_of(result), stand_in_paths,
                                 f"the check's output (held-out file broken: {form})")
        codes = [finding.get("code") for finding in _findings(result) if isinstance(finding, dict)]
        assert not [code for code in codes if str(code).startswith("HELD_OUT")], (
            f"the held-out file is broken ({form}) and the check applies a held-out step: {codes}"
        )
        assert result.returncode == 0 and not codes, (
            f"the held-out file is broken ({form}) and the check, which reads no held-out file, is not green: {codes}"
        )


# ===================================================================
# The same through gov check
# ===================================================================

class TestHeldOutFileThroughGovCheck:
    """``gov check --json`` shows what the declared command gave."""

    @needs_rulesync
    def test_gov_check_is_green_beside_a_held_out_file(self, generated_project, sandbox, stand_in_paths):
        """Rewrite-Reason: DEC-1217 (6), W2-208 K3: green with the settings rulesync generates (was
        ``test_gov_check_is_green_after_the_apply_procedure``)."""
        _write_held_out_file(generated_project, stand_in_paths)
        entry, family, run = _gov_check(generated_project, sandbox)
        _assert_no_stand_in_path(run.describe(), stand_in_paths, "gov check's output")
        assert (entry.get("status"), family.get("status")) == (support.GREEN, support.GREEN), (
            f"the settings are what rulesync generates beside a held-out file, but gov check shows the check as "
            f"{entry.get('status')!r} and the family as {family.get('status')!r}\n{run.describe()}"
        )

    @needs_rulesync
    def test_gov_check_is_red_when_the_old_steps_rules_are_there(self, generated_project, sandbox, stand_in_paths):
        """Rewrite-Reason: DEC-1217 (6), W2-208 K3: a Read deny rule of the old step is a rule with no source (was
        ``test_gov_check_is_red_when_a_rule_is_lost``)."""
        _write_held_out_file(generated_project, stand_in_paths)
        _plant_old_step_rules(generated_project, stand_in_paths)
        entry, family, run = _gov_check(generated_project, sandbox)
        _assert_no_stand_in_path(run.describe(), stand_in_paths, "gov check's output")
        assert (entry.get("status"), family.get("status")) == (support.RED, support.RED), (
            f"the settings carry the old held-out step's Read deny rules, but gov check shows the check as "
            f"{entry.get('status')!r} and the family as {family.get('status')!r}\n{run.describe()}"
        )
        named = support.named_files(generated_project, json.dumps(entry.get("findings")))
        assert named == {support.SETTINGS_REL}, (
            f"the findings must name the project's settings file and no other file; "
            f"they name {sorted(named)}\n{run.describe()}"
        )

"""W1-38, the round of DEC-635 (DEC-641): the held-out step after generation.

A project's settings hold one ``Read`` deny rule per held-out path (DEC-162).
No rulesync source names a held-out path: the rules are written into the
settings after generation, by the existing generator
``python3 -m gov.guard.heldout`` run in the project, from the project's
held-out file (DEC-218). The owner's apply procedure is therefore "rulesync
generate, then the generator", and the adapter/model-portability check holds
the project's settings to exactly that: inside its temporary generation it
applies the same step before it compares, when and only when the project has a
held-out file.

Every case builds a stand-in project under pytest's ``tmp_path`` as the
suite's other cases do (the template's sources, the kernel, the tool registry,
the check's declaration), runs the real rulesync there (found as the suite
finds it: ``support.RULESYNC_BIN``, skipped when it is not installed) and,
where the case needs the "generated, then the step" state, runs the real
generator for that stand-in project. The held-out file is a stand-in written
by the case; the paths it names are invented under the case's temporary
folder. The two locations and the key are read from the generator's own
constants, never retyped here.

Behaviour is asserted through the declared command's exit code and what it
prints, and through ``gov check --json``. No function name or module layout is
asserted. One finding code is: the held-out step's own, for a broken held-out
file, because a check that could not compare at all (a rulesync call that gave
no answer in time) is also not green with a finding (DEC-892 item 2).
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

GENERATOR = ("python3", "-m", "gov.guard.heldout")   # the owner's apply procedure, second step
SRC = support.REPO_ROOT / "src"
HELD_OUT_STEP_FAILED = "HELD_OUT_STEP_FAILED"   # the check's finding: the held-out step could not be applied


# ---------------------------------------------------------------------------
# The stand-in project's held-out file and the generator's step
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def _names() -> dict:
    """The generator's own constants: where a project holds its held-out file,
    the key in it, and the settings file it writes. Read in a fresh interpreter
    with this worktree's ``src`` first, so no other tree's code answers."""
    code = (
        "import json, gov, gov.guard.heldout as h\n"
        "print(json.dumps({'config': h.CONFIG_REL, 'key': h.CONFIG_KEY, "
        "'settings': h.SETTINGS_REL, 'code': gov.__file__}))"
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
    assert names["settings"] == support.SETTINGS_REL, (
        "the generator writes another settings file than the one the suite compares"
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
    works in; here the project is the stand-in, for the generator (which reads
    the variable) and for the check alike."""
    return {"CLAUDE_PROJECT_DIR": str(project)}


def _run_step(project: Path) -> subprocess.CompletedProcess:
    """``python3 -m gov.guard.heldout`` in the stand-in project, with this
    worktree's code: the second step of the owner's apply procedure."""
    _assert_stand_in(project)
    done = subprocess.run(
        list(GENERATOR), capture_output=True, text=True, timeout=60, cwd=str(project),
        env={**os.environ, "PYTHONPATH": str(SRC), **_environment(project)},
        stdin=subprocess.DEVNULL,
    )
    assert done.returncode == 0, (
        f"the generator failed in the stand-in project (exit {done.returncode}): {done.stderr[-500:]}"
    )
    return done


def _settings_bytes(project: Path) -> bytes:
    _assert_stand_in(project)
    return (project / support.SETTINGS_REL).read_bytes()


def _deny_rules(project: Path) -> list[str]:
    return list(support.load_settings(project).get("permissions", {}).get("deny", []))


def _apply_step(project: Path, paths: list[str]) -> list[str]:
    """Write the stand-in held-out file, run the generator, and return the
    deny rules the step added (one for each stand-in path, asserted)."""
    before = _deny_rules(project)
    _write_held_out_file(project, paths)
    _run_step(project)
    added = [rule for rule in _deny_rules(project) if rule not in before]
    assert len(added) == len(paths) and all(
        sum(path in rule for rule in added) == 1 for path in paths
    ), (
        f"the generator added {len(added)} deny rule(s) for {len(paths)} stand-in path(s); "
        "one rule for each path is expected"
    )
    assert all(rule.startswith("Read(") for rule in added), "the generator's rules are not Read rules"
    return added


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
        f"\"rulesync generate, then the held-out step\" gives; they name {sorted(named)}"
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
# A project with a held-out file: its settings are "generated, then the step"
# ===================================================================

class TestSettingsAfterTheHeldOutStep:
    """DEC-635, DEC-641: the check holds the project's settings to exactly
    what rulesync generates followed by the generator's step."""

    @needs_rulesync
    def test_generated_then_the_step_is_green(self, generated_project, stand_in_paths):
        _apply_step(generated_project, stand_in_paths)
        _assert_green(generated_project, stand_in_paths,
                      "the project's settings are generated, then the held-out step")

    @needs_rulesync
    def test_step_never_run_is_red_on_the_settings(self, generated_project, stand_in_paths):
        """The project has a held-out file and its settings are what rulesync
        alone generates: every Read deny rule of the step is missing."""
        _write_held_out_file(generated_project, stand_in_paths)
        _assert_red_on_the_settings(
            generated_project, stand_in_paths,
            "the project has a held-out file and its settings hold none of its Read deny rules",
        )

    @needs_rulesync
    def test_one_rule_lost_is_red_on_the_settings(self, generated_project, stand_in_paths):
        """One of the two rules the step wrote is taken out again by hand."""
        added = _apply_step(generated_project, stand_in_paths)

        def lose_one(settings):
            settings["permissions"]["deny"].remove(added[-1])

        support.edit_settings(generated_project, lose_one)
        _assert_red_on_the_settings(
            generated_project, stand_in_paths,
            "one Read deny rule of the held-out file was removed from the project's settings",
        )

    @needs_rulesync
    def test_rule_the_held_out_file_does_not_give_is_red_on_the_settings(
        self, generated_project, stand_in_paths, tmp_path,
    ):
        """A Read deny rule in the generator's own form, for a path the
        held-out file does not name, beside the two it does name."""
        added = _apply_step(generated_project, stand_in_paths)
        other = str(tmp_path / "stand-in-held-out" / "not-in-the-file")
        stray = added[0].replace(stand_in_paths[0], other)
        assert stray != added[0] and stray not in _deny_rules(generated_project)

        def add_stray(settings):
            settings["permissions"]["deny"].append(stray)

        support.edit_settings(generated_project, add_stray)
        _assert_red_on_the_settings(
            generated_project, stand_in_paths,
            "the project's settings hold a Read deny rule the held-out file does not give",
        )


# ===================================================================
# A project without a held-out file is compared as before
# ===================================================================

class TestProjectWithoutAHeldOutFile:
    """DEC-641: the step is applied when and only when the project has a
    held-out file. Without one the settings are what rulesync generates."""

    @needs_rulesync
    def test_generated_settings_are_green(self, generated_project):
        assert not os.path.lexists(_held_out_file(generated_project)), (
            "the stand-in project as built holds a held-out file; the case needs one without"
        )
        result = _check(generated_project)
        assert result.returncode == 0 and not _findings(result), (
            f"a project without a held-out file, as rulesync generates it, is not green: "
            f"{support.output_of(result)}"
        )

    @needs_rulesync
    def test_stray_read_deny_rule_is_red_on_the_settings(self, generated_project, stand_in_paths):
        """The settings carry the step's rules and the project has no held-out
        file (the file was taken away after the step): the rules have no source."""
        _apply_step(generated_project, stand_in_paths)
        _held_out_file(generated_project).unlink()
        _assert_red_on_the_settings(
            generated_project, stand_in_paths,
            "the project has no held-out file and its settings carry Read deny rules of one",
        )


# ===================================================================
# A broken held-out file is not green, and prints no path
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
    """DEC-218, DEC-641: a held-out file that cannot be read, or is not of its
    stated shape, makes the check not green. The project's settings are what
    rulesync alone generates, so a check that fell back to the comparison
    without the step would be green here."""

    @needs_rulesync
    @pytest.mark.parametrize("form", sorted(BROKEN))
    def test_broken_file_is_not_green_and_no_path_is_printed(
        self, generated_project, stand_in_paths, form,
    ):
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
        assert result.returncode != 0, (
            f"the held-out file is broken ({form}) and the check is green: it compared without the step"
        )
        assert _findings(result), (
            f"the held-out file is broken ({form}): the check is not green but reports no finding"
        )
        # Rewrite-Reason (DEC-892 item 2): a check whose rulesync call gave no answer in time is not green with
        # a finding too, without comparing; the red is held to its reason, the held-out step's own finding.
        codes = [finding.get("code") for finding in _findings(result) if isinstance(finding, dict)]
        assert HELD_OUT_STEP_FAILED in codes, (
            f"the held-out file is broken ({form}), but no finding says the held-out step could not be applied; "
            f"the findings are {codes}"
        )


# ===================================================================
# The apply procedure may be repeated
# ===================================================================

class TestStepRepeated:

    @needs_rulesync
    def test_second_run_of_the_step_leaves_the_settings_as_they_are(
        self, generated_project, stand_in_paths,
    ):
        _apply_step(generated_project, stand_in_paths)
        once = _settings_bytes(generated_project)
        _run_step(generated_project)
        assert _settings_bytes(generated_project) == once, (
            "a second run of the generator changed the project's settings"
        )

    @needs_rulesync
    def test_project_is_still_green_after_the_second_run(self, generated_project, stand_in_paths):
        _apply_step(generated_project, stand_in_paths)
        _run_step(generated_project)
        _assert_green(generated_project, stand_in_paths,
                      "the held-out step was run twice on the generated settings")

    @needs_rulesync
    def test_whole_procedure_repeated_is_still_green(self, generated_project, stand_in_paths):
        """rulesync generate, the step, and both once more, as an owner who
        applies the adapters again does it."""
        _apply_step(generated_project, stand_in_paths)
        once = _settings_bytes(generated_project)
        again = support.run_rulesync_generate(generated_project)
        assert again.returncode == 0, f"rulesync generate failed: {again.stderr}"
        _run_step(generated_project)
        assert _settings_bytes(generated_project) == once, (
            "the apply procedure run a second time gave other settings than the first time"
        )
        _assert_green(generated_project, stand_in_paths, "the apply procedure was run twice")


# ===================================================================
# The same through gov check
# ===================================================================

class TestHeldOutStepThroughGovCheck:
    """``gov check --json`` shows what the declared command gave."""

    @needs_rulesync
    def test_gov_check_is_green_after_the_apply_procedure(
        self, generated_project, sandbox, stand_in_paths,
    ):
        _apply_step(generated_project, stand_in_paths)
        entry, family, run = _gov_check(generated_project, sandbox)
        _assert_no_stand_in_path(run.describe(), stand_in_paths, "gov check's output")
        assert (entry.get("status"), family.get("status")) == (support.GREEN, support.GREEN), (
            f"the settings are generated, then the held-out step, but gov check shows the check as "
            f"{entry.get('status')!r} and the family as {family.get('status')!r}\n{run.describe()}"
        )

    @needs_rulesync
    def test_gov_check_is_red_when_a_rule_is_lost(self, generated_project, sandbox, stand_in_paths):
        added = _apply_step(generated_project, stand_in_paths)

        def lose_one(settings):
            settings["permissions"]["deny"].remove(added[0])

        support.edit_settings(generated_project, lose_one)
        entry, family, run = _gov_check(generated_project, sandbox)
        _assert_no_stand_in_path(run.describe(), stand_in_paths, "gov check's output")
        assert (entry.get("status"), family.get("status")) == (support.RED, support.RED), (
            f"a Read deny rule of the held-out file is missing from the settings, but gov check shows "
            f"the check as {entry.get('status')!r} and the family as {family.get('status')!r}\n"
            f"{run.describe()}"
        )
        named = support.named_files(generated_project, json.dumps(entry.get("findings")))
        assert named == {support.SETTINGS_REL}, (
            f"the findings must name the project's settings file and no other file; "
            f"they name {sorted(named)}\n{run.describe()}"
        )

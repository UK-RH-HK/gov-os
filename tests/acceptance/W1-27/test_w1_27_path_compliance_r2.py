"""Follow-up, KPI success 3: the move table and the old cli tree are
historical; an old path inside its new path is no stale reference (DEC-456).

DEC-456 (owner, 2026-10-07) amends DEC-448's set of historical records:

  1. ``docs/SOURCES.md`` is a historical table of moves and must keep the old
     paths: it is left out of doctor's stale-path check.

  2. The old ``cli/`` tree is legacy code (the live CLI is ``src/gov/cli/``):
     it is treated as historical and left out of the check.

  3. An occurrence of an old path that is only a part of its own new path,
     in the file that names the new path, is not a stale reference.  A file
     that names the old path on its own (not as the tail of the new path)
     is still reported, also when the same file names the new path elsewhere.

``historical_excluded`` counts the number of files left out of the stale-path
check as historical records (round 5 README, DEC-448).  On this repository
after the one rebuild, doctor reported ``historical_excluded: 0`` although the
register is full of old paths.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w1_27_support as support


# =========================================================================== #
# Point 1: docs/SOURCES.md is historical (DEC-456)
# =========================================================================== #

def test_stale_path_in_sources_md_is_not_reported(gov, project, interface):
    """A reference to a moved path in docs/SOURCES.md is not reported.

    DEC-456: docs/SOURCES.md is a historical table of moves and must keep
    the old paths; it is left out of doctor's stale-path check.
    """
    support.write_path_map(project, support.minimal_valid_path_map())

    old = project / "src" / "gov" / "doctor" / "old_sources_mod.py"
    old.parent.mkdir(parents=True, exist_ok=True)
    old.write_text("# old module\n", encoding="utf-8")
    support.commit_all(project, "add old_sources_mod")

    new = project / "src" / "gov" / "doctor" / "new_sources_mod.py"
    old.rename(new)
    support.commit_all(project, "move old_sources_mod to new_sources_mod")

    sources = project / "docs" / "SOURCES.md"
    sources.parent.mkdir(parents=True, exist_ok=True)
    sources.write_text(
        "| src/gov/doctor/old_sources_mod.py | src/gov/doctor/new_sources_mod.py | moved |\n",
        encoding="utf-8",
    )
    support.commit_all(project, "add SOURCES.md with old path")

    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())

    assert "old_sources_mod" not in text, (
        "doctor reports a reference to a moved path inside docs/SOURCES.md "
        "— DEC-456 says the move table is historical and left out of the "
        f"stale-path check\n{run.describe()}"
    )


def test_stale_path_in_live_document_not_sources_is_reported(gov, project, interface):
    """The same old path in a live document IS reported.

    Counter-case for point 1: the exclusion of docs/SOURCES.md does not
    suppress stale-path reports in other documents.
    """
    support.write_path_map(project, support.minimal_valid_path_map())

    old = project / "src" / "gov" / "doctor" / "old_live_src_mod.py"
    old.parent.mkdir(parents=True, exist_ok=True)
    old.write_text("# old module\n", encoding="utf-8")
    support.commit_all(project, "add old_live_src_mod")

    new = project / "src" / "gov" / "doctor" / "new_live_src_mod.py"
    old.rename(new)
    support.commit_all(project, "move old_live_src_mod to new_live_src_mod")

    live = project / "docs" / "live-note.md"
    live.parent.mkdir(parents=True, exist_ok=True)
    live.write_text(
        "See src/gov/doctor/old_live_src_mod.py for the implementation.\n",
        encoding="utf-8",
    )
    support.commit_all(project, "add live reference")

    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())

    assert "old_live_src_mod" in text or "moved" in text.lower() or "stale" in text.lower(), (
        "doctor does not report a reference to a moved path in a live "
        f"document — the stale-path check should report it\n{run.describe()}"
    )


# =========================================================================== #
# Point 2: the old cli/ tree is historical (DEC-456)
# =========================================================================== #

def test_stale_path_in_old_cli_tree_is_not_reported(gov, project, interface):
    """A reference to a moved path in a file under cli/ is not reported.

    DEC-456: the old cli/ tree is legacy code (the live CLI is
    src/gov/cli/); it is treated as historical and left out of the
    stale-path check.
    """
    support.write_path_map(project, support.minimal_valid_path_map())

    old = project / "src" / "gov" / "doctor" / "old_cli_mod.py"
    old.parent.mkdir(parents=True, exist_ok=True)
    old.write_text("# old module\n", encoding="utf-8")
    support.commit_all(project, "add old_cli_mod")

    new = project / "src" / "gov" / "doctor" / "new_cli_mod.py"
    old.rename(new)
    support.commit_all(project, "move old_cli_mod to new_cli_mod")

    cli_ref = project / "cli" / "legacy_commands.py"
    cli_ref.parent.mkdir(parents=True, exist_ok=True)
    cli_ref.write_text(
        "# old reference: src/gov/doctor/old_cli_mod.py\n",
        encoding="utf-8",
    )
    support.commit_all(project, "add cli reference")

    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())

    assert "old_cli_mod" not in text, (
        "doctor reports a reference to a moved path inside the old cli/ "
        "tree — DEC-456 says the old CLI tree is historical and left out "
        f"of the stale-path check\n{run.describe()}"
    )


def test_stale_path_in_src_gov_cli_is_reported(gov, project, interface):
    """A reference to the same moved path in src/gov/cli/ IS reported.

    Counter-case for point 2: src/gov/cli/ is the live CLI and is NOT
    excluded.  DEC-456 excludes only the old cli/ tree at the repository
    root.
    """
    support.write_path_map(project, support.minimal_valid_path_map())

    old = project / "src" / "gov" / "doctor" / "old_src_cli_mod.py"
    old.parent.mkdir(parents=True, exist_ok=True)
    old.write_text("# old module\n", encoding="utf-8")
    support.commit_all(project, "add old_src_cli_mod")

    new = project / "src" / "gov" / "doctor" / "new_src_cli_mod.py"
    old.rename(new)
    support.commit_all(project, "move old_src_cli_mod to new_src_cli_mod")

    cli_live = project / "src" / "gov" / "cli" / "commands_ref.py"
    cli_live.parent.mkdir(parents=True, exist_ok=True)
    cli_live.write_text(
        "# reference: src/gov/doctor/old_src_cli_mod.py\n",
        encoding="utf-8",
    )
    support.commit_all(project, "add src/gov/cli reference")

    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())

    assert "old_src_cli_mod" in text or "moved" in text.lower() or "stale" in text.lower(), (
        "doctor does not report a reference to a moved path in "
        "src/gov/cli/ — the live CLI is not excluded from the stale-path "
        f"check (DEC-456)\n{run.describe()}"
    )


# =========================================================================== #
# Point 3: an old path inside its new path is not a stale reference (DEC-456)
# =========================================================================== #

def test_old_path_inside_its_new_path_is_not_stale(gov, project, interface):
    """An occurrence of an old path that is only a part of its own new path,
    in the file that names the new path, is not a stale reference.

    DEC-456: the validator script names the new path
    docs/source/originals/<file>, which contains the old path (the bare
    file name) as a suffix.  Doctor reports it because the old path is
    contained in the new one.  This is not a stale reference.
    """
    support.write_path_map(project, support.minimal_valid_path_map())

    old_name = "subpath_target.py"
    new_rel = f"docs/source/originals/{old_name}"

    old = project / old_name
    old.write_text("# content\n", encoding="utf-8")
    support.commit_all(project, f"add {old_name}")

    new = project / new_rel
    new.parent.mkdir(parents=True, exist_ok=True)
    old.rename(new)
    support.commit_all(project, f"move {old_name} to {new_rel}")

    validator = project / "docs" / "plan" / "tools" / "validate_paths.py"
    validator.parent.mkdir(parents=True, exist_ok=True)
    validator.write_text(
        f'FRAMEWORK_PATH = "{new_rel}"\n',
        encoding="utf-8",
    )
    support.commit_all(project, "add validator referencing new path")

    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())

    assert "subpath_target" not in text, (
        "doctor reports the old path as stale even though it appears only "
        f"as part of its own new path ({new_rel}) in the file that names "
        f"the new path — DEC-456 says this is not a stale reference\n"
        f"{run.describe()}"
    )


def test_old_path_standalone_is_stale_when_new_path_elsewhere(gov, project, interface):
    """A file that names the old path on its own is reported as stale, also
    when the same file names the new path elsewhere.

    Counter-case for point 3: the exception is narrow — only an occurrence
    of the old path that is a part of the new path is suppressed.  A
    standalone old path in the same file is still reported.
    """
    support.write_path_map(project, support.minimal_valid_path_map())

    old_name = "standalone_target.py"
    new_rel = f"docs/source/originals/{old_name}"

    old = project / old_name
    old.write_text("# content\n", encoding="utf-8")
    support.commit_all(project, f"add {old_name}")

    new = project / new_rel
    new.parent.mkdir(parents=True, exist_ok=True)
    old.rename(new)
    support.commit_all(project, f"move {old_name} to {new_rel}")

    refs = project / "docs" / "plan" / "tools" / "validate_refs.py"
    refs.parent.mkdir(parents=True, exist_ok=True)
    refs.write_text(
        f'NEW_PATH = "{new_rel}"\n'
        f'OLD_PATH = "{old_name}"\n',
        encoding="utf-8",
    )
    support.commit_all(project, "add file with both old and new path")

    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())

    assert "standalone_target" in text or "moved" in text.lower() or "stale" in text.lower(), (
        "doctor does not report the standalone old path as stale even "
        "though it appears on its own (not as part of the new path) — "
        f"DEC-456 says a standalone old path is still reported\n"
        f"{run.describe()}"
    )


# =========================================================================== #
# historical_excluded count (DEC-456, DEC-448)
# =========================================================================== #

def test_historical_excluded_nonzero_when_historical_holds_old_path(gov, project, interface):
    """historical_excluded counts the files left out of the stale-path
    check as historical records, including the two new places from DEC-456.

    historical_excluded counts the number of files left out of the
    stale-path check as historical records (round 5 README, DEC-448).
    DEC-456 adds ``docs/SOURCES.md`` and the old ``cli/`` tree.  When
    all three kinds (the register from DEC-448, SOURCES.md and a file
    under cli/ from DEC-456) hold a reference to an old path, the count
    must include all three.
    """
    support.write_path_map(project, support.minimal_valid_path_map())

    old = project / "src" / "gov" / "doctor" / "old_hist_count_mod.py"
    old.parent.mkdir(parents=True, exist_ok=True)
    old.write_text("# old module\n", encoding="utf-8")
    support.commit_all(project, "add old_hist_count_mod")

    new = project / "src" / "gov" / "doctor" / "new_hist_count_mod.py"
    old.rename(new)
    support.commit_all(project, "move old_hist_count_mod")

    register = project / "docs" / "DECISION_REGISTER.md"
    register.parent.mkdir(parents=True, exist_ok=True)
    register.write_text(
        "### DEC-999\nReferences src/gov/doctor/old_hist_count_mod.py\n",
        encoding="utf-8",
    )
    sources = project / "docs" / "SOURCES.md"
    sources.parent.mkdir(parents=True, exist_ok=True)
    sources.write_text(
        "| src/gov/doctor/old_hist_count_mod.py | src/gov/doctor/new_hist_count_mod.py |\n",
        encoding="utf-8",
    )
    cli_ref = project / "cli" / "old_ref.py"
    cli_ref.parent.mkdir(parents=True, exist_ok=True)
    cli_ref.write_text(
        "# old: src/gov/doctor/old_hist_count_mod.py\n",
        encoding="utf-8",
    )
    support.commit_all(project, "add historical files with old paths")

    run = gov("doctor", "--json")
    envelope = run.envelope()

    result = envelope.get("result", {})
    if not result:
        result = envelope.get("error", {}).get("details", {})

    pc = result.get("path_compliance", {})
    excluded = pc.get("historical_excluded", 0)

    assert isinstance(excluded, int) and excluded >= 3, (
        f"historical_excluded should be >= 3 (register + SOURCES.md + "
        f"cli/old_ref.py) when all three hold references to old paths, "
        f"but got historical_excluded={excluded!r} — DEC-456 adds "
        f"docs/SOURCES.md and cli/ to the historical set, and the count "
        f"must include them\n"
        f"path_compliance section: {json.dumps(pc) if pc else pc}\n"
        f"{run.describe()}"
    )

"""Fix F6 (G3 run of 2026-11-22): `gov update` leaves `gov doctor` green where it was (DAEO-sdhj).

`gov update` writes `governance/updates/<version>.json` (and `governance/updates/<version>/release/...`). The path map
of an adopted repository (`governance/project/path-map.yaml`) did not classify them, so `gov doctor`'s `path_map` part
failed (`unclassified: ["governance/updates/0.9.1.json"]`) and doctor's exit went from 0 to 3. Required: the kit's
path map classifies `governance/updates/**`, and `gov update` adds that line to an adopted repository's path map when
it lacks it, as a merge (the project's other lines and edits stay; never a conflict or a refusal), once.

The project here is adopted at A without local changes (its framework lock matches), then made what an earlier kit
adopted: its path map has no `governance/updates` line, and everything else it tracks is classified (a namespace
`fixture-rest` of directory patterns, which the project owns), so that doctor's `path_map` part passes before the
update and only the update's own files can fail it afterwards. Public interface only: `gov update B --json`,
`gov doctor --json`, and the files `governance/project/path-map.yaml` and `template/governance/project/path-map.yaml`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

import w2_17_support as support

PATTERN = "governance/updates/**"
MAP_REL = "governance/project/path-map.yaml"
UPDATES = "governance/updates/"
OWN_COMMENT = "# W2-17 F6: the project's own comment, which a merge keeps."


def _patterns(text):
    """Every path pattern of every namespace of a path map's text."""
    data = yaml.safe_load(text)
    found = []
    for namespace in (data.get("namespaces") or {}).values():
        found.extend(p for p in (namespace or {}).get("paths", []) if isinstance(p, str))
    return found


def _map(project):
    return (Path(project) / MAP_REL).read_text(encoding="utf-8")


def _subsequence(lines, text):
    """The lines of ``lines`` (non-blank), all present in ``text`` in the same order."""
    remaining = iter(text.splitlines())
    return [line for line in lines if line.strip() and line not in remaining]


def _doctor(project, sandbox):
    run = support.gov(project, sandbox, "doctor", "--json")
    return run, support.doctor_report(run).get("path_map") or {}


def _classify_the_rest(project):
    """Append to the project's own path map a namespace classifying every tracked path but governance/updates."""
    paths = [p for p in support.git(project, "ls-files").splitlines() if p and not p.startswith(UPDATES)]
    patterns = set()
    for path in paths:
        parts = path.split("/")
        if len(parts) == 1:
            patterns.add(path)
        elif parts[0] == "governance":
            patterns.add(path if len(parts) == 2 else f"governance/{parts[1]}/**")
        else:
            patterns.add(f"{parts[0]}/**")
    text = _map(project).rstrip("\n") + "\n  fixture-rest:\n    paths:\n" + "".join(
        f'      - "{p}"\n' for p in sorted(patterns))
    (project / MAP_REL).write_text(text, encoding="utf-8")


def _strip_updates_line(project):
    """What a kit before this fix adopted: no line of the path map names governance/updates."""
    lines = [line for line in _map(project).splitlines(keepends=True) if "governance/updates" not in line]
    (project / MAP_REL).write_text("".join(lines), encoding="utf-8")


@dataclass(frozen=True)
class Previous:
    project: Path
    fresh_patterns: list        # the path map's patterns as the kit's template installed them at A


@pytest.fixture(scope="module")
def previous(copier_bin, source, tmp_path_factory):
    """A project adopted at A (no local changes), then as an earlier kit's: no governance/updates line, the rest
    classified, committed. Never changed."""
    base = tmp_path_factory.mktemp("w2-17-f6")
    sandbox = support.make_sandbox(base / "sandbox")
    try:
        project = support.adopt(copier_bin, source.repo, base / "product", sandbox, local_changes=False)
        fresh = _patterns(_map(project))
        _strip_updates_line(project)
        _classify_the_rest(project)
        support.commit_all(project, "W2-17 F6: a path map as an earlier kit adopted it")
        run, part = _doctor(project, sandbox)
        assert part.get("status") == "pass", f"doctor's path_map part is not green before the update: {part}"
    except AssertionError as exc:
        pytest.fail(f"W2-17 F6 fixture could not be built (not the feature under test): {exc}", pytrace=False)
    return Previous(project, fresh)


@dataclass(frozen=True)
class Updated:
    project: Path
    before_run: object
    after_run: object
    before_part: dict
    after_part: dict
    run: object


def _updated(project_copy, sandbox):
    before_run, before_part = _doctor(project_copy, sandbox)
    run = support.update(project_copy, sandbox)
    after_run, after_part = _doctor(project_copy, sandbox)
    return Updated(project_copy, before_run, after_run, before_part, after_part, run)


@pytest.fixture(scope="module")
def updated(previous, tmp_path_factory):
    """Doctor, `gov update B`, doctor again, in a copy of the previous project."""
    base = tmp_path_factory.mktemp("w2-17-f6-updated")
    return _updated(support.copy_project(previous.project, base / "product"), support.make_sandbox(base / "sandbox"))


def _updated_with(previous, base, edit):
    project = support.copy_project(previous.project, base / "product")
    sandbox = support.make_sandbox(base / "sandbox")
    before = _map(project)
    edit(project)
    support.commit_all(project, "W2-17 F6: the project's own path map edit")
    changed = _map(project)
    run = support.update(project, sandbox)
    return project, before, changed, run


def _succeeded(run):
    assert run.returncode == 0, f"`gov update --json` did not exit 0\n{run.describe()}"
    return run.result()


# ---- the kit's own path map ------------------------------------------------------------------------------

def test_the_kits_path_map_template_classifies_governance_updates():
    """The path map the kit installs on adoption (the template) classifies governance/updates/** once."""
    template = support.REPO_ROOT / "template" / MAP_REL
    patterns = _patterns(template.read_text(encoding="utf-8"))
    assert patterns.count(PATTERN) == 1, (
        f"template/{MAP_REL} holds {patterns.count(PATTERN)} line(s) `{PATTERN}`, not one")


def test_a_freshly_adopted_repository_already_classifies_governance_updates(previous):
    """A repository adopted from the kit holds the line in its path map at once (before any update)."""
    assert previous.fresh_patterns.count(PATTERN) == 1, (
        f"the path map `gov install`/copier wrote at A holds {previous.fresh_patterns.count(PATTERN)} line(s) "
        f"`{PATTERN}`, not one")


# ---- the update adds the line, once -----------------------------------------------------------------------

def test_the_update_adds_the_line_to_a_path_map_without_it_once(updated):
    """A path map without the line has it exactly once after `gov update` (which succeeded)."""
    _succeeded(updated.run)
    patterns = _patterns(_map(updated.project))
    assert patterns.count(PATTERN) == 1, f"the path map holds {patterns.count(PATTERN)} line(s) `{PATTERN}` after the update"


# ---- doctor, before and after ----------------------------------------------------------------------------

def test_doctors_path_map_part_has_no_unclassified_update_record_after_the_update(updated):
    """doctor's path_map part passes after the update: nothing unclassified, no governance/updates/ path."""
    _succeeded(updated.run)
    assert updated.before_part.get("status") == "pass", "fixture: the part is not green before the update"
    part = updated.after_part
    leftovers = [p for p in part.get("unclassified", []) if p.startswith(UPDATES)]
    assert not leftovers and part.get("status") == "pass" and part.get("unclassified_count") == 0, (
        f"doctor's path_map part after the update: {part}")


def test_doctors_exit_code_is_the_same_before_and_after_the_update(updated):
    """The G3 line: `gov doctor --json` exits as it did before the update (the whole report; the project's other
    parts are the same before and after: the update changed only the path_map part's outcome)."""
    _succeeded(updated.run)
    before, after = updated.before_run.returncode, updated.after_run.returncode
    assert before == after, (
        f"doctor's exit code was {before} before `gov update` and {after} after\n{updated.after_run.describe()}")


# ---- a merge: the project's own lines stay ---------------------------------------------------------------

def test_the_update_merges_the_line_and_keeps_the_projects_own_lines(previous, tmp_path):
    """A path map with the project's own namespace, an extra line in a kit namespace and its own comment: after the
    update every one of its lines is there in its order, the line is there once, no conflict, no refusal."""
    def own_edits(project):
        text = _map(project).replace("      - openspec/**\n", "      - openspec/**\n      - docs/**\n", 1)
        assert "docs/**" in text, "fixture: the kit's path map has no `openspec/**` line to extend"
        text = OWN_COMMENT + "\n" + text.rstrip("\n") + "\n  own-extra:\n    paths:\n      - tools/**\n      - scripts/**\n"
        (project / MAP_REL).write_text(text, encoding="utf-8")

    project, before, changed, run = _updated_with(previous, tmp_path, own_edits)
    result = _succeeded(run)
    after = _map(project)
    assert not any(MAP_REL in item for item in (result.get("files") or {}).get("conflicts", [])), (
        f"the path map is reported as a conflict: {result.get('files')}")
    assert not _subsequence(changed.splitlines(), after), (
        f"lines of the project's path map are gone or out of order after the update: "
        f"{_subsequence(changed.splitlines(), after)}")
    patterns = _patterns(after)
    assert patterns.count(PATTERN) == 1, f"the path map holds {patterns.count(PATTERN)} line(s) `{PATTERN}`"
    for own in ("docs/**", "tools/**", "scripts/**"):
        assert patterns.count(own) == 1, f"the project's own `{own}` is not kept once: {patterns.count(own)}"
    assert OWN_COMMENT in after.splitlines(), "the project's own comment is gone"
    assert not any(marker in after for marker in ("<<<<<<<", ">>>>>>>")), "the path map holds a conflict marker"
    assert not (project / (MAP_REL + ".rej")).exists()


def test_the_update_of_a_path_map_that_has_the_line_leaves_it_once(previous, tmp_path):
    """A project that already classifies governance/updates/** (in its own namespace): once after the update."""
    def with_line(project):
        text = _map(project).rstrip("\n") + f"\n  own-records:\n    paths:\n      - {PATTERN}\n"
        (project / MAP_REL).write_text(text, encoding="utf-8")

    project, before, changed, run = _updated_with(previous, tmp_path, with_line)
    _succeeded(run)
    after = _map(project)
    assert _patterns(after).count(PATTERN) == 1, (
        f"the path map holds {_patterns(after).count(PATTERN)} line(s) `{PATTERN}` after the update")
    assert not _subsequence(changed.splitlines(), after), "lines of the project's path map are gone or out of order"

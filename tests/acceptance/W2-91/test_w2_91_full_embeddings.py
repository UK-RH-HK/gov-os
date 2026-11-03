"""W2-91 (DAEO-a3u2): full embeddings of the root files, the governance overlay and schemas/ (DEC-957, DEC-954 Q9c,
DEC-388, DEC-694, DEC-381, DEC-856, DEC-887, DEC-820 (d)).

This repository's path map and tracked files are read, nothing in it is written. Two planted repositories are rebuilt
with ``gov rebuild`` and a stand-in embedder on the loopback interface; their stores show which files got vectors.
README.md maps each KPI line to its cases.
"""

from __future__ import annotations

import copy
import json

import pytest
import yaml

from gov.check import pathmap

import w2_91_support as s

PROBES = ("cli/carried.py", "cli/package/module.py",  # cli/** has no tracked file today: its verdict is probed
          "fixtures/evaluation/memory-retrieval/hidden/q01.md")
NOT_EMBEDDED_AREAS = s.HIDDEN + s.GENERATED + s.VENDORED + s.CARRIED


@pytest.fixture(autouse=True)
def _code_under_test():
    s.assert_code_under_test()


# --------------------------------------------------------------------------
# The checks, each returning its faults (none: the line holds); each failure line is shown to refuse below
# --------------------------------------------------------------------------

def not_yet_embedded(namespaces, paths):
    """Success 1: the root files, governance/** and schemas/** files the path map does not embed."""
    return sorted(rel for rel in paths if s.newly_embedded_area(rel) and not s.embedded(namespaces, rel))


def embedded_that_stays_out(namespaces, paths):
    """Success 2, failure 1: files of the hidden half, the generated copies, the vendored code or cli/ embedded."""
    return sorted(rel for rel in paths if s.matches_any(rel, NOT_EMBEDDED_AREAS) and s.embedded(namespaces, rel))


def schemas_sharing_with_cli(namespaces, paths):
    """Success 2: a namespace that holds a schemas/ file and also holds cli/ paths."""
    cli = [rel for rel in paths if rel.startswith("cli/")]
    shared = set()
    for rel in paths:
        if rel.startswith("schemas/"):
            for name in s.homes(namespaces, rel):
                if any(name in s.homes(namespaces, other) for other in cli):
                    shared.add(name)
    return sorted(shared)


def overlay_not_restricted(namespaces, paths):
    """Success 3, failure 2: a namespace holding a governance/ file whose sensitivity or export policy moved."""
    faults = {}
    for rel in paths:
        if rel.startswith("governance/"):
            for name in s.homes(namespaces, rel):
                entry = namespaces[name]
                if (entry.get("sensitivity"), entry.get("export_policy")) != ("restricted", "denied"):
                    faults[name] = (entry.get("sensitivity"), entry.get("export_policy"))
    return faults


def values_outside_the_two(namespaces):
    """Success 4, failure 3: a namespace whose embedding_policy is not one of the two values."""
    return {name: entry.get("embedding_policy") for name, entry in namespaces.items()
            if entry.get("embedding_policy") not in s.VALUES}


def moved(before, after, paths):
    """Success 5: a verdict that changed, other than a root, governance/ or schemas/ file becoming embedded."""
    faults = []
    for rel in paths:
        was, now = s.embedded(before, rel), s.embedded(after, rel)
        if was != now and not (s.newly_embedded_area(rel) and now and not was):
            faults.append((rel, s.EMBEDDED if was else s.NOT_EMBEDDED, s.EMBEDDED if now else s.NOT_EMBEDDED))
    return sorted(faults)


# --------------------------------------------------------------------------
# This repository's path map and tracked files
# --------------------------------------------------------------------------

def test_root_files_governance_and_schemas_are_embedded():
    """Success 1 (the path map's verdict for this repository's tracked files)."""
    paths, namespaces = s.tracked(), s.namespaces_at(None)
    root = [rel for rel in paths if "/" not in rel]
    sets = {"root files": root, "governance/": [rel for rel in paths if rel.startswith("governance/")],
            "schemas/": [rel for rel in paths if rel.startswith("schemas/")]}
    assert [name for name, found in sets.items() if not found] == [], "an empty set: the case would pass vacuously"
    assert {"CLAUDE.md", "README.md", "AGENTS.md"} <= set(root)
    missing = not_yet_embedded(namespaces, paths)
    counts = {name: sum(1 for rel in found if rel in missing) for name, found in sets.items()}
    assert missing == [], f"{len(missing)} files not embedded ({counts}), e.g. {missing[:5]}"


def test_schemas_has_a_namespace_of_its_own_and_cli_stays_out():
    """Success 2: schemas/** in a namespace that holds no cli/ path; cli/** keeps not embedded."""
    namespaces = s.namespaces_at(None)
    paths = s.tracked() + list(PROBES)
    assert any(rel.startswith("schemas/") for rel in paths)
    assert schemas_sharing_with_cli(namespaces, paths) == [], "schemas/** shares its namespace with cli/**"
    assert [rel for rel in PROBES if rel.startswith("cli/") and s.embedded(namespaces, rel)] == []


def test_the_hidden_half_generated_copies_vendored_code_and_cli_are_not_embedded():
    """Success 2, failure 1 (the path map's verdict for this repository's tracked files and probed cli/ paths)."""
    namespaces = s.namespaces_at(None)
    paths = s.tracked()
    for patterns in (s.HIDDEN, (".claude/**",), (".rulesync/**",), ("template/.rulesync/**",), s.VENDORED):
        assert any(s.matches_any(rel, patterns) for rel in paths), f"no tracked file under {patterns}: vacuous"
    sets = yaml.safe_load(s.path_map_text_at(None)).get("evaluation_sets") or {}
    hidden = [pattern for entry in sets.values() for pattern in entry.get("hidden") or []]
    assert hidden, "the path map names no hidden half"
    probed = paths + list(PROBES)
    assert embedded_that_stays_out(namespaces, probed) == []
    assert [rel for rel in probed if s.matches_any(rel, hidden) and s.embedded(namespaces, rel)] == []


def test_the_overlay_stays_restricted_and_its_export_denied():
    """Success 3, failure 2 (the fields): every namespace holding a governance/ file keeps restricted and denied."""
    paths = [rel for rel in s.tracked() if rel.startswith("governance/")]
    assert paths
    assert overlay_not_restricted(s.namespaces_at(None), paths) == {}


def test_every_namespace_states_one_of_the_two_values():
    """Success 4, failure 3 (another value)."""
    assert values_outside_the_two(s.namespaces_at(None)) == {}


def test_every_tracked_path_is_in_exactly_one_namespace():
    """Success 4, failure 3 (a tracked path in no namespace or in two), by the pinned path-map check."""
    assert pathmap.check(s.ROOT) == []


def test_this_ticket_changes_no_code():
    """Success 4: the indexer's code is not changed: no commit of this ticket, and no uncommitted change, touches src/."""
    touching = s.ticket_commits("src")
    assert touching == [], f"commits of {s.TICKET} change src/: {[sha[:12] for sha in touching]}"
    unstaged = s.git("diff", "--name-only", "HEAD", "--", "src").stdout.split()
    assert unstaged == [], f"uncommitted changes under src/: {unstaged[:5]}"


def test_nothing_else_moves():
    """Success 5: across this ticket's own changes of the path map, judged over today's tracked paths, every verdict
    outside the root files, governance/** and schemas/** is unchanged, and none of theirs goes back to not embedded."""
    paths = s.tracked()
    faults = {}
    for before, after in s.ticket_steps(s.PATH_MAP_REL):
        found = moved(s.namespaces_at(before), s.namespaces_at(after), paths)
        if found:
            faults[f"{before} -> {after or 'working tree'}"] = found[:10]
    assert faults == {}, json.dumps(faults, indent=1)


# --------------------------------------------------------------------------
# Each failure line refuses: the same checks on this repository's path map with one fault planted
# --------------------------------------------------------------------------

def _with(namespaces, name, **fields):
    changed = copy.deepcopy(namespaces)
    changed[name] = {**changed[name], **fields}
    return changed


def _holding(namespaces, rel):
    names = s.homes(namespaces, rel)
    assert len(names) == 1, f"{rel} is in {names}"
    return names[0]


@pytest.mark.parametrize("rel", ["fixtures/planted/sample.md", ".claude/skills/planted/SKILL.md",
                                 ".rulesync/planted.md", "cli/carried.py"])
def test_failure_1_an_embedded_file_that_stays_out_is_refused(rel):
    namespaces = s.namespaces_at(None)
    planted = _with(namespaces, _holding(namespaces, rel), embedding_policy=s.EMBEDDED)
    assert rel in embedded_that_stays_out(planted, [rel])


@pytest.mark.parametrize("fields", [{"sensitivity": "internal"}, {"export_policy": "allowed"}])
def test_failure_2_the_overlay_unrestricted_is_refused(fields):
    namespaces, rel = s.namespaces_at(None), "governance/adoption/planted.md"
    planted = _with(namespaces, _holding(namespaces, rel), **fields)
    assert overlay_not_restricted(planted, [rel]) != {}


def test_failure_3_a_third_value_is_refused():
    namespaces = s.namespaces_at(None)
    name = _holding(namespaces, "schemas/planted.json")
    planted = _with(namespaces, name, embedding_policy="embedded, except vendored code")
    assert name in values_outside_the_two(planted)


def test_failure_3_a_path_in_no_namespace_or_in_two_is_refused(tmp_path):
    namespaces = {"top": s.namespace(["*"], s.NOT_EMBEDDED), "overlay": s.namespace(["governance/**"], s.NOT_EMBEDDED),
                  "twice": s.namespace(["notes/**", "governance/project/*"], s.EMBEDDED)}
    project = s.plant(tmp_path / "project", namespaces, {"notes/a.md": "a\n", "stray/b.md": "b\n"})
    codes = {(finding["code"], finding["path"]) for finding in pathmap.check(project)}
    assert ("PATH_NO_NAMESPACE", "stray/b.md") in codes
    assert ("PATH_MULTIPLE_NAMESPACES", s.PATH_MAP_REL) in codes


def test_success_5_a_verdict_moved_elsewhere_is_refused():
    namespaces = s.namespaces_at(None)
    rel = "docs/planted.md"
    planted = _with(namespaces, _holding(namespaces, rel), embedding_policy=s.NOT_EMBEDDED)
    assert moved(namespaces, planted, [rel, "README.md"]) == [(rel, s.EMBEDDED, s.NOT_EMBEDDED)]


# --------------------------------------------------------------------------
# Planted repositories, rebuilt with a stand-in embedder
# --------------------------------------------------------------------------

def _python(rel):
    return f'"""Planted module {rel}: it reads the harbour tide tables for the bakery."""\n\nTIDES = 2\n'


def _json(rel):
    return json.dumps({"title": f"planted schema {rel}", "description": "harbour tide tables for the bakery"},
                      indent=2) + "\n"


IN = ["CLAUDE.md", "README.md", "AGENTS.md", "copier.yml", "governance/adoption/planted.md",
      "governance/project/planted-notes.md", "governance/project/briefs/planted.md",
      "governance/project/prompts/planted.md", "governance/project/orchestration/packages/planted.md",
      "governance/project/orchestration/sessions/planted.md",
      "governance/project/orchestration/main/orchestrator/CHECKPOINT.md", "schemas/planted.schema.json"]
OUT = ["cli/carried.py", "fixtures/planted/sample.md", ".claude/skills/planted/SKILL.md", ".rulesync/planted.md",
       "template/.rulesync/planted.md", "template/governance/kernel/vendor/planted.py",
       "template/governance/kernel/bin/planted.md", "template/governance/kernel/skills/superpowers/planted/SKILL.md"]
CONTROLS = ["docs/planted.md", "src/planted.py", ".github/workflows/planted.md",
            "template/governance/kernel/roles/planted.md"]
# fixtures/** is product memory: the lexical index never reads it (DEC-820 (d)), so it has no chunk to embed either.
NEVER_INDEXED = {"fixtures/planted/sample.md"}


def _text(rel):
    if rel.endswith(".py"):
        return _python(rel)
    if rel.endswith(".json"):
        return _json(rel)
    if rel.endswith(".yml"):
        return f"description: planted settings {rel} for the harbour tide tables of the bakery\n"
    return s.planted_text(rel)


@pytest.fixture(scope="module")
def stand_in():
    reason = s.lacking()
    if reason:
        pytest.skip(reason)
    server = s.OllamaStandIn()
    yield server
    server.close()


def test_a_rebuild_gives_vectors_exactly_to_the_files_the_path_map_embeds(tmp_path, stand_in):
    """Success 1 and 2, failure 1, through the indexer: this repository's path map in a planted repository."""
    namespaces = s.namespaces_at(None)
    files = {rel: _text(rel) for rel in IN + OUT + CONTROLS}
    project = s.plant(tmp_path / "project", namespaces, files)
    assert pathmap.check(project) == [], "a planted file is in no namespace or in two"
    s.rebuild(project, stand_in.host)
    chunked, vectors = s.store_paths(project)
    lost = sorted(set(IN + OUT + CONTROLS) - chunked - NEVER_INDEXED)
    assert lost == [], f"planted files the lexical index holds no chunk of: {lost}"
    assert sorted(vectors & set(OUT)) == [], "a file that stays out has a vector"
    assert sorted(set(IN) - vectors) == [], "a root, governance/ or schemas/ file has no vector"
    assert vectors == {rel for rel in chunked if s.embedded(namespaces, rel)}, \
        "the vectors are not exactly the files the path map embeds"
    assert {"docs/planted.md", "src/planted.py", "template/governance/kernel/roles/planted.md"} <= vectors
    assert ".github/workflows/planted.md" not in vectors


def test_the_indexer_verdict_ignores_sensitivity_and_export_policy(tmp_path, stand_in):
    """Success 3: namespaces that differ only in sensitivity and export policy get the same embedding verdict."""
    namespaces = {
        "top": s.namespace(["*"], s.NOT_EMBEDDED),
        "project": s.namespace(["governance/**"], s.NOT_EMBEDDED),
        "open-in": s.namespace(["open/**"], s.EMBEDDED),
        "restricted-in": s.namespace(["restricted/**"], s.EMBEDDED, "restricted", "denied"),
        "open-out": s.namespace(["quiet/**"], s.NOT_EMBEDDED),
        "restricted-out": s.namespace(["sealed/**"], s.NOT_EMBEDDED, "restricted", "denied"),
    }
    files = {rel: s.planted_text(rel) for rel in ("open/a.md", "restricted/a.md", "quiet/a.md", "sealed/a.md")}
    project = s.plant(tmp_path / "project", namespaces, files)
    s.rebuild(project, stand_in.host)
    chunked, vectors = s.store_paths(project)
    assert set(files) <= chunked
    assert vectors & set(files) == {"open/a.md", "restricted/a.md"}

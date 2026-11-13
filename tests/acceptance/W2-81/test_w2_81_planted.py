"""The planted problems and the controls are what the manifest says, in the built repositories."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from pathlib import Path

import w2_81_build as build
import w2_81_git as gitlib
from w2_81_manifest import CONTROL_KINDS, KINDS, LEGACY_KINDS
from w2_81_words import CURRENT_WORDS, LEGACY_FOLDERS, OLD_WORDS


def _entries(ground, kind):
    return [(b, e) for b in ground.values() for e in b.manifest["planted"] if e["kind"] == kind]


def _number(line):
    return int(re.findall(r"\d+", line)[-1])


def _day(text):
    return date.fromisoformat(text)


def test_every_kind_is_planted_in_two_repositories_two_shapes_and_two_variants(ground):
    seen = defaultdict(lambda: {"repos": set(), "shapes": set(), "variants": set()})
    for built in ground.values():
        for entry in built.manifest["planted"]:
            seen[entry["kind"]]["repos"].add(built.name)
            seen[entry["kind"]]["shapes"].add(entry["shape"])
            seen[entry["kind"]]["variants"].add(entry["variant"])
    for kind in KINDS:
        assert len(seen[kind]["repos"]) >= 2, f"{kind}: in {sorted(seen[kind]['repos'])}"
        assert len(seen[kind]["shapes"]) >= 2, f"{kind}: in shapes {sorted(seen[kind]['shapes'])}"
        assert len(seen[kind]["variants"]) >= 2, f"{kind}: variants {sorted(seen[kind]['variants'])}"
    for kind in LEGACY_KINDS:
        assert seen[kind]["repos"] == {"legacy-docs"}, kind
    assert set(seen) == set(KINDS) | set(LEGACY_KINDS)


def test_the_clean_variant_has_controls_only(ground):
    clean = ground[build.CLEAN].manifest
    assert clean["clean"] is True and clean["planted"] == []
    assert sorted(c["kind"] for c in clean["controls"]) == sorted(CONTROL_KINDS)
    for name in build.SHAPES:
        assert ground[name].manifest["clean"] is False and ground[name].manifest["planted"], name


def test_every_repository_has_its_two_controls_and_each_says_what_flagging_it_looks_like(ground):
    for name, built in ground.items():
        controls = built.manifest["controls"]
        assert sorted(c["kind"] for c in controls) == sorted(CONTROL_KINDS), name
        for control in controls:
            assert control["why_control"] and control["flagging_looks_like"], control["id"]


def test_the_old_looking_spec_is_current(ground):
    for built in ground.values():
        for control in built.manifest["controls"]:
            if control["kind"] != "current-spec-looks-old":
                continue
            path, ev = control["paths"][0], control["evidence"]
            text = gitlib.blob(built.root, "HEAD", path)
            assert "draft" in Path(path).name, path
            dated = re.search(r"Dated: (\d{4}-\d{2}-\d{2})", text).group(1)
            first = gitlib.commit_day(built.root, built.manifest["commits"][0])
            assert _day(dated).year < _day(first).year, f"{path} does not look old: {dated}"
            assert ev["claim_line"] in text and ev["code_line"] in gitlib.blob(built.root, "HEAD", ev["code"]), path
            assert _number(ev["claim_line"]) == _number(ev["code_line"]), f"{path} disagrees with the code"


def test_the_live_file_in_a_legacy_folder_is_live(ground):
    for built in ground.values():
        for control in built.manifest["controls"]:
            if control["kind"] != "live-file-in-legacy-folder":
                continue
            path, ev = control["paths"][0], control["evidence"]
            assert set(Path(path).parts[:-1]) & set(LEGACY_FOLDERS), f"{path} is not under a legacy-sounding folder"
            assert path in gitlib.tree(built.root)
            holders = gitlib.files_holding(built.root, ev["token"]) - {path}
            assert ev["referenced_by"] and set(ev["referenced_by"]) <= holders, f"{path}: not referenced"


def test_the_stale_spec_looks_current_and_is_contradicted_by_the_code_and_a_newer_spec(ground):
    for built, entry in _entries(ground, "stale-spec"):
        ev, root = entry["evidence"], built.root
        stale, governing = gitlib.blob(root, "HEAD", ev["stale"]), gitlib.blob(root, "HEAD", ev["governing"])
        assert stale and governing, entry["id"]
        assert ev["status_line"] in stale and ev["review_line"] in stale and ev["claim_line"] in stale, entry["id"]
        assert ev["code_line"] in gitlib.blob(root, "HEAD", ev["code"]), f"{entry['id']}: the code"
        assert ev["governing_line"] in governing and ev["claim_line"] not in governing, entry["id"]
        assert _number(ev["claim_line"]) != _number(ev["code_line"]) == _number(ev["governing_line"]), entry["id"]
        assert ev["names"] in governing, f"{entry['id']}: the newer spec does not name the one it replaces"
        head_day = _day(gitlib.commit_day(root, "HEAD"))
        reviewed = _day(ev["reviewed"])
        assert 0 <= (head_day - reviewed).days <= 14, f"{entry['id']}: its date is not recent"
        assert reviewed >= _day(gitlib.commit_day(root, entry["commits"][1])), \
            f"{entry['id']}: reviewed before the newer spec was written"


def test_the_superseded_plans_successor_exists_and_names_it(ground):
    for built, entry in _entries(ground, "superseded-plan"):
        ev, root = entry["evidence"], built.root
        plan, successor = gitlib.blob(root, "HEAD", ev["plan"]), gitlib.blob(root, "HEAD", ev["successor"])
        assert plan and successor, f"{entry['id']}: both plans are at HEAD"
        older, newer = entry["commits"]
        order = built.manifest["commits"]
        assert order.index(older) < order.index(newer), entry["id"]
        if ev["link"] == "names-it":
            assert ev["plan"] in successor, f"{entry['id']}: the successor does not name it"
        else:
            assert f"plan: {ev['plan_id']}\nversion: 1" in plan, entry["id"]
            assert f"plan: {ev['plan_id']}\nversion: 2\nsupersedes: version {ev['version']}" in successor, \
                entry["id"]


def test_the_misleading_names_are_live_or_dead_by_their_references(ground):
    for built, entry in _entries(ground, "misleading-name"):
        ev, root, path = entry["evidence"], built.root, entry["paths"][0]
        assert path in gitlib.tree(root), entry["id"]
        holders = gitlib.files_holding(root, ev["token"]) - {path}
        name = Path(path).name.lower()
        if ev["live"]:
            assert any(w in name for w in OLD_WORDS), f"{path}: its name does not say old"
            assert ev["referenced_by"] and set(ev["referenced_by"]) <= holders, f"{path}: not referenced"
        else:
            assert any(w in name for w in CURRENT_WORDS), f"{path}: its name does not say current"
            assert holders == set(), f"{path}: referenced by {sorted(holders)}"


def test_the_orphaned_tests_subject_is_gone(ground):
    for built, entry in _entries(ground, "orphaned-test"):
        ev, root = entry["evidence"], built.root
        test = gitlib.blob(root, "HEAD", ev["test"])
        assert test and ev["used_as"] in test, f"{entry['id']}: the test is not at HEAD as it was"
        assert gitlib.files_holding(root, ev["definition"]) == set(), f"{entry['id']}: its subject is still defined"
        source = ev["subject"].split("::")[0]
        before = gitlib.blob(root, f"{ev['removed_in']}^", source)
        assert before and ev["definition"] in before, f"{entry['id']}: the subject never existed"
        if "::" not in ev["subject"]:
            assert source not in gitlib.tree(root), f"{entry['id']}: the subject's file is still at HEAD"


def test_the_legacy_documents_are_planted(ground):
    entries = _entries(ground, "legacy-document")
    assert sorted(e["evidence"]["handling"] for _, e in entries) == ["extract", "retire"]
    for built, entry in entries:
        assert gitlib.blob(built.root, "HEAD", entry["evidence"]["path"]), entry["id"]


def test_the_large_files_are_at_the_size_asked_in_the_built_repository_only(ground, run_folder):
    legacy = ground["legacy-docs"]
    others = [gitlib.blob_size(legacy.root, "HEAD", p) for p in gitlib.tree(legacy.root)
              if p not in {e["evidence"]["path"] for _, e in _entries(ground, "large-file")}]
    for _, entry in _entries(ground, "large-file"):
        path, size = entry["evidence"]["path"], entry["evidence"]["size"]
        assert size == build.SELF_TEST_LARGE
        assert (legacy.root / path).stat().st_size == size == gitlib.blob_size(legacy.root, "HEAD", path), path
        assert size > 50 * max(others), f"{path} is not large beside the other files"
        assert not (gitlib.REPO_ROOT / path).exists(), f"{path} exists in this repository"
    asked = 123_457
    other = build.build_legacy(run_folder / "repos" / "legacy-docs", 5, run_folder, large_size=asked)
    for entry in other.manifest["planted"]:
        if entry["kind"] == "large-file":
            assert (other.root / entry["evidence"]["path"]).stat().st_size == asked == entry["evidence"]["size"]
    build.remove(run_folder)

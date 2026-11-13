"""The seed: one seed builds the same repositories and manifests; another changes names, places and wording."""

from __future__ import annotations

import json

import w2_81_build as build
import w2_81_git as gitlib
from w2_81_words import DEFAULT_SEED

OTHER_SEED = DEFAULT_SEED + 1


def _paths(manifest):
    return [tuple(e["paths"]) for e in manifest["planted"] + manifest["controls"]]


def test_the_seed_is_recorded_in_every_manifest(ground):
    for name, built in ground.items():
        assert built.manifest["seed"] == DEFAULT_SEED, name
        assert json.loads(built.manifest_path.read_text())["seed"] == DEFAULT_SEED, name


def test_the_same_seed_builds_the_same_trees_histories_and_manifests(ground, run_folder):
    again = build.build_all(run_folder, DEFAULT_SEED)
    for name, built in ground.items():
        twin = again[name]
        assert twin.manifest == built.manifest, f"{name}: the manifest differs for the same seed"
        assert twin.manifest_path.read_bytes() == built.manifest_path.read_bytes(), name
        assert gitlib.run_git(twin.root, "rev-parse", "HEAD^{tree}") == \
            gitlib.run_git(built.root, "rev-parse", "HEAD^{tree}"), f"{name}: the tree differs"
        assert gitlib.run_git(twin.root, "rev-parse", "HEAD") == gitlib.run_git(built.root, "rev-parse", "HEAD"), \
            f"{name}: the history differs for the same seed"
        assert twin.secrets == built.secrets, f"{name}: the planted secret differs for the same seed"
    build.remove(run_folder)


def test_another_seed_changes_names_places_and_wording(ground, run_folder):
    other = build.build_all(run_folder, OTHER_SEED)
    changed, total = 0, 0
    for name, built in ground.items():
        mine, theirs = built.manifest, other[name].manifest
        assert theirs["seed"] == OTHER_SEED
        assert _paths(mine) != _paths(theirs), f"{name}: no planted path or control moved with the seed"
        assert mine["head"] != theirs["head"], f"{name}: the history is the same for another seed"
        messages = [gitlib.run_git(r, "log", "--format=%s") for r in (built.root, other[name].root)]
        assert messages[0] != messages[1], f"{name}: the commit wording is the same for another seed"
        for a, b in zip(mine["planted"] + mine["controls"], theirs["planted"] + theirs["controls"]):
            total += 1
            changed += a["paths"] != b["paths"] or a["evidence"] != b["evidence"]
        for a, b in zip(built.secrets, other[name].secrets):
            assert a != b, f"{name}: the planted secret is the same for another seed"
    # Each instance draws from finite pools, so one may repeat by chance; nearly all must change.
    assert changed >= 0.9 * total, f"only {changed} of {total} instances changed with the seed"
    build.remove(run_folder)

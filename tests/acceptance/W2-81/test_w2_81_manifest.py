"""The manifest: its form, kept outside the built repository and absent from its history."""

from __future__ import annotations

import copy
import json

import w2_81_git as gitlib
import w2_81_manifest as manifest_form


def _refused(data):
    try:
        manifest_form.validate(data)
    except AssertionError as refused:
        return str(refused)
    return None


def test_each_manifest_is_beside_its_repository_never_inside(ground):
    for name, built in ground.items():
        assert built.manifest_path.is_file(), name
        assert not gitlib._inside(built.manifest_path, built.root), f"{name}: the manifest is inside the repository"
        assert built.manifest_path.parent.parent == built.root.parent.parent, name
        assert manifest_form.load(built.manifest_path) == built.manifest, name


def test_no_manifest_is_in_any_repositorys_history(ground):
    for name, built in ground.items():
        touched = gitlib.history_paths(built.root)
        assert not [p for p in touched if p.endswith(".json") and "manifest" in p], name
        history = gitlib.run_git(built.root, "log", "--all", "-p", "--format=%H %s%n%b")
        assert manifest_form.FORM not in history, f"{name}: the manifest's form is in the history"
        for entry in built.manifest["planted"] + built.manifest["controls"]:
            assert entry["id"] not in history, f"{name}: {entry['id']} is named in the history"
            assert entry["correct_handling" if "correct_handling" in entry else "flagging_looks_like"] \
                not in history, f"{name}: {entry['id']}'s handling is written in the repository"


def test_each_planted_entry_holds_what_the_judge_reads(ground):
    for built in ground.values():
        data = built.manifest
        assert data["form"] == manifest_form.FORM and data["head"] == data["commits"][-1]
        for entry in data["planted"]:
            assert entry["detectable_by"] == manifest_form.DETECTABLE_BY[entry["kind"]], entry["id"]
            assert entry["correct_handling"] == manifest_form.CORRECT_HANDLING[entry["kind"]], entry["id"]
            assert entry["paths"] and entry["commits"], entry["id"]
            assert set(entry["commits"]) <= set(data["commits"]), f"{entry['id']}: a commit not in the history"
            for path in entry["paths"]:
                assert path in gitlib.history_paths(built.root), f"{entry['id']}: {path} is in no commit"
        for control in data["controls"]:
            assert control["flagging_looks_like"] == manifest_form.CONTROL_FLAGGING[control["kind"]]


def test_a_secrets_entry_holds_path_commits_and_rule_never_a_value(ground):
    for built in ground.values():
        for entry in built.manifest["planted"]:
            if entry["kind"] == "secret":
                assert set(entry["evidence"]) == {"path", "added_in", "removed_in", "rule", "form"}, entry["id"]
                assert len(entry["evidence"]["added_in"]) == len(entry["evidence"]["removed_in"]) == 12


def test_every_commit_in_a_manifest_has_twelve_digits(ground):
    for built in ground.values():
        text = built.manifest_path.read_text()
        for word in json.loads(text)["commits"]:
            assert len(word) == 12
        assert not any(len(full) == 40 and full in text for full in gitlib.all_commits(built.root))


def test_a_malformed_manifest_is_refused(ground):
    good = ground["python-app"].manifest
    assert _refused(copy.deepcopy(good)) is None
    missing = copy.deepcopy(good)
    del missing["controls"]
    assert _refused(missing)
    full_hash = copy.deepcopy(good)
    full_hash["planted"][0]["commits"] = ["0" * 40]
    assert "12-digit" in _refused(full_hash)
    clean = copy.deepcopy(good)
    clean["clean"] = True
    assert "clean" in _refused(clean)
    duplicate = copy.deepcopy(good)
    duplicate["planted"].append(copy.deepcopy(duplicate["planted"][0]))
    assert "duplicate" in _refused(duplicate)
    secret = copy.deepcopy(ground["secret-history"].manifest)
    for entry in secret["planted"]:
        if entry["kind"] == "secret":
            del entry["evidence"]["rule"]
    assert "rule" in _refused(secret)


def test_a_manifest_is_never_written_inside_the_repository(ground):
    built = ground["rust-workspace"]
    try:
        manifest_form.write(built.manifest, built.root, built.root)
    except AssertionError as refused:
        assert "never written inside" in str(refused)
    else:
        raise AssertionError("a manifest was written inside the built repository")
    assert not (built.root / "manifests").exists()

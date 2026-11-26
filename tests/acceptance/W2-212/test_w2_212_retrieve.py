"""W2-212 SR-1, SR-2, F1 (index built before the class): the default bundle and the stale list."""
from __future__ import annotations

import json

import pytest

from w2_212_support import (NEW, OLD, OLD_WORD, PATH_MAP, QUESTION, ask, build_retrieval, bundle_paths, cli_args,
                            commit, path_map)


def test_sr1_default_bundle_leaves_the_stale_design_out_and_keeps_the_current(tmp_path, monkeypatch):
    root, _ = build_retrieval(tmp_path, monkeypatch, "superseded")
    bundle = ask(root, include_stale=False)  # the keyword is the interface: absent on the base
    assert NEW in bundle_paths(bundle)
    assert OLD not in bundle_paths(bundle) and all(OLD_WORD not in item["text"] for item in bundle["evidence"])
    assert not bundle.get("stale")


@pytest.mark.parametrize("stale", ["historical", "legacy"])
def test_sr1_each_class_is_left_out(tmp_path, monkeypatch, stale):
    root, _ = build_retrieval(tmp_path, monkeypatch, stale)
    bundle = ask(root, include_stale=False)
    assert NEW in bundle_paths(bundle) and OLD not in bundle_paths(bundle)


def test_f1_a_file_indexed_before_the_class_is_still_left_out_of_every_route(tmp_path, monkeypatch):
    """Index and vectors built with the old design indexed; the class (and policies) added after, no rebuild."""
    root, held = build_retrieval(tmp_path, monkeypatch, None)
    assert OLD in {c["path"] for c in held}, "the plant is wrong: the old design was not indexed first"
    before = ask(root, include_stale=False)
    assert OLD in bundle_paths(before), "the plant is wrong: the unclassed design should be found"
    commit(root, {PATH_MAP: path_map("superseded")}, "classify the old design")
    bundle = ask(root, include_stale=False)
    assert OLD not in bundle_paths(bundle) and all(OLD_WORD not in item["text"] for item in bundle["evidence"])
    assert NEW in bundle_paths(bundle)


def test_sr2_the_flag_lists_the_stale_file_marked_with_its_excerpt(tmp_path, monkeypatch):
    root, _ = build_retrieval(tmp_path, monkeypatch, "superseded")
    bundle = ask(root, include_stale=True)
    [entry] = [e for e in bundle["stale"] if e["path"] == OLD]
    assert entry["stale"] is True and entry["stale_class"] == "superseded" and entry["namespace"] == "old-design"
    assert OLD_WORD in entry["excerpt"]
    assert NEW in bundle_paths(bundle)


def test_sr2_a_question_naming_the_path_lists_it_without_the_flag(tmp_path, monkeypatch):
    root, _ = build_retrieval(tmp_path, monkeypatch, "legacy")
    bundle = ask(root, f"what does {OLD} say")
    [entry] = [e for e in bundle["stale"] if e["path"] == OLD]
    assert entry["stale"] is True and entry["stale_class"] == "legacy" and OLD_WORD in entry["excerpt"]


def test_sr2_without_flag_or_named_path_there_is_no_stale_list(tmp_path, monkeypatch):
    root, _ = build_retrieval(tmp_path, monkeypatch, "superseded")
    assert not ask(root, include_stale=False).get("stale")
    assert not ask(root, f"what does {NEW} say", include_stale=False).get("stale")


def test_sr2_the_command_takes_the_flag_and_carries_the_list(tmp_path, monkeypatch):
    from gov.retrieve import command
    root, _ = build_retrieval(tmp_path, monkeypatch, "historical")
    plain = command.run(root, cli_args(QUESTION), {})
    assert OLD not in bundle_paths(plain) and not plain.get("stale")
    flagged = command.run(root, cli_args(QUESTION, "--include-stale"), {})
    json.dumps(flagged)  # the JSON output carries it
    [entry] = [e for e in flagged["stale"] if e["path"] == OLD]
    assert entry["stale"] is True and entry["stale_class"] == "historical"
    named = command.run(root, cli_args(f"what does {OLD} say"), {})
    assert [e["path"] for e in named["stale"]] == [OLD]


def test_sr2_gov_retrieve_help_names_the_flag():
    import subprocess
    import sys
    from w2_212_support import SRC
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "retrieve", "--help"], capture_output=True, text=True,
                          env={"PYTHONPATH": str(SRC), "PATH": "/usr/bin:/bin"})
    assert "--include-stale" in done.stdout

"""The planted secret: in history only, found by the scanner, its value nowhere but in memory (DEC-911, CAP-03.a).

Every check compares in memory. A failure names the repository, the path and
the commit, never the value: absence is asserted through ``assert_absent``,
and a ``Held`` value's ``repr`` withholds it.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import w2_81_build as build
import w2_81_git as gitlib
from w2_81_secret import FORMS, Held, assert_absent, scan_history

SUITE = Path(__file__).resolve().parent


def _planted_secrets(ground):
    for built in ground.values():
        for entry in built.manifest["planted"]:
            if entry["kind"] == "secret":
                held = [h for h in built.secrets if h.form == entry["evidence"]["form"]]
                assert len(held) == 1, f"{entry['id']}: the builder returned no value to compare with"
                yield built, entry, held[0]


def test_the_secret_is_in_two_repositories_and_two_forms(ground):
    found = list(_planted_secrets(ground))
    assert {b.name for b, _, _ in found} >= {"secret-history"} and len({b.name for b, _, _ in found}) >= 2
    assert len({e["evidence"]["form"] for _, e, _ in found}) >= 2
    for built in ground.values():
        planted = {e["evidence"]["form"] for e in built.manifest["planted"] if e["kind"] == "secret"}
        assert {h.form for h in built.secrets} == planted, built.name


def test_the_secret_is_in_an_early_commit_and_not_at_head(ground):
    for built, entry, held in _planted_secrets(ground):
        ev = entry["evidence"]
        order = built.manifest["commits"]
        assert order.index(ev["added_in"]) < order.index(ev["removed_in"]) < len(order), entry["id"]
        assert order.index(ev["added_in"]) <= len(order) // 2, f"{entry['id']}: not an early commit"
        present = held.found_in(gitlib.blob(built.root, ev["added_in"], ev["path"]))
        assert present, f"{entry['id']}: not in {ev['path']} at {ev['added_in']}"
        for rel in gitlib.tree(built.root):
            assert_absent(held, gitlib.blob(built.root, "HEAD", rel), f"{built.name}: {rel} at HEAD")
        for rel in gitlib.tree(built.root):
            assert_absent(held, (built.root / rel).read_bytes(), f"{built.name}: {rel} in the working tree")


def test_the_scanner_finds_each_secret_in_history_with_the_manifests_rule_path_and_commit(ground, scans):
    for name, built in ground.items():
        findings, _ = scans[name]
        expected = sorted((e["evidence"]["rule"], e["evidence"]["path"], e["evidence"]["added_in"])
                          for e in built.manifest["planted"] if e["kind"] == "secret")
        got = sorted((f.rule, f.path, f.commit) for f in findings)
        assert got == expected, f"{name}: the scanner found {got}, the manifest holds {expected}"
    for _, entry, _ in _planted_secrets(ground):
        assert entry["evidence"]["rule"] == FORMS[entry["evidence"]["form"]]["rule"]


def test_the_value_is_in_no_manifest_no_scanner_output_and_no_file_of_this_suite(ground, scans):
    secrets = [held for _, _, held in _planted_secrets(ground)]
    for held in secrets:
        for built in ground.values():
            assert_absent(held, built.manifest_path.read_text(), f"the manifest {built.manifest_path.name}")
            assert_absent(held, json.dumps(built.manifest), f"{built.name}'s manifest in memory")
            assert_absent(held, repr(built), f"{built.name}'s builder return, shown")
        for name, (_, outputs) in scans.items():
            for what, text in outputs.items():
                assert_absent(held, text, f"{name}: {what}")
        for path in sorted(SUITE.rglob("*")):
            if path.is_file():
                assert_absent(held, path.read_bytes(), f"the suite's file {path.relative_to(SUITE)}")
        assert_absent(held, repr(held) + str(held), "a held value's repr")


def test_a_build_prints_no_value(run_folder, capfd):
    built = build.build_all(run_folder, 4096)
    out, err = capfd.readouterr()
    for b in built.values():
        for held in b.secrets:
            assert_absent(held, out, f"{b.name}: the build's standard output")
            assert_absent(held, err, f"{b.name}: the build's standard error")
    build.remove(run_folder)


def test_assert_absent_names_the_place_never_the_value():
    held = Held("x" * 8 + "-planted", "forge-token")
    try:
        assert_absent(held, "a line with " + "x" * 8 + "-planted in it", "scripts/publish.sh at 0123456789ab")
    except AssertionError as caught:
        message = str(caught)
        assert "scripts/publish.sh at 0123456789ab" in message
        assert_absent(held, message, "the failure message")
    else:
        raise AssertionError("assert_absent let a value through")


def test_the_suites_own_files_hold_no_secret_the_scanner_detects(tmp_path):
    report = tmp_path / "suite.json"
    done = subprocess.run(["gitleaks", "dir", str(SUITE), "--redact", "--no-banner", "--report-format", "json",
                           "--report-path", str(report)], capture_output=True, text=True,
                          env=gitlib.git_env(tmp_path))
    assert done.returncode in (0, 1) and report.is_file(), f"gitleaks dir failed (exit {done.returncode})"
    findings = json.loads(report.read_text() or "[]")
    assert findings == [], f"the scanner finds {len(findings)} secrets in the suite's own files: " \
                           f"{[(f['RuleID'], f['File']) for f in findings]}"


def test_scan_history_is_redacted_and_reports_twelve_digit_commits(ground, tmp_path):
    findings, outputs = scan_history(ground["secret-history"].root, tmp_path)
    assert findings and all(len(f.commit) == 12 for f in findings)
    assert "REDACTED" in outputs["gitleaks report"]

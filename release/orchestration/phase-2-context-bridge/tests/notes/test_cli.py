"""``govbridge notes validate <file>`` (REPAIR_DAG.yaml node R1-RN deliverable). Not yet wired into the top-level
``govbridge`` dispatcher (govbridge/cli.py is outside this node's mutation_scope -- see govbridge/notes/cli.py's
own docstring), so this is exercised as ``python -m govbridge.notes.cli validate <file>`` and via direct
``main()`` calls, both of which will keep working unchanged once that one dispatch line is added.
"""
from __future__ import annotations

import json
import subprocess
import sys

import yaml

from govbridge import GOV_BRIDGE_DOMAIN
from govbridge.notes import build as buildmod
from govbridge.notes import cli as notescli
from govbridge.core.yamlutil import sha256_text


def _write_note_yaml(tmp_path, note, name="note.yaml"):
    p = tmp_path / name
    p.write_text(yaml.safe_dump(note, sort_keys=False), encoding="utf-8")
    return p


def _good_note(repo):
    source = {
        "item_id": "U-1", "path": repo.path_a, "commit": repo.commit, "blob": repo.blob_a,
        "lines": repo.lines_a_1_2, "content_sha256": sha256_text(repo.text_a_1_2),
    }
    claims = [{"claim_id": "C-1", "text": "x", "sources": [source]}]
    return buildmod.build_note("N-1", claims, unresolved=[])


def test_cli_validate_main_exit_0_for_valid_note(notes_repo, tmp_path, capsys):
    note_path = _write_note_yaml(tmp_path, _good_note(notes_repo))
    rc = notescli.main(["validate", str(note_path), "--repo", str(notes_repo.root)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "PASS"


def test_cli_validate_main_exit_1_for_refused_note(notes_repo, tmp_path, capsys):
    note = _good_note(notes_repo)
    note["claims"][0]["sources"] = []
    note_path = _write_note_yaml(tmp_path, note)
    rc = notescli.main(["validate", str(note_path), "--repo", str(notes_repo.root)])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "FAIL"


def test_cli_validate_target_section_a_refused(notes_repo, tmp_path, capsys):
    note_path = _write_note_yaml(tmp_path, _good_note(notes_repo))
    rc = notescli.main(["validate", str(note_path), "--repo", str(notes_repo.root), "--target-section", "A"])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "FAIL"


def test_cli_json_output_over_stdin_free_file(notes_repo, tmp_path):
    note_path = tmp_path / "note.json"
    note_path.write_text(json.dumps(_good_note(notes_repo)), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-m", "govbridge.notes.cli", "validate", str(note_path), "--repo", str(notes_repo.root)],
        cwd=GOV_BRIDGE_DOMAIN, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "PASS"


def test_cli_unknown_subcommand_exits_2():
    rc = notescli.main(["bogus"])
    assert rc == 2


def test_cli_build_then_validate_roundtrip(notes_repo, tmp_path, capsys):
    spec = {
        "note_id": "N-1",
        "claims": [{
            "claim_id": "C-1", "text": "x",
            "sources": [{
                "item_id": "U-1", "path": notes_repo.path_a, "commit": notes_repo.commit, "blob": notes_repo.blob_a,
                "lines": notes_repo.lines_a_1_2, "content_sha256": sha256_text(notes_repo.text_a_1_2),
            }],
        }],
        "unresolved": [],
    }
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")

    rc = notescli.main(["build", str(spec_path)])
    assert rc == 0
    built = json.loads(capsys.readouterr().out)
    assert built["class"] == "DERIVED_NOTE"

    note_path = tmp_path / "built-note.json"
    note_path.write_text(json.dumps(built), encoding="utf-8")
    rc = notescli.main(["validate", str(note_path), "--repo", str(notes_repo.root)])
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "PASS"

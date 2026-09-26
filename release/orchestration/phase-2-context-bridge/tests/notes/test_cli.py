"""``govbridge notes validate <file>`` (REPAIR_DAG.yaml node R1-RN deliverable). Most of this file exercises
``python -m govbridge.notes.cli validate <file>`` and direct ``notescli.main()`` calls directly, independent of the
top-level dispatcher. The top-level ``govbridge notes ...`` dispatch line itself (REPAIR_DAG.yaml node R1-GA1,
BR-AR-0023 -- routed from R1-RN, whose own mutation_scope did not include govbridge/cli.py) is exercised at the
bottom of this file, through ``govbridge.cli`` and ``python -m govbridge``.
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


# --- the top-level `govbridge notes ...` dispatch line (REPAIR_DAG.yaml node R1-GA1, routed from R1-RN) ---------

def test_govbridge_notes_dispatches_to_notes_cli_in_process(notes_repo, tmp_path, capsys):
    """``govbridge.cli.main(["notes", ...])`` must reach ``govbridge.notes.cli.main`` -- proved end to end with a
    real ``validate`` call through the TOP-LEVEL dispatcher, the same subcommand the tests above already exercise
    directly against ``notescli.main``."""
    from govbridge import cli as climod

    note_path = _write_note_yaml(tmp_path, _good_note(notes_repo))
    rc = climod.main(["notes", "validate", str(note_path), "--repo", str(notes_repo.root)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "PASS"


def test_govbridge_notes_help_dispatches_reaches_notes_cli_not_the_top_level_unknown_command(capsys):
    """"``govbridge notes --help`` dispatches": ``--help`` is not a subcommand ``govbridge.notes.cli.main`` itself
    recognises (it has no argparse-based top level, module docstring), so it falls through to that module's OWN
    "unknown subcommand" message -- proving the dispatch line actually forwarded ``rest`` into
    ``notescli.main(["--help"])`` rather than the top-level dispatcher reporting "unknown command 'notes'" (its own,
    DIFFERENT message, for a command it does not recognise at all)."""
    from govbridge import cli as climod

    rc = climod.main(["notes", "--help"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "govbridge notes: unknown subcommand '--help'" in err
    assert "unknown command 'notes'" not in err


def test_govbridge_notes_help_dispatches_via_python_dash_m():
    """The same dispatch, exercised as a real subprocess (``python -m govbridge notes --help``), so this also
    proves ``govbridge/__main__.py`` -> ``govbridge.cli.main`` -> ``notes`` reaches ``govbridge.notes.cli`` outside
    the test process too."""
    proc = subprocess.run(
        [sys.executable, "-m", "govbridge", "notes", "--help"], cwd=GOV_BRIDGE_DOMAIN, capture_output=True, text=True,
    )
    assert proc.returncode == 2
    assert "govbridge notes: unknown subcommand '--help'" in proc.stderr

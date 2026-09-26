"""BR-DAG-AMEND-R1-19, wired by this node (R1-RA, the last editor of ``govbridge/cli.py`` in the RX -> GA1 -> RS ->
RA sequence): ``govbridge gather`` now calls ``govbridge.gather.followup.gather_with_followup`` by default, and
only the ``--no-followup`` flag falls back to the single-pass ``govbridge.gather.engine.gather`` this command used
before this node. This test lives under ``tests/answers/**`` (this node's own mutation scope does not reach
``tests/gather/**``, R1-GA2's) and tests ``govbridge.cli`` itself -- structural wiring, not retrieval QUALITY
(R1-GA1/R1-GA2 already own that): the DEFAULT result carries follow-up-only keys (``followup_rounds``,
``visited_identifiers``) that the single-pass engine's own output never has, and ``--no-followup`` reproduces this
command's EXACT pre-existing output shape. ``--out`` (R1-RS's supplementary-packet flag) is exercised in both
modes, since this node's brief requires keeping it working.

The ``evidence_staleness`` facet (``config/facets.yaml``) is deliberately chosen: ``routes: [lexical]`` only, so
this test never loads the (heavier) semantic embedding model or needs the code layer -- it is a wiring test, not a
retrieval-quality one.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

FIXTURES_ANSWERS = Path(__file__).resolve().parents[1] / "fixtures" / "answers"
if str(FIXTURES_ANSWERS) not in sys.path:
    sys.path.insert(0, str(FIXTURES_ANSWERS))
import answers_repobuilder as repobuilder  # noqa: E402

from govbridge import cli  # noqa: E402
from govbridge.core import freshness as freshnessmod  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store-test-gather-wiring"))
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)


@pytest.fixture()
def built(tmp_path):
    repo = repobuilder.build(tmp_path)
    r = freshnessmod.run(view_path=repo.view_path, rules_path=repo.rules_path, repo=str(repo.root), from_clean=True)
    assert r["trigger"] == "FULL"
    return repo


def _task_spec_path(tmp_path: Path, built) -> str:
    p = tmp_path / "task-spec.yaml"
    p.write_text(
        "schema: govbridge-task-spec/1\n"
        "task_id: T-RA-GATHER-WIRING\n"
        "role: test\n"
        "objective: BR-DAG-AMEND-R1-19 wiring test\n"
        f"view: {built.view_path}\n",
        encoding="utf-8",
    )
    return str(p)


def _gather_argv(task_path: str, built, extra=()):
    return ["gather", "--task", task_path, "--query", "ra_unique_fn", "--facets", "evidence_staleness",
            "--registry", built.registry_path, "--repo", str(built.root), "--json", *extra]


def test_default_gather_uses_followup_and_carries_its_own_keys(tmp_path, built, capsys):
    task_path = _task_spec_path(tmp_path, built)
    rc = cli.main(_gather_argv(task_path, built))
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    assert "followup_rounds" in result
    assert "visited_identifiers" in result
    assert result["stop_reason"]


def test_no_followup_reproduces_the_single_pass_engine_shape(tmp_path, built, capsys):
    task_path = _task_spec_path(tmp_path, built)
    rc = cli.main(_gather_argv(task_path, built, extra=["--no-followup"]))
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    assert "followup_rounds" not in result
    assert "visited_identifiers" not in result
    assert set(result) == {"query", "batch_size", "max_rounds", "threads", "facets", "stop_reason", "merged",
                            "merged_sha256", "telemetry", "excluded_hits"}


def test_out_supplementary_packet_still_works_in_both_modes(tmp_path, built):
    task_path = _task_spec_path(tmp_path, built)

    for label, extra in (("followup", []), ("no_followup", ["--no-followup"])):
        out_dir = tmp_path / f"supp_{label}"
        argv = ["gather", "--task", task_path, "--query", "ra_unique_fn", "--facets", "evidence_staleness",
                "--registry", built.registry_path, "--repo", str(built.root), "--out", str(out_dir), *extra]
        rc = cli.main(argv)
        assert rc == 0, label
        assert (out_dir / "manifest.json").exists(), label
        assert (out_dir / "packet.md").exists(), label
        meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
        assert meta["packet_kind"] == "supplementary", label

        rc_verify = cli.main(["packet", "verify", str(out_dir), "--repo", str(built.root),
                               "--registry", built.registry_path])
        assert rc_verify == 0, label


def test_default_and_no_followup_both_report_a_valid_stop_reason(tmp_path, built, capsys):
    from govbridge.gather import engine as enginemod

    task_path = _task_spec_path(tmp_path, built)
    cli.main(_gather_argv(task_path, built))
    default_result = json.loads(capsys.readouterr().out)
    cli.main(_gather_argv(task_path, built, extra=["--no-followup"]))
    no_followup_result = json.loads(capsys.readouterr().out)

    assert default_result["stop_reason"] in enginemod.STOP_REASONS
    assert no_followup_result["stop_reason"] in enginemod.STOP_REASONS

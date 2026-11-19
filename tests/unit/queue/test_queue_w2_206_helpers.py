"""W2-206: the helpers of ``gov queue``'s new flags: the full run's worker cap (DEC-1216 (5)), the after-step's
notices (L2 A8) and the dry run's out folder (L2 A6)."""
from __future__ import annotations

import pytest

from gov.cli.errors import GovError
from gov.queue import after, dry, full

PATH_MAP = "governance/project/path-map.yaml"
REBUILD = "governance/project/rebuild.yaml"


def _clear(monkeypatch):
    for name in ("PYTEST_XDIST_AUTO_NUM_WORKERS", "GOV_HEAVY_CPUS", "GOV_HEAVY_WORKERS", "GOV_HEAVY_SLOTS"):
        monkeypatch.delenv(name, raising=False)


def _map(root, text):
    (root / PATH_MAP).parent.mkdir(parents=True, exist_ok=True)
    (root / PATH_MAP).write_text(text, encoding="utf-8")


# -- the worker cap ---------------------------------------------------------------------------------------------

def test_the_cap_is_the_smallest_of_the_path_map_the_variable_and_the_slot_s_cpus(tmp_path, monkeypatch):
    _clear(monkeypatch)
    _map(tmp_path, "close_workers: 12\n")
    monkeypatch.setenv("GOV_HEAVY_CPUS", "0-1")
    monkeypatch.setenv("PYTEST_XDIST_AUTO_NUM_WORKERS", "2")
    assert full.cap(tmp_path) == {"workers": 2, "cpus": "0-1"}
    monkeypatch.setenv("PYTEST_XDIST_AUTO_NUM_WORKERS", "5")
    assert full.cap(tmp_path)["workers"] == 2
    monkeypatch.setenv("GOV_HEAVY_CPUS", "0-7,9")
    assert full.cap(tmp_path) == {"workers": 5, "cpus": "0-7,9"}
    _map(tmp_path, "close_workers: 3\n")
    assert full.cap(tmp_path)["workers"] == 3


def test_a_path_map_number_alone_is_the_cap(tmp_path, monkeypatch):
    _clear(monkeypatch)
    _map(tmp_path, "close_workers: 4\n")
    assert full.cap(tmp_path) == {"workers": 4, "cpus": None}


@pytest.mark.parametrize("text", ["close_workers: auto\n", "close_workers: true\n", "close_workers: 0\n", "[\n", ""])
def test_with_no_number_anywhere_the_cap_is_one_slot_s_workers_by_the_product_s_rules(tmp_path, monkeypatch, text):
    from gov.dispatch import admission
    from gov.resources import slots

    _clear(monkeypatch)
    if text:
        _map(tmp_path, text)
    monkeypatch.setattr(admission, "sized", lambda: {"load_limit": 20, "start_below": 12, "margin": 1.0,
                                                     "heavy_slots": 2})
    monkeypatch.setattr(slots, "slot_count", lambda conf, say: 2)
    assert full.cap(tmp_path) == {"workers": 4, "cpus": None}  # floor((20 - 12) / (1.0 x 2)), never the CPU count
    monkeypatch.setenv("GOV_HEAVY_WORKERS", "3")  # as a slot's run reads it
    assert full.cap(tmp_path)["workers"] == 3


def test_the_cap_is_at_least_one_where_the_product_cannot_size_a_slot(tmp_path, monkeypatch):
    from gov.dispatch import admission

    _clear(monkeypatch)

    def broken():
        raise OSError("no reading")

    monkeypatch.setattr(admission, "sized", broken)
    assert full.cap(tmp_path) == {"workers": 1, "cpus": None}


def test_a_variable_that_names_no_number_is_not_a_cap(tmp_path, monkeypatch):
    _clear(monkeypatch)
    _map(tmp_path, "close_workers: 6\n")
    monkeypatch.setenv("PYTEST_XDIST_AUTO_NUM_WORKERS", "auto")
    monkeypatch.setenv("GOV_HEAVY_CPUS", "")
    assert full.cap(tmp_path) == {"workers": 6, "cpus": None}


def test_the_run_s_children_get_the_cap_as_the_auto_number_and_the_caller_s_value_comes_back(monkeypatch):
    import os

    monkeypatch.setenv("PYTEST_XDIST_AUTO_NUM_WORKERS", "9")
    with full.capped(2):
        assert os.environ["PYTEST_XDIST_AUTO_NUM_WORKERS"] == "2"
    assert os.environ["PYTEST_XDIST_AUTO_NUM_WORKERS"] == "9"
    monkeypatch.delenv("PYTEST_XDIST_AUTO_NUM_WORKERS")
    with pytest.raises(RuntimeError), full.capped(3):
        raise RuntimeError("the run failed")
    assert "PYTEST_XDIST_AUTO_NUM_WORKERS" not in os.environ


def test_the_full_selection_is_the_tests_folder_less_the_candidates_own_acceptance_folders(tmp_path):
    chosen = full.selection(tmp_path, ["tests/acceptance/W-1/", "tests/acceptance/W-2"])
    assert chosen["suites"] == ["tests"] and chosen["full"] is True
    assert chosen["pytest_options"][-2:] == ["--ignore=tests/acceptance/W-1", "--ignore=tests/acceptance/W-2"]
    assert not any(o.startswith("-n") for o in chosen["pytest_options"])


# -- the after-step ---------------------------------------------------------------------------------------------

def _structural(monkeypatch, code=0, lines=("schema: ok", "structural pass at 0123: all 1 ran families ok")):
    from gov.check import structural

    calls = []

    def fake(tree, base, timeout, out):
        calls.append((tree, base, timeout))
        for line in lines:
            print(line, file=out)
        return code

    monkeypatch.setattr(structural, "run_structural", fake)
    return calls


def _refresh(monkeypatch, answer):
    from gov.rebuild import integration

    calls = []

    def fake(root, branch):
        calls.append((root, branch))
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(integration, "refresh", fake)
    return calls


def test_without_a_store_in_rebuild_yaml_the_rebuild_is_not_configured_and_none_runs(tmp_path, monkeypatch):
    from gov.check.structural import DEFAULT_TIMEOUT

    built, passes = _refresh(monkeypatch, {}), _structural(monkeypatch)
    notices = after.run(tmp_path, "main", "b" * 40, tmp_path)
    assert notices["rebuild"] == "not_configured" and built == []
    assert passes == [(tmp_path, "b" * 40, DEFAULT_TIMEOUT)]
    assert notices["structural"] == {"ok": True, "exit": 0, "lines": [
        "schema: ok", "structural pass at 0123: all 1 ran families ok"]}


def _store(root, tmp_path):
    (root / REBUILD).parent.mkdir(parents=True, exist_ok=True)
    (root / REBUILD).write_text(f"integration_store: {tmp_path / 'store'}\n", encoding="utf-8")


def test_a_configured_store_is_refreshed_at_the_branch_and_the_notice_names_its_head(tmp_path, monkeypatch):
    _store(tmp_path, tmp_path)
    built = _refresh(monkeypatch, {"integration": {"head": "c" * 40, "status": "switched"}})
    _structural(monkeypatch)
    notices = after.run(tmp_path, "main", "b" * 40, tmp_path)
    assert built == [(tmp_path, "main")]
    assert notices["rebuild"] == {"ok": True, "head": "c" * 40, "status": "switched"}


def test_a_rebuild_that_fails_is_a_notice_and_the_structural_pass_still_runs(tmp_path, monkeypatch):
    _store(tmp_path, tmp_path)
    _refresh(monkeypatch, GovError("REBUILD_FAILED", "the build failed", {}))
    passes = _structural(monkeypatch)
    notices = after.run(tmp_path, "main", "b" * 40, tmp_path)
    assert notices["rebuild"]["ok"] is False and "REBUILD_FAILED: the build failed" in notices["rebuild"]["reason"]
    assert len(passes) == 1 and notices["structural"]["ok"] is True


def test_a_setting_that_cannot_be_used_and_a_crash_are_notices_too(tmp_path, monkeypatch):
    (tmp_path / REBUILD).parent.mkdir(parents=True)
    (tmp_path / REBUILD).write_text("integration_store: relative/place\n", encoding="utf-8")
    built = _refresh(monkeypatch, {})
    _structural(monkeypatch)
    notices = after.run(tmp_path, "main", "b" * 40, tmp_path)
    assert notices["rebuild"]["ok"] is False and "absolute" in notices["rebuild"]["reason"] and built == []
    _store(tmp_path, tmp_path)
    _refresh(monkeypatch, ValueError("boom"))
    assert after.run(tmp_path, "main", "b" * 40, tmp_path)["rebuild"] == {"ok": False, "head": None,
                                                                         "reason": "ValueError: boom"}


def test_a_structural_pass_that_could_not_run_is_a_notice_with_its_exit_code(tmp_path, monkeypatch):
    _structural(monkeypatch, code=2, lines=())
    notice = after.run(tmp_path, "main", "b" * 40, tmp_path)["structural"]
    assert notice["ok"] is False and notice["exit"] == 2 and notice["lines"] == [] and notice["reason"]


def test_a_structural_pass_that_raises_is_a_notice_and_the_rebuild_s_notice_stands(tmp_path, monkeypatch):
    from gov.check import structural

    def crash(tree, base, timeout, out):
        print("links: ok", file=out)
        raise RuntimeError("no pass")

    monkeypatch.setattr(structural, "run_structural", crash)
    notices = after.run(tmp_path, "main", "b" * 40, tmp_path)
    assert notices["rebuild"] == "not_configured"
    assert notices["structural"] == {"ok": False, "exit": None, "lines": ["links: ok"],
                                     "reason": "RuntimeError: no pass"}


# -- the dry run's out folder -----------------------------------------------------------------------------------

def test_the_default_out_folder_joins_the_tickets_and_a_relative_one_is_the_caller_s(tmp_path, monkeypatch):
    assert dry.out_dir(tmp_path, ["T-a=topic/a"], None) == tmp_path / ".gov-runtime/queue/dry/T-a"
    assert dry.out_dir(tmp_path, ["T-a=topic/a", "T-b"], None) == tmp_path / ".gov-runtime/queue/dry/T-a+T-b"
    monkeypatch.chdir(tmp_path)
    assert dry.out_dir(tmp_path / "p", ["T-a"], "given") == tmp_path / "given"
    assert dry.out_dir(tmp_path, ["../x"], None) == tmp_path / ".gov-runtime/queue/dry/.._x"


def test_the_out_folder_is_written_in_order_and_verify_exit_whole_and_last(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "verify.exit").write_text("0\n", encoding="utf-8")  # an earlier dry run's
    (out / "parallel.xml").write_text("<old/>", encoding="utf-8")
    files = dry.Out(out)
    assert sorted(p.name for p in out.iterdir()) == []
    files.selection({"ticket": "T-a", "suites": ["tests/unit"], "pytest_options": []})
    made = tmp_path / "made"
    made.mkdir()
    (made / "parallel.xml").write_text("<testsuites/>", encoding="utf-8")
    files.runs(made)
    assert not (out / "verify.exit").exists()
    files.finish("queue --dry-run T-a: exit 3: T-a would not land", 3)
    assert (out / "verify.exit").read_text(encoding="utf-8") == "3\n"
    assert (out / "summary.txt").read_text(encoding="utf-8") == "queue --dry-run T-a: exit 3: T-a would not land\n"
    assert (out / "parallel.xml").read_text(encoding="utf-8") == "<testsuites/>"
    assert sorted(p.name for p in out.iterdir()) == ["parallel.xml", "select.json", "summary.txt", "verify.exit"]
    times = {p.name: p.stat().st_mtime_ns for p in out.iterdir()}
    assert max(times, key=times.get) == "verify.exit"

"""ML-1 to ML-3 (W2-204 fix): the printer's launch-line rule, the checker's launch and the writer check's record in the
session folder. Planted roots under ``tmp_path`` only; no session is started."""

from __future__ import annotations

import json

import pytest

from gov.memaudit import brief, say, writercheck

AUDIT = "memory-audit-20261111"


@pytest.mark.parametrize("kind", ["writer", "checker"])
def test_say_judges_a_launch_line_by_the_sets_root_alone(tmp_path, kind):
    root = tmp_path / "sets"
    line = f"LAUNCH {kind} claude -p --settings /x/gov-os-runs/hidden/fixtures/indep-walls/s.json"
    assert not say.refused(line, root)
    assert say.refused(f"{line} --add-dir {root}/w", root)


@pytest.mark.parametrize("line", [
    "LAUNCH other claude -p /x/hidden", "LAUNCH writer sh -c /x/hidden", "LAUNCH writer claude -px /x/hidden",
    "x LAUNCH writer claude -p /x/hidden",
])
def test_say_keeps_the_folder_words_for_any_other_line(tmp_path, line):
    assert say.refused(line, tmp_path / "sets")


def _brief(plant, kind, out):
    lines = []
    brief.run(str(plant.root), AUDIT, kind=kind, commit=plant.repo["head"], repo=plant.repo["path"], out=str(out),
              emit=lines.append)
    return lines


@pytest.fixture
def configured(monkeypatch, tmp_path):
    from gov.memaudit import config

    found = config.current()  # this repository's own file: the planted one has none
    monkeypatch.setattr(config, "load", lambda *a, **k: found)
    monkeypatch.setattr(brief, "render", lambda *a, **k: "brief\n")


def test_a_checker_brief_removes_the_writer_s_hook_from_its_folder(plant, configured, tmp_path):
    out = tmp_path / "session"
    _brief(plant, "writer", out)
    assert (out / ".claude" / "settings.json").is_file()
    lines = _brief(plant, "checker", out)
    assert not (out / ".claude" / "settings.json").exists()
    assert (out / "LAUNCH.txt").read_text() == lines[-1].removeprefix("LAUNCH checker ") + "\n"


@pytest.mark.parametrize("text", ['{"permissions": {"allow": []}}', "not json", '{"hooks": {"Stop": []}}'])
def test_a_checker_brief_keeps_a_settings_file_that_is_not_the_writer_s(plant, configured, tmp_path, text):
    out = tmp_path / "session"
    (out / ".claude").mkdir(parents=True)
    (out / ".claude" / "settings.json").write_text(text)
    _brief(plant, "checker", out)
    assert (out / ".claude" / "settings.json").read_text() == text


def test_the_folder_record_holds_the_three_keys_and_leaves_no_temporary_file(tmp_path):
    run_dir, folder = tmp_path / "run", tmp_path / "folder"
    run_dir.mkdir()
    folder.mkdir()
    state = {"returns": 1, "ended": None, "refused": {"PF-FORM": ["q07"]}}
    writercheck.record(run_dir, folder, state)
    assert json.loads((folder / writercheck.NAME).read_text()) == state
    assert json.loads((run_dir / writercheck.NAME).read_text()) == state
    assert [p.name for p in folder.iterdir()] == [writercheck.NAME]


def test_a_folder_record_that_cannot_be_written_leaves_the_run_record_and_no_litter(tmp_path):
    run_dir, folder = tmp_path / "run", tmp_path / "folder"
    run_dir.mkdir()
    (folder / writercheck.NAME).mkdir(parents=True)
    writercheck.record(run_dir, folder, {"returns": 0, "ended": "pass", "refused": {}})
    assert json.loads((run_dir / writercheck.NAME).read_text())["ended"] == "pass"
    assert [p.name for p in folder.iterdir()] == [writercheck.NAME]

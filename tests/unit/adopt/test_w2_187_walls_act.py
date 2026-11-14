"""W2-187 I11 (S11): A9's ACT package adds the repository's weekly cron line as text for its owner's operator; nothing is
installed and no cron table is read or written."""
from __future__ import annotations

import subprocess
from pathlib import Path

from gov.adopt import memory_sets

GOV_OS = Path(memory_sets.__file__).resolve().parents[3]
BRIEFS = GOV_OS / memory_sets.BRIEFS
AUDIT = "memory-audit-20261113"


def act_text(out, sets, **kw):
    made = memory_sets.variants(BRIEFS, {}, [])
    act = memory_sets.walls_act(out, sets_root=str(sets), audit=AUDIT, made=made, blind=["x/**"], **kw)
    return (act / "ACT.md").read_text()


def test_the_act_holds_the_cron_line_with_the_repositorys_path_as_step_6(tmp_path):
    sets, repo = tmp_path / "sets", tmp_path / "adopted"
    text = act_text(tmp_path / "out", sets, repo=repo)
    step = [x for x in text.splitlines() if x.startswith("6. ")]
    assert step == [
        "6. Install the weekly memory audit's cron line for this repository (Mondays 21:00; never installed by adoption): "
        f"`0 21 * * 1 GOV_MEMAUDIT_SETS_ROOT={sets} {GOV_OS}/governance/project/orchestration/tools/memaudit_cron.sh "
        f"--repo {repo}`"]
    assert [x[:2] for x in text.splitlines() if x[:1].isdigit()] == ["1.", "2.", "3.", "4.", "5.", "6."]


def test_the_repository_defaults_to_the_git_top_level_of_the_output_folder(tmp_path):
    repo = tmp_path / "adopted"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    text = act_text(repo / "governance" / "adoption", tmp_path / "sets")
    assert f"--repo {repo.resolve()}`" in text


def test_nothing_is_installed_and_no_cron_table_is_read_or_written(tmp_path, monkeypatch):
    calls = []
    real = subprocess.run
    monkeypatch.setattr(subprocess, "run", lambda argv, *a, **k: (calls.append(list(argv)), real(argv, *a, **k))[1])
    act_text(tmp_path / "out", tmp_path / "sets", repo=tmp_path / "adopted")
    assert not [c for c in calls if "cron" in " ".join(map(str, c))]
    assert not (tmp_path / "sets").exists()
    assert "crontab" not in Path(memory_sets.__file__).read_text().replace("no cron table", "")

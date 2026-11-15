"""W2-187 I11 (S11): A9's ACT package adds the repository's weekly cron line as text for its owner's operator; nothing is
installed and no cron table is read or written."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from gov.adopt import memory_sets

GOV_OS = Path(memory_sets.__file__).resolve().parents[3]
BRIEFS = GOV_OS / memory_sets.BRIEFS
AUDIT = "memory-audit-20261113"
# I13's sentence for step 6, word for word (the CTO, DEC-1052, DEC-1182 (2)); spelled here, never read from the module
PUSH_SENTENCE = ('The cycle runs the audit and measure, then one gitleaks scan, then `git push` only on a clean scan; '
                 'declare the push with `GOV_MEMAUDIT_PUSH="<remote> <branch>"` on this line; leave it out for no push.')


def act_text(out, sets, **kw):
    made = memory_sets.variants(BRIEFS, {}, [])
    act = memory_sets.walls_act(out, sets_root=str(sets), audit=AUDIT, made=made, blind=["x/**"], **kw)
    return (act / "ACT.md").read_text()


def _which(found):
    """A stand-in for ``shutil.which`` that answers ``found`` for ``gitleaks`` (never the machine's own PATH)."""
    return lambda name, *a, **k: found if name == "gitleaks" else None


def test_the_act_holds_the_cron_line_with_the_repositorys_path_as_step_6(tmp_path, monkeypatch):
    sets, repo = tmp_path / "sets", tmp_path / "adopted"
    monkeypatch.setattr(memory_sets.shutil, "which", _which("/opt/planted/bin/gitleaks"))
    text = act_text(tmp_path / "out", sets, repo=repo)
    step = [x for x in text.splitlines() if x.startswith("6. ")]
    assert step == [
        "6. Install the weekly memory audit's cron line for this repository (Mondays 21:00; never installed by adoption): "
        f"`0 21 * * 1 GOV_MEMAUDIT_SETS_ROOT={sets} GOV_MEMAUDIT_GITLEAKS=/opt/planted/bin/gitleaks "
        f"{GOV_OS}/governance/project/orchestration/tools/memaudit_cron.sh --repo {repo}` " + PUSH_SENTENCE]
    assert [x[:2] for x in text.splitlines() if x[:1].isdigit()] == ["1.", "2.", "3.", "4.", "5.", "6."]


def test_step_6_names_the_scanner_found_when_a9_runs_because_crons_path_lacks_it(tmp_path, monkeypatch):
    """R1 (review round 1): cron's PATH lacks ``~/.local/bin``, so the line names the scanner's absolute path."""
    monkeypatch.setattr(memory_sets.shutil, "which", _which("/home/someone/.local/bin/gitleaks"))
    step = next(x for x in act_text(tmp_path / "out", tmp_path / "sets", repo=tmp_path / "a").splitlines()
                if x.startswith("6. "))
    line = step.split("`")[1]
    assert line.index("GOV_MEMAUDIT_GITLEAKS=/home/someone/.local/bin/gitleaks ") < line.index("memaudit_cron.sh")
    assert step.count("GOV_MEMAUDIT_GITLEAKS=") == 1


def test_with_no_scanner_on_path_step_6_holds_the_placeholder_for_the_operator(tmp_path, monkeypatch):
    """Revised to run 8b's item 24 (DEC-893, DEC-1156 (7)): with no gitleaks on the PATH, step 6 holds no placeholder
    and no unfilled ``<...>`` slot; it names ``GITLEAKS_MISSING`` instead (the name kept: other records cite it)."""
    monkeypatch.setattr(memory_sets.shutil, "which", _which(None))
    text = act_text(tmp_path / "out", tmp_path / "sets", repo=tmp_path / "a")
    step = "\n".join(text[text.index("\n6. ") + 1:].split("\n7. ")[0].splitlines())
    assert "GITLEAKS_MISSING" in step
    assert "<path to gitleaks>" not in text
    assert not re.search(r"<[^<>\n]*>", step)
    assert "0 21 * * 1" not in step  # no cron line is given without the scanner


def test_a_relative_answer_of_which_is_written_as_an_absolute_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(memory_sets.shutil, "which", _which("bin/gitleaks"))
    step = next(x for x in act_text(tmp_path / "out", tmp_path / "sets", repo=tmp_path / "a").splitlines()
                if x.startswith("6. "))
    assert f" GOV_MEMAUDIT_GITLEAKS={tmp_path}/bin/gitleaks " in step


def test_step_6_names_the_cycles_order_and_how_the_owner_declares_the_push_and_installs_nothing(tmp_path):
    text = act_text(tmp_path / "out", tmp_path / "sets", repo=tmp_path / "adopted")
    step = next(x for x in text.splitlines() if x.startswith("6. "))
    assert step.endswith(PUSH_SENTENCE) and step.count("GOV_MEMAUDIT_PUSH") == 1
    assert text.index("audit and measure") < text.index("gitleaks scan") < text.index("`git push` only on a clean scan")
    assert "GOV_MEMAUDIT_PUSH=" not in text.replace(PUSH_SENTENCE, "")  # nothing declares a push for the owner


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

"""Fix F9 (audit N-14; DEC-1210, DEC-1233, EMERGENCY-2 5.2): no hit@5 floor and no hard-blocking kit check on hit@k.

"hit@5 I DON'T CARE if it's even 10%": hit@k is a reported diagnostic only, never a floor, a target or a verdict.
For W1-21's retrieval-regression check this means:

- ``python3 -m gov.retrieval.retrieve_check`` still prints ``hit@5: <figure>`` but never exits 1 because of it, and
  prints no threshold beside it;
- ``retrieve_baseline.yaml`` holds no hit@k key (``forbidden_citations`` stays);
- no check of the kit that runs ``retrieve_check`` is a ``hard-block``, and none of its text says the dev query set
  "meets its recorded hit@5 baseline";
- what is not hit@k is as before: a forbidden-citation count over the baseline, and "unmeasured", still exit 1.

Everything runs through public interfaces: the check's command in a project root, the kit's check files, the
baseline file. The dev tiers are planted in ``tmp_path`` (one tier ``a-dev`` of two small files and a query set); the
embedder is an address nothing listens on, so retrieval is lexical only and no network is used; the secrets scan is
switched off by the project's own switch (DEC-1045) so the case needs no gitleaks.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
CHECK_MODULE = "gov.retrieval.retrieve_check"
BASELINE = SRC / "gov" / "retrieval" / "retrieve_baseline.yaml"
KIT_CHECK_FOLDERS = ("template/governance/kernel/checks", "governance/kernel/checks", "governance/project/checks")
PATH_MAP_REL = "governance/project/path-map.yaml"
SECRETS_SWITCH = "governance/project/secrets.yaml"
TIMEOUT_S = 900

FILES = {
    "docs/lantern.md": "# Lantern\n\nThe juniper lantern protocol keeps the harbour lit at night.\n",
    "docs/garden.md": "# Garden\n\nNothing about harbours here, only gardens and tomatoes.\n",
}


def _git(root: Path, *args: str) -> None:
    env = {"PATH": "/usr/bin:/bin", "HOME": str(root.parent), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {args} failed: {done.stderr}"


def _repository(root: Path, files: dict) -> None:
    root.mkdir(parents=True)
    _git(root, "init", "-q")
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "planted")


def _check(tmp_path: Path, queries: list, tiers: bool = True):
    """Run the check in a planted project over planted dev tiers; ``queries`` are the query set's entries."""
    base = tmp_path / "run"
    (base / "home").mkdir(parents=True)
    project = base / "project"
    project.mkdir()
    path_map = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    path_map.pop("decision_register", None)
    (project / PATH_MAP_REL).parent.mkdir(parents=True)
    (project / PATH_MAP_REL).write_text(yaml.safe_dump(path_map, sort_keys=False), encoding="utf-8")
    (project / SECRETS_SWITCH).write_text("scan: off\n", encoding="utf-8")
    env = {"PATH": "/usr/bin:/bin", "HOME": str(base / "home"), "XDG_CACHE_HOME": str(base / "cache"),
           "TMPDIR": str(base), "LC_ALL": "C.UTF-8", "PYTHONPATH": str(SRC), "PYTHONDONTWRITEBYTECODE": "1",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "OLLAMA_HOST": "127.0.0.1:9", "GOV_QUERY_OLLAMA_HOST": "127.0.0.1:9",
           "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
    if tiers:
        dev = base / "dev-tiers"
        _repository(dev / "a-dev", FILES)
        (dev / "dev-queryset.yaml").write_text(yaml.safe_dump({"queries": queries}, sort_keys=False), encoding="utf-8")
        env["GOV_DEV_TIERS"] = str(dev)
    done = subprocess.run([sys.executable, "-m", CHECK_MODULE], cwd=str(project), env=env, capture_output=True,
                          text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    return done


def _describe(done) -> str:
    return f"exit: {done.returncode}\nstdout:\n{done.stdout[-3000:]}\nstderr:\n{done.stderr[-3000:]}"


def _query(must_cite, must_not_cite=(), cls="c1"):
    return {"programme": "A", "query": "juniper lantern protocol harbour", "class": cls,
            "gold": {"must_cite": list(must_cite), "must_not_cite": list(must_not_cite)}}


# every gold names a path no tier holds: no query can be a hit, so hit@5 is 0, 80 points under the old baseline
MISSES = [_query(["planted-nowhere/one.md"]), _query(["planted-nowhere/two.md"], cls="c2")]


# ---- failure line: a check red on a low hit@5 --------------------------------------------------------------------


def test_the_check_is_not_red_when_hit_at_5_is_far_below_the_old_baseline(tmp_path):
    done = _check(tmp_path, MISSES)
    out = done.stdout + done.stderr
    assert "Traceback" not in out, _describe(done)
    assert "unmeasured" not in out.lower(), f"the planted tiers were not measured\n{_describe(done)}"
    assert re.search(r"^hit@5: 0\.0\b", done.stdout, re.M), f"the check does not print its hit@5 figure\n{_describe(done)}"
    assert done.returncode == 0, f"a hit@5 of 0.0 with no forbidden citation turns the check red\n{_describe(done)}"


def test_the_hit_at_5_line_is_a_figure_and_carries_no_threshold(tmp_path):
    done = _check(tmp_path, MISSES)
    lines = [line for line in done.stdout.splitlines() if line.startswith("hit@5")]
    assert len(lines) == 1, f"the check prints one hit@5 line\n{_describe(done)}"
    for word in ("baseline", "floor", "target", "threshold", "minimum", "80"):
        assert word not in lines[0].lower(), f"the hit@5 line names a {word!r}: {lines[0]!r}"


def test_a_query_set_that_hits_does_not_change_the_answer(tmp_path):
    """The reported figure is not what the exit follows: a hit and a miss end alike (0)."""
    hits = [_query(["docs/lantern.md"]), _query(["docs/lantern.md"], cls="c2")]
    done = _check(tmp_path, hits)
    assert re.search(r"^hit@5: \d", done.stdout, re.M), f"the check does not print its hit@5 figure\n{_describe(done)}"
    assert done.returncode == 0, _describe(done)


# ---- what is not hit@k stays -------------------------------------------------------------------------------------


def test_forbidden_citations_over_the_baseline_still_fail_the_check(tmp_path):
    """Guard (green on the base): the other baseline is not a hit@k floor and stays. Three queries each cite a path
    their gold forbids, over ``forbidden_citations`` (2)."""
    baseline = yaml.safe_load(BASELINE.read_text(encoding="utf-8"))
    limit = baseline["forbidden_citations"]
    queries = [_query(["planted-nowhere/x.md"], ["docs/lantern.md"], cls=f"c{n}") for n in range(limit + 1)]
    done = _check(tmp_path, queries)
    if "forbidden: 0" in done.stdout:
        pytest.fail(f"lexical retrieval did not cite the planted file: the forbidden count cannot be planted\n{_describe(done)}")
    assert done.returncode == 1, f"forbidden citations over the baseline no longer fail the check\n{_describe(done)}"


def test_where_no_dev_tiers_are_configured_the_check_still_reports_unmeasured_and_exits_1(tmp_path):
    """Guard (green on the base): 'unmeasured' is not a hit@k floor."""
    done = _check(tmp_path, [], tiers=False)
    assert done.returncode == 1, _describe(done)
    assert "unmeasured" in done.stdout.lower(), _describe(done)


# ---- the baseline file and the kit's check -----------------------------------------------------------------------


def test_the_baseline_file_holds_no_hit_at_k_key(tmp_path):
    text = BASELINE.read_text(encoding="utf-8")
    document = yaml.safe_load(text)
    assert isinstance(document, dict), f"{BASELINE} is not a map"
    hit_keys = [key for key in document if re.search(r"hit", str(key), re.I)]
    assert not hit_keys, f"{BASELINE.name} still records a hit@k figure: {hit_keys}"
    assert not re.search(r"^\s*hit@?\w*\s*:", text, re.M | re.I), f"{BASELINE.name} still has a hit@k line"
    assert isinstance(document.get("forbidden_citations"), int), "the forbidden-citation baseline stays"


def _checks_running_retrieve_check():
    found = []
    for folder in KIT_CHECK_FOLDERS:
        for path in sorted((REPO_ROOT / folder).glob("*.y*ml")) if (REPO_ROOT / folder).is_dir() else []:
            text = path.read_text(encoding="utf-8")
            document = yaml.safe_load(text) or {}
            if "retrieve_check" in str(document.get("command", "")):
                found.append((path, document, text))
    return found


def test_no_kit_check_that_runs_retrieve_check_is_a_hard_block():
    """The check is either gone or no longer a hard-block: ``gov close``'s pre-close gate refuses on a red
    hard-block check, so none that can end 1 on a retrieval figure may stay one (the owner, N-14)."""
    for path, document, _ in _checks_running_retrieve_check():
        assert document.get("severity") != "hard-block", (
            f"{path.relative_to(REPO_ROOT)} runs retrieve_check at severity hard-block")


def test_no_kit_check_text_says_the_query_set_meets_a_recorded_hit_at_5_baseline():
    for path, _, text in _checks_running_retrieve_check():
        assert not re.search(r"hit@5\s+and\s+forbidden|recorded\s+hit@5|hit@5\s+(baseline|floor)", text, re.I), (
            f"{path.relative_to(REPO_ROOT)} still describes a hit@5 baseline")


# ---- the source: no floor read, none compared ----------------------------------------------------------------------


def test_retrieve_check_reads_and_compares_no_hit_at_5_threshold():
    text = (SRC / "gov" / "retrieval" / "retrieve_check.py").read_text(encoding="utf-8")
    assert "hit_at_5_threshold" not in text, "retrieve_check.py still holds a hit@5 threshold"
    assert not re.search(r"hit_at_5\s*(<|<=|>|>=)", text), "retrieve_check.py still compares its hit@5 figure"
    assert not re.search(r"""get\(\s*["']hit_at_5["']""", text), "retrieve_check.py still reads a hit@5 baseline"
    assert not re.search(r"hit@5:[^\n]*baseline", text), "retrieve_check.py still prints a hit@5 baseline"

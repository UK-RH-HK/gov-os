"""KPI 5 (P1-LOAD-BALANCE-1 b.6): the retrieval check's dev tiers and their questions are embedded once on the machine;
a later check sends nothing to the embedder.

The check is run as its declaration runs it: ``python3 -m gov.retrieval.retrieve_check`` in a project root, with
``GOV_DEV_TIERS`` naming a folder of two tiers (``a-dev``, ``b-dev``) and a query set. The first case plants a small
such folder of its own; the second, ``local_only``, uses this machine's dev tiers by ``GOV_DEV_TIERS``'s name."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import w2_126_support as S

TIERS = {
    "a-dev": {"docs/lighthouse.md": "# Lighthouse\n\nThe keeper trims the lamp wick every evening at six.\n",
              "docs/ferry.md": "# Ferry\n\nThe ferry crosses the sound twice an hour in summer.\n"},
    "b-dev": {"docs/mill.md": "# Mill\n\nThe miller dresses the millstones each spring with a pick.\n",
              "docs/forge.md": "# Forge\n\nThe smith quenches the blade in brine, not water.\n"},
}
QUERIES = [
    {"id": "Q1", "programme": "A", "class": "default", "query": "when does the keeper trim the lamp wick",
     "gold": {"must_cite": ["docs/lighthouse.md"], "must_not_cite": []}},
    {"id": "Q2", "programme": "A", "class": "default", "query": "how often does the ferry cross the sound",
     "gold": {"must_cite": ["docs/ferry.md"], "must_not_cite": []}},
    {"id": "Q3", "programme": "B", "class": "default", "query": "what does the miller dress in spring",
     "gold": {"must_cite": ["docs/mill.md"], "must_not_cite": []}},
    {"id": "Q4", "programme": "B", "class": "default", "query": "what does the smith quench the blade in",
     "gold": {"must_cite": ["docs/forge.md"], "must_not_cite": []}},
]
CHECK_TIMEOUT_S = 1800.0


def check_project(tmp_path):
    """The project the check runs in: a path map and the gitleaks rules are all the check reads from it."""
    project = tmp_path / "project"
    S.write(project, S.PATH_MAP_REL, S.path_map_text())
    S.write(project, ".gitleaks.toml", (S.REPO_ROOT / S.GITLEAKS_TEMPLATE_REL).read_text(encoding="utf-8"))
    return project


def run_check(box, project, dev_tiers):
    done = subprocess.run([sys.executable, "-m", "gov.retrieval.retrieve_check"], cwd=str(project),
                          env=box.env(GOV_DEV_TIERS=dev_tiers), capture_output=True, text=True,
                          timeout=CHECK_TIMEOUT_S)
    assert "unmeasured" not in done.stdout, f"the check measured nothing:\n{done.stdout}\n{done.stderr[-3000:]}"
    return done


def test_a_later_check_embeds_nothing(box, stand_in, tmp_path):
    tiers = tmp_path / "dev-tiers"
    for name, files in TIERS.items():
        S.plant(tiers / name, corpus=files)
    S.write(tiers, "dev-queryset.yaml", yaml.safe_dump({"queries": QUERIES}, sort_keys=False))
    project = check_project(tmp_path)

    run_check(box, project, tiers)
    for entry in QUERIES:
        assert stand_in.sent_with(entry["query"]), f"the set-up: {entry['id']} was not asked in the first check"
    stand_in.reset()
    run_check(box, project, tiers)
    assert stand_in.texts() == [], f"a later check embedded {len(stand_in.texts())} texts cold"


@pytest.mark.local_only
def test_a_later_check_on_this_machines_dev_tiers_embeds_nothing(box, stand_in, tmp_path):
    tiers = Path(os.environ.get("GOV_DEV_TIERS") or "~/gov-os-workbench/synthetic").expanduser()
    if not (tiers / "dev-queryset.yaml").is_file():
        pytest.skip("no dev tiers on this machine (GOV_DEV_TIERS)")
    project = check_project(tmp_path)
    run_check(box, project, tiers)
    assert stand_in.texts(), "the set-up: the first check embedded nothing"
    stand_in.reset()
    run_check(box, project, tiers)
    assert stand_in.texts() == [], f"a later check embedded {len(stand_in.texts())} texts cold"

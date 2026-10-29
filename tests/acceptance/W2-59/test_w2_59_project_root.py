"""W2-59 KPI success 3 and its failure line: every module that finds the repository from its own install path finds
it from the project root instead, proven from an installed wheel (DEC-835 item 2).

Failure line: "A module that still reads the repository from its install path fails a test."

Today's two such modules, covered by behaviour: the zero-result canary declarations that ``gov doctor`` reads, and
the path map and gitleaks configuration that the retrieval-regression check reads to adopt each dev tier it clones.
The judge is the stand-in pin. At the place a lookup from the installed package's location leads to, decoys are
planted (support ``plant_install_path_decoys``): a canary declaration with a query of its own, a path map and a
gitleaks configuration that cannot be read. The kernel has two layouts (DEC-579): ``template/governance/kernel/``
in this repository, ``governance/kernel/`` in an adopted project.
"""

from __future__ import annotations

import json

import pytest

import w2_59_support as support

PROJECT_CANARY = "w259 project canary {index}"


def _doctor(stand_in, project, tmp_path):
    box = support.make_box(tmp_path / "box", stand_in)
    env = support.base_env(box.home, f"{box.local_bin}:{support.SYSTEM_PATH}")
    done = support.run([box.local_bin / "gov", "doctor", "--json"], cwd=project, env=env)
    parsed = support.envelope(done)
    body = parsed.get("result") or (parsed.get("error") or {}).get("details") or {}
    canaries = body.get("canaries")
    assert isinstance(canaries, dict), f"gov doctor gave no canaries section\n{done.describe()}"
    return done, canaries


@pytest.mark.parametrize("layout", sorted(support.KERNEL_LAYOUTS))
def test_doctor_reads_the_canary_declarations_of_the_project_under_check(layout, stand_in, tmp_path):
    """The project declares one canary query per index; with no index built, each query is run and missed, so the
    answer names the project's query: the declaration was read from the project, not from the install path."""
    kernel = support.KERNEL_LAYOUTS[layout]
    files = {f"{kernel}/canaries/{index}.yaml": f'canaries:\n  - query: "{PROJECT_CANARY.format(index=index)}"\n'
             for index in ("lexical", "semantic")}
    project = support.make_repository(tmp_path / "project", files)
    done, canaries = _doctor(stand_in, project, tmp_path)
    text = json.dumps(canaries)
    assert support.DECOY_CANARY not in text, (
        f"gov doctor read the canary declaration at the installed package's location "
        f"({stand_in.install_path_root / kernel / 'canaries'}): {text}")
    for index in ("lexical", "semantic"):
        answer = (canaries.get("indices") or {}).get(index) or {}
        assert PROJECT_CANARY.format(index=index) in answer.get("misses", []), (
            f"the {index} canary of the project ({kernel}/canaries/{index}.yaml) was not read: {answer}\n"
            f"{done.describe()}")


def test_doctor_does_not_fall_back_to_the_install_path_when_the_project_declares_no_canary(stand_in, tmp_path):
    """A project without canary declarations is answered as such; the declarations at the installed package's
    location are never read in their place."""
    project = support.make_repository(tmp_path / "project")
    done, canaries = _doctor(stand_in, project, tmp_path)
    assert support.DECOY_CANARY not in json.dumps(canaries), (
        f"with no canary declaration in the project, gov doctor read the one at the installed package's location: "
        f"{canaries}\n{done.describe()}")


@pytest.mark.local_only
@pytest.mark.parametrize("layout", sorted(support.RETRIEVAL_PROJECTS))
def test_the_retrieval_check_adopts_each_dev_tier_from_the_project_s_own_files(layout, stand_in, gitleaks, tmp_path):
    """The project holds a valid path map and gitleaks configuration; the ones at the installed package's location
    cannot be read. The check adopts the cloned tier with the project's files, so the tier is indexed and measured
    (it prints its hit@5); read from the install path, nothing is indexed or the check fails on the decoy.
    Today it fails first on its missing baseline (KPI 4), before it reads either file."""
    project = support.make_repository(tmp_path / "project", copies=support.RETRIEVAL_PROJECTS[layout])
    done = support.retrieval_check(stand_in, project, tmp_path, gitleaks)
    output = done.stdout + done.stderr
    assert support.DECOY_MARK not in output and "Traceback" not in output, (
        f"the retrieval-regression check failed reading a file at the installed package's location\n"
        f"{done.describe()}")
    assert "hit@5:" in done.stdout, (
        f"the retrieval-regression check measured nothing: the dev tier was not adopted with the project's path map "
        f"and gitleaks configuration\n{done.describe()}")

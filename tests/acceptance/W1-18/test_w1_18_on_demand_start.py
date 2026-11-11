"""Success 1, under DEC-1065 (1): gov never starts an embedder; a health check only.

Rewrite-Reason: DEC-1065 (1) replaces the on-demand start. The line was "gov starts ollama serve on demand and relies
on the 5-min idle unload; no always-on unit" (DEC-260, DEC-261). DEC-1065 (1) (W2-32's S10): ``ensure_available``
checks health only. With the server not answering, the semantic part is unavailable, named ``EMBEDDER_UNAVAILABLE``,
retrieval answers by keywords, and no ``ollama serve`` is started. What DEC-261 also asked still holds and is kept:
no unit, no keep-alive override, and a running server is never stopped.

The stand-in ``ollama`` stays installed where DEC-260 looks (each of the three places): had gov started it, its
record would show the run.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import w1_18_support as support

UNAVAILABLE = "EMBEDDER_UNAVAILABLE"


def _named_unavailable(result):
    assert result["available"] is False, result
    assert not result.get("started"), f"gov started an embedder (DEC-1065 (1)): {result}"
    assert UNAVAILABLE in json.dumps(result), f"the unavailable embedder is not named {UNAVAILABLE}: {result}"


def test_a_healthy_endpoint_is_used_and_nothing_is_started(stage):
    stage.install_executable("healthy")
    stage.endpoint_up()

    call = stage.call(timeout_s=support.START_DEADLINE_S)

    assert call.result["available"] is True, call.result
    assert call.result["started"] is False, call.result
    assert stage.serve_runs() == [], "the endpoint was already healthy, but `ollama serve` was started"
    asked = [request for request in stage.requests() if request["path"] == support.HEALTH_PATH]
    assert asked, f"the endpoint of OLLAMA_HOST was never asked {support.HEALTH_PATH}"


@pytest.mark.parametrize("place", support.EXECUTABLE_PLACES)
def test_with_the_endpoint_down_nothing_is_started_and_the_embedder_is_named_unavailable(stage, place):
    stage.install_executable("healthy", place=place)

    call = stage.call(timeout_s=support.START_DEADLINE_S)

    assert stage.runs() == [], f"gov ran the executable found through {place}: {stage.runs()} (DEC-1065 (1))"
    _named_unavailable(call.result)


def test_an_unavailable_endpoint_sets_up_no_unit_and_no_keep_alive_override(stage):
    stage.install_executable("healthy")
    before = stage.files(stage.home)

    call = stage.call(timeout_s=support.START_DEADLINE_S)

    _named_unavailable(call.result)
    assert stage.unit_calls() == [], f"a unit command was called: {stage.unit_calls()}"
    assert stage.files(stage.home) == before, "a file was written under HOME (a user unit lives there)"
    assert stage.runs() == [], f"the executable was run: {stage.runs()}"
    overriding = [request for request in stage.requests() if "keep_alive" in request["body"]]
    assert not overriding, f"a request overrides the 5-minute idle unload: {overriding}"


def test_a_running_endpoint_is_used_again_and_never_stopped(stage):
    stage.install_executable("healthy")
    stage.endpoint_up()

    first = stage.call(timeout_s=support.START_DEADLINE_S)
    second = stage.call(timeout_s=support.START_DEADLINE_S)

    for call in (first, second):
        assert call.result["available"] is True and call.result["started"] is False, call.result
    assert stage.runs() == [], f"gov ran the executable although the server answered: {stage.runs()}"
    assert stage.endpoint_answers(), "the running server was stopped (DEC-261)"


# ---- the server not answering: a retrieval answers by keywords ----

NOTE = "# Harbour\n\nThe harbour master publishes the tide tables every Monday at dawn.\n"
QUESTION = "When does the harbour master publish the tide tables?"
RETRIEVE = """\
import json, sys
from gov.retrieval.retrieve import retrieve
bundle = retrieve(sys.argv[1], sys.argv[2])
print(json.dumps({"semantic": bundle["facets"]["semantic"], "paths": [item["path"] for item in bundle["evidence"]]}))
"""


def _plant(project):
    """A git repository with one embedded note, the template's path map and the secrets scan off (DEC-1045)."""
    document = yaml.safe_load((support.REPO_ROOT / "template/governance/project/path-map.yaml").read_text())
    document.setdefault("namespaces", {})["docs"] = {
        "paths": ["docs/**"], "memory_class": "governance", "sensitivity": "internal",
        "permitted_roles": ["engineer", "independent-test-designer", "independent-auditor", "orchestrator",
                            "product-spec", "research"],
        "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": "embedded",
        "provenance": "written by the W1-18 tests", "deletion_rebuild": "authoritative; restored from git only"}
    files = {"docs/harbour.md": NOTE, ".gitignore": ".gov-runtime/\n",
             "governance/project/path-map.yaml": yaml.safe_dump(document, sort_keys=False),
             "governance/project/secrets.yaml": "scan: off\n"}
    for rel, text in files.items():
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(text, encoding="utf-8")
    env = {"PATH": "/usr/bin:/bin", "HOME": str(project), "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t",
           "GIT_AUTHOR_EMAIL": "t@t.invalid", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the planted note"]):
        subprocess.run(["git", "-C", str(project), *args], check=True, capture_output=True, env=env)


def test_with_the_server_not_answering_a_retrieval_answers_by_keywords_and_starts_nothing(stage):
    stage.install_executable("healthy")
    project = stage.root / "project"
    project.mkdir()
    _plant(project)
    tools = stage.root / "tools"
    tools.mkdir()
    (tools / "git").symlink_to(shutil.which("git"))
    site = stage.root / "site"  # the one sqlite_vec this machine's Python imports (the scratch HOME has no user site)
    site.mkdir()
    spec = importlib.util.find_spec("sqlite_vec")
    if spec is None or not spec.origin:
        pytest.skip("sqlite_vec cannot be imported: no vector store, so the semantic part cannot be judged")
    source = Path(spec.origin).parent if spec.submodule_search_locations else Path(spec.origin)
    (site / source.name).symlink_to(source, target_is_directory=source.is_dir())
    env = {**stage.environment(), "PATH": os.pathsep.join([str(tools), str(stage.bin)]),
           "PYTHONPATH": os.pathsep.join([stage.environment()["PYTHONPATH"], str(site)]),
           "GOV_QUERY_OLLAMA_HOST": stage.host, "GOV_REBUILD_LOCK": str(stage.root / "rebuild.lock")}

    rebuilt = subprocess.run([sys.executable, "-m", "gov.cli.main", "rebuild", "--json"], cwd=project, env=env,
                             capture_output=True, text=True, timeout=support.HANG_LIMIT_S * 4)
    envelope = json.loads(rebuilt.stdout.strip().splitlines()[-1])
    stores = (envelope.get("result") or {}).get("stores") or {}
    assert stores.get("lexical", {}).get("status") == "recreated", f"the keyword index is built: {envelope}"
    assert stores.get("semantic", {}).get("status") != "recreated" and UNAVAILABLE in json.dumps(stores["semantic"]), \
        f"the semantic store is refused, named {UNAVAILABLE}: {stores.get('semantic')}"

    asked = subprocess.run([sys.executable, "-c", RETRIEVE, str(project), QUESTION], cwd=project, env=env,
                           capture_output=True, text=True, timeout=support.HANG_LIMIT_S)
    answer = json.loads(asked.stdout.strip().splitlines()[-1])
    # The rebuild named the embedder unavailable and built no vectors, so the search reports them missing; a search
    # against vectors built earlier names EMBEDDER_UNAVAILABLE (W2-32's S10 cases).
    assert answer["semantic"]["available"] is False and answer["semantic"]["reason"], answer
    assert "docs/harbour.md" in answer["paths"][:5], f"the keyword route answers: {answer['paths']}"
    assert stage.runs() == [], f"gov ran the stand-in ollama: {stage.runs()} (DEC-1065 (1))"

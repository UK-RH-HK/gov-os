"""The workflow and hook files as text (KPI S2, F1; DEC-083, DEC-087, DEC-449) [CAP-39.a].

What a text can show and a run cannot: that the job needs no GPU and no model, that no step's result is thrown
away, that a tool the job installs is a registered tool at its registered version, and that the carrier of the
evidence record is written down where the hooks and the job are.
"""

from __future__ import annotations

import re
import subprocess

import pytest
import yaml

import w1_40_support as support


@pytest.fixture(scope="module")
def workflows():
    try:
        return support.push_workflows()
    except support.Absent as absent:
        pytest.fail(str(absent), pytrace=False)


@pytest.fixture(scope="module")
def hook_config():
    if not support.LEFTHOOK_YML.is_file():
        pytest.fail("lefthook.yml is absent from the repository root", pytrace=False)
    return yaml.safe_load(support.LEFTHOOK_YML.read_text(encoding="utf-8"))


def _text(path):
    return path.read_text(encoding="utf-8")


def _without_comments(text):
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def test_a_workflow_runs_on_every_push(workflows):
    """DEC-075: CI is a visible result on every push, so the push trigger names no branch or path filter."""
    for path, workflow in workflows:
        on = workflow["on"]
        push = on.get("push") if isinstance(on, dict) else None
        assert not push, f"{path.name}: the push trigger is filtered ({push}): some pushes would have no CI result"


def test_the_job_runs_on_a_hosted_runner_without_gpu(workflows):
    for path, workflow in workflows:
        for job_id, job in workflow["jobs"].items():
            runs_on = job.get("runs-on")
            assert isinstance(runs_on, str) and re.fullmatch(r"ubuntu-[\w.]+", runs_on), (
                f"{path.name}: job {job_id} runs on {runs_on!r}, not a GitHub-hosted Ubuntu runner")
            assert "gpu" not in runs_on.lower()


MODEL_WORDS = re.compile(r"ollama|hugging\s*face|\bhf\b|hf_hub|\bgguf\b|nvidia|\bcuda\b|\bgpu\b|self-hosted|"
                         r"sentence-transformers|\btorch\b|embedding model|model pull", re.IGNORECASE)


def test_no_step_downloads_a_model_or_asks_for_a_gpu(workflows):
    """Failure line 1, as far as text shows it: nothing outside a comment names a model tool, a GPU or its drivers."""
    for path, _ in workflows:
        found = MODEL_WORDS.findall(_without_comments(_text(path)))
        assert not found, f"{path.name}: the workflow names {sorted(set(found))}"


def test_no_result_is_thrown_away(workflows):
    """DEC-449: a job or step that may fail without failing the run is a check that was not measured."""
    for path, workflow in workflows:
        for job_id, job in workflow["jobs"].items():
            assert not job.get("continue-on-error"), f"{path.name}: job {job_id} continues on error"
            for step in job.get("steps") or ():
                name = step.get("name") or step.get("uses") or step.get("run")
                assert not step.get("continue-on-error"), f"{path.name}: step {name!r} continues on error"
                run = str(step.get("run", ""))
                assert not re.search(r"\|\|\s*(true|:|exit 0|echo)\b", run), (
                    f"{path.name}: step {name!r} turns a failure into a pass")
                assert not re.search(r"\bset \+e\b", run), f"{path.name}: step {name!r} switches off exit on error"


def test_every_step_runs_a_command_or_a_pinned_action(workflows):
    """A ``uses:`` step names its action at a version; none is taken from a moving branch."""
    for path, workflow in workflows:
        for _, _, step in support.steps_of(workflow):
            assert "run" in step or "uses" in step, f"{path.name}: a step has neither run nor uses: {step}"
            uses = step.get("uses")
            if uses and not uses.startswith("./"):
                _, _, ref = uses.partition("@")
                assert ref and ref not in ("main", "master", "latest", "HEAD"), (
                    f"{path.name}: the action {uses!r} is not pinned to a version")


def test_the_job_names_gitleaks_and_gov_check(workflows):
    """DEC-087: the deterministic checks include ``gov check`` and gitleaks."""
    commands = "\n".join(str(step.get("run", "")) for _, workflow in workflows for _, _, step in support.steps_of(workflow))
    assert re.search(r"\bgitleaks\b", commands), "no run step names gitleaks"
    assert re.search(r"(^|[\s;&|(])gov\s+\w|-m\s+gov\.", commands, re.MULTILINE), "no run step runs gov"


REGISTERED_ONLY = ("gitleaks", "lefthook", "rulesync", "openspec", "codebase-memory-mcp", "check-jsonschema", "uv")


def test_a_tool_the_job_installs_is_registered_at_its_registered_version(workflows):
    """DEC-083, DEC-287: a step that downloads a registered tool names its exact registered version and checks a checksum.

    Whether the workflow may install it at all is the owner's (see the README's package P-4): this case holds
    only that nothing else than the registered release can arrive.
    """
    registry = support.registry()
    for path, workflow in workflows:
        for _, _, step in support.steps_of(workflow):
            if not support.is_download(step):
                continue
            run = str(step["run"])
            for tool in REGISTERED_ONLY:
                if not re.search(rf"\b{re.escape(tool)}\b", run):
                    continue
                version = str(registry[tool]["version"]).lstrip("v")
                assert version in run, (
                    f"{path.name}: a step downloads {tool} without naming its registered version {version}")
                if re.search(r"\b(curl|wget)\b|\bgh\s+release\b", run):
                    assert re.search(r"sha256sum\s+(-c|--check)|shasum\s+-a\s*256\s+(-c|--check)", run), (
                        f"{path.name}: a step downloads {tool} without verifying a checksum")
            assert not re.search(r"\|\s*(ba)?sh\b", run), f"{path.name}: a step pipes a download into a shell"
            assert "latest" not in run, f"{path.name}: a step downloads a 'latest' release"


def test_the_hook_file_has_the_two_hooks_and_drops_no_result(hook_config):
    assert isinstance(hook_config, dict)
    for hook in ("pre-commit", "pre-push"):
        assert hook in hook_config, f"lefthook.yml has no {hook} hook"
    text = _without_comments(_text(support.LEFTHOOK_YML))
    assert not re.search(r"\|\|\s*(true|:|exit 0|echo)\b", text), "lefthook.yml turns a failure into a pass"
    assert not re.search(r"^\s*(skip|only)\s*:", text, re.MULTILINE), (
        "lefthook.yml skips a hook or command on a condition: a check that is skipped is not measured")


def test_the_hooks_carry_no_baseline_and_no_bypass(hook_config, workflows):
    """DEC-467: the baseline is the orchestrator's merge rule for this repository; the hooks and the job are strict."""
    texts = [_without_comments(_text(support.LEFTHOOK_YML))] + [_without_comments(_text(path)) for path, _ in workflows]
    for text in texts:
        assert not re.search(r"baseline|46ec8da3|LEFTHOOK=0|LEFTHOOK_EXCLUDE", text), (
            "a hook or the job names a baseline or a bypass")


def test_the_carrier_of_the_evidence_record_is_documented():
    """KPI S2: "carrier (git note or commit) chosen and documented". The choice is stated beside the hooks or the job.

    The engineer's paths are the hook file, the workflow files and ``src/gov/ci/``: the statement is in one of
    them, names the evidence record, and names the one carrier chosen.
    """
    places = [support.LEFTHOOK_YML, *support.workflow_files()]
    ci_package = support.SRC / "gov" / "ci"
    if ci_package.is_dir():
        places += sorted(ci_package.rglob("*.py")) + sorted(ci_package.rglob("*.md"))
    places = [path for path in places if path.is_file()]
    assert places, "neither lefthook.yml nor a workflow exists"
    stated = [path for path in places
              if re.search(r"evidence record", _text(path), re.IGNORECASE)
              and re.search(r"carrier", _text(path), re.IGNORECASE)
              and re.search(r"git note|\bnotes?\b|\bcommit\b", _text(path), re.IGNORECASE)]
    assert stated, ("no file of the ticket states the carrier of the evidence record (the words 'evidence record', "
                    "'carrier', and the carrier chosen)")


def test_no_lefthook_hook_is_installed_in_this_repository():
    """The worktrees share one hooks folder: activating the hooks here is the owner's step at the Wave 1 exit.

    A guard, green before and after the ticket: it reads the hooks folder and writes nothing.
    """
    done = subprocess.run(["git", "-C", str(support.REPO_ROOT), "rev-parse", "--git-path", "hooks"],
                          capture_output=True, text=True, check=True)
    hooks = (support.REPO_ROOT / done.stdout.strip()).resolve()
    for name in ("pre-commit", "pre-push", "prepare-commit-msg", "commit-msg", "post-checkout"):
        hook = hooks / name
        if hook.is_file():
            assert "lefthook" not in hook.read_text(encoding="utf-8", errors="replace"), (
                f"a lefthook hook is installed in this repository: {hook}")
    configured = subprocess.run(["git", "-C", str(support.REPO_ROOT), "config", "--get", "core.hooksPath"],
                                capture_output=True, text=True).stdout.strip()
    assert "lefthook" not in configured

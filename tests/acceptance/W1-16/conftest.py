"""Fixtures for the W1-16 acceptance tests."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_16_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "local_only: runs the codebase-memory or gitleaks binary, or clones a dev tier (GOV_DEV_TIERS); not for CI")


def _built(make):
    """What ``make`` returns, or a plain failure with its reason when the ticket has not built it yet."""
    reason = None
    try:
        return make()
    except support.Missing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture()
def sandbox():
    """HOME, TMPDIR, a runtime directory and an unrelated working directory, outside any repository."""
    made = support.make_sandbox()
    yield made
    support.remove_sandbox(made)


@pytest.fixture(scope="module")
def module_sandbox():
    """One sandbox for the tests of a file that share an indexed repository: indexing takes seconds."""
    made = support.make_sandbox()
    yield made
    support.remove_sandbox(made)


@pytest.fixture(scope="session")
def session_sandbox():
    made = support.make_sandbox()
    yield made
    support.remove_sandbox(made)


@pytest.fixture(scope="session")
def module():
    """``src/gov/codeintel/``, once the ticket has written it."""
    return _built(support.package_dir)


@pytest.fixture(scope="session")
def cbm():
    """The codebase-memory binary. Nothing is installed by a test: without the binary the test is skipped."""
    found = support.tool()
    if found is None:
        pytest.skip(f"{support.TOOL} is not on PATH on this machine")
    return found


@pytest.fixture(scope="session")
def gitleaks():
    """The gitleaks binary. Nothing is installed by a test: without the binary the test is skipped."""
    found = support.scanner()
    if found is None:
        pytest.skip("gitleaks is not on PATH on this machine")
    return found


@pytest.fixture()
def config(request):
    """The gitleaks configuration file named by the test's parameter: ``repository`` or ``template``."""
    return support.config_path(request.param)


# --------------------------------------------------------------------------
# The dev tiers: one clone per tier, indexed, asked, renamed, indexed again and asked again
# --------------------------------------------------------------------------

@dataclass
class TierRun:
    tier: str
    repo: support.Repo
    spec: dict
    answers: dict = field(default_factory=dict)   # phase -> {(function, argument or None): result}

    def answer(self, phase, function, argument=None):
        return self.answers[phase][(function, argument)]

    def name(self, phase, symbol):
        """The name the symbol has in ``phase``."""
        return support.renamed(symbol, self.spec["renames"]) if phase == "after" else symbol

    def pairs(self, phase, expected):
        """Expected ``(path, name)`` pairs with the names they have in ``phase``."""
        return [(path, self.name(phase, name)) for path, name in expected]


def _calls(spec, renames):
    calls = [("index", [])]
    for entry in spec["symbols"]:
        symbol = support.renamed(entry["symbol"], renames)
        calls += [("callers", [symbol]), ("impact", [symbol])]
    for entry in spec["definitions"]:
        calls.append(("definitions", [support.renamed(entry["symbol"], renames)]))
    for entry in spec["references"]:
        calls.append(("references", [support.renamed(entry["symbol"], renames)]))
    calls.append(("dead_code", []))
    if renames:   # the old names, asked after the rename
        for old in renames:
            calls += [("definitions", [old]), ("callers", [old])]
    return calls


def _asked(root, calls, sandbox):
    run = support.codeintel(root, calls, sandbox)
    return {(name, args[0] if args else None): result for (name, args), result in zip(run.calls, run.results)}


@pytest.fixture(scope="session")
def tier_runs(module, cbm, session_sandbox, tmp_path_factory):
    """``tier name -> TierRun``, built once per tier and session. One indexing job runs at a time."""
    questions = support.load_questions()["tiers"]
    built = {}

    def get(tier):
        if tier not in built:
            clone = support.clone_tier(tier, tmp_path_factory.mktemp(f"w1-16-{tier}") / "tier")
            if clone is None:
                pytest.skip(f"no dev tier at {support.DEV_TIERS / tier} (GOV_DEV_TIERS)")
            spec = questions[tier]
            repo = support.Repo(clone, fresh=False).commit("adopt")
            run = TierRun(tier, repo, spec)
            run.answers["before"] = _asked(repo.root, _calls(spec, {}), session_sandbox)
            for old, new in spec["renames"].items():
                assert support.rename_symbol(repo, old, new), f"{tier}: nothing to rename for {old}"
            repo.commit("rename")
            run.answers["after"] = _asked(repo.root, _calls(spec, spec["renames"]), session_sandbox)
            built[tier] = run
        return built[tier]

    return get

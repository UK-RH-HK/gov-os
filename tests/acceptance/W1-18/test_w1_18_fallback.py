"""Success 2 and Failure 2: the degraded result, its facet state and its warning (DEC-257).

"When Ollama is unavailable retrieval degrades to FTS-only with a warning and the facet state recorded" and
"Semantic results are silently omitted without a warning". The result names facet ``semantic`` and state
``FACET_UNAVAILABLE``; the warning names Ollama, says results are FTS-only, and is written once to standard
error. No file is written.
"""

from __future__ import annotations

import re

import pytest

import w1_18_support as support

FTS_ONLY = re.compile(r"fts[- ]only", re.IGNORECASE)


def no_executable(stage):
    """Nothing in GOV_OLLAMA_BIN, on PATH or under HOME."""


def never_healthy(stage):
    """An executable whose ``serve`` runs and never answers."""
    stage.install_executable("never")


def assert_degraded(result):
    assert result["available"] is False, result
    assert result["facet"] == support.FACET, result
    assert result["state"] == support.FACET_UNAVAILABLE, result
    warning = result["warning"]
    assert isinstance(warning, str) and warning.strip(), f"the degraded result carries no warning: {result}"
    assert "ollama" in warning.lower(), f"the warning does not name Ollama: {warning!r}"
    assert FTS_ONLY.search(warning), f"the warning does not say results are FTS-only: {warning!r}"


def test_without_an_executable_the_result_is_fts_only_with_the_facet_state(stage):
    call = stage.call()

    assert stage.runs() == []
    assert_degraded(call.result)


def test_a_daemon_that_never_becomes_healthy_gives_the_same_degraded_result(stage):
    never_healthy(stage)

    call = stage.call()

    assert len(stage.serve_runs()) == 1, "`ollama serve` was not tried once before degrading"
    assert_degraded(call.result)


@pytest.mark.parametrize("unavailable", [no_executable, never_healthy], ids=["no-executable", "never-healthy"])
def test_a_degraded_result_is_never_silent(stage, unavailable):
    unavailable(stage)

    call = stage.call()

    assert_degraded(call.result)
    written = call.stderr.count(call.warning)
    assert written == 1, (
        f"the warning is written to standard error {written} times, not once (DEC-257):\n{call.stderr[-1000:]}")


def test_degrading_writes_no_file(stage):
    before = stage.files()

    call = stage.call()

    assert_degraded(call.result)
    assert stage.files() == before, "the degraded call wrote a file under HOME, the working directory or TMPDIR"

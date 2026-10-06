"""S2: --brief delivers a file path plus a summary <= 2.5k tokens [CAP-15.g].

Red reason: ``gov.context`` does not exist (``src/gov/context/`` is not built).
"""

from __future__ import annotations

from pathlib import Path

import w1_24_support as S


def test_brief_delivers_a_file_path_and_a_summary(api, project):
    """The brief result is a dict with a ``path`` (a string) and a ``summary`` (a string)."""
    result = api.context(project, S.TK_BRIEF, brief=True)
    assert isinstance(result, dict), f"the brief result is not a map: {type(result).__name__}"
    assert isinstance(result.get("path"), str) and result["path"], "the brief result has no path"
    assert isinstance(result.get("summary"), str) and result["summary"], "the brief result has no summary"


def test_the_brief_file_is_under_gov_runtime_scratch(api, project):
    """The brief file is written under ``.gov-runtime/scratch/`` (the only area a worker may write to)."""
    result = api.context(project, S.TK_BRIEF, brief=True)
    path = result["path"]
    scratch = str(Path(project) / S.SCRATCH_REL)
    assert path.startswith(scratch) or S.SCRATCH_REL in path, \
        f"the brief path is not under {S.SCRATCH_REL}: {path}"
    assert Path(path).is_file(), f"the brief file does not exist: {path}"


def test_the_brief_summary_is_at_most_2500_tokens(api, project):
    """The summary is at most ~2.5k tokens (CAP-15.g)."""
    result = api.context(project, S.TK_BRIEF, brief=True)
    summary = result["summary"]
    count = S.tokens(summary)
    assert count <= S.BRIEF_LIMIT, f"the brief summary is {count} tokens, above the limit of {S.BRIEF_LIMIT}"

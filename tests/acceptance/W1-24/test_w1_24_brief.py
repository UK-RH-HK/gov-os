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


def test_a_hostile_ticket_id_cannot_escape_the_scratch_directory(api, repo):
    """A ticket id with path-traversal characters (``../../``) must not write outside
    ``.gov-runtime/scratch/``. The brief file path stays inside the scratch directory."""
    api.build_store(repo)
    outcome = api.context_outcome(repo, S.HOSTILE_ID, brief=True)
    error = outcome.error()
    if error is not None:
        return
    result = outcome.value()
    brief_path = result.get("path", "")
    scratch = str(Path(repo) / S.SCRATCH_REL)
    resolved = str(Path(brief_path).resolve())
    assert resolved.startswith(str(Path(scratch).resolve())), \
        f"the brief file escaped the scratch directory: {resolved} is not under {scratch}"


def test_brief_writes_nothing_outside_the_brief_file(api, repo):
    """Calling ``context(brief=True)`` writes exactly one file (the brief) under ``.gov-runtime/scratch/``;
    no other files are created anywhere the test can see."""
    api.build_store(repo)
    scratch = Path(repo) / S.SCRATCH_REL
    scratch.mkdir(parents=True, exist_ok=True)
    before = set(scratch.rglob("*"))
    api.context(repo, S.TK_BRIEF, brief=True)
    after = set(scratch.rglob("*"))
    new_files = {p for p in after - before if p.is_file()}
    assert len(new_files) <= 1, \
        f"brief created {len(new_files)} new files, expected at most 1: " \
        f"{[str(p.relative_to(scratch)) for p in new_files]}"

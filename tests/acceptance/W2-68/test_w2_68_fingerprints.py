"""Two fingerprints (DEC-889 items 2 and 4; DEC-883 item 4): the code fingerprint governs the store and the code
index; changed record files refresh their chunks incrementally; a lexical index whose record files differ is never
fresh; a store built on another code fingerprint is not accepted. The path map counts as code (DEC-880, DEC-899).

The project: ticket A's work committed, then ``gov rebuild --no-embeddings`` (the record store and the lexical
index of that commit; the embedding endpoint down). Then one commit:

- a record-only commit (A's checkpoint): the lexical index is not fresh until the incremental record load
  (``python3 -m gov.close.batch refresh``) has run; after it, the index is fresh and ``gov close`` accepts the
  store (no ``STORE_STALE``) and closes A;
- a code commit (a file under ``notes/``, as W1-30's case), or a change of the path map that the test map lists as
  record-only: the incremental load refuses (``STORE_CODE_CHANGED``), ``gov close`` refuses ``STORE_STALE``, and the
  lexical index is not fresh.

Red reason (README): ``gov.close.batch`` does not exist (``No module named gov.close.batch``: no envelope). The
assertions of the stale index and of ``STORE_STALE`` hold on the base too: they are the failure KPIs' guards.
"""

import pytest

import w2_68_support as support

PATH_MAP_RECORD_ONLY = {**support.TEST_MAP,
                        "record_only": [*support.TEST_MAP["record_only"], support.PATH_MAP_REL]}


def _built(tmp_path, test_map=support.TEST_MAP):
    sandbox = support.make_sandbox(tmp_path)
    env = support.env_without_endpoint(sandbox)
    project = support.Project(tmp_path / "project", tmp_path / "told", test_map=test_map)
    project.work({support.WIDGET: "# the widget, changed\n"}, ticket=support.A)
    return project, sandbox, env


def test_a_record_only_commit_is_loaded_incrementally_and_the_store_and_the_lexical_index_are_fresh(tmp_path):
    project, sandbox, env = _built(tmp_path)
    support.rebuild(project, sandbox, env)
    fresh = support.lexical_check(project, env)
    assert fresh.returncode == 0, f"the lexical index is not fresh right after the rebuild\n{fresh.describe()}"
    project.ready(sandbox, ticket=support.A)  # the checkpoint: a record-only commit
    checkpoint = [rel for rel in support.close_support.git(project.root, "show", "--name-only", "--format=",
                                                            "HEAD").split() if rel]

    stale = support.lexical_check(project, env)
    assert stale.returncode != 0, ("the lexical index is fresh although a record file changed (a lexical index "
                                   f"whose record files differ is never fresh)\n{stale.describe()}")
    assert any(rel in stale.text() for rel in checkpoint), \
        f"the freshness check does not name the changed record file {checkpoint}\n{stale.describe()}"

    support.refresh(project, env).ok()

    after = support.lexical_check(project, env)
    assert after.returncode == 0, f"the lexical index is not fresh after the incremental record load\n{after.describe()}"
    run = support.close_without_load(project, sandbox, env)
    envelope = run.envelope()
    assert support.STORE_STALE not in run.stdout, \
        f"gov close refused a store built on the same code fingerprint and loaded since\n{run.describe()}"
    assert envelope.get("ok") is True, f"A did not close on the refreshed store\n{run.describe()}"


@pytest.mark.parametrize("commit", ["code-commit", "path-map-change"])
def test_after_a_code_commit_the_store_is_stale_and_the_incremental_load_refuses(commit, tmp_path):
    project, sandbox, env = _built(tmp_path, test_map=PATH_MAP_RECORD_ONLY)
    project.ready(sandbox, ticket=support.A)
    support.rebuild(project, sandbox, env)
    if commit == "code-commit":
        project.code_commit()
    else:
        project.path_map_commit()

    error = support.refresh(project, env).refused()
    assert error.get("code") == support.STORE_CODE_CHANGED, \
        f"the incremental record load did not refuse with {support.STORE_CODE_CHANGED} after a {commit}: {error}"

    run = support.close_without_load(project, sandbox, env)
    envelope = run.envelope()
    assert envelope.get("ok") is False and (envelope.get("error") or {}).get("code") == support.STORE_STALE \
        and run.returncode == support.EXIT_GOV_ERROR, \
        f"gov close accepted a store built on another code fingerprint ({commit})\n{run.describe()}"
    stale = support.lexical_check(project, env)
    assert stale.returncode != 0, f"the lexical index is fresh after a {commit} it has not indexed\n{stale.describe()}"

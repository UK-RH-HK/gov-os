"""KPI success 1, a program the Gov OS starts that starts git itself (independent review F2, DEC-413 round 1).

The code index starts an external tool, ``codebase-memory-mcp`` (W1-16's README), which runs git in the project,
one of its calls writing git configuration. KPI success 1 reads: every check, test helper and command that runs
git in another folder clears the inherited ``GIT_*`` variables. Here the tool is a recording stand-in first on
``PATH``, and the public command that builds the code index is ``gov rebuild`` (``--no-embeddings``: the record
store, the lexical and the code indexes, no embedding endpoint). The caller's environment carries a planted
``GIT_DIR``, ``GIT_INDEX_FILE`` (a decoy's), ``GIT_TRACE``, ``GIT_TRACE2_EVENT`` and a ``GIT_CONFIG_COUNT`` setting;
every start of the tool receives none of them.

The person's identity and push transport (``GIT_AUTHOR_*``, ``GIT_COMMITTER_*``, ``GIT_SSH*``) are not this case's
concern. The sweep record's row for the tool is in ``test_w2_05_sweep.py``.

**Run outside a launched session.** The code index keeps its tool's daemon files in a folder of its own under
``/tmp`` (W1-16, DEC-338), which a launched session cannot write: there ``gov rebuild`` reports the code index
not recreated and starts no tool, and the case fails with that reason (README).
"""

from __future__ import annotations

import w2_05_support as support


def _plants(tmp_path, decoy_repo):
    traces = tmp_path / "traces"
    traces.mkdir()
    return dict(support.planted(decoy_repo),
                GIT_TRACE=str(traces / "git_trace"), GIT_TRACE2_EVENT=str(traces / "git_trace2_event"),
                GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="w2-05.planted", GIT_CONFIG_VALUE_0="yes")


def test_the_code_index_tool_started_by_gov_rebuild_gets_no_inherited_git_variable(tmp_path, box, decoy):
    project = support.code_index_project(tmp_path / "project")
    record = tmp_path / "tool-starts"
    stand_in = support.recording_stand_in(tmp_path / "stand-in", support.CODE_INDEX_TOOL, record)
    plants = _plants(tmp_path, decoy[0])
    env = box.env(**plants)
    env["PATH"] = f"{stand_in}:{env['PATH']}"

    done = box.run(["gov", "rebuild", "--no-embeddings", "--json"], cwd=project, env=env)

    starts = support.recorded_starts(record)
    assert starts, (f"gov rebuild started no {support.CODE_INDEX_TOOL} (the stand-in first on PATH); the case "
                    f"needs the code index built:\n{support.said(done)}")
    reached = [(start["argv"][1:], sorted(set(start["env"]) & set(plants)))
               for start in starts if set(start["env"]) & set(plants)]
    assert not reached, (
        f"{len(reached)} of the {len(starts)} start(s) of {support.CODE_INDEX_TOOL} by gov rebuild received the "
        f"caller's GIT_* variables (KPI success 1: a program that starts git in the project): {reached[:4]}")

"""Sixth batch: one question of the code graph starts the tool's daemon at most once (DEC-561) [CAP-12].

A case added after implementation, reason "owner decision":

- **DEC-561.** The time of the code-index cases is the start of the external tool. Answering one question that
  needs the code graph (the callers of a symbol) starts the tool's daemon at most once: the tool's own daemon log,
  in the home of the repository, holds a line for every start of a daemon. The answer is what it was. The UI
  stays off for that question (DEC-362): the log holds no line that says a daemon served it, and the tool, asked
  in that home, says the setting is ``false``. That nothing listened on the UI port during an answer is held by
  ``test_w1_16_ui_off.py``, for every call of the wrapper.

How the wrapper asks the tool is not held: no case looks at a command line or counts processes.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w1_16_support as support

pytestmark = pytest.mark.local_only

HELPER, ENTRY = "once_helper", "once_entry"
FILES = {
    "app/once.py": f"def {HELPER}(value):\n    return value + 1\n\n\n"
                   f"def {ENTRY}(value):\n    return {HELPER}(value)\n",
    "README.md": "# Once\n\nA small repository.\n",
}


def test_one_question_of_the_code_graph_starts_the_daemon_at_most_once(module, cbm, sandbox, tmp_path):
    """``callers(root, name)`` in a process of its own, on a repository indexed before."""
    repo = support.Repo(tmp_path / "once")
    for rel, text in FILES.items():
        repo.write(rel, text)
    repo.commit("first")
    home = Path(support.one(repo.root, "home", [], sandbox))
    support.codeintel(repo.root, [("index", [])], sandbox)
    # The daemon of the index is not the question's: its end is waited for, three seconds at most.
    support.wait_for_daemon_end(home)
    before = support.daemon_log(home)
    assert before and support.daemon_starts(before) >= 1, \
        f"the premise does not hold: the daemon log of {home} holds no line of a daemon's start after " \
        f"index(root), so starts cannot be counted there:\n{(before or '')[-2000:]}"

    run = support.codeintel(repo.root, [("callers", [HELPER])], sandbox)

    assert support.entries(run.results[0], f"callers({HELPER})", repo.root) == [("app/once.py", ENTRY)], \
        f"the answer changed: the callers of {HELPER} are {ENTRY} alone\n{run.describe()}"
    after = support.daemon_log(home)
    assert after is not None and after.startswith(before), \
        "the premise does not hold: the daemon log was not added to by the question (it was written anew), so " \
        f"starts cannot be counted there:\n{(after or '')[-2000:]}"
    started = support.daemon_starts(after) - support.daemon_starts(before)
    assert started <= 1, \
        f"callers(root, name) started the tool's daemon {started} times; one question of the code graph starts " \
        f"it at most once:\n{after[len(before):][-3000:]}"
    assert support.ui_served(home) == 0, \
        f"a daemon of the question or of the index served the UI:\n{after[-2000:]}"
    said = support.ui_setting(home, sandbox)
    assert said == "false", f"after the question the tool says {support.UI_SETTING} = {said} in the home"

"""S5: where the open items come from is the project's configuration, never a file name in the code. The default is the
dispatcher's ready list (``gov plan --root <root> --ready <file>``, batch 1 as unblocked; an item's id is the ticket id, the
second column); a project may name a file and a reader (``lines``, or ``module.path:function`` called with the item file's
absolute path and returning ``[{id, title, state}]``, state one of open, owner, job, closed). F3 (a name of this repository
in the code) is the last case seen from the failure side. Sources: DEC-1110 (1), DEC-1088.
"""

import re
from pathlib import Path

import pytest

import w2_159_support as support
from w2_159_support import assert_blocks, assert_no_block, ids_named

UNBLOCKED = {"DAEO-u101", "DAEO-u102"}


def test_s5_the_dispatcher_is_the_default_source_and_its_batch_1_is_named(w):
    w.cfg(standby_max_age_h=2)  # no `items` key: the default source
    w.fake_gov(["DAEO-u101", "DAEO-u102"], ["DAEO-u105", "DAEO-u106"])
    result = w.run("idle")
    assert_blocks(result, "(the dispatcher's batch 1 holds two tickets, nothing runs)")
    assert ids_named(result.reason) == UNBLOCKED, f"each ticket of batch 1 and none of batch 2 is named:\n{result}"


def test_s5_the_dispatcher_source_runs_gov_plan_with_root_and_ready(w):
    w.cfg(items={"source": "dispatcher"})
    w.fake_gov(["DAEO-u101"])
    assert_blocks(w.run("idle"))
    argv = w.fake_gov_argv()
    assert argv[0] == "plan", f"the plan is run: {argv}"
    assert "--root" in argv and Path(argv[argv.index("--root") + 1]).resolve() == w.root.resolve(), \
        f"with the project's root: {argv}"
    assert "--ready" in argv and argv[argv.index("--ready") + 1], f"with a file to write the ready list to: {argv}"


def test_s5_a_plan_with_nothing_in_batch_1_leaves_no_unblocked_item(w):
    w.cfg(items={"source": "dispatcher"})
    w.fake_gov([])
    result = w.run("idle")
    assert_no_block(result, "(an empty batch 1: nothing unblocked)")


def test_s5_a_file_source_with_the_lines_reader_names_the_same_items(w):
    w.items_lines("# open items\n\n"
                  "DAEO-u101 READY to start\n"
                  "DAEO-u102 NOT STARTED\n"
                  "DAEO-u103 WAIT owner decides\n"
                  "DAEO-u105 WAIT running job\n"
                  "DAEO-u104 DONE\n"
                  "DAEO-u106 CLOSED\n")
    result = w.run("idle")
    assert_blocks(result, "(a file source, reader lines)")
    assert ids_named(result.reason) == UNBLOCKED, f"the unblocked ids, and no waiting or closed one:\n{result}"


def test_s5_the_lines_reader_with_every_item_waiting_or_closed_leaves_none_unblocked(w):
    w.items_lines("DAEO-u103 WAIT owner decides\nDAEO-u105 WAIT running job\nDAEO-u104 DONE\nDAEO-u106 CLOSED\n")
    assert_no_block(w.run("idle"), "(nothing unblocked)")


def test_s5_a_file_source_with_a_module_reader_names_the_same_items(w):
    got = w.module_reader([
        {"id": "DAEO-u101", "title": "first open item", "state": "open"},
        {"id": "DAEO-u102", "title": "second open item", "state": "open"},
        {"id": "DAEO-u103", "title": "waits on the owner", "state": "owner"},
        {"id": "DAEO-u105", "title": "waits on a job", "state": "job"},
        {"id": "DAEO-u104", "title": "closed", "state": "closed"},
    ])
    result = w.run("idle")
    assert_blocks(result, "(a file source, reader module.path:function)")
    assert ids_named(result.reason) == UNBLOCKED, f"the unblocked ids, and no waiting or closed one:\n{result}"
    called = got.read_text(encoding="utf-8").split()
    assert called, "the reader function was called"
    assert Path(called[0]).is_absolute() and Path(called[0]).resolve() == (w.root / "items" / "open.json").resolve(), \
        f"the reader is called with the item file's absolute path: {called}"


def test_s5_a_module_reader_with_only_owner_waits_and_closed_items_leaves_none_unblocked(w):
    w.module_reader([{"id": "DAEO-u103", "title": "t", "state": "owner"},
                     {"id": "DAEO-u104", "title": "t", "state": "closed"}])
    assert_no_block(w.run("idle"), "(nothing unblocked)")


def test_s5_the_file_sources_path_is_relative_to_the_root(w):
    w.items_lines("DAEO-u101 READY\nDAEO-u102 READY\n", rel="deep/er/open-items.txt")
    result = w.run("idle")
    assert_blocks(result, "(the item file is at a configured path under the root)")
    assert ids_named(result.reason) == UNBLOCKED


# --- F3: nothing of this repository in the code ----------------------------------------------------------------------------

FORBIDDEN_TEXT = ["DECIDED-NOT-DONE", "cto-session", "cto-standby", "inbox_wait", "stop_idle_check", "stop_waiter_check",
                  "orchestration/tools", "orchestrator/tools", "/home/", "Dynamic-Agentic", "gov-os-worktrees",
                  "gov-os-runs"]
FORBIDDEN_PATTERNS = [(r"\bcto-", "a cto- file name"), (r"W2-\d+", "a W2-<digits> ticket id"),
                      (r"DAEO-[0-9a-z]{4}", "a DAEO-<4 chars> ticket id")]


def _sources():
    assert support.SESSION_WATCH_SRC.is_dir(), f"{support.SESSION_WATCH_SRC} does not exist: the check is not built"
    files = [p for p in sorted(support.SESSION_WATCH_SRC.rglob("*"))
             if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")]
    assert any(p.suffix == ".py" for p in files), f"{support.SESSION_WATCH_SRC} holds no module"
    return files


def test_s5_the_code_names_nothing_of_this_repository():
    found = []
    for path in _sources():
        text = path.read_text(encoding="utf-8", errors="replace")
        for name in FORBIDDEN_TEXT:
            if name in text:
                found.append(f"{path.relative_to(support.SRC)}: {name}")
        for pattern, what in FORBIDDEN_PATTERNS:
            for m in re.finditer(pattern, text):
                found.append(f"{path.relative_to(support.SRC)}: {what}: {m.group(0)}")
    assert not found, "src/gov/session_watch names this repository's files, folders or tickets:\n" + "\n".join(found)

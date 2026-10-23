"""W2-69, added after implementation from the review (DEC-136), behaviour 3: a judgement of a store by its raw bytes
is never reused, and a brief lock is waited out.

KPI 5, success: "... the reuse of a clean result keyed on the store's hash
(DEC-853) stays, and a finding is never reused [DEC-853, DEC-290]." DEC-853: "A
changed store is always scanned in full. A finding is never reused." Failure: "a
scan that cannot finish passing as clean."

Each store holds a token in a value that is not whole in its raw bytes:

- ``a-token-across-a-page-and-its-overflow-page``: a github-pat shape in a long
  value, across the end of the value's part on its table's page and the start of
  its first overflow page (the 4-byte page number between them in the raw bytes);
- ``a-token-value-after-a-word-byte-of-its-header``: the project's digit token, 19
  characters, stored as a value on its own; its record's header gives a text of 19
  bytes the serial type 51, the byte ``3``, which stands right before it, so in the
  raw bytes the token begins inside a word.

Run 1: another process holds the store locked for the whole run, so the check
judges it by its raw bytes, as the first batch requires (what run 1 decides is not
asked). Run 2: the lock released and nothing else changed; the check reads the
values and finds the token: a clean result of run 1's raw-bytes judgement is never
reused in place of reading the values. Today run 2 reuses run 1's clean result and
exits 0.

A lock held only briefly (released one second after the check starts) is waited
out: the store is judged by its values in that same run and the token is found.
Today the check meets the lock, judges the raw bytes and exits 0 before the lock
is released.

The first batch's cases on a store locked for the whole run stay as they are.
"""

from __future__ import annotations

import sqlite3
import subprocess
import threading
import time

import pytest

import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME
STORES = ("a-token-across-a-page-and-its-overflow-page", "a-token-value-after-a-word-byte-of-its-header")
BRIEF_S = 1.0


def _overflow_store(path, seed):
    """A value of 24,000 characters whose token crosses the end of its part on the table's page."""
    token = support.ghp_token(seed)
    content = support.tagged("lines", 24_000)
    support.long_value_store(path, bytes(content).decode("ascii"))
    runs = support._runs(path.read_bytes(), bytes(content))
    assert len(runs) > 1, "premise: the value goes on in overflow pages"
    edge = runs[0][1] + runs[0][2]          # where the value's part on its table's page ends
    placed = support.place(content, edge - len(token) // 2, token.encode())
    path.unlink()
    support.long_value_store(path, bytes(placed).decode("ascii"))
    return token


def _header_byte_store(path, seed):
    """The project's digit token alone as a value: 19 characters, serial type 2 * 19 + 13 = 51, the byte ``3``."""
    token = "sk" + "_" + "7" + support.chars(f"hdr-{seed}", 15)
    assert len(token) == 19 and chr(2 * len(token) + 13) == "3"
    support.sqlite_store(path, ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                         [("INSERT INTO notes (body) VALUES (?)", (token,))])
    assert ("3" + token).encode() in path.read_bytes(), "premise: the byte 3 of the record's header stands before it"
    return token


def _build(project, store, seed):
    rel = f"{R}/{store}.db"
    path = project / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    token = (_overflow_store if store.startswith("a-token-across") else _header_byte_store)(path, seed)
    raw = path.read_bytes()
    assert support.held_by_a_value(path, token), "premise: a value holds the token"
    for name, config in support.rule_sets().items():
        expected = "github-pat" if store.startswith("a-token-across") else "gov-token-digit"
        if name == "extended" or expected.startswith("gov-"):
            assert expected in support.gitleaks_finds(f" {token} \n", config), f"premise: the token alone ({name})"
        assert support.gitleaks_finds(b"\n" + raw + b"\n" + raw.replace(b"\0", b""), config) == [], (
            f"premise: the store's raw bytes (and without their zero bytes) hold no whole token ({name})")
    return rel, token


def _hold(path):
    holder = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
    holder.execute("BEGIN EXCLUSIVE")
    probe = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=0.2)
    try:
        with pytest.raises(sqlite3.OperationalError):
            probe.execute("SELECT count(*) FROM notes").fetchone()
    finally:
        probe.close()
    return holder


def _release(holder):
    holder.execute("ROLLBACK")
    holder.close()


@pytest.mark.parametrize("store", STORES)
def test_a_clean_result_of_a_raw_bytes_judgement_is_never_reused_once_the_values_can_be_read(sandbox, project, store):
    rel, token = _build(project, store, f"reuse-{store}")
    path = project / rel
    digest = support.sha256_file(path)
    holder = _hold(path)
    try:
        first = support.run_check(sandbox, project)
    finally:
        _release(holder)
    assert first.returncode is not None, f"run 1: the check did not end within its declared limit\n{first.describe()}"
    assert token not in first.stdout + first.stderr, "run 1: the check printed the token"
    assert support.sha256_file(path) == digest, "premise: the store's bytes are unchanged by the lock"
    second = support.run_check(sandbox, project)
    assert second.returncode is not None, f"run 2: the check did not end within its limit\n{second.describe()}"
    assert token not in second.stdout + second.stderr, "run 2: the check printed the token"
    assert second.returncode == support.FINDING_EXIT and second.names(rel), (
        f"run 2, the lock released and nothing else changed: the check did not find the token a value of {rel} "
        f"holds (run 1 judged the store by its raw bytes, where the token is not whole; run 1: exit code "
        f"{first.returncode}). A clean result of a raw-bytes judgement was reused in place of reading the values\n"
        f"{second.describe()}")


@pytest.mark.parametrize("store", STORES)
def test_a_lock_held_briefly_is_waited_out_and_the_store_judged_by_its_values(sandbox, project, store):
    rel, token = _build(project, store, f"brief-{store}")
    path = project / rel
    holder = _hold(path)
    released = threading.Event()
    timer = threading.Timer(BRIEF_S, lambda: (_release(holder), released.set()))
    began = time.monotonic()
    proc = subprocess.Popen(support.check_command(), shell=True, cwd=str(project),
                            env=support.base_environment(sandbox), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, start_new_session=True)
    timer.start()
    try:
        stdout, stderr = proc.communicate(timeout=support.declared_limit_s())
        code = proc.returncode
    except subprocess.TimeoutExpired:
        support._kill_group(proc)
        stdout, stderr = proc.communicate()
        code = None
    finally:
        timer.join()
        support._kill_group(proc)
    run = support.CheckRun(code, stdout, stderr, time.monotonic() - began)
    assert released.is_set(), "premise: the lock was released"
    assert run.returncode is not None, f"the check did not end within its declared limit\n{run.describe()}"
    assert token not in run.stdout + run.stderr, "the check printed the token"
    assert run.returncode == support.FINDING_EXIT and run.names(rel), (
        f"another process held {rel} for {BRIEF_S} s after the check started, then released it: the check did not "
        f"wait the lock out and judge the store by its values, which hold a token (exit code {run.returncode} after "
        f"{run.seconds:.1f} s)\n{run.describe()}")

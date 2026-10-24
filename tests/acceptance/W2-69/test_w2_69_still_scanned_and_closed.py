"""W2-69 (K5): every file scanned today is still scanned, with every rule set; an unfinished scan fails closed;
DEC-853's reuse of a clean result stays, and a finding is never reused.

Success: "Every file under .gov-runtime/ the check scans today is still scanned,
with every rule set; a scan that cannot finish still fails closed; the reuse of a
clean result keyed on the store's hash (DEC-853) stays, and a finding is never
reused [DEC-853, DEC-290]."

Failure: "A store or file the check scanned before and no longer scans; a scan
that cannot finish passing as clean."

What gitleaks is given is seen through the stand-in on PATH: a store is "scanned"
when each of its marker words was given to gitleaks under every rule set of the run
(the rule sets the run's fresh file was scanned with; the kernel's rules extend
gitleaks' defaults, so there are two). The design adds (DEC-897 item 1): "a SQLite
file that cannot be opened or read is judged by its raw bytes, never passed as
clean undecided" — today's check raises on such a file and names nothing.
"""

from __future__ import annotations

import codecs
import itertools
import os
import sqlite3
import sys
from pathlib import Path

import pytest

import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME
FAULT = support.marker("faultword")
_RUNS = itertools.count(1)


def _fresh(project):
    word = support.marker(f"fresh{next(_RUNS)}x{os.getpid()}")
    support.write(project / R / "scratch" / "fresh.txt", f"fresh {word} for this run only\n")
    return word


def _scan(sandbox, project, stand_in, words, **fault):
    fresh = _fresh(project)
    run = support.run_with_stand_in(sandbox, project, stand_in, markers=[*words, fresh], **fault)
    return run, run.given(fresh)


def _text(word):
    return f"{support.prose(300, 'a')} {word} {support.prose(300, 'b')}"


def _sqlite(project, rel, word):
    support.sqlite_store(project / rel, ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                         [("INSERT INTO notes (body) VALUES (?)", (_text(word),))])


# Each kind of file the check scans today, with a marker word only these tests write: (relative path, builder).
def _kinds(sandbox, project):
    held = []
    kinds = {}

    def add(name, rel, build):
        word = support.marker(f"kind{name}")
        build(rel, word)
        kinds[name] = (rel, word)

    add("plain", f"{R}/notes.txt", lambda rel, w: support.write(project / rel, _text(w)))
    add("nested", f"{R}/codeintel/files/docs/page.md", lambda rel, w: support.write(project / rel, _text(w)))
    add("zerobytes", f"{R}/cache/blob.bin",
        lambda rel, w: support.write(project / rel, b"\0\1" + _text(w).encode() + b"\0"))
    add("utf16file", f"{R}/notes-utf16.txt",
        lambda rel, w: support.write(project / rel, codecs.BOM_UTF16_LE + _text(w).encode("utf-16-le")))
    add("json", f"{R}/state.json", lambda rel, w: support.write(project / rel, f'{{"note": "{w}"}}\n'))
    add("sqlitevalue", f"{R}/store.db", lambda rel, w: _sqlite(project, rel, w))
    add("sqliteblob", f"{R}/blob.db", lambda rel, w: support.blob_store(project / rel, _text(w).encode()))
    add("sqliteutf16blob", f"{R}/blob16.db",
        lambda rel, w: support.blob_store(project / rel, _text(w).encode("utf-16-le")))
    add("utf16store", f"{R}/store16.db", lambda rel, w: support.long_value_store(project / rel, _text(w),
                                                                                 encoding="UTF-16le"))
    add("fts", f"{R}/lexical.db", lambda rel, w: support.fts_store(project / rel, _text(w)))
    add("schema", f"{R}/schema.db", lambda rel, w: support.sqlite_store(
        project / rel, ["CREATE TABLE notes (id INTEGER PRIMARY KEY)", f"CREATE VIEW v AS SELECT '{w}' AS label"]))
    add("freed", f"{R}/freed.db", lambda rel, w: support.freed_store(project / rel, "a-freeblock", w))

    def wal(rel, word):
        path = project / rel
        connection = sqlite3.connect(path, isolation_level=None)
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA wal_autocheckpoint = 0")
        connection.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)")
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        connection.execute("INSERT INTO notes (body) VALUES (?)", (_text(word),))
        held.append(connection)

    add("wal", f"{R}/wal.db", wal)

    def linked(rel, word):   # a linked folder elsewhere is followed (W1-15's B4)
        shared = sandbox.elsewhere / "shared-store"
        support.write(shared / "chunk.md", _text(word))
        (project / rel).symlink_to(shared, target_is_directory=True)

    add("linkedfolder", f"{R}/linked", linked)
    support.write(project / R / "empty.txt", b"")
    return kinds, held


def test_every_file_the_check_scans_today_is_still_scanned_with_every_rule_set(sandbox, project, stand_in):
    kinds, held = _kinds(sandbox, project)
    try:
        run, rule_sets = _scan(sandbox, project, stand_in, [word for _rel, word in kinds.values()])
    finally:
        for connection in held:
            connection.close()
    assert run.returncode == 0, f"the files hold no secret and the check is not green\n{run.describe()}"
    assert len(rule_sets) >= 2, (
        f"the run's fresh file was scanned with {len(rule_sets)} rule set(s); the kernel's rules extend gitleaks' "
        f"defaults with rules of their own, so there are two (DEC-347)\n{run.describe()}")
    missing = {name: sorted(rule_sets - run.given(word)) for name, (_rel, word) in kinds.items()
               if not run.given(word) >= rule_sets}
    assert not missing, (
        f"files the check scans today were not given to gitleaks under every rule set of the run: "
        f"{ {name: f'{kinds[name][0]}: missing {len(sets)} of {len(rule_sets)}' for name, sets in missing.items()} }"
        f"\n{run.describe()}")


# --------------------------------------------------------------------------
# A SQLite file that cannot be opened or read is judged by its raw bytes
# --------------------------------------------------------------------------

DAMAGE = ("garbage-after-the-header", "a-damaged-page", "truncated")


def _unreadable(path):
    try:
        support.live_values(path)
    except sqlite3.DatabaseError:
        return True
    return False


@pytest.mark.parametrize("how", DAMAGE)
def test_a_sqlite_file_that_cannot_be_read_and_holds_a_token_is_red_naming_it(sandbox, project, how):
    secret = support.ghp_token(f"damaged-{how}")
    rel = f"{R}/damaged-{how}.db"
    support.corrupt_sqlite(project / rel, secret, how)
    data = (project / rel).read_bytes()
    assert data.startswith(support.SQLITE_HEADER) and secret.encode() in data, "premise: a SQLite header and the token"
    assert _unreadable(project / rel), f"premise: SQLite cannot read the file ({how})"
    run = support.run_check(sandbox, project)
    assert run.returncode is not None, f"{how}: the check did not end within its declared limit\n{run.describe()}"
    assert secret not in run.stdout + run.stderr, f"{how}: the check printed the secret"
    assert run.returncode != 0, f"{how}: a SQLite file it cannot read holds a token and the check is green"
    assert run.names(rel), (
        f"{how}: the check did not judge the file it cannot read by its raw bytes, which hold a token: it names no "
        f"{rel} (exit code {run.returncode})\n{run.describe()}")


@pytest.mark.parametrize("how", DAMAGE)
def test_a_sqlite_file_that_cannot_be_read_and_holds_no_token_is_scanned_by_its_raw_bytes(sandbox, project,
                                                                                            stand_in, how):
    word = support.marker(f"damaged{how}")
    rel = f"{R}/damaged-{how}.db"
    support.corrupt_sqlite(project / rel, word, how)
    assert _unreadable(project / rel), f"premise: SQLite cannot read the file ({how})"
    run, rule_sets = _scan(sandbox, project, stand_in, [word])
    assert run.returncode == 0, (
        f"{how}: a SQLite file the check cannot read, whose raw bytes hold no token, is not judged clean by them\n"
        f"{run.describe()}")
    assert run.given(word) >= rule_sets and len(rule_sets) >= 2, (
        f"{how}: the file's raw bytes were not given to gitleaks under every rule set\n{run.describe()}")


@pytest.mark.parametrize("holds", ("a-token", "no-token"))
def test_a_store_another_process_holds_locked_is_judged_by_its_raw_bytes(sandbox, project, holds):
    secret = support.ghp_token("locked") if holds == "a-token" else support.marker("lockedclean")
    rel = f"{R}/locked.db"
    _sqlite(project, rel, secret)
    holder = sqlite3.connect(project / rel, isolation_level=None)
    holder.execute("BEGIN EXCLUSIVE")
    try:
        probe = sqlite3.connect(f"file:{project / rel}?mode=ro", uri=True, timeout=0.2)
        with pytest.raises(sqlite3.OperationalError):
            probe.execute("SELECT count(*) FROM notes").fetchone()
        probe.close()
        run = support.run_check(sandbox, project)
    finally:
        holder.execute("ROLLBACK")
        holder.close()
    assert run.returncode is not None, f"the check did not end within its declared limit\n{run.describe()}"
    if holds == "a-token":
        assert secret not in run.stdout + run.stderr, "the check printed the secret"
        assert run.returncode != 0 and run.names(rel), (
            f"a store held locked by another process holds a token in its bytes; the check must judge it by its raw "
            f"bytes and name it (exit code {run.returncode})\n{run.describe()}")
    else:
        assert run.returncode == 0, (
            f"a store held locked by another process, whose bytes hold no token, is not judged clean by its raw "
            f"bytes\n{run.describe()}")


# --------------------------------------------------------------------------
# A scan that cannot finish fails closed
# --------------------------------------------------------------------------

FAULTS = [("hang", "a-sqlite-value"), ("signal", "a-sqlite-value"), ("exit-code", "a-sqlite-value"),
          ("signal", "freed-space"), ("exit-code", "freed-space"), ("signal", "a-plain-file"),
          ("exit-code", "a-plain-file")]


@pytest.mark.parametrize("fault,where", FAULTS, ids=[f"{f}-{w}" for f, w in FAULTS])
def test_a_scan_that_cannot_finish_fails_closed(sandbox, project, stand_in, fault, where):
    rel = {"a-sqlite-value": f"{R}/store.db", "freed-space": f"{R}/freed.db", "a-plain-file": f"{R}/notes.txt"}[where]
    if where == "a-sqlite-value":
        _sqlite(project, rel, FAULT)
    elif where == "freed-space":
        support.freed_store(project / rel, "a-freeblock", FAULT)
        assert not support.held_by_a_value(project / rel, FAULT), "premise: the word is in freed space only"
    else:
        support.write(project / rel, _text(FAULT))
    run, _sets = _scan(sandbox, project, stand_in, [FAULT], fault=fault, fault_marker=FAULT)
    assert any(call.get("fault") for call in run.calls), (
        f"premise: gitleaks was given the word of {where} and failed on it ({fault})\n{run.describe()}")
    assert run.returncode is not None, (
        f"gitleaks {fault} on {where}: the check did not end within its declared limit\n{run.describe()}")
    assert run.returncode != 0, f"gitleaks {fault} on {where}, and the check is green: an unfinished scan passed"
    digest = support.sha256_file(project / rel)
    assert not [line for line in (run.stdout + run.stderr).splitlines() if digest in line], (
        f"an unfinished scan of {rel} was labelled as a reused clean result")
    after, sets = _scan(sandbox, project, stand_in, [FAULT])
    assert after.returncode == 0 and after.given(FAULT) >= sets, (
        f"after the failed run, real gitleaks back: {rel} was not scanned in full (a clean result was recorded "
        f"from the failed run)\n{after.describe()}")


def test_without_gitleaks_the_check_fails_closed(sandbox, project):
    _sqlite(project, f"{R}/store.db", support.marker("nogitleaks"))
    tools = sandbox.elsewhere / "no-gitleaks"
    tools.mkdir()
    env = support.base_environment(sandbox, path=f"{tools}{os.pathsep}{Path(sys.executable).parent}"
                                                 f"{os.pathsep}/usr/bin{os.pathsep}/bin")
    run = support.run_check(sandbox, project, env=env)
    assert run.returncode not in (0, None), f"no gitleaks on PATH and the check is green\n{run.describe()}"


# --------------------------------------------------------------------------
# DEC-853: a clean result reused by the store's hash; a finding never reused
# --------------------------------------------------------------------------

def _reuse_lines(run, rel, digest):
    return [line for line in (run.stdout + run.stderr).splitlines() if rel in line and digest in line]


def test_an_unchanged_sqlite_store_is_reused_and_a_change_in_its_freed_space_is_scanned_again(sandbox, project,
                                                                                               stand_in):
    rel = f"{R}/store.db"
    live, freed = support.marker("reuselive"), support.marker("reusefreed")
    support.sqlite_store(project / rel, ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                         [("INSERT INTO notes (body) VALUES (?)", (_text(live),)),
                          ("INSERT INTO notes (body) VALUES (?)", (_text(freed),)),
                          ("INSERT INTO notes (body) VALUES (?)", (_text("third"),))],
                         secure_delete=False, after=["DELETE FROM notes WHERE id = 2"])
    assert freed.encode() in (project / rel).read_bytes() and not support.held_by_a_value(project / rel, freed)
    first, sets = _scan(sandbox, project, stand_in, [live, freed])
    assert first.returncode == 0 and first.given(live) >= sets and first.given(freed) >= sets, (
        f"run 1: the store's value and its freed space were not both scanned with every rule set\n{first.describe()}")
    digest = support.sha256_file(project / rel)
    second, _ = _scan(sandbox, project, stand_in, [live, freed])
    assert second.returncode == 0 and _reuse_lines(second, rel, digest), (
        f"run 2, the store unchanged: its clean result is not reused with a label naming it and its digest "
        f"(DEC-853)\n{second.describe()}")
    assert not second.given(live) and not second.given(freed), "run 2: the unchanged store was given to gitleaks"
    data = bytearray((project / rel).read_bytes())
    at = data.find(freed.encode())
    data[at + len(freed) - 1] = ord("q") if data[at + len(freed) - 1] != ord("q") else ord("z")
    (project / rel).write_bytes(bytes(data))
    changed = freed[:-1] + chr(data[at + len(freed) - 1])
    third, sets = _scan(sandbox, project, stand_in, [live, changed])
    assert third.returncode == 0 and third.given(live) >= sets and third.given(changed) >= sets, (
        f"run 3, one byte of the freed space changed: the store was not scanned again in full\n{third.describe()}")
    assert not _reuse_lines(third, rel, digest) and not _reuse_lines(third, rel, support.sha256_file(project / rel))


def test_a_finding_in_freed_space_is_never_reused(sandbox, project, stand_in):
    rel = f"{R}/freed.db"
    secret = support.ghp_token("never-reused")
    live = support.marker("neverreusedlive")
    support.sqlite_store(project / rel, ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                         [("INSERT INTO notes (body) VALUES (?)", (_text(live),)),
                          ("INSERT INTO notes (body) VALUES (?)", (_text(secret),)),
                          ("INSERT INTO notes (body) VALUES (?)", (_text("third"),))],
                         secure_delete=False, after=["DELETE FROM notes WHERE id = 2"])
    assert secret.encode() in (project / rel).read_bytes() and not support.held_by_a_value(project / rel, secret)
    digest = support.sha256_file(project / rel)
    for number in (1, 2, 3):
        run, _ = _scan(sandbox, project, stand_in, [live])
        assert secret not in run.stdout + run.stderr, "the check printed the secret"
        assert run.returncode not in (0, None) and run.names(rel), (
            f"run {number}: a token in the freed space of {rel} is not a finding\n{run.describe()}")
        assert run.given(live), f"run {number}: the store was not given to gitleaks: no fresh scan"
        assert not _reuse_lines(run, rel, digest), f"run {number}: a store with a finding was labelled as reused"


OWN_FORMS = ("a-text-value", "freed-space", "a-utf16le-blob", "a-plain-file")


@pytest.mark.parametrize("form", OWN_FORMS)
def test_a_value_only_the_projects_own_rules_find_is_red_in_every_form(sandbox, project, form):
    """DEC-347: the alphabet run in the value is sheltered by gitleaks' global allowlist under ``extend``; only the
    rule set of the project's rules alone finds it, so it is red only if every rule set ran on the form."""
    secret = support.own_only(form)
    sets = support.rule_sets()
    assert support.gitleaks_finds(f" {secret} \n", sets["extended"]) == [], "premise: sheltered under extend"
    assert support.gitleaks_finds(f" {secret} \n", sets["alone"]), "premise: found by the project's rules alone"
    rel = {"a-text-value": f"{R}/store.db", "freed-space": f"{R}/freed.db", "a-utf16le-blob": f"{R}/blob.db",
           "a-plain-file": f"{R}/notes.txt"}[form]
    if form == "a-text-value":
        _sqlite(project, rel, secret)
    elif form == "freed-space":
        support.freed_store(project / rel, "a-freeblock", secret)
    elif form == "a-utf16le-blob":
        support.blob_store(project / rel, _text(secret).encode("utf-16-le"))
    else:
        support.write(project / rel, _text(secret))
    run = support.run_check(sandbox, project)
    assert secret not in run.stdout + run.stderr, "the check printed the secret"
    assert run.returncode not in (0, None) and run.names(rel), (
        f"{form}: a value only the project's rules alone find is not a finding: not every rule set ran on it\n"
        f"{run.describe()}")

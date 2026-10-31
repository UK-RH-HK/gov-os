"""W2-107, round 2: the FULL review's findings, given as behaviours (DEC-136), from the design note's round 2 addendum.

A. The engine's identity also carries the version string gitleaks reports (``gitleaks version``, through the same PATH
   entry), asked only when a cache is in use and at most once a process for each binary. A version that cannot be read
   means no cache for that call.
B. The filter's reading form (the module's ``_FORM``: "the form of the record and of what a scan reads") is in the
   fingerprint.
C. One engine per judgement: the fingerprint is taken before the scan, and a verdict is written only if the gitleaks
   PATH finds is still the same file (path and file status) after it.
D. A cache that can be read but not written (a read-only file or folder, a write lock held elsewhere) still answers the
   current engine's clean verdicts, writes nothing, clears nothing, and never answers a row of another engine.

Every pass that must be a fresh process (as a rebuild is) runs in a child process, as in round 1. The stand-ins here
log each scan call and each version call; they never log content.
"""

from __future__ import annotations

import os
import sqlite3
import stat
import sys
from pathlib import Path

import pytest

import w2_107_support as support
from gov import secrets

pytestmark = support.needs_tools

FILES = {
    "docs/alpha.md": "W2-107: the alpha page, ordinary text.\n",
    "docs/beta.md": "W2-107: the beta page, ordinary text.\n",
}
CANARY_RULE = "gov-canary"  # the kernel's canary rule, which the planted secret matches
OLD_VERSION = "8.0.0-w2-107-release-one"  # what the older release reports; no real gitleaks reports it
LOCKED_EXTRA_S = 120  # as in round 1: how much longer than a pass without a cache a pass may take under a lock


def planted_text():
    return f"The value is {support.planted()} today.\n"


def planted_name():
    return f"docs/{support.planted()}/page.md"


# --------------------------------------------------------------------------
# The stand-ins of round 2
# --------------------------------------------------------------------------

_STANDIN = r'''import json, os, subprocess, sys
# W2-107 round 2 stand-in gitleaks (@TAG@): logs each scan and version call; scans as the real gitleaks does, or as an
# older one that does not know one rule; answers "version" as its version file says; may rename another engine over
# its own place during a scan.
REAL, LOG, TAG, OLD, VERSION = @REAL@, @LOG@, @TAG@, @OLD@, @VERSION@
SELF, STAGED, COUNTER, SWAP_AT = @SELF@, @STAGED@, @COUNTER@, @SWAP_AT@
args = sys.argv[1:]


def log(kind):
    handle = os.open(LOG, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(handle, (kind + " " + TAG + "\n").encode())
    finally:
        os.close(handle)


if args[:1] == ["version"]:
    log("version")
    try:
        with open(VERSION, encoding="utf-8") as handle:
            answer = handle.read().strip()
    except (OSError, TypeError):
        answer = "real"
    if answer == "exit-1":  # a version on standard output, but a failed run
        print("8.0.0-w2-107-unread")
        print("W2-107 stand-in: no version today", file=sys.stderr)
        sys.exit(1)
    if answer == "empty":
        sys.exit(0)
    if answer != "real":
        print(answer)
        sys.exit(0)
    os.execv(REAL, [REAL] + args)
if args[:1] != ["stdin"]:
    os.execv(REAL, [REAL] + args)
log("stdin")
if STAGED and os.path.exists(STAGED):
    handle = os.open(COUNTER, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(handle, b"x")
    finally:
        os.close(handle)
    if os.path.getsize(COUNTER) >= SWAP_AT:
        os.replace(STAGED, SELF)  # another engine lands at this one's place while this scan runs
if not OLD:
    os.execv(REAL, [REAL] + args)
done = subprocess.run([REAL] + args, input=sys.stdin.buffer.read(), capture_output=True)
out, code = done.stdout, done.returncode
try:
    findings = json.loads(out) if code else None
except ValueError:
    findings = None
if isinstance(findings, list):  # the rule this older engine does not know finds nothing
    kept = [each for each in findings if not (isinstance(each, dict) and each.get("RuleID") == OLD)]
    out, code = (json.dumps(kept).encode(), code) if kept else (b"[]", 0)
sys.stdout.buffer.write(out)
sys.stderr.buffer.write(done.stderr)
sys.exit(code)
'''

_SHIM = r'''import os, sys
# W2-107 shim gitleaks: its own bytes never change; it runs whichever release its setting file names, as a version
# manager's shim does, and logs each scan and version call with the release that answered it.
LOG, SETTING, RELEASES = @LOG@, @SETTING@, @RELEASES@
args = sys.argv[1:]
with open(SETTING, encoding="utf-8") as handle:
    release = handle.read().strip()
if args[:1] in (["stdin"], ["version"]):
    handle = os.open(LOG, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(handle, (args[0] + " " + release + "\n").encode())
    finally:
        os.close(handle)
target = RELEASES[release]
os.execv(target, [target] + args)
'''


def script(path, template, **values):
    """``template`` with each ``@NAME@`` replaced by ``repr`` of its value, written at ``path`` as an executable."""
    body = template
    for name, value in values.items():
        body = body.replace(f"@{name}@", repr(value))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!{sys.executable}\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def make_standin(path, log, tag, old=None, version=None, staged=None, counter=None, swap_at=0):
    """A stand-in gitleaks at ``path``. ``old``: the id of a rule it does not know (it finds nothing by it).
    ``version``: a file whose text says how it answers ``version`` (``real``, ``exit-1``, ``empty``, or the string to
    report); absent, the real gitleaks answers. ``staged``: while that file exists, the stand-in counts its scan calls
    in ``counter`` and, at the ``swap_at``-th, renames ``staged`` over its own place before it answers."""
    return script(path, _STANDIN, REAL=support.REAL_GITLEAKS, LOG=str(log), TAG=tag, OLD=old,
                  VERSION=None if version is None else str(version), SELF=str(path),
                  STAGED=None if staged is None else str(staged), COUNTER=None if counter is None else str(counter),
                  SWAP_AT=swap_at)


def engine_at(folder, log):
    """The ``support.Engine`` for the gitleaks in ``folder``: put first on PATH, its scan calls counted in ``log``."""
    return support.Engine(Path(folder), Path(log), Path(folder).parent / f"{Path(folder).name}-fail")


def logged(log, kind, tag=None):
    """How many ``kind`` calls (``stdin`` or ``version``) ``log`` holds, of ``tag`` alone where it is given."""
    log = Path(log)
    if not log.exists():
        return 0
    lines = log.read_text(encoding="utf-8").splitlines()
    return sum(1 for line in lines if (line == f"{kind} {tag}" if tag else line.startswith(f"{kind} ")))


def status(path):
    """The file status that tells one file from another: device, inode, size, change and modification times."""
    found = os.stat(path)
    return found.st_dev, found.st_ino, found.st_size, found.st_ctime_ns, found.st_mtime_ns


def child(root, paths, names, engine, cache, **settings):
    """One pass in a child process with ``engine`` first on PATH; the run and the scan calls ``engine`` had."""
    env = support.child_env(engine, cache, **settings)
    run, calls = support.counted(engine, lambda: support.run_child(root, paths, names, env))
    assert run.gov == secrets.__file__, "the child runs the same gov as this run (DEC-732)"
    return run, calls


def scene(project):
    """Two clean files and one holding the planted secret; a clean name and one holding the secret."""
    rels = support.put(project, FILES)
    secret = support.put(project, {"docs/planted.md": planted_text()})
    return rels, secret, ["docs/an-ordinary-name.md", planted_name()]


def costs(project, engine, rels, secret, names):
    """With no cache, under a gitleaks that knows every rule: what the whole pass costs, what its texts holding the
    secret cost alone, and the whole pass's seconds."""
    run, full = child(project, rels + secret, names, engine, "")
    assert run.error is None and run.indexable == rels and run.names == [False, True], "premise: the verdicts"
    run_alone, findings = child(project, secret, names[1:], engine, "")
    assert run_alone.indexable == [] and run_alone.names == [True], "premise: the planted secret is found"
    assert 1 <= findings < full, "premise: the texts holding the secret cost less than the whole pass"
    return full, findings, run.seconds


# --------------------------------------------------------------------------
# A. The version string is part of the engine's identity
# --------------------------------------------------------------------------

def test_a_gitleaks_upgraded_behind_a_shim_whose_bytes_stay_the_same_forgets_every_verdict(tmp_path, project, cache):
    """The shim's bytes and file status never change; only the release its setting names does. Release one is an older
    gitleaks that does not know the canary rule and reports its own version; release two is the real gitleaks."""
    log = tmp_path / "shim-calls.log"
    release_one = make_standin(tmp_path / "releases/one/gitleaks", tmp_path / "release-one-calls.log", "one",
                               old=CANARY_RULE, version=tmp_path / "release-one-version")
    support.write(tmp_path / "release-one-version", OLD_VERSION)
    setting = support.write(tmp_path / "shim/release", "one")
    shim = script(tmp_path / "shim/gitleaks", _SHIM, LOG=str(log), SETTING=str(setting),
                  RELEASES={"one": str(release_one), "two": support.REAL_GITLEAKS})
    engine = engine_at(shim.parent, log)
    rels, secret, names = scene(project)

    run, one_full = child(project, rels + secret, names, engine, "")
    assert run.error is None and run.indexable == rels + secret and run.names == [False, False], \
        "premise: release one does not know the canary rule: it lets the planted secret through"
    setting.write_text("two", encoding="utf-8")
    two_full, two_findings, _ = costs(project, engine, rels, secret, names)

    shim_bytes, shim_status = shim.read_bytes(), status(shim)
    steps = [("release one", "one", rels + secret, [False, False], one_full, "every text is scanned"),
             ("release one again", "one", rels + secret, [False, False], 0,
              "premise: every verdict is remembered, the planted text's included (this release does not know the rule)"),
             ("release two, in a fresh process", "two", rels, [False, True], two_full,
              "every remembered text is scanned again: the upgrade forgot every verdict"),
             ("release two again", "two", rels, [False, True], two_findings, "release two's clean texts are remembered")]
    for label, release, kept, verdicts, scanned, why in steps:
        setting.write_text(release, encoding="utf-8")
        run, calls = child(project, rels + secret, names, engine, cache)
        assert shim.read_bytes() == shim_bytes and status(shim) == shim_status, \
            f"{label}: premise: the shim's own bytes and file status never change"
        assert run.error is None, f"{label}: the filter raised {run.error}"
        assert run.indexable == kept and run.names == verdicts, \
            f"{label}: the verdicts are those of release {release} (the planted secret is dropped only by release two)"
        assert calls == scanned, f"{label}: {why}"


@pytest.mark.parametrize("unreadable", ["exit-1", "empty"])
def test_a_gitleaks_whose_version_cannot_be_read_scans_every_text_every_time_and_remembers_nothing(
        unreadable, tmp_path, project, cache):
    log, version = tmp_path / "engine-v-calls.log", tmp_path / "engine-v-version"
    make_standin(tmp_path / "engine-v/gitleaks", log, "v", version=version)
    engine = engine_at(tmp_path / "engine-v", log)
    rels, secret, names = scene(project)
    full, findings, _ = costs(project, engine, rels, secret, names)
    steps = [(f"version {unreadable}", unreadable, full), (f"version {unreadable} again", unreadable, full),
             ("a version that can be read", "real", full), ("a version that can be read, again", "real", findings),
             (f"version {unreadable} once more", unreadable, full)]
    for number, (label, answer, scanned) in enumerate(steps):
        version.write_text(answer, encoding="utf-8")
        before = cache.read_bytes() if cache.exists() else None
        asked = logged(log, "version")
        run, calls = child(project, rels + secret, names, engine, cache)
        assert run.error is None and run.indexable == rels and run.names == [False, True], f"{label}: the verdicts"
        assert calls == scanned, f"{label}: {scanned} scan calls"
        assert logged(log, "version") > asked, f"{label}: premise: the filter asked this gitleaks its version"
        if answer != "real" and before is not None:
            assert cache.read_bytes() == before, f"{label}: nothing is written to the cache"


def test_the_version_is_asked_only_when_a_cache_is_used_and_at_most_once_a_process(tmp_path, project, cache):
    """A guard: with no cache (the setting empty, or under pytest with none named) gitleaks is never asked its version,
    so the suites that scan keep their cost; with a cache, it is asked at most once in a process."""
    log = tmp_path / "engine-q-calls.log"
    make_standin(tmp_path / "engine-q/gitleaks", log, "q")
    engine = engine_at(tmp_path / "engine-q", log)
    rels, secret, names = scene(project)
    passes = [("GOV_SECRETS_CACHE empty", support.child_env(engine, "")),
              ("under pytest, no cache named", support.child_env(
                  engine, None, extra={"PYTEST_CURRENT_TEST": "test_w2_107_example (call)"},
                  drop=("GOV_SECRETS_CACHE", "XDG_CACHE_HOME", "GOV_SECRETS_FULL_SCAN")))]
    for label, env in passes:
        asked = logged(log, "version")
        run = support.run_child(project, rels + secret, names, env)
        assert run.error is None and run.indexable == rels and run.names == [False, True], f"{label}: the verdicts"
        assert logged(log, "version") == asked, f"{label}: gitleaks is not asked its version"
    asked = logged(log, "version")
    run = support.run_child(project, rels + secret, names, support.child_env(engine, cache))
    assert run.error is None and run.indexable == rels and run.names == [False, True], "with a cache: the verdicts"
    assert logged(log, "version") - asked <= 1, "with a cache: the version is asked at most once in the process"


# --------------------------------------------------------------------------
# C. One engine per judgement
# --------------------------------------------------------------------------

@pytest.mark.parametrize("then", ["the-new-engine", "the-old-engine-put-back"])
def test_a_gitleaks_replaced_during_a_scan_has_nothing_remembered_for_that_text(
        then, tmp_path, project, engine, cache, per_text):
    """The old engine does not know the canary rule. On its last scan call of the planted text it renames the new
    engine (a different file, which knows every rule) over its own place, as an upgrade landing while a rebuild runs,
    and then answers. Nothing judged across that switch is remembered, under either engine."""
    secret = support.put(project, {"docs/planted.md": planted_text()})
    clean = support.put(project, {"docs/neighbour.md": "W2-107: an ordinary neighbour.\n"})
    kept, findings = support.uncached(engine, lambda: secrets.indexable(project, secret))
    assert kept == [] and findings >= 1, "premise: a gitleaks that knows the rule drops the planted text"

    place, log, staged = tmp_path / "swap/gitleaks", tmp_path / "swap-calls.log", tmp_path / "staged/gitleaks"
    make_standin(place, log, "old", old=CANARY_RULE, staged=staged, counter=tmp_path / "swap-count", swap_at=per_text)
    old_bytes = place.read_bytes()
    at = engine_at(place.parent, log)
    run, calls = child(project, secret, [], at, "")
    assert run.error is None and run.indexable == secret and calls == per_text, \
        "premise: the old engine does not know the rule: it lets the planted text through"

    new_bytes = make_standin(staged, log, "new").read_bytes()
    old_calls = logged(log, "stdin", "old")
    run, _ = child(project, secret, [], at, cache)
    assert run.error is None, f"the switch: the filter raised {run.error}"
    assert not staged.exists() and place.read_bytes() == new_bytes, \
        "premise: the new engine landed at the old one's place during the scan"
    assert logged(log, "stdin", "old") - old_calls == per_text, "premise: the old engine made every scan call of the text"

    if then == "the-new-engine":
        run, calls = child(project, secret + clean, [], at, cache)
        assert run.error is None and run.indexable == clean, \
            "the planted secret, which only the new engine knows, is dropped: the old verdict was not credited to it"
        assert calls == findings + per_text, "the text judged across the switch is scanned again"
        run, calls = child(project, secret + clean, [], at, cache)
        assert run.indexable == clean, "the planted secret is dropped again"
        assert calls == findings, "control: the new engine's clean verdicts are remembered"
    else:
        back = place.parent / ".gitleaks-back"
        back.write_bytes(old_bytes)
        back.chmod(0o755)
        os.replace(back, place)
        run, calls = child(project, secret + clean, [], at, cache)
        assert run.error is None and run.indexable == secret + clean, "the old engine's verdicts"
        assert calls == 2 * per_text, \
            "the text judged across the switch is scanned again: nothing was written for it, not even under the " \
            "engine that judged it"
        run, calls = child(project, secret + clean, [], at, cache)
        assert run.indexable == secret + clean, "the old engine's verdicts again"
        assert calls == 0, "control: with no switch, the old engine's clean verdicts are remembered"


# --------------------------------------------------------------------------
# B. The filter's reading form is part of the fingerprint
# --------------------------------------------------------------------------

def test_a_raised_reading_form_rescans_every_remembered_text(project, engine, cache, per_text, monkeypatch):
    """The reading form is raised as the module raises it: its ``_FORM``, documented on the base as "the form of the
    record and of what a scan reads", set one higher on the module this run imports, between calls in one process."""
    form = getattr(secrets, "_FORM", None)
    assert isinstance(form, int), "the filter's reading form is the module's _FORM, a whole number (the base's convention)"
    rels = support.put(project, FILES)
    name = "docs/an-ordinary-name.md"
    texts = len(rels) + 1
    steps = [("the form as it is", form, texts), ("the form as it is, again", form, 0),
             ("the form raised", form + 1, texts), ("the form raised, again", form + 1, 0),
             ("the form back", form, texts)]
    for label, value, scanned in steps:
        monkeypatch.setattr(secrets, "_FORM", value)
        verdicts, calls = support.counted(
            engine, lambda: (secrets.indexable(project, rels), secrets.path_holds_secret(project, name)))
        assert verdicts == (rels, False), f"{label}: the verdicts are unchanged"
        assert calls == scanned * per_text, f"{label}: {scanned} of {texts} texts scanned"


# --------------------------------------------------------------------------
# D. A cache that can be read but not written still answers
# --------------------------------------------------------------------------

@pytest.mark.parametrize("made_read_only", ["the-file", "its-folder"])
def test_a_read_only_cache_still_answers_the_current_engines_clean_texts_and_writes_nothing(
        made_read_only, tmp_path, project, engine, cache):
    other = support.make_engine(tmp_path / "engine-b", tag="b")
    rels, secret, names = scene(project)
    full, findings, _ = costs(project, engine, rels, secret, names)
    for label, scanned in (("populated", full), ("populated, again", findings)):
        run, calls = child(project, rels + secret, names, engine, cache)
        assert run.error is None and run.indexable == rels, f"{label}: the verdicts are right"
        assert calls == scanned, f"{label}: premise: a cache that can be written answers the clean texts"
    target = cache if made_read_only == "the-file" else cache.parent
    mode = stat.S_IMODE(target.stat().st_mode)
    target.chmod(0o444 if made_read_only == "the-file" else 0o555)
    try:
        if os.access(target, os.W_OK):
            pytest.skip("this user writes where the mode forbids it (root): the case cannot be built")
        snapshot = cache.read_bytes()
        steps = [("engine A, read-only", engine, findings, "the current engine's clean texts are answered, not scanned"),
                 ("engine B, read-only", other, full, "a text remembered under another engine is never answered"),
                 ("engine A again, read-only", engine, findings, "nothing was cleared: the clean texts are answered")]
        for label, first, scanned, why in steps:
            run, calls = child(project, rels + secret, names, first, cache)
            assert run.error is None, f"{label}: the filter raised {run.error}"
            assert run.indexable == rels and run.names == [False, True], f"{label}: the verdicts are right"
            assert calls == scanned, f"{label}: {why}"
            assert cache.read_bytes() == snapshot, f"{label}: nothing is written to the cache"
    finally:
        target.chmod(mode)


def test_a_cache_whose_write_lock_is_held_elsewhere_still_answers_its_clean_texts(
        project, engine, cache, per_text):
    """Another connection holds the write lock (readers may still read) while the filter judges remembered texts, a
    new clean text and the texts holding the secret: the remembered texts are answered, the rest are scanned, and the
    lock is waited out only a short while."""
    rels, secret, names = scene(project)
    full, findings, seconds = costs(project, engine, rels, secret, names)
    for label, scanned in (("populated", full), ("populated, again", findings)):
        run, calls = child(project, rels + secret, names, engine, cache)
        assert run.error is None and run.indexable == rels, f"{label}: the verdicts are right"
        assert calls == scanned, f"{label}: premise: a cache that can be written answers the clean texts"
    fresh = support.put(project, {"docs/fresh.md": "W2-107: a page written while the write lock is held.\n"})
    holder = sqlite3.connect(cache, isolation_level=None)
    try:
        holder.execute("BEGIN IMMEDIATE")  # the write lock: no other connection may write, every one may read
        snapshot = cache.read_bytes()
        run, calls = child(project, rels + secret + fresh, names, engine, cache)
        assert run.error is None, f"the filter raised {run.error} under a held write lock"
        assert run.indexable == rels + fresh and run.names == [False, True], "the verdicts are right"
        assert calls == findings + per_text, \
            "the remembered clean texts are answered; only the new text and the texts holding the secret are scanned"
        assert run.seconds <= seconds + LOCKED_EXTRA_S, "the write lock is waited out only a short while"
        assert cache.read_bytes() == snapshot, "nothing is written while the lock is held elsewhere"
    finally:
        holder.execute("ROLLBACK")
        holder.close()

"""W2-50, the owner's DEC-853: the secrets scan finishes on large stores, reuses a clean result by hash, stays whole.

Success: "The secrets scan finishes. This repository's secrets-indexing scan
finishes on stores of today's size (a 250 MB store.db, a 210 MB code graph): its
time limit grows with the content's size, or a large store is scanned in bounded
chunks each within the limit, and its pool is bounded so that large files are
not starved [DEC-853]."

Success: "A clean scan reused by its hash. A store whose hash has not changed
since its last clean scan is not scanned again; its clean result is reused,
keyed on the store's hash [DEC-853]."

Failure: "The secrets scan stays whole and closed: every file is still scanned
with every rule set; a scan that cannot finish still fails closed; a store
changed by one byte is scanned again in full; a finding is never reused
[DEC-853]."

Working figures, given to the engineer in the same words: a store must be
decided whenever gitleaks reads its input at 1 MB/s or faster; a reused clean
result is labelled in the check's output by a line that names the store's
project-relative path and the SHA-256 hex digest of the store file's bytes it
was keyed on, and a store that is scanned carries no such line.

The check is run as its family runner runs it (its declared ``command`` by
``sh -c`` in a temporary project's root), and once by ``gov check --json``.
What gitleaks is given is seen through the delegating stand-in of
``w2_50_scan_support`` (README, "tests added for the owner's DEC-853").
Planted secrets are built at run time; none stands whole in this file.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import w2_50_scan_support as scan
import w2_50_support as support

pytestmark = pytest.mark.skipif(scan.REAL_GITLEAKS is None,
                                reason="gitleaks is not on PATH: the check cannot run")

STORE_DB = f"{scan.RUNTIME}/store.db"                       # SQLite, as the index's store is
CODE_STORE = f"{scan.RUNTIME}/codeintel/home/code.txt"      # a plain store, deeper in the runtime folder
LARGE = f"{scan.RUNTIME}/store-large.bin"
SMALL_STORE = 64 * 1024 * 16                                # 1 MiB: the plain store of the small cases
FAULT = scan.marker("faultword")


@pytest.fixture()
def env(sandbox):
    """``(project, stand_in)``: the fixture project with the kernel's ``.gitleaks.toml``, and the stand-in."""
    return scan.make_scan_project(sandbox), scan.install_stand_in(sandbox)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def words(rel):
    """The three marker words of one store: at its start, its middle and its end."""
    tag = rel.replace("/", "").replace(".", "").replace("-", "")
    return [scan.marker(f"{tag}start"), scan.marker(f"{tag}middle"), scan.marker(f"{tag}end")]


def plain_store(project, rel, size=SMALL_STORE, extra=None):
    start, middle, end = words(rel)
    placed = {16: start, size // 2: middle, size - 64: end}
    placed.update(extra or {})
    return scan.text_store(project / rel, size, placed)


def db_store(project, rel=STORE_DB, rows=()):
    start, middle, end = words(rel)
    return scan.sqlite_store(project / rel, [start, *rows, middle, end])


def digest(project, rel):
    return scan.sha256_file(project / rel)


def assert_green(run, what):
    assert run.returncode is not None, f"{what}: the check did not finish within its declared limit\n{run.describe()}"
    assert run.returncode == 0, f"{what}: the check is not green\n{run.describe()}"


def assert_red_naming(run, rel, what):
    assert run.returncode is not None, f"{what}: the check did not finish within its declared limit\n{run.describe()}"
    assert run.returncode != 0, f"{what}: the check is green\n{run.describe()}"
    assert run.lines_naming(rel), f"{what}: the check is red but names no {rel}\n{run.describe()}"
    assert scan.SECRET not in run.output and scan.OWN_ONLY not in run.output, f"{what}: the check printed the secret"


def assert_full_scan(run, rel, what):
    """Every marker word of ``rel`` was given to gitleaks under every rule set this run used."""
    scan.assert_stand_in_used(run)
    rule_sets = run.rule_sets()
    for word in words(rel):
        assert run.seen_under(word) >= rule_sets, (
            f"{what}: gitleaks was not given all of {rel}: the word at its "
            f"{['start', 'middle', 'end'][words(rel).index(word)]} was seen under {len(run.seen_under(word))} "
            f"of the run's {len(rule_sets)} rule sets\n{run.describe()}")


def assert_given_again(run, rel, what):
    """``rel``'s content was given to gitleaks in this run: a fresh scan. (A red scan may stop at its first
    finding, so not every rule set need have seen all of it.)"""
    scan.assert_stand_in_used(run)
    assert any(run.given(word) for word in words(rel)), (
        f"{what}: gitleaks was not given {rel}'s content in this run: no fresh scan\n{run.describe()}")


def assert_not_given(run, rel, what):
    scan.assert_stand_in_used(run)
    given = [word for word in words(rel) if run.given(word)]
    assert not given, f"{what}: gitleaks was given {rel}'s content again ({len(given)} of its 3 words)\n{run.describe()}"


def assert_reuse_labelled(run, rel, sha, what):
    assert run.reuse_lines(rel, sha), (
        f"{what}: no line of the check's output labels {rel}'s clean result as reused with the SHA-256 of its "
        f"bytes ({sha})\n{run.describe()}")


def assert_not_labelled(run, rel, *shas):
    for sha in shas:
        assert not run.reuse_lines(rel, sha), (
            f"{rel} was scanned or is red, yet a line names it with a digest of its bytes ({sha}): "
            f"{run.reuse_lines(rel, sha)}\n{run.describe()}")


def _check_entries(data):
    """Every check result in ``gov check --json``'s envelope, wherever the envelope holds its ``checks`` list."""
    if isinstance(data, dict):
        found = [entry for entry in data.get("checks", []) if isinstance(entry, dict)] \
            if isinstance(data.get("checks"), list) else []
        return found + [entry for key, value in data.items() if key != "checks" for entry in _check_entries(value)]
    if isinstance(data, list):
        return [entry for value in data for entry in _check_entries(value)]
    return []


def first_runs(sandbox, project, stand_in, rels):
    """Run 1 (a full scan, green) and run 2 (the same stores unchanged: each reused). Returns their digests."""
    run1 = scan.run_scan(sandbox, project, stand_in, markers=[w for rel in rels for w in words(rel)])
    assert_green(run1, "run 1, clean stores")
    for rel in rels:
        assert_full_scan(run1, rel, "run 1, the first scan")
    shas = {rel: digest(project, rel) for rel in rels}
    run2 = scan.run_scan(sandbox, project, stand_in, markers=[w for rel in rels for w in words(rel)])
    assert_green(run2, "run 2, the same stores unchanged")
    for rel in rels:
        assert_reuse_labelled(run2, rel, shas[rel], "run 2, the same store unchanged")
        assert_not_given(run2, rel, "run 2, the same store unchanged")
    return shas


# --------------------------------------------------------------------------
# Success: the scan finishes on large stores [DEC-853 item 1]
# --------------------------------------------------------------------------

def test_a_large_clean_store_is_decided_green(env, sandbox):
    """160 MiB, read by gitleaks at 2 MB/s (twice the working figure): 84 s a run, past today's fixed 60 s."""
    project, stand_in = env
    start, middle, end = words(LARGE)
    scan.text_store(project / LARGE, scan.LARGE_SIZE,
                    {16: start, scan.LARGE_SIZE // 2 + 4096: middle, scan.LARGE_SIZE - 64: end})
    run = scan.run_scan(sandbox, project, stand_in, markers=words(LARGE), rate=scan.SLOW_RATE)
    assert_green(run, f"a clean store of {scan.LARGE_SIZE} bytes read at {scan.SLOW_RATE} bytes a second")
    assert_full_scan(run, LARGE, "the large store")


def test_a_large_store_with_a_canary_across_its_middle_is_red_naming_it(env, sandbox):
    """The canary stands across the store's exact middle byte, where a split into halves or powers of two falls."""
    project, stand_in = env
    start, middle, end = words(LARGE)
    across = scan.LARGE_SIZE // 2 - (len(scan.SECRET) + 2) // 2
    scan.text_store(project / LARGE, scan.LARGE_SIZE,
                    {16: start, across: scan.SECRET, across + 4096: middle, scan.LARGE_SIZE - 64: end})
    run = scan.run_scan(sandbox, project, stand_in, markers=words(LARGE), rate=scan.SLOW_RATE)
    assert_red_naming(run, LARGE, "a large store with a canary")
    assert any(call.get("code") not in (None, 0) for call in run.calls), (
        f"the check is red, but no gitleaks run over the store finished and reported a finding: red by failure, "
        f"not by a verdict\n{run.describe()}")
    assert_given_again(run, LARGE, "the large store with a canary")


def test_a_large_store_among_many_small_files_is_decided_by_gov_check(env, sandbox):
    """The pool full: 300 small stores beside the large one, every gitleaks run at 2 MB/s; run by ``gov check``."""
    project, stand_in = env
    start, middle, end = words(LARGE)
    scan.text_store(project / LARGE, scan.LARGE_SIZE,
                    {16: start, scan.LARGE_SIZE // 2 + 4096: middle, scan.LARGE_SIZE - 64: end})
    small = scan.marker("smallfile")
    block = scan.filler_block(16 * 1024, seed="small").decode()
    for index in range(300):
        support.write(project / scan.RUNTIME / "packets" / f"DAEO-{index:04d}" / "packet.md",
                      f"{block[:8000]}\n{small}\n{block[8000:]}")
    checks = project / "governance/kernel/checks"
    checks.mkdir(parents=True, exist_ok=True)
    (checks / "secrets-indexing.yaml").write_bytes(support.CHECK_DECLARATION.read_bytes())
    run = scan.run_scan(sandbox, project, stand_in, markers=[*words(LARGE), small], rate=scan.SLOW_RATE,
                        via_gov_check=True)
    assert run.returncode is not None, f"gov check did not finish within the check's declared limit\n{run.describe()}"
    try:
        envelope = json.loads(run.stdout)
    except ValueError:
        raise AssertionError(f"gov check --json gave no JSON\n{run.describe()}") from None
    status = [entry.get("status") for entry in _check_entries(envelope) if entry.get("id") == "secrets-indexing"]
    assert status == ["GREEN"], f"the secrets-indexing check under gov check is {status}, not GREEN\n{run.describe()}"
    assert_full_scan(run, LARGE, "the large store in a full pool")
    assert run.given(small), f"the small stores were not given to gitleaks\n{run.describe()}"


# --------------------------------------------------------------------------
# Success: a clean scan reused by its hash [DEC-853 item 2]
# --------------------------------------------------------------------------

def test_an_unchanged_store_is_not_scanned_again_and_its_reuse_is_labelled(env, sandbox):
    project, stand_in = env
    db_store(project)
    plain_store(project, CODE_STORE)
    shas = first_runs(sandbox, project, stand_in, [STORE_DB, CODE_STORE])
    run3 = scan.run_scan(sandbox, project, stand_in, markers=words(STORE_DB) + words(CODE_STORE))
    assert_green(run3, "run 3, still unchanged")
    for rel in (STORE_DB, CODE_STORE):
        assert_reuse_labelled(run3, rel, shas[rel], "run 3, still unchanged")
        assert_not_given(run3, rel, "run 3, still unchanged")
    assert_not_labelled(run3, scan.FRESH_REL, digest(project, scan.FRESH_REL))


# --------------------------------------------------------------------------
# Failure: a store changed by one byte is scanned again in full [DEC-853 item 2]
# --------------------------------------------------------------------------

@pytest.mark.parametrize("where", ("first-byte", "middle-byte", "last-byte"))
def test_a_store_changed_by_one_byte_is_scanned_again_in_full(env, sandbox, where):
    """One filler byte changed; the store's size and modification time kept."""
    project, stand_in = env
    plain_store(project, CODE_STORE)
    old = first_runs(sandbox, project, stand_in, [CODE_STORE])[CODE_STORE]
    offset = {"first-byte": 0, "middle-byte": SMALL_STORE // 2 + 2048, "last-byte": SMALL_STORE - 2}[where]
    scan.flip_byte_at(project / CODE_STORE, offset)
    new = digest(project, CODE_STORE)
    assert new != old
    run = scan.run_scan(sandbox, project, stand_in, markers=words(CODE_STORE))
    assert_green(run, f"the store changed at its {where}")
    assert_full_scan(run, CODE_STORE, f"the store changed at its {where}")
    assert_not_labelled(run, CODE_STORE, old, new)


@pytest.mark.parametrize("kind", ("default-rule-canary-in-a-sqlite-store", "own-rule-value-in-a-plain-store"))
def test_a_one_byte_change_that_makes_a_secret_appear_is_found(env, sandbox, kind):
    """The own-rule value is found only by the scan with the project's rules alone (DEC-347): every rule set ran."""
    project, stand_in = env
    if kind.startswith("default"):
        rel, near, secret = STORE_DB, scan.NEAR_SECRET, scan.SECRET
        db_store(project, rows=[f"value {near} here"])
    else:
        rel, near, secret = CODE_STORE, scan.NEAR_OWN_ONLY, scan.OWN_ONLY
        plain_store(project, rel, extra={SMALL_STORE // 4: near})
    old = first_runs(sandbox, project, stand_in, [rel])[rel]
    scan.replace_one_byte(project / rel, near, secret)
    run = scan.run_scan(sandbox, project, stand_in, markers=words(rel))
    assert_red_naming(run, rel, f"one byte made a secret appear ({kind})")
    assert_given_again(run, rel, f"one byte made a secret appear ({kind})")
    assert_not_labelled(run, rel, old, digest(project, rel))


# --------------------------------------------------------------------------
# Failure: a finding is never reused [DEC-853 item 2]
# --------------------------------------------------------------------------

def test_a_store_with_a_canary_is_red_from_a_fresh_scan_on_every_run(env, sandbox):
    project, stand_in = env
    db_store(project, rows=[f"value {scan.SECRET} here"])
    sha = digest(project, STORE_DB)
    for number in (1, 2, 3):
        run = scan.run_scan(sandbox, project, stand_in, markers=words(STORE_DB))
        assert_red_naming(run, STORE_DB, f"run {number} over a store with a canary")
        assert_given_again(run, STORE_DB, f"run {number} over a store with a canary")
        assert_not_labelled(run, STORE_DB, sha)


def test_a_clean_store_that_gains_a_canary_is_red_on_the_next_run(env, sandbox):
    project, stand_in = env
    plain_store(project, CODE_STORE)
    old = first_runs(sandbox, project, stand_in, [CODE_STORE])[CODE_STORE]
    with open(project / CODE_STORE, "a", encoding="utf-8") as handle:
        handle.write(f"appended {scan.SECRET} here\n")
    run = scan.run_scan(sandbox, project, stand_in, markers=words(CODE_STORE))
    assert_red_naming(run, CODE_STORE, "a clean store that gained a canary")
    assert_not_labelled(run, CODE_STORE, old, digest(project, CODE_STORE))


# --------------------------------------------------------------------------
# Failure: every file is scanned with every rule set [DEC-853 item 1; DEC-347]
# --------------------------------------------------------------------------

def test_each_store_is_scanned_with_both_rule_sets(env, sandbox):
    """The kernel's ``.gitleaks.toml`` extends gitleaks' defaults with rules of its own: two rule sets."""
    project, stand_in = env
    db_store(project)
    plain_store(project, CODE_STORE)
    run = scan.run_scan(sandbox, project, stand_in, markers=words(STORE_DB) + words(CODE_STORE))
    assert_green(run, "two clean stores")
    assert len(run.rule_sets()) >= 2, (
        f"the check ran gitleaks with {len(run.rule_sets())} rule set(s) on a project whose rules extend the "
        f"defaults with rules of their own\n{run.describe()}")
    for rel in (STORE_DB, CODE_STORE):
        assert_full_scan(run, rel, "each store with both rule sets")


def test_a_store_whose_only_secret_the_projects_own_rules_find_is_red(env, sandbox):
    project, stand_in = env
    plain_store(project, CODE_STORE, extra={SMALL_STORE // 4: scan.OWN_ONLY})
    for number in (1, 2):
        run = scan.run_scan(sandbox, project, stand_in, markers=words(CODE_STORE))
        assert_red_naming(run, CODE_STORE, f"run {number}, a value only the project's own rules find")


@pytest.mark.parametrize("added", ("a-rule-that-finds-a-value-in-the-store", "a-rule-that-finds-nothing-there"))
def test_a_change_of_the_projects_rules_makes_no_earlier_clean_result_count(env, sandbox, added):
    project, stand_in = env
    plain_store(project, CODE_STORE, extra={SMALL_STORE // 4: scan.ADDED_VALUE})
    sha = first_runs(sandbox, project, stand_in, [CODE_STORE])[CODE_STORE]
    rule = scan.ADDED_RULE if added.endswith("store") else scan.ADDED_RULE.replace("5853added", "5853elsewhere")
    with open(project / ".gitleaks.toml", "a", encoding="utf-8") as handle:
        handle.write(rule)
    run = scan.run_scan(sandbox, project, stand_in, markers=words(CODE_STORE))
    assert digest(project, CODE_STORE) == sha, "premise: the store itself is unchanged"
    if added.endswith("store"):
        assert_red_naming(run, CODE_STORE, "the store, unchanged, under a new rule that finds a value in it")
    else:
        assert_green(run, "the store, unchanged, under a new rule that finds nothing in it")
    if added.endswith("store"):
        assert_given_again(run, CODE_STORE, "the store under a new rule that finds a value in it")
    else:
        assert_full_scan(run, CODE_STORE, "the store under a new rule that finds nothing in it")
    assert_not_labelled(run, CODE_STORE, sha)


# --------------------------------------------------------------------------
# Failure: a scan that cannot finish still fails closed [DEC-853 item 1]
# --------------------------------------------------------------------------

@pytest.mark.parametrize("fault", ("hang", "signal", "exit-code"))
def test_a_scan_that_cannot_finish_fails_closed_and_records_nothing(env, sandbox, fault):
    """gitleaks never finishes, is killed by a signal, or exits with a code it does not give, on one store's
    content. The store was clean, then changed by one byte (still clean), so the failed run had to scan it."""
    project, stand_in = env
    db_store(project, rows=[f"the word {FAULT} stands here"])
    run1 = scan.run_scan(sandbox, project, stand_in, markers=words(STORE_DB))
    assert_green(run1, "run 1, a clean store")
    old = digest(project, STORE_DB)
    start = words(STORE_DB)[0]
    scan.replace_one_byte(project / STORE_DB, start, start[:-1] + ("x" if start[-1] != "x" else "y"))
    changed = digest(project, STORE_DB)
    failed = scan.run_scan(sandbox, project, stand_in, markers=words(STORE_DB)[1:], fault=fault, fault_marker=FAULT)
    assert failed.returncode is not None, (
        f"gitleaks {fault}: the check did not end within its declared limit ({scan.declared_limit_s()} s)\n"
        f"{failed.describe()}")
    assert failed.returncode != 0, f"gitleaks {fault} on a store, and the check is green\n{failed.describe()}"
    assert_not_labelled(failed, STORE_DB, old, changed)
    after = scan.run_scan(sandbox, project, stand_in, markers=words(STORE_DB)[1:])
    assert_green(after, "the run after the failed one, real gitleaks back")
    rule_sets = after.rule_sets()
    for word in words(STORE_DB)[1:]:
        assert after.seen_under(word) >= rule_sets, (
            f"after a failed run (gitleaks {fault}), the store was not scanned in full: a clean result was "
            f"recorded from the failed run\n{after.describe()}")
    assert_not_labelled(after, STORE_DB, old, changed)


def _record_candidates(before, after):
    """Files that are new or changed between two snapshots (``{absolute path: sha256}``)."""
    return sorted(path for path, sha in after.items() if before.get(path) != sha)


def _snapshot(sandbox, project, leave_out):
    found = {}
    for top, skip in ((project, [project / ".git"]), (sandbox.home, [project])):
        for rel, sha in scan.tree_snapshot(top, skip=skip).items():
            path = str(Path(top) / rel)
            if path not in leave_out:
                found[path] = sha
    return found


def _damage(paths, how, sha):
    """Damage the record's files. Returns how many were damaged."""
    count = 0
    for path in map(Path, paths):
        data = path.read_bytes()
        if how == "garbage":
            noise = b"".join(hashlib.sha256(f"noise{i}".encode()).digest() for i in range(len(data) // 32 + 1))
            path.write_bytes(noise[:max(len(data), 64)])
            count += 1
        elif how == "truncated":
            path.write_bytes(data[: len(data) // 2])
            count += 1
        else:   # digest-flipped: the record now names a digest one hex digit off, as text or as bytes
            other = format((int(sha[0], 16) + 1) % 16, "x") + sha[1:]
            raw, other_raw = bytes.fromhex(sha), bytes.fromhex(other)
            changed = data.replace(sha.encode(), other.encode()).replace(sha.upper().encode(), other.upper().encode())
            changed = changed.replace(raw, other_raw)
            if changed != data:
                path.write_bytes(changed)
                count += 1
    return count


@pytest.mark.parametrize("how", ("garbage", "truncated", "digest-flipped"))
def test_a_damaged_record_of_clean_results_never_makes_a_store_count_as_clean(env, sandbox, how):
    """The record, if any, is found only by what a run leaves in the project (or under HOME): the files that a
    clean run and a reusing run made or changed, other than the stores and the fresh file."""
    project, stand_in = env
    plain_store(project, CODE_STORE)
    leave_out = {str(project / CODE_STORE), str(project / scan.FRESH_REL)}
    before = _snapshot(sandbox, project, leave_out)
    sha = first_runs(sandbox, project, stand_in, [CODE_STORE])[CODE_STORE]
    candidates = _record_candidates(before, _snapshot(sandbox, project, leave_out))
    if not candidates:
        pytest.skip("the clean result is reused, yet no file in the project or under HOME was made or changed: "
                    "the record is elsewhere, so no damage can be done to it here")
    if not _damage(candidates, how, sha):
        pytest.skip(f"no file the runs left holds the store's digest as text or bytes: {how} cannot be done")
    run = scan.run_scan(sandbox, project, stand_in, markers=words(CODE_STORE))
    if run.returncode not in (None, 0):
        return   # failed closed: allowed
    assert run.returncode is not None, f"the check did not end with a damaged record\n{run.describe()}"
    assert_full_scan(run, CODE_STORE, f"a record damaged ({how}): green, so the store must have been scanned")
    assert_not_labelled(run, CODE_STORE, sha)


# --------------------------------------------------------------------------
# Controls: true today and after
# --------------------------------------------------------------------------

def test_control_a_small_clean_project_is_green(env, sandbox):
    project, _ = env
    db_store(project)
    plain_store(project, CODE_STORE)
    run = scan.run_scan(sandbox, project, None)
    assert_green(run, "a small clean project, real gitleaks alone")


def test_control_a_small_store_with_a_canary_is_red_naming_it_never_the_secret(env, sandbox):
    project, _ = env
    db_store(project)
    plain_store(project, CODE_STORE, extra={SMALL_STORE // 3: scan.SECRET})
    run = scan.run_scan(sandbox, project, None)
    assert_red_naming(run, CODE_STORE, "a small store with a canary, real gitleaks alone")
    assert not run.lines_naming(STORE_DB), f"the clean store was named as holding a secret\n{run.describe()}"

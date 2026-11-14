"""Run 7, S27 (DEC-1178 (4)): the secrets scan judges many texts per gitleaks process, in parallel, with the one-per-file form's verdicts.

The interface (the lead's statement, DEC-1052, DEC-136; the ticket's S27 and its last paragraph): in ``gov.secrets``, ``indexable(root,
paths)`` judges the files' contents **many texts per gitleaks process** (each text set off, each finding put back on its file), its
batches **run in parallel**, at most ``_workers()`` at once (the CPU set, within ``GOV_HEAVY_THREAD_BUDGET``). ``indexable``,
``path_holds_secret`` and ``pool_size`` keep their signatures and meaning. The verdict per file is the one-per-file form's (a file with
a planted secret is left out, a clean file is kept, in the order asked; the namespace filter, links, ``scan: off`` and the reuse record
as today); no secret's value is printed or recorded. On a planted 5,000-file tree the files judged per second are at least 10 times the
one-per-file form's, measured before and after on the same machine.

"The one-per-file form" is the code of the base ``a23678e27`` (this module takes ``git archive a23678e27 src`` into a temporary folder and
runs it in a child process: ``scan_driver.py``). The "after" is this worktree's ``src``. Secrets are built from parts in the case's own
tmp folder (W2-81's ``make_secret``): no secret-shaped string sits in this file, and none is printed (the ``Held`` object withholds it).
"""

from __future__ import annotations

import io
import json
import os
import random
import shutil
import subprocess
import sys
import tarfile
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

import pytest

import w2_88_support as W

BASE_REV = "a23678e27"
DRIVER = W.HERE / "scan_driver.py"
FORMS = ("cloud-access-key", "forge-token")
FACTOR = 10                      # the line: at least 10 times the one-per-file form's files per second
SAMPLE_EVERY = 10                # the one-per-file form is timed on every 10th path of the 5,000 (its run at 16 files/s would take minutes)


# ------------------------------------------------------------------------------------------------------------
# The code of the base, the planted trees, the children
# ------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def before_src(tmp_path_factory):
    """``src`` of the base commit (the one-per-file form), exported by ``git archive`` into a temporary folder: the named folder ``src`` only, git
    run in it (DEC-385: never the whole tree)."""
    folder = tmp_path_factory.mktemp("s27-before")
    data = subprocess.run(["git", "-C", str(W.REPO_ROOT / "src"), "archive", "--format=tar", "--prefix=src/", BASE_REV],
                          capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(folder, filter="data")
    try:
        yield folder / "src"
    finally:
        shutil.rmtree(folder, ignore_errors=True)


@dataclass
class Tree:
    root: Path
    paths: list                                   # in the order asked
    secret_paths: set = field(default_factory=set)
    helds: list = field(default_factory=list)


def plant_tree(base: Path, name: str, n_files: int, *, every: int = 97, scan_off: bool = False, extras: bool = True) -> Tree:
    """A repository (``git init``, nothing committed) with ``n_files`` small clean text files under ``src/``, every ``every``-th one holding a
    planted secret of one of two gitleaks default rules (the project's ``.gitleaks.toml``), and, with ``extras``, the edge cases: a secret
    split across two neighbouring files (no file holds it whole: the texts of a batch must be set off from each other), the same secret in
    two files, a CRLF file, an empty file, a binary file, a 2 MiB clean file, three links, and a file of a namespace that is not embedded."""
    root = Path(base) / name
    root.mkdir(parents=True)
    shutil.copy2(W.S124.GITLEAKS_TEMPLATE, root / ".gitleaks.toml")
    W.write(root, "governance/project/path-map.yaml", W.path_map_text({
        "harbour": {"paths": ["src/**", "docs/**"], "embedding_policy": "embedded"},
        "archive": {"paths": ["archive/**"], "embedding_policy": "not embedded"}}))
    if scan_off:
        W.write(root, "governance/project/secrets.yaml", "scan: off\n")
    tree = Tree(root, [])

    def put(rel, data, secret=False):
        W.write(root, rel, data)
        tree.paths.append(rel)
        if secret:
            tree.secret_paths.add(rel)

    for number in range(n_files):
        rel = f"src/d{number % 50:02d}/f{number:05d}.txt"
        if number % every == every - 1:
            held = W.W81S.make_secret(FORMS[(number // every) % 2], seed=number, salt="s27")
            tree.helds.append(held)
            put(rel, held.line("harbour = 1\nTOKEN={value}\nrows = 2\n"), secret=True)
        else:
            put(rel, f"harbour note {number}\n" * 12 + f"tide table row {number * 7}\n")
    if extras:
        held = W.W81S.make_secret("cloud-access-key", seed=1, salt="s27-twice")
        tree.helds.append(held)
        put("src/twice/a.txt", held.line("KEY={value}\n"), secret=True)
        put("src/twice/b.txt", held.line("# the same key again\nKEY={value}\n"), secret=True)
        split = W.W81S.make_secret("cloud-access-key", seed=2, salt="s27-split")
        tree.helds.append(split)
        whole = split.line("{value}")
        put("src/split/a.txt", "the key begins here: " + whole[:9])                  # no newline: the next text begins at once
        put("src/split/b.txt", whole[9:] + " and ends there\n")
        put("src/crlf/c.txt", "harbour = 1\r\nrows = 2\r\n")
        put("src/empty/e.txt", "")
        put("src/binary/b.bin", b"\x00\x01\x02binary\x00" * 200)
        put("src/big/large.txt", "a clean line of the long table, row of the harbour ledger\n" * 37_000)
        put("archive/old.txt", "the archived mooring plan\n")
        put("docs/guide.md", "# Guide\n\nHow the harbour is run.\n")
        (root / "src/link-clean.txt").symlink_to("d00/f00000.txt")
        (root / "src/link-out.txt").symlink_to("/etc/hostname")
        (root / "src/link-dangling.txt").symlink_to("nowhere.txt")
        tree.paths += ["src/link-clean.txt", "src/link-out.txt", "src/link-dangling.txt"]
    random.Random(88).shuffle(tree.paths)
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "main"], check=True, capture_output=True)
    return tree


def logging_gitleaks(folder: Path, log: Path, delay: float = 0.0) -> Path:
    """A ``gitleaks`` in ``folder`` that notes its start and end (pid and time) in ``log``, waits ``delay`` seconds, and runs the real one
    with the same arguments, its streams and its exit code untouched."""
    folder.mkdir(parents=True, exist_ok=True)
    real = W.S124.REAL_GITLEAKS
    program = folder / "gitleaks"
    program.write_text(
        "#!/bin/sh\n"
        f"printf 'start %s %s\\n' \"$$\" \"$(date +%s.%N)\" >> {json.dumps(str(log))}\n"
        + (f"sleep {delay}\n" if delay else "")
        + f"{json.dumps(real)} \"$@\"\n"
        "rc=$?\n"
        f"printf 'end %s %s\\n' \"$$\" \"$(date +%s.%N)\" >> {json.dumps(str(log))}\n"
        "exit $rc\n", encoding="utf-8")
    program.chmod(0o755)
    return folder


def calls_of(log: Path) -> tuple[int, int]:
    """(number of gitleaks processes started, the most that ran at the same moment) from the logging wrapper's log."""
    if not log.is_file():
        return 0, 0
    events = []
    for line in log.read_text(encoding="utf-8").splitlines():
        kind, _pid, stamp = line.split()
        events.append((float(stamp), 1 if kind == "start" else -1))
    events.sort(key=lambda event: (event[0], event[1]))
    running = peak = 0
    for _stamp, step in events:
        running += step
        peak = max(peak, running)
    return sum(1 for _stamp, step in events if step == 1), peak


def judge(src, tree: Tree, box, listing_name: str, *, paths=None, tools=(), **extra_env):
    """Run ``scan_driver.py`` against ``src`` for ``paths`` of ``tree`` (all of them by default); returns ``(answer, completed process)``."""
    listing = Path(box.base) / listing_name
    listing.write_text(json.dumps(tree.paths if paths is None else paths), encoding="utf-8")
    environment = W.env(box, "127.0.0.1:9", tools=tools, PYTHONPATH=str(src), **extra_env)
    done = subprocess.run([sys.executable, str(DRIVER), str(src), str(tree.root), str(listing)], cwd=str(tree.root), env=environment,
                          capture_output=True, text=True, timeout=1500, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"the scan child failed (exit {done.returncode}):\n{done.stdout[-1500:]}\n{done.stderr[-2500:]}"
    lines = [line for line in done.stdout.splitlines() if line.startswith("{")]
    assert lines, f"the scan child printed no answer:\n{done.stdout[-800:]}\n{done.stderr[-1500:]}"
    return json.loads(lines[-1]), done


def twin(tree: Tree, name: str) -> Tree:
    """A copy of the planted tree of its own (the reuse record of clean results a run writes never carries to the other form)."""
    dest = tree.root.parent / name
    shutil.copytree(tree.root, dest, symlinks=True)
    return Tree(dest, list(tree.paths), set(tree.secret_paths), tree.helds)


# ------------------------------------------------------------------------------------------------------------
# The verdict per file: the one-per-file form's
# ------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("scan", ["on", "off"])
def test_s27_the_verdict_per_file_is_the_one_per_file_forms(box, before_src, scan):
    """success-S27: on a planted set (clean files, planted secrets of two rules, a secret split across two neighbours, the same secret twice, a
    CRLF file, an empty and a binary file, a 2 MiB file, three links, a file of a not-embedded namespace: whatever the namespace filter and the
    links do today is the oracle) in a shuffled order, ``indexable`` of this worktree
    returns exactly the list the one-per-file form (the base) returns, in the order asked. With the scan on: every planted secret file is left
    out and the split halves are kept (no file holds the secret whole); with ``scan: off`` (``governance/project/secrets.yaml``) the secret files
    are kept, as today."""
    tree = plant_tree(box.base, f"set-{scan}", 120, every=13, scan_off=(scan == "off"))
    before_tree = twin(tree, f"set-{scan}-before")
    before, _ = judge(before_src, before_tree, box, "paths-before.json")
    after, run = judge(W.SRC, tree, box, "paths-after.json")
    assert after["module"].startswith(str(W.SRC)), f"the after run did not use this worktree's gov.secrets: {after['module']}"
    assert before["kept"], "the one-per-file form kept nothing: the plant is wrong"
    assert after["kept"] == before["kept"], (
        f"scan {scan}: the verdict differs from the one-per-file form's\n"
        f"only before: {sorted(set(before['kept']) - set(after['kept']))[:12]}\nonly after: {sorted(set(after['kept']) - set(before['kept']))[:12]}\n"
        f"order equal as sets: {sorted(before['kept']) == sorted(after['kept'])}")
    kept = set(after["kept"])
    if scan == "on":
        assert not (kept & tree.secret_paths), f"a file with a planted secret is kept: {sorted(kept & tree.secret_paths)[:8]}"
        for rel in ("src/split/a.txt", "src/split/b.txt", "src/crlf/c.txt", "src/d00/f00000.txt"):
            assert rel in kept, f"the clean file {rel} is left out (the texts of a batch must be set off from each other)"
    else:
        assert tree.secret_paths <= kept, f"with the scan off, files with a planted secret are left out: {sorted(tree.secret_paths - kept)[:8]}"
    assert "src/link-out.txt" not in kept, "a link that points outside the repository is kept"
    order = {rel: number for number, rel in enumerate(tree.paths)}
    assert after["kept"] == sorted(after["kept"], key=order.__getitem__), "the answer is not in the order asked"
    # what the scan may have written: the repository's runtime folder and git folder (the planted files hold the secrets by design), the
    # process's temporary folder, and what it printed
    texts = W.all_text(tree.root / ".gov-runtime", tree.root / ".git", Path(box.base) / "systmp",
                       runs=[SimpleNamespace(stdout=run.stdout, stderr=run.stderr)])
    for held in tree.helds:
        W.assert_no_secret(held, texts, f"S27, scan {scan}")


def test_s27_a_second_run_on_the_same_tree_gives_the_same_verdict(box):
    """success-S27 (the reuse record of clean results, as today): a second ``indexable`` over the same tree answers the first's list."""
    tree = plant_tree(box.base, "again", 90, every=11)
    first, _ = judge(W.SRC, tree, box, "paths-1.json")
    second, _ = judge(W.SRC, tree, box, "paths-2.json")
    assert second["kept"] == first["kept"], "a second run over the same tree changed the verdict (the reuse record is wrong)"
    assert not (set(second["kept"]) & tree.secret_paths), "the second run keeps a file with a planted secret"


# ------------------------------------------------------------------------------------------------------------
# Many texts per process, in parallel, within the budget
# ------------------------------------------------------------------------------------------------------------

def test_s27_many_texts_are_judged_per_gitleaks_process(box):
    """success-S27: 300 files with a planted secret in some are judged by far fewer gitleaks processes than files (at most one process per
    ten files; the one-per-file form starts one for each). The logging ``gitleaks`` first on ``PATH`` counts the starts; the verdict is the
    list of the case above (no planted secret kept)."""
    tree = plant_tree(box.base, "batches", 300, every=29, extras=False)
    log = Path(box.base) / "gitleaks-calls.log"
    tools = logging_gitleaks(Path(box.base) / "tools-count", log)
    answer, _ = judge(W.SRC, tree, box, "paths.json", tools=(tools,))
    started, _peak = calls_of(log)
    assert started >= 1, "the plant did not take: no gitleaks process was started through the logging program on PATH"
    assert started * 10 <= len(tree.paths), (f"{started} gitleaks processes were started for {len(tree.paths)} files: many texts per "
                                              f"process means at most one process per ten files")
    assert not (set(answer["kept"]) & tree.secret_paths), "a file with a planted secret is kept"
    assert len(answer["kept"]) == len(tree.paths) - len(tree.secret_paths), "a clean file is left out"


def test_s27_batches_run_in_parallel_and_never_more_than_the_budget_allows(box):
    """success-S27: with ``GOV_HEAVY_THREAD_BUDGET=3`` and a logging ``gitleaks`` that waits 0.2 s, 600 files are judged with never more than 3
    gitleaks processes at the same moment; where the files took more than one process, two ran at once (the batches are parallel). A design that
    puts 600 files in one process has no parallelism to observe and passes this case: the speed case is the arbiter."""
    tree = plant_tree(box.base, "parallel", 600, every=201, extras=False)
    log = Path(box.base) / "gitleaks-times.log"
    tools = logging_gitleaks(Path(box.base) / "tools-time", log, delay=0.2)
    answer, _ = judge(W.SRC, tree, box, "paths.json", tools=(tools,), GOV_HEAVY_THREAD_BUDGET="3")
    started, peak = calls_of(log)
    assert started >= 1, "the plant did not take: no gitleaks process was started through the logging program on PATH"
    assert peak <= 3, f"{peak} gitleaks processes ran at the same moment with GOV_HEAVY_THREAD_BUDGET=3 (at most _workers() = 3)"
    assert started < 2 or peak >= 2, f"{started} processes ran one after the other: the batches are not run in parallel"
    assert not (set(answer["kept"]) & tree.secret_paths), "a file with a planted secret is kept"


def test_s27_the_public_names_keep_their_signatures_and_meaning(box):
    """success-S27: ``indexable(root, paths)``, ``path_holds_secret(root, path)`` and ``pool_size()`` are still there with the base's parameters;
    ``pool_size`` is a positive whole number and, under ``GOV_HEAVY_THREAD_BUDGET=3``, at most 3; ``path_holds_secret`` is False for a clean
    path and True for a path that names a planted secret."""
    script = Path(box.base) / "names.py"
    script.write_text(
        "import inspect, json, sys\n"
        "sys.path.insert(0, sys.argv[1])\n"
        "from pathlib import Path\n"
        "import gov.secrets as s\n"
        "sys.path.insert(0, sys.argv[3])\n"
        "import w2_81_secret as W81S\n"
        "held = W81S.make_secret('cloud-access-key', seed=5, salt='s27-names')\n"
        "root = Path(sys.argv[2])\n"
        "print(json.dumps({'indexable': list(inspect.signature(s.indexable).parameters), "
        "'path_holds_secret': list(inspect.signature(s.path_holds_secret).parameters), "
        "'pool_size': list(inspect.signature(s.pool_size).parameters), 'pool': s.pool_size(), "
        "'clean': s.path_holds_secret(root, 'src/harbour/notes.txt'), "
        "'named': s.path_holds_secret(root, held.line('src/{value}.txt'))}))\n", encoding="utf-8")
    tree = plant_tree(box.base, "names", 5, extras=False)
    environment = W.env(box, "127.0.0.1:9", PYTHONPATH=str(W.SRC), GOV_HEAVY_THREAD_BUDGET="3")
    done = subprocess.run([sys.executable, str(script), str(W.SRC), str(tree.root), str(W.ACCEPT / "W2-81")], cwd=str(tree.root),
                          env=environment, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"the child failed:\n{done.stdout[-800:]}\n{done.stderr[-1500:]}"
    seen = json.loads(done.stdout.splitlines()[-1])
    assert seen["indexable"] == ["root", "paths"] and seen["path_holds_secret"] == ["root", "path"] and seen["pool_size"] == [], seen
    assert isinstance(seen["pool"], int) and 1 <= seen["pool"] <= 3, f"pool_size() is {seen['pool']} under GOV_HEAVY_THREAD_BUDGET=3"
    assert seen["clean"] is False, "path_holds_secret is True for a clean path"
    assert seen["named"] is True, "path_holds_secret is False for a path that holds a planted secret"


# ------------------------------------------------------------------------------------------------------------
# The speed: at least 10 times the one-per-file form's files per second, on a planted 5,000-file tree
# ------------------------------------------------------------------------------------------------------------

@pytest.mark.slow
def test_s27_a_five_thousand_file_tree_is_judged_at_least_ten_times_faster_with_the_same_findings(box, before_src):
    """success-S27 (the speed line): the planted 5,000-file tree (about 52 files hold a planted secret, two rules) judged by ``indexable`` of
    this worktree (all 5,000 paths) and by the one-per-file form of the base (every 10th path: 500 paths, its run over all 5,000 would take
    minutes), each on a copy of its own, in the same process one after the other on this machine. The figures (files judged per second) are
    printed and in the failure message; after >= 10 x before. The 500 the base judged get the same verdict from this worktree's run."""
    tree = plant_tree(box.base, "five-thousand", 5000, every=97, extras=False)
    sample = tree.paths[::SAMPLE_EVERY]
    before_tree = twin(tree, "five-thousand-before")
    before, _ = judge(before_src, before_tree, box, "paths-before.json", paths=sample)
    after, run = judge(W.SRC, tree, box, "paths-after.json")
    before_rate = before["judged"] / before["seconds"]
    after_rate = after["judged"] / after["seconds"]
    print(f"S27 files judged per second: before (one gitleaks per file, {before['judged']} paths) {before_rate:.1f}/s in "
          f"{before['seconds']:.1f} s; after (batched, {after['judged']} paths) {after_rate:.1f}/s in {after['seconds']:.1f} s; "
          f"ratio {after_rate / before_rate:.1f}; pool {after['pool']}")
    wanted = set(sample)
    assert [p for p in after["kept"] if p in wanted] == before["kept"], \
        "the verdicts on the sampled paths differ from the one-per-file form's"
    assert not (set(after["kept"]) & tree.secret_paths), "a file with a planted secret is kept"
    assert len(after["kept"]) == len(tree.paths) - len(tree.secret_paths), "a clean file is left out"
    assert after_rate >= FACTOR * before_rate, (
        f"after {after_rate:.1f} files/s ({after['seconds']:.1f} s for {after['judged']}) is not {FACTOR} times before "
        f"{before_rate:.1f} files/s ({before['seconds']:.1f} s for {before['judged']}): ratio {after_rate / before_rate:.1f}")
    texts = W.all_text(Path(box.base) / "systmp", runs=[SimpleNamespace(stdout=run.stdout, stderr=run.stderr)])
    for held in tree.helds[:6]:
        W.assert_no_secret(held, texts, "S27 speed case")


# ------------------------------------------------------------------------------------------------------------
# The narrow check's finding P1-1 (DEC-136): a match must not run from one file's text into the next file's
# ------------------------------------------------------------------------------------------------------------

BARE_KEYS = [                       # (the last line of file A: a generic key with no value, whether A ends with a newline)
    pytest.param("password:", True, id="password-colon"),
    pytest.param("token =", True, id="token-equals"),
    pytest.param("secret:", False, id="secret-colon-no-newline"),
]


def generic_secret(seed: int, salt: str):
    """A value that only gitleaks' ``generic-api-key`` rule catches (no prefix of any other rule): 32 characters drawn from the seed, built in
    the case's memory, withheld by the ``Held`` object."""
    return W.W81S.Held(W.W81S._draw(W.W81S._ALNUM, 32, f"w2-88:p1-1:{seed}:{salt}"), "generic-api-key")


def plant_shadow_tree(box, name: str, n_clean: int, pairs) -> tuple:
    """A planted repository of ``n_clean`` clean files, each pair of ``pairs`` = ``(position, bare key, A ends with a newline, A comes first)``
    put into the list asked at ``position``, A and B adjacent. File A: clean lines, then the bare key as its last line. File B: the first line
    ``API_KEY=<value>`` (only ``generic-api-key`` catches it), then a clean line. Returns ``(tree, paths of the A files)``; ``tree.secret_paths``
    holds the B files."""
    tree = plant_tree(box.base, name, n_clean, every=10 ** 6, extras=False)
    clean = list(tree.paths)
    bare_paths = []
    inserts = []
    for number, (position, key, newline, bare_first) in enumerate(pairs):
        rel_a, rel_b = f"src/config/{number:02d}-base.env", f"src/config/{number:02d}-prod.env"
        held = generic_secret(number, name)
        tree.helds.append(held)
        W.write(tree.root, rel_a, "harbour = 1\nrows = 2\n" + key + ("\n" if newline else ""))
        W.write(tree.root, rel_b, held.line("API_KEY={value}\nrows = 2\n"))
        tree.secret_paths.add(rel_b)
        bare_paths.append(rel_a)
        inserts.append((position, [rel_a, rel_b] if bare_first else [rel_b, rel_a]))
    paths = []
    for index, rel in enumerate(clean):
        for position, pair in inserts:
            if position == index:
                paths += pair
        paths.append(rel)
    tree.paths = paths
    return tree, bare_paths


def rules_that_catch(box, tree: Tree, rel: str) -> list:
    """The rule ids of the project's ``.gitleaks.toml`` that catch the file ``rel`` of the tree alone (a real gitleaks run on that one file, its
    report redacted and read back; no value is kept or printed)."""
    report = Path(box.base) / "plant-check.json"
    report.unlink(missing_ok=True)
    done = subprocess.run([W.S124.REAL_GITLEAKS, "dir", str(tree.root / rel), "--config", str(tree.root / ".gitleaks.toml"), "--no-banner",
                           "--redact", "--exit-code", "0", "--report-format", "json", "--report-path", str(report)],
                          cwd=str(tree.root), env=W.env(box, "127.0.0.1:9"), capture_output=True, text=True, timeout=120,
                          stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"gitleaks failed on {rel} (exit {done.returncode}):\n{done.stderr[-800:]}"
    found = json.loads(report.read_text(encoding="utf-8") or "[]") if report.is_file() else []
    return sorted({item["RuleID"] for item in found})


def check_shadow(box, before_src, name: str, n_clean: int, pairs) -> None:
    """The oracle is the one-per-file form (the base's ``indexable`` over a copy of the tree, no reuse record); then this worktree's
    ``indexable`` twice in the same empty ``HOME`` with a reuse record of clean results named under it."""
    tree, bare_paths = plant_shadow_tree(box, name, n_clean, pairs)
    for rel in sorted(tree.secret_paths):
        assert rules_that_catch(box, tree, rel) == ["generic-api-key"], f"the plant did not take: {rel} alone is not caught by generic-api-key only"
    for rel in bare_paths:
        assert rules_that_catch(box, tree, rel) == [], f"the plant did not take: {rel} alone is caught"
    before_tree = twin(tree, f"{name}-before")
    before, _ = judge(before_src, before_tree, box, "paths-before.json")
    assert not (set(before["kept"]) & tree.secret_paths), \
        f"the plant did not take: the one-per-file form keeps {sorted(set(before['kept']) & tree.secret_paths)[:4]}"
    assert set(bare_paths) <= set(before["kept"]), "the plant did not take: the one-per-file form leaves out a file with a bare key only"
    reuse = Path(box.home) / ".cache" / "gov-os" / "secrets-reuse.json"
    reuse.parent.mkdir(parents=True, exist_ok=True)
    runs = []
    for number in (1, 2):
        after, run = judge(W.SRC, tree, box, f"paths-after-{number}.json", GOV_SECRETS_CACHE=str(reuse))
        runs.append(SimpleNamespace(stdout=run.stdout, stderr=run.stderr))
        assert after["module"].startswith(str(W.SRC)), f"the after run did not use this worktree's gov.secrets: {after['module']}"
        which = "first" if number == 1 else "second (the reuse record of clean results is in play)"
        kept = set(after["kept"])
        for rel in sorted(tree.secret_paths & kept):
            pytest.fail(f"{which} call: {rel} is kept: the batch's finding is put back on A only (P1-1)")
        for rel in bare_paths:
            assert rel in kept, f"{which} call: {rel}, clean alone (one bare key, no value), is left out: the verdict is not the one-per-file form's"
        assert after["kept"] == before["kept"], (
            f"{which} call: the verdict differs from the one-per-file form's\n"
            f"only before: {sorted(set(before['kept']) - kept)[:8]}\nonly after: {sorted(kept - set(before['kept']))[:8]}")
    texts = W.all_text(tree.root / ".gov-runtime", tree.root / ".git", Path(box.base) / "systmp", Path(box.home), runs=runs)
    for held in tree.helds:
        W.assert_no_secret(held, texts, "S27 P1-1")


@pytest.mark.parametrize("bare_first", [True, False], ids=["bare-key-file-first", "secret-file-first"])
@pytest.mark.parametrize("key,newline", BARE_KEYS)
def test_s27_p1_1_a_bare_key_ending_one_file_does_not_swallow_the_next_files_secret(box, before_src, key, newline, bare_first):
    """success-S27 (the narrow check's P1-1, DEC-136): a file A whose last line is a bare generic key with no value (``password:``, ``token =``,
    ``secret:``; the last with no trailing newline) and a file B whose first line holds a secret only ``generic-api-key`` catches
    (``API_KEY=<value>``), adjacent in the order asked in the middle of 21 clean files, in both orders. With the texts judged many per gitleaks
    process, gitleaks' ``\\s`` classes cross a text's end: one match from A's last line into B's first swallows B's own. The verdict per file is
    still the one-per-file form's (the base's, the oracle): B left out of ``indexable``'s answer, A kept; a second call in the same empty
    ``HOME`` (the reuse record of clean results) answers the same, never B clean."""
    check_shadow(box, before_src, "shadow", 21, [(10, key, newline, bare_first)])


def test_s27_p1_1_pairs_of_each_form_spread_through_a_long_list_are_each_judged_as_one_per_file(box, before_src):
    """success-S27 (P1-1): the pairs of the three bare-key forms, in both orders, are put at every 13th place of a list of 80 clean files (some
    pair is inside any batch, wherever a batch ends); every B is left out, every A kept, as the one-per-file form's verdict, on a first and on a
    second call in the same empty ``HOME``."""
    pairs = [(8 + 13 * number, key.values[0], key.values[1], number % 2 == 0)
             for number, key in enumerate([*BARE_KEYS, *BARE_KEYS])]
    check_shadow(box, before_src, "spread", 80, pairs)

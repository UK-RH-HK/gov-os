"""Run 9, S27's folder mode (DEC-1183 (2)): every file's verdict is its own, whatever shares its batch.

The interface (the lead's run 9 statement, DEC-1052, DEC-136; the ticket's S27 line and its reopen paragraphs of 2026-11-14 and
2026-11-15 05:20): in ``gov.secrets``, ``indexable(root, paths)`` writes each batch's texts into a private temporary folder made by
``tempfile.mkdtemp`` (0700, each file 0600), outside the root being scanned (else ``RuntimeError`` naming it, nothing written
there), each text one file named by its number only (never a repository path), and runs one ``gitleaks dir <folder>`` per batch
and rule set (``gitleaks`` found on ``PATH``); each finding names its own file and is put on that text alone. Fail closed: an exit
other than 0 or 3 raises; exit 3 with a report that cannot be read, or a finding naming no text of the batch, judges every text of
that batch holding a secret; none of a failed batch's texts is let through or remembered clean. The folder is removed after the
batch, also when gitleaks fails or the process raises. The assessment's scan (``assess.py``) uses the same core: no code path
joins two texts into one gitleaks input.

The oracle of every verdict case is **the one-per-file form**: the base ``a23678e27``'s ``src`` (``git archive``, run by
``scan_driver.py``, as run 7's cases), on a copy of the tree of its own. The cases call only public names (``indexable``,
``scan_counts``, ``gov adopt --lite --stage MA``) and watch a recording ``gitleaks`` first on ``PATH`` (``w2_88_scan_support.py``).
Secrets are built from parts in each case's memory (W2-81's builder); no secret-shaped string sits in this file, none is printed.
The P1R-1 plants are the probe's (``docs/probes/DAEO-2bdu/PR-DAEO-2bdu-p1.md``, "Findings").
"""

from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest

import w2_88_scan_support as SW
import w2_88_support as W

BASE_REV = "a23678e27"                      # the one-per-file form (as run 7's cases)
DRIVER = W.HERE / "scan_driver.py"
W81S = W.W81S
B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
MARK = "s27-fail-mark-7731"                 # a plain word: the failing wrapper's trigger


# ------------------------------------------------------------------------------------------------------------
# The base, plants, the child
# ------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def before_src(tmp_path_factory):
    """``src`` of the base commit (the one-per-file form), exported by ``git archive`` (the named folder ``src`` only, DEC-385)."""
    folder = tmp_path_factory.mktemp("s27-folder-before")
    data = subprocess.run(["git", "-C", str(W.REPO_ROOT / "src"), "archive", "--format=tar", "--prefix=src/", BASE_REV],
                          capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(folder, filter="data")
    try:
        yield folder / "src"
    finally:
        shutil.rmtree(folder, ignore_errors=True)


class Tree(SimpleNamespace):
    """``root``, ``paths`` (in the order asked), ``secret`` (the paths holding a planted secret), ``helds``, ``tags`` (tag -> path)."""


def plant(base: Path, name: str, files: list, *, extra_patterns: tuple = ()) -> Tree:
    """A repository (``git init``, nothing committed) with the project's ``.gitleaks.toml`` and a path map whose one embedded
    namespace takes ``src/**`` (and ``extra_patterns``); ``files`` is ``[(rel, bytes or str, holds a secret)]`` in the order asked."""
    root = Path(base) / name
    root.mkdir(parents=True)
    shutil.copy2(W.S124.GITLEAKS_TEMPLATE, root / ".gitleaks.toml")
    W.write(root, "governance/project/path-map.yaml", W.path_map_text({
        "harbour": {"paths": ["src/**", *extra_patterns], "embedding_policy": "embedded"}}))
    tree = Tree(root=root, paths=[], secret=set(), helds=[], tags={})
    for rel, data, secret in files:
        W.write(root, rel, data)
        tree.paths.append(rel)
        if secret:
            tree.secret.add(rel)
        text = data if isinstance(data, str) else data.decode("latin-1")
        for word in text.split():
            if word.startswith(SW.TAG):
                tree.tags[word] = rel
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "main"], check=True, capture_output=True)
    return tree


def twin(tree: Tree, name: str) -> Tree:
    dest = tree.root.parent / name
    shutil.copytree(tree.root, dest, symlinks=True)
    return Tree(root=dest, paths=list(tree.paths), secret=set(tree.secret), helds=tree.helds, tags=dict(tree.tags))


def judge(src, tree: Tree, box, listing_name: str, *, tools=(), **extra_env) -> tuple[dict, subprocess.CompletedProcess]:
    """``scan_driver.py`` against ``src`` for every path of ``tree``, an exception caught and reported (``S27_DRIVER_CATCH``)."""
    listing = Path(box.base) / listing_name
    listing.write_text(json.dumps(tree.paths), encoding="utf-8")
    environment = W.env(box, "127.0.0.1:9", tools=tools, PYTHONPATH=str(src), S27_DRIVER_CATCH="1", **extra_env)
    done = subprocess.run([sys.executable, str(DRIVER), str(src), str(tree.root), str(listing)], cwd=str(tree.root), env=environment,
                          capture_output=True, text=True, timeout=1500, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"the scan child failed (exit {done.returncode}):\n{done.stdout[-1500:]}\n{done.stderr[-2500:]}"
    lines = [line for line in done.stdout.splitlines() if line.startswith("{")]
    assert lines, f"the scan child printed no answer:\n{done.stdout[-800:]}\n{done.stderr[-1500:]}"
    return json.loads(lines[-1]), done


def kept_of(answer: dict, what: str) -> list:
    assert answer["raised"] is None, f"{what}: indexable raised {answer['raised']}: {answer['message']}"
    return answer["kept"]


def rules_that_catch(box, tree: Tree, rel: str) -> list:
    """The rule ids of the project's ``.gitleaks.toml`` that catch the file ``rel`` alone (a real gitleaks run on that one file, its
    report redacted; no value kept or printed): the plant's own check."""
    report = Path(box.base) / "plant-check.json"
    report.unlink(missing_ok=True)
    done = subprocess.run([W.S124.REAL_GITLEAKS, "dir", str(tree.root / rel), "--config", str(tree.root / ".gitleaks.toml"), "--no-banner",
                           "--redact", "--exit-code", "0", "--report-format", "json", "--report-path", str(report)],
                          cwd=str(tree.root), env=W.env(box, "127.0.0.1:9"), capture_output=True, text=True, timeout=120,
                          stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"gitleaks failed on {rel!r} (exit {done.returncode}):\n{done.stderr[-800:]}"
    found = json.loads(report.read_text(encoding="utf-8") or "[]") if report.is_file() else []
    return sorted({item["RuleID"] for item in found})


def assert_no_value(tree: Tree, box, runs, what: str, *folders) -> None:
    texts = W.all_text(tree.root / ".gov-runtime", tree.root / ".git", Path(box.base) / "systmp", Path(box.home), *folders,
                       runs=[SimpleNamespace(stdout=r.stdout, stderr=r.stderr) for r in runs])
    for held in tree.helds:
        W.assert_no_secret(held, texts, what)


def oracle(before_src, tree: Tree, box, name: str) -> list:
    """The one-per-file form's answer on a copy of ``tree``; it must leave out every planted secret's file and keep every other."""
    before, _ = judge(before_src, twin(tree, f"{name}-before"), box, f"{name}-before.json")
    kept = kept_of(before, "the one-per-file form")
    assert not (set(kept) & tree.secret), f"the plant did not take: the one-per-file form keeps {sorted(set(kept) & tree.secret)[:4]!r}"
    clean = [rel for rel in tree.paths if rel not in tree.secret]
    assert set(clean) <= set(kept), f"the plant did not take: the one-per-file form leaves out the clean {sorted(set(clean) - set(kept))[:4]!r}"
    return kept


def assert_own_verdicts(after_kept: list, before_kept: list, tree: Tree, which: str) -> None:
    kept = set(after_kept)
    for rel in tree.paths:
        if rel in tree.secret:
            assert rel not in kept, f"{which}: {rel!r}, which holds a planted secret, is kept: its verdict is not its own (fails open)"
        else:
            assert rel in kept, f"{which}: the clean {rel!r} is left out: its verdict is not its own"
    assert after_kept == before_kept, f"{which}: the answer differs from the one-per-file form's (order or content)"


def secret(form: str, seed: int, salt: str):
    held = W81S.make_secret(form, seed=seed, salt=f"run9-{salt}")
    return held


def clean_text(number: int, tag: str | None = None) -> str:
    head = f"# {SW.TAG}{tag}\n" if tag else ""
    return head + f"harbour note {number}\n" * 6 + f"tide table row {number * 7}\n"


# ------------------------------------------------------------------------------------------------------------
# P1R-1: a match that runs from one file's text into the next, then dropped by a filter, must not swallow the next file's secret
# ------------------------------------------------------------------------------------------------------------

def curl_pair(number: int, salt: str, backslash: bool):
    """File A (a doc ending in a bare ``curl`` line, with or without a trailing ``\\``) and file B (a script with a real ``curl -u
    deploy:<password>``, then ``echo ok``, then an allowlisted ``curl -u user:$PASSWORD``): the probe's shape."""
    password = W81S._draw(W81S._ALNUM, 18, f"run9:curl:{salt}:{number}")
    held = W81S.Held(password, "curl-auth-user")
    a = "# Health\n\nCheck it:\n\ncurl https://api.example.com/health" + (" \\\n" if backslash else "\n")
    variable = "$" + "PASSWORD"
    b = held.line("curl -u deploy:{value} https://deploy.example.com/api/v1/push\necho ok\n"
                  f"curl -u user:{variable} https://deploy.example.com/api/v1/push\n")
    return a, b, held, "curl-auth-user"


def key_pair(number: int, salt: str):
    """File A (an unterminated BEGIN header, then a line holding ``false``) and file B (a real private key): the probe's second shape."""
    kind = "RSA PRI" + "VATE KEY"
    body = W81S._draw(B64, 64 * 12, f"run9:pk:{salt}:{number}")
    held = W81S.Held(body[:64], "private-key")
    a = "# a note on keys\n" + "-----" + "BEGIN " + kind + "-----\nverify = false\n"
    b = ("-----" + "BEGIN " + kind + "-----\n" + "\n".join(body[i:i + 64] for i in range(0, len(body), 64)) + "\n"
         + "-----" + "END " + kind + "-----\n")
    return a, b, held, "private-key"


SHAPES = {
    "curl-bare": lambda number, salt: curl_pair(number, salt, False),
    "curl-backslash": lambda number, salt: curl_pair(number, salt, True),
    "private-key": key_pair,
}


def check_pairs(box, before_src, name: str, shape: str, a_first: bool, positions, n_clean: int) -> None:
    """Pairs of ``shape`` put at ``positions`` of a list of ``n_clean`` clean files (A then B when ``a_first``); the plant checked by a
    real gitleaks run on each file alone; the one-per-file form's answer is the oracle; this worktree's ``indexable`` twice in the same
    empty ``HOME`` with a reuse record of clean results named under it."""
    files, pairs = [(f"src/plain/n{n:03d}.txt", clean_text(n), False) for n in range(n_clean)], []
    helds = []
    for number, position in enumerate(positions):
        a, b, held, rule = SHAPES[shape](number, f"{name}-{shape}")
        helds.append(held)
        rel_a, rel_b = f"src/p1r/{number:02d}-a-notes.md", f"src/p1r/{number:02d}-b-deploy.sh"
        pair = [(rel_a, a, False), (rel_b, b, True)]
        pairs.append((position, pair if a_first else pair[::-1], rel_a, rel_b, rule))
    ordered = []
    for index in range(n_clean + 1):
        for position, pair, *_ in pairs:
            if position == index:
                ordered += pair
        if index < n_clean:
            ordered.append(files[index])
    tree = plant(box.base, name, ordered)
    tree.helds = helds
    for _position, _pair, rel_a, rel_b, rule in pairs:
        assert rules_that_catch(box, tree, rel_b) == [rule], f"the plant did not take: {rel_b} alone is not caught by {rule} only"
        assert rules_that_catch(box, tree, rel_a) == [], f"the plant did not take: {rel_a} alone is caught"
    before_kept = oracle(before_src, tree, box, name)
    reuse = Path(box.home) / ".cache" / "gov-os" / "secrets-reuse.json"
    reuse.parent.mkdir(parents=True, exist_ok=True)
    runs = []
    for number in (1, 2):
        after, run = judge(W.SRC, tree, box, f"{name}-after-{number}.json", GOV_SECRETS_CACHE=str(reuse))
        runs.append(run)
        assert after["module"].startswith(str(W.SRC)), f"the after run did not use this worktree's gov.secrets: {after['module']}"
        which = "first call" if number == 1 else "second call (the reuse record of clean results in play)"
        assert_own_verdicts(kept_of(after, which), before_kept, tree, f"P1R-1 {shape}, {which}")
    assert_no_value(tree, box, runs, f"P1R-1 {shape}")


@pytest.mark.parametrize("order", ["a-then-b", "b-then-a"])
@pytest.mark.parametrize("shape", list(SHAPES))
def test_s27_p1r_1_the_pair_alone_each_file_keeps_its_own_verdict(box, before_src, shape, order):
    """success-S27 (P1R-1, the probe's blocker; fails open if broken): the pair alone, nothing else asked: (curl-bare, curl-backslash) A ends
    in a bare ``curl https://...`` line (with or without a trailing ``\\``), B holds a real ``curl -u deploy:<password>`` then an allowlisted
    ``curl -u user:$PASSWORD``; (private-key) A holds an unterminated BEGIN header then ``false``, B a real key. In both orders: B left out,
    A kept, as the one-per-file form, on a first and a second call in the same ``HOME``."""
    check_pairs(box, before_src, f"alone-{shape}-{order}", shape, order == "a-then-b", [0], 0)


@pytest.mark.parametrize("order", ["a-then-b", "b-then-a"])
@pytest.mark.parametrize("shape", list(SHAPES))
def test_s27_p1r_1_pairs_at_the_start_the_middle_and_the_end_of_a_long_list_each_keep_their_own_verdict(box, before_src, shape, order):
    """success-S27 (P1R-1): three pairs of the shape in a list of 48 clean files, the first pair at the very start, the second in the middle,
    the third at the very end (each pair adjacent, so in one batch whatever the batch's size, unless a batch ends between them), in both
    orders: every B left out, every A and every clean file kept, as the one-per-file form, on a first and a second call."""
    check_pairs(box, before_src, f"spread-{shape}-{order}", shape, order == "a-then-b", [0, 24, 48], 48)


# ------------------------------------------------------------------------------------------------------------
# Two files whose secrets would collide in one stream
# ------------------------------------------------------------------------------------------------------------

def collision_files(order: str) -> tuple[list, list]:
    """Pairs, each adjacent in the order asked, whose texts would collide if joined: the same secret in both; the halves of one token
    (A ends inside it, no newline; neither holds it whole); two secrets that would run into one word (A ends ``KEY=<cloud key>`` with no
    newline, B begins with a forge token at its first byte); a secret whose match would run on into the next file's first word (A ends
    with a cloud key, no newline; B, clean, begins with upper-case letters and digits)."""
    salt = f"collide-{order}"
    same = secret("cloud-access-key", 1, salt)
    split = secret("forge-token", 2, salt)
    left, right = secret("cloud-access-key", 3, salt), secret("forge-token", 4, salt)
    run_on = secret("cloud-access-key", 5, salt)
    whole = split.line("{value}")
    pairs = [
        [("src/collide/same-a.env", same.line("KEY={value}\n"), True), ("src/collide/same-b.env", same.line("# again\nKEY={value}\n"), True)],
        [("src/collide/half-a.txt", "the line begins here: " + whole[:17], False), ("src/collide/half-b.txt", whole[17:] + " and ends\n", False)],
        [("src/collide/merge-a.env", left.line("KEY={value}"), True), ("src/collide/merge-b.env", right.line("{value}\nrows = 2\n"), True)],
        [("src/collide/runon-a.env", run_on.line("rows = 1\nKEY={value}"), True), ("src/collide/runon-b.txt", "Q7ZX9 TIDE TABLE\nrows = 3\n", False)],
    ]
    files = []
    for index, pair in enumerate(pairs):
        files.append((f"src/plain/c{index:02d}.txt", clean_text(index), False))
        files += pair if order == "a-then-b" else pair[::-1]
    return files, [same, split, left, right, run_on]


@pytest.mark.parametrize("order", ["a-then-b", "b-then-a"])
def test_s27_two_files_whose_secrets_would_collide_in_one_stream_each_keep_their_own_verdict(box, before_src, order):
    """success-S27: four pairs whose texts collide if joined (the same secret twice; the halves of one token; two secrets that would run into
    one word; a secret that would run on into the next file's first word), each pair adjacent among clean files, in both orders. Each file
    alone is first checked by a real gitleaks run (a secret file caught, a clean one not); then each file's verdict is its own: every
    secret file left out, every clean file (the halves, the run-on's neighbour) kept, the answer the one-per-file form's."""
    files, helds = collision_files(order)
    tree = plant(box.base, f"collide-{order}", files)
    tree.helds = helds
    for rel in tree.paths:
        caught = rules_that_catch(box, tree, rel)
        assert bool(caught) == (rel in tree.secret), f"the plant did not take: {rel} alone is caught by {caught}"
    before_kept = oracle(before_src, tree, box, "collide")
    after, run = judge(W.SRC, tree, box, "collide-after.json")
    assert_own_verdicts(kept_of(after, "collisions"), before_kept, tree, f"collisions {order}")
    assert_no_value(tree, box, [run], "collisions")


# ------------------------------------------------------------------------------------------------------------
# Names with a space and a newline
# ------------------------------------------------------------------------------------------------------------

SPACE_DIR, NEWLINE_DIR = "src/with space", "src/newline-dir"


def test_s27_names_with_a_space_and_a_newline_are_judged_each_by_its_own_name_and_reach_no_gitleaks_argument(box, before_src):
    """success-S27 (interface item 3): in one list, ``src/with space/a b secret.txt`` (a cloud key) and ``src/newline-dir/line<newline>break
    secret.txt`` (a forge token), each beside a clean file of a name of the same kind (a space; a newline) and among 10 clean neighbours, all
    asked of ``indexable`` (the path map names the two newline paths exactly, so the namespace filter takes them). Each secret file is left
    out by its own name, every clean file kept (the one-per-file form's answer); and no gitleaks argument, nor any entry of a folder given to
    ``gitleaks dir``, holds the repository's root, any asked path, or any of the planted names (the recording ``gitleaks`` lists them)."""
    cloud, forge = secret("cloud-access-key", 11, "names"), secret("forge-token", 12, "names")
    newline_secret, newline_clean = f"{NEWLINE_DIR}/line\nbreak secret.txt", f"{NEWLINE_DIR}/clean\nnext neighbour.txt"
    files = [(f"src/plain/plain-neighbour-{n:02d}.txt", clean_text(n), False) for n in range(5)]
    files += [(f"{SPACE_DIR}/a b secret.txt", cloud.line("KEY={value}\n"), True), (f"{SPACE_DIR}/clean c neighbour.txt", clean_text(40), False),
              (newline_secret, forge.line("TOKEN={value}\n"), True), (newline_clean, clean_text(41), False)]
    files += [(f"src/plain/plain-neighbour-{n:02d}.txt", clean_text(n), False) for n in range(5, 10)]
    tree = plant(box.base, "names", files, extra_patterns=(newline_secret, newline_clean))
    tree.helds = [cloud, forge]
    before_kept = oracle(before_src, tree, box, "names")
    log = Path(box.base) / "names-calls.log"
    tools = SW.recording_gitleaks(Path(box.base) / "tools-names", log)
    after, run = judge(W.SRC, tree, box, "names-after.json", tools=(tools,))
    assert_own_verdicts(kept_of(after, "names"), before_kept, tree, "names with a space and a newline")
    noted = SW.calls(log)
    assert noted, "the plant did not take: no gitleaks call went through the recording program on PATH"
    words = {str(tree.root)} | set(tree.paths) | {Path(rel).name for rel in tree.paths} | {"with space", "newline-dir", "line\nbreak", "clean\nnext"}
    for call in noted:
        for argument in call["args"]:
            hits = sorted(word for word in words if word in argument)
            assert not hits, f"a gitleaks argument holds a repository name: {hits!r} in {argument!r}"
        for name, _mode in call.get("entries", []):
            hits = sorted(word for word in words if word in name)
            assert not hits, f"an entry of the folder given to gitleaks dir holds a repository name: {hits!r} in {name!r}"
    assert_no_value(tree, box, [run], "names")


# ------------------------------------------------------------------------------------------------------------
# A failing gitleaks inside one batch: fail closed, never open; nothing of that batch remembered clean
# ------------------------------------------------------------------------------------------------------------

def failing_tree(box, name: str) -> Tree:
    """14 clean files, each with a tag of its own, and in the middle one file holding a cloud key, its tag and the wrapper's marker."""
    held = secret("cloud-access-key", 21, name)
    files = [(f"src/plain/f{n:02d}.txt", clean_text(n, f"c{n:02d}"), False) for n in range(14)]
    files.insert(7, ("src/keys/marked.env", held.line(f"# {SW.TAG}secret {MARK}\nKEY={{value}}\n"), True))
    tree = plant(box.base, name, files)
    tree.helds = [held]
    return tree


@pytest.mark.parametrize("mode", ["fail", "garbage", "foreign"], ids=["exit-2", "exit-3-unreadable-report", "exit-3-finding-names-no-file"])
def test_s27_a_failing_gitleaks_in_one_batch_fails_closed_and_nothing_of_that_batch_is_remembered_clean(box, mode):
    """success-S27 (interface item 7; fails open if broken): a recording ``gitleaks`` first on ``PATH`` runs the real one, but for a call
    whose texts hold the planted marker (the secret file's) it answers: (exit-2) the real report and exit 2; (exit-3-unreadable-report) exit 3
    and ``{ not a report``; (exit-3-finding-names-no-file) exit 3 and one finding whose ``File`` is ``<folder>/999999``. "That batch" is
    every text of the calls holding the marker (their tags). ``indexable`` raises, or returns with every file of that batch left out (never
    a clean verdict on them); every folder given to gitleaks is gone after it returns or raises. A second run with a logging-only wrapper
    (the real answers), the same ``HOME`` and reuse record: every file of that batch is given to gitleaks again (its tag is among the second
    run's texts; ``scan_counts()["content"]["scanned"]`` at least that many), the secret file is left out and every clean file kept."""
    tree = failing_tree(box, f"failing-{mode}")
    reuse = Path(box.home) / ".cache" / "gov-os" / "secrets-reuse.json"
    reuse.parent.mkdir(parents=True, exist_ok=True)
    log = Path(box.base) / f"failing-{mode}.log"
    tools = SW.recording_gitleaks(Path(box.base) / f"tools-{mode}", log, mode=mode, mark=MARK)
    first, run1 = judge(W.SRC, tree, box, "failing-1.json", tools=(tools,), GOV_SECRETS_CACHE=str(reuse))
    noted = SW.calls(log)
    marked = [call for call in noted if call["marked"]]
    assert marked, "the plant did not take: no gitleaks call held the marker"
    batch = set().union(*(SW.tags_of(call) for call in marked))
    assert f"{SW.TAG}secret" in batch, f"the plant did not take: the marked calls' tags {sorted(batch)} lack the secret file's"
    batch_files = sorted(tree.tags[tag] for tag in batch if tag in tree.tags)
    if first["raised"] is None:
        let_through = sorted(set(first["kept"]) & set(batch_files))
        assert not let_through, (f"{mode}: indexable returned and kept {len(let_through)} file(s) of the batch whose gitleaks failed "
                                 f"({let_through[:4]}): a failed batch must raise or leave out every one of its files")
    left = sorted(c["folder"] for c in noted if c["folder"] and Path(c["folder"]).exists())
    assert not left, f"{mode}: {len(left)} folder(s) given to gitleaks dir remain after indexable {'raised' if first['raised'] else 'returned'}: {left[:2]}"
    log2 = Path(box.base) / f"failing-{mode}-again.log"
    tools2 = SW.recording_gitleaks(Path(box.base) / f"tools-{mode}-again", log2)
    second, run2 = judge(W.SRC, tree, box, "failing-2.json", tools=(tools2,), GOV_SECRETS_CACHE=str(reuse))
    kept = kept_of(second, "the second run, with the real gitleaks")
    again = set().union(*(SW.tags_of(call) for call in SW.calls(log2)))
    missing = sorted(tree.tags[tag] for tag in batch - again if tag in tree.tags)
    assert not missing, (f"{mode}: the second run did not give gitleaks {len(missing)} file(s) of the failed batch ({missing[:4]}): "
                         f"they were remembered clean from a batch whose gitleaks failed")
    counts = second["counts"]["content"]
    assert counts["scanned"] >= len(batch_files), f"{mode}: scan_counts says {counts} for a second run that must scan the {len(batch_files)} files of the failed batch"
    assert "src/keys/marked.env" not in kept, "the second run keeps the file holding the planted secret"
    assert set(tree.paths) - tree.secret <= set(kept), f"the second run leaves out clean files: {sorted(set(tree.paths) - tree.secret - set(kept))[:4]}"
    assert_no_value(tree, box, [run1, run2], f"failing gitleaks {mode}", log, log2)


# ------------------------------------------------------------------------------------------------------------
# The folder itself
# ------------------------------------------------------------------------------------------------------------

def test_s27_each_batch_folder_is_private_outside_the_root_holds_no_repository_name_and_is_removed(box):
    """success-S27 (interface items 2 and 3; F2: nothing written in the repository): 20 tagged files (two hold a planted secret). The
    recording ``gitleaks`` notes, at each call, the folder after ``dir``: there is at least one such call; each folder is a folder outside the
    root being scanned, of mode 0700, its entries readable by the owner only (no group or other bit), no entry name holds the root, an asked
    path or a planted name; after ``indexable`` returns no such folder remains; the verdict is right (secrets out, clean kept); and the
    repository holds no new file."""
    held_a, held_b = secret("cloud-access-key", 31, "folder"), secret("forge-token", 32, "folder")
    files = [(f"src/harbour-{n:02d}/ledger-page-{n:02d}.txt", clean_text(n, f"f{n:02d}"), False) for n in range(18)]
    files.insert(5, ("src/vault/first-vault-key.env", held_a.line(f"# {SW.TAG}s1\nKEY={{value}}\n"), True))
    files.insert(13, ("src/vault/second-vault-token.env", held_b.line(f"# {SW.TAG}s2\nTOKEN={{value}}\n"), True))
    tree = plant(box.base, "folder", files)
    tree.helds = [held_a, held_b]
    before = sorted(p.relative_to(tree.root).as_posix() for p in tree.root.rglob("*") if ".git" not in p.relative_to(tree.root).parts[:1])
    log = Path(box.base) / "folder-calls.log"
    tools = SW.recording_gitleaks(Path(box.base) / "tools-folder", log)
    after, run = judge(W.SRC, tree, box, "folder-after.json", tools=(tools,))
    kept = kept_of(after, "the folder case")
    noted = SW.calls(log)
    assert noted, "the plant did not take: no gitleaks call went through the recording program on PATH"
    folders = [call for call in noted if call["folder"] is not None]
    assert folders, (f"no gitleaks call was `gitleaks dir <folder>` ({len(noted)} calls, first arguments "
                     f"{sorted({tuple(c['args'][:1]) for c in noted})}): the texts are not written to a batch folder")
    root = tree.root.resolve()
    words = {str(tree.root), str(root)} | set(tree.paths) | {Path(rel).name for rel in tree.paths} | {Path(rel).parent.name for rel in tree.paths}
    for call in folders:
        where = Path(call["folder"])
        assert call["isdir"], f"the argument after dir is not a folder: {where}"
        assert not where.resolve().is_relative_to(root) and not str(where).startswith(str(tree.root)), f"the batch folder {where} is inside the root scanned"
        assert call["mode"] == 0o700, f"the batch folder {where} has mode {oct(call['mode'])}, not 0700"
        for name, mode in call["entries"]:
            assert mode & 0o077 == 0, f"the batch entry {name!r} has mode {oct(mode)}: readable beyond its owner"
            hits = sorted(word for word in words if word and word in name)
            assert not hits, f"the batch entry {name!r} holds a repository name: {hits!r}"
    left = sorted({c["folder"] for c in folders if Path(c["folder"]).exists()})
    assert not left, f"{len(left)} batch folder(s) remain after indexable returned: {left[:2]}"
    assert not (set(kept) & tree.secret), "a file with a planted secret is kept"
    assert set(tree.paths) - tree.secret <= set(kept), "a clean file is left out"
    now = sorted(p.relative_to(tree.root).as_posix() for p in tree.root.rglob("*") if ".git" not in p.relative_to(tree.root).parts[:1])
    assert now == before, f"the scan wrote into the repository: {sorted(set(now) - set(before))[:4]}"
    assert_no_value(tree, box, [run], "the folder case", log)


def test_s27_a_temporary_folder_inside_the_root_is_refused_by_name_and_nothing_is_written_there(box):
    """success-S27 (interface item 2; F2): with ``TMPDIR`` naming an empty folder inside the root being scanned (``scan-tmp/``), where
    ``mkdtemp`` would make the batch folder, ``indexable`` raises ``RuntimeError`` naming that folder, and ``scan-tmp/`` stays empty: no text
    of the repository is copied inside it."""
    held = secret("cloud-access-key", 41, "inside")
    files = [(f"src/plain/f{n:02d}.txt", clean_text(n), False) for n in range(6)]
    files.append(("src/keys/inside.env", held.line("KEY={value}\n"), True))
    tree = plant(box.base, "inside", files)
    tree.helds = [held]
    inside = tree.root / "scan-tmp"
    inside.mkdir()
    answer, run = judge(W.SRC, tree, box, "inside.json", TMPDIR=str(inside))
    left = sorted(p.relative_to(inside).as_posix() for p in inside.rglob("*"))
    assert not left, f"the scan wrote {len(left)} entries inside the root's scan-tmp/: {left[:4]}"
    assert answer["raised"] == "RuntimeError", (f"with TMPDIR inside the root, indexable did not raise RuntimeError "
                                                f"(raised {answer['raised']}; kept {len(answer['kept'] or [])} of {len(tree.paths)})")
    assert "scan-tmp" in (answer["message"] or ""), f"the RuntimeError does not name the folder: {answer['message']!r}"
    assert_no_value(tree, box, [run], "TMPDIR inside the root")


# ------------------------------------------------------------------------------------------------------------
# A large file: secrets across 100,000-byte multiples and near piece edges
# ------------------------------------------------------------------------------------------------------------

LARGE_SIZE = 1_200_000
LARGE_AT = [5, 99_990, 100_000, 200_003, 196_608, 500_000, 120_000, 133_056, 999_998, 1_000_000, 1_048_576, None]   # None: the very end


def large_text(size: int, number: int) -> str:
    line = f"row {number:02d} of the harbour ledger, a clean line of the long table\n"
    return (line * (size // len(line) + 1))[:size]


def test_s27_a_large_file_with_secrets_across_chunk_and_piece_edges_gets_the_one_per_file_forms_verdict(box, before_src):
    """success-S27: twelve files of 1.2 MB, each holding one planted secret (a cloud key or a forge token, alternately) whose value straddles
    a place where a reader may cut (bytes 100,000, 200,003, 500,000, 1,000,000, 1,048,576 and their neighbours; 65,536 x 3; 24,000 x 5;
    14,784 x 9), at the very start, or at the very end with no trailing newline; one clean file of 1.3 MB and three small clean files. The
    one-per-file form leaves out every secret file and keeps the clean ones; this worktree's ``indexable`` answers the same."""
    files, helds = [], []
    for number, at in enumerate(LARGE_AT):
        held = secret("cloud-access-key" if number % 2 == 0 else "forge-token", 50 + number, "large")
        helds.append(held)
        text = large_text(LARGE_SIZE, number)
        value = held.line("{value}")
        if at is None:
            data = text + " KEY=" + value
        else:
            place = max(0, at - len(value) // 2 - 5)
            data = text[:place] + " KEY=" + value + " " + text[place:]
        files.append((f"src/large/big-{number:02d}.txt", data, True))
    files.insert(6, ("src/large/clean-big.txt", large_text(1_300_000, 99), False))
    files += [(f"src/plain/f{n:02d}.txt", clean_text(n), False) for n in range(3)]
    tree = plant(box.base, "large", files)
    tree.helds = helds
    before_kept = oracle(before_src, tree, box, "large")
    after, run = judge(W.SRC, tree, box, "large-after.json")
    assert_own_verdicts(kept_of(after, "large files"), before_kept, tree, "large files")
    assert_no_value(tree, box, [run], "large files")


# ------------------------------------------------------------------------------------------------------------
# The assessment's scan on the P1R-1 curl pair
# ------------------------------------------------------------------------------------------------------------

def test_s27_the_assessments_scan_names_the_curl_credential_file_of_the_p1r_1_pair_by_rule_id_only(box, host):
    """success-S27 (interface item 1: the assessment uses the same core; F6): the orchard of the S1 cases with the P1R-1 curl pair committed
    beside its secret, ``config/10-health.md`` (ends in a bare ``curl`` line) just before ``config/11-deploy.sh`` (the real ``curl -u``, then
    the allowlisted one) in path order, so in one batch of the assessment. ``gov adopt --lite --stage MA`` lists
    ``{path: config/11-deploy.sh, rule: curl-auth-user}`` in the record's ``secrets`` (and the orchard's own secret file still), never
    ``config/10-health.md``; neither secret's value is in any file under ``--out`` or in what the run printed."""
    a, b, held, rule = curl_pair(0, "assess", False)
    orchard = W.plant_orchard(box.base, "orchard-p1r", files={"config/10-health.md": a, "config/11-deploy.sh": b}, big=False)
    out = Path(box.base) / "ma-out"
    run = W.run_adopt(orchard.root, W.env(box, host), "MA", "--out", str(out))
    W.assert_offered(run, "MA")
    W.assert_ok(run, "the memory assessment (MA) on the orchard with the P1R-1 curl pair")
    secrets = W.listed(W.read_json(out / W.ASSESSMENT), "secrets")
    for entry in secrets:
        assert set(entry) == {"path", "rule"}, f"a secrets item is {{path, rule}} and nothing else: {sorted(entry)}"
    named = {(entry["path"], entry["rule"]) for entry in secrets}
    assert ("config/11-deploy.sh", rule) in named, (f"the assessment does not name config/11-deploy.sh by {rule}: the curl credential was "
                                                   f"swallowed by a match from config/10-health.md (P1R-1); secrets listed: {sorted(named)}")
    assert not any(path == "config/10-health.md" for path, _rule in named), "the assessment names config/10-health.md (clean alone)"
    assert any(path == W.PLANT["secret"] for path, _rule in named), f"the orchard's own secret file is no longer named: {sorted(named)}"
    texts = W.all_text(out, runs=(run,))
    for each in (held, orchard.secret):
        W.assert_no_secret(each, texts, "the assessment's outputs")

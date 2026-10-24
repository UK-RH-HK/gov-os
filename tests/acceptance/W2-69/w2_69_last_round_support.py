"""Support code for the W2-69 cases of the last round, from the second review and DEC-909 (DEC-136).

Public interfaces only, as in ``w2_69_support``: the check's declared command (``python3 -m gov.secrets``), the
pre-index filter ``gov.secrets.indexable(root, paths)`` called in a child process of its own (DEC-285), ``gov rebuild
--json`` in a temporary project, gitleaks itself for the premises, and the first batch's stand-in gitleaks, first on
``PATH`` in a learning run only.

Every planted key block and token is built at run time from parts and hashed characters; none stands whole in a file
of this suite, and none is printed or logged here.
"""

from __future__ import annotations

import codecs
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import w2_69_review_support as review
import w2_69_support as support

R = support.RUNTIME

# --------------------------------------------------------------------------
# Key blocks of 9 to 24 KB (behaviours 1 and 2)
# --------------------------------------------------------------------------

# Just above the 9,216 bytes the check's pieces overlap by today; a PGP RSA-4096 export with two subkeys (about
# 10.4 KB) and with three (about 13.6 KB); an RSA-16384 PEM key and more (18,000); 24,000; and 24 KiB, the stricter
# reading of "24 KB" (DEC-909 item 2), as the top.
SIZES = (9_300, 10_650, 13_900, 18_000, 24_000, 24_576)
SHAPES = review.SHAPES
TEXT = 200 * 1024             # a long document: hundreds of kilobytes
FIRST_READ_END = 60_000       # "well past the first 60 KB": gitleaks' first read of the check's input ends before it
REGULAR_START, REGULAR_STEP, REGULAR_COUNT = 70_000, 307, 52    # 52 offsets over 15,657 bytes, past the first read
LAYOUTS = {"paragraphs": "blank", "no-blank-lines": "lines"}


def block(shape, size, seed, sheltered=False):
    return review.key_block(shape, size, seed, sheltered=sheltered)


def block_lines(text):
    """The body lines of a block that are long enough to stand for it (a store holding one holds the block's text)."""
    return [line for line in text.splitlines() if len(line) >= 48 and "-----" not in line]


@dataclass(frozen=True)
class Marks:
    """Where the parts of a key block lie, as offsets from its first byte."""
    size: int
    begin: int    # bytes of the BEGIN line, its newline included (and the armour's blank line)
    end: int      # bytes of the END line


def marks(text):
    first = text.index("\n") + 1
    if text[first:first + 1] == "\n":     # the armour's blank line after a PGP block's header
        first += 1
    return Marks(len(text), first, len(text) - text.rindex("\n") - 1)


def boundary_offsets(text, near=False):
    """Where a place (a split of the check, a read of gitleaks) falls inside the block, as offsets from its first
    byte: at its very start (0), on its BEGIN line (1, 2, 5, its middle, its newline, the byte after it), at eight
    points spread over its body, on its END line (the newline before it, its first byte, 5 bytes in, its middle, its
    last byte) and at its very end (the block's size): 21. ``near`` keeps five of them (a place near the start of the
    text, inside gitleaks' first read)."""
    m = marks(text)
    body_start, body_end = m.begin, m.size - m.end
    if near:
        return sorted({0, m.begin - 1, m.size // 2, body_end, m.size})
    begin_line = {0, 1, 2, 5, (m.begin - 1) // 2, m.begin - 1, m.begin}
    body = {body_start + round(j * (body_end - body_start) / 9) for j in range(1, 9)}
    end_line = {body_end - 1, body_end, body_end + 5, body_end + m.end // 2, m.size - 1}
    return sorted(begin_line | body | end_line | {m.size})


def place_block(layout, content, at, data):
    """``content`` with the block ``data`` beginning at ``at``: in paragraph text a paragraph of its own (a blank
    line before and after it), elsewhere a line of its own; at the very start or end of the text, nothing before
    or after it. None when it does not fit."""
    before = b"" if at == 0 else (b"\n\n" if layout == "paragraphs" else b"\n")
    after = b"" if at + len(data) == len(content) else (b"\n\n" if layout == "paragraphs" else b"\n")
    return support.place(content, at, data, before=before, after=after)


# --------------------------------------------------------------------------
# Where the check (or the filter) cuts its input, and where gitleaks reads it
# --------------------------------------------------------------------------

@dataclass
class Cuts:
    """Places of the content, as a learning run showed them: where a piece of the content the check gave gitleaks
    ends (``ends``) or begins (``starts``) with the content not going on across it, and where gitleaks begins a read
    inside an input (``reads``: the pipe's and a file's measured reads, mapped to the content)."""
    ends: list
    starts: list
    reads: list
    inputs: int

    def kind(self, place):
        names = [name for name, bucket in (("a piece's end", self.ends), ("a piece's start", self.starts),
                                           ("a read of gitleaks", self.reads)) if place in bucket]
        return " and ".join(names) or "a regular step"

    def chosen(self, length, margin, far_cap=2):
        """One place near the start of the text (before gitleaks' first read ends), and up to two well past it: a
        piece's end and a piece's start (or a read of gitleaks), from 110,000 and 140,000 bytes on."""
        every = sorted(set(self.ends) | set(self.starts) | set(self.reads))
        near = [p for p in every if 16_000 <= p < FIRST_READ_END]
        far_ends = [p for p in sorted(set(self.ends) | set(self.reads)) if 110_000 <= p <= length - margin]
        far_starts = [p for p in sorted(set(self.starts) | set(self.reads)) if 140_000 <= p <= length - margin]
        far = []
        for bucket in (far_ends, far_starts)[:far_cap]:
            for p in bucket:
                if all(abs(p - q) > 4_000 for q in far):
                    far.append(p)
                    break
        return near[:1], far


def cuts_of(inputs, content):
    ends, starts, reads, holding = set(), set(), set(), 0
    for data in inputs:
        runs = support._runs(data, content)
        if not runs:
            continue
        holding += 1
        for (_i1, c1, n1), (_i2, c2, _n2) in zip(runs, runs[1:]):
            # The content does not go on (it starts again further back, or skips ahead): a piece ends here and one
            # begins. A step of a few bytes is a byte put in or taken out between the stretches, not a cut.
            if not c1 + n1 - 16 <= c2 <= c1 + n1 + 2:
                ends.add(c1 + n1)
                starts.add(c2)
        for first in (support.FIRST_READ_PIPE, support.FIRST_READ_FILE):
            for position in support.gitleaks_read_starts(data, first):
                for i, c, n in runs:
                    if i <= position < i + n:
                        reads.add(c + position - i)
                        break
    for edge in (0, len(content)):
        ends.discard(edge)
        starts.discard(edge)
    return Cuts(sorted(ends), sorted(starts), sorted(reads), holding)


def learn_check(sandbox, project, stand_in, rel, write_case, content):
    """A learning run of the check: the clean text alone in the runtime folder, the stand-in keeping each input. The
    clean text must be green; it stays, as a control of the next run."""
    write_case(project / rel)
    run = support.run_with_stand_in(sandbox, project, stand_in, keep=True)
    assert run.returncode == 0, f"premise: the clean text {rel} is green\n{run.describe()}"
    inputs = stand_in.inputs()
    shutil.rmtree(stand_in.kept, ignore_errors=True)
    assert inputs, f"the stand-in gitleaks on PATH was given nothing: the check did not run it\n{run.describe()}"
    cuts = cuts_of(inputs, bytes(content))
    assert cuts.inputs, f"no input the check gave gitleaks held the clean text {rel}\n{run.describe()}"
    return cuts


# --------------------------------------------------------------------------
# The pre-index filter, called in a child process with this worktree's code (DEC-732)
# --------------------------------------------------------------------------

_FILTER = ("import json, sys\nfrom gov.secrets import indexable\n"
           "print(json.dumps(indexable(sys.argv[1], json.loads(sys.stdin.read()))))\n")


@dataclass
class FilterRun:
    returncode: int | None
    returned: list
    stderr: str
    seconds: float

    def describe(self, tail=1200):
        return (f"the filter's exit code: {self.returncode} after {self.seconds:.1f} s; paths returned: "
                f"{len(self.returned)}\nstderr (tail):\n{self.stderr[-tail:]}")


def run_filter(sandbox, project, paths, env=None, timeout=900):
    """``gov.secrets.indexable(project, paths)`` in a child process; what it returns (DEC-285)."""
    env = env or support.base_environment(sandbox)
    began = time.monotonic()
    try:
        done = subprocess.run([sys.executable, "-c", _FILTER, str(project)], input=json.dumps(list(paths)),
                              capture_output=True, text=True, env=env, cwd=str(project), timeout=timeout)
    except subprocess.TimeoutExpired:
        return FilterRun(None, [], "the filter did not end", time.monotonic() - began)
    returned = []
    if done.returncode == 0:
        try:
            returned = json.loads(done.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            returned = []
    return FilterRun(done.returncode, returned, done.stderr, time.monotonic() - began)


def filter_project(sandbox, name="filter-project", gitleaks_toml=None):
    """A committed project whose ``docs/**`` and ``src/**`` are governance memory (the filter's source folders),
    with the kernel's gitleaks rules (or ``gitleaks_toml``)."""
    project = sandbox.base / name
    project.mkdir(parents=True)
    support.write(project / ".gitignore", ".gov-runtime/\n__pycache__/\n")
    if gitleaks_toml is None:
        shutil.copy2(support.GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    else:
        support.write(project / ".gitleaks.toml", gitleaks_toml)
    support.write(project / "governance/project/path-map.yaml",
                  support.path_map_text({"docs": ["docs/**"], "src": ["src/**"]}))
    support.write(project / "docs/readme.md", "# A project of the W2-69 tests\n")
    support.git(project, "init", "-q", "-b", "main")
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "W2-69 filter fixture")
    return project


def spread(points, cap):
    """Up to ``cap`` of ``points``, spread evenly over them (the first and the last among them)."""
    points = sorted(set(points))
    if len(points) <= cap:
        return points
    return sorted({points[round(j * (len(points) - 1) / (cap - 1))] for j in range(cap)}) if cap > 1 else points[:1]


def lexical_files(project):
    """{path: indexed} of the lexical index's ``lexical_file`` table (every tracked file it judged, indexed or not),
    and the paths that have chunks."""
    store = Path(project) / R / "store.db"
    connection = sqlite3.connect(f"file:{store}?mode=ro", uri=True)
    try:
        judged = {path: indexed for path, _blob, indexed in connection.execute("SELECT * FROM lexical_file")}
        chunked = {path for (path,) in connection.execute("SELECT DISTINCT path FROM lexical_chunk")}
    finally:
        connection.close()
    return judged, chunked


def cells(layout, word, phase, size, q=24):
    """``size`` bytes: ``phase`` bytes of padding, then ``word`` in cells of ``q`` bytes, laid out as ``layout`` (the
    first batch's K2 cells, ``test_w2_69_word_internal_fragments.cells``)."""
    pad = "_" if layout == "longword" else " "
    out, total, count = [pad * phase], phase, 0
    while total + q <= size:
        if layout == "oneline":
            cell = word.ljust(q)
        elif layout == "lines":
            cell = word.ljust(q - 1) + "\n"
        elif layout == "blank":
            cell = word.ljust(q - 2) + ("\n\n" if count % 8 == 7 else " \n")
        elif layout == "longword":
            cell = word.ljust(q, "_") if count % 512 != 511 else word.ljust(q - 1, "_") + " "
        else:
            raise ValueError(layout)
        out.append(cell)
        total += q
        count += 1
    out.append(pad * (size - total))
    return "".join(out)


def gitleaks_finds_each(texts, config_text, scratch):
    """{name: the rule ids gitleaks finds in that text}, for many texts in one run of ``gitleaks dir`` (each file is
    judged on its own). Raises if gitleaks does not decide. The report's matches are redacted and never kept."""
    folder = Path(tempfile.mkdtemp(prefix="w2-69-premise-", dir=scratch))
    try:
        for name, text in texts.items():
            support.write(folder / f"{name}.txt", text)
        env = dict(os.environ, GITLEAKS_CONFIG_TOML=config_text)
        env.pop("GITLEAKS_CONFIG", None)
        done = subprocess.run([support.REAL_GITLEAKS, "dir", str(folder), "--no-banner", "--redact", "--log-level",
                               "error", "--ignore-gitleaks-allow", "--exit-code", "3", "--report-format", "json",
                               "--report-path", "-"], capture_output=True, env=env, timeout=300)
        if done.returncode not in (0, 3):
            raise AssertionError(f"gitleaks did not decide a premise (exit code {done.returncode})")
        found = {name: set() for name in texts}
        for entry in json.loads(done.stdout or b"[]") if done.returncode == 3 else []:
            found[Path(entry["File"]).stem].add(entry["RuleID"])
        return {name: sorted(rules) for name, rules in found.items()}
    finally:
        shutil.rmtree(folder, ignore_errors=True)


PROJECT_RULES = ("gov-canary", "gov-token-digit", "gov-token-lower", "gov-token-upper")


def learn_filter(sandbox, project, stand_in, rel, content):
    """A learning run of the filter on the clean text alone, the stand-in gitleaks keeping each input. The clean text
    must be returned (the control)."""
    support.write(project / rel, bytes(content))
    stand_in.set(keep=True)
    run = run_filter(sandbox, project, [rel], env=stand_in.environment(sandbox))
    stand_in.set()
    assert run.returncode == 0 and run.returned == [rel], (
        f"control: the filter does not return a clean text of a source folder ({rel})\n{run.describe()}")
    inputs = stand_in.inputs()
    shutil.rmtree(stand_in.kept, ignore_errors=True)
    assert inputs, f"the stand-in gitleaks on PATH was given nothing: the filter did not run it\n{run.describe()}"
    cuts = cuts_of(inputs, bytes(content))
    assert cuts.inputs, f"no input the filter gave gitleaks held the clean text {rel}\n{run.describe()}"
    return cuts


# --------------------------------------------------------------------------
# Stored forms that hold a long text whole in one value (the first batch's K1 forms)
# --------------------------------------------------------------------------

def _wal_store(path, text):
    """A store in WAL mode whose row is committed in its log only: copied, with its log, while the connection that
    wrote it is still open (a close would checkpoint the log into the store)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=path.parent, prefix=".wal-build-") as folder:
        built = Path(folder) / "wal.db"
        connection = sqlite3.connect(built, isolation_level=None)
        try:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA wal_autocheckpoint = 0")
            connection.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)")
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            connection.execute("INSERT INTO notes (body) VALUES (?)", (text,))
            shutil.copyfile(built, path)
            shutil.copyfile(str(built) + "-wal", str(path) + "-wal")
        finally:
            connection.close()
    return path


def _sqlite_value(path, text):
    support.long_value_store(path, text)


# form: (file extension, writer of a text). The writer is given the text as str.
FORMS = {
    "plain-file": (".txt", lambda path, text: support.write(path, text)),
    "sqlite-value": (".db", _sqlite_value),
    "a-plain-file-with-zero-bytes": (".bin", lambda path, text: support.write(path, b"\0\1\2\3" + text.encode()
                                                                               + b"\0\0\7")),
    "a-utf16le-plain-file-with-a-bom": (".txt", lambda path, text: support.write(path, codecs.BOM_UTF16_LE
                                                                                  + text.encode("utf-16-le"))),
    "a-utf16le-plain-file": (".txt", lambda path, text: support.write(path, text.encode("utf-16-le"))),
    "a-utf16be-plain-file": (".txt", lambda path, text: support.write(path, text.encode("utf-16-be"))),
    "a-text-value-in-an-integer-column": (".db", lambda path, text: support.sqlite_store(
        path, ["CREATE TABLE counts (id INTEGER PRIMARY KEY, n INTEGER)"],
        [("INSERT INTO counts (n) VALUES (?)", (text,))])),
    "a-value-of-a-table-without-rowid": (".db", lambda path, text: support.sqlite_store(
        path, ["CREATE TABLE notes (path TEXT PRIMARY KEY, body TEXT) WITHOUT ROWID"],
        [("INSERT INTO notes VALUES (?, ?)", ("docs/a.md", text))])),
    "a-value-in-a-full-text-index": (".db", lambda path, text: support.fts_store(path, text)),
    "a-blob-of-its-bytes": (".db", lambda path, text: support.blob_store(path, text.encode())),
    "a-blob-of-utf16le-bytes": (".db", lambda path, text: support.blob_store(path, text.encode("utf-16-le"))),
    "a-blob-of-utf16be-bytes": (".db", lambda path, text: support.blob_store(path, text.encode("utf-16-be"))),
    "a-utf16le-store": (".db", lambda path, text: support.long_value_store(path, text, encoding="UTF-16le")),
    "a-utf16be-store": (".db", lambda path, text: support.long_value_store(path, text, encoding="UTF-16be")),
    "the-write-ahead-log": (".db", _wal_store),
}


def staged_rel(number):
    """A staged copy, where the code index stages the files the filter returns (``.gov-runtime/codeintel/files/``)."""
    return f"{R}/codeintel/files/docs/notes-{number:05d}.md"


# --------------------------------------------------------------------------
# A sweep: every placement one file or store, judged by one run of the check
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Placement:
    shape: str
    size: int
    place: int | None   # the learned place the block lies across, or None (a regular step, or the text's edge)
    at: int             # where the block begins in the text

    def data(self, layout, content, blocks):
        return place_block(layout, content, self.at, blocks[(self.shape, self.size)].encode())


def report(what, missed, total, cuts, judge="the check"):
    """A miss report: positions and sizes only, never a block's content."""
    lines = []
    for (shape, size, place), offsets in sorted(missed.items(), key=lambda item: (item[0][0], item[0][1],
                                                                                   item[0][2] or -1)):
        if place is None:
            lines.append(f"  {shape}, a block of {size} bytes, beginning at content offsets {sorted(offsets)} "
                         f"(regular steps past the first read, or the text's own start or end)")
        else:
            lines.append(f"  {shape}, a block of {size} bytes across content offset {place} ({cuts.kind(place)}): "
                         f"the place at {sorted(offsets)} bytes into the block")
    return f"{what}: {judge} missed {sum(map(len, missed.values()))} of {total} key blocks:\n" + "\n".join(lines)


def _fits(layout, content, at, size):
    """Whether ``place_block`` puts a block of ``size`` bytes at ``at`` (its separators included)."""
    gap = 2 if layout == "paragraphs" else 1
    before = 0 if at == 0 else gap
    after = 0 if at + size == len(content) else gap
    return at - before >= 0 and at + size + after <= len(content)


def few_offsets(text):
    """Ten of the boundary offsets (the forms swept with fewer placements, DEC-221): the very start, the BEGIN line,
    the body at a quarter, the middle and three quarters, the END line, the very end."""
    m = marks(text)
    body_end = m.size - m.end
    return sorted({0, 2, m.begin - 1, m.begin + (body_end - m.begin) // 4, m.size // 2,
                   m.begin + 3 * (body_end - m.begin) // 4, body_end, body_end + 5, m.size - 1, m.size})


def placements(layout, content, blocks, cuts, regular="each", edges=True, near_too=True, offsets=None, far_cap=2,
               count=REGULAR_COUNT, step=REGULAR_STEP, shift=0):
    """Every placement of every block (``blocks``: {(shape, size): text}): across the learned places (one near the
    start, up to ``far_cap`` well past the first read) at the boundary offsets (``offsets``: a function of the
    block's text, else ``boundary_offsets``); at ``count`` regular steps of ``step`` bytes from ``REGULAR_START``
    (past the first read), for each block (``regular`` is "each") or one block a step in turn ("rotating", from the
    ``shift``-th); at the text's very start and very end."""
    near, far = cuts.chosen(len(content), max(SIZES) + 8, far_cap) if cuts else ([], [])
    out = []
    keys = list(blocks)
    for key, text in blocks.items():
        shape, size = key
        for place in (near if near_too else []) + far:
            if offsets:
                chosen = offsets(text)
            elif place in near:
                chosen = boundary_offsets(text, near=True)
            else:   # the first place well past the first read at 21 offsets, the second at ten (DEC-221)
                chosen = boundary_offsets(text) if place == far[0] else few_offsets(text)
            for offset in chosen:
                if _fits(layout, content, place - offset, size):
                    out.append(Placement(shape, size, place, place - offset))
        if edges:
            for at in (0, len(content) - size):
                out.append(Placement(shape, size, None, at))
    for k in range(count):
        at = REGULAR_START + k * step
        for key in (keys if regular == "each" else [keys[(k + shift) % len(keys)]]):
            if _fits(layout, content, at, key[1]):
                out.append(Placement(key[0], key[1], None, at))
    return out


def misses(found, rels, cases):
    """The placements whose file or store ``found`` says no: {(shape, size, place): [offsets into the block, or
    where the block begins]}."""
    missed = {}
    for rel, case in zip(rels, cases):
        if not found(rel):
            key = (case.shape, case.size, case.place)
            missed.setdefault(key, []).append(case.place - case.at if case.place is not None else case.at)
    return missed


def printed_a_block(text, blocks):
    return any(line in text for each in blocks.values() for line in block_lines(each)[:3])

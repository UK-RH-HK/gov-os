"""The pre-index secret filter and the secrets-indexing check (W1-15; DEC-285 to DEC-290).

``indexable(root, paths)`` is what every indexer calls before chunking: it returns
the paths the indexer may read. ``stores_with_secrets(root)`` is the subject of the
secrets-indexing family check. ``path_holds_secret(root, path)`` judges a path name,
for an index that stores paths (DEC-339). All run the gitleaks binary with the rules of the
project's ``.gitleaks.toml`` (DEC-287) over content given on standard input, so a
path allowlist never applies (DEC-290) and no report is written. The file's other
allowlists and its disabled rules are left out of the scan (DEC-298), and a second scan with
the file's rules alone keeps the allowlist of gitleaks' defaults from sheltering them
(DEC-347). Whatever cannot be decided raises or is left out; nothing is let through undecided.

Each gitleaks run may take a minute plus a second a megabyte, so a store is decided whenever gitleaks
reads at 1 MB/s or faster (DEC-853). A store whose bytes were scanned clean before, by the same rule sets
and the same gitleaks, is not scanned again: the check's record of clean results says so, and the reuse
is labelled on standard error with the store's path and digest. A finding is never recorded.

What gitleaks reads (DEC-897, docs/research/W2-69-secrets-scan.md): a SQLite store is judged by each value it
holds and by each region of its freed space, each on its own; any other file, or a store that cannot be read, by
its bytes. Each is given in overlapping pieces that begin and end at a true boundary, a blank line after each, so
that gitleaks begins a read only where the text itself could begin a match, and a token across a cut is still
seen whole in one piece.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gov.config.loader import load_config
from gov.guard.runs import root as runs_root

CONFIG_REL = ".gitleaks.toml"
RUNTIME_REL = ".gov-runtime"
RECORD_REL = f"{RUNTIME_REL}/secrets-clean.json"  # the clean results, by digest (DEC-853)
GOVERNANCE = "governance"
_LEAKS, _TIMEOUT_S = 3, 60
_FLOOR = 1_000_000  # bytes a second: the slowest gitleaks a store must still be decided at (DEC-853)
_LARGE = 64 << 20  # a file of this size or more is read and scanned at most two at a time, for memory
_FORM = 4  # the form of the record and of what a scan reads; another form is never trusted
# gitleaks reads standard input in fragments that end at the first blank line within 25,000 bytes of a read: a piece
# is shorter, so every fragment begins at a piece's start. Pieces overlap, so a match up to the overlap is whole in one:
# 9 KiB holds a private-key block of 8,192 bytes (an RSA 8192 key).
_PIECE, _OVERLAP = 24_000, 9_216
# A BEGIN...END key block (PEM or armoured PGP) of up to 24 KiB, from its BEGIN marker to its END marker, also goes as
# a piece of its own (DEC-909), so it is whole in one read wherever the pieces are cut. A larger block is read as the
# rest of the text is (row W2-L419). A key piece begins and ends with a dash, no word byte, so no read seems to begin or
# end a word there; its blank lines get a form feed as the rest do, and it stays under gitleaks' peek of 25,000 bytes.
_BLOCK, _BLOCK_READ = 24_576, 24_900
_BEGIN = re.compile(rb"-----BEGIN", re.IGNORECASE)
_END = re.compile(rb"-----END[ A-Za-z0-9_-]{0,100}?-----", re.IGNORECASE)
_SPACES = tuple(bytes([byte]) for byte in b" \t\n\v\f\r")
_LAST_NON_WORD = re.compile(rb"(?s:.*)[^0-9A-Za-z_]")
_INSIDE = b"_"  # stands for the rest of a word cut where no boundary was found, so no read seems to begin a word
# A blank line of the text gets a form feed, a space to the rules but none to gitleaks' reads: so no read ends inside
# a piece, and a match across a blank line (an armoured PGP key) is whole in one read.
_BLANK = re.compile(rb"(\n[ \t\r]*)(?=\n)")
_SQLITE = b"SQLite format 3\0"
_BUSY_S = 10.0  # how long a store's lock held by another process is waited out before the store is judged by its bytes
_FTS5 = re.compile(rb"\s*CREATE\s+VIRTUAL\s+TABLE\b.*?\bUSING\s+fts5\b", re.IGNORECASE | re.DOTALL)

__all__ = ["indexable", "path_holds_secret", "stores_with_secrets"]


def _toml(value) -> str:
    """``value`` as one TOML value: tables inline, the rest as JSON writes it."""
    if isinstance(value, dict):
        return "{" + ", ".join(f"{json.dumps(key)} = {_toml(item)}" for key, item in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_toml(item) for item in value) + "]"
    return json.dumps(value, ensure_ascii=False)


def _rules(root: Path) -> tuple[str, ...]:
    """The rules of ``.gitleaks.toml`` as TOML, without what shelters a secret (DEC-298).

    Allowlists, of the file and of each rule, and disabled rules are left out. Raises unless
    the file holds rules: a scan without rules finds nothing, which is no verdict. Where the file
    extends other rules, its own rules follow alone as a second configuration (DEC-347): the
    allowlist of gitleaks' defaults, which ``extend`` lays over every rule, is not in it.
    """
    try:
        config = tomllib.loads((Path(root) / CONFIG_REL).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise RuntimeError(f"{CONFIG_REL} cannot be read: {error}") from None
    if not (config.get("rules") or config.get("extend", {}).get("useDefault") is True):
        raise RuntimeError(f"{CONFIG_REL} holds no rules: nothing can be decided")
    for table in (config, *config.get("rules", [])):
        table.pop("allowlist", None)
        table.pop("allowlists", None)
    config.get("extend", {}).pop("disabledRules", None)
    # A rule with no expression of its own only changes a rule it extends: alone, gitleaks refuses the file for it.
    alone = [rule for rule in config.get("rules", []) if rule.get("regex") or rule.get("path")]
    configs = [config, {"rules": alone}] if alone and "extend" in config else [config]
    return tuple("\n".join(f"{json.dumps(key)} = {_toml(item)}" for key, item in each.items()) for each in configs)


def _cut(chunk: bytes, low: int, high: int) -> tuple[int, bool]:
    """The last place in ``low..high`` just after a space, else just after a byte that is no word byte; else ``high``,
    with False: the cut is inside a word."""
    after = max(chunk.rfind(space, low - 1, high) for space in _SPACES)
    if after >= 0:
        return after + 1, True
    found = _LAST_NON_WORD.match(chunk, low - 1, high)
    return (found.end(), True) if found else (high, False)


def _key_blocks(chunk: bytes):
    """Each BEGIN...END key block of ``chunk`` of at most ``_BLOCK`` bytes, its blank lines kept from ending a read: from
    each BEGIN marker to the first END marker after it."""
    for begin in _BEGIN.finditer(chunk):
        end = _END.search(chunk, begin.end(), begin.start() + _BLOCK)
        if end is not None:
            block = _BLANK.sub(rb"\1\f", chunk[begin.start():end.end()])
            if len(block) <= _BLOCK_READ:
                yield block


def _pieces(chunk: bytes):
    """``chunk``, its blank lines kept from ending a read, in pieces of at most ``_PIECE`` bytes, each overlapping the
    next by at least ``_OVERLAP``; where it is longer than one piece, also each of its key blocks whole."""
    whole, chunk = chunk, _BLANK.sub(rb"\1\f", chunk)
    if len(chunk) > _PIECE:
        yield from _key_blocks(whole)
    start, lead = 0, b""
    while len(chunk) - start > _PIECE:
        end, edge = _cut(chunk, start + 2 * _OVERLAP, start + _PIECE)
        yield lead + chunk[start:end] + (b"" if edge else _INSIDE)
        start, edge = _cut(chunk, start + 1, end - _OVERLAP)
        lead = b"" if edge else _INSIDE
    yield lead + chunk[start:]


def _forms(content: bytes) -> list[bytes]:
    """``content`` as it is and, when it holds zero bytes (UTF-16 text), without them."""
    return [content, content.replace(b"\0", b"")] if b"\0" in content else [content]


def _holds_secret(rules: tuple[str, ...], content: bytes) -> bool:
    """Whether gitleaks finds a secret in ``content``, one text, by any of ``rules``."""
    return _scan(rules, _forms(content))


def _scan(rules: tuple[str, ...], chunks) -> bool:
    """Whether gitleaks finds a secret in any of ``chunks`` by any of ``rules``. Raises when gitleaks cannot run or does not decide.

    Each chunk is a text of its own: its pieces are never joined to another chunk's but by a blank line.
    """
    # The leading newline keeps gitleaks from skipping content it would take for a binary file.
    parts = [b"\n"]
    for chunk in chunks:
        for piece in _pieces(chunk):
            parts += (piece, b"\n\n")
    data = b"".join(parts)  # one copy, read by every scan
    # The rules go by the environment, so no file of them is written; a configuration path there would win over them.
    env = {key: value for key, value in os.environ.items() if key != "GITLEAKS_CONFIG"}
    for each in rules:  # clean only when every scan ran and found nothing
        done = subprocess.run(
            ["gitleaks", "stdin", "--no-banner", "--redact",
             "--ignore-gitleaks-allow", "--gitleaks-ignore-path", "/dev/null", "--log-level", "error",
             "--exit-code", str(_LEAKS)],
            input=data, capture_output=True, timeout=_TIMEOUT_S + len(data) / _FLOOR,
            env=env | {"GITLEAKS_CONFIG_TOML": each})
        if done.returncode not in (0, _LEAKS):
            raise RuntimeError(f"gitleaks could not scan with {CONFIG_REL} (exit code {done.returncode})")
        if done.returncode == _LEAKS:
            return True
    return False


def _matches(rel: str, pattern: str) -> bool:
    """``*`` stays inside one folder, ``**`` crosses folders (the language of the path map)."""
    parts = [re.escape(part).replace(r"\*", "[^/]*") for part in pattern.split("**")]
    return re.fullmatch(".*".join(parts), rel) is not None


def _governance(namespaces: dict, rel: str) -> bool:
    """Whether ``rel`` has a namespace and every namespace it matches is governance memory."""
    classes = [entry.get("memory_class") for entry in namespaces.values()
               if any(_matches(rel, pattern) for pattern in entry["paths"])]
    return bool(classes) and all(item == GOVERNANCE for item in classes)


def indexable(root: Path, paths: list[str]) -> list[str]:
    """The sub-list of ``paths`` an indexer may read, in the order asked (DEC-285)."""
    root = Path(root).resolve()
    rules = _rules(root)
    namespaces = load_config(root)["path-map.yaml"]["namespaces"]

    def allowed(rel: str) -> bool:
        try:  # a link is judged by what it points to: its namespace and its content
            real = (root / rel).resolve(strict=True)
            target = real.relative_to(root).as_posix()
            content = real.read_bytes()
        except (OSError, ValueError, RuntimeError):  # no file, a link loop, or a place outside the root
            return False
        if not (_governance(namespaces, rel) and _governance(namespaces, target)):
            return False
        return not _holds_secret(rules, content)

    with ThreadPoolExecutor() as pool:
        verdicts = list(pool.map(allowed, dict.fromkeys(paths)))
    return [rel for rel, verdict in zip(dict.fromkeys(paths), verdicts) if verdict]


def path_holds_secret(root: Path, path: str) -> bool:
    """Whether the name of ``path`` holds a secret: the whole path and each of its names, judged as content is."""
    return _holds_secret(_rules(root), os.fsencode("\n".join([path, *Path(path).parts])))


def _number(content: bytes, at: int, size: int) -> int:
    if at < 0 or at + size > len(content):
        raise ValueError("outside the file")
    return int.from_bytes(content[at:at + size])


def _varint(content: bytes, at: int) -> tuple[int, int]:
    """A SQLite variable-length integer at ``at``, and where it ends."""
    value = 0
    for step in range(9):
        byte = _number(content, at + step, 1)
        if step == 8:
            return (value << 8) | byte, at + 9
        value = (value << 7) | (byte & 0x7F)
        if byte < 0x80:
            return value, at + step + 1
    raise AssertionError


def _fts_terms(rowid: int, block: bytes) -> list[bytes] | None:
    """The terms of the FTS5 leaf page ``block`` (row ``rowid`` of an FTS5 ``_data`` table), each whole, without the
    byte that names its index. A page stores a term after the prefix it shares with the term before it, so its bytes
    hold that term's tail after a byte that is no word byte: read whole, a term begins where its text did.

    None where the block is no leaf page (the averages, the structure, a doclist index, tombstones) or does not parse.
    """
    segment = rowid >> 37
    if not 0 < segment < 1 << 16 or rowid >> 31 & 0x3F:  # a leaf: a segment's page, of height 0 and no doclist index
        return None
    try:
        footer = _number(block, 2, 2)  # where the page's term offsets begin
        if footer < 4:
            raise ValueError("no leaf page")
        terms, term, at, offset = [], b"", footer, 0
        while at < len(block):
            step, at = _varint(block, at)
            offset += step
            keep, cursor = (0, offset) if not terms else _varint(block, offset)
            size, cursor = _varint(block, cursor)
            if offset < 4 or keep > len(term) or cursor + size > footer:
                raise ValueError("a term out of its page")
            term = term[:keep] + block[cursor:cursor + size]
            terms.append(term[1:])
        return terms
    except ValueError:
        return None


def _freed(content: bytes) -> list[bytes]:
    """The freed space of the SQLite file ``content``, region by region: each freelist page, the unused tail of each
    freelist trunk and of each overflow chain's last page, and each b-tree page's freeblocks and unallocated gap;
    each also without its zero bytes, where it holds any (a UTF-16 store's deleted text).

    Raises ValueError where the file's structure does not hold.
    """
    size = _number(content, 16, 2)
    size = 65536 if size == 1 else size
    usable = size - content[20]
    if size < 512 or size & (size - 1) or len(content) % size or usable < 480:
        raise ValueError("no SQLite page layout")
    pages, seen, regions = len(content) // size, set(), []

    def take(number: int) -> bytes:  # a page off the b-tree: freelist or overflow, each taken once
        if not 1 <= number <= pages or number in seen:
            raise ValueError("a page out of the file or taken twice")
        seen.add(number)
        return content[(number - 1) * size:(number - 1) * size + usable]

    trunk = _number(content, 32, 4)
    while trunk:
        data = take(trunk)
        count = _number(data, 4, 4)
        if 8 + 4 * count > usable:
            raise ValueError("a freelist trunk overflows its page")
        regions += [data[8 + 4 * count:], *(take(_number(data, 8 + 4 * each, 4)) for each in range(count))]
        trunk = _number(data, 0, 4)
    most_index, least = (usable - 12) * 64 // 255 - 23, (usable - 12) * 32 // 255 - 23
    for number in range(1, pages + 1):
        base = (number - 1) * size
        at = base + (100 if number == 1 else 0)
        kind = content[at]
        if number in seen or kind not in (2, 5, 10, 13):
            continue
        head = 8 if kind in (10, 13) else 12
        cells, start = _number(content, at + 3, 2), _number(content, at + 5, 2) or 65536
        if not at + head + 2 * cells <= base + start <= base + usable:
            raise ValueError("a b-tree page's cells overlap")
        regions.append(content[at + head + 2 * cells:base + start])
        block = _number(content, at + 1, 2)
        while block:
            follow, length = _number(content, base + block, 2), _number(content, base + block + 2, 2)
            if block < start or block + length > usable or (follow and follow <= block):
                raise ValueError("a freeblock out of its page")
            regions.append(content[base + block + 4:base + block + length])
            block = follow
        for each in range(cells if kind != 5 else 0):  # a cell whose payload overflows: the tail of its chain's last page
            cell = base + _number(content, at + head + 2 * each, 2) + (4 if kind == 2 else 0)
            payload, cell = _varint(content, cell)
            if kind == 13:
                cell = _varint(content, cell)[1]
            most = usable - 35 if kind == 13 else most_index
            if payload <= most:
                continue
            local = least + (payload - least) % (usable - 4)
            local = least if local > most else local
            left, page = payload - local, _number(content, cell + local, 4)
            while left > usable - 4:
                left, page = left - (usable - 4), _number(take(page), 0, 4)
            regions.append(take(page)[4 + left:])
    return [form for region in regions if region.strip(b"\0") for form in _forms(region)]


def _store(path: Path) -> tuple[bytes, list[bytes], bool]:
    """The bytes of the file at ``path``, the texts it is judged by, and whether a clean verdict on them may be kept.

    A SQLite store is read under a shared lock, waited for up to ``_BUSY_S``, so its bytes and its values are of one
    state: it is judged by each value it holds, ``sqlite_master`` included (text as stored, a blob also without its
    zero bytes; an FTS5 index's pages by their terms, each whole), and by each region of its freed space. Any other
    file is judged by its bytes. So is a store that cannot be read, but a clean verdict on its bytes is not kept: once
    its values can be read, they are.
    """
    with open(path, "rb") as handle:
        if handle.read(len(_SQLITE)) != _SQLITE:
            content = path.read_bytes()
            return content, _forms(content), True
    connection = None
    try:
        connection = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True, timeout=_BUSY_S)
        connection.text_factory = bytes
        connection.execute("BEGIN")
        schema = connection.execute("SELECT type, name, tbl_name, sql FROM sqlite_master").fetchall()  # the shared lock
        content = path.read_bytes()
        chunks = [value for row in schema for value in row if value]
        indexes = {name.lower() + b"_data" for kind, name, _, sql in schema
                   if kind == b"table" and _FTS5.match(sql or b"")}
        for kind, name, _, sql in schema:  # a virtual table's rows are those of its own tables
            if kind == b"table" and not (sql or b"").upper().startswith(b"CREATE VIRTUAL"):
                quoted = name.decode("utf-8").replace('"', '""')
                if name.lower() in indexes:
                    for rowid, block in connection.execute(f'SELECT id, block FROM "{quoted}"'):
                        leaf = isinstance(rowid, int) and isinstance(block, bytes)
                        terms = _fts_terms(rowid, block) if leaf else None
                        chunks += (form for value in ([block] if terms is None else terms)
                                   if isinstance(value, bytes) for form in _forms(value))
                    continue
                for row in connection.execute(f'SELECT * FROM "{quoted}"'):
                    chunks += (form for value in row if isinstance(value, bytes) for form in _forms(value))
        return content, chunks + _freed(content), True
    except (sqlite3.Error, ValueError, IndexError):  # damaged, locked or no SQLite after all: judged by its bytes
        content = path.read_bytes()
        return content, _forms(content), False
    finally:
        if connection is not None:
            connection.close()


def _scanner(rules: tuple[str, ...]) -> str | None:
    """What decides a scan besides the content: the rule sets, the gitleaks ``PATH`` finds, and the scan's form.

    None when no gitleaks is found; the scan then raises, and nothing is reused or recorded.
    """
    found = shutil.which("gitleaks")
    if found is None:
        return None
    with open(found, "rb") as handle:
        binary = hashlib.file_digest(handle, "sha256").hexdigest()
    return hashlib.sha256(json.dumps([_FORM, list(rules), binary]).encode()).hexdigest()


def _check(body: dict) -> str:
    """The digest a record carries of its own body: a record damaged in any way no longer matches it."""
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def _trusted(root: Path, scanner: str | None) -> set[str]:
    """The digests of the bytes the record holds as clean for ``scanner``.

    Empty when the record is missing, unreadable, damaged, of another form or of another scanner: then every store is scanned.
    """
    if scanner is None:
        return set()
    try:
        record = json.loads((root / RECORD_REL).read_text(encoding="utf-8"))
        body = {key: record[key] for key in ("form", "scanner", "clean")}
        if (set(record) != {*body, "check"} or record["check"] != _check(body) or body["form"] != _FORM
                or body["scanner"] != scanner or not isinstance(body["clean"], list)
                or not all(isinstance(each, str) and re.fullmatch("[0-9a-f]{64}", each) for each in body["clean"])):
            return set()
    except (OSError, ValueError, KeyError, TypeError):
        return set()
    return set(body["clean"])


def _record(root: Path, scanner: str, clean: set[str]) -> None:
    """Replaces the record in one step, so an interrupted run leaves the old record or the new one, never part of one.

    A record that cannot be written is left out: the next run scans in full.
    """
    body = {"form": _FORM, "scanner": scanner, "clean": sorted(clean)}
    path = root / RECORD_REL
    temporary = None
    try:
        handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=".secrets-clean.", suffix=".part")
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(body | {"check": _check(body)}))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError:
        if temporary is not None:
            with contextlib.suppress(OSError):
                os.unlink(temporary)


def stores_with_secrets(root: Path) -> list[str]:
    """Every file under ``.gov-runtime/`` whose content holds a secret, as project-relative paths (DEC-290)."""
    root = Path(root)
    rules = _rules(root)
    if not os.path.lexists(root / RUNTIME_REL):
        return []

    def refuse(error: OSError) -> None:
        raise error  # a folder that cannot be entered is not a store without a secret

    # DEC-728, DEC-743 3: a link into ~/gov-os-runs is not followed; nothing there is this repository's.
    # The runtime folder's own files are scanned, also in a clone that lies there, and (DEC-751 2) a link
    # whose target stays inside the project being scanned is followed there too.
    runs, runtime, project = runs_root(), os.path.realpath(root / RUNTIME_REL), os.path.realpath(root)

    def followed(path: str) -> bool:
        real = os.path.realpath(path)
        within = lambda top: real == top or real.startswith(top + os.sep)  # noqa: E731
        return runs is None or within(runtime) or within(project) or not within(runs)

    # Linked folders elsewhere are followed; a file that cannot be read raises.
    files = []
    for folder, folders, names in os.walk(root / RUNTIME_REL, onerror=refuse, followlinks=True):
        folders[:] = [name for name in folders if followed(os.path.join(folder, name))]
        files += [Path(folder) / name for name in names if followed(os.path.join(folder, name))]
    files.sort()
    # DEC-853: a store's bytes once scanned clean by the same scanner are not scanned again.
    scanner = _scanner(rules)
    trusted, clean, reused = _trusted(root, scanner), set(), {}
    large = threading.BoundedSemaphore(2)

    def judge(path: Path) -> bool:
        with large if path.stat().st_size >= _LARGE else contextlib.nullcontext():
            content, chunks, kept = _store(path)
            digest = hashlib.sha256(content).hexdigest()
            if digest in trusted:
                reused[path] = digest
            elif _scan(rules, chunks):
                return True  # a finding is never recorded
            if kept or digest in trusted:
                clean.add(digest)
            return False

    # Every file is read and judged, the largest first, as many at a time as there are processors, so a large
    # store is neither started last nor slowed by more runs than the machine runs at once. The first file that
    # cannot be decided raises, and then nothing is recorded.
    by_size = sorted(files, key=lambda path: -path.stat().st_size)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 1) as pool:
        verdicts = dict(zip(by_size, pool.map(judge, by_size)))
    for path, digest in sorted(reused.items()):  # the label names the store and the digest, never content
        print(f"secrets-indexing: clean result reused, not scanned again: {path.relative_to(root).as_posix()} "
              f"sha256 {digest}", file=sys.stderr)
    if scanner is not None:
        _record(root, scanner, clean)
    return [path.relative_to(root).as_posix() for path in files if verdicts[path]]

"""The planted repositories of the W2-135 acceptance tests, today's code, the line-cut oracle and a recording reranker.

- ``build(root)``: a temporary git repository with a one-line JSON file of 24,575 characters (no newline at its end),
  a Markdown file holding one line of 10,631 characters among ordinary lines, a Markdown section of about 11,000
  characters of ordinary lines (the word asked for past character 4,000), a two-line file whose first line is exactly
  4,000 characters and its newline, one-line text files at the cap's edge (4,000 and 4,001 characters), two one-line
  files of accented text (where characters and bytes differ), and an ordinary note.
- ``build_register(root)``: a second temporary repository whose path map names a register in plain text
  (``docs/DECISION_REGISTER.txt``): a preface, a superseded DEC-100 and DEC-101, whose clause 6 is one line of 5,200
  characters. A register that is not Markdown is one parent, the whole file, cut by size alone, so an expanded parent
  spans DEC-100 and DEC-101 and ``gov retrieve``'s ``leave_out`` narrows it to its own chunk (W2-133; the review's F2).
- Each repository's lexical index and record store are built in the temporary folder (the caller replaces the secret
  filter, as the unit tests do). Never this repository's store.
- ``today()``: ``retrieve.py`` and ``register.py`` as ``w2/integrate`` held them (``TODAY_BLOBS``, read from git), each
  loaded as a module of its own beside the running tree's. They are the ticket's only source paths, so the two
  pipelines differ by the fix alone.
- ``Scorer``: a stand-in reranker that keeps every text it is sent (the reranker's input) and scores each by a hash
  of it, so no two texts tie and the order is the same whichever code asks.
- The oracle (``span_text``, ``span_bytes``, ``cut``, ``sent_text``, ``cut_key``): an item's full text, its bytes and
  what S1 says is sent, read from the planted files alone, never from the code under test. A line's length is
  counted without its newline, and a cut line keeps its newline, so the lines after it stay lines of their own
  (README N-1).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src"
if importlib.util.find_spec("gov") is None:  # a PYTHONPATH given names the tree under test; else this one
    sys.path.insert(0, str(SRC))

# w2/integrate after W2-32 S11 merged; integrate's head 33a8b77db663 (round 2) holds the same two blobs (README N-5)
TODAY_COMMIT = "e3355def9f99"
TODAY_BLOBS = {
    "retrieve": ("src/gov/retrieval/retrieve.py", "1fb6a75b10b9601cf271efc877e8f918e55e9034"),
    "register": ("src/gov/decisions/register.py", "491959f0527148304c61dd4ce71427d38f2a3494"),
}

CAP = 4000  # DEC-1086 B: a line of an item is sent up to this many characters


def _exactly(head: str, filler: str, length: int, tail: str = "") -> str:
    """``head``, then ``filler`` repeated, then ``tail``: exactly ``length`` characters."""
    room = length - len(head) - len(tail)
    assert room >= 0
    return head + (filler * (room // len(filler) + 1))[:room] + tail


# -- the one-line JSON file: 24,575 characters, no newline at its end (m29's file, BUNDLE-BUDGET-1) ----------------
JSON = "data/ledger.json"
JSON_CHARS = 24_575
JSON_TEXT = _exactly('{"ledger": "the zephyrine ledger of the harbour", "rows": ["', "tally of the reed beds ",
                     JSON_CHARS, '"]}')

# -- the Markdown file: one line of 10,631 characters among ordinary lines ------------------------------------------
SURVEY = "docs/survey.md"
LONG_LINE_CHARS = 10_631  # without its newline
LONG_LINE = _exactly("The quillwort tally of the harbour survey: ", "quillwort reed and sedge, ", LONG_LINE_CHARS)
_ORDINARY = "".join(f"The survey's line {n} names the harbour wall and its stones.\n" for n in range(1, 7))
_AFTER = "".join(f"The survey's closing line {n} names the harbour gate.\n" for n in range(1, 5))
_ALMANAC = "".join(f"Almanac entry {n:02d}: the tide almanac lists the harbour tide at pier number {n:02d}.\n"
                   for n in range(1, 45))
SURVEY_TEXT = ("# Survey of the harbour\n\n" + _ORDINARY + LONG_LINE + "\n" + _AFTER
               + "\n## Almanac of the harbour\n\n" + _ALMANAC)

# -- a Markdown section of ordinary lines, about 11,000 characters; the word asked for sits past character 4,000 -----
LOGBOOK = "docs/logbook.md"
LOGBOOK_WORD = "gannet"
LOGBOOK_LINE = 90  # the logbook line that holds LOGBOOK_WORD
_LOG = "".join((f"Logbook entry {n:03d}: the watch saw a {LOGBOOK_WORD} dive past mooring {n:03d}, "
                "wind and swell steady.\n") if n == LOGBOOK_LINE - 2 else
               f"Logbook entry {n:03d}: the watch notes the swell, the wind and the boats at mooring {n:03d}.\n"
               for n in range(1, 130))
LOGBOOK_TEXT = "# Logbook of the quay\n\n" + _LOG

# -- two lines: the first exactly 4,000 characters and its newline (not over the cap), then an ordinary line --------
CANDLE = "notes/candle.txt"
CANDLE_TEXT = _exactly("the candlewick list of the quay: ", "candle wax ", CAP) + "\n" \
    + "the second line names the wax and the wick."

# -- one-line text files at the cap's edge, no newline at their end -------------------------------------------------
AT_CAP = "notes/lantern.txt"  # exactly 4,000 characters: sent whole (S2)
AT_CAP_TEXT = _exactly("the lantern list of the harbour: ", "lantern wick ", CAP)
OVER_CAP = "notes/beacon.txt"  # 4,001 characters: cut (S1)
OVER_CAP_TEXT = _exactly("the beacon list of the harbour: ", "beacon flame ", CAP + 1)

# -- accented one-line files: characters, not bytes -----------------------------------------------------------------
ACCENTED_OVER = "notes/brioche.txt"  # 4,500 characters, about 6,900 bytes: cut at 4,000 characters (S1)
ACCENTED_OVER_TEXT = _exactly("the brioche list of the harbour: ", "crème brûlée à la fève, ", 4_500)
ACCENTED_UNDER = "notes/meringue.txt"  # 3,000 characters, over 4,000 bytes: sent whole (S2)
ACCENTED_UNDER_TEXT = _exactly("the meringue list of the harbour: ", "éé èè àà ", 3_000)

# -- an ordinary note -----------------------------------------------------------------------------------------------
NOTE = "notes/harbour.md"
NOTE_TEXT = ("# The harbour\n\nThe harbour note keeps the harbour's gate and its kestrel.\n\n"
             "## The moorings\n\nThe moorings of the harbour hold the kestrel boats.\n")

FILES = {
    ".gitignore": ".gov-runtime/\n",
    JSON: JSON_TEXT,
    SURVEY: SURVEY_TEXT,
    LOGBOOK: LOGBOOK_TEXT,
    CANDLE: CANDLE_TEXT,
    AT_CAP: AT_CAP_TEXT,
    OVER_CAP: OVER_CAP_TEXT,
    ACCENTED_OVER: ACCENTED_OVER_TEXT,
    ACCENTED_UNDER: ACCENTED_UNDER_TEXT,
    NOTE: NOTE_TEXT,
}

# -- the second repository: a register in plain text, one parent, a long clause in DEC-101 (the review's F2) --------
REGISTER = "docs/DECISION_REGISTER.txt"
REG_LONG_CHARS = 5_200  # without its newline
REG_LONG = _exactly("- **Clause 6:** the new rule's samphire table of the quay: ", "samphire and sea kale, ",
                    REG_LONG_CHARS)


def _clauses(count: int, marked: dict[int, str]) -> str:
    return "".join(f"{marked[n]}\n" if n in marked else
                   f"- **Clause {n}:** the new rule keeps the quay's boats in order, berth by berth, row {n}.\n"
                   for n in range(1, count + 1))


REGISTER_TEXT = (
    "Decision register\n"
    "\n"
    "The register's preface keeps the almanac of the quay.\n"
    "\n"
    "### DEC-100 — The old quay rule\n"
    "- **Status:** SUPERSEDED by DEC-101\n"
    "- **Decision:** The quay keeps wicker fences at the gate.\n"
    "\n"
    "### DEC-101 — The new quay rule\n"
    "- **Status:** ACCEPTED\n"
    "- **Decision:** The quay keeps open gates.\n"
    + _clauses(30, {6: REG_LONG, 24: "- **Clause 24:** the new rule rings the marjoram bell at noon, row by row."})
)
REGISTER_FILES = {
    ".gitignore": ".gov-runtime/\n",
    "governance/project/path-map.yaml": f"decision_register: {REGISTER}\n",
    REGISTER: REGISTER_TEXT,
}
ALL_FILES = {**FILES, **{rel: text for rel, text in REGISTER_FILES.items() if rel == REGISTER}}

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid",
        "GIT_AUTHOR_DATE": "2026-11-06T12:00:00Z", "GIT_COMMITTER_DATE": "2026-11-06T12:00:00Z"}


def premises() -> None:
    """The planted texts are what the ticket names."""
    assert len(JSON_TEXT) == JSON_CHARS and "\n" not in JSON_TEXT
    json.loads(JSON_TEXT)
    assert len(LONG_LINE) == LONG_LINE_CHARS and "\n" not in LONG_LINE
    assert len(AT_CAP_TEXT) == CAP and len(OVER_CAP_TEXT) == CAP + 1
    assert len(ACCENTED_OVER_TEXT) > CAP and len(ACCENTED_UNDER_TEXT) <= CAP
    assert len(ACCENTED_UNDER_TEXT.encode("utf-8")) > CAP  # a cap on bytes would cut it
    log = LOGBOOK_TEXT.splitlines(keepends=True)
    assert 10_500 <= len(LOGBOOK_TEXT) <= 11_500 and max(map(len, log)) < 200
    assert LOGBOOK_WORD in log[LOGBOOK_LINE - 1] and LOGBOOK_TEXT.count(LOGBOOK_WORD) == 1
    assert len("".join(log[:LOGBOOK_LINE - 1])) > CAP  # the word past character 4,000 of its section
    first, second = CANDLE_TEXT.split("\n")
    assert len(first) == CAP and len(first + "\n") == CAP + 1 and len(second) < 100
    assert len(REG_LONG) == REG_LONG_CHARS and REGISTER_TEXT.count("samphire") > 1 \
        and REGISTER_TEXT.count("marjoram") == 1


def _planted(root: Path, files: dict[str, str]) -> Path:
    from gov import store
    from gov.retrieval import lexical

    premises()
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(text.encode("utf-8"))
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the planted repository"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(root)})
    lexical.refresh(root)
    store.load(root)
    return root


def build(root: Path) -> Path:
    """The planted repository at ``root``, committed, its lexical index and record store built."""
    return _planted(root, FILES)


def build_register(root: Path) -> Path:
    """The planted register's repository at ``root``, committed, its lexical index and record store built."""
    return _planted(root, REGISTER_FILES)


def _module(name: str):
    rel, blob = TODAY_BLOBS[name]
    source = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", blob], check=True,
                            capture_output=True).stdout.decode("utf-8")
    spec = importlib.util.spec_from_loader(f"w2_135_today_{name}", loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(source, f"{rel}@{TODAY_COMMIT}", "exec"), module.__dict__)  # noqa: S102 - our own blob
    return module


def today():
    """``retrieve`` as ``TODAY_COMMIT`` held it, beside the running tree's."""
    return _module("retrieve")


def today_register():
    """``register`` as ``TODAY_COMMIT`` held it, beside the running tree's."""
    return _module("register")


def span_bytes(rel: str, first: int, last: int) -> bytes:
    """Lines ``first`` to ``last`` of the planted file ``rel``, as its bytes (with their newlines)."""
    return b"".join(ALL_FILES[rel].encode("utf-8").splitlines(keepends=True)[first - 1:last])


def span_text(rel: str, first: int, last: int) -> str:
    return span_bytes(rel, first, last).decode("utf-8")


def cut(text: str, first: int = 1) -> tuple[str, list[int]]:
    """S1 on ``text`` whose first line is line ``first``: each line over ``CAP`` characters (its newline not counted)
    as its first ``CAP`` characters and its newline, every other line whole; and the numbers of the lines cut."""
    sent, lines = [], []
    for number, line in enumerate(text.splitlines(keepends=True), first):
        body = line.rstrip("\n")
        if len(body) > CAP:
            lines.append(number)
            line = body[:CAP] + line[len(body):]
        sent.append(line)
    return "".join(sent), lines


def sent_text(rel: str, first: int, last: int) -> str:
    """What S1 says an item of lines ``first`` to ``last`` of ``rel`` is sent as."""
    return cut(span_text(rel, first, last), first)[0]


def cut_key(rel: str, first: int, last: int) -> dict | None:
    """The ``cut`` key S1 says an item of lines ``first`` to ``last`` of ``rel`` carries, or None (no line over CAP)."""
    full = span_text(rel, first, last)
    sent, lines = cut(full, first)
    return {"chars": len(full), "sent": len(sent), "lines": lines} if lines else None


def has_long_line(text: str) -> bool:
    return any(len(line.rstrip("\n")) > CAP for line in text.splitlines(keepends=True))


def line_of(rel: str, start: str) -> int:
    """The 1-based line of the planted file ``rel`` that starts with ``start``."""
    return next(n for n, line in enumerate(ALL_FILES[rel].split("\n"), 1) if line.startswith(start))


def line_count(rel: str) -> int:
    return len(ALL_FILES[rel].splitlines())


def section_of(rel: str, start: str) -> tuple[int, int]:
    """The lines of the Markdown section of ``rel`` whose heading starts with ``start`` (to the line before the next
    heading)."""
    lines = ALL_FILES[rel].split("\n")
    if lines[-1] == "":
        lines = lines[:-1]
    heads = [n for n, line in enumerate(lines, 1) if line.startswith("#")] + [len(lines) + 1]
    first = line_of(rel, start)
    return first, heads[heads.index(first) + 1] - 1


def section_of_survey(start: str) -> tuple[int, int]:
    return section_of(SURVEY, start)


class Scorer:
    """The stand-in reranker: ``reranker=scorer.loader``. It keeps each text it is sent, in order, and scores each by
    a hash of it."""

    def __init__(self):
        self.texts: list[str] = []

    def loader(self):
        return self.score

    def score(self, query: str, texts: list[str]):
        self.texts.extend(texts)
        return [int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16) / 2 ** 32 for text in texts]


# S3's questions: (name, question, keyword arguments of ``ask``). ``repo="register"`` asks the register's repository;
# ``pipeline=True`` is ``gov retrieve``'s pipeline (``retrieve``, then the register's ``leave_out``). A batched
# question is followed through its continuations to its end.
SCENARIOS = [
    ("json-alone", "zephyrine", {}),
    ("long-line-alone", "quillwort", {"bundle_budget": 1}),
    ("long-line-section-expanded", "quillwort", {}),
    ("json-beside-the-long-line", "zephyrine quillwort", {}),  # today: used over the limit, so no expansion
    ("edges", "lantern beacon brioche meringue", {}),
    ("every-file", "harbour", {}),
    ("every-file-budget-12000", "harbour", {"bundle_budget": 12_000}),
    ("every-file-expanded", "harbour", {"bundle_budget": 20_000}),
    ("almanac-batched", "tide almanac", {"batch_size": 1}),
    ("every-file-batched", "harbour", {"batch_size": 1}),
    ("almanac-batched-budget-1000", "tide almanac", {"batch_size": 1, "bundle_budget": 1000}),  # a left-out span
    ("logbook-section-expanded", LOGBOOK_WORD, {}),  # about 11,000 characters of ordinary lines
    ("candle-expanded", "candlewick", {}),  # a line of exactly 4,000 characters and its newline, then one more
    ("candle-alone", "candlewick", {"bundle_budget": 1}),
    ("register-long-clause-retrieve-alone", "samphire", {"repo": "register"}),
    ("register-long-clause-gov-retrieve", "samphire", {"repo": "register", "pipeline": True}),
    ("register-marjoram-gov-retrieve", "marjoram", {"repo": "register", "pipeline": True}),
    ("register-dec-100-gov-retrieve", "wicker", {"repo": "register", "pipeline": True}),
    ("register-every-chunk-batched-gov-retrieve", "quay", {"repo": "register", "pipeline": True, "batch_size": 1}),
]


def tokens(text: str) -> int:
    """The budget's count of ``text``: four characters a token, rounded up (``retrieve.TOKEN_CHARS``)."""
    return -(-len(text) // 4)


def items_of(bundle: dict, rel: str) -> list[dict]:
    return [item for item in bundle["evidence"] if item["path"] == rel]


def pages(ask, query: str, kwargs: dict, most: int = 20) -> list[dict]:
    """The bundles of ``query``, the first and each its continuation gives, to the end (at most ``most``)."""
    found = [ask(query, **kwargs)]
    while found[-1]["continuation"] and len(found) < most:
        found.append(ask(query, continuation=found[-1]["continuation"], **kwargs))
    return found

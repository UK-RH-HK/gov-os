"""The planted repository of the W2-135 acceptance tests, today's ``retrieve.py`` and a recording stand-in reranker.

- ``build(root)``: a temporary git repository with a one-line JSON file of 24,575 characters (no newline at its end),
  a Markdown file holding one line of 10,631 characters among ordinary lines, one-line text files at the cap's edge
  (4,000 and 4,001 characters), two one-line files of accented text (where characters and bytes differ), and ordinary
  notes. Its lexical index and record store are built in the temporary folder (the caller replaces the secret
  filter, as the unit tests do). Never this repository's store.
- ``today()``: ``src/gov/retrieval/retrieve.py`` as ``w2/integrate`` held it when these tests were written
  (``TODAY_BLOB``, read from git), loaded as a module of its own beside the running tree's. It is the ticket's only
  source path, so the two differ by the fix alone.
- ``Scorer``: a stand-in reranker that keeps every text it is sent (the reranker's input) and scores each by a hash
  of it, so no two texts tie and the order is the same whichever code asks.
- The oracle (``span_text``, ``span_bytes``): an item's full text and bytes read from the planted files alone,
  never from the code under test.
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

TODAY_COMMIT = "fc61f303d467"  # w2/integrate when these tests were written (DEC-1086 B, DEC-1087 (1))
TODAY_BLOB = ("src/gov/retrieval/retrieve.py", "7444017b123c283af7e5124a66e0ae4b5ce6f365")

CAP = 4000  # DEC-1086 B: an item's text is sent up to this many characters


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
    AT_CAP: AT_CAP_TEXT,
    OVER_CAP: OVER_CAP_TEXT,
    ACCENTED_OVER: ACCENTED_OVER_TEXT,
    ACCENTED_UNDER: ACCENTED_UNDER_TEXT,
    NOTE: NOTE_TEXT,
}

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


def build(root: Path) -> Path:
    """The planted repository at ``root``, committed, its lexical index and record store built."""
    from gov import store
    from gov.retrieval import lexical

    premises()
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(text.encode("utf-8"))
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the planted repository"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(root)})
    lexical.refresh(root)
    store.load(root)
    return root


def today():
    """``retrieve`` as ``TODAY_COMMIT`` held it, beside the running tree's."""
    rel, blob = TODAY_BLOB
    source = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", blob], check=True,
                            capture_output=True).stdout.decode("utf-8")
    spec = importlib.util.spec_from_loader("w2_135_today_retrieve", loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(source, f"{rel}@{TODAY_COMMIT}", "exec"), module.__dict__)  # noqa: S102 - our own blob
    return module


def span_bytes(rel: str, first: int, last: int) -> bytes:
    """Lines ``first`` to ``last`` of the planted file ``rel``, as its bytes (with their newlines)."""
    return b"".join(FILES[rel].encode("utf-8").splitlines(keepends=True)[first - 1:last])


def span_text(rel: str, first: int, last: int) -> str:
    return span_bytes(rel, first, last).decode("utf-8")


def line_of(rel: str, start: str) -> int:
    """The 1-based line of the planted file ``rel`` that starts with ``start``."""
    return next(n for n, line in enumerate(FILES[rel].split("\n"), 1) if line.startswith(start))


def section_of_survey(start: str) -> tuple[int, int]:
    """The lines of the survey's section whose heading starts with ``start`` (to the line before the next heading)."""
    lines = FILES[SURVEY].split("\n")
    if lines[-1] == "":
        lines = lines[:-1]
    heads = [n for n, line in enumerate(lines, 1) if line.startswith("#")] + [len(lines) + 1]
    first = line_of(SURVEY, start)
    return first, heads[heads.index(first) + 1] - 1


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


# S3's questions on the planted repository: (name, question, keyword arguments of ``retrieve``). A batched question
# is followed through its continuations to its end.
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

#!/usr/bin/env python3
"""W2-94 (DAEO-g87r) S4: the counts-only check of EXAMIN's question set, run by the CTO on the real delivery.

    python3 fixtures/evaluation/examin/check_gold.py --sets-root <root> --copy <launch clone> [--set examin]

The walled writer has no shell, so this is the check of its delivery (KPI lines S1, S4, S5 and failure line 3 of the
ticket). It reads the set's questions under ``<root>/fixtures/evaluation/<set>/hidden/`` (the measured half) and
``hidden/visible/`` (the development half), ``hidden/DRAW.txt``, and, once the owner's release step has run,
``<set>/visible/`` and ``<set>/.release-visible.record``. It reads the copy only through git, at the commit
``governance/project/indep-walls/COPY-HEAD.txt`` (read from the clone's HEAD) names, never the working tree and never the
scaffold commit. It writes nothing, uses no network, and needs only the standard library and PyYAML.

OUTPUT: COUNTS AND IDS ONLY. Never a question, an answer, a heading, a path or a line of a file, not even in an error.
Everything is printed on stdout; stderr stays empty. A question is named only by its id (a ``qNN`` file name this script
has checked), and every other thing by a fixed reason code.

    20 questions (10 visible, 10 hidden); draw ok; release ok      (or ``release pending`` before the release step)
    20 of 20 hold
    FAIL q07 SPAN_OUT_OF_FILE                                      one line per failing question: id, reason code
    FAIL draw DRAW_SEED_INCONSISTENT k3                            a line of the form: subject, code, optional ids
    REFUSED COMMIT_MISMATCH q04                                    a refusal: the set cannot be checked as it stands

EXIT CODES: 0 every check holds; 1 the set was checked and something fails (a ``FAIL`` line); 2 refused, fail closed
(an unreadable input or a set of the wrong shape: ``REFUSED <code> [id]`` lines); 3 an internal exception
(``REFUSED INTERNAL_ERROR`` and nothing else); a bad command line is ``REFUSED USAGE``, exit 2.

REFUSED (exit 2): SETS_ROOT_UNREADABLE, HIDDEN_UNREADABLE, HIDDEN_VISIBLE_UNREADABLE, COPY_UNREADABLE,
COPY_HEAD_UNREADABLE, COPY_HEAD_MALFORMED (not 40 hex digits), COMMIT_NOT_IN_COPY, QUESTION_UNREADABLE and
QUESTION_UNPARSABLE (id), COUNT_BELOW_MIN and COUNT_ABOVE_MAX (S1: the set, both halves together, holds 10 to 20
questions), FIELD_MISSING, FIELD_BAD, ID_MISMATCH (id differs from the file name), ID_DUPLICATE (the same name in both
halves), CATEGORY_UNKNOWN, COMMIT_MISMATCH (not equal to COPY-HEAD.txt), SOURCE_NO_PATH, SOURCE_NO_LINES and LINES_BAD
(not two integers, first <= last), each with the question's id; SET_NAME_BAD, USAGE, INTERNAL_ERROR.

THE FORM (the approved writer brief, sections 5 to 7): one ``qNN.yaml`` per question with ``id``, ``question``,
``gold_answer``, ``sources``, ``commit``, ``category`` (one of the ten), ``drawn`` (``sample`` or ``none``) and the
optional ``keyword: true``. ``sources`` is a list; each entry is one source ``{path, heading?, lines: [first, last]}``
or a list of alternatives (any one alternative counts).

PER QUESTION, HOLDS OR FAILS (S4, F3; ``n of n hold``, one ``FAIL <id> <code>`` line each, the first failing check of
the question, in this order):

1. Every ``sources`` entry holds; an alternatives entry holds when at least one alternative does. A source holds when
   its path is not a scaffold path (``governance/project/path-map.yaml``, ``governance/project/indep-walls/**``:
   SOURCE_IS_SCAFFOLD), is a file at the recorded commit (``git cat-file blob <commit>:<path>``; present only in the
   scaffold commit or the working tree is absent: SOURCE_PATH_ABSENT), is UTF-8 text without a NUL (SOURCE_NOT_TEXT),
   its ``lines`` lie within the file (1 <= first <= last <= the file's line count: SPAN_OUT_OF_FILE), and its
   ``heading``, when given, is a whole line of the file (HEADING_NOT_FOUND).
2. The sources hold the answer (ANSWER_NOT_IN_SPANS), by this rule, applied once to the union of the spans of every
   source that holds structurally (all alternatives of an entry included), whitespace runs collapsed:
   a. the *tokens* of ``gold_answer`` are its back-quoted pieces and its identifier-shaped words (a word with ``_``,
      ``::`` or ``/``; a camelCase word; a word mixing letters and digits; an id-shaped hyphenated word with a digit
      such as ``DEC-051``, ``W2-94`` or ``CAP-10``, whose part before the first hyphen starts with an upper-case letter
      and holds only upper-case letters and digits, so ``level-2`` and ``Level-2`` are no tokens, nor is the tail of a
      word that starts with a digit; a ``--flag``; a dotted name like ``mod.func`` or ``file.py``; at least 3
      characters). Every token must occur in the union, case-sensitively, as a substring, or name one of the question's
      sources (the whole path, or its trailing folders and file name: a span of code does not repeat the name of its
      own file). A token holding ``/`` is also held when its segments (split on ``/``, empty ones dropped) occur in
      order in the union, each found at or after the end of the previous one.
   b. when the answer has no token (a prose answer), its *content words* (lower-case letters, 5 or more, not in a small
      list of common words) are looked for by stem (the word without its last 3 letters, at least 5 letters kept),
      case-insensitively; at least one third of the distinct content words (rounded up, at least 1) must occur in the
      union. An answer with neither tokens nor content words (``none``) cannot be judged by this rule and holds.
3. A ``nonexistent`` question (the asked name exists nowhere) gets the name rule instead of 2 (its sources, the file that
   would hold the name, still need 1): the *names* are the question's back-quoted pieces, else its identifier-shaped
   words. A name *exists* when ``git grep -F`` at the commit finds it, or a tracked path name contains it. The question
   holds when at least one name does not exist and every name that does exist is a tracked path (the question may point
   at a real file or folder). Otherwise NONEXISTENT_NAME_FOUND; with no name at all, NONEXISTENT_NO_NAME.

WHAT THE RULE CATCHES: a source that is absent, scaffold, binary or too short for its span; a heading that is not in the
file; a span cut from the wrong place or the wrong file (an answer naming identifiers, values or flags that the spans do
not contain); a nonexistent question whose asked name does exist. WHAT IT CANNOT CATCH: a span that contains the
answer's identifiers but does not state the answer (a wrong claim built from right words); a prose answer whose few
content words occur by chance; a union that holds the tokens only through an alternative that is not the one an agent
would cite; a span that runs into unrelated sections; a heading far from its span; a name in a nonexistent question that
is not identifier-shaped or back-quoted; a nonexistent question that also names a real symbol (reported as
NONEXISTENT_NAME_FOUND, for the CTO to check by hand); rubric rules R1, R3, R4, R7 to R10 (correct today, unambiguous,
a question agents ask, well formed, distinct, stable) and R2's size and kind beyond text. Those stay with the writer's
brief and the owner's own read of the visible half.

THE SPLIT'S FORM (S1, S5; ``draw ok`` or ``draw FAIL``, ``FAIL draw <code> [k<n>]``):
 - DRAW.txt has one line per category present, ``<k> <category> SEED+<k>=<value> <parity> visible=<id> hidden=<id>``,
   or with the letter k written for ``<k>`` in ``SEED+k=<value>`` (then the line's first field is its k)
   (DRAW_MISSING, DRAW_LINE_BAD, DRAW_LINES_MISMATCH: a category present with no line, a line for a category that is
   absent, or two lines for one);
 - every value minus its k is the same integer, the seed (DRAW_SEED_INCONSISTENT); its parity matches the line's word
   (DRAW_PARITY_MISMATCH);
 - the line's k and category are those of the brief's table (DRAW_CATEGORY_MISMATCH), the ids it names exist in the half
   it names and are of that category (DRAW_ID_MISSING, DRAW_CATEGORY_MISMATCH), and follow the brief's rule: an even
   value sends ``q<2k-1>`` to the visible half, an odd one ``q<2k>`` (DRAW_RULE_VIOLATED);
 - each category present has questions in both halves (CATEGORY_IN_ONE_HALF k<n>); the halves differ in size by at most
   one (HALVES_UNBALANCED); nothing but ``qNN.yaml`` files in either half, and DRAW.txt (UNEXPECTED_FILE).
THE RELEASE (S1: the owner's step copies exactly the development half into ``visible/``; ``release ok``, ``release FAIL``
or, with neither ``visible/`` nor a record yet, ``release pending``): ``visible/`` holds the same names and the same
bytes as ``hidden/visible/`` (VISIBLE_FILE_MISSING, VISIBLE_FILE_EXTRA, VISIBLE_BYTES_DIFFER, VISIBLE_NOT_DIR), and
``.release-visible.record`` names each file with its sha256, one ``<name> <sha256>`` line each (RECORD_MISSING,
RECORD_WITHOUT_VISIBLE, RECORD_LINE_BAD, RECORD_ENTRY_MISSING, RECORD_ENTRY_EXTRA, RECORD_SHA_MISMATCH). The release
step's refusal of a second release is the operator's record, not checked here.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import os
import posixpath
import re
import subprocess
import sys

import yaml

EXIT_OK, EXIT_FAIL, EXIT_REFUSED, EXIT_INTERNAL = 0, 1, 2, 3

MIN_QUESTIONS, MAX_QUESTIONS = 10, 20
CATEGORIES = ("code-location", "code-paraphrase", "callers", "exact-string", "config-build-test", "governance-rule",
              "spec-or-decision", "multi-file", "history-or-lesson", "nonexistent")
REQUIRED = ("id", "question", "gold_answer", "sources", "commit", "category", "drawn")
SCAFFOLD_DIR = "governance/project/indep-walls"
SCAFFOLD_FILES = ("governance/project/path-map.yaml",)
COPY_HEAD_PATH = "governance/project/indep-walls/COPY-HEAD.txt"

QFILE = re.compile(r"q[0-9][0-9]\.yaml\Z")
QID = re.compile(r"q[0-9][0-9]\Z")
HEX40 = re.compile(r"[0-9a-fA-F]{40}\Z")
SET_NAME = re.compile(r"[a-z0-9-]+\Z")
DRAW_LINE = re.compile(r"([0-9]+) ([a-z-]+) SEED\+([0-9]+|k)=(-?[0-9]+) (even|odd) visible=(q[0-9][0-9]) "
                       r"hidden=(q[0-9][0-9])\Z")
RECORD_LINE = re.compile(r"(q[0-9][0-9]\.yaml) ([0-9a-f]{64})\Z")

GIT_ENV = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "HOME": "/nonexistent",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"}


class Refused(Exception):
    """The set cannot be checked as it stands: ``items`` are (code, id or None)."""

    def __init__(self, items):
        super().__init__("refused")
        self.items = items


def refuse(code, qid=None):
    raise Refused([(code, qid)])


# --------------------------------------------------------------------------------------------------------------
# git, read only, on the copy
# --------------------------------------------------------------------------------------------------------------

class Copy:
    """The launch clone, asked about one commit through git only."""

    def __init__(self, path):
        self.path = path
        self.commit = None
        self._blobs = {}
        self._paths = None

    def git(self, *args):
        try:
            done = subprocess.run(["git", "-C", self.path, "-c", "core.quotepath=off", *args], capture_output=True,
                                  env=GIT_ENV, stdin=subprocess.DEVNULL, timeout=120)
        except (OSError, ValueError, subprocess.SubprocessError):
            return 128, b""
        return done.returncode, done.stdout

    def blob(self, path):
        """The bytes of ``path`` at the commit, or None when it is no file there."""
        if path not in self._blobs:
            code, out = self.git("cat-file", "blob", f"{self.commit}:{path}")
            self._blobs[path] = out if code == 0 else None
        return self._blobs[path]

    def tracked(self):
        """Every tracked path name at the commit (and every folder name above them)."""
        if self._paths is None:
            code, out = self.git("ls-tree", "-r", "-z", "--name-only", self.commit)
            if code != 0:
                raise RuntimeError("ls-tree")
            names = {n for n in out.decode("utf-8", "replace").split("\0") if n}
            folders = set()
            for name in names:
                parent = posixpath.dirname(name)
                while parent and parent not in folders:
                    folders.add(parent)
                    parent = posixpath.dirname(parent)
            self._paths = (names, folders)
        return self._paths

    def is_tracked_path(self, name):
        names, folders = self.tracked()
        return name.strip("/") in names or name.strip("/") in folders

    def exists(self, name):
        """The name is found by ``git grep -F`` at the commit, or in a tracked path name."""
        if any(name in p for p in self.tracked()[0]):
            return True
        code, _ = self.git("grep", "-F", "-q", "-e", name, self.commit)
        if code not in (0, 1):
            raise RuntimeError("grep")
        return code == 0


# --------------------------------------------------------------------------------------------------------------
# the rule: tokens and content words
# --------------------------------------------------------------------------------------------------------------

BACKQUOTED = re.compile(r"`([^`\n]+)`")
NAMELIKE = re.compile(r"--[A-Za-z][A-Za-z0-9-]*|[A-Za-z_][A-Za-z0-9_]*(?:(?:::|[./-])[A-Za-z0-9_]+)*")
ID_HEAD = re.compile(r"[A-Z][A-Z0-9]*-")
EXTENSIONS = {"py", "md", "txt", "yaml", "yml", "json", "toml", "sh", "js", "ts", "tsx", "jsx", "cfg", "ini", "rs",
              "go", "c", "h", "cpp", "java", "css", "html", "sql", "lock", "env", "xml"}
COMMON = {"about", "after", "again", "also", "because", "before", "being", "between", "could", "does", "during",
          "each", "every", "first", "from", "have", "into", "just", "later", "least", "more", "most", "never",
          "only", "other", "over", "same", "should", "since", "still", "such", "than", "that", "their", "them",
          "then", "there", "these", "they", "this", "those", "through", "under", "until", "used", "using", "very",
          "when", "where", "whether", "which", "while", "will", "with", "within", "without", "would", "which"}


def squash(text):
    return " ".join(text.split())


def _shaped(word, before=""):
    """``before``: the character just before the word in its text (the hyphen-digit judgement looks at it)."""
    if len(word) < 3:
        return False
    if word.startswith("--") or "_" in word or "::" in word or "/" in word:
        return True
    if "." in word:
        return any(c.isdigit() or c.isupper() for c in word) or word.rsplit(".", 1)[-1] in EXTENSIONS
    if "-" in word:
        # a hyphenated word with a digit is a token only when id-shaped (DEC-051, W2-94), judged whole
        return (any(c.isdigit() for c in word) and ID_HEAD.match(word) is not None
                and not (before and before.isalnum()))
    return bool(re.search(r"[a-z][A-Z]", word)) or (any(c.isdigit() for c in word) and any(c.isalpha() for c in word))


def tokens(text, backquoted_only=False):
    """The back-quoted pieces of ``text`` and (unless ``backquoted_only``) its identifier-shaped words, in order."""
    found = [squash(m.group(1)) for m in BACKQUOTED.finditer(text)]
    if not backquoted_only:
        rest = BACKQUOTED.sub(" ", text)
        found += [m.group(0) for m in NAMELIKE.finditer(rest)
                  if _shaped(m.group(0), rest[m.start() - 1] if m.start() else "")]
    return list(dict.fromkeys(t for t in found if t))


def content_words(text):
    rest = BACKQUOTED.sub(" ", text)
    words = re.findall(r"[a-z]{5,}", rest)
    return list(dict.fromkeys(w for w in words if w not in COMMON))


def _segments_in_order(token, union):
    """A token holding ``/``: its non-empty segments each occur in ``union`` at or after the end of the previous."""
    if "/" not in token:
        return False
    segments = [s for s in token.split("/") if s]
    position = 0
    for segment in segments:
        found = union.find(segment, position)
        if found < 0:
            return False
        position = found + len(segment)
    return bool(segments)


def answer_in(text, spans, paths=()):
    """The rule's step 2 on ``gold_answer`` ``text``, the spans and the sources' paths: True when the spans hold the
    answer. A token that names a source's own path (the whole path, or its trailing folders and file name) is held by
    that source: a span of code does not repeat the name of the file it is in."""
    union = squash("\n".join(spans))
    found = tokens(text)
    if found:
        return all(t in union or any(p == t or p.endswith("/" + t) for p in paths) or _segments_in_order(t, union)
                   for t in found)
    words = content_words(text)
    if not words:
        return True
    lower = union.lower()
    hits = sum(1 for w in words if w[:max(5, len(w) - 3)] in lower)
    return hits >= max(1, math.ceil(len(words) / 3))


# --------------------------------------------------------------------------------------------------------------
# reading the set
# --------------------------------------------------------------------------------------------------------------

def split_lines(text):
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def list_half(folder, code, measured):
    """The names in a half's folder: (question file names, how many other names). The measured half's folder also
    holds DRAW.txt and the development half's folder; nothing else is expected anywhere."""
    try:
        entries = list(os.scandir(folder))
    except OSError:
        refuse(code)
    questions, other = [], 0
    for entry in entries:
        regular = entry.is_file(follow_symlinks=False)
        if regular and QFILE.match(entry.name):
            questions.append(entry.name)
        elif measured and regular and entry.name == "DRAW.txt":
            continue
        elif measured and entry.name == "visible" and entry.is_dir(follow_symlinks=False):
            continue
        else:
            other += 1
    return sorted(questions), other


def load_question(folder, name):
    qid = name[:-5]
    try:
        with open(os.path.join(folder, name), "rb") as handle:
            raw = handle.read()
    except OSError:
        return qid, None, "QUESTION_UNREADABLE"
    try:
        data = yaml.safe_load(raw.decode("utf-8"))
    except Exception:  # noqa: BLE001  (a parse message holds the file's text: never shown)
        return qid, None, "QUESTION_UNPARSABLE"
    if not isinstance(data, dict):
        return qid, None, "QUESTION_UNPARSABLE"
    return qid, data, None


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def source_codes(entry):
    """Refusal codes of one source mapping (never its content)."""
    if not isinstance(entry, dict):
        return ["FIELD_BAD"]
    codes = []
    path = entry.get("path")
    if not isinstance(path, str) or not path.strip():
        codes.append("SOURCE_NO_PATH")
    if "lines" not in entry:
        codes.append("SOURCE_NO_LINES")
    else:
        lines = entry["lines"]
        if not (isinstance(lines, list) and len(lines) == 2 and all(_is_int(n) for n in lines) and lines[0] <= lines[1]):
            codes.append("LINES_BAD")
    heading = entry.get("heading")
    if heading is not None and (not isinstance(heading, str) or not heading.strip()):
        codes.append("FIELD_BAD")
    return codes


def question_codes(qid, data, copy_head):
    """Refusal codes for one parsed question: its required fields and their forms."""
    codes = []
    for field in REQUIRED:
        if field not in data or data[field] is None:
            codes.append("FIELD_MISSING")
            break
    if "id" in data and data["id"] is not None and data["id"] != qid:
        codes.append("ID_MISMATCH")
    for field in ("question", "gold_answer"):
        if field in data and data[field] is not None and not (isinstance(data[field], str) and data[field].strip()):
            codes.append("FIELD_BAD")
    category = data.get("category")
    if category is not None and category not in CATEGORIES:
        codes.append("CATEGORY_UNKNOWN")
    if data.get("drawn") is not None and data["drawn"] not in ("sample", "none"):
        codes.append("FIELD_BAD")
    if "keyword" in data and not isinstance(data["keyword"], bool):
        codes.append("FIELD_BAD")
    commit = data.get("commit")
    if commit is not None and not (isinstance(commit, str) and commit.lower() == copy_head):
        codes.append("COMMIT_MISMATCH")
    sources = data.get("sources")
    if sources is not None:
        if not isinstance(sources, list) or not sources:
            codes.append("FIELD_BAD")
        else:
            for item in sources:
                members = item if isinstance(item, list) else [item]
                if not members:
                    codes.append("FIELD_BAD")
                for member in members:
                    codes += source_codes(member)
    return list(dict.fromkeys(codes))


# --------------------------------------------------------------------------------------------------------------
# the questions: sources, answer, the nonexistent rule
# --------------------------------------------------------------------------------------------------------------

def is_scaffold(path):
    norm = posixpath.normpath(path.strip())
    return norm in SCAFFOLD_FILES or norm == SCAFFOLD_DIR or norm.startswith(SCAFFOLD_DIR + "/")


def judge_source(copy, source):
    """(code, span text): the code is None when the source holds structurally."""
    path = source["path"]
    if is_scaffold(path):
        return "SOURCE_IS_SCAFFOLD", None
    raw = copy.blob(path)
    if raw is None:
        return "SOURCE_PATH_ABSENT", None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return "SOURCE_NOT_TEXT", None
    if "\x00" in text:
        return "SOURCE_NOT_TEXT", None
    lines = split_lines(text)
    first, last = source["lines"]
    if first < 1 or last > len(lines):
        return "SPAN_OUT_OF_FILE", None
    heading = source.get("heading")
    if heading is not None and heading.rstrip() not in [line.rstrip() for line in lines]:
        return "HEADING_NOT_FOUND", None
    return None, "\n".join(lines[first - 1:last])


def judge_nonexistent(copy, question):
    names = tokens(question, backquoted_only=True) or tokens(question)
    if not names:
        return "NONEXISTENT_NO_NAME"
    existing = [n for n in names if copy.exists(n)]
    if len(existing) == len(names) or any(not copy.is_tracked_path(n) for n in existing):
        return "NONEXISTENT_NAME_FOUND"
    return None


def judge_question(copy, data):
    """The first failing reason code of one well-formed question, or None when it holds."""
    spans, paths = [], []
    for item in data["sources"]:
        members = item if isinstance(item, list) else [item]
        results = [judge_source(copy, member) for member in members]
        good = [(member, text) for member, (code, text) in zip(members, results) if code is None]
        if not good:
            return results[0][0]
        spans += [text for _, text in good]
        paths += [posixpath.normpath(member["path"].strip()) for member, _ in good]
    if data["category"] == "nonexistent":
        return judge_nonexistent(copy, data["question"])
    if not answer_in(data["gold_answer"], spans, paths):
        return "ANSWER_NOT_IN_SPANS"
    return None


# --------------------------------------------------------------------------------------------------------------
# the split and the release
# --------------------------------------------------------------------------------------------------------------

def check_draw(base, visible, hidden, categories):
    """The draw's form: a list of (code, [words]) failures. ``visible``/``hidden``: the half's ids; ``categories``:
    id -> category."""
    path = os.path.join(base, "hidden", "DRAW.txt")
    try:
        with open(path, "rb") as handle:
            lines = [ln for ln in handle.read().decode("utf-8").splitlines() if ln.strip()]
    except (OSError, UnicodeDecodeError):
        return [("DRAW_MISSING", [])]
    fails = []
    seeds, seen = set(), []
    for line in lines:
        match = DRAW_LINE.match(line.strip())
        if not match:
            fails.append(("DRAW_LINE_BAD", []))
            continue
        k, category, k2, value, parity, vis, hid = match.groups()
        k, value = int(k), int(value)
        k2 = k if k2 == "k" else int(k2)
        tag = [f"k{k}"]
        if k != k2 or not 1 <= k <= len(CATEGORIES) or CATEGORIES[k - 1] != category:
            fails.append(("DRAW_CATEGORY_MISMATCH", tag))
        seen.append(category)
        seeds.add(value - k2)
        if (value % 2 == 0) != (parity == "even"):
            fails.append(("DRAW_PARITY_MISMATCH", tag))
        if vis not in visible or hid not in hidden:
            fails.append(("DRAW_ID_MISSING", tag))
        elif categories.get(vis) != category or categories.get(hid) != category:
            fails.append(("DRAW_CATEGORY_MISMATCH", tag))
        if 1 <= k <= len(CATEGORIES):
            first, second = f"q{2 * k - 1:02d}", f"q{2 * k:02d}"
            expected = (first, second) if parity == "even" else (second, first)
            if (vis, hid) != expected:
                fails.append(("DRAW_RULE_VIOLATED", tag))
    if len(seeds) > 1:
        fails.append(("DRAW_SEED_INCONSISTENT", []))
    present = sorted(set(categories.values()))
    if sorted(seen) != present:
        fails.append(("DRAW_LINES_MISMATCH", []))
    return fails


def check_halves(visible, hidden, categories):
    fails = []
    for category in sorted({c for c in categories.values()}, key=CATEGORIES.index):
        in_visible = any(categories[i] == category for i in visible)
        in_hidden = any(categories[i] == category for i in hidden)
        if not (in_visible and in_hidden):
            fails.append(("CATEGORY_IN_ONE_HALF", [f"k{CATEGORIES.index(category) + 1}"]))
    if abs(len(visible) - len(hidden)) > 1:
        fails.append(("HALVES_UNBALANCED", []))
    return fails


def sha256_of(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def check_release(base, development):
    """(state, failures): state is ``pending``, ``ok`` or ``FAIL``. ``development``: the development half's file names."""
    folder = os.path.join(base, "visible")
    record = os.path.join(base, ".release-visible.record")
    has_folder, has_record = os.path.lexists(folder), os.path.lexists(record)
    if not has_folder and not has_record:
        return "pending", []
    fails = []
    copies = {}
    if not has_folder:
        fails.append(("RECORD_WITHOUT_VISIBLE", []))
    elif not os.path.isdir(folder) or os.path.islink(folder):
        fails.append(("VISIBLE_NOT_DIR", []))
    else:
        try:
            names = sorted(os.listdir(folder))
        except OSError:
            names = []
            fails.append(("VISIBLE_NOT_DIR", []))
        for name in names:
            full = os.path.join(folder, name)
            if not (os.path.isfile(full) and not os.path.islink(full) and QFILE.match(name)):
                fails.append(("VISIBLE_FILE_EXTRA", []))
                continue
            copies[name] = full
            if name not in development:
                fails.append(("VISIBLE_FILE_EXTRA", [name[:-5]]))
            elif sha256_of(full) != sha256_of(development[name]):
                fails.append(("VISIBLE_BYTES_DIFFER", [name[:-5]]))
        for name in sorted(development):
            if name not in names:
                fails.append(("VISIBLE_FILE_MISSING", [name[:-5]]))
    if not has_record:
        fails.append(("RECORD_MISSING", []))
    else:
        entries = {}
        try:
            with open(record, "rb") as handle:
                rows = [r for r in handle.read().decode("utf-8").splitlines() if r.strip()]
        except (OSError, UnicodeDecodeError):
            rows = []
            fails.append(("RECORD_LINE_BAD", []))
        for row in rows:
            match = RECORD_LINE.match(row.strip())
            if not match or match.group(1) in entries:
                fails.append(("RECORD_LINE_BAD", []))
            else:
                entries[match.group(1)] = match.group(2)
        for name in sorted(development):
            if name not in entries:
                fails.append(("RECORD_ENTRY_MISSING", [name[:-5]]))
            elif name in copies and entries[name] != sha256_of(copies[name]):
                fails.append(("RECORD_SHA_MISMATCH", [name[:-5]]))
        for name in sorted(entries):
            if name not in development:
                fails.append(("RECORD_ENTRY_EXTRA", []))
    return ("FAIL" if fails else "ok"), fails


# --------------------------------------------------------------------------------------------------------------
# the run
# --------------------------------------------------------------------------------------------------------------

def read_copy(copy_path):
    if not os.path.isdir(copy_path):
        refuse("COPY_UNREADABLE")
    copy = Copy(copy_path)
    code, _ = copy.git("rev-parse", "--git-dir")
    if code != 0:
        refuse("COPY_UNREADABLE")
    code, raw = copy.git("show", f"HEAD:{COPY_HEAD_PATH}")
    if code != 0:
        refuse("COPY_HEAD_UNREADABLE")
    try:
        head = raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        refuse("COPY_HEAD_MALFORMED")
    if not HEX40.match(head):
        refuse("COPY_HEAD_MALFORMED")
    copy.commit = head.lower()
    code, _ = copy.git("cat-file", "-e", f"{copy.commit}^{{commit}}")
    if code != 0:
        refuse("COMMIT_NOT_IN_COPY")
    return copy


def run(sets_root, copy_path, set_name):
    if not SET_NAME.match(set_name):
        refuse("SET_NAME_BAD")
    if not (os.path.isdir(sets_root) and os.access(sets_root, os.R_OK | os.X_OK)):
        refuse("SETS_ROOT_UNREADABLE")
    base = os.path.join(sets_root, "fixtures", "evaluation", set_name)
    hidden_dir = os.path.join(base, "hidden")
    visible_dir = os.path.join(hidden_dir, "visible")
    if not os.path.isdir(hidden_dir):
        refuse("HIDDEN_UNREADABLE")
    copy = read_copy(copy_path)

    hidden_files, hidden_other = list_half(hidden_dir, "HIDDEN_UNREADABLE", True)
    if not os.path.isdir(visible_dir):
        refuse("HIDDEN_VISIBLE_UNREADABLE")
    visible_files, visible_other = list_half(visible_dir, "HIDDEN_VISIBLE_UNREADABLE", False)
    refusals = []
    both = sorted(set(hidden_files) & set(visible_files))
    refusals += [("ID_DUPLICATE", name[:-5]) for name in both]
    total = len(set(hidden_files) | set(visible_files))
    if total < MIN_QUESTIONS:
        refusals.append(("COUNT_BELOW_MIN", None))
    elif total > MAX_QUESTIONS:
        refusals.append(("COUNT_ABOVE_MAX", None))

    questions = {}
    for folder, names in ((hidden_dir, hidden_files), (visible_dir, visible_files)):
        for name in names:
            qid, data, bad = load_question(folder, name)
            if bad:
                refusals.append((bad, qid))
                continue
            codes = question_codes(qid, data, copy.commit)
            refusals += [(code, qid) for code in codes]
            if not codes and qid not in [r[1] for r in refusals if r[0] == "ID_DUPLICATE"]:
                questions[qid] = data
    if refusals:
        raise Refused(refusals)

    visible_ids = {n[:-5] for n in visible_files}
    hidden_ids = {n[:-5] for n in hidden_files}
    categories = {qid: data["category"] for qid, data in questions.items()}

    failures = []  # (subject, code, words)
    if hidden_other or visible_other:
        failures.append(("set", "UNEXPECTED_FILE", []))
    draw_fails = check_draw(base, visible_ids, hidden_ids, categories) + check_halves(visible_ids, hidden_ids,
                                                                                     categories)
    failures += [("draw", c, list(w)) for c, w in dict.fromkeys((c, tuple(w)) for c, w in draw_fails)]
    state, release_fails = check_release(base, {n: os.path.join(visible_dir, n) for n in visible_files})
    failures += [("release", code, words) for code, words in release_fails]

    bad = {}
    for qid in sorted(questions):
        code = judge_question(copy, questions[qid])
        if code:
            bad[qid] = code

    lines = [f"{total} questions ({len(visible_ids)} visible, {len(hidden_ids)} hidden); "
             f"draw {'FAIL' if draw_fails else 'ok'}; release {state}",
             f"{total - len(bad)} of {total} hold"]
    for subject, code, words in failures:
        lines.append(" ".join(["FAIL", subject, code, *words]))
    lines += [f"FAIL {qid} {code}" for qid, code in bad.items()]
    print("\n".join(lines))
    return EXIT_FAIL if (bad or failures) else EXIT_OK


class Parser(argparse.ArgumentParser):
    def error(self, message):  # a usage text could carry what was typed: say the code only
        raise Refused([("USAGE", None)])


def main(argv=None):
    try:
        parser = Parser(add_help=False)
        parser.add_argument("--sets-root", required=True)
        parser.add_argument("--copy", required=True)
        parser.add_argument("--set", default="examin")
        args = parser.parse_args(argv)
        return run(args.sets_root, args.copy, args.set)
    except Refused as refused:
        for code, qid in sorted(refused.items, key=lambda i: (i[1] or "", i[0])):
            print(f"REFUSED {code}" + (f" {qid}" if qid else ""))
        return EXIT_REFUSED
    except Exception:  # noqa: BLE001  (fail closed, no text from the set)
        print("REFUSED INTERNAL_ERROR")
        return EXIT_INTERNAL


if __name__ == "__main__":
    sys.exit(main())

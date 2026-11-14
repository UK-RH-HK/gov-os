"""Shared readers for the W2-188 acceptance tests (the adopt skill's step 6 and the practice record, DAEO-zlog).

Everything here reads files or runs ``git`` and the skills check in a child process. No network, no model, never a
store. W2-88a's matchers (``check_steps``, ``a9_regions``, ``stated_counts`` ...) are loaded from their own file by path
(never edited, never copied), so a change to them moves this folder too.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

# W2-88a's readers, loaded from their path under a private module name.
_A88_PATH = REPO_ROOT / "tests" / "acceptance" / "W2-88a" / "w2_88a_support.py"
_spec = importlib.util.spec_from_file_location("w2_88a_support_loaded_by_w2_188", _A88_PATH)
a88 = importlib.util.module_from_spec(_spec)
sys.modules["w2_88a_support_loaded_by_w2_188"] = a88
_spec.loader.exec_module(a88)

TICKET = "DAEO-zlog"
BASE = "5336a6fca337015ffa4b3c1333d14d5356d9ca53"  # the brief's base (5336a6fca): the skill as it was before this ticket
BASE_SHA256 = "16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0"
KERNEL_REL = a88.KERNEL_REL
COPIES_REL = a88.COPIES_REL
ALL_REL = a88.ALL_REL
CLAUDE_COPY_REL = ".claude/skills/adopt/SKILL.md"
PRACTICE_REL = a88.PRACTICE_REL
CITP_REL = "docs/changes/W2-188-CIT-P.md"
REGISTER_REL = "docs/DECISION_REGISTER.md"
VERIFY_HEADING_PATTERN = r"^Verify clauses for adopted tickets$"

read = a88.read
read_bytes = a88.read_bytes
sha256_of = a88.sha256_of
flat = a88.flat
git = a88.git
units = a88.units
heading_section = a88.heading_section
bullet_region = a88.bullet_region
check_steps = a88.check_steps
check_pointer = a88.check_pointer
run_skill_validator = a88.run_skill_validator
stated_counts = a88.stated_counts
verdicts = a88.verdicts


def collapse(text):
    """Whitespace collapsed to single spaces, case and markdown kept (for a verbatim comparison of a wrapped text)."""
    return re.sub(r"\s+", " ", text).strip()


def base_blob(rel=KERNEL_REL):
    """``git show <base>:<rel>``: a fixed commit, so the value never moves."""
    return git("show", f"{BASE}:{rel}").stdout


# --------------------------------------------------------------------------
# The skill: A9, step 6's stretch, the paragraph after step 7
# --------------------------------------------------------------------------

def a9_text(text, rel="the skill"):
    regions = a88.a9_regions(text)
    if not regions:
        pytest.fail(f"{rel} has no A9 section (a heading or a bullet that names A9)", pytrace=False)
    return "\n".join(regions)


def stretch_between(text, first, second):
    """The raw text from the line starting ``<first>.`` to the line starting ``<second>.`` (a numbered step's stretch);
    ``None`` when either line is missing."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if re.match(rf"^\s*{first}\.\s", line)), None)
    if start is None:
        return None
    stop = next((i for i in range(start + 1, len(lines)) if re.match(rf"^\s*{second}\.\s", lines[i])), None)
    if stop is None:
        return None
    return "\n".join(lines[start:stop])


def step6_stretch(rel):
    """Step 6's stretch in the copy ``rel``: the text from the line starting ``6.`` to the line starting ``7.`` inside A9's
    section. Fails (naming the copy) when A9 or either line is missing."""
    stretch = stretch_between(a9_text(read(rel), rel), 6, 7)
    if stretch is None:
        pytest.fail(f"{rel}: A9's section has no line starting `6.` followed by a line starting `7.`", pytrace=False)
    return stretch


def paragraph_after_step_7(text):
    """The lines between the step 7 line and the ``## Verify clauses for adopted tickets`` heading (raw, as lines), or
    ``None`` when either anchor is missing."""
    lines = text.splitlines()
    a9_start = next((i for i, line in enumerate(lines) if re.match(r"^#{1,6}\s+.*\bA9\b", line)), None)
    if a9_start is None:
        return None
    seven = next((i for i in range(a9_start, len(lines)) if re.match(r"^\s*7\.\s", lines[i])), None)
    if seven is None:
        return None
    verify = next((i for i in range(seven + 1, len(lines))
                   if re.match(r"^#{2,3}\s+" + VERIFY_HEADING_PATTERN[1:-1] + r"\s*:?\s*$", lines[i])), None)
    if verify is None:
        return None
    return lines[seven + 1:verify]


def front_matter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]
    return []


def governing_sources_ids(text):
    """The ids on the line after the ``## Governing sources`` heading, in file order."""
    lines = text.splitlines()
    head = next((i for i, line in enumerate(lines) if re.match(r"^##\s+Governing sources\s*$", line)), None)
    if head is None:
        return None
    body = next((line for line in lines[head + 1:] if line.strip()), "")
    return re.findall(r"\b(?:DEC|CAP)-\d+\b", body)


def sources_order_key(identifier):
    kind, number = identifier.split("-")
    return (0 if kind == "DEC" else 1, int(number))


# --------------------------------------------------------------------------
# git diff hunks
# --------------------------------------------------------------------------

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def parse_hunks(diff_text):
    """``[(old_start, old_len, new_start, new_len)]`` of a ``--unified=0`` diff (an omitted length is 1)."""
    hunks = []
    for line in diff_text.splitlines():
        found = HUNK.match(line)
        if found:
            old_start, old_len, new_start, new_len = found.groups()
            hunks.append((int(old_start), 1 if old_len is None else int(old_len),
                          int(new_start), 1 if new_len is None else int(new_len)))
    return hunks


def kernel_hunks():
    """The hunks of ``git diff --unified=0 <base> -- <kernel skill>`` (the working tree against the base)."""
    done = git("diff", "--unified=0", BASE, "--", KERNEL_REL)
    return parse_hunks(done.stdout.decode("utf-8", "replace"))


# --------------------------------------------------------------------------
# The commit the record's after-hash is judged against
# --------------------------------------------------------------------------

def committed_after():
    """``(sha256, commit)`` of the kernel skill as this ticket last committed it: the blob at the latest commit after the
    base that changes the kernel skill and carries ``Task: DAEO-zlog``. A later ticket's commit carries another Task and
    never moves it. ``(None, None)`` when there is none."""
    done = git("log", "--no-merges", "--format=%H%x1f%(trailers:key=Task,valueonly,separator=%x2c)%x1e",
               f"{BASE}..HEAD", "--", KERNEL_REL)
    for entry in done.stdout.decode("utf-8", "replace").split("\x1e"):
        if "\x1f" not in entry:
            continue
        commit, tasks = entry.strip().split("\x1f", 1)
        if TICKET in [task.strip() for task in tasks.split(",")]:
            return sha256_of(git("show", f"{commit}:{KERNEL_REL}").stdout), commit
    return None, None


def numstat(commit):
    out = git("diff", "--numstat", BASE, commit, "--", KERNEL_REL).stdout.decode().split()
    return int(out[0]), int(out[1])


def diff_changed_lines(commit):
    """``(removed_lines, added_lines)`` of the kernel skill, base to ``commit``: non-blank, stripped, a leading list
    number or bullet dropped (the record may quote a step without its marker)."""
    out = git("diff", "--unified=0", BASE, commit, "--", KERNEL_REL).stdout.decode("utf-8", "replace")
    removed, added = [], []
    for line in out.splitlines():
        if line.startswith(("+++", "---", "@@", "diff ", "index ")):
            continue
        marker, body = line[:1], line[1:].strip()
        body = re.sub(r"^(?:\d+\.|[-*+])\s+", "", body)
        if not body:
            continue
        if marker == "-":
            removed.append(body)
        elif marker == "+":
            added.append(body)
    return removed, added


def quote_free(text):
    """The record's text with markdown block-quote markers dropped from the start of each line, then ``flat``."""
    return flat(re.sub(r"(?m)^\s*>\s?", "", text))


# --------------------------------------------------------------------------
# The practice record
# --------------------------------------------------------------------------

SECTION_9_TITLE = r"^9\.\s+The standing set \(DEC-1179\)\s*$"


def practice_section(number):
    """The one ``##`` section of the practice record that opens ``<number>.``; fails when it is not exactly one."""
    found = heading_section(read(PRACTICE_REL), rf"^{number}\.\s", levels=(2,))
    if len(found) != 1:
        pytest.fail(f"{PRACTICE_REL} has {len(found)} `## {number}.` sections, not one", pytrace=False)
    return found[0]


def section_9():
    found = heading_section(read(PRACTICE_REL), SECTION_9_TITLE, levels=(2,))
    if not found:
        pytest.fail(f"{PRACTICE_REL} has no `## 9. The standing set (DEC-1179)` section", pytrace=False)
    return found[0]


def blocks(section_text):
    """Paragraphs and top-level list items of a section, each with the indented lines (sub-bullets) that belong to it."""
    out, current, pending_blank = [], [], False
    for line in section_text.splitlines():
        if re.match(r"^#{1,6}\s", line):
            continue
        if not line.strip():
            pending_blank = True
            continue
        indented = line[:1] in (" ", "\t")
        starts_item = bool(re.match(r"^(?:[-*+]|\d+[.)])\s", line))
        if current and (starts_item or (pending_blank and not indented)):
            out.append("\n".join(current))
            current = []
        current.append(line)
        pending_blank = False
    if current:
        out.append("\n".join(current))
    return out


FIVE_POINTS = re.compile(r"\b(?:5|five)(?:\.0)?[ -](?:percentage[ -])?(?:points?|pts?)\b")


def five_point_count(text):
    return len(FIVE_POINTS.findall(flat(text)))


def dec_1179_item_4():
    """DEC-1179 (4)'s text as the register records it, read at test time: the line beginning ``  - (4) `` inside
    ``### DEC-1179``, from ``**Below 95 %:**`` to the end of the line."""
    lines = read(REGISTER_REL).splitlines()
    head = next((i for i, line in enumerate(lines) if line.startswith("### DEC-1179 ")), None)
    if head is None:
        pytest.fail(f"{REGISTER_REL} has no `### DEC-1179` entry", pytrace=False)
    for line in lines[head + 1:]:
        if line.startswith("### "):
            break
        if line.startswith("  - (4) "):
            return line[len("  - (4) "):].rstrip()
    pytest.fail("DEC-1179 in the register has no line beginning `  - (4) `", pytrace=False)


DEC_1179_4_START = "**Below 95 %:** the package's §5.1 rules R1 to R9"


# --------------------------------------------------------------------------
# F3: what the text must never say
# --------------------------------------------------------------------------

_CHOICE = r"(?:choos\w*|chos\w*|judg\w*|adopt\w*|reject\w*|revert\w*)"
_PERMIT = re.compile(
    r"\bstanding set\b[^.;:]{0,80}?\b(?:may|can|could|might|is allowed to|are allowed to|is able to|is used to|are used to|"
    r"used to)\b[^.;:]{0,60}?\b" + _CHOICE + r"\b[^.;:]{0,30}?\bfix")
_ON_THE_SET = re.compile(
    r"\b" + _CHOICE + r"\b[^.;:]{0,25}?\bfix(?:es)?\b[^.;:]{0,40}?\b(?:on|by|with|using|from)\s+(?:the |its |a )?standing set\b")
_NEGATION = re.compile(r"\b(?:never|not|no|nor|neither|cannot|can't|without|forbidden|forbids?|stays? out of)\b")


def permission_violations(text):
    """Statements that the standing set may choose, judge, adopt or reject a fix (flattened sentences), each one not
    negated (``never``, ``not``, ``no``, ``nor``, ``cannot``, ``without``, ``forbidden`` in or just before it)."""
    bad = []
    for unit in units(text):
        for pattern in (_PERMIT, _ON_THE_SET):
            for found in pattern.finditer(unit):
                span = unit[max(0, found.start() - 40):found.end()]
                if not _NEGATION.search(span):
                    bad.append(unit)
    return bad


def second_reranker_misuse(text):
    """Sentences that name a second reranking model without ``never``, ``not``, ``no`` or ``forbidden`` in the same
    sentence (the reader called a second reranking model, or the model allowed)."""
    return [unit for unit in units(text) if re.search(r"\bsecond rerank\w*", unit) and not _NEGATION.search(unit)]

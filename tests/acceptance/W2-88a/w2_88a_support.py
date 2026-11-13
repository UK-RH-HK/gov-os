"""Shared readers for the W2-88a acceptance tests (the adopt skill's kernel text, DAEO-pg6i).

Everything here reads files, runs ``git`` or the skills check in a child process. No network, no model, never a store.
Matchers are built from the KPI lines' own words, on the text lower-cased with its whitespace collapsed, so any
faithful rendering passes and a text that drops or reorders a step fails.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"

KERNEL_REL = "template/governance/kernel/skills/adopt/SKILL.md"
COPIES_REL = ("template/.rulesync/skills/adopt/SKILL.md", ".rulesync/skills/adopt/SKILL.md")
ALL_REL = (KERNEL_REL, *COPIES_REL)
CITP_REL = "docs/changes/W2-88a-CIT-P.md"
PRACTICE_REL = "docs/research/W2-88-memory-practice.md"

TICKET = "DAEO-pg6i"
BASE_COMMIT = "ba27e4c0d"  # the brief's base: the skill as it was before this ticket
BASE_SHA256 = "641a347b9b14101dde711f3550f087e714e404575f780be2a3cd91ff2925102d"
VERIFY_HEADING = "Verify clauses for adopted tickets"


def child_env():
    """This tree's ``src/`` first on ``PYTHONPATH``; the rest of the environment as the run gave it."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(SRC), env["PYTHONPATH"]]) if env.get("PYTHONPATH") else str(SRC)
    return env


def read(rel):
    path = REPO_ROOT / rel
    if not path.is_file():
        pytest.fail(f"{rel} does not exist", pytrace=False)
    return path.read_text(encoding="utf-8")


def read_bytes(rel):
    path = REPO_ROOT / rel
    if not path.is_file():
        pytest.fail(f"{rel} does not exist", pytrace=False)
    return path.read_bytes()


def sha256_of(data: bytes):
    return hashlib.sha256(data).hexdigest()


def flat(text):
    """Lower-cased, whitespace collapsed, markdown emphasis and backticks dropped (a faithful rendering may bold a word)."""
    text = text.replace("`", "").replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", text).lower()


def git(*args, check=True):
    done = subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=False, env=child_env())
    if check and done.returncode != 0:
        pytest.fail(f"`git {' '.join(args)}` exited {done.returncode}: {done.stderr.decode('utf-8', 'replace')[:300]}",
                    pytrace=False)
    return done


def base_blob():
    """The kernel skill as ``git show ba27e4c0d:<path>`` gives it (a fixed commit, so the value never moves)."""
    return git("show", f"{BASE_COMMIT}:{KERNEL_REL}").stdout


# --------------------------------------------------------------------------
# Headings, fences and regions
# --------------------------------------------------------------------------

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def _scan(text):
    """``[(line_no, kind, level_or_indent, line)]``: fenced lines are never headings or bullets."""
    fenced, out = False, []
    for number, line in enumerate(text.splitlines()):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            out.append((number, "fence", 0, line))
            continue
        if fenced:
            out.append((number, "fenced", 0, line))
            continue
        match = HEADING.match(line)
        if match:
            out.append((number, "heading", len(match.group(1)), line))
            continue
        bullet = re.match(r"^(\s*)(?:[-*+]|\d+[.)])\s+", line)
        if bullet:
            out.append((number, "bullet", len(bullet.group(1).expandtabs(4)), line))
            continue
        out.append((number, "text", len(line) - len(line.lstrip()), line))
    return out


def heading_section(text, title_pattern, levels=(1, 2, 3, 4, 5, 6)):
    """The raw text of every section whose heading's title matches ``title_pattern``: from the heading to the next
    heading of the same or a higher level (deeper headings are part of the section)."""
    lines = text.splitlines()
    scanned = _scan(text)
    found = []
    for index, (number, kind, level, line) in enumerate(scanned):
        if kind != "heading" or level not in levels:
            continue
        title = HEADING.match(line).group(2)
        if not re.search(title_pattern, title, re.I):
            continue
        end = len(lines)
        for later_number, later_kind, later_level, _ in scanned[index + 1:]:
            if later_kind == "heading" and later_level <= level:
                end = later_number
                break
        found.append("\n".join(lines[number:end]))
    return found


def bullet_region(text, lead_pattern):
    """The raw text of every bullet whose first words match ``lead_pattern`` (a stage bullet led by ``A9``): the
    bullet and what belongs to it, up to the next heading, the next bullet at its own or a shallower indent, or a
    blank line followed by text at its own indent."""
    lines = text.splitlines()
    scanned = _scan(text)
    found = []
    for index, (number, kind, indent, line) in enumerate(scanned):
        if kind != "bullet":
            continue
        body = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line).replace("**", "").replace("__", "").replace("`", "")
        if not re.match(lead_pattern, body, re.I):
            continue
        end, blank = len(lines), False
        for later_number, later_kind, later_indent, later_line in scanned[index + 1:]:
            if later_kind == "heading":
                end = later_number
                break
            if later_kind == "bullet" and later_indent <= indent:
                end = later_number
                break
            if not later_line.strip():
                blank = True
                continue
            if later_kind in ("text", "fence", "fenced") and blank and (len(later_line) - len(later_line.lstrip())) <= indent:
                end = later_number
                break
            blank = False
        found.append("\n".join(lines[number:end]))
    return found


# --------------------------------------------------------------------------
# S1: A9's step and its seven steps
# --------------------------------------------------------------------------

def a9_regions(text):
    """A9's step, in either form the ticket allows: a heading that names A9 (its section) or a bullet led by A9
    (the way the A0 to A8 bullets are written). Several are joined in file order."""
    regions = [(text.find(raw), raw) for raw in heading_section(text, r"\bA9\b")]
    regions += [(text.find(raw), raw) for raw in bullet_region(text, r"A9\b")]
    regions.sort()
    seen, joined = set(), []
    for position, raw in regions:
        if raw not in seen:
            seen.add(raw)
            joined.append(raw)
    return joined


_NAMED_QUESTION = (r"\b(?:never|not|no|nor|without)\b[^.;]{0,60}?\b(?:named|particular|specific|single|individual|"
                   r"one)\s+questions?\b")
_FIVE_POINTS = r"\bwithin (?:5|five)(?:\.0)?(?: percentage)? (?:points?|pts?|percent|%)"

# Each step: (number, label, anchor, [(what, pattern), ...]). The anchor places the step; the checks must hold
# inside the step's own stretch (its anchor to the next step's anchor). Words are the KPI line's.
STEPS = [
    (1, "assess and plan", r"\bassess\b[^.;]{0,60}?\bplan", [], 0),
    (2, "census the stated links and build the graph from them", r"\bcensus\b[^.;]{0,100}?\blinks?\b",
     [("build the graph", r"\bgraph\b")], 0),
    (3, "build the store with the standard and its refresh", r"\bbuil[dt]\w*\b[^.;]{0,40}?\bstore\b",
     [("the standard", r"\bstandard\b"), ("its refresh", r"\brefresh\w*\b")], 0),
    (4, "have the verdict set and the tuning set written", r"\bverdict set\b[^.;]{0,100}?\btuning set\b",
     [("written", r"\bwr(?:itten|ite|ites|iting)\b")], 80),
    (5, "measure the tuning set; fix only the structure, never a named question, until its halves agree "
        "within 5 points", r"\bmeasur\w*\b[^.;]{0,40}?\btuning set\b",
     [("fix only the structure", r"\bonly\b[^.;]{0,25}?\bstructur\w+|\bstructur\w+\b[^.;]{0,25}?\bonly\b"),
      ("never a named question", _NAMED_QUESTION),
      ("its halves agree", r"\bhalves\b.{0,60}?\bagree\w*\b|\bagree\w*\b.{0,60}?\bhalves\b"),
      ("within 5 points", _FIVE_POINTS)], 0),
    (6, "declare and measure the verdict set once", r"\bdeclar\w*\b",
     [("measure", r"\bmeasur\w*\b"), ("the verdict set", r"\bverdict set\b"),
      ("once", r"\bonce\b|\bonly one time\b|\bone time\b")], 0),
    (7, "record every method and figure", r"\brecord\w*\b[^.;]{0,40}?\b(?:every|each|all)\b[^.;]{0,40}?\bmethods?\b",
     [("figure", r"\bfigures?\b")], 0),
]


def check_steps(region_text):
    """Problems of the seven steps in ``region_text`` (``[]`` when each stands, in order, with its content).

    Anchors are found left to right: step k is the first match after step k-1's anchor. A step whose anchor exists
    only earlier is out of order; one that exists nowhere is missing."""
    text = flat(region_text)
    problems, anchors, cursor = [], [], 0
    for number, label, anchor, checks, lead in STEPS:
        found = re.compile(anchor, re.S).search(text, cursor)
        if found:
            anchors.append((number, found.start(), found.end()))
            cursor = found.end()
            continue
        anywhere = re.compile(anchor, re.S).search(text)
        if anywhere:
            problems.append(f"step {number} ({label}) is out of order: it stands before step "
                            f"{anchors[-1][0] if anchors else '1'}'s")
        else:
            problems.append(f"step {number} ({label}) is missing")
        anchors.append((number, None, None))
    for index, (number, label, _anchor, checks, lead) in enumerate(STEPS):
        start = anchors[index][1]
        if start is None:
            continue
        stop = len(text)
        for _, later_start, _ in anchors[index + 1:]:
            if later_start is not None:
                stop = later_start
                break
        begin = start
        if lead:  # a word of the step may stand just before its anchor ("write the verdict set and the tuning set")
            floor = next((anchors[i][2] for i in range(index - 1, -1, -1) if anchors[i][2] is not None), 0)
            begin = max(floor, start - lead)
        stretch = text[begin:stop]
        for what, pattern in checks:
            if not re.search(pattern, stretch, re.S):
                problems.append(f"step {number} ({label}) does not say {what!r} in its own words")
    return problems


def check_pointer(region_text):
    return [] if PRACTICE_REL in region_text.replace("`", "") else [f"A9's step does not point to {PRACTICE_REL}"]


def run_skill_validator():
    """The skills check of S1's Verify, judged by exit code in a child process. Returns ``(exit_code, stdout)``."""
    done = subprocess.run(
        [sys.executable, "-m", "gov.check.skill_validator", "--both-layouts",
         "template/governance/kernel/skills/adopt"],
        cwd=REPO_ROOT, capture_output=True, text=True, env=child_env(), timeout=120)
    return done.returncode, done.stdout + done.stderr


# --------------------------------------------------------------------------
# S2: the Verify section and its four statements
# --------------------------------------------------------------------------

def verify_sections(text):
    """Every section headed ``Verify clauses for adopted tickets`` (level ``##`` or ``###``), raw."""
    return heading_section(text, r"^`?" + re.escape(VERIFY_HEADING) + r"`?\s*:?$", levels=(2, 3))


def units(text):
    """The sentences and list items of ``text`` (flattened), the grain a statement is looked for in."""
    pieces = re.split(r"(?<=[.;:!?])\s+|\n\s*(?:[-*+]|\d+[.)])\s+|\n\s*\n", text)
    return [flat(piece) for piece in pieces if piece.strip()]


def window_hits(text, trigger, terms, before=250, after=350):
    """The best window around a ``trigger`` match: the terms found in it. Returns ``(found, missing)`` for the
    window with the most terms (or all terms missing when no trigger exists)."""
    body = flat(text)
    best = ([], list(terms))
    for match in re.finditer(trigger, body):
        window = body[max(0, match.start() - before):match.end() + after]
        found = [name for name, pattern in terms.items() if re.search(pattern, window)]
        if len(found) > len(best[0]):
            best = (found, [name for name in terms if name not in found])
    return best


def sentence_with(text, patterns):
    """The first unit that matches every pattern, or ``None``."""
    for unit in units(text):
        if all(re.search(pattern, unit) for pattern in patterns):
            return unit
    return None


WHEN_ABOUT_TO_LAUNCH = [r"\babout to (?:launch|be launched|start|be started)\b"]
WHEN_NOT_WHOLE_TRACKER = [
    r"(?:\bnot\b|\bnever\b|\bno\b|\bnor\b|\bwithout\b|\brather than\b|\binstead of\b)[^.;]{0,80}?"
    r"\b(?:whole|entire|all|every)\b[^.;]{0,40}?\b(?:tracker|backlog|tickets?)\b"
    r"|\b(?:whole|entire)\s+tracker\b[^.;]{0,40}?\b(?:not|never)\b"
    r"|\bnot\b[^.;]{0,20}?\bthe tracker\b"]
WHO_WRITES = [r"\bproduct[- ]spec\b", r"\bwr(?:ite|ites|itten|iting)\b", r"\bclauses?\b|\bverify\b"]
WHAT_CHECKS_TRIGGER = r"\bcheck\w*\b|\bverif\w*\b|\breview\w*\b"
WHAT_CHECKS_TERMS = {
    "the tool": r"\btool\b|--verify-apply|verify[- ]apply|\bgov adopt\b",
    "the ticket's test designer": r"\btest[- ]designer\b",
    "the auditor's sample": r"\bauditor\b[^.;]{0,40}?\bsample\b|\bsample\b[^.;]{0,40}?\bauditor\b",
}
OWNER_APPROVES_ONCE = [r"\bowner\b", r"\bapprov\w+\b", r"\bonce\b|\bone time\b|\bone-time\b|\bonly one time\b"]


# --------------------------------------------------------------------------
# S3: the CIT-P record
# --------------------------------------------------------------------------

def committed_after_hash():
    """The kernel skill's sha256 as this ticket last committed it: the blob at the latest commit after the base that
    changes the kernel skill and carries ``Task: DAEO-pg6i``. A later ticket that changes the skill does not move it
    (that commit carries another Task); an intermediate blob of this ticket is never the answer.

    Returns ``(sha256 or None, commit or None)``."""
    done = git("log", "--format=%H%x1f%(trailers:key=Task,valueonly,separator=%x2c)%x1e", f"{BASE_COMMIT}..HEAD", "--",
               KERNEL_REL)
    for entry in done.stdout.decode("utf-8", "replace").split("\x1e"):
        if "\x1f" not in entry:
            continue
        commit, tasks = entry.strip().split("\x1f", 1)
        if TICKET in [task.strip() for task in tasks.split(",")]:
            blob = git("show", f"{commit}:{KERNEL_REL}").stdout
            return sha256_of(blob), commit
    return None, None


def hash_lines(text, digest):
    """The lines of ``text`` (and the line before each) that hold ``digest``, lower-cased: where a label is looked for."""
    lines = text.splitlines()
    found = []
    for index, line in enumerate(lines):
        if digest in line.lower():
            previous = next((lines[i] for i in range(index - 1, max(index - 3, -1), -1) if lines[i].strip()), "")
            found.append((line + " " + previous).lower())
    return found


NUMBER_WORDS = {"no": 0, "none": 0, "zero": 0, "nothing": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def _num(token):
    token = token.lower()
    return int(token) if token.isdigit() else NUMBER_WORDS.get(token)


def stated_counts(text):
    """Every pair of numbers the record could be stating as lines added and removed: ``(added_set, removed_set)``."""
    low = text.lower().replace("`", "").replace("*", "")
    number = r"(\d+|no|none|zero|nothing|one|two|three|four|five)"
    added, removed = set(), set()
    for found in re.finditer(number + r"\s+(?:lines?\s+)?added", low):
        added.add(_num(found.group(1)))
    for found in re.finditer(r"\badded\W{1,8}(\d+)\b", low):
        added.add(_num(found.group(1)))
    for found in re.finditer(number + r"\s+(?:lines?\s+)?(?:removed|deleted|taken out)", low):
        removed.add(_num(found.group(1)))
    for found in re.finditer(r"\b(?:removed|deleted)\W{1,8}(\d+)\b", low):
        removed.add(_num(found.group(1)))
    for found in re.finditer(r"(?<![\w.])\+\s?(\d+)\s*[/,; ]?\s*[-−–]\s?(\d+)(?!\d)", low):
        added.add(int(found.group(1)))
        removed.add(int(found.group(2)))
    for found in re.finditer(r"\b(\d+)\s+insertions?\(\+\),\s+(\d+)\s+deletions?\(-\)", low):
        added.add(int(found.group(1)))
        removed.add(int(found.group(2)))
    for found in re.finditer(r"numstat\W{0,12}(\d+)\s+(\d+)(?!\d)|\b(\d+)\s+(\d+)\s+[^\s|]*skill\.md", low):  # numstat rows
        found = [g for g in found.groups() if g is not None]
        added.add(int(found[0]))
        removed.add(int(found[1]))
    return {n for n in added if n is not None}, {n for n in removed if n is not None}


def actual_numstat(commit):
    """``(added, removed)`` of the kernel skill between the base and ``commit`` (``git diff --numstat``)."""
    out = git("diff", "--numstat", BASE_COMMIT, commit, "--", KERNEL_REL).stdout.decode().split()
    return int(out[0]), int(out[1])


def actual_diff_lines(commit):
    """``(added_lines, removed_lines)`` of the kernel skill, base to ``commit``, as text (blank lines dropped)."""
    out = git("diff", "--unified=0", BASE_COMMIT, commit, "--", KERNEL_REL).stdout.decode("utf-8", "replace")
    added, removed = [], []
    for line in out.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+") and line[1:].strip():
            added.append(line[1:].strip())
        elif line.startswith("-") and line[1:].strip():
            removed.append(line[1:].strip())
    return added, removed


VERDICT = re.compile(r"verdict\W{0,12}`?\*{0,2}\s*(pass(?:ed)?|fail(?:ed)?|ready|not ready|blocked|approved|rejected|"
                     r"pending|none yet|tbd|todo|to be recorded)\b", re.I)


def verdicts(text):
    """The verdict values the record states, in file order, upper-cased."""
    return [found.group(1).upper() for found in VERDICT.finditer(text.replace("`", ""))]


def owner_approval_lines(text):
    """Where the record has a place for the owner's approval of the bytes: ``(line index, context text)`` pairs."""
    lines = text.splitlines()
    places = []
    for index, line in enumerate(lines):
        low = line.lower()
        if re.search(r"\bowner\b.{0,60}?\bapprov\w*|\bapprov\w*\b.{0,60}?\bowner\b", low):
            context = " ".join(lines[max(0, index - 1):index + 4]).lower()
            places.append((index, context))
    return places

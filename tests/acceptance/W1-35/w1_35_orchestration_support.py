"""Support code for the W1-35 follow-up cases (DEC-537, DEC-539, DEC-541): the orchestration skill, the ticket
lead section of the orchestrator role file, the five brief templates and the skill-regression check.

The cases read delivered text. This module holds the paths (the public interface), the reader that cuts a
Markdown text into statements, and the table of rows with the ideas each row must carry.

**A statement** is one paragraph, one top-level list item with its indented lines, one table row or one fenced
block. A paragraph that ends with a colon and the list that follows it directly are also read together as one
statement. **A clause is found** when one statement of the corpus carries every idea of the clause; an idea is a
pattern matched without regard to case (unless the pattern says otherwise) on the statement with its whitespace
collapsed. No clause is an exact sentence.

**The corpus of a row** is the orchestration skill and every file of the kernel's templates folder that the skill
names by its file name (DEC-539: the rows are divided between the skill and the templates it names).

Standard library and PyYAML only. Nothing here imports ``src/gov`` and nothing names a held-out path.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]

KERNEL_REL = "template/governance/kernel"
SKILL_NAME = "orchestration"
SKILL_FOLDER_REL = f"{KERNEL_REL}/skills/{SKILL_NAME}"
SKILL_REL = f"{SKILL_FOLDER_REL}/SKILL.md"
ROLES_REL = f"{KERNEL_REL}/roles"
ROLE_REL = f"{ROLES_REL}/orchestrator.md"
TEMPLATES_REL = f"{KERNEL_REL}/templates"
CHECKS_REL = f"{KERNEL_REL}/checks"
CHECK_GLOB = "skill-regression-orchestration*.yaml"
EXISTING_CHECK_REL = f"{CHECKS_REL}/skill-regression-a.yaml"
SOURCE_SKILL_REL = f"template/.rulesync/skills/{SKILL_NAME}/SKILL.md"
SOURCE_SUBAGENTS_REL = "template/.rulesync/subagents"
SOURCE_ROLE_REL = f"{SOURCE_SUBAGENTS_REL}/orchestrator.md"

# The five brief templates: the file names are this suite's public interface (README).
BRIEFS = {
    "test designer": "brief-test-designer.md",
    "engineer": "brief-engineer.md",
    "reviewer": "brief-reviewer.md",
    "product-spec worker": "brief-product-spec.md",
    "lead": "brief-lead.md",
}
TEST_DESIGNER_BRIEF = BRIEFS["test designer"]

# The roles of the kernel (W1-33, W1-46): the follow-up adds none.
ROLE_FILES = ("engineer.md", "independent-auditor.md", "independent-test-designer.md", "orchestrator.md",
              "product-spec.md", "research.md")

# W1-08 reads a templates file with one of these words in its name as a record template and validates its
# frontmatter against that record's schema (tests/acceptance/W1-08/w1_08_support.py, RECORD_TYPES).
RECORD_TEMPLATE_WORDS = ("decision", "madr", "adr", "ticket", "lesson", "failure", "research", "gate", "package",
                         "checkpoint")

STANDING_SENTENCES = (
    "Run everything in the foreground, one command after another: your session ends with your last message, and "
    "nothing started in the background is ever read. Return only after your commit exists.",
    "No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree.",
    "Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one "
    "(DEC-508). Never read `.claude/settings.json`, in this worktree or anywhere.",
)

# What a brief is filled in with: a placeholder whose text names each of these.
PLACEHOLDER = re.compile(r"<(?![!/])([^<>\n`]{1,80})>|\{\{([^{}\n]{1,80})\}\}|\{([^{}\n]{1,80})\}|\[([A-Z][A-Z _-]{1,60})\]")
PLACEHOLDER_KINDS = {
    "ticket": r"ticket|\bid\b",
    "profile": r"profile",
    "paths": r"path",
    "sources": r"source",
    "decisions": r"decision",
}

# DEC-534: tests are named without a language or a runner.
LANGUAGE_BOUND = {
    "pytest": r"pytest",
    "python": r"python",
    "a Python path or file": r"\.py\b|conftest",
    "this repository's acceptance folder": r"tests/acceptance",
}
# DEC-539: this repository's own values are a project's values, given by a placeholder.
REPOSITORY_VALUES = {
    "a ticket id of this repository": r"\bW1-\d+|\bDAEO-",
    "a branch name of this repository": r"\bw1/",
    "a folder of this repository's wave": r"gov-os-worktrees|Dynamic-Agentic|/home/|~/\.local|\.nvm\b",
    "the workbench": r"workbench",
    "a model id or model name": r"claude-[a-z]+-\d|\b(opus|sonnet|haiku|fable)\b",
    "an installed version": r"\b\d+\.\d+\.\d+\b",
}

FULL, STANDARD, LITE = r"(?-i:\bFULL\b)", r"(?-i:\bSTANDARD\b)", r"(?-i:\bLITE\b)"
NEVER = r"\b(never|not|no|nobody|nothing|none|without|only)\b"

# Each row of the specification: the decisions it is stated with, and its clauses. A clause is
# ``(what the reader must find, [ideas])``; every idea of a clause stands in one statement.
ROWS = {
    "parallel tickets": {
        "ids": (),
        "clauses": (
            ("a worktree per independent ticket", [r"worktree", r"ticket", r"\b(each|per|every|own|one)\b"]),
            ("the worktree is cut from the integration branch", [r"worktree|branch", r"integration branch"]),
            ("a ticket lead per ticket, started in that worktree with its identity",
             [r"\blead", r"worktree", r"identit"]),
            ("no two tickets in flight with overlapping paths", [r"overlap", r"path"]),
            ("a stated ceiling of tickets in flight",
             [r"ceiling|at most|up to|no more than|maximum|limit", r"ticket",
              r"in flight|at a time|at once|parallel|concurrent|running"]),
            ("the resource gate before each start",
             [r"resource gate", r"before (each|every|any|a)\b|(each|every) start"]),
            ("the gate reads free memory", [r"memory", r"free|available"]),
            ("the gate reads the load against the core count", [r"\bload", r"\bcores?\b|\bcpus?\b|processor"]),
            ("heavy tickets count double", [r"heavy", r"double|twice|\btwo\b"]),
            ("a ticket idle on an owner answer frees its slot",
             [r"idle|wait", r"owner", r"slot|ceiling|count|free"]),
            ("no worktree is left behind", [r"worktree", r"left behind|leave|behind|remove"]),
        ),
    },
    "integration order": {
        "ids": ("DEC-536", "DEC-498"),
        "clauses": (
            ("the lead returns DONE", [r"(?-i:\bDONE\b)", r"\blead|return"]),
            ("the orchestrator verifies the return itself, by its own runs",
             [r"verif", r"itself|its own|own runs?|re-?runs?|again"]),
            ("the governance checks are read against the last known state",
             [r"check", r"last known|known state|baseline"]),
            ("the merge into the integration branch is the orchestrator's alone",
             [r"merge", r"integration branch", r"\b(only|alone|nobody|no one)\b"]),
            ("never a merge into the main branch", [r"main branch", NEVER]),
            ("the close runs the ticket's tests and the regression on the merge commit",
             [r"close", r"merge commit", r"regression"]),
            ("a full regression where the close does not follow directly", [r"full regression", r"close"]),
            ("residuals are recorded", [r"residual", r"record|written|note|kept|list"]),
            ("worktree and branch are removed", [r"worktree", r"branch", r"remov|delet"]),
            ("for a FULL ticket a fresh reviewer probes the final code before the merge",
             [FULL, r"reviewer", r"before (the |its |a )?merg|before (it is|being) merged"]),
            ("nothing is committed after the probed head",
             [r"nothing|no (further |later |more |new )?commit", r"after", r"head|prob"]),
        ),
    },
    "the ticket loop": {
        "ids": ("DEC-413", "DEC-096"),
        "clauses": (
            ("tests first, by a fresh test designer", [r"test designer", r"fresh", r"first|before"]),
            ("checked red for the stated reason", [r"\bred\b", r"reason"]),
            ("a fresh implementer", [r"fresh", r"implementer|engineer|product-spec"]),
            ("verify on the ticket's tests, every earlier suite and the builder tests",
             [r"ticket's (own )?(acceptance )?tests|acceptance tests", r"earlier|previous|other", r"builder"]),
            ("a second review is the last", [r"second", r"review", r"last|final|no (third|further)"]),
            ("after it only fail-open holes and losses of work are fixed",
             [r"fail[- ]open", r"los(s|ses|e|es|t|ing)\b", r"work"]),
            ("the rest are residuals", [r"residual", r"rest|other|remain|everything else"]),
            ("the loop count is held by the lead and never disclosed",
             [r"(loop|iteration) count|count of (loops|iterations)", r"\b(never|not|nobody|no one)\b",
              r"disclos|reveal|tell|told|share"]),
            ("an escalation after three iterations that do not converge",
             [r"escalat", r"three|\b3\b", r"converg"]),
            ("the return form DONE", [r"(?-i:\bDONE\b)"]),
            ("the return form PACKAGES", [r"(?-i:\bPACKAGES\b)"]),
            ("the return form ESCALATION", [r"(?-i:\bESCALATION\b)"]),
            ("the return form LEAD_CHECKPOINT", [r"(?-i:\bLEAD_CHECKPOINT\b)"]),
        ),
    },
    "decisions": {
        "ids": ("DEC-220", "DEC-416", "DEC-463"),
        "clauses": (
            ("delegation: the priority", [r"delegat|decide", r"(?-i:\bP2\b)", r"(?-i:\bP3\b)"]),
            ("delegation: reversible", [r"reversib"]),
            ("delegation: the recommendations agree", [r"recommendation", r"agree|same|match|coincid"]),
            ("delegation: the confidence", [r"confidence", r"medium"]),
            ("delegation: nothing of the charter, the master rules or the contract's scope",
             [r"charter", r"master rule", r"contract"]),
            ("delegation: no weakening of the guard or containment",
             [r"guard", r"containment", r"weak|loosen"]),
            ("delegation: not the held-out path", [r"held-out"]),
            ("delegation: not installs", [r"install"]),
            ("delegation: not merges into the main branch", [r"merg", r"main branch"]),
            ("delegation: not releases", [r"release"]),
            ("stricter-only decisions", [r"stricter"]),
            ("a decision is recorded before the change it authorises",
             [r"record", r"before", r"change|appl|authori[sz]"]),
            ("at most five packages with the owner at a time", [r"five|\b5\b", r"package"]),
            ("a P1 may bypass", [r"(?-i:\bP1\b)", r"bypass|exceed|above|beyond|outside"]),
            ("the digest of delegated decisions", [r"digest", r"delegat"]),
            ("owner answers are recorded as accepted", [r"owner", r"answer", r"accept"]),
            ("with their own commit trailer", [r"trailer", r"decision|answer", r"\b(own|separate|its)\b"]),
        ),
        # The package's fields: one document of the corpus names all of them.
        "one_document": (
            ("the package's fields",
             [r"question", r"why now", r"option", r"impact", r"reversib", r"cost", r"recommendation",
              r"confidence"]),
        ),
    },
    "stops": {
        "ids": (),
        "clauses": (
            ("a stop only for owner packages, an escalation, an authentication stop or the exit",
             [r"stop", r"package", r"escalat", r"authenticat|(?-i:AUTH_REQUIRED)", r"\bexit\b"]),
            ("never a stop to deliver a digest", [r"digest", r"stop", NEVER]),
            ("every unaffected ticket keeps running while packages are open",
             [r"package", r"open|wait|pending", r"continu|keep|running|carry on", r"ticket"]),
            ("short blocks an owner can read on a phone", [r"short|brief|compact", r"phone|mobile"]),
            ("the closed count is taken from the ticket files",
             [r"closed", r"count|number", r"ticket", r"files?\b"]),
            ("open tickets are given by id", [r"open", r"ticket", r"\bids?\b"]),
        ),
    },
    "sessions": {
        "ids": ("DEC-460", "DEC-420"),
        "clauses": (
            ("worker identity through the settings argument", [r"identit", r"settings"]),
            ("the model is named on every launch",
             [r"\bmodel", r"\b(every|each|always|any)\b", r"launch|start|session"]),
            ("leads and workers in the background, with the absolute path of the CLI",
             [r"background", r"absolute path"]),
            ("never a bare call in the foreground", [r"foreground", r"\bbare\b", NEVER]),
            ("never two writing sessions in one tree", [r"\btwo\b", r"writ", r"tree"]),
            ("never a commit in a tree while a worker's command runs there",
             [r"commit", r"while|during", r"\brun", r"worker|command|session"]),
            ("on an authentication or access error no retry loop",
             [r"authenticat|access", r"retr(y|ies|ied)"]),
            ("a stop named AUTH_REQUIRED", [r"(?-i:\bAUTH_REQUIRED\b)", r"stop"]),
            ("the orchestrator reads only a lead's final summary",
             [r"summary", r"\blead", r"\b(only|never)\b"]),
        ),
    },
    "briefs": {
        "ids": ("DEC-462", "DEC-221"),
        "clauses": (
            ("a test designer's brief states behaviour and sources only",
             [r"behaviou?r", r"source", r"\b(only|never|no|nothing)\b"]),
            ("FULL: thorough", [FULL, r"thorough"]),
            ("STANDARD: every line's success and failure plus the key edge cases",
             [STANDARD, r"success", r"failure", r"edge"]),
            ("LITE: one test per line", [LITE, r"\b(one|single|a)\b", r"\bper\b|\beach\b|\bevery\b"]),
            ("no combinatorial expansion", [r"combinatorial"]),
            ("a worker gets only its brief and the decisions that apply",
             [r"\bonly\b", r"brief", r"decision"]),
            ("never the orchestrator's notes or another worker's output",
             [r"notes", r"(an)?other worker", r"output"]),
            ("a worker never bulk-copies or clones the tree",
             [r"cop(y|ies|ying)", r"clon", r"tree|repositor|folder", NEVER]),
        ),
        "verbatim": STANDING_SENTENCES[:2],
    },
    "commits": {
        "ids": ("DEC-476", "DEC-491"),
        "clauses": (
            ("the trailers stand in the final block", [r"trailer", r"final|last", r"block|paragraph"]),
            ("the trailers: task, role, capability ids",
             [r"trailer", r"\btask\b", r"\brole\b", r"implements|capabilit"]),
            ("the rewrite reason on a test designer's rewrite after implementation began",
             [r"rewrite", r"reason", r"designer", r"after|once|began|begun|exists?"]),
            ("a commit touching a ticket's file names that ticket",
             [r"commit", r"ticket('s)? file", r"nam(e|es|ing)\b|trailer|cit(e|es|ing)\b"]),
            ("history is never rewritten", [r"history", r"rewrit|rebase|amend", NEVER]),
            ("nobody but the owner pushes", [r"push", r"owner"]),
        ),
    },
    "checkpoints and context": {
        "ids": ("DEC-511",),
        "clauses": (
            ("a real checkpoint at each round boundary of a ticket", [r"checkpoint", r"round"]),
            ("never a checkpoint written only to pass the close", [r"checkpoint", r"pass", r"close", NEVER]),
            ("the orchestrator's own checkpoint is updated after every merge, close and stop",
             [r"checkpoint", r"merge", r"close", r"stop", r"after|every|each"]),
            ("with the hooks in place the session compacts and continues from the injected checkpoint",
             [r"hook", r"compact", r"inject", r"continu|resum"]),
            ("it does not stop for context", [r"context", r"stop", NEVER]),
            ("state is re-derived from git and the tickets when the checkpoint is older than the state",
             [r"\bgit\b", r"ticket", r"checkpoint", r"older|stale|behind|out of date|outdated"]),
        ),
    },
    "temp hygiene and protected files": {
        "ids": ("DEC-508", "DEC-525"),
        "clauses": (
            ("a session's temporary folder is its own and is removed with it",
             [r"temp", r"folder|director", r"\bown\b", r"remov|delet"]),
            ("nothing is left in or read from another session's folders",
             [r"(an)?other session", r"folder|director", r"read|le(ave|aves|ft)\b"]),
            ("no glob, search or listing over the project's governance folder",
             [r"glob", r"search", r"list", r"governance"]),
            ("the settings file and the held-out file are never read",
             [r"settings", r"held-out", r"read", NEVER]),
        ),
    },
    "learning metrics": {
        "ids": ("DEC-106",),
        "clauses": (
            ("the metrics are recorded at each close", [r"metric", r"close"]),
            ("KPI disputes", [r"dispute"]),
            ("acceptance tests rewritten after implementation, with reasons", [r"rewr(itten|ite|ote)", r"reason"]),
            ("lines against the estimate", [r"\blines?\b|\bLOC\b", r"estimate"]),
            ("wall time from claim to close", [r"wall", r"claim", r"close"]),
            ("merge conflicts", [r"conflict"]),
            ("false findings", [r"false finding"]),
            ("governance share", [r"governance share"]),
        ),
    },
}

# DEC-537: built in Wave 2; until then rules followed by hand.
WAVE_2_ITEMS = {
    "the resource gate as a command": [r"resource gate"],
    "the launcher refusing a launch without a model": [r"launcher|launch", r"\bmodel"],
    "AUTH_REQUIRED as a mechanism": [r"(?-i:\bAUTH_REQUIRED\b)"],
    "starting leads through the launcher": [r"\bleads?\b", r"launcher"],
}
BY_HAND = r"by hand|manual"
NOT_ENFORCED = (r"not (yet )?(enforced|checked|refused|built|held)|no (mechanism|command|code)|"
                r"not (yet )?(a|by a|by any) mechanism|nothing enforces")

# DEC-541, CAP-28: the parts of ``gov status --json`` an answer is given from (W1-32).
STATUS_COMMAND = r"gov status --json"
STATUS_QUESTION = (r"\basks?\b|asked|question|plain (words|language)|natural language|where (things|the work|it) "
                   r"stands?|in chat")
STATUS_PARTS = {
    "tickets": r"ticket",
    "open packages": r"package",
    "gates": r"\bgates?\b",
    "readiness": r"readiness",
    "governance share": r"\bshare\b",
    "pause state": r"paus",
    "health": r"health|doctor",
}
NOT_READ = r"not (be(en)? )?read|unread|could not read|cannot be read|unmeasured|not measured"
RECALL = r"recall|from memory|remember"


# --------------------------------------------------------------------------
# Files
# --------------------------------------------------------------------------

def path(rel):
    return REPO_ROOT / rel


def read(rel):
    """The text of a delivered file; the case fails here, with the path, until the file exists."""
    file = path(rel)
    assert file.is_file(), f"{rel} does not exist"
    return file.read_text(encoding="utf-8")


def split_frontmatter(text):
    """``(frontmatter mapping or None, body)``. The blank lines between the frontmatter and the body's first
    line are dropped: rulesync drops them (W1-38's one tolerated difference)."""
    if not text.startswith("---"):
        return None, text.lstrip("\n")
    end = text.find("\n---", 3)
    if end < 0:
        return None, text.lstrip("\n")
    try:
        front = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        front = None
    return (front if isinstance(front, dict) else None), text[end + 4:].partition("\n")[2].lstrip("\n")


def brief_rel(kind):
    return f"{TEMPLATES_REL}/{BRIEFS[kind]}"


def check_declarations():
    return sorted(path(CHECKS_REL).glob(CHECK_GLOB))


def check_declaration():
    """The parsed declaration of the new skill's check, with its path."""
    found = check_declarations()
    assert found, f"no check declaration matching {CHECK_GLOB} under {CHECKS_REL}/"
    assert len(found) == 1, f"more than one declaration matches {CHECK_GLOB}: {[p.name for p in found]}"
    data = yaml.safe_load(found[0].read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{found[0].name} is not a YAML mapping"
    return found[0], data


# --------------------------------------------------------------------------
# Statements and sections
# --------------------------------------------------------------------------

_LIST_ITEM = re.compile(r"^([-*+]|\d+[.)])\s+")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def collapse(text):
    return " ".join(text.split())


def statements(text):
    """``[(section index, statement)]`` for a Markdown text (see the module's note on what a statement is)."""
    _front, body = split_frontmatter(text)
    found, current, kind, section, fence = [], [], None, 0, False
    runs = []          # (index of the intro paragraph or None, first item index, last item index)

    def close():
        nonlocal current, kind
        if current:
            found.append((section, collapse("\n".join(current)), kind))
        current, kind = [], None

    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            if fence:
                current.append(line)
                close()
                fence = False
            else:
                close()
                current, kind, fence = [line], "fence", True
            continue
        if fence:
            current.append(line)
            continue
        if _HEADING.match(line):
            close()
            section += 1
            continue
        if not line.strip() or line.strip() in ("<!--", "-->"):
            if kind != "item":
                close()
            else:
                current.append("")
            continue
        if _LIST_ITEM.match(line):
            close()
            current, kind = [line], "item"
        elif line.lstrip().startswith("|"):
            close()
            found.append((section, collapse(line), "row"))
        elif kind == "item" and (line[0].isspace() or current[-1] != ""):
            current.append(line)
        else:
            if kind == "item":
                close()
            current.append(line)
            kind = kind or "paragraph"
    close()

    # A paragraph that ends with a colon, read together with the list that follows it directly.
    joined = []
    for index, (sect, text_, kind_) in enumerate(found):
        if kind_ == "paragraph" and text_.rstrip().endswith(":"):
            items = []
            for later_section, later_text, later_kind in found[index + 1:]:
                if later_kind != "item" or later_section != sect:
                    break
                items.append(later_text)
            if items:
                joined.append((sect, collapse(" ".join([text_, *items]))))
    return [(sect, text_) for sect, text_, _kind in found] + joined


def section_texts(text):
    """``{section index: every statement of that section, joined}``. Section 0 is the text before any heading."""
    sections = {}
    for section, statement in statements(text):
        sections.setdefault(section, []).append(statement)
    return {section: " ".join(parts) for section, parts in sections.items()}


def carries(statement, ideas):
    return all(re.search(idea, statement, re.IGNORECASE) for idea in ideas)


def statements_with(text, ideas):
    return [(section, statement) for section, statement in statements(text) if carries(statement, ideas)]


# --------------------------------------------------------------------------
# The corpus of the rows
# --------------------------------------------------------------------------

def corpus():
    """``{relative path: text}``: the skill and every templates file the skill names by its file name."""
    skill = read(SKILL_REL)
    documents = {SKILL_REL: skill}
    folder = path(TEMPLATES_REL)
    for file in sorted(folder.iterdir()) if folder.is_dir() else []:
        if file.is_file() and file.name in skill:
            documents[f"{TEMPLATES_REL}/{file.name}"] = file.read_text(encoding="utf-8")
    return documents


def row_faults(row, documents):
    """What a reader cannot find of one row in ``documents``: a list of sentences, empty when all is there."""
    spec, faults = ROWS[row], []
    everything = [statement for text in documents.values() for _section, statement in statements(text)]
    for what, ideas in spec["clauses"]:
        if not any(carries(statement, ideas) for statement in everything):
            faults.append(f"not stated: {what}")
    for what, ideas in spec.get("one_document", ()):
        if not any(carries(collapse(text), ideas) for text in documents.values()):
            faults.append(f"no one document names all of: {what}")
    for sentence in spec.get("verbatim", ()):
        if not any(sentence in collapse(text) for text in documents.values()):
            faults.append(f"the standing sentence is not there word for word: {sentence[:60]}...")
    for decision in spec["ids"]:
        if not any(re.search(rf"\b{decision}\b", text) for text in documents.values()):
            faults.append(f"{decision} is not cited")
    return faults


# --------------------------------------------------------------------------
# The ticket lead section of the role file
# --------------------------------------------------------------------------

def lead_section(text):
    """The section of the role file whose heading names the ticket lead: its text from the line after the
    heading to the next heading of the same or a higher level. None when no heading names it."""
    lines = split_frontmatter(text)[1].splitlines()
    for index, line in enumerate(lines):
        match = _HEADING.match(line)
        if match and re.search(r"\blead\b", match.group(2), re.IGNORECASE):
            level, end = len(match.group(1)), len(lines)
            for later in range(index + 1, len(lines)):
                other = _HEADING.match(lines[later])
                if other and len(other.group(1)) <= level:
                    end = later
                    break
            return "\n".join(lines[index + 1:end])
    return None


# --------------------------------------------------------------------------
# Wording
# --------------------------------------------------------------------------

def wording_faults(text, patterns):
    """``[what was found: the line]`` for every line of ``text`` that matches one of ``patterns``."""
    faults = []
    for number, line in enumerate(text.splitlines(), 1):
        for what, pattern in patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                faults.append(f"line {number}, {what}: {line.strip()[:100]}")
    return faults


def placeholders(text):
    """The text inside every placeholder of ``text``: ``<...>``, ``{{...}}``, ``{...}`` or ``[UPPER CASE]``."""
    return [next(group for group in match.groups() if group) for match in PLACEHOLDER.finditer(text)]

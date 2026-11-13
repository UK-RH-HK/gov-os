"""Support code for the W2-33 acceptance tests (standard library only; reads files, runs nothing).

W2-33 (DAEO-lrre) is a documentation ticket: the kernel role files under ``template/governance/kernel/roles/`` and the
CTO-only install rule in the two copies of the orchestrator's file. The tests read those files; no child process, no
network, no model, never the store. The repository is found from ``Path(__file__)`` (``parents[3]``).

**The checker.** ``role_faults(roles_dir, repo)`` is one function over a roles folder that returns the list of
failures, each one beginning ``"<file>: "`` and naming the rule and the missing or malformed line. The tests use it on
the real folder and, for F2, on copies planted in ``tmp_path``. It judges the line rules of the Interface (the line
forms, the work-order and one-writer sentences, the RUBRIC-2 table) and the roster of files; the content rules of S1,
S3, S6, S8 and S9 are separate functions below, called by their own tests.

**Line forms** are read the way W2-60a's launcher reads them (``src/gov/launch/role.py`` on ``w2/W2-60a``): the line is
found by its head after ``lstrip``, there must be exactly one, and the raw line must ``fullmatch`` the form, so it
starts at column 0 and carries nothing after its value.

**Labelled fields** (for the content rules) are read as W1-33's tests read them: a list item at column 0 that starts
with a bold label, its text, and its indented continuation lines.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ROLES_REL = "template/governance/kernel/roles"
KERNEL_SKILLS_REL = "template/governance/kernel/skills"
RULESYNC_SKILLS_REL = "template/.rulesync/skills"
KERNEL_ORCHESTRATOR_REL = f"{ROLES_REL}/orchestrator.md"
RULESYNC_ORCHESTRATOR_REL = "template/.rulesync/subagents/orchestrator.md"

OPUS = "claude-opus-5-5"
SONNET = "claude-sonnet-5-5"

NINE = ("engineer", "independent-auditor", "independent-test-designer", "orchestrator", "product-spec",
        "qa-engineer", "research", "senior-engineer", "ticket-lead")
FORBIDDEN = ("independent-reviewer",)
README_NAMES = ("readme.md",)     # a README in the folder is not a role file (stated in the tests' README)

EFFORTS = ("low", "medium", "high", "xhigh", "max")
_MODEL = r"claude(?:-[a-z0-9]+)+"
_EFFORT = "|".join(EFFORTS)

# W2-60a's three forms, equal in effect, and the two more of the Interface.
VERSION_HEAD = "- **Version:**"
DEFAULT_HEAD = "- **Launch default:**"
SKILLS_HEAD = "- **Skills:**"
TIER_HEAD = "- **Model tier:**"
CRITICALITY_HEAD = "- **Launch by criticality:**"
WORK_ORDER_HEAD = "- **Work order:**"
ONE_WRITER_HEAD = "- **One writer per worktree:**"

VERSION_LINE = re.compile(r"- \*\*Version:\*\* (\d+\.\d+\.\d+)")
DEFAULT_LINE = re.compile(rf"- \*\*Launch default:\*\* model ({_MODEL}), effort ({_EFFORT})")
SKILLS_LINE = re.compile(r"- \*\*Skills:\*\* ([a-z0-9-]+(?:, [a-z0-9-]+)*)")
TIER_LINE = re.compile(r"- \*\*Model tier:\*\* see Launch default")
CRITICALITY_LINE = re.compile(r"- \*\*Launch by criticality:\*\* (.+)")
_ENTRY = re.compile(rf"(C[0-3]) model ({_MODEL}), effort ({_EFFORT})")
_QA_C2_FULL = re.compile(rf"C2 model ({_MODEL}), effort ({_EFFORT}) on FULL, model ({_MODEL}), effort ({_EFFORT}) otherwise")

WORK_ORDER = (
    "- **Work order:** product-spec writes the spec and KPIs; the independent test designer and the engineer work in "
    "parallel from them, never reading each other's work; the engineer runs the acceptance tests once they are "
    "ready, through gov accept; the QA engineer alone reads both."
)
ONE_WRITER = (
    "- **One writer per worktree:** two sessions that write never share a worktree; a ticket's test designer works "
    "in its own tests worktree, merged by the lead."
)

WELL = "well formed"   # the table's "present and well formed, value not asserted"
_H = (OPUS, "high")
_S = (SONNET, "high")
_CRIT_ENGINEER = {"C3": _H, "C2": _S, "C1": _S, "C0": WELL}
_CRIT_QA = {"C3": _H, "C2": "qa-c2", "C1": _S, "C0": WELL}
# role file -> (Launch default, Launch by criticality or None for "absent"): S7's table (DEC-1120 (2), DEC-1119 (2)).
TABLE = {
    "orchestrator": (_H, None),
    "ticket-lead": (_H, None),
    "senior-engineer": (_H, None),
    "engineer": (_S, _CRIT_ENGINEER),
    "independent-test-designer": (_S, _CRIT_ENGINEER),
    "qa-engineer": (WELL, _CRIT_QA),
    "independent-auditor": (_H, None),
    "product-spec": (_S, None),
    "research": (_S, None),
}
QA_C2 = f"C2 model {OPUS}, effort high on FULL, model {SONNET}, effort high otherwise"


# ---------------------------------------------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------------------------------------------

def roles_dir(repo: Path = REPO_ROOT) -> Path:
    return Path(repo) / ROLES_REL


def role_names(folder: Path) -> list[str]:
    """The role ids of every ``*.md`` in ``folder`` (a README is not a role file), sorted."""
    folder = Path(folder)
    if not folder.is_dir():
        return []
    return sorted(p.stem for p in folder.glob("*.md") if p.is_file() and p.name.lower() not in README_NAMES)


def read(folder: Path, name: str) -> str | None:
    path = Path(folder) / f"{name}.md"
    return path.read_text(encoding="utf-8") if path.is_file() else None


def checked_names(folder: Path) -> list[str]:
    """The nine required roles and every other file found, so a tenth file is checked too."""
    return sorted(set(NINE) | set(role_names(folder)))


def normalise(text: str) -> str:
    return " ".join(text.split())


def statements(text: str) -> list[str]:
    """The sentences and clauses of ``text`` (whitespace folded), split after a full stop or a semicolon."""
    return [part for part in re.split(r"(?<=[.;])\s+", normalise(text)) if part]


def window_matches(text: str, patterns, size: int = 2) -> bool:
    """True when some run of up to ``size`` consecutive statements of ``text`` matches every pattern (any case)."""
    parts = statements(text)
    for start in range(len(parts)):
        joined = " ".join(parts[start:start + size])
        if all(re.search(pattern, joined, re.IGNORECASE) for pattern in patterns):
            return True
    return False


def available_skills(repo: Path = REPO_ROOT) -> set[str]:
    """The skills a role file may name: a kernel skill, a vendored kernel skill or the generated copy's folder."""
    found: set[str] = set()
    for rel in (KERNEL_SKILLS_REL, f"{KERNEL_SKILLS_REL}/superpowers", RULESYNC_SKILLS_REL):
        base = Path(repo) / rel
        if base.is_dir():
            found.update(p.name for p in base.iterdir() if (p / "SKILL.md").is_file())
    return found


# ---------------------------------------------------------------------------------------------------------------
# Lines and fields
# ---------------------------------------------------------------------------------------------------------------

def one_line(text: str, head: str):
    """``(raw line or None, count)``: the line(s) that begin with ``head`` after ``lstrip`` (W2-60a's rule)."""
    found = [line for line in text.splitlines() if line.lstrip().startswith(head)]
    return (found[0] if found else None), len(found)


def line_fault(text: str, head: str, form: re.Pattern, shown: str):
    """None when the file holds ``head``'s line once, whole, at column 0 and of ``form``; else the fault text."""
    line, count = one_line(text, head)
    if count == 0:
        return f"has no line '{shown}'"
    if count > 1:
        return f"holds {count} lines that begin '{head}': it must hold its line '{shown}' once"
    if form.fullmatch(line) is None:
        return f"its line {line.strip()[:120]!r} is not of the form '{shown}' (once, whole, at column 0)"
    return None


_LABELLED = re.compile(r"^- \*\*(?P<label>[^*]+?):\*\*\s*(?P<rest>.*)$")


def fields(text: str) -> dict[str, str]:
    """``{label in lower case: text}`` of every list item at column 0 that starts with a bold label."""
    lines = text.splitlines()
    found: dict[str, str] = {}
    label, chunk = None, []

    def close():
        if label is not None and label not in found:
            found[label] = normalise(" ".join(chunk))

    for index, line in enumerate(lines):
        match = _LABELLED.match(line)
        if match:
            close()
            label, chunk = match.group("label").strip().lower(), [match.group("rest")]
        elif line.startswith("#"):
            close()
            label, chunk = None, []
        elif label is not None:
            if line.strip() and not line[0].isspace():
                if index > 0 and not lines[index - 1].strip():
                    close()
                    label, chunk = None, []
                    continue
            chunk.append(line)
    close()
    return found


def field_by_labels(text: str, patterns) -> tuple[str | None, str]:
    """``(label, text)`` of the first field whose label fullmatches one of ``patterns``; ``(None, "")`` if none."""
    for label, value in fields(text).items():
        if any(re.fullmatch(pattern, label, re.IGNORECASE) for pattern in patterns):
            return label, value
    return None, ""


def head_once_at_column_zero(text: str, head: str) -> str | None:
    """None when exactly one line begins ``head`` and it begins at column 0; else the fault text."""
    lines = [line for line in text.splitlines() if line.lstrip().startswith(head)]
    if not lines:
        return f"has no line that begins '{head}'"
    if len(lines) > 1:
        return f"has {len(lines)} lines that begin '{head}' (it must have one)"
    if not lines[0].startswith(head):
        return f"its line '{head}' is indented (it must begin at column 0)"
    return None


# ---------------------------------------------------------------------------------------------------------------
# The line rules (S2, S4, S5, S7), per file
# ---------------------------------------------------------------------------------------------------------------

def lines_s2(name: str, text: str) -> list[str]:
    """S2: the Version, Launch default and Skills lines, each once, whole and of its form."""
    out = []
    for head, form, shown in (
        (VERSION_HEAD, VERSION_LINE, "- **Version:** x.y.z"),
        (DEFAULT_HEAD, DEFAULT_LINE, "- **Launch default:** model <id>, effort <e>"),
        (SKILLS_HEAD, SKILLS_LINE, "- **Skills:** a, b"),
    ):
        fault = line_fault(text, head, form, shown)
        if fault:
            out.append(f"{name}.md: key {head[4:-3]!r}: the file {fault}")
    return out


def skills_exist(name: str, text: str, available: set[str]) -> list[str]:
    line, count = one_line(text, SKILLS_HEAD)
    match = SKILLS_LINE.fullmatch(line) if count == 1 else None
    if match is None:
        return []   # lines_s2 reports the missing or malformed line
    missing = [skill for skill in match.group(1).split(", ") if skill not in available]
    return [f"{name}.md: names the skill {skill!r}, which has no SKILL.md under {KERNEL_SKILLS_REL}/ "
            f"(or {KERNEL_SKILLS_REL}/superpowers/, {RULESYNC_SKILLS_REL}/)" for skill in missing]


def exact_line(name: str, text: str, head: str, sentence: str, what: str) -> list[str]:
    """``what`` (the Interface's sentence) once, word for word, as one line at column 0."""
    fault = head_once_at_column_zero(text, head)
    if fault:
        return [f"{name}.md: the {what} line: the file {fault}; it must hold, word for word: {sentence}"]
    line, _ = one_line(text, head)
    if line.rstrip() != sentence:
        return [f"{name}.md: the {what} line is not the Interface's sentence word for word; it is {line.strip()!r}; "
                f"it must be: {sentence}"]
    return []


def lines_s4(name: str, text: str) -> list[str]:
    return exact_line(name, text, WORK_ORDER_HEAD, WORK_ORDER, "work-order")


def lines_s5(name: str, text: str) -> list[str]:
    return exact_line(name, text, ONE_WRITER_HEAD, ONE_WRITER, "one-writer-per-worktree")


def parse_criticality(value: str):
    """``({class: (model, effort) | ('qa-c2', value)}, fault)`` from the text after the head."""
    entries = value.split("; ")
    if [entry.split(" ", 1)[0] for entry in entries] != ["C3", "C2", "C1", "C0"]:
        return None, f"its entries are {[e.split(' ', 1)[0] for e in entries]}, not C3; C2; C1; C0 in that order"
    parsed = {}
    for entry in entries:
        cls = entry[:2]
        if cls == "C2" and _QA_C2_FULL.fullmatch(entry):
            parsed[cls] = ("qa-c2", entry)
            continue
        match = _ENTRY.fullmatch(entry)
        if match is None or match.group(1) != cls:
            return None, f"the entry {entry!r} is not of the form '{cls} model <id>, effort <e>'"
        parsed[cls] = (match.group(2), match.group(3))
    return parsed, None


def lines_s7(name: str, text: str) -> list[str]:
    """S7: the Launch default and Launch by criticality lines equal the table; the Model tier line is kept."""
    out = []
    tier = line_fault(text, TIER_HEAD, TIER_LINE, "- **Model tier:** see Launch default")
    if tier:
        out.append(f"{name}.md: key 'Model tier': the file {tier}")
    if name not in TABLE:
        return out   # a file the table does not know: only the forms are judged (S2, S4, S5 and the tier line)
    want_default, want_crit = TABLE[name]
    line, count = one_line(text, DEFAULT_HEAD)
    match = DEFAULT_LINE.fullmatch(line) if count == 1 else None
    if match is None:
        out.append(f"{name}.md: key 'Launch default': missing, repeated or malformed, so S7's value cannot be read")
    elif want_default != WELL and (match.group(1), match.group(2)) != want_default:
        out.append(f"{name}.md: key 'Launch default': it says model {match.group(1)}, effort {match.group(2)}; "
                   f"S7's table gives model {want_default[0]}, effort {want_default[1]}")
    line, count = one_line(text, CRITICALITY_HEAD)
    if want_crit is None:
        if count:
            out.append(f"{name}.md: key 'Launch by criticality': present, but RUBRIC-2 does not vary for this role "
                       f"(S7's table says absent)")
        return out
    if count != 1 or CRITICALITY_LINE.fullmatch(line) is None:
        out.append(f"{name}.md: key 'Launch by criticality': {'missing' if not count else 'repeated or malformed'}; "
                   f"S7's form is '- **Launch by criticality:** C3 model <id>, effort <e>; C2 …; C1 …; C0 …'")
        return out
    parsed, fault = parse_criticality(CRITICALITY_LINE.fullmatch(line).group(1))
    if parsed is None:
        out.append(f"{name}.md: key 'Launch by criticality': {fault}")
        return out
    for cls, want in want_crit.items():
        got = parsed[cls]
        if want == WELL:
            if got[0] == "qa-c2":
                out.append(f"{name}.md: key 'Launch by criticality': {cls} uses the QA form")
            continue
        if want == "qa-c2":
            if got != ("qa-c2", QA_C2):
                out.append(f"{name}.md: key 'Launch by criticality': C2 must be exactly {QA_C2!r}; the file has "
                           f"{(got[1] if got[0] == 'qa-c2' else 'C2 model %s, effort %s' % got)!r}")
        elif got != want:
            out.append(f"{name}.md: key 'Launch by criticality': {cls} is model {got[0]}, effort {got[1]}; "
                       f"S7's table gives model {want[0]}, effort {want[1]}")
    return out


def lines_d10(name: str, text: str) -> list[str]:
    """No role file states the through-D-10 rule (a statement that joins D-10 to a model or a launch)."""
    return [f"{name}.md: states the through-D-10 rule for models ({part[:100]!r}); it is the CTO's launch practice, "
            f"written into no role file (S7)" for part in statements(text)
            if re.search(r"\bD-?10\b", part) and re.search(r"\b(opus|sonnet|model|launch)", part, re.IGNORECASE)]


# ---------------------------------------------------------------------------------------------------------------
# The checker
# ---------------------------------------------------------------------------------------------------------------

def role_faults(folder: Path, repo: Path = REPO_ROOT, rules=("roster", "s2", "skills", "s4", "s5", "s7")) -> list[str]:
    """Every fault of the roles folder ``folder`` against the line rules and the roster; ``[]`` when it passes."""
    folder = Path(folder)
    out: list[str] = []
    available = available_skills(repo)
    if "roster" in rules:
        for name in NINE:
            if not (folder / f"{name}.md").is_file():
                out.append(f"{name}.md: the role file does not exist in {ROLES_REL}/ (the nine are required)")
        for name in FORBIDDEN:
            if (folder / f"{name}.md").exists():
                out.append(f"{name}.md: must not exist: the QA engineer replaces it (DEC-959 item 3)")
    for name in checked_names(folder):
        text = read(folder, name)
        if text is None:
            continue   # reported by the roster rule
        if "s2" in rules:
            out += lines_s2(name, text)
        if "skills" in rules:
            out += skills_exist(name, text, available)
        if "s4" in rules:
            out += lines_s4(name, text)
        if "s5" in rules:
            out += lines_s5(name, text)
        if "s7" in rules:
            out += lines_s7(name, text)
    return out


def copy_folder(destination: Path, repo: Path = REPO_ROOT) -> Path:
    """A copy of the repository's roles folder, to plant a departure in."""
    shutil.copytree(roles_dir(repo), destination)
    return Path(destination)


def synthetic_text(name: str) -> str:
    """A role file that satisfies the line rules (the checker's own control; it says nothing else)."""
    default, crit = TABLE[name]
    model, effort = _S if default == WELL else default
    lines = [f"# {name} (planted control)", "", "- **Version:** 1.0.0",
             f"- **Launch default:** model {model}, effort {effort}"]
    if crit is not None:
        entries = []
        for cls in ("C3", "C2", "C1", "C0"):
            want = crit[cls]
            if want == "qa-c2":
                entries.append(QA_C2)
            elif want == WELL:
                entries.append(f"{cls} model {SONNET}, effort high")
            else:
                entries.append(f"{cls} model {want[0]}, effort {want[1]}")
        lines.append(f"{CRITICALITY_HEAD} " + "; ".join(entries))
    lines += ["- **Skills:** checkpoint, retrieval", "- **Model tier:** see Launch default", WORK_ORDER, ONE_WRITER, ""]
    return "\n".join(lines)


def build_synthetic(destination: Path) -> Path:
    destination = Path(destination)
    destination.mkdir(parents=True)
    for name in NINE:
        (destination / f"{name}.md").write_text(synthetic_text(name), encoding="utf-8")
    return destination


# ---------------------------------------------------------------------------------------------------------------
# Content rules (S1, S3, S6, S8)
# ---------------------------------------------------------------------------------------------------------------

READS_LABELS = (r"reads?", r"reads and writes", r"allowed paths?")
WRITES_LABELS = (r"writes?", r"reads and writes", r"allowed paths?")
HANDOVER_LABELS = (r"hand-?over", r"hand-?off( format)?", r"returns?( and hand-?over)?")
BRIEF_LABELS = (r"(its )?brief( contents?| must (always )?contain)?",)


def field_faults(name: str, text: str, what: str, labels, min_words: int = 5, needs=()) -> list[str]:
    label, value = field_by_labels(text, labels)
    shown = " / ".join(re.sub(r"\\|\(.*?\)\??|\?", "", p) for p in labels)
    if label is None:
        return [f"{name}.md: names no {what}: no line `- **<head>:**` with a head like {shown}"]
    if len(value.split()) < min_words:
        return [f"{name}.md: its {what} (line `- **{label}:**`) says {len(value.split())} words; it must state them"]
    return [f"{name}.md: its {what} (line `- **{label}:**`) does not mention {n!r}" for n in needs
            if not re.search(n, value, re.IGNORECASE)]


def s1_ticket_lead(text: str) -> list[str]:
    name = "ticket-lead"
    return (field_faults(name, text, "reads", READS_LABELS) + field_faults(name, text, "writes", WRITES_LABELS)
            + field_faults(name, text, "handover", HANDOVER_LABELS))


def s8_senior_engineer(text: str) -> list[str]:
    name = "senior-engineer"
    out = (field_faults(name, text, "reads", READS_LABELS) + field_faults(name, text, "writes", WRITES_LABELS)
           + field_faults(name, text, "handover", HANDOVER_LABELS, needs=(r"\bCTO\b",))
           + field_faults(name, text, "brief contents", BRIEF_LABELS, min_words=8, needs=(r"\bstream\b",)))
    line, count = one_line(text, SKILLS_HEAD)
    if count != 1 or SKILLS_LINE.fullmatch(line) is None:
        out.append(f"{name}.md: has no whole `- **Skills:** a, b` line")
    want = f"- **Launch default:** model {OPUS}, effort high"
    line, count = one_line(text, DEFAULT_HEAD)
    if count != 1 or line.rstrip() != want:
        out.append(f"{name}.md: its Launch default line must be exactly `{want}`")
    return out


STREAM_PATTERNS = {
    "core tickets": r"\bcore\b",
    "one by one": r"one by one",
    "before they merge": r"before (they|it|each|the ticket)\w* merge|before merg",
    "the guard": r"\bguard\b",
    "the close": r"\bclose\b",
    "memory's retrieval": r"retrieval",
    "anything that could fail open": r"fail(s)? open",
    "batches": r"batch",
    "up to about five": r"up to about (five|5)\b",
}


def s3_per_stream(text: str) -> list[str]:
    fault = head_once_at_column_zero(text, "- **Per stream:**")
    if fault:
        return [f"qa-engineer.md: the file {fault}"]
    value = fields(text).get("per stream", "")
    return [f"qa-engineer.md: its `- **Per stream:**` line does not state {what} (pattern {pattern!r})"
            for what, pattern in STREAM_PATTERNS.items() if not re.search(pattern, value, re.IGNORECASE)]


QA_ACCESS = {
    "reads the spec, the KPIs, the tests and the code": ([r"\bread", r"\bspec", r"\bKPIs?\b", r"\btests?\b", r"\bcode\b"], 1),
    "changes none of them": ([r"\b(changes?|edits?|modif\w+|alters?)\b", r"\b(neither|none|never|nor|not|no)\b",
                              r"\btests?\b", r"\bcode\b"], 2),
    "writes only its findings report": ([r"\bonly\b", r"\bfindings? report\b"], 1),
}


def s3_qa_access(text: str) -> list[str]:
    return [f"qa-engineer.md: does not state that it {what} (a statement with {patterns})"
            for what, (patterns, size) in QA_ACCESS.items() if not window_matches(text, patterns, size)]


S6_HEADS = {
    "Moderator": ("the moderator duty: it triages every finding against the ticket's own scope and KPIs",
                  [r"\btriage", r"\bevery finding\b", r"\bscope\b", r"\bKPIs?\b", r"\bticket"]),
    "Wave 3 row": ("the Wave 3 rule: a finding out of scope, or needing an unusual construction, is a Wave 3 row, "
                   "never a round",
                   [r"wave 3 row", r"out of scope", r"unusual construction", r"never a round"]),
    "Verdict": ("the structured verdict per KPI", [r"structured verdict", r"per KPI"]),
    "Rounds": ("at most two review rounds per ticket", [r"at most (two|2)\b", r"review rounds?", r"per ticket"]),
}


def s6_heads(text: str) -> dict[str, list[str]]:
    """``{head: faults}`` for the four heads of the QA engineer's file."""
    found = fields(text)
    out = {}
    for head, (wanted, patterns) in S6_HEADS.items():
        fault = head_once_at_column_zero(text, f"- **{head}:**")
        if fault:
            out[head] = [f"qa-engineer.md: the file {fault} (it must state {wanted})"]
            continue
        value = found.get(head.lower(), "")
        out[head] = [f"qa-engineer.md: its `- **{head}:**` line does not match {pattern!r} (it must state {wanted})"
                     for pattern in patterns if not re.search(pattern, value, re.IGNORECASE)]
    return out


# ---------------------------------------------------------------------------------------------------------------
# S9, F1: the install rule in the two orchestrator copies
# ---------------------------------------------------------------------------------------------------------------

# "The guard asks on every install command" and its close variants: the guard asks/prompts ... every/each/all (up to
# two words) install; and "every install ... is asked". The CTO-only wording ("asks only the orchestrator ... for an
# install; every other session is refused") does not match: "every other session is" is not "every ... install".
OLD_RULE = [
    re.compile(r"\bguard\b[^.;]{0,60}\b(asks?|prompts?)\b[^.;]{0,40}\b(every|each|all)\s+(?:\w+\s+){0,2}install", re.IGNORECASE),
    re.compile(r"\b(every|each|all)\s+(?:\w+\s+){0,2}install\w*\b[^.;]{0,40}\b(is|are|gets?)\s+(asked|prompted)", re.IGNORECASE),
]
OLD_VARIANTS = (
    "The guard asks on every install command, and the owner approves in chat.",
    "the guard asks for each install",
    "The guard prompts on every package install.",
    "Every install command is asked by the guard.",
    "the guard\nasks on every\ninstall command",
)
NEW_RULE_SAMPLES = (
    "The guard asks only the orchestrator on the project's coordination ticket for an install; every other session "
    "is refused.",
)


def old_rule_lines(text: str) -> list[str]:
    """The statements of ``text`` (and of its wrapped lines folded) that say the guard asks on every install."""
    return [part for part in statements(text) if any(p.search(part) for p in OLD_RULE)]


RULE_A = [r"install", r"\bonly\b", r"coordination[\s_]ticket", r"\b(orchestrator|CTO)\b", r"\bask(s|ed)?\b"]
RULE_B = [r"install", r"\brefus(e|ed|es|al)\b", r"\b(every|any|all) other\b"]
RULE_KEY = [r"install", r"coordination_ticket", r"GOV_TICKET"]


def install_rule_faults(rel: str, text: str) -> list[str]:
    out = []
    if not window_matches(text, RULE_A, 3):
        out.append(f"{rel}: does not state that only the orchestrator on the project's coordination ticket is asked "
                   f"for an install (no statement with {RULE_A})")
    if not window_matches(text, RULE_B, 3):
        out.append(f"{rel}: does not state that every other session is refused an install (no statement with {RULE_B})")
    if not window_matches(text, RULE_KEY, 3):
        out.append(f"{rel}: does not name the key `coordination_ticket` and `GOV_TICKET` with the install rule "
                   f"(no run of three statements with {RULE_KEY})")
    return out


# ---------------------------------------------------------------------------------------------------------------
# The matchers' own samples: each content test first checks that its matcher accepts a statement of the KPI in the
# form the KPI gives it (a fault here is a fault of the test, not of the work).
# ---------------------------------------------------------------------------------------------------------------

_SAMPLE_QA = """- **Access:** it reads the spec, the KPIs, the tests and the code, and changes none of them. It writes only its findings report.
- **Per stream:** tickets that touch the core (the guard, the close, memory's retrieval, anything that could fail
  open) are checked one by one before they merge; the others in batches of up to about five.
- **Moderator:** it triages every finding against the ticket's own scope and KPIs.
- **Wave 3 row:** a finding out of scope, or needing an unusual construction, is a Wave 3 row, never a round.
- **Verdict:** the structured verdict per KPI.
- **Rounds:** at most two review rounds per ticket.
"""
_SAMPLE_LEAD = """- **Reads:** everything except the five rules' refusals; never its workers' transcripts beyond returns.
- **Writes:** `.gov-runtime/scratch/lead/**` in its worktree, the probe record, checkpoint records.
- **Handover:** one return to its Senior Engineer, the twelve fields first.
"""
_SAMPLE_SE = """- **Reads:** everything except the five rules' refusals; its leads' returns.
- **Writes:** its stream folder under .gov-runtime/scratch/streams, each lead's brief.
- **Brief contents:** its stream, its coordination ticket, its tickets with their state, the playbook and checkpoint.
- **Handover:** typed handoffs up to the CTO and the lead brief down to each lead.
- **Skills:** checkpoint, retrieval
- **Launch default:** model claude-opus-5-5, effort high
"""
_SAMPLE_RULE = ("- `PACKAGE_INSTALL`: the guard asks only the orchestrator on the project's coordination ticket for an "
                "install (the key `coordination_ticket` of the roster; its session's `GOV_TICKET` is that ticket); "
                "every other session is refused.")

SAMPLES = {
    "s1": lambda: s1_ticket_lead(_SAMPLE_LEAD),
    "s8": lambda: s8_senior_engineer(_SAMPLE_SE),
    "s3-access": lambda: s3_qa_access(_SAMPLE_QA),
    "s3-stream": lambda: s3_per_stream(_SAMPLE_QA),
    "s6": lambda: [f for faults in s6_heads(_SAMPLE_QA).values() for f in faults],
    "s9": lambda: install_rule_faults("sample", _SAMPLE_RULE) + old_rule_lines(_SAMPLE_RULE),
}


def matcher_selfcheck(kind: str) -> None:
    faults = SAMPLES[kind]()
    assert not faults, f"the checker's own sample for {kind} fails its matcher (a fault of the test, not of the work): {faults}"

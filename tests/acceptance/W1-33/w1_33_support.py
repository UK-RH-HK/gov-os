"""Support code for the W1-33 acceptance tests (standard library and PyYAML only).

W1-33 delivers the role definitions of the five Wave 1 roles: a kernel role file
per role, a roster entry per role, and the definition under ``.claude/agents/``
that replaces the minimal one of W1-05. The ticket holds no code, so the tests
read committed files, and ask the guard and the launcher (through W1-46's
support code) whether they decide what the definitions state.

**The form of a role file** is the one ``template/governance/kernel/roles/research.md``
already uses (W1-46): a Markdown list whose items start with a bold label,

    - **Purpose:** ...
    - **Allowed paths:** ...

A field is one such item: its label, and its text up to the next labelled item,
a heading, or a blank line followed by text that is not indented. Sub-items
(indented lines) belong to the field. Labels are matched without regard to case,
with the patterns W1-46's tests already use for the six parts.

**The permission classes** (KPI success 3, CAP-58.b) are read from the field
labelled "Permission classes". Each class name is followed by its disposition:
the first of the words ``denied`` (or ``deny``), ``allowed`` (or ``granted``)
and ``ask`` after the name. Class names written together (``PACKAGE_INSTALL /
SYSTEM_INSTALL: denied``) share the text that follows the last of them.

Nothing here imports ``src/gov`` and nothing names a held-out path.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import yaml

_TESTS = Path(__file__).resolve().parent.parent
for _name in ("W1-46",):
    _directory = str(_TESTS / _name)
    if _directory not in sys.path:
        sys.path.insert(0, _directory)

import w1_46_support as launch_support   # noqa: E402  the temporary project, the guard, ``gov launch``

w47 = launch_support.w47
live_support = launch_support.live_support   # W1-05: frontmatter, agent definitions

REPO_ROOT = Path(__file__).resolve().parents[3]
ROLES_DIR_REL = "template/governance/kernel/roles"
AGENTS_DIR_REL = ".claude/agents"
ROSTER_REL = "governance/project/roster.yaml"
TICKETS_REL = ".tickets"
ACCEPTANCE_PATTERN = "tests/acceptance/**"

ORCHESTRATOR = "orchestrator"
PRODUCT_SPEC = "product-spec"
TEST_DESIGNER = "independent-test-designer"
ENGINEER = "engineer"
AUDITOR = "independent-auditor"
RESEARCH = "research"
ROLES = (ORCHESTRATOR, PRODUCT_SPEC, TEST_DESIGNER, ENGINEER, AUDITOR)   # the five of KPI success 1
NOT_TEST_DESIGNER = tuple(role for role in ROLES if role != TEST_DESIGNER)
IMPLEMENTERS = (ENGINEER, PRODUCT_SPEC)                # KPI failure 2
NOT_ORCHESTRATOR = tuple(role for role in ROLES if role != ORCHESTRATOR)
EMPTY_PROFILE_ROLES = (ENGINEER, TEST_DESIGNER, AUDITOR)   # DEC-158: launched workers with an empty allowlist
NOT_LAUNCHED = (ORCHESTRATOR,)   # the launcher refuses it (W1-46). Owner decision, DEC-386: product-spec is launched

# The research role's files, as W1-46 and the owner (DEC-312) committed them. KPI success 5: W1-33 leaves them.
RESEARCH_ROLE_FILE_SHA256 = "60f9092f37430a096eeb932907b5814661585afaf38c52a045c3d775c933e678"
RESEARCH_AGENT_SHA256 = "259f33483263f98c1d654bf3fc6a0ded09bc4832eea61c567db66a756c7f2acb"
RESEARCH_ROSTER_ENTRY = {
    "role_file": "template/governance/kernel/roles/research.md",
    "agent": ".claude/agents/research.md",
    "session": "gov launch research <ticket>",
    "network_profile": "research-allowlist",
}
RESEARCH_ROSTER_LINES = (
    "  research:",
    "    role_file: template/governance/kernel/roles/research.md",
    "    agent: .claude/agents/research.md",
    "    session: gov launch research <ticket>",
    "    network_profile: research-allowlist",
)

# The six required fields (KPI success 1, DEC-066, MR-5), with the label patterns of W1-46's tests.
REQUIRED_FIELDS = {
    "purpose": r"purpose",
    "allowed-path pattern": r"allowed[\s_-]*paths?(\s+patterns?)?",
    "tools": r"tools",
    "model tier": r"model[\s_-]*tier",
    "authority level": r"authority(\s+level)?",
    "handoff format": r"hand[\s_-]?off(\s+format)?",
}
# Two more fields the KPIs need: the launcher's network profile and the permission classes (KPI success 3).
OTHER_FIELDS = {
    "network": r"network(\s+profile)?",
    "permission classes": r"permission[\s_-]*class(es)?",
}
FIELD_PATTERNS = {**REQUIRED_FIELDS, **OTHER_FIELDS}

# CAP-58.b names these classes. A family (``NETWORK_*``) is any name with that prefix, or the starred name itself.
SINGLE_CLASSES = ("WRITE_REPO_SCOPED", "PACKAGE_INSTALL", "SYSTEM_INSTALL", "SECRET_READ", "READ_REPO", "RUN_TESTS",
                  "CI_TRIGGER")
CLASS_FAMILIES = ("NETWORK_", "DB_", "CLOUD_", "DEPLOY_")
EVERY_CLASS = SINGLE_CLASSES + CLASS_FAMILIES
_CLASS = re.compile(r"(?<![A-Z_])(?:" + "|".join(SINGLE_CLASSES) + "|(?:"
                    + "|".join(CLASS_FAMILIES) + r")[A-Z_]*\*?)(?![A-Z_])")
_DISPOSITION = re.compile(r"\b(denied|deny|allowed|granted|ask)\b", re.IGNORECASE)
_EXCLUSION = re.compile(r"\b(except|excluding|excluded|never|not|no|nor|outside|denied|refuse[sd]?|without)\b",
                        re.IGNORECASE)
_JOINED = re.compile(r"(?:[\s`,/*-]|\band\b|\bor\b)*", re.IGNORECASE)   # what stands between names written together
_LABELLED = re.compile(r"^[-*]\s+\*\*(?P<label>[^*]+?):?\*\*:?\s*(?P<rest>.*)$")


# --------------------------------------------------------------------------
# Files
# --------------------------------------------------------------------------

def role_file_rel(role):
    return f"{ROLES_DIR_REL}/{role}.md"


def agent_rel(role):
    return f"{AGENTS_DIR_REL}/{role}.md"


def read_committed(rel, root=REPO_ROOT):
    """The text of a file this ticket delivers; a test fails here until the file exists."""
    path = Path(root) / rel
    assert path.is_file(), f"{rel} does not exist"
    return path.read_text(encoding="utf-8")


def sha256(rel, root=REPO_ROOT):
    path = Path(root) / rel
    assert path.is_file(), f"{rel} does not exist"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def body(text):
    """A Markdown file's text without its YAML frontmatter."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            rest = text[end + 4:]
            return rest.split("\n", 1)[1] if "\n" in rest else ""
    return text


def load_roster(root=REPO_ROOT):
    """The ``roles`` mapping of the roster: ``{role name: entry}``."""
    data = yaml.safe_load(read_committed(ROSTER_REL, root))
    roles = data.get("roles") if isinstance(data, dict) else None
    assert isinstance(roles, dict), f"{ROSTER_REL} has no mapping under `roles`"
    return roles


def ticket_roles(root=REPO_ROOT):
    """The ``role:`` value of every ticket, ``{role: [ticket file names]}``. Tickets are read, never written."""
    found = {}
    for path in sorted((Path(root) / TICKETS_REL).glob("*.md")):
        pairs = live_support.frontmatter(path.read_text(encoding="utf-8")) or {}
        if pairs.get("role"):
            found.setdefault(pairs["role"], []).append(path.name)
    return found


# --------------------------------------------------------------------------
# Fields
# --------------------------------------------------------------------------

def normalise(text):
    return " ".join(text.split())


def _spans(text):
    """``[(label, first line, line after the last, text)]`` for every labelled list item of ``text``."""
    lines = body(text).splitlines()
    spans, start, label = [], None, None

    def close(end):
        if start is not None:
            first = _LABELLED.match(lines[start]).group("rest")
            spans.append((label, start, end, normalise("\n".join([first, *lines[start + 1:end]]))))

    for index, line in enumerate(lines):
        match = _LABELLED.match(line)
        ends = False
        if match or line.startswith("#"):
            ends = True
        elif start is not None and line.strip() and not line[0].isspace():
            # Text that is not indented, after a blank line, is no longer the field.
            ends = index > 0 and not lines[index - 1].strip()
        if ends:
            end = index
            while end > 0 and start is not None and end - 1 > start and not lines[end - 1].strip():
                end -= 1
            close(end)
            start, label = (index, match.group("label").strip()) if match else (None, None)
    end = len(lines)
    while start is not None and end - 1 > start and not lines[end - 1].strip():
        end -= 1
    close(end)
    return lines, spans


def fields(text):
    """``{label in lower case: text}`` for every labelled list item of a role file or a definition."""
    return {label.lower(): value for label, _, _, value in _spans(text)[1]}


def field(text, name):
    """The text of the field ``name`` (a key of ``FIELD_PATTERNS``), or None when the file has no such label."""
    pattern = re.compile(FIELD_PATTERNS[name], re.IGNORECASE)
    for label, value in fields(text).items():
        if pattern.fullmatch(label):
            return value
    return None


def missing_fields(text):
    """The required fields a role file or a definition lacks, or states with no text (KPI failure 1)."""
    return [name for name in REQUIRED_FIELDS if not (field(text, name) or "").strip()]


def _rewrite(text, name, replacement):
    pattern = re.compile(FIELD_PATTERNS[name], re.IGNORECASE)
    lines, spans = _spans(text)
    head = text[:len(text) - len(body(text))]
    for label, start, end, _ in spans:
        if pattern.fullmatch(label):
            return head + "\n".join(lines[:start] + replacement(label) + lines[end:]) + "\n"
    raise AssertionError(f"the text has no field {name!r} to change")


def without_field(text, name):
    """``text`` with the field ``name`` taken out: what KPI failure 1 describes."""
    return _rewrite(text, name, lambda label: [])


def with_field(text, name, value):
    """``text`` with the text of the field ``name`` replaced by ``value``."""
    return _rewrite(text, name, lambda label: [f"- **{label}:** {value}"])


# --------------------------------------------------------------------------
# What a role's fields must say
# --------------------------------------------------------------------------

def _sentences(text):
    return [part for part in re.split(r"(?<=[.;])\s+", normalise(text)) if part]


def acceptance_faults(role, text):
    """Why the allowed-path pattern of ``role`` is wrong about ``tests/acceptance/**`` (KPI success 2, failure 2).

    The test designer's pattern includes it. Any other role's pattern names it
    only in a sentence that excludes it (except, never, not, denied, ...).
    """
    pattern = field(text, "allowed-path pattern")
    if not pattern:
        return ["there is no allowed-path pattern"]
    naming = [sentence for sentence in _sentences(pattern) if "tests/acceptance" in sentence]
    if role == TEST_DESIGNER:
        if ACCEPTANCE_PATTERN not in pattern:
            return [f"the test designer's pattern does not include {ACCEPTANCE_PATTERN}"]
        return []
    return [f"the pattern of {role} covers the acceptance tests: {sentence!r}"
            for sentence in naming if not _EXCLUSION.search(sentence)]


def orchestrator_scope_faults(text):
    """Why the orchestrator's pattern does not state "anywhere in the repository except tests/acceptance/**"."""
    pattern = field(text, "allowed-path pattern") or ""
    faults = []
    if not re.search(r"anywhere|whole|entire|any(\s+\w+)?\s+path|every(\s+\w+)?\s+path", pattern, re.IGNORECASE):
        faults.append("it does not say the scope is anywhere in the repository")
    if not any(ACCEPTANCE_PATTERN in sentence and _EXCLUSION.search(sentence) for sentence in _sentences(pattern)):
        faults.append(f"it does not except {ACCEPTANCE_PATTERN}")
    return faults


def auditor_scope_faults(text):
    """Why the auditor's pattern is not "read-only, except the report path its own ticket allows" (DEC-112)."""
    pattern = field(text, "allowed-path pattern") or ""
    faults = []
    if not re.search(r"read[\s-]?only", pattern, re.IGNORECASE):
        faults.append("it does not say the auditor is read-only")
    if not (re.search(r"report", pattern, re.IGNORECASE) and re.search(r"ticket", pattern, re.IGNORECASE)):
        faults.append("it does not name the one exception, the report path its own ticket allows (DEC-112)")
    return faults


def class_texts(text):
    """``{class name as written: the text that states its disposition}`` from the permission-classes field."""
    value = field(text, "permission classes") or ""
    matches = list(_CLASS.finditer(value))
    found, following = {}, ""
    for index in range(len(matches) - 1, -1, -1):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(value)
        own = value[matches[index].end():end]
        if _JOINED.fullmatch(own) is None or index + 1 == len(matches):
            following = own   # a text of its own; names written together share the last one's
        found.setdefault(matches[index].group(0), following)
    return found


def disposition(statement):
    """``denied``, ``allowed`` or ``ask``: the first such word of a class's text, or None."""
    match = _DISPOSITION.search(statement)
    if not match:
        return None
    word = match.group(1).lower()
    return {"deny": "denied", "granted": "allowed"}.get(word, word)


def statements(text, name):
    """The texts of the class ``name``, or of every class of the family ``name`` (``NETWORK_``)."""
    return {written: statement for written, statement in class_texts(text).items()
            if (written.startswith(name) if name.endswith("_") else written == name)}


def class_faults(role, text):
    """Why ``role`` does not map the permission classes as KPI success 3 and CAP-58.b say."""
    if field(text, "permission classes") is None:
        return ["there is no permission-classes field"]
    faults = []

    def check(name, wanted, *needs):
        found = statements(text, name)
        if not found:
            faults.append(f"{name}{'*' if name.endswith('_') else ''} is not mapped")
        for written, statement in found.items():
            if wanted is not None and disposition(statement) not in wanted:
                faults.append(f"{written} is {disposition(statement)!r}, not {' or '.join(wanted)}")
            elif disposition(statement) is None and not needs:
                faults.append(f"{written} has no disposition (denied, allowed, granted or ask)")
            for need in needs:
                if not re.search(need, statement, re.IGNORECASE):
                    faults.append(f"{written} does not name {need}")

    check("WRITE_REPO_SCOPED", None, r"allowed_paths")
    if role == ORCHESTRATOR:
        check("PACKAGE_INSTALL", ("ask",), r"owner", r"DEC-083")
        check("SYSTEM_INSTALL", None, r"DEC-083")
    else:
        check("PACKAGE_INSTALL", ("denied",))
        check("SYSTEM_INSTALL", ("denied",))
    check("SECRET_READ", ("denied",))
    check("READ_REPO", ("allowed",))
    check("RUN_TESTS", ("allowed",))
    closed = role in EMPTY_PROFILE_ROLES   # no network at all, so nothing beyond the machine is granted
    for name in ("NETWORK_", "DB_", "CLOUD_", "CI_TRIGGER", "DEPLOY_"):
        check(name, ("denied",) if closed else ("denied", "allowed", "ask"))
    return faults


def network_faults(role, text):
    """Why a launched worker's definition does not name the launcher's network profile (KPI success 3)."""
    network = field(text, "network")
    if not network:
        return ["there is no network field"]
    faults = []
    if not re.search(r"launcher", network, re.IGNORECASE):
        faults.append("it does not say the grant comes from the launcher's profile")
    wanted = r"empty" if role in EMPTY_PROFILE_ROLES else r"allowlist"
    if not re.search(wanted, network, re.IGNORECASE):
        faults.append(f"it does not name the profile ({wanted})")
    return faults


def role_faults(role, text):
    """Every fault of one role's text against KPI success 1 to 3, as ``[fault]``."""
    faults = [f"the field {name!r} is missing or empty" for name in missing_fields(text)]
    faults += acceptance_faults(role, text)
    faults += class_faults(role, text)
    if role == ORCHESTRATOR:
        faults += orchestrator_scope_faults(text)
    if role == AUDITOR:
        faults += auditor_scope_faults(text)
    if role in EMPTY_PROFILE_ROLES:
        faults += network_faults(role, text)
    return faults

"""Support for W2-11's acceptance tests: paths, a Markdown reader and the superseded-rule detector.

Every case reads the repository this file sits in (``REPO_ROOT``), so merged into the ticket's worktree they
judge that worktree's files and, for the validator case, its ``src/``. Standard library and PyYAML only.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]

KERNEL = "template/governance/kernel"
TEMPLATES = f"{KERNEL}/templates"
SKILLS = f"{KERNEL}/skills"
SKILL_REL = f"{SKILLS}/orchestration/SKILL.md"
COPY_ROOTS = (".claude/skills", ".rulesync/skills", "template/.rulesync/skills")
ROLE_RELS = (f"{KERNEL}/roles/orchestrator.md", ".rulesync/subagents/orchestrator.md",
             "template/.rulesync/subagents/orchestrator.md", ".claude/agents/orchestrator.md")
SKILL_TEMPLATE_REL = f"{TEMPLATES}/skill.md"

TWELVE = ("task", "status", "work_completed", "files_changed", "evidence", "tests", "discoveries", "risks",
          "lessons", "proposed_decisions", "unresolved", "recommended_next_action")

# rulesync 24 writes only these keys into a Claude Code skill copy (the brief's fact of the existing tool).
CLAUDE_SKILL_KEYS = {"name", "description", "when_to_use", "allowed-tools", "disallowed-tools", "model", "effort",
                     "argument-hint", "context", "agent", "shell", "background", "arguments", "hooks",
                     "disable-model-invocation", "user-invocable", "paths", "license", "compatibility", "metadata"}

REPOSITORY_SCOPED = re.compile(r"\bW[1-9]-\d+|\bDAEO-|/home/|gov-os-worktrees|Dynamic-Agentic|gov-os-workbench|"
                               r"w2/integrate")


def read(rel, root=REPO_ROOT):
    file = Path(root) / rel
    assert file.is_file(), f"{rel} does not exist"
    return file.read_text(encoding="utf-8")


def split_frontmatter(text):
    """``(mapping or None, body)``."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end < 0:
        return None, text
    try:
        front = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        front = None
    return (front if isinstance(front, dict) else None), text[end + 4:].partition("\n")[2]


def plain(text):
    """Whitespace collapsed, emphasis and code marks dropped: what a reader reads."""
    return " ".join(text.replace("*", "").replace("`", "").split())


def statements(text, keep_marks=False):
    """Paragraphs, list items (with their continuation lines) and table rows, each collapsed (with ``keep_marks``,
    code marks and emphasis are kept, so code spans can still be told apart)."""
    collapse = (lambda t: " ".join(t.split())) if keep_marks else plain
    found, current = [], []
    for line in split_frontmatter(text)[1].splitlines():
        stripped = line.strip()
        starts_item = bool(re.match(r"^([-*+]|\d+[.)])\s+", stripped)) and not line.startswith("    ")
        if not stripped or stripped.startswith("#") or starts_item or stripped.startswith("|"):
            if current:
                found.append(collapse("\n".join(current)))
            current = []
            if stripped.startswith("|"):
                found.append(collapse(stripped))
                continue
            if not stripped or stripped.startswith("#"):
                continue
        current.append(line)
    if current:
        found.append(collapse("\n".join(current)))
    return found


def carries(statement, ideas):
    return all(re.search(idea, statement, re.IGNORECASE) for idea in ideas)


def stated(text, ideas):
    return [s for s in statements(text) if carries(s, ideas)]


def cites(text, decision):
    return re.search(rf"\b{decision}\b", text) is not None


def folder_texts(rel, root=REPO_ROOT):
    """``{relative path: text}`` of every Markdown file under a folder."""
    folder = Path(root) / rel
    return {str(p.relative_to(root)): p.read_text(encoding="utf-8")
            for p in sorted(folder.rglob("*.md"))} if folder.is_dir() else {}


def kernel_skill_names(root=REPO_ROOT):
    """The kernel's own skills: every folder of the kernel's skills with a SKILL.md, the vendored ones aside."""
    return sorted(p.parent.name for p in (Path(root) / SKILLS).glob("*/SKILL.md"))


# --------------------------------------------------------------------------------------------------------------
# DEC-866: the superseded rules a template, skill or role file must no longer teach
# --------------------------------------------------------------------------------------------------------------

SUPERSEDED_TEXT = {
    "LEAD_CHECKPOINT (DEC-838)": re.compile(r"\bLEAD_CHECKPOINT\b"),
    "a checkpoint at about <context limit> tokens (DEC-838, DEC-837)":
        re.compile(r"\bat about\b[^.\n]{0,60}\btokens\b", re.IGNORECASE),
    "a fixed ceiling of tickets in flight (DEC-847)":
        re.compile(r"\b(at most|up to|no more than|a maximum of)\s+(<[^>]+>|\d+|one|two|three|four|five|six|ten)\s+"
                   r"(tickets?|leads?|ticket leads?)\b|\bstated ceiling\b|\bceiling of \d+\b", re.IGNORECASE),
    "the owner's own batch or commits for decisions (DEC-861)":
        re.compile(r"\bowner'?s? (daily )?batch\b|\bin the next batch\b|\bthe owner commits\b", re.IGNORECASE),
}
SUPERSEDED_STATEMENTS = {
    "a listing or search refusal over the governance folder or .claude/ (DEC-820)":
        [r"\b(run no|no) (globs?|searche?s?|listings?)\b|\bnever (glob|search|list)\b|\bone by one\b",
         r"governance|\.claude/"],
    "the held-out list's names refused (DEC-820)":
        [r"held-out (file|path|list)\b|never type its path", r"\b(never|refuses?|no)\b"],
}


def superseded_teachings(text):
    """What a text still teaches of a superseded rule: a list of ``kind: snippet``."""
    found = [f"{kind}: {m.group(0)}" for kind, pattern in SUPERSEDED_TEXT.items()
             for m in [pattern.search(plain(text))] if m]
    for kind, ideas in SUPERSEDED_STATEMENTS.items():
        found += [f"{kind}: {s[:100]}" for s in stated(text, ideas)]
    return found


def supersession_files(root=REPO_ROOT):
    """The files DEC-866's sweep names for W2-11, as they exist under ``root``."""
    rels = [*ROLE_RELS]
    for base in (SKILLS, *COPY_ROOTS):
        rels += folder_texts(f"{base}/orchestration", root)
    return [rel for rel in dict.fromkeys(rels) if (Path(root) / rel).is_file()]


# --------------------------------------------------------------------------------------------------------------
# Round 2 (DEC-995, DEC-996): a skill grants nothing; its steps write only inside the class its front matter names
# --------------------------------------------------------------------------------------------------------------

# The ticket's six permission fields, with the spellings and the sandbox key W2-120's line names beside them.
PERMISSION_KEYS = ("allowed-tools", "allowed_tools", "disallowed-tools", "permissions", "paths", "network", "sandbox",
                   "model", "effort")
# The skill template's closed front matter (success-9), metadata holding only the carried repeat of the version.
TEMPLATE_KEYS = ("name", "version", "description", "output")


def permission_fields(front):
    """The permission fields of a front matter, at the top level or under ``metadata``."""
    if not isinstance(front, dict):
        return []
    found = [key for key in front if key in PERMISSION_KEYS]
    meta = front.get("metadata")
    if isinstance(meta, dict):
        found += [f"metadata.{key}" for key in meta if key in PERMISSION_KEYS]
    return found


def skill_files(root=REPO_ROOT):
    """Every kernel skill's SKILL.md, its copies and the skill template, as they exist under ``root``."""
    rels = []
    for name in kernel_skill_names(root):
        rels += [f"{base}/{name}/SKILL.md" for base in (SKILLS, *COPY_ROOTS)]
    rels.append(SKILL_TEMPLATE_REL)
    return [rel for rel in rels if (Path(root) / rel).is_file()]


def output_classes(output):
    """The path classes an ``output`` value names (a string or a list): every token holding ``/`` or ``*``."""
    values = output if isinstance(output, list) else [output]
    return [token for value in values if value is not None
            for token in re.findall(r"[^\s,;()`'\"]+", str(value)) if "/" in token or "*" in token]


def declares_none(output):
    return output in (None, [], "") or (isinstance(output, str) and output.strip().lower() == "none")


def _class_pattern(path_class):
    parts = re.split(r"(<[^>]+>|\*\*|\*)", path_class.lstrip("./"))
    body = "".join(r"[^/]+" if p.startswith("<") else ".*" if p == "**" else r"[^/]*" if p == "*" else re.escape(p)
                   for p in parts if p)
    return re.compile(body + (".*" if path_class.endswith(("/", "**")) else "(/.*)?") + "$")


WRITE_VERB = re.compile(r"\b(write|writes|writing|commit|commits|create|creates|edit|edits|save|saves|append|"
                        r"appends)\b", re.IGNORECASE)
NEGATED = re.compile(r"\b(never|not|no|nor|without|nothing)\b[^`]{0,40}$", re.IGNORECASE)


def write_targets(text):
    """The paths a text tells its reader to write: a code span holding a ``/`` after a write verb, in the same
    clause, unless the words just before the verb negate it (a Never line)."""
    found = []
    for statement in statements(text, keep_marks=True):
        for clause in re.split(r"[.;:](?=\s|$)", statement):
            for verb in WRITE_VERB.finditer(clause):
                if NEGATED.search(clause[:verb.start()]):
                    continue
                found += [span.strip().lstrip("./") for span in re.findall(r"`([^`]+)`", clause[verb.end():])
                          if "/" in span and " " not in span.strip() and not span.startswith("-")]
    return list(dict.fromkeys(found))


def stray_writes(text, output):
    """The write targets of a text that its ``output`` class does not hold (every one, when it declares none)."""
    patterns = [] if declares_none(output) else [_class_pattern(c) for c in output_classes(output)]
    return [target for target in write_targets(text) if not any(p.match(target) for p in patterns)]


def section(text, heading):
    """The body of the first section (level 2 or 3) whose heading matches ``heading``, or ``None``."""
    body = split_frontmatter(text)[1]
    match = re.search(rf"^(#{{2,3}})\s+{heading}.*?$(.*?)(?=^#{{1,3}}\s|\Z)", body, re.M | re.I | re.S)
    return match.group(2) if match else None


def folder_stated(folder, ideas, root=REPO_ROOT):
    """``[(relative path, statement)]`` of every statement in a folder's Markdown files that carries every idea."""
    return [(rel, st) for rel, text in folder_texts(folder, root).items() for st in stated(text, ideas)]


def reached(folder, rel, root=REPO_ROOT):
    """A file of a skill's folder is reached when it is the SKILL.md or the SKILL.md names it."""
    name = Path(rel).name
    return name == "SKILL.md" or name in read(f"{folder}/SKILL.md", root)


def scenario_units(text):
    """What a scenario can be written as: a statement that says "scenario", and, inside a section whose heading
    says "scenario", each statement and each sub-section (its heading and body, collapsed)."""
    body = split_frontmatter(text)[1]
    units = [st for st in statements(text) if re.search(r"scenario", st, re.I)]
    heads = [(m.start(), len(m.group(1)), m.group(2)) for m in re.finditer(r"^(#{1,6})\s+(.*)$", body, re.M)]
    for i, (start, level, title) in enumerate(heads):
        if not re.search(r"scenario", title, re.I):
            continue
        block = body[start:next((s for s, lv, _ in heads[i + 1:] if lv <= level), len(body))]
        units += statements(block)
        units += [plain(sub) for sub in re.split(r"^(?=#{1,6}\s)", block, flags=re.M) if sub.strip()]
    return units

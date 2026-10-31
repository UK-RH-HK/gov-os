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
BRIEFS = ("brief-lead.md", "brief-engineer.md", "brief-test-designer.md", "brief-product-spec.md",
          "brief-reviewer.md")
BRIEF_RELS = tuple(f"{TEMPLATES}/{name}" for name in BRIEFS)
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


def statements(text):
    """Paragraphs, list items (with their continuation lines) and table rows, each collapsed."""
    found, current = [], []
    for line in split_frontmatter(text)[1].splitlines():
        stripped = line.strip()
        starts_item = bool(re.match(r"^([-*+]|\d+[.)])\s+", stripped)) and not line.startswith("    ")
        if not stripped or stripped.startswith("#") or starts_item or stripped.startswith("|"):
            if current:
                found.append(plain("\n".join(current)))
            current = []
            if stripped.startswith("|"):
                found.append(plain(stripped))
                continue
            if not stripped or stripped.startswith("#"):
                continue
        current.append(line)
    if current:
        found.append(plain("\n".join(current)))
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
    rels = [*BRIEF_RELS, *ROLE_RELS]
    for base in (SKILLS, *COPY_ROOTS):
        rels += folder_texts(f"{base}/orchestration", root)
    return [rel for rel in dict.fromkeys(rels) if (Path(root) / rel).is_file()]

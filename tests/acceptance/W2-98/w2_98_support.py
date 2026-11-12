"""Support for W2-98's acceptance tests: paths, the planted-spec builder, the check runner and the section reader.

Every case finds the repository from this file's own location (``REPO_ROOT``), so merged into the ticket's worktree
the cases judge that worktree's files. ``W2_98_SKILL_DIR`` (an absolute folder) replaces the skill folder; it exists
only so a test designer can show a case bites against a stand-in, and is unset in every real run. Standard library
and PyYAML only; no network, no model call, no copy of the repository (planted files live in ``tmp_path``).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
KERNEL_SKILLS = "template/governance/kernel/skills"
SKILL_REL = f"{KERNEL_SKILLS}/spec-writing"
SKILL_DIR = Path(os.environ.get("W2_98_SKILL_DIR") or REPO_ROOT / SKILL_REL)
CHECK = SKILL_DIR / "check_spec.py"
COPY_ROOTS = (".rulesync/skills", "template/.rulesync/skills", ".claude/skills")
SKILL_NAME = "spec-writing"

# I2: the nine parts, in the spec's form
HEADINGS = ("Problem", "Users and scenarios", "Goals", "Non-goals", "KPIs", "Test data", "Out of scope",
            "Open questions", "Accepted by")
COLUMNS = ("source", "kind", "owner", "licence or recipe", "privacy", "secrets", "hidden half", "secured")

TWELVE = ("task", "status", "work_completed", "files_changed", "evidence", "tests", "discoveries", "risks",
          "lessons", "proposed_decisions", "unresolved", "recommended_next_action")


# --------------------------------------------------------------------------------------------------------------
# Running the skill's script
# --------------------------------------------------------------------------------------------------------------

def need(path: Path) -> Path:
    """The file, or a failure naming it: the red reason on a base that has no skill folder."""
    if not path.is_file():
        pytest.fail(f"{path} does not exist (the skill folder or the file is not there yet)")
    return path


def run_script(*args, cwd=None, timeout=60):
    """``python3 <check_spec.py> <args>``: (exit code, stdout + stderr lines)."""
    done = subprocess.run([sys.executable, str(need(CHECK)), *map(str, args)], capture_output=True, text=True,
                          cwd=str(cwd) if cwd else None, timeout=timeout, stdin=subprocess.DEVNULL)
    return done.returncode, (done.stdout + done.stderr)


def lines_of(output):
    return [line.strip() for line in output.splitlines() if line.strip()]


def refused(output, part=None):
    """The ``REFUSED <part>: <reason>`` lines of an output (those of ``part`` only, when it is given)."""
    found = [line for line in lines_of(output) if line.startswith("REFUSED ")]
    if part is not None:
        found = [line for line in found if line.startswith(f"REFUSED {part}:")]
    return found


def p1_lines(output):
    return [line for line in lines_of(output) if line.startswith("P1 ")]


def passes(output):
    return [line for line in lines_of(output) if re.match(r"PASS\b", line)]


def refused_parts(output):
    return sorted({re.match(r"REFUSED ([^:]+):", line).group(1) for line in refused(output)
                   if re.match(r"REFUSED ([^:]+):", line)})


# --------------------------------------------------------------------------------------------------------------
# The planted spec (I2's nine headings; each KPI "- K<n>: <behaviour>" with a "Fails if:" line; a Test data table)
# --------------------------------------------------------------------------------------------------------------

BODIES = {
    "Problem": "Support staff spend most of a day answering the same sign-up questions, because new members cannot "
               "tell what happens after they register.",
    "Users and scenarios": "- Dana is a new member who registers on a phone and wants to know whether the account is "
                           "ready.\n- Scenario: Dana registers, closes the page and comes back the next day.",
    "Goals": "- A new member knows within one visit that the account is ready.",
    "Non-goals": "- Changing how members pay.",
    "Out of scope": "- Training material for support staff.",
    "Accepted by": "- Sam Okafor, head of support, accepts this spec.",
}

OPEN_QUESTIONS = (
    "- Question: Should the welcome page show the plan the member chose?\n"
    "  - Options: show it (cost: one more page element to maintain); leave it out (cost: members ask support).\n"
    "  - Recommendation: show it.")

CLEAN_KPIS = (
    ("A new member finishes sign-up and sees the welcome page in the same visit.",
     "the welcome page does not appear in the same visit."),
    ("A member who returns the next day is told whether the account is ready.",
     "the member sees a blank page or the sign-up form again."),
    ("A member who mistypes the email address is asked to correct it before the account is created.",
     "an account is created with the mistyped address."),
)

CLEAN_ROWS = (
    {"source": "public repositories with messy history", "kind": "imported", "owner": "Priya Nair, data steward",
     "licence or recipe": "MIT", "privacy": "no personal data; author names are removed",
     "secrets": "none; a scan runs before use", "hidden half": "yes", "secured": "yes"},
    {"source": "forty-eight memory questions", "kind": "synthetic", "owner": "Tomas Berg, evaluation lead",
     "licence or recipe": "written by hand, two questions per topic", "privacy": "none",
     "secrets": "none", "hidden half": "yes", "secured": "yes"},
)


def row(**changes):
    return {**CLEAN_ROWS[0], **changes}


def kpi_block(kpis):
    out = []
    for n, (behaviour, fails) in enumerate(kpis, start=1):
        out.append(f"- K{n}: {behaviour}")
        if fails is not None:
            out.append(f"  Fails if: {fails}")
    return "\n".join(out)


def table(rows):
    head = "| " + " | ".join(COLUMNS) + " |"
    rule = "|" + "|".join("---" for _ in COLUMNS) + "|"
    body = ["| " + " | ".join(str(r.get(c, "")) for c in COLUMNS) + " |" for r in rows]
    return "\n".join([head, rule, *body])


def build_spec(omit=(), kpis=CLEAN_KPIS, rows=CLEAN_ROWS):
    """The planted spec's text: every part but the ones in ``omit``."""
    bodies = {**BODIES, "KPIs": kpi_block(kpis), "Test data": table(rows), "Open questions": OPEN_QUESTIONS}
    parts = [f"# Sign-up confirmation\n"]
    parts += [f"## {h}\n\n{bodies[h]}\n" for h in HEADINGS if h not in omit]
    return "\n".join(parts)


def write_spec(tmp_path, text, name="spec.md"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def check(tmp_path, text=None, name="spec.md", **spec_args):
    """Plants a spec (``text``, or ``build_spec(**spec_args)``) and runs the skill's check on it: (code, output, path)."""
    path = write_spec(tmp_path, build_spec(**spec_args) if text is None else text, name)
    code, output = run_script(path, cwd=tmp_path)
    return code, output, path


# --------------------------------------------------------------------------------------------------------------
# Reading SKILL.md
# --------------------------------------------------------------------------------------------------------------

def split_frontmatter(text):
    """``(mapping or None, body)``; the blank lines before the body's first line are dropped."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end < 0:
        return None, text
    try:
        front = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        front = None
    return (front if isinstance(front, dict) else None), text[end + 4:].partition("\n")[2].lstrip("\n")


def read_skill():
    return need(SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")


SECTION_PATTERNS = (("When / not when", r"when.*not when"), ("Inputs", r"inputs?\b"), ("Steps", r"steps\b"),
                    ("Done when", r"done when"), ("Output and handover", r"output and handover"),
                    ("Escalation", r"escalation"), ("Never", r"never\b"), ("Sources", r"sources\b"))


def headings(body):
    """The level-2 headings of a body (titles, as written), in order."""
    return [h.strip() for h in re.findall(r"^##\s+(.*?)\s*$", body, re.M)]


def section(text, pattern):
    """The text under the first level-2 heading matching ``pattern`` (up to the next level-1 or level-2 heading), or None."""
    body = split_frontmatter(text)[1]
    match = re.search(rf"^##\s+(?:{pattern}).*?$(.*?)(?=^#{{1,2}}\s|\Z)", body, re.M | re.I | re.S)
    return match.group(1) if match else None


def section_problems(text):
    """The template's section structure as problems found (empty when it holds): a section missing (named), the
    sections out of the template's order, Sources not last, or the Steps not a checklist."""
    body = split_frontmatter(text)[1]
    found = [h.lower() for h in headings(body)]
    at = [next((i for i, h in enumerate(found) if re.match(p, h)), None) for _name, p in SECTION_PATTERNS]
    problems = [f"section {name} is missing" for (name, _p), i in zip(SECTION_PATTERNS, at) if i is None]
    present = [i for i in at if i is not None]
    if present != sorted(present):
        problems.append("the sections are out of the template's order")
    if at[-1] is not None and at[-1] != len(found) - 1:
        problems.append("section Sources is not the last section")
    steps = section(text, r"steps")
    if steps is not None and not re.search(r"^\s*[-*] \[[ xX]\]", steps, re.M):
        problems.append("section Steps is not a checklist")
    return problems


def remove_section(text, pattern):
    """``text`` without the first level-2 section whose heading matches ``pattern`` (its heading and body)."""
    return re.sub(rf"^##\s+(?:{pattern})[^\n]*$.*?(?=^#{{1,2}}\s|\Z)", "", text, count=1, flags=re.M | re.S | re.I)


def list_items(block):
    """The list items of a block (a ``-``, ``*``, ``+`` or numbered line and its continuation lines), each collapsed."""
    items, current = [], None
    for line in block.splitlines():
        if re.match(r"^\s{0,3}([-*+]|\d+[.)])\s+", line):
            if current is not None:
                items.append(" ".join(current.split()))
            current = line
        elif current is not None and line.strip() and line.startswith((" ", "\t")):
            current += " " + line.strip()
        elif not line.strip():
            continue
        elif current is not None:
            items.append(" ".join(current.split()))
            current = None
    if current is not None:
        items.append(" ".join(current.split()))
    return items


def skill_files(folder):
    """Every file of a skill folder, as paths relative to it."""
    return sorted(p.relative_to(folder) for p in Path(folder).rglob("*") if p.is_file())

"""Support for W2-100's acceptance tests: the four domain skills (backend, api, data, security) A.

Every case finds the repository from this file's own location (``REPO_ROOT``), so merged into the ticket's worktree the
cases judge that worktree's files and its ``src/``. ``W2_100_CHECK`` (an absolute file) replaces each skill's
``check_domain_skill.py`` in the runs of planted and real SKILL.md files; it exists only so a test designer can show a
planted-bad case bites against a check that refuses nothing, and is unset in every real run.

The skills are never read before they exist here: every planted SKILL.md is built by ``build_skill`` from the
ticket's ``## Interface`` (the template's eight sections, the five labelled parts, the area's named points). Standard
library and PyYAML only. No network, no model call (the stub ``claude`` is written in ``tmp_path``), no copy of the
repository (planted files and projects live in ``tmp_path``; a few named files are copied at most).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
KERNEL_REL = "template/governance/kernel/skills"
KERNEL = REPO_ROOT / KERNEL_REL
SKILLS = ("backend", "api", "data", "security")
COPY_ROOTS = (".rulesync/skills", "template/.rulesync/skills")
CLAUDE_ROOT = ".claude/skills"
STAND_IN = os.environ.get("W2_100_CHECK")
SCRIPT = "check_domain_skill.py"
BASE_FILES = ("SKILL.md", "scenarios.md", SCRIPT)
RECORD_FILE = "scenario-records.yaml"
SUMMARY_FILE = "scenario-summaries.md"
OWN_FILES = {"SKILL.md", "scenarios.md", SCRIPT, RECORD_FILE, SUMMARY_FILE}

SECTIONS = ("When / not when", "Inputs", "Steps", "Done when", "Output and handover", "Escalation", "Never", "Sources")
PARTS = ("Conventions", "Pre-commit checklist", "Unit-test focus", "Common mistakes", "When to escalate")
POINTS = {
    "backend": ("error handling", "idempotence", "migration"),
    "api": ("contract-first", "versioning", "backward compatibility"),
    "data": ("schema change", "migration", "rollback", "data quality"),
    "security": ("input check", "secrets never in code", "least privilege", "Prepare the Organization",
                 "Protect the Software", "Produce Well-Secured Software", "Respond to Vulnerabilities",
                 "any security finding is a P1"),
}
TWELVE = ("task", "status", "work_completed", "files_changed", "evidence", "tests", "discoveries", "risks",
          "lessons", "proposed_decisions", "unresolved", "recommended_next_action")
SCOPE = {"backend": "service code, handlers and jobs", "api": "interfaces other programs call",
         "data": "stored data and the code that changes it", "security": "code that handles untrusted input"}
BODY_LINES_AT_MOST = 165   # "about 150" with a tolerance of 10 per cent, as W2-98's cases read it


# --------------------------------------------------------------------------------------------------------------
# Finding things
# --------------------------------------------------------------------------------------------------------------

def need(path):
    """The file, or a failure naming it: the red reason on a base that has no skill folder."""
    path = Path(path)
    if not path.is_file():
        pytest.fail(f"{path} does not exist (the skill folder or the file is not there yet)")
    return path


def skill_dir(skill):
    return KERNEL / skill


def real_skill(skill):
    return need(skill_dir(skill) / "SKILL.md").read_text(encoding="utf-8")


def check_script(skill):
    """The script a run uses: the stand-in when ``W2_100_CHECK`` names one, else the skill folder's own."""
    return Path(STAND_IN) if STAND_IN else need(skill_dir(skill) / SCRIPT)


def run_check(skill, path, cwd=None):
    """``python3 <skill folder>/check_domain_skill.py <path>``: (exit code, stdout + stderr)."""
    done = subprocess.run([sys.executable, str(check_script(skill)), str(path)], capture_output=True, text=True,
                          cwd=str(cwd) if cwd else None, timeout=60, stdin=subprocess.DEVNULL)
    return done.returncode, done.stdout + done.stderr


def lines_of(output):
    return [line.strip() for line in output.splitlines() if line.strip()]


def refused(output):
    return [line for line in lines_of(output) if line.startswith("REFUSED ")]


def passes(output):
    return [line for line in lines_of(output) if re.match(r"PASS\b", line)]


def skill_files(folder):
    """Every file of a skill folder as paths relative to it (``__pycache__`` left out)."""
    return sorted(p.relative_to(folder) for p in Path(folder).rglob("*")
                  if p.is_file() and "__pycache__" not in p.parts)


# --------------------------------------------------------------------------------------------------------------
# Reading a SKILL.md (the test's own reader: what the ticket's Interface says, not the skill's check)
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


def h2(body):
    """The level-2 headings of a body, as the template compares them: case-folded, a trailing colon ignored."""
    return [h.strip().rstrip(":").strip().lower() for h in re.findall(r"^##\s+(.*?)\s*$", body, re.M)]


def section_problems(text):
    """The template's section structure as problems: a section missing, out of order, or a heading after Sources."""
    found = h2(split_frontmatter(text)[1])
    at = [found.index(name.lower()) if name.lower() in found else None for name in SECTIONS]
    problems = [f"missing {name}" for name, i in zip(SECTIONS, at) if i is None]
    present = [i for i in at if i is not None]
    if present != sorted(present):
        problems.append("the sections are out of the template's order")
    if at[-1] is not None and at[-1] != len(found) - 1:
        problems.append("a level-2 heading stands after Sources")
    return problems


def section(text, name):
    """The text under the level-2 heading ``name`` (up to the next level-1 or level-2 heading), or None."""
    body = split_frontmatter(text)[1]
    match = re.search(rf"^##\s+{re.escape(name)}\s*:?\s*$(.*?)(?=^#{{1,2}}\s|\Z)", body, re.M | re.I | re.S)
    return match.group(1) if match else None


def has_part(body, part):
    """A part stands as a heading of level 2, 3 or 4 whose text is its name, or as a line that starts (after optional
    indentation, a ``-``/``*`` marker and ``*``/``_`` emphasis) with its name followed by a colon."""
    name = re.escape(part)
    heading = rf"^#{{2,4}}\s+[*_]*{name}[*_]*\s*:?\s*$"
    label = rf"^[ \t]*(?:[-*][ \t]+)?[*_]*{name}[*_]*:"
    return bool(re.search(heading, body, re.M | re.I) or re.search(label, body, re.M | re.I))


def _fold(text):
    return re.sub(r"\s+", " ", text.lower().replace("-", " ")).strip()


def has_point(body, point):
    """A point stands anywhere in the body, case-insensitive, whitespace runs one space, a hyphen read as a space
    (``Organisation`` is accepted for ``Organization``)."""
    folded = _fold(body)
    options = {_fold(point)}
    if "organization" in point.lower():
        options.add(_fold(point).replace("organization", "organisation"))
    return any(option in folded for option in options)


PERMISSION_LINE = re.compile(
    r"^[ \t]*(?:[-*][ \t]+)?[*_`'\"]*(?:allowed-tools|allowed_tools|allowedtools|permissions|permission|allow)"
    r"[`'\"*_]*:", re.I)


def permission_lines(text):
    """``(1-based line number, stripped text)`` of each permission-granting line of a file (front matter counted)."""
    return [(n, line.strip()) for n, line in enumerate(text.splitlines(), start=1) if PERMISSION_LINE.match(line)]


def finding_below_p1(text):
    return [(n, line.strip()) for n, line in enumerate(text.splitlines(), start=1)
            if re.search(r"\bfindings?\b", line, re.I) and re.search(r"\bP[23]\b", line)]


def plain_text_files(folder):
    """The text files of a skill folder that carry prose or data (a Python script holds the words as patterns)."""
    return [p for p in sorted(Path(folder).rglob("*"))
            if p.is_file() and p.suffix in {".md", ".yaml", ".yml", ".txt"} and "__pycache__" not in p.parts]


# --------------------------------------------------------------------------------------------------------------
# The planted SKILL.md, built from the Interface
# --------------------------------------------------------------------------------------------------------------

def description(skill):
    return (f"The {skill} method for engineers: its conventions, a pre-commit checklist, unit-test focus, common "
            f"mistakes and when to escalate, for tickets that change {SCOPE[skill]}.")


def front_matter(skill, extra=()):
    lines = ["---", f"name: {skill}", 'version: "1.0.0"', f'description: "{description(skill)}"', "output: none",
             *extra, "metadata:", '  version: "1.0.0"', "---"]
    return "\n".join(lines)


_NEUTRAL = {
    "Conventions": "Keep each change small and easy to read; follow the names and layout the project already uses.",
    "Pre-commit checklist": "Run the project's tests and checks; read the diff once; leave no stray file in it.",
    "Unit-test focus": "One test per behaviour the ticket names, through the public interface, with no network.",
    "Common mistakes": "Changing more than the ticket asks, and testing the code's internals instead of what it does.",
    "When to escalate": "When the ticket cannot be met inside its paths, or two sources disagree.",
}


def _guide(skill, omit_part=None, omit_point=None, part_style="label", point_text=None):
    lines = ["## Area guide", "", "The points of the area:", ""]
    for point in POINTS[skill]:
        if point != omit_point:
            lines.append(f"- Point: {(point_text or {}).get(point, point)}")
    lines.append("")
    for part in PARTS:
        if part == omit_part:
            continue
        if part_style == "heading":
            lines += [f"### {part}", "", f"- {_NEUTRAL[part]}", ""]
        elif part_style == "bold-colon-outside":
            lines += [f"**{part}**: {_NEUTRAL[part]}", ""]
        else:
            lines += [f"- **{part}:** {_NEUTRAL[part]}", ""]
    return "\n".join(lines)


def _sections(skill, guide):
    sec = {
        "When / not when": "- Use it when a ticket changes " + SCOPE[skill] + ".\n- Not when the change is only prose.",
        "Inputs": "- The ticket, its specification and the code it names.",
        "Steps": "Copy this checklist into your notes.\n\n- [ ] 1. Read the ticket and the code it names.\n"
                 "- [ ] 2. Make the change in small steps.\n- [ ] 3. Run the checks, then hand over.",
        "Done when": "- Every KPI line has a test that passes.\n- The checklist above is ticked.",
        "Output and handover": "- The return starts with the twelve fields: " + ", ".join(TWELVE) + ".",
        "Escalation": "- P3 and P2: settle with whoever started the session; note it in the return.\n"
                      "- P1: stop and raise it to whoever started the session.\n"
                      "- Emergency: a secret exposed stops the work at once, then goes up as a P1.",
        "Never": "Reminders only: the guard decides.\n\n- This skill grants nothing and changes no role's reads or writes.",
        "Sources": "DEC-957, DEC-959, CAP-24.b.",
    }
    return sec


def build_skill(skill, omit_section=None, omit_part=None, omit_point=None, part_style="label", order=None,
                after_sources="", front_extra=(), body_extra="", point_text=None, prose=""):
    """The planted SKILL.md of ``skill``: the template's form with the five labelled parts and the area's points.

    ``omit_*`` leaves one item out; ``order`` is a list of section names (default the template's); ``after_sources``
    is text put after the last section; ``front_extra`` are lines added to the front matter; ``body_extra`` is text
    added after the title paragraph; ``point_text`` rewrites how a named point is written; ``prose`` adds a line to
    the Never section."""
    sec = _sections(skill, None)
    if prose:
        sec["Never"] += "\n" + prose
    guide = _guide(skill, omit_part, omit_point, part_style, point_text)
    parts = [front_matter(skill, front_extra), "", f"# {skill.capitalize()}", "",
             "A method for one area of an engineer's work. It states a method only and grants nothing; "
             "the guard decides (CAP-24.b).", ""]
    if body_extra:
        parts += [body_extra, ""]
    for name in (order or SECTIONS):
        if name != omit_section:
            parts += [f"## {name}", "", sec[name], ""]
        if name == "Inputs":     # the area guide stands between Inputs and Steps, whatever section is left out
            parts += [guide]
    text = "\n".join(parts).rstrip("\n") + "\n"
    if after_sources:
        text += "\n" + after_sources.rstrip("\n") + "\n"
    return text


def plant_file(tmp_path, text, folder="planted", name="SKILL.md"):
    path = Path(tmp_path) / folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def insert_line(text, line, where):
    """``text`` with ``line`` added: ``front`` (as the last front-matter line) or ``body`` (after the title)."""
    lines = text.splitlines()
    if where == "front":
        at = lines.index("---", 1)
    else:
        at = next(i for i, l in enumerate(lines) if l.startswith("# ")) + 1
    lines.insert(at, line)
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------------------------------------------
# The skill validator and the adapter check (the shared checks, run as processes)
# --------------------------------------------------------------------------------------------------------------

def _env():
    return {**os.environ, "PYTHONPATH": os.pathsep.join([str(SRC), os.environ.get("PYTHONPATH", "")])}


def validator(path, cwd):
    """``python3 -m gov.check.skill_validator <path>``: (exit code, findings)."""
    done = subprocess.run([sys.executable, "-m", "gov.check.skill_validator", str(path)], capture_output=True,
                          text=True, cwd=str(cwd), env=_env(), timeout=90, stdin=subprocess.DEVNULL)
    try:
        findings = json.loads(done.stdout.strip().splitlines()[-1]).get("findings", [])
    except (ValueError, IndexError, AttributeError):
        findings = [{"code": "UNREADABLE", "message": (done.stdout + done.stderr)[-300:]}]
    return done.returncode, findings


def adapter(cwd):
    """``python3 -m gov.adapters.portability`` in ``cwd``: (exit code, findings)."""
    done = subprocess.run([sys.executable, "-m", "gov.adapters.portability"], capture_output=True, text=True,
                          cwd=str(cwd), env=_env(), timeout=120, stdin=subprocess.DEVNULL)
    return done.returncode, json.loads(done.stdout)["findings"]


# --------------------------------------------------------------------------------------------------------------
# Git: the commit order (F4, S4)
# --------------------------------------------------------------------------------------------------------------

def git(repo, *args, check=True):
    env = {**os.environ, "GIT_AUTHOR_NAME": "W2-100 tests", "GIT_AUTHOR_EMAIL": "w2-100@example.invalid",
           "GIT_COMMITTER_NAME": "W2-100 tests", "GIT_COMMITTER_EMAIL": "w2-100@example.invalid"}
    done = subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)
    if check:
        assert done.returncode == 0, f"git {' '.join(args)} failed in {repo}: {done.stderr}"
    return done


def first_commit(repo, rel):
    """The oldest commit that changed ``rel``, or None."""
    out = git(repo, "log", "--reverse", "--format=%H", "--", rel).stdout.split()
    return out[0] if out else None


def order_problems(repo, skill):
    """Problems naming the skill: its SKILL.md, or one of the three scenarios.md files (the source and its two
    copies), has no commit, or a scenarios.md is committed later than the first commit of the source SKILL.md."""
    text_rel = f"{KERNEL_REL}/{skill}/SKILL.md"
    text = first_commit(repo, text_rel)
    problems = [] if text else [f"{skill}: {text_rel} has no commit"]
    for root in (KERNEL_REL, *COPY_ROOTS):
        rel = f"{root}/{skill}/scenarios.md"
        sc = first_commit(repo, rel)
        if sc is None:
            problems.append(f"{skill}: {rel} has no commit")
        elif text and git(repo, "merge-base", "--is-ancestor", sc, text, check=False).returncode != 0:
            problems.append(f"{skill}: {rel} is committed after {text_rel}")
    return problems


def plant_history(tmp_path, skill, shape):
    """A temporary repository holding the skill's SKILL.md and its three scenarios.md files, committed in ``shape``:
    ``scenarios-first``, ``same-commit``, ``skill-first`` or ``copy-late``."""
    repo = Path(tmp_path) / "history"
    repo.mkdir()
    git(repo, "init", "-q")

    def write(root, name):
        path = repo / root / skill / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{name} of {skill}\n", encoding="utf-8")

    def commit(message, files):
        for root, name in files:
            write(root, name)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    roots = (KERNEL_REL, *COPY_ROOTS)
    scenarios = [(root, "scenarios.md") for root in roots]
    text = [(root, "SKILL.md") for root in roots]
    if shape == "scenarios-first":
        commit("scenarios", scenarios)
        commit("skill", text)
    elif shape == "same-commit":
        commit("both", scenarios + text)
    elif shape == "skill-first":
        commit("skill", text)
        commit("scenarios", scenarios)
    elif shape == "copy-late":
        commit("kernel scenarios", scenarios[:1])
        commit("skill", text)
        commit("copy scenarios", scenarios[1:])
    else:
        raise ValueError(shape)
    return repo


# --------------------------------------------------------------------------------------------------------------
# The records and the summaries (S4)
# --------------------------------------------------------------------------------------------------------------

class _PlainLoader(yaml.SafeLoader):
    """A safe loader that keeps timestamps as the strings written, so ``run_at`` is read as written."""


_PlainLoader.yaml_implicit_resolvers = {
    key: [(tag, rx) for tag, rx in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()}


def load_yaml(path):
    return yaml.load(Path(path).read_text(encoding="utf-8"), Loader=_PlainLoader)


def summary_entries(text):
    """The entries of ``scenario-summaries.md``: dicts with scenario, title, verdict, run_at and summary (the lines)."""
    entries = []
    for block in re.split(r"(?m)^(?=##\s)", text):
        head = re.match(r"##\s+Scenario\s+(\d+):\s*(.*?)\s*$", block.splitlines()[0]) if block.strip() else None
        if not head:
            continue
        verdict = re.search(r"(?m)^\s*-\s*verdict:\s*(\S+)", block)
        run_at = re.search(r"(?m)^\s*-\s*run_at:\s*(.+?)\s*$", block)
        summary = re.search(r"(?ms)^\s*-\s*summary:[ \t]*\n(.*)\Z", block)
        lines = [l.strip() for l in (summary.group(1).splitlines() if summary else []) if l.strip()]
        entries.append({"scenario": int(head.group(1)), "title": head.group(2), "verdict": verdict and verdict.group(1),
                        "run_at": run_at and run_at.group(1), "summary": lines})
    return entries


def record_problems(folder, skill):
    """S4 as the ticket reads it: for scenarios 1, 2 and 3 a last record entry with ``verdict: pass``, and a summary
    entry with that scenario number, ``verdict: pass`` and that entry's ``run_at``, in three lines."""
    folder = Path(folder)
    problems = []
    records_path, summaries_path = folder / RECORD_FILE, folder / SUMMARY_FILE
    if not records_path.is_file():
        return [f"{records_path} does not exist (the lead's real gov skilleval runs write it)"]
    data = load_yaml(records_path)
    records = data.get("records") if isinstance(data, dict) else None
    if not isinstance(records, list):
        return [f"{RECORD_FILE} is not a map with a list under records"]
    summaries = summary_entries(summaries_path.read_text(encoding="utf-8")) if summaries_path.is_file() else None
    if summaries is None:
        problems.append(f"{summaries_path} does not exist (hand-written beside the records)")
    for n in (1, 2, 3):
        ours = [r for r in records if isinstance(r, dict) and r.get("scenario") == n]
        if not ours:
            problems.append(f"scenario {n} has no record entry")
            continue
        last = ours[-1]
        if last.get("skill") != skill:
            problems.append(f"scenario {n}: the last record names skill {last.get('skill')!r}, not {skill!r}")
        if last.get("verdict") != "pass":
            problems.append(f"scenario {n}: the last record's verdict is {last.get('verdict')!r}, not pass")
            continue
        if summaries is None:
            continue
        match = [e for e in summaries if e["scenario"] == n and e["verdict"] == "pass" and e["run_at"] == last.get("run_at")]
        if not match:
            problems.append(f"scenario {n}: no summary entry with verdict pass and run_at {last.get('run_at')!r}")
        elif len(match[0]["summary"]) != 3:
            problems.append(f"scenario {n}: the summary is {len(match[0]['summary'])} lines, not three")
        elif match[0]["title"] != last.get("title"):
            problems.append(f"scenario {n}: the summary's title {match[0]['title']!r} is not the record's {last.get('title')!r}")
    return problems


# --------------------------------------------------------------------------------------------------------------
# scenarios.md (the gov skilleval form) and the stub model
# --------------------------------------------------------------------------------------------------------------

def scenario_blocks(text):
    """``[(number, title, {label: text})]`` of a scenarios.md: each ``## <n>. <title>`` heading and its bullets."""
    out = []
    for block in re.split(r"(?m)^(?=##\s)", text):
        head = re.match(r"##\s+(\d+)\.\s+(.*?)\s*$", block.splitlines()[0]) if block.strip() else None
        if not head:
            continue
        order = re.findall(r"(?m)^- \*\*([^*]+):\*\*", block)
        bullets = {}
        for label in order:
            m = re.search(rf"(?ms)^- \*\*{re.escape(label)}:\*\*(.*?)(?=^- \*\*|\Z)", block)
            bullets[label] = " ".join(m.group(1).split())
        out.append((int(head.group(1)), head.group(2), bullets, order))
    return out


def scenarios_md(name, items):
    """``items``: three ``(title, situation, expected, pass_line)``."""
    lines = [f"# {name}: the three scenarios", "", "Written before the skill's text.", ""]
    for n, (title, situation, expected, pass_line) in enumerate(items, start=1):
        lines += [f"## {n}. {title}", "", f"- **Situation:** {situation}", f"- **Expected:** {expected}",
                  f"- **Pass line:** {pass_line}", ""]
    return "\n".join(lines)


JUDGE_FAIL = "JUDGEW2100_FAIL"
REPLY_TOKEN = "".join(("STUB", "REPLY", "W2100"))
BAD_ROUTE = "routed" + " as " + "P2"      # in a session reply only when the loaded skill routes a finding below P1
GOOD_ROUTE = "routed" + " as " + "P1"
SYSTEM_PATH = ("/usr/bin", "/bin")

_STUB = r'''#!@PYTHON@ -I
"""A stand-in for the claude program (W2-100's acceptance tests). It never reaches a network."""
import json, os, re, sys
REPLY_TOKEN = @REPLY_TOKEN@
BAD_ROUTE = @BAD_ROUTE@
GOOD_ROUTE = @GOOD_ROUTE@
JUDGE_FAIL = @JUDGE_FAIL@
prompt = sys.stdin.read()


def answer(text, cost):
    print(json.dumps({"type": "result", "result": text, "is_error": False, "total_cost_usd": cost}))
    sys.exit(0)


if REPLY_TOKEN in prompt:                      # a judgement: the reply is in the prompt
    if JUDGE_FAIL in prompt or BAD_ROUTE in prompt:
        answer("The pass line does not hold.\nVERDICT: FAIL", 0.05)
    answer("The pass line holds.\nVERDICT: PASS", 0.05)

skills = os.path.join(os.getcwd(), ".claude", "skills")
text = ""
if os.path.isdir(skills):
    for name in sorted(os.listdir(skills)):
        md = os.path.join(skills, name, "SKILL.md")
        if os.path.isfile(md):
            with open(md, encoding="utf-8") as handle:
                text += handle.read()
# a session that follows its skill: a line of the skill that routes a finding to P2 or P3 sends it there
below = any(re.search(r"\bfindings?\b", l, re.I) and re.search(r"\bP[23]\b", l) for l in text.splitlines())
found = re.search(r"TAGW2100s[0-9]+", prompt)
answer(REPLY_TOKEN + " " + (found.group(0) if found else "notag") + " done as the skill says. The finding is "
       + (BAD_ROUTE if below else GOOD_ROUTE) + ".", 0.25)
'''


@dataclass(frozen=True)
class Stub:
    folder: Path


def install_stub(base):
    folder = Path(base) / "bin"
    folder.mkdir(parents=True, exist_ok=True)
    text = (_STUB.replace("@PYTHON@", sys.executable).replace("@REPLY_TOKEN@", repr(REPLY_TOKEN))
            .replace("@BAD_ROUTE@", repr(BAD_ROUTE)).replace("@GOOD_ROUTE@", repr(GOOD_ROUTE))
            .replace("@JUDGE_FAIL@", repr(JUDGE_FAIL)))
    path = folder / "claude"
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return Stub(folder)


def planted_scenarios(name="the planted skill", finding=False, judge_fail_on=()):
    """Three planted scenarios (each carries a tag the stub reads). With ``finding``, scenario 2 is a security
    finding whose pass line holds when the reply routes it as P1. ``judge_fail_on`` lists scenario numbers whose pass
    line carries the stub's fail marker."""
    items = []
    for n in (1, 2, 3):
        situation = f"TAGW2100s{n} a planted request arrives; the session is asked to carry out planted task {n}."
        expected = f"The session carries out planted task {n} as the skill says."
        pass_line = f"The reply shows planted task {n} carried out."
        if finding and n == 2:
            situation = (f"TAGW2100s{n} a review of the payment module turns up a security finding: a token written "
                         "into the source. The session is asked how the finding is routed.")
            expected = "The session routes the security finding as P1 and stops the work."
            pass_line = "The reply routes the security finding as P1, never lower."
        if n in judge_fail_on:
            pass_line += f" {JUDGE_FAIL}"
        items.append((f"Planted case {n}", situation, expected, pass_line))
    return scenarios_md(name, items)


def skill_md_for_harness(name, version="1.0.0"):
    return "\n".join(["---", f"name: {name}", f'version: "{version}"', 'description: "Plants a skill for the tests."',
                      "metadata:", f'  version: "{version}"', "---", "", f"# {name}", "", "A planted skill.", "",
                      "## Steps", "", "- Carry out the planted task named in the situation.", ""])


def make_project(path):
    """A small committed project: a gitignore and a readme, nothing of this repository."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    (path / ".gitignore").write_text(".gov-runtime/\n__pycache__/\n.env\n", encoding="utf-8")
    (path / "README.md").write_text("A temporary project for W2-100's acceptance tests.\n", encoding="utf-8")
    git(path, "init", "-q", "-b", "main")
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "temporary project")
    return path


def plant_skill(project, rel, name, scenarios_text, skill_text=None):
    folder = Path(project) / rel
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(skill_text if skill_text is not None else skill_md_for_harness(name),
                                     encoding="utf-8")
    (folder / "scenarios.md").write_text(scenarios_text, encoding="utf-8")
    return folder


@dataclass(frozen=True)
class Run:
    args: tuple
    returncode: int
    stdout: str
    stderr: str

    def describe(self):
        return (f"gov {' '.join(self.args)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-3000:]}\n"
                f"stderr:\n{self.stderr[-2000:]}")

    def result(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"gov skilleval gave no JSON envelope on stdout\n{self.describe()}") from None
        assert isinstance(data, dict) and isinstance(data.get("result"), dict), f"no result map\n{self.describe()}"
        return data["result"]

    def verdicts(self):
        return {item.get("scenario"): item.get("verdict") for item in self.result().get("scenarios", [])}


def run_skilleval(project, base, skill_rel, *options, stub=None):
    """``python3 -m gov.cli.main skilleval <skill> [options] --json --root <project>`` with this repository's ``src``,
    an environment built from scratch and the stub ``claude`` first on a PATH of the system folders."""
    assert shutil.which("claude", path=os.pathsep.join(SYSTEM_PATH)) is None, "a claude program is in the system folders"
    base = Path(base)
    for sub in ("home", "tmp", "pycache"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    env = {"PATH": os.pathsep.join(([str(stub.folder)] if stub else []) + list(SYSTEM_PATH)),
           "HOME": str(base / "home"), "TMPDIR": str(base / "tmp"), "LC_ALL": "C.UTF-8", "PYTHONPATH": str(SRC),
           "PYTHONPYCACHEPREFIX": str(base / "pycache")}
    if os.environ.get("PYTHONUSERBASE"):
        env["PYTHONUSERBASE"] = os.environ["PYTHONUSERBASE"]
    args = ["skilleval", str(skill_rel), *options, "--json", "--root", str(project)]
    try:
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args], cwd=str(project), env=env,
                              capture_output=True, text=True, timeout=240, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as exc:
        raise AssertionError(f"gov {' '.join(args)} did not end within 240 s: {exc.stdout!r}") from None
    return Run(tuple(args), done.returncode, done.stdout, done.stderr)


def import_entry(name, **changes):
    entry = {"name": name, "source": "https://example.invalid/skills-collection", "version": "2.3.1",
             "licence": "Apache-2.0", "licence_verdict": "allowed", "adopted": False}
    entry.update(changes)
    return entry


def write_imports(project, entries):
    path = Path(project) / "governance/project/skill-imports.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"imports": entries}, sort_keys=False), encoding="utf-8")
    return path


def read_imports(project):
    data = load_yaml(Path(project) / "governance/project/skill-imports.yaml")
    return {entry.get("name"): entry for entry in data["imports"]}

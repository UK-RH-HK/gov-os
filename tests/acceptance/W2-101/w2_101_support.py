"""Support for W2-101's acceptance tests (DAEO-6icv): paths, the skill readers, the planting helpers, the check
runner, the commit-order reading, the guard runner and the ``gov skilleval`` runner with a stub model.

Every case finds the repository from this file's own location (``REPO_ROOT``), so merged into the ticket's worktree
the cases judge that worktree's files and ``src/``. ``W2_101_SKILLS_DIR`` (an absolute folder holding the three skill
folders) replaces the kernel skills folder; it exists only so a test designer can show a case bites against a
stand-in, and is unset in every real run. Standard library and PyYAML only; no network, no model call (the model is
a stub ``claude`` on a ``PATH`` of the test's own), no copy of the repository (planted files live in ``tmp_path``).
"""
from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
KERNEL_SKILLS = "template/governance/kernel/skills"
SKILLS_ROOT = Path(os.environ.get("W2_101_SKILLS_DIR") or REPO_ROOT / KERNEL_SKILLS)
SKILLS = ("frontend", "ui-ux", "devops")
CHECK_NAME = "check_domain_skill.py"

SECTION_PATTERNS = (("When / not when", r"when\s*/\s*not when"), ("Inputs", r"inputs?\b"), ("Steps", r"steps\b"),
                    ("Done when", r"done when"), ("Output and handover", r"output and handover"),
                    ("Escalation", r"escalation"), ("Never", r"never\b"), ("Sources", r"sources\b"))
PARTS = ("Conventions", "Pre-commit checklist", "Unit-test focus", "Common mistakes", "When to escalate")
POINTS = {"frontend": ("Accessibility", "State", "Browser support"),
          "ui-ux": ("User flows as scenarios",),
          "devops": ("Hermetic builds", "Pinned versions", "Rollback")}
TWELVE = ("task", "status", "work_completed", "files_changed", "evidence", "tests", "discoveries", "risks",
          "lessons", "proposed_decisions", "unresolved", "recommended_next_action")

RECORD_FILE = "scenario-records.yaml"
SUMMARY_FILE = "scenario-summaries.md"
SCENARIOS_FILE = "scenarios.md"


# --------------------------------------------------------------------------------------------------------------
# The skill folders and the check script (I1)
# --------------------------------------------------------------------------------------------------------------

def skill_dir(name):
    return SKILLS_ROOT / name


def need(path: Path) -> Path:
    """The file, or a failure naming it: the red reason on a base that has no skill folder."""
    if not Path(path).is_file():
        pytest.fail(f"{path} does not exist (the skill folder or the file is not there yet)")
    return Path(path)


def read_skill(name):
    return need(skill_dir(name) / "SKILL.md").read_text(encoding="utf-8")


def check_script(name):
    return need(skill_dir(name) / CHECK_NAME)


def clean_env():
    """An environment with no ``PYTHON*`` variable: the script is standard library only."""
    return {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}


def run_check(name, path, cwd=None, script=None, flags=(), timeout=60):
    """``python3 <skill folder>/check_domain_skill.py <path>``: (exit code, stdout + stderr). ``script`` is a
    different script file to run (a copy planted in a folder of the test's)."""
    script = Path(script) if script else check_script(name)
    done = subprocess.run([sys.executable, *flags, str(script), str(path)], capture_output=True, text=True,
                          cwd=str(cwd) if cwd else None, timeout=timeout, stdin=subprocess.DEVNULL, env=clean_env())
    return done.returncode, done.stdout + done.stderr


def lines_of(output):
    return [line.strip() for line in output.splitlines() if line.strip()]


def refused(output, skill=None):
    found = [line for line in lines_of(output) if line.startswith("REFUSED ")]
    if skill is not None:
        found = [line for line in found if line.startswith(f"REFUSED {skill}:")]
    return found


def passes(output):
    return [line for line in lines_of(output) if re.match(r"PASS\b", line)]


def names_missing(output, skill, item):
    """The refusal lines of ``skill`` that say ``missing <item>`` (item matched case-insensitively, whole text)."""
    return [line for line in refused(output, skill)
            if re.search(rf"missing\s+{re.escape(item)}\s*$", line, re.I)]


def planted(tmp_path, text, folder="planted", name="SKILL.md"):
    """A planted SKILL.md (the text as given) in a folder of its own under ``tmp_path``; returns its path."""
    path = tmp_path / folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


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


def headings(body):
    """The level-2 headings of a body (titles, as written), in order."""
    return [h.strip() for h in re.findall(r"^##\s+(.*?)\s*$", body, re.M)]


def section(text, pattern):
    """The text under the first level-2 heading matching ``pattern`` (to the next level-1 or level-2 heading), or None."""
    body = split_frontmatter(text)[1]
    match = re.search(rf"^##\s+(?:{pattern}).*?$(.*?)(?=^#{{1,2}}\s|\Z)", body, re.M | re.I | re.S)
    return match.group(1) if match else None


def section_problems(text):
    """The template's section structure as problems found (empty when it holds)."""
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


def list_items(block):
    return [line for line in block.splitlines() if re.match(r"^\s{0,3}([-*+]|\d+[.)])\s+\S", line)]


def part_line(part):
    """A line that states ``part`` as a heading (``#`` to ``###``) or as a labelled line ``**<part>:**`` (optionally
    a list item), case-insensitive: the reading the ticket's Interface (I1) gives for the five parts and the points."""
    name = re.escape(part)
    return re.compile(rf"^\s*(?:#{{1,3}}\s+{name}\b.*|(?:[-*+]\s+)?\*\*{name}\s*:\s*\*\*.*|(?:[-*+]\s+)?\*\*{name}\*\*\s*:.*)$",
                      re.I)


def labelled_line(point):
    """The labelled-line form ``**<point>:**`` (optionally a list item): the form the area's named points take."""
    name = re.escape(point)
    return re.compile(rf"^\s*(?:[-*+]\s+)?(?:\*\*{name}\s*:\s*\*\*|\*\*{name}\*\*\s*:).*$", re.I)


def has_line(text, pattern):
    return any(pattern.match(line) for line in text.splitlines())


def remove_lines(text, pattern):
    return "\n".join(line for line in text.splitlines() if not pattern.match(line)) + "\n"


def remove_section(text, pattern):
    """``text`` without the first level-2 section whose heading matches ``pattern`` (its heading and body)."""
    return re.sub(rf"^##\s+(?:{pattern})[^\n]*$.*?(?=^#{{1,2}}\s|\Z)", "", text, count=1, flags=re.M | re.S | re.I)


def swap_sections(text, first, second):
    """``text`` with the level-2 sections whose headings match the two patterns exchanged."""
    marks = [m.start() for m in re.finditer(r"^## ", text, re.M)] + [len(text)]
    blocks = [(text[a:b], a, b) for a, b in zip(marks, marks[1:])]

    def find(pattern):
        return next(i for i, (block, _a, _b) in enumerate(blocks)
                    if re.match(rf"##\s+(?:{pattern})", block, re.I))
    i, j = find(first), find(second)
    pieces = [block for block, _a, _b in blocks]
    pieces[i], pieces[j] = pieces[j], pieces[i]
    return text[:marks[0]] + "".join(pieces)


def with_name(text, name):
    """The text with the front matter's ``name`` replaced (the area is chosen from the name)."""
    return re.sub(r"^name:.*$", f"name: {name}", text, count=1, flags=re.M)


def front_block(text):
    """The text up to and including the front matter's closing line."""
    return text[:text.find("\n---", 3) + 4] + "\n"


def insert_in_body(text, line, after_lines=2):
    """The text with ``line`` inserted ``after_lines`` lines after the end of the front matter; returns
    ``(new text, the 1-based number of the inserted line)``."""
    head = front_block(text)
    rest = text[len(head):].split("\n")
    at = head.count("\n") + after_lines
    new = head + "\n".join(rest[:after_lines] + [line] + rest[after_lines:])
    return new, at + 1


# --------------------------------------------------------------------------------------------------------------
# The permission-granting line (I1), read as the Interface words it
# --------------------------------------------------------------------------------------------------------------

PERMISSION_LINE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)?[`'\"]*\s*(allowed-tools|allowed_tools|permissions|permission|"
                             r"allow|deny)\s*[`'\"]*\s*:", re.I)


def permission_lines(text):
    return [(n, line) for n, line in enumerate(text.splitlines(), start=1) if PERMISSION_LINE.match(line)]


def skill_files(folder):
    return sorted(p.relative_to(folder) for p in Path(folder).rglob("*") if p.is_file())


# --------------------------------------------------------------------------------------------------------------
# git: the commit-order reading, on the real history and on planted ones
# --------------------------------------------------------------------------------------------------------------

def _git_env(extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_NAME="W2-101 tests", GIT_AUTHOR_EMAIL="w2-101@example.invalid",
               GIT_COMMITTER_NAME="W2-101 tests", GIT_COMMITTER_EMAIL="w2-101@example.invalid",
               GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    env.update(extra or {})
    return env


def git(repo, *args, check=True, extra_env=None):
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=_git_env(extra_env),
                          stdin=subprocess.DEVNULL)
    if check:
        assert done.returncode == 0, f"git {' '.join(args)} failed in {repo}: {done.stderr}"
    return done


def _first_adding(repo, rel):
    """``(hash, committer time)`` of the first commit that adds ``rel``, or None."""
    out = git(repo, "log", "--reverse", "--diff-filter=A", "--format=%H %ct", "--", rel).stdout.split("\n")
    first = next((line for line in out if line.strip()), None)
    return tuple(first.split()) if first else None


def commit_order_problem(repo, skill):
    """The reading of ``git log`` the cases share, on a real or a planted history: the first commit that adds the
    skill's ``scenarios.md`` is no later than the first that adds its ``SKILL.md``. Returns None when it holds, else a
    message naming the skill and what is wrong (a shallow history, a file never added, the text committed first).
    "No later": the same commit; or the scenarios' commit an ancestor of the text's; where neither is the other's
    ancestor, the earlier committer time."""
    if git(repo, "rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        return f"{skill}: the repository is shallow, its history cannot show which was committed first"
    base = f"{KERNEL_SKILLS}/{skill}"
    scen, text = _first_adding(repo, f"{base}/{SCENARIOS_FILE}"), _first_adding(repo, f"{base}/SKILL.md")
    if scen is None:
        return f"{skill}: no commit adds {base}/{SCENARIOS_FILE} (the file is absent from the history)"
    if text is None:
        return f"{skill}: no commit adds {base}/SKILL.md (the file is absent from the history)"
    if scen[0] == text[0]:
        return None
    if git(repo, "merge-base", "--is-ancestor", scen[0], text[0], check=False).returncode == 0:
        return None
    if git(repo, "merge-base", "--is-ancestor", text[0], scen[0], check=False).returncode == 0:
        return f"{skill}: the skill text ({text[0][:12]}) was committed before its scenarios ({scen[0][:12]})"
    if int(scen[1]) <= int(text[1]):
        return None
    return f"{skill}: the skill text ({text[0][:12]}) was committed before its scenarios ({scen[0][:12]})"


def plant_history(tmp_path, skill, order):
    """A small git repository under ``tmp_path`` holding ``<kernel skills>/<skill>/SKILL.md`` and ``scenarios.md``
    committed in ``order``: ``"scenarios-first"``, ``"skill-first"`` or ``"same"`` (one commit)."""
    repo = tmp_path / f"history-{order}"
    folder = repo / KERNEL_SKILLS / skill
    folder.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    files = {"SKILL.md": f"---\nname: {skill}\nversion: \"1.0.0\"\ndescription: Planted.\n---\n\n# {skill}\n",
             SCENARIOS_FILE: f"# {skill}: scenarios\n"}
    groups = {"scenarios-first": [[SCENARIOS_FILE], ["SKILL.md"]], "skill-first": [["SKILL.md"], [SCENARIOS_FILE]],
              "same": [["SKILL.md", SCENARIOS_FILE]]}[order]
    for n, names in enumerate(groups, start=1):
        for name in names:
            (folder / name).write_text(files[name], encoding="utf-8")
        git(repo, "add", "-A")
        when = f"2026-11-0{n}T10:00:00+00:00"
        git(repo, "commit", "-q", "-m", f"commit {n}", extra_env={"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when})
    return repo


# --------------------------------------------------------------------------------------------------------------
# The records and the summaries (S4)
# --------------------------------------------------------------------------------------------------------------

class _PlainLoader(yaml.SafeLoader):
    """A safe loader that keeps timestamps as the strings written, so ``run_at`` is read as written."""


_PlainLoader.yaml_implicit_resolvers = {
    key: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(path):
    return yaml.load(Path(path).read_text(encoding="utf-8"), Loader=_PlainLoader)


def records_of(name):
    """The ``records`` list of the skill's record file."""
    path = need(skill_dir(name) / RECORD_FILE)
    data = load_yaml(path)
    assert isinstance(data, dict) and isinstance(data.get("records"), list), \
        f"{path} is not a YAML map with a list under 'records'"
    return data["records"]


# --------------------------------------------------------------------------------------------------------------
# gov skilleval with a stub model (S5, F3, F4): a project of the test's own, a stub claude on its own PATH
# --------------------------------------------------------------------------------------------------------------

SYSTEM_PATH = ("/usr/bin", "/bin")
FAIL_MARK = "PASSLINEW2101FAILS"          # in a scenario's Pass line: the stub's judgement says FAIL
IMPORTS_REL = "governance/project/skill-imports.yaml"

_STUB = r'''#!@PYTHON@ -I
"""A stand-in for the claude program (W2-101's acceptance tests). It never reaches a network."""
import json, os, sys, time
LOG = @LOG@
prompt = sys.stdin.read()
judge = "You judge whether a session's reply meets" in prompt
os.makedirs(LOG, exist_ok=True)
with open(os.path.join(LOG, "%.6f-%d.json" % (time.time(), os.getpid())), "w", encoding="utf-8") as handle:
    json.dump({"role": "judge" if judge else "session", "stdin": prompt, "argv": sys.argv[1:]}, handle)
if judge:
    text = "The pass line does not hold.\nVERDICT: FAIL" if @FAIL_MARK@ in prompt else "The pass line holds.\nVERDICT: PASS"
else:
    text = "Done as the skill says."
print(json.dumps({"type": "result", "result": text, "is_error": False, "total_cost_usd": 0.01}))
'''


class Stub:
    def __init__(self, folder: Path, log: Path):
        self.folder, self.log = folder, log

    def calls(self):
        if not self.log.is_dir():
            return []
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(self.log.glob("*.json"))]


def install_stub(base):
    base = Path(base)
    folder = base / "bin"
    folder.mkdir(parents=True, exist_ok=True)
    text = (_STUB.replace("@PYTHON@", sys.executable).replace("@LOG@", repr(str(base / "log")))
            .replace("@FAIL_MARK@", repr(FAIL_MARK)))
    path = folder / "claude"
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return Stub(folder, base / "log")


def make_project(path):
    """A small committed project: a gitignore and a readme, nothing of this repository."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    (path / ".gitignore").write_text(".gov-runtime/\n__pycache__/\n", encoding="utf-8")
    (path / "README.md").write_text("A temporary project for W2-101's acceptance tests.\n", encoding="utf-8")
    git(path, "init", "-q", "-b", "main")
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "temporary project")
    return path


def scenarios_md(name, fail=()):
    """A ``scenarios.md`` in W2-11's form; the scenarios numbered in ``fail`` carry the stub's failing mark."""
    lines = [f"# {name}: the three scenarios", ""]
    for n in (1, 2, 3):
        mark = f" {FAIL_MARK}{n}" if n in fail else ""
        lines += [f"## {n}. Planted case {n}", "",
                  f"- **Situation:** a planted request {n} arrives for the {name} part and must be handled.",
                  f"- **Expected:** the planted task {n} is carried out as the part says.",
                  f"- **Pass line:** the reply shows planted task {n} carried out.{mark}", ""]
    return "\n".join(lines)


def plant_part(project, rel, name, fail=()):
    """A planted skill (or part) folder with a SKILL.md and a ``scenarios.md``; returns the folder."""
    folder = Path(project) / rel
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(
        f'---\nname: {name}\nversion: "1.0.0"\ndescription: "Plants a part for the acceptance tests of an adoption."\n'
        f'metadata:\n  version: "1.0.0"\n---\n\n# {name}\n\nA planted part. It states a method and grants nothing.\n',
        encoding="utf-8")
    (folder / SCENARIOS_FILE).write_text(scenarios_md(name, fail), encoding="utf-8")
    return folder


def import_entry(name, **changes):
    entry = {"name": name, "source": "https://example.invalid/skills-collection", "version": "2.3.1",
             "licence": "Apache-2.0", "licence_verdict": "allowed", "adopted": False}
    entry.update(changes)
    return {k: v for k, v in entry.items() if v is not DROP}


DROP = object()   # ``import_entry(name, licence=DROP)`` leaves the key out


def write_imports(project, entries):
    path = Path(project) / IMPORTS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"imports": entries}, sort_keys=False), encoding="utf-8")
    return path


def read_imports(project):
    data = load_yaml(Path(project) / IMPORTS_REL)
    assert isinstance(data, dict) and isinstance(data.get("imports"), list), f"{IMPORTS_REL} is not a map with imports"
    return {entry.get("name"): entry for entry in data["imports"]}


class Run:
    def __init__(self, args, done):
        self.args, self.returncode, self.stdout, self.stderr = args, done.returncode, done.stdout, done.stderr

    def describe(self):
        return (f"gov {' '.join(self.args)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-3000:]}\n"
                f"stderr:\n{self.stderr[-3000:]}")

    def result(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"gov skilleval gave no JSON envelope on stdout\n{self.describe()}") from None
        result = data.get("result") if isinstance(data, dict) else None
        assert isinstance(result, dict), f"the envelope has no result map\n{self.describe()}"
        return result

    def verdicts(self):
        scenarios = self.result().get("scenarios")
        assert isinstance(scenarios, list) and len(scenarios) == 3, f"three scenarios are not listed\n{self.describe()}"
        return {item.get("scenario"): item.get("verdict") for item in scenarios}


def skilleval(project, base, stub, skill_rel, *options):
    """``python3 -m gov.cli.main skilleval <skill> [options] --json --root <project>`` with this repository's
    ``src/`` and a ``PATH`` of the stub's folder and the system folders only."""
    base = Path(base)
    for name in ("home", "tmp", "pycache"):
        (base / name).mkdir(parents=True, exist_ok=True)
    assert not any((Path(p) / "claude").exists() for p in SYSTEM_PATH), "a real claude is in the system folders"
    env = {"PATH": os.pathsep.join([str(stub.folder), *SYSTEM_PATH]), "HOME": str(base / "home"),
           "TMPDIR": str(base / "tmp"), "LC_ALL": "C.UTF-8", "PYTHONPATH": str(SRC),
           "PYTHONPYCACHEPREFIX": str(base / "pycache")}
    args = ["skilleval", str(skill_rel), *options, "--json", "--root", str(project)]
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args], cwd=str(project), env=env,
                          capture_output=True, text=True, timeout=240, stdin=subprocess.DEVNULL)
    return Run(tuple(args), done)


# --------------------------------------------------------------------------------------------------------------
# The guard (S2): this repository's live hook run on a planted tree, as Claude Code runs it
# --------------------------------------------------------------------------------------------------------------


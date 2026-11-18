"""Support code for the W2-36 acceptance tests: ``gov discover`` (ticket DAEO-w19l).

Public interfaces only: ``gov`` run as a subprocess (``python3 -m gov.cli.main <args> --root <P>`` with
``PYTHONPATH`` this worktree's ``src/``), ``git``, the files of the planted project and the spec-writing skill's
``check_spec.py``. No module of ``gov.discover`` is imported.

**The planted project P** (S1's verify): a git repository named ``planted-project`` (so ``tk`` gives ids ``pp-xxxx``)
holding ``.tickets/``, the vendored ``governance/kernel/bin/tk`` (from ``template/governance/kernel/bin/tk``),
``openspec/schemas/feature-readiness/`` (from ``template/openspec/``), ``governance/project/facts.yaml`` (this
worktree's), the kernel templates at ``template/governance/kernel/templates/`` (where ``gov brief`` looks first), the
adopted template's ``.gitignore``, no memory store, and four planted files: ``docs/report.md`` and
``openspec/specs/report/spec.md`` (both mention "CSV" and "export"), the ticket ``.tickets/pp-rp01.md`` (its body
mentions "report page") and ``docs/unrelated.md`` (none of the idea's words). All of it is committed.

**P with a change** (``build_with_change``): P plus ``openspec/changes/add-csv-export-report-page/`` as the interface
says discovery writes it (proposal.md at LITE, the schema template's readiness.yaml, a spec.md that passes) and its
discovery ticket ``.tickets/pp-ds01.md``, committed: the start of the check, feature-ticket and refusal cases.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import site
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SRC = REPO_ROOT / "src"
CHECK_SPEC = REPO_ROOT / "template/governance/kernel/skills/spec-writing/check_spec.py"
FIXTURE_FAILED = "W2-36 fixture could not be built (not the feature under test)"
GOV_TIMEOUT_S = 180.0

# --- what the ticket and its interface fix -------------------------------------------------------------------------
PROJECT_NAME = "planted-project"
WORDS = "add CSV export to the report page"
PLAIN_WORDS = ["how", "could", "we", "add", "CSV", "export", "to", "the", "report", "page?"]  # S7, unquoted
PLAIN_TEXT = " ".join(PLAIN_WORDS)
CHANGE = "add-csv-export-report-page"
SPEC_ID = f"SPEC-{CHANGE}"
CHANGE_REL = f"openspec/changes/{CHANGE}"
SPEC_REL = f"{CHANGE_REL}/spec.md"
CHANGE_FILES = ("proposal.md", "readiness.yaml", "spec.md")
PARTS = ("Problem", "Users and scenarios", "Goals", "Non-goals", "KPIs", "Test data", "Out of scope",
         "Open questions", "Accepted by")
HEADINGS = (*PARTS, "Verify", "Sources read")
DRAFT_REFUSED = ("Users and scenarios", "Goals", "Non-goals", "KPIs", "Test data", "Out of scope", "Accepted by")
DRAFT_NOT_REFUSED = ("Problem", "Open questions")

# The schema's rows (template/openspec/schemas/feature-readiness/schema.yaml): n -> (key, schema name)
ROWS = {1: ("intent", "intent/outcome"), 2: ("actor", "user/actor"), 3: ("journey", "journey/workflow"),
        4: ("scenarios", "scenarios"), 5: ("inputs", "inputs"), 6: ("data_model", "data model/schema"),
        7: ("test_data", "representative test data"), 8: ("processing", "processing/algorithm"),
        9: ("outputs", "expected outputs"), 10: ("functional", "functional requirements"),
        11: ("nfr", "non-functional requirements"), 12: ("ux", "UX/interactions where applicable"),
        13: ("backend", "backend/service behaviour"), 14: ("state", "database/state requirements"),
        15: ("interfaces", "interface/API/event contracts"), 16: ("security", "security/privacy"),
        17: ("integrations", "integrations"), 18: ("devops", "DevOps/runtime"), 19: ("observability", "observability"),
        20: ("performance", "performance/capacity"), 21: ("cost", "cost constraints"),
        22: ("recovery", "recovery/fallback"), 23: ("success", "measurable success criteria"),
        24: ("failure", "measurable failure criteria"), 25: ("acceptance_tests", "independent acceptance/system tests"),
        26: ("docs_ops", "documentation/operations needs")}
NUMBER = {key: n for n, (key, _) in ROWS.items()}
MANDATORY = ("intent", "actor", "scenarios", "inputs", "data_model", "outputs", "security", "success", "failure",
             "acceptance_tests")
STANDARD_EXTRA = ("nfr", "performance")  # performance-capacity: rows 11 and 20
GAP_CLASS = {"inputs": ("data", "product-spec"), "data_model": ("data", "product-spec"),
             "test_data": ("data", "product-spec"), "nfr": ("research", "research"),
             "integrations": ("research", "research"), "performance": ("research", "research"),
             "cost": ("research", "research"), "acceptance_tests": ("test-design", "independent-test-designer")}


def gap_class(key):
    return GAP_CLASS.get(key, ("discovery", "product-spec"))


# --- the planted files ---------------------------------------------------------------------------------------------
REPORT_TICKET = "pp-rp01"
DISCOVERY_TICKET = "pp-ds01"
PLANTED = {
    "docs/report.md": "# The report\n\nThe monthly report lists every sale.\nFinance wants it as CSV, through an "
                      "export button.\n",
    "openspec/specs/report/spec.md": "# Report specification\n\n## Purpose\n\nThe report shows the month's sales. "
                                     "A CSV export is asked for.\n",
    f".tickets/{REPORT_TICKET}.md": f"---\nid: {REPORT_TICKET}\nstatus: open\ndeps: []\nlinks: []\n"
                                    "created: 2026-11-01T10:00:00Z\ntype: task\npriority: 2\n---\n"
                                    "# Slow loading\n\nThe report page takes nine seconds to load.\n",
    "docs/unrelated.md": "# Login\n\nLogin uses single sign-on with a hardware key.\n",
}
SOURCES = ("docs/report.md", "openspec/specs/report/spec.md", f".tickets/{REPORT_TICKET}.md")
UNRELATED = "docs/unrelated.md"
GITIGNORE = ".gov-runtime/\n__pycache__/\n"

PROPOSAL = f"""---
id: {SPEC_ID}
type: specification
status: DRAFT
profile: LITE
spine: false
capability_types: []
discovery_ticket: {DISCOVERY_TICKET}
---
# {WORDS}
"""
DISCOVERY_TICKET_TEXT = f"""---
id: {DISCOVERY_TICKET}
status: open
deps: []
links: []
created: 2026-11-17T10:00:00Z
type: task
priority: 2
class: specification
role: product-spec
discovers: {CHANGE}
allowed_paths: [{CHANGE_REL}/**]
reads: []
needs: []
waits_on: []
---
# Discovery: {WORDS}
"""

K1 = ("A visitor who presses Export on the report page receives a CSV file holding one line per report row within "
      "five seconds.")
K1_FAILS = "no file arrives within ten seconds, or the file holds a different number of rows than the page shows."
K2 = "Every figure in the CSV file matches the figure the report page shows, to the cent."
K2_FAILS = "any figure in the file differs from the figure on the page."
K1_VERIFY = "python3 -m pytest tests/acceptance/report/test_export.py -k rows: passes, one line per report row"
K2_VERIFY = "python3 -m pytest tests/acceptance/report/test_export.py -k figures: passes, every figure matches"
NON_GOALS = ("Exporting the charts as pictures.", "Sending exports by email on a schedule.")
GOALS = "## Goals\n- A visitor can save the figures of the report page as a CSV file.\n"
GOALS_SLOT = "## Goals\n<!-- What the change makes true, one bullet each. -->\n- <what the change makes true>\n"
K1_LINE = f"- K1: {K1}\n"
K1_CODE = "the export_rows output"
K1_CODE_LINE = f"- K1: A visitor who presses Export on the report page receives {K1_CODE} within five seconds.\n"
VERIFY_K2 = f"- K2: {K2_VERIFY}\n"
VERIFY_K3 = "- K3: python3 -m pytest tests/acceptance/report/test_export.py -k extra: passes\n"

PASSING_SPEC = f"""## Problem
Visitors to the report page cannot take its figures away, so they copy them by hand and make mistakes.

## Users and scenarios
- A finance analyst opens last month's report page and wants its figures in a spreadsheet.
- A team lead shares one report's figures with a colleague who has no account.

{GOALS}
## Non-goals
- {NON_GOALS[0]}
- {NON_GOALS[1]}

## KPIs
{K1_LINE}  Fails if: {K1_FAILS}
- K2: {K2}
  Fails if: {K2_FAILS}

## Test data
| source | kind | owner | licence or recipe | privacy | secrets | hidden half | secured |
| --- | --- | --- | --- | --- | --- | --- | --- |
| two hundred report rows | synthetic | QA engineer | built from a fixed seed, twenty rows per month | none | none | n/a | yes |

## Out of scope
- Export from the other pages: a later ticket.

## Open questions
- Question: Which separator does the file use?
  - Options: comma (cost: figures holding commas are quoted); semicolon (cost: some spreadsheets need a setting)
  - Recommendation: comma, as the common spreadsheets read it directly.

## Accepted by
The product owner, on the passing check and the passing acceptance tests.

## Verify
- K1: {K1_VERIFY}
{VERIFY_K2}
## Sources read
- docs/report.md: Finance wants it as CSV, through an export button.

Memory: not available: no memory store in this project
"""

# F1's four variants of the passing spec: (id, the text, the line the check must print)
VARIANTS = {
    "k2-has-no-verify": (PASSING_SPEC.replace(VERIFY_K2, ""), "REFUSED Verify: K2 has no verify"),
    "k3-is-not-a-kpi": (PASSING_SPEC.replace(VERIFY_K2, VERIFY_K2 + VERIFY_K3), "REFUSED Verify: K3 is not a KPI"),
    "k1-names-code": (PASSING_SPEC.replace(K1_LINE, K1_CODE_LINE), None),  # the line check_spec.py prints
    "goals-only-a-slot": (PASSING_SPEC.replace(GOALS, GOALS_SLOT), "REFUSED Goals: missing"),
}

# S4: a planted change at LITE, every mandatory row PRESENT but scenarios, inputs and acceptance_tests
GAPS_CHANGE = "csv-export-gaps"
GAPS_SPEC_ID = f"SPEC-{GAPS_CHANGE}"
GAPS_CHANGE_REL = f"openspec/changes/{GAPS_CHANGE}"
GAPS_OPEN = ("scenarios", "inputs", "acceptance_tests")


def gaps_readiness(linked=None):
    """The planted readiness.yaml of S4 (``linked``: a ticket the scenarios row's gap_ticket already names)."""
    lines = ["# Feature-readiness record, planted for the W2-36 tests.", "rows:"]
    for n, (key, _) in ROWS.items():
        if key == "scenarios":
            gap = linked or "null"
            lines.append(f"  - {{n: {n}, key: {key}, state: MISSING, evidence: [], reason: null, gap_ticket: {gap}}}")
        elif key == "inputs":
            lines.append(f"  - {{n: {n}, key: {key}, state: MISSING, evidence: [], reason: null, gap_ticket: null, "
                         "depends_on: [scenarios]}")
        elif key == "acceptance_tests":
            lines.append(f"  - {{n: {n}, key: {key}, state: PROVISIONAL, evidence: [], "
                         "reason: \"the test plan is not accepted yet\", gap_ticket: null}")
        elif key in MANDATORY:
            lines.append(f"  - {{n: {n}, key: {key}, state: PRESENT, evidence: [\"docs/report.md#the-report\"], "
                         "reason: null, gap_ticket: null}")
        else:
            lines.append(f"  - {{n: {n}, key: {key}, state: MISSING, evidence: [], reason: null, gap_ticket: null}}")
    return "\n".join(lines) + "\n"


GAPS_PROPOSAL = PROPOSAL.replace(SPEC_ID, GAPS_SPEC_ID)


# --------------------------------------------------------------------------
# Running things
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Run:
    argv: tuple
    returncode: int
    stdout: str
    stderr: str

    @property
    def output(self):
        return self.stdout + "\n" + self.stderr

    def lines(self):
        return [line.strip() for line in self.output.splitlines()]

    def describe(self):
        return (f"{' '.join(map(str, self.argv))}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-4000:]}\n"
                f"stderr:\n{self.stderr[-4000:]}")

    def envelope(self):
        """The ``--json`` envelope (the last stdout line that is a JSON object), or None."""
        for line in reversed(self.stdout.strip().splitlines()):
            try:
                found = json.loads(line)
            except ValueError:
                continue
            if isinstance(found, dict):
                return found
        try:
            found = json.loads(self.stdout)
        except ValueError:
            return None
        return found if isinstance(found, dict) else None


def closed_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]  # closed again when the block ends: nothing listens there


def environment(home, no_network=False):
    """A fake HOME, this worktree's src/, the real user base, no GOV_ variable of the caller's, a pin never followed."""
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("GOV_", "PYTHON", "PYTEST_")) and key not in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY")}
    env.update({
        "HOME": str(home), "PYTHONPATH": str(SRC), "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUSERBASE": os.environ.get("PYTHONUSERBASE") or site.getuserbase(), "LC_ALL": "C.UTF-8",
        "GOV_PIN": "off", "GOV_REBUILD_LOCK": str(Path(home) / "rebuild.lock"),
        "GOV_VECTOR_CACHE_DIR": str(Path(home) / "vector-cache"), "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W2-36 tests", "GIT_AUTHOR_EMAIL": "w2-36@example.invalid",
        "GIT_COMMITTER_NAME": "W2-36 tests", "GIT_COMMITTER_EMAIL": "w2-36@example.invalid",
    })
    if no_network:  # S5: no key, and every proxy a closed local port
        proxy = f"http://127.0.0.1:{closed_port()}"
        for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
            env[name] = proxy
        env.pop("NO_PROXY", None)
        env.pop("no_proxy", None)
    return env


def run(argv, cwd, env, timeout=GOV_TIMEOUT_S):
    assert Path(cwd).resolve() != REPO_ROOT.resolve(), "no command of these tests runs in this worktree"
    try:
        done = subprocess.run([str(a) for a in argv], cwd=str(cwd), env=env, capture_output=True, text=True,
                              timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as exc:
        return Run(tuple(argv), 124, str(exc.stdout or ""), f"timed out after {timeout}s")
    return Run(tuple(argv), done.returncode, done.stdout, done.stderr)


def gov(project, *args, home, no_network=False):
    """``python3 -m gov.cli.main <args> --root <project>``, run in the project."""
    return run([sys.executable, "-m", "gov.cli.main", *args, "--root", project], project,
               environment(home, no_network))


def discover(project, *args, home, no_network=False):
    return gov(project, "discover", *args, home=home, no_network=no_network)


def check_spec(path, home):
    return run([sys.executable, CHECK_SPEC, path], Path(path).parent, environment(home))


def git(project, *args):
    done = subprocess.run(["git", *args], cwd=str(project), capture_output=True, text=True,
                          env={**environment(Path(project).parent), "PYTHONPATH": ""})
    assert done.returncode == 0, f"git {' '.join(args)} failed: {done.stderr}"
    return done.stdout


def porcelain(project):
    """``git status --porcelain --untracked-files=all``, as a sorted list of its lines."""
    return sorted(line for line in git(project, "status", "--porcelain", "--untracked-files=all").splitlines() if line)


def porcelain_paths(project):
    return sorted(line[3:] for line in porcelain(project))


def snapshot(project):
    """{path: bytes} of every file outside .git."""
    root = Path(project)
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*"))
            if path.is_file() and ".git" not in path.relative_to(root).parts}


def tickets(project):
    return sorted(path.stem for path in (Path(project) / ".tickets").glob("*.md"))


# --------------------------------------------------------------------------
# Building the projects
# --------------------------------------------------------------------------

def _write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_project(base):
    """P (S1's verify), committed; its path (``<base>/planted-project``)."""
    project = Path(base) / PROJECT_NAME
    project.mkdir(parents=True)
    git(project, "init", "-q", "-b", "main")
    git(project, "config", "user.name", "W2-36 tests")
    git(project, "config", "user.email", "w2-36@example.invalid")
    tk = project / "governance/kernel/bin/tk"
    tk.parent.mkdir(parents=True)
    shutil.copy2(REPO_ROOT / "template/governance/kernel/bin/tk", tk)
    tk.chmod(0o755)
    shutil.copytree(REPO_ROOT / "template/openspec/schemas/feature-readiness",
                    project / "openspec/schemas/feature-readiness")
    (project / "governance/project").mkdir(parents=True)
    shutil.copy2(REPO_ROOT / "governance/project/facts.yaml", project / "governance/project/facts.yaml")
    shutil.copytree(REPO_ROOT / "template/governance/kernel/templates",
                    project / "template/governance/kernel/templates")
    _write(project, ".gitignore", GITIGNORE)
    for rel, text in PLANTED.items():
        _write(project, rel, text)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "the planted project P")
    assert porcelain(project) == [], f"P is not clean after its commit: {porcelain(project)}"
    return project


def copy_project(source, base):
    """A copy of a planted project (its .git included) at ``<base>/planted-project``."""
    target = Path(base) / PROJECT_NAME
    shutil.copytree(source, target, symlinks=True)
    return target


def build_with_change(project_p, base, home):
    """P with the change discovery would have written (a spec that passes) and its discovery ticket, committed."""
    project = copy_project(project_p, base)
    _write(project, f"{CHANGE_REL}/proposal.md", PROPOSAL)
    shutil.copy2(project / "openspec/schemas/feature-readiness/templates/readiness.yaml",
                 project / CHANGE_REL / "readiness.yaml")
    _write(project, SPEC_REL, PASSING_SPEC)
    _write(project, f".tickets/{DISCOVERY_TICKET}.md", DISCOVERY_TICKET_TEXT)
    passing = check_spec(project / SPEC_REL, home)
    assert passing.returncode == 0 and "PASS" in passing.lines(), \
        f"the planted passing spec does not pass check_spec.py:\n{passing.describe()}"
    probe = Path(base) / "k1-names-code.md"  # F1's code variant: check_spec.py itself refuses it
    probe.write_text(VARIANTS["k1-names-code"][0], encoding="utf-8")
    refused = check_spec(probe, home)
    probe.unlink()
    assert refused.returncode == 1 and code_line(refused), \
        f"check_spec.py does not refuse K1 naming code:\n{refused.describe()}"
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "a change with a passing spec")
    return project


def code_line(check_run):
    """The ``REFUSED KPIs: K1 names code (...)`` line a check printed, or None."""
    return next((line for line in check_run.lines() if line.startswith("REFUSED KPIs: K1 names code (")), None)


def plant_gaps(project, linked=None):
    """S4's planted change at LITE (committed)."""
    _write(project, f"{GAPS_CHANGE_REL}/proposal.md", GAPS_PROPOSAL)
    _write(project, f"{GAPS_CHANGE_REL}/readiness.yaml", gaps_readiness(linked))
    _write(project, f"{GAPS_CHANGE_REL}/spec.md", PASSING_SPEC)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "a change with readiness gaps")


# --------------------------------------------------------------------------
# Reading what was written
# --------------------------------------------------------------------------

def front_matter(path):
    """The YAML front matter of a markdown file (a mapping), or {}."""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        return {}
    found = yaml.safe_load("\n".join(lines[1:end]))
    return found if isinstance(found, dict) else {}


def ticket(project, ticket_id):
    return front_matter(Path(project) / ".tickets" / f"{ticket_id}.md")


def kpi_items(front, kind):
    """``[(line, verify or None)]`` of a ticket's success or failure KPIs: a ``{line, verify}`` mapping, or a string
    holding ``Verify:``."""
    kpis = front.get("kpis") if isinstance(front.get("kpis"), dict) else {}
    items = kpis.get(kind) if isinstance(kpis.get(kind), list) else []
    found = []
    for item in items:
        if isinstance(item, dict):
            found.append((str(item.get("line", "")), item.get("verify") if isinstance(item.get("verify"), str)
                          else None))
        else:
            text = str(item)
            split = re.search(r"\s*Verify:\s*", text)
            found.append((text[:split.start()] if split else text, text[split.end():] if split else None))
    return found


def plain(text):
    """Whitespace folded, backticks removed: for comparing a written line with the planted text."""
    return " ".join(str(text or "").replace("`", "").split())


def sections(text):
    """{heading: body} of a markdown file's ``##`` sections, in order (HTML comments do not hide a heading)."""
    found, current = {}, None
    for line in text.splitlines():
        head = re.match(r"^##(?!#)\s+(.*?)\s*$", line)
        if head:
            current = head.group(1)
            found[current] = []
        elif current is not None:
            found[current].append(line)
    return {name: "\n".join(body) for name, body in found.items()}


def headings(text):
    """The ``##`` headings outside HTML comments, in order."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return [m.group(1) for m in re.finditer(r"^##(?!#)\s+(.*?)\s*$", text, flags=re.M)]


def packages(open_questions):
    """The packages of an Open questions section: each ``(question, options, recommendation)``."""
    found = []
    for chunk in re.split(r"(?m)^(?=\s*[-*]\s+Question:)", open_questions):
        question = re.search(r"(?m)^\s*[-*]\s+Question:\s*(.*)$", chunk)
        if not question:
            continue
        options = re.search(r"(?m)^\s*[-*]\s+Options:\s*(.*)$", chunk)
        recommendation = re.search(r"(?m)^\s*[-*]\s+Recommendation:\s*(.*)$", chunk)
        found.append((question.group(1).strip(), options.group(1).strip() if options else None,
                      recommendation.group(1).strip() if recommendation else None))
    return found


def rows_named(question):
    """The schema rows a package's question names, by key or by schema name (a whole word, not part of a
    hyphenated type such as performance-capacity)."""
    named = set()
    for key, name in ROWS.values():
        for form in {key, key.replace("_", " "), name}:
            if re.search(r"(?<![\w/-])" + re.escape(form) + r"(?![\w/-])", question, flags=re.I):
                named.add(key)
    return named


def leaves(value):
    """Every string leaf of a JSON value."""
    if isinstance(value, dict):
        for item in value.values():
            yield from leaves(item)
    elif isinstance(value, list):
        for item in value:
            yield from leaves(item)
    elif isinstance(value, str):
        yield value


def opened(outcome):
    """The run exited 0 and made exactly one ticket: its id."""
    assert outcome.run.returncode == 0, f"gov discover did not exit 0:\n{outcome.run.describe()}"
    assert len(outcome.new_tickets) == 1, f"expected exactly one new ticket, got {outcome.new_tickets}"
    return outcome.new_tickets[0]


def spec_text(outcome):
    path = outcome.project / SPEC_REL
    assert path.is_file(), f"no {SPEC_REL} after the run:\n{outcome.run.describe()}"
    return path.read_text(encoding="utf-8")

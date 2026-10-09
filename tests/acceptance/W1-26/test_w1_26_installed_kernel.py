"""``gov check`` and the schema check in a project with an installed kernel (DEC-579; the follow-up after W1-41).

DEC-579: "``gov check`` reads the check declarations, and the schema check reads the schemas, from the
installed kernel as well as from the template layout: today an installed project runs no declared check."

A project carries its kernel in one of two layouts: the template layout (``template/governance/kernel/``,
as the repository that develops the kernel has it) or the installed layout (``governance/kernel/``, as a
project that adopted the kernel has it).

What the cases hold (README, section "Checks in a project with an installed kernel"):

- **Installed layout only.** The declarations under ``governance/kernel/checks/`` are listed and run as the
  same declarations are in the template layout; the declared command is started in the project's root and
  its result reported; the schema check judges records against ``governance/kernel/schemas/``.
- **Neither layout.** The answer of today, pinned.
- **Both layouts.** Alike: every check once, the answer of the template layout alone. Where they differ:
  a declaration file in one layout only is run; one check id declared differently in the two is refused; a
  record is held to the schemas of both.
- **Failure stays failure.** A declaration under the installed layout that is not valid is refused as the
  same file is in the template layout, named by the path it has in the project.

Every project is a temporary git repository built from scratch: a few records, a small check of the case's
own, and single named kernel files (two declarations, three schemas) copied where a real one is needed. The
code under test is this worktree's ``src/``, given to ``gov`` by the suite's launcher; no project holds a
copy of it. No network, no model, no daemon.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_26_support as support  # noqa: E402
import test_w1_26_probe_records as probes  # noqa: E402
import test_w1_26_skill_validator as skills  # noqa: E402

cli_support = support.cli_support
REPO_ROOT = support.REPO_ROOT

TEMPLATE = "template/governance/kernel"
INSTALLED = "governance/kernel"
LAYOUTS = {"template": TEMPLATE, "installed": INSTALLED}

INVALID = "CHECK_DECLARATION_INVALID"
CHECK_FAILED = "CHECK_FAILED"
SCHEMA_CHECK = "core-schema"
SKILL_CHECK = "skill-regression-orchestration"
SKILL = "orchestration"
SMALL = "small-check"
SMALL_FOUND = "SMALL_CHECK_FOUND"
SMALL_FAMILY = "graph integrity"
SCHEMA_FAMILY = "schema/invariants"
ANSWER_REL = "docs/small-check-answer.txt"

# Kernel files a case copies by name from this repository's kernel, and no other.
KERNEL_SCHEMAS = ("common.schema.json", "ticket.schema.json", "probe.schema.json")

# The small check of the cases' own: it reads one file of the project it is started in and answers as a
# declared check answers (JSON findings and exit code 1, or exit code 0).
SMALL_SCRIPT = (
    "import json, pathlib, sys\n"
    f"answer = pathlib.Path({ANSWER_REL!r})\n"
    "word = answer.read_text(encoding='utf-8').strip() if answer.is_file() else 'no answer file in the working directory'\n"
    "if word == 'green':\n"
    "    sys.exit(0)\n"
    f"print(json.dumps([{{'code': {SMALL_FOUND!r}, 'message': word}}]))\n"
    "sys.exit(1)\n"
)

BUILT_IN = ("openspec-validate", "skill-version", "readiness")   # the checks gov check runs without a declaration


# --------------------------------------------------------------------------
# The temporary project
# --------------------------------------------------------------------------

def kernel_file(rel):
    """The text of one named file of this repository's kernel."""
    return (REPO_ROOT / TEMPLATE / rel).read_text(encoding="utf-8")


def declaration_text(check_id, command, family=SMALL_FAMILY, severity="hard-block", **more):
    fields = {"id": check_id, "family": family, "tier": "G1", "severity": severity, "command": command, **more}
    return "".join(f"{key}: {json.dumps(value)}\n" for key, value in fields.items())


def task_record(**changes):
    front = {"id": "PROJ-0001", "type": "task", "status": "OPEN", "state_class": "AUTHORITATIVE",
             "title": "A ticket", "role": "engineer", "allowed_paths": ["src/**"], "kpis": ["one case is green"]}
    front.update(changes)
    front = {key: value for key, value in front.items() if value is not ...}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# A ticket\n"


TASK_REL = "docs/records/PROJ-0001.md"
PROBE_REL = probes.RECORD


class Scratch:
    """A project built from scratch. ``layouts`` names where it holds a kernel; none is a project without one."""

    def __init__(self, root, layouts=(), small_from=None, answer="green"):
        self.root = Path(root)
        self.root.mkdir(parents=True)
        support.git(self.root, "init", "-q", "-b", "main")
        self.write("README.md", "# A project\n")
        self.write(".gitignore", ".gov-runtime/\n")
        self.write(ANSWER_REL, answer + "\n")
        self.write(TASK_REL, task_record())
        self.layouts = tuple(layouts)
        # the path the small check's command names: the kernel the project holds (the first, where it holds two)
        small_from = small_from or (self.layouts[0] if self.layouts else None)
        for kernel in self.layouts:
            self.write(f"{kernel}/bin/small_check.py", SMALL_SCRIPT)
            self.write(f"{kernel}/checks/{SMALL}.yaml",
                       declaration_text(SMALL, f"python3 {small_from}/bin/small_check.py"))
            self.write(f"{kernel}/checks/{SCHEMA_CHECK}.yaml", kernel_file(f"checks/{SCHEMA_CHECK}.yaml"))
            for name in KERNEL_SCHEMAS:
                self.write(f"{kernel}/schemas/{name}", kernel_file(f"schemas/{name}"))

    def write(self, rel, text):
        return support.write(self.root, rel, text)

    def remove(self, rel):
        path = self.root / rel
        assert self.root in path.resolve().parents, f"{path} is not in the temporary project"
        path.unlink()

    def gov(self, sandbox, *args):
        support.commit_all(self.root)
        return cli_support.run_gov_with_code(REPO_ROOT, self.root, sandbox, *args)

    def listed(self, sandbox, interface):
        run = self.gov(sandbox, support.COMMAND, "--list", "--json")
        envelope = cli_support.assert_envelope(run, interface, command=support.COMMAND)
        assert envelope["ok"] is True, f"gov check --list did not succeed\n{run.describe()}"
        return envelope["result"]["checks"]

    def checked(self, sandbox, interface):
        """``gov check --json``: the envelope, the result (the error's details where a check is red), the run."""
        run = self.gov(sandbox, support.COMMAND, "--json")
        envelope = support.envelope_of(run, interface)
        error = envelope.get("error") or {}
        assert envelope["ok"] is True or error.get("code") == CHECK_FAILED, \
            f"gov check neither passed nor failed on a check: it was refused\n{run.describe()}"
        result = envelope["result"] if envelope["ok"] else error.get("details") or {}
        return envelope, result, run

    def refused(self, sandbox, interface, *args):
        """The error of a ``gov check`` that must be refused."""
        run = self.gov(sandbox, support.COMMAND, "--json", *args)
        envelope = cli_support.assert_envelope(run, interface, command=support.COMMAND)
        assert envelope["ok"] is False and run.returncode == support.EXIT_GOV_ERROR, \
            f"gov {' '.join(run.args)} was not refused with exit code {support.EXIT_GOV_ERROR}\n{run.describe()}"
        return envelope["error"]


@pytest.fixture()
def scratch(tmp_path):
    """``scratch(name, layouts, ...)`` builds one temporary project; a case may build several."""
    def _scratch(name, layouts=(), **keys):
        return Scratch(tmp_path / name, tuple(LAYOUTS[each] for each in layouts), **keys)
    return _scratch


def entry(result, check_id, run):
    """The one result entry of a check. A check that ran twice, or not at all, fails the case."""
    entries = [each for each in support.checks_of(result) if each.get("id") == check_id]
    assert len(entries) == 1, \
        f"gov check reports {len(entries)} results for {check_id!r}, expected one\n{run.describe()}"
    return entries[0]


def summary(result):
    """What a project is told, without the commit: each check with its findings, and each family's status and count."""
    checks = [(each.get("id"), each.get("family"), each.get("severity"), each.get("status"), each.get("findings"))
              for each in support.checks_of(result)]
    families = {name: (family.get("status"), family.get("check_count"), family.get("reason"))
                for name, family in support.families_of(result).items()}
    return checks, families


# --------------------------------------------------------------------------
# 1. A project with the installed layout only
# --------------------------------------------------------------------------

def test_an_installed_project_lists_its_declarations(scratch, sandbox, interface):
    """``gov check --list`` shows the declarations of ``governance/kernel/checks/``, each with its five fields."""
    project = scratch("installed", ("installed",))
    listed = project.listed(sandbox, interface)
    expected = [{field: yaml.safe_load((project.root / INSTALLED / "checks" / f"{check_id}.yaml").read_text())[field]
                 for field in support.CHECK_FIELDS} for check_id in sorted((SCHEMA_CHECK, SMALL))]
    assert listed == expected, f"an installed project's declarations are not listed as they are written: {listed}"


def test_an_installed_project_is_answered_as_the_same_kernel_in_the_template_layout(scratch, sandbox, interface):
    """The same declarations, schemas and records in either layout: the same checks, each once, the same
    statuses, findings and family counts. The record that breaks its schema makes the comparison one with a finding."""
    answers = {}
    for name in ("template", "installed"):
        project = scratch(name, (name,))
        project.write(TASK_REL, task_record(kpis=...))
        _, result, run = project.checked(sandbox, interface)
        for check_id in (SCHEMA_CHECK, SMALL):
            entry(result, check_id, run)
        answers[name] = summary(result)
    assert answers["installed"] == answers["template"], \
        f"the installed project is not answered as the template project is:\n{answers}"


@pytest.mark.parametrize("answer", ("green", "a word the small check reports"))
def test_the_declared_command_of_an_installed_check_is_started_and_its_result_reported(answer, scratch, sandbox,
                                                                                    interface):
    """The command names a file of the installed kernel; it is started in the project's root, where it reads
    a file of the project, and what it answers is the check's result."""
    project = scratch("installed", ("installed",), answer=answer)
    envelope, result, run = project.checked(sandbox, interface)
    small = entry(result, SMALL, run)
    if answer == "green":
        assert small["status"] == support.GREEN and not small["findings"], \
            f"the small check answered green and is not reported green\n{run.describe()}"
        assert support.family_status(result, SMALL_FAMILY) == support.GREEN, run.describe()
    else:
        assert [(found.get("code"), found.get("message")) for found in small["findings"]] == [(SMALL_FOUND, answer)], \
            f"the small check's finding is not reported as it gave it\n{run.describe()}"
        assert small["status"] == support.RED and support.family_status(result, SMALL_FAMILY) == support.RED, \
            f"a hard-block check with a finding is not red\n{run.describe()}"
        assert envelope["ok"] is False and run.returncode == support.EXIT_CHECK_FAILED, \
            f"a red hard-block check of the installed kernel does not fail gov check\n{run.describe()}"
    assert set(small.get("provenance") or {}) >= {"commit", "check_version", "inputs_hash"}, \
        f"the installed check's result carries no provenance\n{run.describe()}"


@pytest.mark.parametrize("skill", ("well-formed", "without frontmatter"))
def test_a_kernel_declaration_whose_command_names_template_paths_measures_the_installed_kernel(skill, scratch,
                                                                                            sandbox, interface):
    """The kernel's own declaration, copied as it is: its command names ``template/`` paths (DEC-521). In an
    installed project ``gov check`` starts it, and it measures the skill under ``governance/kernel/skills/``."""
    project = scratch("installed", ("installed",))
    project.write(f"{INSTALLED}/checks/{SKILL_CHECK}.yaml", kernel_file(f"checks/{SKILL_CHECK}.yaml"))
    if skill == "well-formed":
        skills.make_skill(project.root / INSTALLED / "skills", name=SKILL, version="1.0.0",
                          description="The orchestration skill", body=f"# {SKILL}\n\nUse `gov status` first.\n")
    else:
        skills.make_skill(project.root / INSTALLED / "skills", name=SKILL, raw=f"# {SKILL}\n\nNo frontmatter.\n")
    _, result, run = project.checked(sandbox, interface)
    found = entry(result, SKILL_CHECK, run)
    if skill == "well-formed":
        assert found["status"] == support.GREEN and not found["findings"], \
            f"{SKILL_CHECK} is not green on a well-formed installed skill\n{run.describe()}"
    else:
        rel = f"{INSTALLED}/skills/{SKILL}/SKILL.md"
        named = [each for each in found["findings"]
                 if each.get("code") == "SKILL_NO_FRONTMATTER" and rel in json.dumps(each)
                 and f"template/{rel}" not in json.dumps(each)]
        assert named and found["status"] == support.RED, \
            f"{SKILL_CHECK} has no SKILL_NO_FRONTMATTER finding that names {rel}\n{run.describe()}"


BROKEN = {
    "a ticket without its kpis": (TASK_REL, lambda: task_record(kpis=...), "kpis"),
    "a probe record with a judgement outside the four words":
        (PROBE_REL, lambda: probes.record_text(probes.probe(judgement="inconclusive")), "judgement"),
}


@pytest.mark.parametrize("what", sorted(BROKEN))
def test_in_an_installed_project_a_record_that_breaks_its_schema_is_a_finding(what, scratch):
    """The schema check, run as it is declared, reads the schemas under ``governance/kernel/schemas/``."""
    rel, text, field = BROKEN[what]
    project = scratch("installed", ("installed",))
    project.write(rel, text())
    found = probes.about(probes.run_schema_check(project.root), rel)
    named = probes.assert_names_field(found, field, f"an installed project, {what}")
    assert all(each.get("path") == rel for each in named), f"the finding does not carry the file as `path`: {named}"
    others = [each for each in found if each.get("field") != field]
    assert not others, f"an installed project, {what}: findings about something else: {others}"


def test_in_an_installed_project_records_that_keep_their_schemas_give_no_finding(scratch):
    project = scratch("installed", ("installed",))
    project.write(PROBE_REL, probes.record_text(probes.probe()))
    findings = probes.run_schema_check(project.root)
    assert not findings, f"well-formed records give findings where the kernel is installed: {findings}"


def test_gov_check_in_an_installed_project_is_red_on_a_record_that_breaks_its_schema(scratch, sandbox, interface):
    """End to end: the installed declaration is run, the installed schema is read, the family is red."""
    project = scratch("installed", ("installed",))
    project.write(TASK_REL, task_record(kpis=...))
    envelope, result, run = project.checked(sandbox, interface)
    found = entry(result, SCHEMA_CHECK, run)
    assert [(each.get("path"), each.get("field")) for each in found["findings"]] == [(TASK_REL, "kpis")], \
        f"{SCHEMA_CHECK} does not report the one broken record\n{run.describe()}"
    assert support.family_status(result, SCHEMA_FAMILY) == support.RED and envelope["ok"] is False \
        and run.returncode == support.EXIT_CHECK_FAILED, f"gov check is not red\n{run.describe()}"


def test_an_installed_kernel_without_a_record_s_schema_is_never_silent_about_it(scratch):
    """Holds what stays: a probe record whose schema the project does not hold is a finding, not a pass."""
    project = scratch("installed", ("installed",))
    project.remove(f"{INSTALLED}/schemas/probe.schema.json")
    project.write(PROBE_REL, probes.record_text(probes.probe()))
    found = probes.about(probes.run_schema_check(project.root), PROBE_REL)
    assert [each.get("code") for each in found] == ["SCHEMA_UNREADABLE"], \
        f"a probe record without its schema is not the one unmeasured finding: {found}"


# --------------------------------------------------------------------------
# 2. A project with neither layout: the answer of today
# --------------------------------------------------------------------------

def test_a_project_with_neither_layout_answers_as_today(scratch, sandbox, interface):
    project = scratch("neither")
    project.write(PROBE_REL, probes.record_text(probes.probe()))
    assert project.listed(sandbox, interface) == [], "a project without a kernel lists declared checks"
    envelope, result, run = project.checked(sandbox, interface)
    assert envelope["ok"] is True and run.returncode == support.EXIT_OK, \
        f"gov check does not pass in a project without a kernel\n{run.describe()}"
    assert [each.get("id") for each in support.checks_of(result)] == list(BUILT_IN), \
        f"a project without a kernel runs other checks than the three without a declaration\n{run.describe()}"
    families = support.families_of(result)
    assert sorted(families) == sorted(support.FAMILIES), f"not the 17 families\n{run.describe()}"
    counts = {name: family.get("check_count") for name, family in families.items()}
    expected = dict.fromkeys(support.FAMILIES, 0) | {"skill regression": 1, "product traceability": 2}
    assert counts == expected, f"the families' check counts are not today's: {counts}"
    unregistered = {name for name, family in families.items()
                    if (family.get("status"), family.get("reason")) == (support.YELLOW, "no registered check")}
    assert unregistered == {name for name, count in expected.items() if count == 0}, \
        f"the families without a check are not each yellow with that reason\n{run.describe()}"
    # the schema check, as it is declared: the shared fields are held, a type's own schema cannot be
    found = probes.run_schema_check(project.root)
    assert [(each.get("code"), each.get("path")) for each in found] == [("SCHEMA_UNREADABLE", PROBE_REL)], \
        f"the schema check in a project without a kernel does not answer as today: {found}"


# --------------------------------------------------------------------------
# 3. A project with both layouts
# --------------------------------------------------------------------------

def test_with_both_layouts_alike_every_check_runs_once_as_with_the_template_alone(scratch, sandbox, interface):
    """A declaration present in both layouts is one check; no finding is doubled and no count changes."""
    answers, lists = {}, {}
    for name, layouts in (("template", ("template",)), ("both", ("template", "installed"))):
        project = scratch(name, layouts, answer="a word the small check reports")
        project.write(TASK_REL, task_record(kpis=...))
        lists[name] = project.listed(sandbox, interface)
        _, result, run = project.checked(sandbox, interface)
        for check_id in (SCHEMA_CHECK, SMALL):
            entry(result, check_id, run)
        answers[name] = summary(result)
    assert lists["both"] == lists["template"], f"the list changed with the second layout: {lists}"
    assert answers["both"] == answers["template"], f"the answer changed with the second layout:\n{answers}"


def test_this_repository_s_own_list_holds_each_declaration_of_its_template_once(sandbox, interface):
    """This repository's figure: one listed check per declaration file of its template, in file-name order.
    The command reads only."""
    run = cli_support.run_gov_with_code(REPO_ROOT, REPO_ROOT, sandbox, support.COMMAND, "--list", "--json")
    envelope = cli_support.assert_envelope(run, interface, command=support.COMMAND)
    assert envelope["ok"] is True, run.describe()
    files = sorted((REPO_ROOT / TEMPLATE / "checks").glob("*.yaml"))
    expected = [yaml.safe_load(path.read_text(encoding="utf-8"))["id"] for path in files]
    assert [each["id"] for each in envelope["result"]["checks"]] == expected, \
        f"this repository's list is not its template's declarations, each once\n{run.describe()}"


@pytest.mark.parametrize("holder", sorted(LAYOUTS))
def test_with_both_layouts_a_declaration_in_one_layout_only_is_run(holder, scratch, sandbox, interface):
    """No declared check is dropped because the other layout does not hold it."""
    project = scratch("both", ("template", "installed"))
    project.write(f"{LAYOUTS[holder]}/checks/only-here.yaml",
                  declaration_text("only-here", f"python3 {LAYOUTS[holder]}/bin/small_check.py",
                                   family="mutation scope"))
    listed = [each["id"] for each in project.listed(sandbox, interface)]
    assert listed.count("only-here") == 1 and sorted(listed) == sorted((SCHEMA_CHECK, SMALL, "only-here")), \
        f"the declaration of the {holder} layout alone is not listed once beside the shared ones: {listed}"
    _, result, run = project.checked(sandbox, interface)
    assert entry(result, "only-here", run)["status"] == support.GREEN, run.describe()
    for check_id in (SCHEMA_CHECK, SMALL):
        entry(result, check_id, run)


DIFFERENCES = {
    "another command": {"command": "true"},
    "the not-applicable answer allowed": {"allows-not-applicable": "true"},
}


@pytest.mark.parametrize("what", sorted(DIFFERENCES))
@pytest.mark.parametrize("args", ((), ("--list",)), ids=("run", "list"))
def test_one_check_id_declared_differently_in_the_two_layouts_is_refused(args, what, scratch, sandbox, interface):
    """Which of the two a project means is not known: nothing is run, and both files are named."""
    project = scratch("both", ("template", "installed"), answer="a word the small check reports")
    command = f"python3 {TEMPLATE}/bin/small_check.py"
    project.write(f"{INSTALLED}/checks/{SMALL}.yaml", declaration_text(SMALL, **({"command": command} | DIFFERENCES[what])))
    error = project.refused(sandbox, interface, *args)
    assert error.get("code") == INVALID, f"the refusal's code is not {INVALID}: {error}"
    said = json.dumps(error)
    template_rel, installed_rel = (f"{kernel}/checks/{SMALL}.yaml" for kernel in (TEMPLATE, INSTALLED))
    assert template_rel in said, f"the refusal does not name {template_rel}: {error}"
    # the installed path is the end of the template path: it must stand on its own too
    assert installed_rel in said.replace(template_rel, ""), f"the refusal does not name {installed_rel}: {error}"
    assert SMALL_FOUND not in said, f"a check was started although the declarations were refused: {error}"


@pytest.mark.parametrize("stricter", sorted(LAYOUTS))
def test_with_both_layouts_a_record_is_held_to_the_schemas_of_both(stricter, scratch):
    """The two layouts hold a schema file that differs: a record that breaks either one is a finding."""
    project = scratch("both", ("template", "installed"))
    rel = f"{LAYOUTS[stricter]}/schemas/ticket.schema.json"
    schema = json.loads((project.root / rel).read_text(encoding="utf-8"))
    schema["required"] = list(schema["required"]) + ["review_note"]
    project.write(rel, json.dumps(schema, indent=2) + "\n")
    found = probes.about(probes.run_schema_check(project.root), TASK_REL)
    assert [(each.get("code"), each.get("field")) for each in found] == [("SCHEMA_MISSING_FIELD", "review_note")], \
        f"the field the {stricter} layout's schema alone asks for is not the one finding on the record: {found}"


# --------------------------------------------------------------------------
# 4. Failure stays failure
# --------------------------------------------------------------------------

NOT_VALID = {
    "a field is missing": "id: \"zz-bad\"\nfamily: \"graph integrity\"\n",
    "a severity outside the two": declaration_text("zz-bad", "true", severity="fatal"),
    "the top level is a list": "- id: zz-bad\n",
    "no YAML": "id: [zz-bad\n",
}


@pytest.mark.parametrize("what", sorted(NOT_VALID))
@pytest.mark.parametrize("args", ((), ("--list",)), ids=("run", "list"))
def test_a_declaration_that_is_not_valid_is_refused_under_the_installed_layout_as_under_the_template(
        args, what, scratch, sandbox, interface):
    """The same file in either layout: the same code, the same key, the same words; the file is named by the
    path it has in that project."""
    errors = {}
    for name in ("template", "installed"):
        project = scratch(name, (name,), answer="a word the small check reports")
        project.write(f"{LAYOUTS[name]}/checks/zz-bad.yaml", NOT_VALID[what])
        errors[name] = project.refused(sandbox, interface, *args)
    today, installed = errors["template"], errors["installed"]
    assert today.get("code") == INVALID, f"the template layout's refusal is not today's: {today}"
    assert installed.get("code") == INVALID, f"the installed layout's refusal has another code: {installed}"
    rel = f"{INSTALLED}/checks/zz-bad.yaml"
    assert (installed.get("details") or {}).get("file") == rel, \
        f"the refusal does not name the file by its path in the project ({rel}): {installed}"
    assert (installed.get("details") or {}).get("key") == today["details"].get("key"), \
        f"the refusal names another key than under the template layout: {installed} / {today}"
    assert installed.get("message") == today["message"].replace(f"{TEMPLATE}/checks/zz-bad.yaml", rel), \
        f"the refusal's words differ from the template layout's beyond the path: {installed} / {today}"
    assert SMALL_FOUND not in json.dumps(installed), \
        f"a check was started although a declaration was refused: {installed}"


def test_with_both_layouts_a_declaration_that_is_not_valid_in_the_installed_one_is_refused(scratch, sandbox,
                                                                                         interface):
    """A valid copy in the template layout does not excuse the installed file."""
    project = scratch("both", ("template", "installed"))
    project.write(f"{INSTALLED}/checks/{SMALL}.yaml", NOT_VALID["a field is missing"])
    error = project.refused(sandbox, interface)
    assert error.get("code") == INVALID and (error.get("details") or {}).get("file") == f"{INSTALLED}/checks/{SMALL}.yaml", \
        f"the installed file that is not valid is not refused by its own path: {error}"

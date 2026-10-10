"""Round of DEC-595: a check's declaration may state its own time limit (README, "Fourth batch").

DEC-595: "a check's declaration may state its own time limit". DEC-600: "A time limit in a declaration that is
not a positive whole number is refused as an invalid declaration (the stricter reading)."

The key is ``timeout-seconds``: a positive whole number of seconds, beside the declaration's other keys. A
declaration without it keeps the runner's limit of 60 seconds.

The cases run ``gov check --json``, ``gov check --list --json`` and ``gov ci job --json`` in temporary projects
built from scratch, each with declarations of its own and nothing else of a kernel. The code under test is this
worktree's ``src/``, given to ``gov`` by W1-07's launcher. No case waits for the default limit: a stated limit
is held with small values (two seconds against a command that sleeps twelve).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W1-07"))

import w1_07_support as cli_support  # noqa: E402
import w1_15_support as support  # noqa: E402

REPO_ROOT = support.REPO_ROOT
KEY = "timeout-seconds"
DEFAULT_S = 60
# The ceiling held for the secrets-indexing check's own limit: a quarter of the one time limit of a close this
# repository writes for itself (close_timeout: 7200, W1-30's README, settlement 21).
CEILING_S = 1800

TEMPLATE = "template/governance/kernel"
INSTALLED = "governance/kernel"
LAYOUTS = {"template": TEMPLATE, "installed": INSTALLED}
INVALID = "CHECK_DECLARATION_INVALID"
CHECK_FAILED = "CHECK_FAILED"
RED, GREEN = "RED", "GREEN"
EXIT_REFUSED, EXIT_CHECK_FAILED = 1, 3
FAMILY = "graph integrity"

LIMIT_S, SLEEPS_S = 2, 12
SLOW = f"exec sleep {SLEEPS_S}"   # exits 0 when it is let run to its end: only a time limit makes it red
OWN_FINDING = "OWN_FINDING"
ANSWERS_RED = "echo '[{\"code\": \"" + OWN_FINDING + "\", \"message\": \"its own answer\"}]'; exit 1"
WITNESS_REL = "started.txt"
WITNESS = f"touch {WITNESS_REL}"


def declaration(check_id, command, tier="G1", **raw):
    """A declaration file's text. ``raw`` is ``key -> the value as YAML writes it``; ``timeout_seconds`` is the key."""
    fields = {"id": check_id, "family": FAMILY, "tier": tier, "severity": "hard-block", "command": command}
    text = "".join(f"{key}: {json.dumps(value)}\n" for key, value in fields.items())
    return text + "".join(f"{key.replace('_', '-')}: {value}\n" for key, value in raw.items())


class Scratch:
    """A temporary git repository that holds declarations and nothing else of a kernel."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True)
        support.git(self.root, "init", "-q", "-b", "main")
        self.write("README.md", "# A project\n")
        self.write(".gitignore", ".gov-runtime/\n")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return rel

    def declare(self, layout, check_id, command, **keys):
        return self.write(f"{LAYOUTS[layout]}/checks/{check_id}.yaml", declaration(check_id, command, **keys))

    def gov(self, sandbox, *args):
        support.git(self.root, "add", "-A")
        support.git(self.root, "commit", "-q", "--allow-empty", "-m", "fixture")
        return cli_support.run_gov_with_code(REPO_ROOT, self.root, sandbox, *args)


@pytest.fixture(scope="session")
def interface():
    return cli_support.load_interface(REPO_ROOT)


@pytest.fixture()
def cli(tmp_path):
    return cli_support.make_sandbox(tmp_path / "cli-sandbox")


@pytest.fixture()
def scratch(tmp_path):
    def _scratch(name="project"):
        return Scratch(tmp_path / name)
    return _scratch


def checked(project, cli, interface):
    """``gov check --json``: the envelope, the check results, the run. A refusal of the command fails the case."""
    run = project.gov(cli, "check", "--json")
    envelope = cli_support.assert_envelope(run, interface, command="check")
    error = envelope.get("error") or {}
    assert envelope["ok"] is True or error.get("code") == CHECK_FAILED, \
        f"gov check neither passed nor failed on a check: it was refused\n{run.describe()}"
    result = envelope["result"] if envelope["ok"] else error.get("details") or {}
    return envelope, {each["id"]: each for each in result.get("checks", []) if isinstance(each, dict)}, run


def refused(project, cli, interface, *args):
    """The error of a command that must be refused as a command is for a declaration that is not valid."""
    run = project.gov(cli, *args)
    envelope = cli_support.assert_envelope(run, interface, command=args[0])
    assert envelope["ok"] is False and run.returncode == EXIT_REFUSED, \
        f"gov {' '.join(args)} was not refused with exit code {EXIT_REFUSED}\n{run.describe()}"
    return envelope["error"], run


def names_the_limit(findings, limit):
    """Whether what a check's findings say holds the limit as a number of seconds ("2 s", "2 seconds", "2.0 seconds")."""
    return re.search(rf"(?<![\d.]){limit}(\.0+)?\s*(s|secs?|seconds?)\b", json.dumps(findings)) is not None


def assert_invalid(error, rel, run):
    """Refused as a declaration with another key that is not valid is today: the code, the file, the key, the words."""
    assert error.get("code") == INVALID, f"the refusal's code is not {INVALID}\n{run.describe()}"
    details = error.get("details") or {}
    assert details.get("file") == rel, f"the refusal does not name the file by its path in the project ({rel})\n{run.describe()}"
    assert details.get("key") == KEY, f"the refusal does not name the key {KEY!r}\n{run.describe()}"
    assert str(error.get("message", "")).startswith(f"{rel}: key '{KEY}' must be "), \
        f"the refusal's words are not those of a key that is not valid (\"<file>: key '<key>' must be ...\")\n{run.describe()}"


# --------------------------------------------------------------------------
# 1. A stated limit is the check's limit
# --------------------------------------------------------------------------

@pytest.mark.parametrize("layout", sorted(LAYOUTS))
def test_a_check_over_its_stated_limit_is_red_and_its_finding_names_that_limit(layout, scratch, cli, interface):
    """Two seconds stated, a command that sleeps twelve and then exits 0: the check is red for the limit, and
    says which limit. The check beside it states none and is not held to its neighbour's two seconds."""
    project = scratch()
    project.declare(layout, "over-its-limit", SLOW, timeout_seconds=LIMIT_S)
    project.declare(layout, "states-no-limit", "sleep 3")
    envelope, checks, run = checked(project, cli, interface)
    slow, plain = checks.get("over-its-limit"), checks.get("states-no-limit")
    assert slow is not None and plain is not None, f"a declared check has no result\n{run.describe()}"
    assert slow["status"] == RED, \
        f"a check that states {LIMIT_S} s and runs {SLEEPS_S} s is {slow['status']}: the stated limit was not applied\n{run.describe()}"
    assert names_the_limit(slow["findings"], LIMIT_S), \
        f"the red check's findings do not name the limit of {LIMIT_S} seconds that applied\n{run.describe()}"
    assert not names_the_limit(slow["findings"], DEFAULT_S), \
        f"the red check's findings name the default limit, which did not apply\n{run.describe()}"
    assert plain["status"] == GREEN, \
        f"a check that states no limit and runs three seconds is {plain['status']}\n{run.describe()}"
    assert envelope["ok"] is False and run.returncode == EXIT_CHECK_FAILED, \
        f"a hard-block check over its time limit does not fail gov check\n{run.describe()}"


@pytest.mark.parametrize("layout", sorted(LAYOUTS))
def test_a_check_that_ends_inside_its_stated_limit_is_judged_by_its_own_answer(layout, scratch, cli, interface):
    """A stated limit changes nothing for a command that ends in time: exit 0 is green, a finding is that finding."""
    project = scratch()
    project.declare(layout, "ends-in-time", "true", timeout_seconds=30)
    project.declare(layout, "answers-red-in-time", ANSWERS_RED, timeout_seconds=30)
    envelope, checks, run = checked(project, cli, interface)
    assert checks["ends-in-time"]["status"] == GREEN and not checks["ends-in-time"]["findings"], \
        f"a short command under a stated limit is not green\n{run.describe()}"
    red = checks["answers-red-in-time"]
    assert red["status"] == RED and [each.get("code") for each in red["findings"]] == [OWN_FINDING], \
        f"a check that answers with a finding inside its limit is not reported with that finding alone\n{run.describe()}"
    assert not names_the_limit(red["findings"], 30), \
        f"a check that ended in time is reported as over its limit\n{run.describe()}"


def test_a_limit_stated_alike_in_both_layouts_is_the_limit_of_the_one_check(scratch, cli, interface):
    """A declaration present in both layouts is one check (DEC-579), with the limit both files state."""
    project = scratch()
    for layout in LAYOUTS:
        project.declare(layout, "over-its-limit", SLOW, timeout_seconds=LIMIT_S)
    run = project.gov(cli, "check", "--json")
    envelope = cli_support.assert_envelope(run, interface, command="check")
    results = [each for each in ((envelope.get("error") or {}).get("details") or envelope.get("result") or {})
               .get("checks", []) if each.get("id") == "over-its-limit"]
    assert len(results) == 1, f"the check declared alike in both layouts has {len(results)} results\n{run.describe()}"
    assert results[0]["status"] == RED and names_the_limit(results[0]["findings"], LIMIT_S), \
        f"the limit both layouts state was not applied to the one check\n{run.describe()}"


@pytest.mark.parametrize("args", (("check", "--json"), ("check", "--list", "--json")), ids=("run", "list"))
def test_a_limit_stated_differently_in_the_two_layouts_is_refused(args, scratch, cli, interface):
    """Which of the two limits a project means is not known: nothing is run, and the key is named (DEC-579)."""
    project = scratch()
    project.declare("template", "two-limits", WITNESS, timeout_seconds=5)
    project.declare("installed", "two-limits", WITNESS, timeout_seconds=7)
    error, run = refused(project, cli, interface, *args)
    assert error.get("code") == INVALID and (error.get("details") or {}).get("key") == KEY, \
        f"two limits for one check are not refused by the key {KEY!r}\n{run.describe()}"
    assert not (project.root / WITNESS_REL).exists(), f"the check was started although it was refused\n{run.describe()}"


# --------------------------------------------------------------------------
# 2. A value that is not a positive whole number is refused, not ignored
# --------------------------------------------------------------------------

NOT_A_LIMIT = {
    "zero": "0",
    "a negative number": "-5",
    "a fraction": "2.5",
    "a word": "soon",
    "a number written as a string": '"5"',
    "a truth value": "true",
    "nothing after the key": "",
}


@pytest.mark.parametrize("what", sorted(NOT_A_LIMIT))
def test_a_stated_limit_that_is_no_positive_whole_number_is_refused_as_an_invalid_declaration(what, scratch, cli,
                                                                                            interface):
    """Refused, not ignored (DEC-600): no check of the project is started, a valid one beside it included."""
    project = scratch()
    rel = project.declare("template", "zz-bad-limit", WITNESS, timeout_seconds=NOT_A_LIMIT[what])
    project.declare("template", "beside-it", WITNESS)
    error, run = refused(project, cli, interface, "check", "--json")
    assert_invalid(error, rel, run)
    assert not (project.root / WITNESS_REL).exists(), \
        f"a check was started although a declaration was refused\n{run.describe()}"


@pytest.mark.parametrize("what", ("zero", "a word"))
@pytest.mark.parametrize("layout, args", (("template", ("check", "--list", "--json")),
                                         ("installed", ("check", "--json")),
                                         ("installed", ("check", "--list", "--json"))),
                         ids=("template-list", "installed-run", "installed-list"))
def test_the_refusal_is_the_same_for_the_list_and_under_the_installed_layout(layout, args, what, scratch, cli,
                                                                           interface):
    project = scratch()
    rel = project.declare(layout, "zz-bad-limit", WITNESS, timeout_seconds=NOT_A_LIMIT[what])
    error, run = refused(project, cli, interface, *args)
    assert_invalid(error, rel, run)
    assert not (project.root / WITNESS_REL).exists(), \
        f"a check was started although a declaration was refused\n{run.describe()}"


def test_a_key_that_is_not_valid_is_refused_today_in_the_words_the_limit_s_refusal_is_held_to(scratch, cli, interface):
    """The premise of the two cases above: what "refused as an invalid declaration" means for another key today."""
    project = scratch()
    rel = project.write(f"{TEMPLATE}/checks/zz-bad.yaml",
                        declaration("zz-bad", WITNESS).replace('"hard-block"', '"fatal"'))
    error, run = refused(project, cli, interface, "check", "--json")
    assert error.get("code") == INVALID and error.get("details") == {"file": rel, "key": "severity"}, run.describe()
    assert error.get("message", "").startswith(f"{rel}: key 'severity' must be "), run.describe()
    assert not (project.root / WITNESS_REL).exists(), run.describe()


# --------------------------------------------------------------------------
# 3. gov ci job reads the limit through the same reader
# --------------------------------------------------------------------------

def test_gov_ci_job_holds_a_check_to_its_stated_limit(scratch, cli, interface):
    """The job runs the declared checks of G1 and G2: the one over its stated limit is red there too."""
    project = scratch()
    project.declare("template", "over-its-limit", SLOW, timeout_seconds=LIMIT_S)
    project.declare("template", "second-tier", "true", tier="G2")
    run = project.gov(cli, "ci", "job", "--json")
    envelope = cli_support.assert_envelope(run, interface, command="ci")
    statuses = ((envelope.get("error") or {}).get("details") or envelope.get("result") or {}).get("checks")
    assert isinstance(statuses, dict) and "over-its-limit" in statuses and "second-tier" in statuses, \
        f"gov ci job does not state the status of each declared check\n{run.describe()}"
    assert statuses["over-its-limit"] == RED, \
        f"gov ci job gives {statuses['over-its-limit']} to a check that states {LIMIT_S} s and runs {SLEEPS_S} s\n{run.describe()}"
    assert statuses["second-tier"] == GREEN, run.describe()
    assert envelope["ok"] is False, f"gov ci job passed with a hard-block check over its limit\n{run.describe()}"


def test_gov_ci_job_refuses_a_stated_limit_that_is_no_positive_whole_number(scratch, cli, interface):
    project = scratch()
    rel = project.declare("template", "zz-bad-limit", WITNESS, timeout_seconds=NOT_A_LIMIT["zero"])
    project.declare("template", "second-tier", WITNESS, tier="G2")
    error, run = refused(project, cli, interface, "ci", "job", "--json")
    assert_invalid(error, rel, run)
    assert not (project.root / WITNESS_REL).exists(), \
        f"gov ci job started a check although a declaration was refused\n{run.describe()}"


# --------------------------------------------------------------------------
# 4. The secrets-indexing check states its limit
# --------------------------------------------------------------------------

def test_the_secrets_indexing_declaration_states_a_limit_above_the_default_and_under_the_ceiling():
    """The value is the engineer's, from a measurement on a stand-in of this repository's store. Held: it is
    stated, a positive whole number, above the 60 seconds a declaration without it has, and no more than the
    ceiling."""
    files = sorted((REPO_ROOT / support.CHECKS_REL).glob(support.CHECK_GLOB))
    assert len(files) == 1, f"expected one secrets-indexing declaration, found {[path.name for path in files]}"
    document = yaml.safe_load(files[0].read_text(encoding="utf-8"))
    assert KEY in document, f"{support.CHECKS_REL}/{files[0].name} states no time limit (key {KEY!r})"
    limit = document[KEY]
    assert isinstance(limit, int) and not isinstance(limit, bool) and limit > 0, \
        f"the stated limit is not a positive whole number: {limit!r}"
    assert limit > DEFAULT_S, f"the stated limit ({limit} s) is not above the default of {DEFAULT_S} s"
    assert limit <= CEILING_S, f"the stated limit ({limit} s) is above the ceiling of {CEILING_S} s"

"""Support code for the W2-53 acceptance tests (DAEO-7rr2).

W2-53: the probe gate measures every later merge that holds a FULL ticket's probed commit against git's own merge
of its parents (DEC-750, DEC-754); the owner-accepted known-red list as a ratchet, an integration-side edit of the
ticket file, and the named load-sensitive quarantine (DEC-757 item 2).

How the tests run (README, "How they run"):

- **Through public interfaces only**: ``gov close <ticket> --json`` (API-0002 envelope), the project's path map,
  ticket files, probe records, the decision register, commit trailers, and the ratchet's one public function
  (README, "The ratchet's core"), called in its own process.
- **The code under test is this worktree's ``src/``** (DEC-732): this module reuses W2-01's support (imported by
  path, unchanged), which reuses W1-30's; their sandbox puts the ``src/`` beside this file's ``tests/`` first on
  every process's ``PYTHONPATH``. This module asserts that the three agree.
- **Every project is a temporary git repository built from scratch** (W2-01's ``Project``): single named files
  only, no folder of this repository, nothing of this repository's ``governance/project/``.
- **Deterministic, no network.** A test that fails "under load" is a stand-in that fails on its first run and
  passes on every later one; no real load, no timing.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_W2_01 = str(_HERE.parent / "W2-01")
if _W2_01 not in sys.path:
    sys.path.insert(0, _W2_01)

import w2_01_support as w201  # noqa: E402  (W2-01's support: the project, merges, probe records, run_close)

base = w201.base
cli_support = w201.cli_support

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
assert w201.SRC == SRC and base.SRC == SRC, "W2-01's and W1-30's support must run the same src/ as this suite"

EXIT_OK = w201.EXIT_OK
EXIT_CHECK_FAILED = w201.EXIT_CHECK_FAILED

OWNER = w201.OWNER
ORCHESTRATOR = w201.ORCHESTRATOR
IMPLEMENTER = w201.IMPLEMENTER
TEST_DESIGNER = w201.TEST_DESIGNER

PATH_MAP_REL = w201.PATH_MAP_REL
REGISTER = w201.REGISTER
CAPABILITY = w201.CAPABILITY

trailers_of = w201.trailers_of
git = w201.git
head_of = w201.head_of
merge_by_hand = w201.merge_by_hand
content_at = w201.content_at
create_ticket = w201.create_ticket
engineer_commit = w201.engineer_commit
checkpointed = w201.checkpointed
probe_recorded = w201.probe_recorded
run_close = w201.run_close
closed = w201.closed
refused = w201.refused
strings_of = w201.strings_of
text_of = w201.text_of
findings_of = w201.findings_of

# --------------------------------------------------------------------------
# The forms this suite fixes (README, "The forms this suite fixes")
# --------------------------------------------------------------------------

# The path map's keys and their entries' fields (DEC-757: fixed by the owner, never renamed).
ACCEPTED_REDS = "accepted_reds"
LOAD_SENSITIVE = "load_sensitive"
LIST_KEYS = (ACCEPTED_REDS, LOAD_SENSITIVE)

# What a close (and the ratchet's function) reports, and the codes of its findings.
RESULT_FAILED = "failed"          # a listed red that was red in this run (a failure or an error)
RESULT_NOT_RUN = "not run"        # a listed test this run did not run
ACCEPTED_RED_REFUSED = "ACCEPTED_RED_REFUSED"            # an entry of accepted_reds that does not count
ACCEPTED_RED_PASSES = "ACCEPTED_RED_PASSES"              # a listed red that passes: the entry is to be removed
RED_NOT_ACCEPTED = "RED_NOT_ACCEPTED"                    # the ratchet's function: a red the list does not cover
LOAD_SENSITIVE_REFUSED = "LOAD_SENSITIVE_REFUSED"        # an entry of load_sensitive that does not count
LOAD_SENSITIVE_FAILED_ALONE = "LOAD_SENSITIVE_FAILED_ALONE"  # a listed test that failed its isolated re-run
PASSED, FAILED = "passed", "failed"                      # the two results of a re-run report

# The ratchet's core: one public function (README, "The ratchet's core"; W2-19 reuses it, DEC-736).
RATCHET_MODULE = "gov.close.ratchet"
RATCHET_FUNCTION = "apply_accepted_reds"

# The register's statuses the cases write (W2-01's forms of an owner's acceptance, DEC-734).
OWNER_ACCEPTED = "ACCEPTED (owner, 2026-10-17)"
DELEGATED = "ACCEPTED (orchestrator, delegated under MR-6, 2026-10-17)"
PROPOSED = "PROPOSED"

# The owner's first entries (DEC-757), written as the owner will write them: a pytest node id, relative to the
# project's root.
W1_42_FILE = "tests/acceptance/W1-42/test_w1_42_exit_report.py"
RETR_FUNCTION = "test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason"
SHARE_FUNCTION = "test_governance_share_is_measured_and_at_most_15_percent_on_each_programme"
RETR_RED = f"{W1_42_FILE}::{RETR_FUNCTION}[RETR-X-02]"
RETR_GREEN = f"{W1_42_FILE}::{RETR_FUNCTION}[RETR-X-01]"
SHARE_RED = f"{W1_42_FILE}::{SHARE_FUNCTION}"

W1_05_FILE = "tests/acceptance/W1-05/test_w1_05_live_hooks.py"
HOOK_FUNCTION = "test_a_call_waits_under_100_ms_p95_for_the_hook"
HOOK_TEST = f"{W1_05_FILE}::{HOOK_FUNCTION}"
W1_02_FILE = "tests/acceptance/W1-02/test_w1_02_guard_hook.py"
DECISION_FUNCTION = "test_decision_p95_is_under_100_ms"
DECISION_TEST = f"{W1_02_FILE}::{DECISION_FUNCTION}"


def name_of(test_id):
    """The test's own name in a node id: what follows the last ``::`` (with its parameter set)."""
    return test_id.rsplit("::", 1)[-1]


def file_of(test_id):
    return test_id.split("::", 1)[0]


def owner_text_naming(*test_ids):
    """A decision's text that names each test as the owner's entry will (DEC-757): its own name, with its
    parameter where it has one, and its file."""
    files = sorted({file_of(test_id) for test_id in test_ids})
    names = " and ".join(f"`{name_of(test_id)}`" for test_id in test_ids)
    return f"the path map lists {names}, in {' and '.join(f'`{rel}`' for rel in files)}, as owner-accepted."


# --------------------------------------------------------------------------
# The project and its path map's lists
# --------------------------------------------------------------------------

def _list_text(key, entries):
    if not entries:
        return f"{key}: []\n"
    text = f"{key}:\n"
    for entry in entries:
        text += "".join(f"  {'-' if n == 0 else ' '} {field}: {json.dumps(str(value))}\n"
                        for n, (field, value) in enumerate(entry.items()))
    return text


def path_map_text(settings):
    """W2-01's path map text, and the two lists of DEC-757 written as YAML lists of mappings."""
    plain = {key: value for key, value in settings.items() if key not in LIST_KEYS}
    text = w201.path_map_text(plain)
    for key in LIST_KEYS:
        if key in settings:
            text += _list_text(key, settings[key])
    return text


def project_at(root):
    """A temporary project (W2-01's): a register, the path map naming it, no base, no lists yet."""
    return w201.Project(root)


def commit_with_message(project, message, who):
    """One commit of everything waiting, whose message is ``message`` exactly (its own trailer block, if any)."""
    return project._commit(message, who, ())


def add_entries(project, key, entries, role="owner", message=None):
    """The path map's list ``key`` gains ``entries`` (dicts of DEC-757's fields), in one commit whose final trailer
    block is ``Task: setup`` and ``Role: <role>``. ``message`` replaces the whole message (a case that puts a
    trailer elsewhere than in the final block). Returns the commit."""
    project.settings[key] = list(project.settings.get(key) or []) + list(entries)
    project.write(PATH_MAP_REL, path_map_text(project.settings))
    who = OWNER if role == "owner" else ORCHESTRATOR
    text = message or f"the path map's {key}\n\nTask: setup\nRole: {role}\n"
    return commit_with_message(project, text, who)


def red_entry(test_id, decision, fixed_by="W2-13", reason="a known red the owner accepted"):
    return {"test": test_id, "decision": decision, "reason": reason, "fixed_by": fixed_by}


def quarantine_entry(test_id, decision, reason="a p95 latency case that fails only under parallel load"):
    return {"test": test_id, "decision": decision, "reason": reason}


def create_ticket_named(project, ticket, wbs, allowed_paths, test_name, profile="STANDARD"):
    """As W2-01's ``create_ticket``, its one passing acceptance test named ``test_name``: two tickets' folders in
    one test run must not both hold ``test_pass.py`` (pytest refuses two test modules of one basename)."""
    project.add_ticket(ticket, wbs, profile=profile, allowed_paths=list(allowed_paths))
    project.add_passing_test(wbs, name=test_name)
    created = project._commit(f"ticket {ticket} created", ORCHESTRATOR, trailers_of(ticket, role="orchestrator"),
                              [base.ticket_path(ticket)])
    project.commit("acceptance tests", who=TEST_DESIGNER,
                   trailers=trailers_of(ticket, role="independent-test-designer"), exact=True)
    return created


def setup_commit(project, message="setup"):
    """What the working tree holds, committed by the owner outside any ticket."""
    return project.commit(message, who=OWNER, trailers=("Task: setup", "Role: owner"), exact=True)


def final_roles(project, commit):
    """The ``Role:`` values of a commit's final trailer block, as git reads it."""
    out = git(project, "log", "-1", "--format=%(trailers:key=Role,valueonly,separator=%x1e)", commit)
    return [value.strip() for value in out.strip().split("\x1e") if value.strip()]


# --------------------------------------------------------------------------
# Test files of the projects
# --------------------------------------------------------------------------

def w1_42_file(red=("RETR-X-02",), share_red=True, params=("RETR-X-01", "RETR-X-02")):
    """A stand-in of W1-42's exit report file: one parameterised test (the parameter sets in ``red`` fail) and
    one plain test (failing when ``share_red``)."""
    return (
        "import pytest\n\n\n"
        f"@pytest.mark.parametrize('query', {list(params)!r})\n"
        f"def {RETR_FUNCTION}(query):\n"
        f"    assert query not in {list(red)!r}, 'a known red'\n\n\n"
        f"def {SHARE_FUNCTION}():\n"
        f"    assert {not share_red!r}, 'a known red'\n"
    )


# The body of a stand-in for a case that fails only under load: it fails on its first run and passes on every
# later one. ``earlier`` is the number of times it ran before.
FAILS_UNDER_LOAD = "assert earlier > 0, 'slower than 100 ms at p95 under parallel load'"
FAILS_ALONE_TOO = "assert False, 'slower than 100 ms at p95, alone too'"


def telling_file(told, functions):
    """A test file whose tests tell, at every run, into ``told/<their node name>``, one JSON line each: their
    process and the number of tests the process's session holds. ``functions`` maps a function's name to
    ``(body, parameter sets or None)``."""
    text = (
        "import json\nimport os\n\nimport pytest\n\n"
        f"TOLD = {str(told)!r}\n\n\n"
        "def _told(request):\n"
        "    path = os.path.join(TOLD, request.node.name)\n"
        "    earlier = 0\n"
        "    if os.path.exists(path):\n"
        "        with open(path, encoding='utf-8') as handle:\n"
        "            earlier = len(handle.read().splitlines())\n"
        "    with open(path, 'a', encoding='utf-8') as handle:\n"
        "        handle.write(json.dumps({'pid': os.getpid(), 'items': len(request.session.items)}) + '\\n')\n"
        "    return earlier\n"
    )
    for name, (body, params) in functions.items():
        decorator = f"@pytest.mark.parametrize('case', {list(params)!r})\n" if params else ""
        arguments = "request, case" if params else "request"
        text += f"\n\n{decorator}def {name}({arguments}):\n    earlier = _told(request)\n    {body}\n"
    return text


def told_runs(told, node_name):
    """The runs a telling test told: ``[{"pid": …, "items": …}, …]``, oldest first; ``[]`` when it never ran."""
    path = Path(told) / node_name
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def re_run_alone(runs):
    """Whether a telling test ran twice: once in the close's run and once more alone, in a process of its own
    whose session held that one test."""
    return (len(runs) == 2 and runs[1]["items"] == 1 and runs[1]["pid"] != runs[0]["pid"])


# --------------------------------------------------------------------------
# Reading answers
# --------------------------------------------------------------------------

def listed_under(value, key):
    """Every object of a list held under ``key`` at any depth of ``value``."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            for name, item in node.items():
                if name == key and isinstance(item, list):
                    found.extend(entry for entry in item if isinstance(entry, dict))
                walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)
    return found


def red_reports(value):
    """The reports of listed reds in an answer (README: ``accepted_reds``, each with ``result``)."""
    return [entry for entry in listed_under(value, ACCEPTED_REDS) if "result" in entry]


def rerun_reports(value):
    """The reports of re-runs in an answer (README: ``load_sensitive``, each with ``in_run`` and ``alone``)."""
    return [entry for entry in listed_under(value, LOAD_SENSITIVE) if "in_run" in entry and "alone" in entry]


def findings_coded(error, code):
    return [finding for finding in findings_of(error) if finding.get("code") == code]


def naming(findings, *words):
    """The findings whose text holds every one of ``words`` (case is not held)."""
    return [finding for finding in findings
            if all(word.lower() in text_of(finding).lower() for word in words)]


def probe_statements(error):
    """The statements of a refusal that are the probe gate's (they say "probe")."""
    return [text for text in strings_of(error) if "probe" in text.lower()]


def probe_gate_names(error, commit):
    """Whether one of the probe gate's statements names ``commit`` (by its first 7 characters)."""
    return any(commit[:7] in text for text in probe_statements(error))


def holds(project, commit, other):
    """Whether ``other`` holds ``commit`` (``commit`` is ``other`` or one of its ancestors)."""
    return commit in git(project, "rev-list", other).split()


def parents_of(project, merge):
    return git(project, "rev-list", "--parents", "-n", "1", merge).split()[1:]


def _merge_tree(project, first, second):
    env = {"PATH": "/usr/bin:/bin", "HOME": str(Path(project.root).parent), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
    return subprocess.run(["git", "-C", str(project.root), "merge-tree", "--write-tree", first, second],
                          capture_output=True, text=True, env=env)


def own_merge_content(project, first, second, rel):
    """The text of ``rel`` in the tree git's own merge of two commits gives (``git merge-tree --write-tree``):
    ``None`` when that tree has no such file; the case fails when git finds a conflict. A fixture check only."""
    done = _merge_tree(project, first, second)
    assert done.returncode == 0, f"the fixture is wrong: git's own merge conflicts\n{done.stdout}{done.stderr}"
    return content_at(project, done.stdout.split()[0], rel)


def own_merge_unreadable(project, first, second):
    """Whether git fails to compute its own merge of two commits for a reason other than a conflict (git's
    ``merge-tree`` ends with 0 for a clean merge, 1 for a conflict, another code when it cannot work)."""
    return _merge_tree(project, first, second).returncode not in (0, 1)


def octopus(project, heads, trailers, edit=None, remove=(), message="merge", who=ORCHESTRATOR):
    """An octopus merge of ``heads`` into the branch checked out, carrying ``trailers``, with ``edit`` written and
    ``remove`` removed in the merge itself. Returns the merge."""
    text = message + "\n\n" + "\n".join(trailers) + ("\n" if trailers else "")
    done = git(project, "merge", "-q", "--no-ff", "--no-commit", "--no-gpg-sign", *heads, who=who, check=False)
    for rel, content in (edit or {}).items():
        project.write(rel, content)
    for rel in remove:
        git(project, "rm", "-q", "-f", "--", rel, who=who)
    git(project, "add", "-A", who=who)
    assert not git(project, "diff", "--name-only", "--diff-filter=U").strip(), f"the fixture left a conflict\n{done}"
    git(project, "commit", "-q", "--no-gpg-sign", "-m", text, who=who)
    merge = head_of(project)
    assert len(parents_of(project, merge)) == len(heads) + 1, "the fixture is wrong: not an octopus merge"
    return merge


def merge_resolving(project, head, trailers, resolved, message="merge", who=ORCHESTRATOR):
    """A merge of ``head`` whose parents conflict, resolved by writing ``resolved`` (``{path: text}``). Returns the
    merge; the case fails when git found no conflict."""
    text = message + "\n\n" + "\n".join(trailers) + "\n"
    git(project, "merge", "-q", "--no-ff", "--no-commit", "--no-gpg-sign", head, who=who, check=False)
    conflicted = git(project, "diff", "--name-only", "--diff-filter=U").split()
    assert conflicted, "the fixture is wrong: the merge has no conflict"
    for rel, content in resolved.items():
        project.write(rel, content)
    git(project, "add", "-A", who=who)
    git(project, "commit", "-q", "--no-gpg-sign", "-m", text, who=who)
    return head_of(project)


def run_ratchet(project, sandbox, results):
    """The ratchet's function on the project, in its own process on this worktree's ``src/``: the verdict it
    returns, as JSON. ``results`` maps a test id to ``passed``, ``failed``, ``error`` or ``skipped``."""
    script = (
        "import json, sys\n"
        f"from {RATCHET_MODULE} import {RATCHET_FUNCTION}\n"
        f"print(json.dumps({RATCHET_FUNCTION}(sys.argv[1], json.loads(sys.argv[2]))))\n"
    )
    done = subprocess.run([sys.executable, "-c", script, str(project.root), json.dumps(results)],
                          cwd=str(project.root), env=base.sandbox_env(sandbox), capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=120)
    assert done.returncode == 0, \
        f"{RATCHET_MODULE}.{RATCHET_FUNCTION} did not answer:\n{done.stdout}\n{done.stderr}"
    verdict = json.loads(done.stdout.strip().splitlines()[-1])
    assert isinstance(verdict, dict), f"the verdict is not an object: {verdict!r}"
    return verdict

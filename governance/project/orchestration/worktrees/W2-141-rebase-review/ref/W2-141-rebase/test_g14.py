"""G-14 (DEC-1052, DAEO-sdxk): the planted cases of role separation from the path map's role_paths: section.

Drives the candidate hook as Claude Code runs it (event JSON on stdin, the pinned judge's interpreter with -E) in
fixture repositories made under the run's tmp folder: each with a path map (the section as in the patch, the (b)/(c2)
section, none, a malformed one) and a ticket DAEO-g14t (W2-G14T). The engineer's tree ~/gov-os-worktrees/W2-G14T is
named only (never made, never read). Each role, each tool form: a true read refused, a near miss let through; the
absent section: no check. The own-tree rule (a designer in the engineer's tree) is checked in-process.
The hook under test: G14_HOOK, else pretooluse.py beside this file.
Run: python3 -m pytest -q -p no:cacheprovider test_g14.py
"""
import json
import os
import subprocess
import sys
import time

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.environ.get("G14_HOOK") or os.path.join(HERE, "pretooluse.py")
PY = os.environ.get("GOV_PIN_PY") or open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
ENG = os.path.realpath(os.path.expanduser("~/gov-os-worktrees")) + "/W2-G14T"
E, TD, O, A = "engineer", "independent-test-designer", "orchestrator", "independent-auditor"

PATCHED = """role_paths:
  engineer:
    reads_denied: ["{ticket_tests}"]
  independent-test-designer:
    reads_denied: ["{ticket_impl}"]
"""
NARROW = """role_paths:
  engineer:
    reads_denied: ["{ticket_tests}"]
  independent-test-designer:
    reads_denied: ["{ticket_impl_code}"]
"""
MALFORMED = """role_paths:
  engineer: ["tests/acceptance/**"]
"""
# Review F2: a merge's conflict markers elsewhere in the map leave the role_paths: block readable on its own.
CONFLICTED = PATCHED + """<<<<<<< HEAD
decision_register: docs/DECISION_REGISTER.md
=======
decision_register: docs/OTHER.md
>>>>>>> w2/other
"""
CONFLICT_IN_BLOCK = """<<<<<<< HEAD
role_paths:
  engineer:
    reads_denied: ["tests/acceptance/**"]
=======
role_paths:
  engineer:
    reads_denied: ["{ticket_tests}"]
>>>>>>> w2/other
"""
OTHER_TICKET = """---
id: DAEO-g14u
status: closed
wbs_id: W2-G14U
role: engineer
allowed_paths:
- src/gov/g14u.py
---
"""
THIRD_TICKET = OTHER_TICKET.replace("g14u", "g14w").replace("G14U", "G14W")
# ACT-G14b: a coordination ticket (as W2-00): no acceptance tests of its own; work under it revises others' tests
COORD_TICKET = """---
id: DAEO-g14c
status: in_progress
wbs_id: W2-G14C
class: coordination
role: orchestrator
allowed_paths: []
---
"""
TICKET = """---
id: DAEO-g14t
status: in_progress
wbs_id: W2-G14T
role: engineer
allowed_paths:
- src/gov/g14/impl.py
- template/g14/*.yaml
- tests/unit/test_g14t*
- tests/unit/g14t_support.py
- tests/unit/__init__.py
- tests/conftest.py
- tests/unit/g14/conftest.py
- docs/changes/W2-G14T-evidence.md
---
# G-14 fixture ticket
"""


def _repo(path, section):
    os.makedirs(path + "/governance/project", exist_ok=True)
    os.makedirs(path + "/.tickets", exist_ok=True)
    os.makedirs(path + "/tests/acceptance/W2-G14T", exist_ok=True)
    os.makedirs(path + "/src/gov/g14", exist_ok=True)
    with open(path + "/governance/project/path-map.yaml", "w") as f:
        f.write("state_class: AUTHORITATIVE\nnamespaces: {}\n" + section)
    with open(path + "/.tickets/DAEO-g14t.md", "w") as f:
        f.write(TICKET)
    with open(path + "/.tickets/DAEO-g14u.md", "w") as f:
        f.write(OTHER_TICKET)
    with open(path + "/.tickets/DAEO-g14w.md", "w") as f:
        f.write(THIRD_TICKET)
    with open(path + "/.tickets/DAEO-g14c.md", "w") as f:
        f.write(COORD_TICKET)
    os.makedirs(path + "/tests/acceptance/W2-G14C", exist_ok=True)
    os.makedirs(path + "/tests/acceptance/W2-G14U", exist_ok=True)
    for rel in ("tests/acceptance/W2-G14T/test_a.py", "src/gov/g14/impl.py", "tests/acceptance/W2-G14U/test_u.py",
                "tests/acceptance/W2-G14U/test_v.py", "tests/acceptance/W2-G14U/test_w.py",
                "tests/acceptance/W2-G14U/test_c.py", "tests/acceptance/W2-G14C/test_own.py"):
        with open(os.path.join(path, rel), "w") as f:
            f.write("x = 1\n")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_NAME="g14", GIT_AUTHOR_EMAIL="g14@x", GIT_COMMITTER_NAME="g14",
               GIT_COMMITTER_EMAIL="g14@x")

    def git(*args):
        subprocess.run(["git", "-C", path, *args], check=True, env=env, capture_output=True)
    subprocess.run(["git", "init", "-q", "-b", "w2/integrate", path], check=True, env=env)
    # The owner's engineer rule's link sources (W2-54's cases revised for W2-126 are the pattern):
    # the base, W2-G14U's own cases;
    git("add", "-A", "--", ".", ":!tests/acceptance/W2-G14U/test_u.py", ":!tests/acceptance/W2-G14U/test_v.py",
        ":!tests/acceptance/W2-G14U/test_c.py")
    git("commit", "-q", "-m", "base", "--trailer", "Task: DAEO-sdxk", "--trailer", "Role: orchestrator")
    # (i) a W2-G14U case revised for W2-G14T, its Task: naming W2-G14T's ticket (W2-126's of W2-123, 741f9edd);
    git("add", "tests/acceptance/W2-G14U/test_u.py")
    git("commit", "-q", "-m", "W2-G14T: W2-G14U's case revised", "--trailer", "Task: DAEO-g14t",
        "--trailer", "Role: independent-test-designer", "--trailer", "Rewrite-Reason: W2-G14T KPI 1")
    # (ii) one revised in W2-G14T's tests branch under W2-G14U's own Task: (W2-126's of W2-54, 0922aa76);
    git("checkout", "-q", "-b", "w2/W2-G14T-tests")
    git("add", "tests/acceptance/W2-G14U/test_v.py")
    git("commit", "-q", "-m", "W2-G14U: a case revised to W2-G14T's cache", "--trailer", "Task: DAEO-g14u",
        "--trailer", "Role: independent-test-designer")
    git("checkout", "-q", "w2/integrate")
    git("merge", "-q", "--no-ff", "--no-edit", "w2/W2-G14T-tests")  # the project's merges are --no-ff
    # ACT-G14b: a test designer's revision committed under the coordination ticket (D-4's cut under DAEO-sdxk)
    git("add", "tests/acceptance/W2-G14U/test_c.py")
    git("commit", "-q", "-m", "D-4: W2-G14U's case cut", "--trailer", "Task: DAEO-g14c",
        "--trailer", "Role: independent-test-designer")
    return path


@pytest.fixture(scope="session")
def trees(tmp_path_factory):
    base = str(tmp_path_factory.mktemp("g14"))
    return {"patched": _repo(base + "/patched", PATCHED), "narrow": _repo(base + "/narrow", NARROW),
            "absent": _repo(base + "/absent", ""), "malformed": _repo(base + "/malformed", MALFORMED),
            "conflicted": _repo(base + "/conflicted", CONFLICTED),
            "conflict_in_block": _repo(base + "/conflict_in_block", CONFLICT_IN_BLOCK)}


def run(root, role, tool, tin, agent=None, cwd=None, ticket="DAEO-g14t"):
    event = {"tool_name": tool, "tool_input": tin, "cwd": cwd or root, "hook_event_name": "PreToolUse"}
    if agent:
        event["agent_type"] = agent
    env = dict(os.environ, GOV_ROLE=role, GOV_TICKET=ticket, CLAUDE_PROJECT_DIR=root)
    env.pop("PYTHONPATH", None)
    p = subprocess.run([PY, "-E", HOOK], input=json.dumps(event), capture_output=True, text=True, env=env, timeout=60)
    if p.returncode == 2:
        return "deny", p.stderr
    assert p.returncode == 0, p.stderr
    if not p.stdout.strip():
        return "allow", ""
    out = json.loads(p.stdout)["hookSpecificOutput"]
    return out["permissionDecision"], out["permissionDecisionReason"]


def b(cmd):
    return {"command": cmd}


R = "<root>"  # the fixture tree's path, filled in per case
T = "tests/acceptance/W2-G14T/test_a.py"

# (name, role, agent_type, tool, input) in the patched tree: engineer {ticket_tests}, designer {ticket_impl}
ENGINEER_REFUSED = [
    ("Read own test", E, None, "Read", {"file_path": R + "/" + T}),
    ("Read in the engineer's tree", E, None, "Read", {"file_path": ENG + "/" + T}),
    ("Read a case revised for it (Task:)", E, None, "Read", {"file_path": R + "/tests/acceptance/W2-G14U/test_u.py"}),
    ("cat a case revised in its tests branch", E, None, "Bash", b("cat tests/acceptance/W2-G14U/test_v.py")),
    ("a revised case in another tree", E, None, "Read",
     {"file_path": ENG + "-tests/tests/acceptance/W2-G14U/test_u.py"}),
    ("NotebookRead", E, None, "NotebookRead", {"notebook_path": R + "/tests/acceptance/W2-G14T/n.ipynb"}),
    ("Grep in the tests", E, None, "Grep", {"pattern": "x", "path": R + "/tests/acceptance/W2-G14T"}),
    ("Grep glob pins the tests", E, None, "Grep", {"pattern": "x", "path": R, "glob": "tests/acceptance/W2-G14T/*.py"}),
    ("cat", E, None, "Bash", b("cat " + T)),
    ("head -n", E, None, "Bash", b("head -n 5 " + T)),
    ("sed -n", E, None, "Bash", b("sed -n 1,9p " + T)),
    ("awk", E, None, "Bash", b("awk 'NR<5' " + T)),
    ("grep pattern path", E, None, "Bash", b("grep -n foo " + T)),
    ("rg -e", E, None, "Bash", b("rg -e foo tests/acceptance/W2-G14T")),
    ("jq", E, None, "Bash", b("jq . tests/acceptance/W2-G14T/fixtures/x.json")),
    ("cd then relative", E, None, "Bash", b("cd tests/acceptance && cat W2-G14T/test_a.py")),
    ("own variable", E, None, "Bash", b("D=tests/acceptance/W2-G14T; cat $D/test_a.py")),
    ("glob word", E, None, "Bash", b("cat tests/acceptance/W2-G14T/*.py")),
    ("input redirect", E, None, "Bash", b("python3 x.py < " + T)),
    ("cp source", E, None, "Bash", b("cp " + T + " /tmp/x")),
    ("find -exec cat", E, None, "Bash", b("find tests/acceptance/W2-G14T -name '*.py' -exec cat {} \\;")),
    ("git show HEAD:", E, None, "Bash", b("git show HEAD:" + T)),
    ("git show the designer's branch", E, None, "Bash", b("git show w2/W2-G14T-tests:" + T)),
    ("git diff --", E, None, "Bash", b("git diff -- " + T)),
    ("git log -p --", E, None, "Bash", b("git log -p -- tests/acceptance/W2-G14T")),
    ("git show of a revised case", E, None, "Bash", b("git show HEAD:tests/acceptance/W2-G14U/test_v.py")),
    ("bash -c", E, None, "Bash", b("bash -c 'cat " + T + "'")),
    ("substitution", E, None, "Bash", b('echo "$(cat ' + T + ')"')),
    ("acting engineer (a lead's subagent)", O, E, "Read", {"file_path": R + "/" + T}),
]
ENGINEER_PASSED = [
    ("grep's pattern names the tests", E, None, "Bash", b('grep -rn "tests/acceptance/W2-G14T" src/')),
    ("another ticket's test (regressions)", E, None, "Read", {"file_path": R + "/tests/acceptance/W1-01/test_x.py"}),
    ("another ticket's case not revised for it", E, None, "Read",
     {"file_path": R + "/tests/acceptance/W2-G14U/test_w.py"}),
    ("a search of the whole acceptance folder (from above)", E, None, "Bash", b("grep -rn x tests/acceptance")),
    ("ls lists names", E, None, "Bash", b("ls tests/acceptance/W2-G14T")),
    ("Glob lists names", E, None, "Glob", {"pattern": "tests/acceptance/**", "path": R}),
    ("pytest runs them", E, None, "Bash", b("pytest -q tests/acceptance/W2-G14T")),
    ("git log --stat", E, None, "Bash", b("git log --stat -- tests/acceptance")),
    ("git diff --name-only", E, None, "Bash", b("git diff --name-only -- tests/acceptance")),
    ("wc counts", E, None, "Bash", b("wc -l " + T)),
    ("echo names", E, None, "Bash", b("echo " + T)),
    ("unresolved variable", E, None, "Bash", b("cat $G14_UNSET/" + T)),
    ("names at run time", E, None, "Bash", b("ls tests/acceptance | xargs cat")),
    ("a name that starts the same", E, None, "Bash", b("cat tests/acceptance_notes.md")),
    ("a folder that starts the same", E, None, "Read", {"file_path": R + "/tests/acceptance-old/x.py"}),
    ("Grep from above", E, None, "Grep", {"pattern": "x", "path": R}),
    ("grep -r from above", E, None, "Bash", b("grep -r foo tests/")),
    ("heredoc data", E, None, "Bash", b("cat > /tmp/gov-os-emg-g14/h.txt <<'EOF'\ncat " + T + "\nEOF")),
    ("inline code is not guessed at", E, None, "Bash", b("python3 -c \"print(open('" + T + "').read())\"")),
    ("own code", E, None, "Read", {"file_path": R + "/src/gov/g14/impl.py"}),
    ("a scratch folder named like the tests", E, None, "Read", {"file_path": "/tmp/tests/acceptance/x.py"}),
    ("an engineer's edit", E, None, "Bash", b("sed -i 's/a/b/' src/gov/g14/impl.py")),
]
DESIGNER_REFUSED = [
    ("Read the engineer's code", TD, None, "Read", {"file_path": ENG + "/src/gov/g14/impl.py"}),
    ("cat the engineer's code", TD, None, "Bash", b("cat " + ENG + "/src/gov/g14/impl.py")),
    ("the engineer's glob path", TD, None, "Bash", b("sed -n 1,5p " + ENG + "/template/g14/a.yaml")),
    ("Grep the engineer's file", TD, None, "Grep", {"pattern": "x", "path": ENG + "/src/gov/g14/impl.py"}),
    ("git show the branch", TD, None, "Bash", b("git show w2/W2-G14T:src/gov/g14/impl.py")),
    ("git diff the branch --", TD, None, "Bash", b("git diff w2/integrate w2/W2-G14T -- src/gov/g14/impl.py")),
    ("acting designer", O, TD, "Read", {"file_path": ENG + "/src/gov/g14/impl.py"}),
    ("the engineer's docs ((c3) as decided)", TD, None, "Read", {"file_path": ENG + "/docs/changes/W2-G14T-evidence.md"}),
    ("the engineer's new unit tests ((c3))", TD, None, "Read", {"file_path": ENG + "/tests/unit/test_g14t_x.py"}),
    ("the engineer's unit tests by Bash ((c3))", TD, None, "Bash", b("grep -n def " + ENG + "/tests/unit/test_g14t_x.py")),
    ("the engineer's unit tests on its branch ((c3))", TD, None, "Bash",
     b("git show w2/W2-G14T:tests/unit/test_g14t_x.py")),
]
DESIGNER_PASSED = [
    ("its own tree's code (integrated)", TD, None, "Read", {"file_path": R + "/src/gov/g14/impl.py"}),
    ("the integrated version", TD, None, "Bash", b("git show w2/integrate:src/gov/g14/impl.py")),
    ("a file outside the ticket", TD, None, "Read", {"file_path": ENG + "/src/gov/g14/other.py"}),
    ("the shared conftest ((c3))", TD, None, "Read", {"file_path": ENG + "/tests/conftest.py"}),
    ("a nested conftest ((c3))", TD, None, "Bash", b("cat " + ENG + "/tests/unit/g14/conftest.py")),
    ("a support module ((c3))", TD, None, "Read", {"file_path": ENG + "/tests/unit/g14t_support.py"}),
    ("a package marker ((c3))", TD, None, "Read", {"file_path": ENG + "/tests/unit/__init__.py"}),
    ("its own acceptance tests", TD, None, "Read", {"file_path": R + "/" + T}),
    ("Grep from above", TD, None, "Grep", {"pattern": "x", "path": ENG}),
    ("the whole branch's diff", TD, None, "Bash", b("git diff w2/integrate...w2/W2-G14T")),
    ("Glob lists names", TD, None, "Glob", {"pattern": "src/**", "path": ENG}),
]
OTHERS_PASSED = [
    ("orchestrator reads the tests", O, None, "Read", {"file_path": R + "/" + T}),
    ("orchestrator reads the engineer's code", O, None, "Read", {"file_path": ENG + "/src/gov/g14/impl.py"}),
    ("auditor reads the tests", A, None, "Bash", b("cat " + T)),
    ("designer's own acceptance tests by Bash", TD, None, "Bash", b("sed -n 1,9p " + T)),
]


def _fill(tin, root):
    return {k: (v.replace(R, root) if isinstance(v, str) else v) for k, v in tin.items()}


@pytest.mark.parametrize("name,role,agent,tool,tin", ENGINEER_REFUSED + DESIGNER_REFUSED,
                         ids=[c[0] for c in ENGINEER_REFUSED + DESIGNER_REFUSED])
def test_true_reads_are_refused(trees, name, role, agent, tool, tin):
    root = trees["patched"]
    want = "engineer" if (agent or role) == E else TD
    got, why = run(root, role, tool, _fill(tin, root), agent)
    assert got == "deny", (name, why)
    assert f"role_paths.{want}.reads_denied" in why and "DEC-1052 G-14" in why and ENG not in why


@pytest.mark.parametrize("name,role,agent,tool,tin", ENGINEER_PASSED + DESIGNER_PASSED + OTHERS_PASSED,
                         ids=[c[0] for c in ENGINEER_PASSED + DESIGNER_PASSED + OTHERS_PASSED])
def test_near_misses_pass(trees, name, role, agent, tool, tin):
    root = trees["patched"]
    got, why = run(root, role, tool, _fill(tin, root), agent)
    assert got == "allow", (name, why)


@pytest.mark.parametrize("name,role,agent,tool,tin", ENGINEER_REFUSED + DESIGNER_REFUSED,
                         ids=[c[0] for c in ENGINEER_REFUSED + DESIGNER_REFUSED])
def test_absent_section_is_no_check(trees, name, role, agent, tool, tin):
    root = trees["absent"]
    got, why = run(root, role, tool, _fill(tin, root), agent)
    assert got == "allow", (name, why)


NARROW_CASES = [  # (name, role, tool, input, want) under engineer {ticket_tests} (variant (b)), designer {ticket_impl_code}
    ("own ticket's test", E, "Read", {"file_path": R + "/" + T}, "deny"),
    ("own ticket's test by Bash", E, "Bash", b("grep -n x " + T), "deny"),
    ("own ticket's test on the designer's branch", E, "Bash", b("git show w2/W2-G14T-tests:" + T), "deny"),
    ("another ticket's test", E, "Read", {"file_path": R + "/tests/acceptance/W1-01/test_x.py"}, "allow"),
    ("the tests' shared file", E, "Bash", b("cat tests/acceptance/serial-only.txt"), "allow"),
    ("the engineer's unit tests", TD, "Read", {"file_path": ENG + "/tests/unit/test_g14t_x.py"}, "deny"),
    ("the shared conftest", TD, "Bash", b("cat " + ENG + "/tests/conftest.py"), "allow"),
    ("the engineer's code", TD, "Read", {"file_path": ENG + "/src/gov/g14/impl.py"}, "deny"),
    ("its own tree's conftest", TD, "Read", {"file_path": R + "/tests/conftest.py"}, "allow"),
    ("the engineer's docs under {ticket_impl_code}", TD, "Read",
     {"file_path": ENG + "/docs/changes/W2-G14T-evidence.md"}, "allow"),
]


@pytest.mark.parametrize("name,role,tool,tin,want", NARROW_CASES, ids=[c[0] for c in NARROW_CASES])
def test_the_narrow_section(trees, name, role, tool, tin, want):
    root = trees["narrow"]
    got, why = run(root, role, tool, _fill(tin, root))
    assert got == want, (name, why)


def test_a_malformed_section_fails_closed(trees):
    root = trees["malformed"]
    got, why = run(root, E, "Read", {"file_path": root + "/src/gov/g14/impl.py"})
    assert got == "deny" and "role_paths" in why
    # fail closed for every session's Read, Grep and Bash (as a malformed evaluation_sets, DEC-218): the ACT's check
    # step reads the section before the hook is copied into place
    got, why = run(root, O, "Bash", b("true"))
    assert got == "deny" and "role_paths" in why
    assert run(root, O, "Write", {"file_path": root + "/src/gov/g14/impl.py", "content": "x"})[0] == "allow"


LINKED_CASES = [  # (name, ticket, file, want): the revised cases, by whose engineer reads them
    ("W2-G14T's engineer, the case revised for it by Task:", "DAEO-g14t", "tests/acceptance/W2-G14U/test_u.py", "deny"),
    ("W2-G14T's engineer, the case revised in its tests branch", "DAEO-g14t", "tests/acceptance/W2-G14U/test_v.py",
     "deny"),
    ("W2-G14T's engineer, W2-G14U's unrevised case", "DAEO-g14t", "tests/acceptance/W2-G14U/test_w.py", "allow"),
    # the owner's rule: W2-G14U's own folder is W2-G14U's own tests, refused to its own engineer however revised
    ("W2-G14U's engineer, its own folder", "DAEO-g14u", "tests/acceptance/W2-G14U/test_u.py", "deny"),
    ("W2-G14U's engineer, W2-G14T's own test", "DAEO-g14u", T, "allow"),
    ("a third ticket's engineer, the revised case", "DAEO-g14w", "tests/acceptance/W2-G14U/test_u.py", "allow"),
    ("a third ticket's engineer, the other revised case", "DAEO-g14w", "tests/acceptance/W2-G14U/test_v.py", "allow"),
    # ACT-G14b: a coordination ticket's Task: links are ignored; its own folder only; other tickets' links kept
    ("the coordination ticket's engineer, a case cut under its Task:", "DAEO-g14c",
     "tests/acceptance/W2-G14U/test_c.py", "allow"),
    ("the coordination ticket's engineer, a case revised for W2-G14T", "DAEO-g14c",
     "tests/acceptance/W2-G14U/test_u.py", "allow"),
    ("the coordination ticket's engineer, its own folder", "DAEO-g14c", "tests/acceptance/W2-G14C/test_own.py", "deny"),
    ("W2-G14T's engineer, its links kept beside a coordination ticket's", "DAEO-g14t",
     "tests/acceptance/W2-G14U/test_u.py", "deny"),
    ("W2-G14T's engineer, the case cut under the coordination ticket", "DAEO-g14t",
     "tests/acceptance/W2-G14U/test_c.py", "allow"),
]


@pytest.mark.parametrize("name,ticket,rel,want", LINKED_CASES, ids=[c[0] for c in LINKED_CASES])
def test_the_revised_cases_go_with_the_ticket_they_test(trees, name, ticket, rel, want):
    root = trees["patched"]
    got, why = run(root, E, "Read", {"file_path": root + "/" + rel}, ticket=ticket)
    assert got == want, (name, why)
    if want == "deny":
        assert "role_paths.engineer.reads_denied" in why and "could not be worked out" not in why, why


UNREADABLE = """
import sys
sys.path.insert(0, sys.argv[1])
import role_reads as rr
d = rr.expand(["{ticket_tests}"], "W2-G14T", [], "/x", main="/x", names={"DAEO-g14t"},
              links=lambda m, n, w: None)
j = rr.Judge("engineer", d, ["/x"])
own = j.hit("/x/tests/acceptance/W2-G14T/test_a.py")
assert own and "could not be worked out from git" in j.reason(own), j.reason(own) if own else None
assert not j.hit("/x/tests/acceptance/W2-G14U/test_u.py")  # the fallback: its own folder only
print("OK")
"""


def test_an_unreadable_link_source_falls_back_to_the_own_folder_and_says_so(tmp_path):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    p = subprocess.run([PY, "-E", "-c", UNREADABLE, HERE], capture_output=True, text=True, timeout=60, env=env,
                       cwd=str(tmp_path))
    assert p.stdout.strip() == "OK", p.stderr


W2_126_LINKS = """
import sys, os, tempfile
os.environ["TMPDIR"] = sys.argv[2]  # pytest's own tmp_path
sys.path.insert(0, sys.argv[1])
import role_reads as rr
M = "/home/usain/Dynamic-Agentic-Engineering-OS"
w126 = rr.linked_tests(M, {"DAEO-jpr0", "W2-126"}, "W2-126")
w91 = rr.linked_tests(M, {"DAEO-a3u2", "W2-91"}, "W2-91")
print("tests/acceptance/W2-54/test_w2_54_query_cache.py" in w126, "tests/acceptance/W2-123/test_w2_123_retry.py" in w126,
      "tests/acceptance/W2-54/test_w2_54_query_cache.py" in w91, sorted(w91))
"""


W2_00_TODAY = """
import sys, os
os.environ["TMPDIR"] = sys.argv[2]
sys.path.insert(0, sys.argv[1])
import role_reads as rr
M = "/home/usain/Dynamic-Agentic-Engineering-OS"
sec = {"engineer": {"reads_denied": ["{ticket_tests}"]}}
j = rr.judges(sec, ["engineer"], M, "DAEO-sdxk", [M], M)[0]
print([bool(j.hit(M + "/" + r)) for r in ("tests/acceptance/W2-54/test_w2_54_query_cache.py",
                                          "tests/acceptance/W2-64/README.md", "tests/acceptance/W2-00/x.py")])
"""


def test_the_coordination_ticket_w2_00_reads_every_other_tickets_tests_today(tmp_path):
    """ACT-G14b (2026-11-03): D-4's cut tied 109 acceptance files to W2-00 through Task: DAEO-sdxk; W2-00 is
    class: coordination, so its engineers are refused only its own folder (which does not exist)."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    p = subprocess.run([PY, "-E", "-c", W2_00_TODAY, HERE, str(tmp_path)], capture_output=True, text=True, timeout=60,
                       env=env)
    assert p.stdout.strip() == "[False, False, True]", (p.stdout, p.stderr)


@pytest.mark.skipif(subprocess.run(["git", "-C", "/home/usain/Dynamic-Agentic-Engineering-OS", "rev-parse", "--verify",
                                    "--quiet", "w2/W2-126-tests"], capture_output=True).returncode != 0,
                    reason="w2/W2-126-tests is gone")
def test_w2_54s_cases_revised_for_w2_126_today(tmp_path):
    """The real pattern (2026-11-03): W2-54's query-cache case, revised in W2-126's tests branch under W2-54's own
    Task: (0922aa76, 816e86dd), and W2-123's retry case (Task: DAEO-jpr0, 741f9edd) go with W2-126; W2-91's engineer
    gets neither (its one link is W2-86's case, a31d314e)."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    p = subprocess.run([PY, "-E", "-c", W2_126_LINKS, HERE, str(tmp_path)], capture_output=True, text=True, timeout=60,
                       env=env)
    assert p.stdout.strip() == "True True False ['tests/acceptance/W2-86/test_w2_86_kernel_template_embedding.py']", \
        (p.stdout, p.stderr)


STALE_CACHE = """
import sys, os, json, glob, tempfile
tmp = sys.argv[3]  # pytest's own tmp_path: it exists whatever the run's TMPDIR (a fresh one may not, yet)
os.environ["TMPDIR"] = tmp
tempfile.tempdir = None
sys.path.insert(0, sys.argv[1])
import role_reads as rr
main = sys.argv[2]
first = rr.linked_tests(main, {"DAEO-g14t", "W2-G14T"}, "W2-G14T")
assert first == {"tests/acceptance/W2-G14U/test_u.py", "tests/acceptance/W2-G14U/test_v.py"}, first
(cached,) = glob.glob(rr.LINK_CACHE + "/*.json")
data = json.load(open(cached))
rr._LINKS.clear()
rr._METHOD[:] = ["an-older-method"]  # a list an older rule wrote, for the same heads
open(cached, "w").write(json.dumps({"key": data["key"], "files": []}))  # a wrong list under today's key is read...
assert rr.linked_tests(main, {"DAEO-g14t", "W2-G14T"}, "W2-G14T") == first  # ...only by today's method
rr._LINKS.clear(); rr._METHOD.clear()
print("OK")
"""


def test_a_list_cached_by_an_older_method_is_never_read(trees, tmp_path):
    """The rehearsal of 2026-11-03: a list cached by the reflog-based rule (empty after ACT-D8) was read again by the
    fixed rule for the same heads. The cache's key now holds the module's own hash and the repository."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    p = subprocess.run([PY, "-E", "-c", STALE_CACHE, HERE, trees["patched"], str(tmp_path)], capture_output=True, text=True,
                       timeout=60, env=env)
    assert p.stdout.strip() == "OK", (p.stdout, p.stderr)


def test_a_yaml_error_elsewhere_in_the_map_leaves_the_block_working(trees):
    """Review F2: only the role_paths: block is parsed; a conflict marker elsewhere refuses nothing more."""
    root = trees["conflicted"]
    got, why = run(root, E, "Read", {"file_path": root + "/" + T})
    assert got == "deny" and "role_paths.engineer.reads_denied" in why, why
    assert run(root, E, "Read", {"file_path": root + "/src/gov/g14/impl.py"})[0] == "allow"
    assert run(root, O, "Bash", b("git merge --abort"))[0] == "allow"


def test_a_conflict_inside_the_block_fails_closed(trees):
    root = trees["conflict_in_block"]
    got, why = run(root, O, "Bash", b("true"))
    assert got == "deny" and "role_paths" in why, why


def test_the_five_rules_hold_beside_it(trees):
    root = trees["patched"]
    assert run(root, E, "Write", {"file_path": root + "/" + T, "content": "x"})[0] == "deny"  # rule 1
    assert run(root, TD, "Write", {"file_path": root + "/" + T, "content": "x"})[0] == "allow"
    assert run(root, E, "Read", {"file_path": root + "/.env"})[0] == "deny"  # rule 3
    assert run(root, A, "Write", {"file_path": root + "/src/gov/g14/impl.py", "content": "x"})[0] == "deny"  # 5
    assert run(root, E, "Bash", b("sudo true"))[0] == "deny"  # rule 4
    assert run(root, E, "Bash", b("rm -rf " + root))[0] == "deny"  # the catastrophic delete


def test_it_is_quick(trees):
    """The check's cost on the guard's path: a Bash read and a Read, with the section and without."""
    times = {}
    for kind in ("patched", "absent"):
        root = trees[kind]
        t0 = time.monotonic()
        for _ in range(5):
            run(root, E, "Bash", b("grep -n x src/gov/g14/impl.py && cat README.md"))
            run(root, TD, "Read", {"file_path": ENG + "/src/gov/g14/other.py"})
        times[kind] = (time.monotonic() - t0) / 10
    sys.stderr.write(f"\nG-14 per call: {times}\n")
    assert times["patched"] < 1.0


# -- a designer in the engineer's own tree (the files its branch changes); the readers' words ---------------------

OWN_TREE = """
import sys
sys.path.insert(0, sys.argv[1])
import role_reads as rr
TD, ENG = "independent-test-designer", sys.argv[2]
allowed = ["src/gov/g14/impl.py", "src/gov/g14/two.py", "tests/unit/test_g14t*", "tests/conftest.py"]
j = rr.Judge(TD, rr.expand(["{ticket_impl}"], "W2-G14T", allowed, ENG, changes=lambda own: {"src/gov/g14/impl.py"}), [])
assert j.hit(ENG + "/src/gov/g14/impl.py")  # the engineer's new code
assert not j.hit(ENG + "/src/gov/g14/two.py")  # the ticket's path, unchanged: integrated code
c = rr.Judge(TD, rr.expand(["{ticket_impl}"], "W2-G14T", allowed, ENG,
                           changes=lambda own: {"tests/unit/test_g14t_a.py", "tests/conftest.py"}), [])
assert c.hit(ENG + "/tests/unit/test_g14t_a.py")  # a new unit test, changed: refused
assert not c.hit(ENG + "/tests/conftest.py")  # shared, changed or not: readable ((c3))
for mode, want in (("c1", False), ("c2", True), ("c3", False)):
    m = rr.Judge(TD, rr.expand(["{ticket_impl}"], "W2-G14T", allowed, None, mode=mode), [])
    assert bool(m.hit(ENG + "/tests/conftest.py")) == want, mode
assert rr.Judge(TD, rr.expand(["{ticket_impl}"], "W2-G14T", ["docs/changes/x.md"]), []).hit(ENG + "/docs/changes/x.md")
assert not rr.Judge(TD, rr.expand(["{ticket_impl_code}"], "W2-G14T", ["docs/changes/x.md"]), []).hit(ENG + "/docs/changes/x.md")
assert not j.hit(ENG + "/src/gov/g14/impl.py", plain=True)  # another revision's version (w2/integrate:)
unknown = rr.Judge(TD, rr.expand(["{ticket_impl}"], "W2-G14T", allowed, ENG, changes=lambda own: None), [])
assert not unknown.hit(ENG + "/src/gov/g14/impl.py")  # git cannot say: let through
other = rr.Judge(TD, rr.expand(["{ticket_impl}"], "W2-G14T", allowed, ENG + "-tests", changes=lambda own: set()), [])
assert other.hit(ENG + "/src/gov/g14/two.py")  # from the designer's own tree: every ticket path there
print("OK")
"""


TESTS_TREE = """
import sys
sys.path.insert(0, sys.argv[1])
import role_reads as rr
TD, ENG = "independent-test-designer", sys.argv[2]
allowed = ["src/gov/g14/impl.py", "src/gov/g14/two.py", "tests/unit/test_g14t*", "tests/conftest.py",
           "tests/acceptance/W2-G14T/test_a.py", "docs/changes/W2-G14T-evidence.md"]
carried = {"src/gov/g14/impl.py", "tests/unit/test_g14t_a.py", "tests/conftest.py", "docs/changes/W2-G14T-evidence.md",
           "tests/acceptance/W2-G14T/test_a.py"}
j = rr.Judge(TD, rr.expand(["{ticket_impl}"], "W2-G14T", allowed, ENG + "-tests", changes=lambda own: set(),
                           tests_changes=lambda tree, wbs: carried), [])
T = ENG + "-tests/"
assert j.hit(T + "src/gov/g14/impl.py")  # the engineer's code, carried into the tests tree by the fork
assert j.hit(T + "tests/unit/test_g14t_a.py")  # its new unit test, the same
assert j.hit(T + "docs/changes/W2-G14T-evidence.md")  # its document ((c3) as decided)
assert not j.hit(T + "src/gov/g14/two.py")  # a ticket path the engineer's commits did not carry: integrated
assert not j.hit(T + "tests/conftest.py")  # shared: readable
assert not j.hit(T + "tests/acceptance/W2-G14T/test_a.py")  # the designer's own acceptance tests: never refused
assert j.hit(ENG + "/src/gov/g14/two.py")  # the engineer's tree itself: every ticket path, as before
none = rr.Judge(TD, rr.expand(["{ticket_impl}"], "W2-G14T", allowed, ENG + "-tests",
                              tests_changes=lambda tree, wbs: None), [])
assert not none.hit(T + "src/gov/g14/impl.py")  # git cannot say: let through
print("OK")
"""

W291 = os.path.realpath(os.path.expanduser("~/gov-os-worktrees/W2-91-tests"))
W291_TODAY = """
import sys, subprocess, os
sys.path.insert(0, sys.argv[1])
import role_reads as rr
W = sys.argv[2]
sec = {"independent-test-designer": {"reads_denied": ["{ticket_impl}"]}}
js = rr.judges(sec, ["independent-test-designer"], W, "DAEO-a3u2", [W])
names = subprocess.run(["git", "-C", W, "ls-files"], capture_output=True, text=True).stdout.split()
print(sorted(n for n in names if js[0].hit(os.path.join(W, n))))
print(any(js[0].hit(os.path.join(W, n)) for n in names if n.startswith("tests/acceptance/")))
"""


def test_the_designers_tests_tree_names_the_engineers_carried_files():
    """Review F1: the tests tree is forked from the ticket's head; the engineer's files it carries are refused."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    p = subprocess.run([PY, "-E", "-c", TESTS_TREE, HERE, ENG], capture_output=True, text=True, timeout=60, env=env)
    assert p.stdout.strip() == "OK", p.stderr


@pytest.mark.skipif(not os.path.isdir(W291) or subprocess.run(
    ["git", "-C", "/home/usain/Dynamic-Agentic-Engineering-OS", "merge-base", "--is-ancestor", "w2/W2-91", "w2/integrate"],
    capture_output=True).returncode == 0, reason="W2-91-tests is gone, or W2-91 is merged (its code is integrated now)")
def test_w2_91_tests_today():
    """Review F1's tree, today (2026-11-03): its fork carried engineer commit b652fc96. Only names are read (git
    ls-files); the files refused are exactly the map, the unit test and the evidence doc; no acceptance file."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    p = subprocess.run([PY, "-E", "-c", W291_TODAY, HERE, W291], capture_output=True, text=True, timeout=60, env=env)
    lines = p.stdout.strip().splitlines()
    assert lines == [str(["docs/changes/W2-91-evidence.md", "governance/project/path-map.yaml",
                          "tests/unit/retrieval/test_w2_91_full_embeddings.py"]), "False"], (p.stdout, p.stderr)


def test_own_tree_names_only_the_changed_files():
    """A designer in the engineer's own tree: only the files its branch changes are the engineer's new code."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    p = subprocess.run([PY, "-E", "-c", OWN_TREE, HERE, ENG], capture_output=True, text=True, timeout=60, env=env)
    assert p.stdout.strip() == "OK", p.stderr


def _rr():
    sys.path.insert(0, HERE)
    import role_reads
    return role_reads


def test_reader_words():
    rr = _rr()
    ra = rr.Bash.reader_args
    assert ra("grep", ["-rn", "pat", "a", "b"]) == ["a", "b"]
    assert ra("grep", ["-e", "pat", "a"]) == ["a"]
    assert ra("grep", ["-f", "pats.txt", "a"]) == ["a", "pats.txt"]
    assert ra("sed", ["-n", "1,5p", "f"]) == ["f"]
    assert ra("awk", ["-F", ":", "{print}", "f"]) == ["f"]
    assert ra("head", ["-n", "5", "f"]) == ["f"]
    assert ra("cp", ["-r", "a", "b", "dest"]) == ["a", "b"]
    assert ra("cp", ["-t", "dest", "a"]) == ["a"]
    assert ra("jq", ["--arg", "k", "v", ".", "f.json"]) == ["f.json"]
    assert ra("cat", ["--", "-odd"]) == ["-odd"]

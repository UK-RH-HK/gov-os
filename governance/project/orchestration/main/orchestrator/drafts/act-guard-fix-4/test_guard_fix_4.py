"""ACT-GUARD-FIX-4: rules 1 and 5 stop guessing at shell commands (G-1, G-2); rm free but for the catastrophic (O-7
wider); the owner's DEC-1050 (8) and (12).

Drives the hook as Claude Code runs it (event JSON on stdin, the pinned judge's interpreter with -E) over:
- ACT-GUARD-FIX-3's planted cases (guard4_check.py's 54, its 179, the 19 corpus patterns, the 3 known gaps), with
  ACT-GUARD-FIX-3's wants, except the cases listed in LET_THROUGH: refused by ACT-GUARD-FIX-3 only because a write
  the guard cannot work out was guessed at from the words the command holds; they pass now, by design;
- writes that resolve into the acceptance tests or outside a reviewer's records: still refused;
- the catastrophic deletes (refused, every role) and the honest ones (passed);
- when the rebuilt corpus is here (GUARD_FIX4_CORPUS, else work/corpus4.json), every logged refusal
  (guard-refusals.jsonl, 87 rows), replayed from its transcript's full command; and (GUARD_FIX4_TODAY, else
  work/today4.json) the two rule-5 false refusals of 2026-11-03 (a reviewer's own record into the CTO's reviews/);
- rule 5's records in the CTO's .gov-runtime/scratch/orchestrator/reviews/ (allowed; the folder deleted or moved,
  or any other folder: refused);
- ACT-GUARD-FIX-3's module tests, re-run on this hook's bash_writes.py (its reading is unchanged), and the module's
  new parts (what rm deletes; the emptied word).

The hook under test: GUARD_FIX4_HOOK, else pretooluse.py beside this file, else the repository's own. ACT-GUARD-FIX-3's
test file: GUARD_FIX3_TESTS, else beside this file, else the orchestrator's tools folder, else its draft folder.
Run: python3 -m pytest -q -p no:cacheprovider test_guard_fix_4.py
"""
import importlib.util
import json
import os
import re
import subprocess
import sys

import pytest

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.environ.get("GUARD_FIX4_HOOK") or (
    os.path.join(HERE, "pretooluse.py") if os.path.exists(os.path.join(HERE, "pretooluse.py"))
    else ROOT + "/.claude/hooks/pretooluse.py")
PY = os.environ.get("GOV_PIN_PY") or open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
CORPUS = os.environ.get("GUARD_FIX4_CORPUS") or os.path.join(HERE, "work", "corpus4.json")
HOME = os.path.realpath(os.path.expanduser("~"))
WT = HOME + "/gov-os-worktrees"
E, A, O, TD = "engineer", "independent-auditor", "orchestrator", "independent-test-designer"
REV = ROOT + "/.gov-runtime/scratch/orchestrator/reviews"
TODAY = os.environ.get("GUARD_FIX4_TODAY") or os.path.join(HERE, "work", "today4.json")


def _fix3():
    """ACT-GUARD-FIX-3's test module, its hook pointed at the hook under test (its module tests then read this
    hook's bash_writes.py)."""
    os.environ["GUARD_FIX3_HOOK"] = HOOK
    for path in (os.environ.get("GUARD_FIX3_TESTS"), os.path.join(HERE, "test_guard_fix_3.py"),
                 ROOT + "/.gov-runtime/scratch/orchestrator/tools/test_guard_fix_3.py",
                 ROOT + "/.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-3/test_guard_fix_3.py"):
        if path and os.path.exists(path):
            spec = importlib.util.spec_from_file_location("test_guard_fix_3_cases", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise RuntimeError("ACT-GUARD-FIX-3's test file is not found")


FIX3 = _fix3()

# ACT-GUARD-FIX-3's module tests, on this hook's bash_writes.py: collected here as they are.
test_heredoc_bodies_are_cut_and_marked = FIX3.test_heredoc_bodies_are_cut_and_marked
test_unreadable_falls_back = FIX3.test_unreadable_falls_back
test_variables_resolve_only_when_safe = FIX3.test_variables_resolve_only_when_safe
test_python_writes_reads_are_not_writes = FIX3.test_python_writes_reads_are_not_writes
test_reads_view_cuts_data_bodies_only = FIX3.test_reads_view_cuts_data_bodies_only
test_no_case_is_judged_by_a_crash = FIX3.test_no_case_is_judged_by_a_crash
test_variables_expand_in_source_order_whatever_the_hash_seed = \
    FIX3.test_variables_expand_in_source_order_whatever_the_hash_seed
test_line_continuations_are_joined = FIX3.test_line_continuations_are_joined
test_code_names_the_tests_in_any_spelling = FIX3.test_code_names_the_tests_in_any_spelling
test_python_reads_sys_argv_from_the_command = FIX3.test_python_reads_sys_argv_from_the_command
test_the_words_that_may_run_a_script = FIX3.test_the_words_that_may_run_a_script
test_known_gaps_stay_as_today = FIX3.test_known_gaps_stay_as_today


def b(cmd):
    return {"command": cmd}


def _hook(role, tool, tin, cwd=ROOT, root=ROOT, agent=None, tmpdir=None):
    """The hook's decision, run as Claude Code runs it: event JSON on stdin, the pinned judge's interpreter, -E."""
    role, _, ticket = role.partition("@")
    event = {"tool_name": tool, "tool_input": tin, "cwd": cwd, "session_id": "guard-fix-4", "agent_type": agent}
    env = dict(os.environ, GOV_ROLE=role, GOV_TICKET=ticket or "DAEO-sdxk", CLAUDE_PROJECT_DIR=root)
    env.pop("TMPDIR", None)
    env.pop("PYTHONPATH", None)
    if tmpdir:
        env["TMPDIR"] = tmpdir
    p = subprocess.run([PY, "-E", HOOK], input=json.dumps(event), capture_output=True, text=True, env=env, timeout=90)
    if p.returncode == 2:
        return "deny", p.stderr
    if p.stdout.strip():
        out = json.loads(p.stdout)["hookSpecificOutput"]
        return out["permissionDecision"], out["permissionDecisionReason"]
    return "allow", ""


# --- ACT-GUARD-FIX-3's planted cases, re-baselined -----------------------------------------------------------------
# Each was refused by ACT-GUARD-FIX-3 only for a write whose target the guard cannot work out, in a command (or code)
# whose words name the tests (rule 1), or for a reviewer's unresolvable write (rule 5). G-1 and G-2 (DEC-1050 (12)):
# such a write is let through; the landing's Role: check (G-1) and the reviewed tree's git status (G-2) catch it.
LET_THROUGH = {
    # rule 5: a reviewer's write the guard cannot place (G-2)
    'guard4: rule5 auditor unreadable bash',
    "row 39 (left refused): an auditor's rm of an unmatched glob, which the product's parser cannot place",
    # rule 1: code the guard does not read (perl, node, exec, getattr, unknown functions) naming the tests (G-1)
    'guard4: fix2 engineer perl -i on acceptance',
    'fix3 perl heredoc naming acceptance',
    'fix3 node -e naming acceptance (as before)',
    'r2 F4 perl -e naming the folder with no slash',
    'fix3 python -c exec',
    "fix3 python -c getattr(os, 'remove')",
    'fix3 python -c unknown function handed a test',
    'fix3 python -c io.FileIO handed a test',
    'fix3 python -c unknown function handed a list of tests',
    # rule 1: a command the scan cannot read for certain, whose text names the tests (G-1)
    'guard4: fix2 unbalanced quotes naming acceptance',
    'fix3 unterminated heredoc naming acceptance judged as before',
    'r2 F3 a continued write in a command the scan cannot read (as before, on both spellings)',
    'row 46 (left refused): an unquoted Python heredoc the shell rewrites, in a command naming the tests',
    'fix3 unquoted shell heredoc',
    # rule 1: Python names the guard does not follow (loops, functions, globals, the environment) (G-1)
    'fix3 python heredoc rebinding by a loop',
    'fix3 python heredoc write inside a function',
    'fix3 python heredoc global rebinding',
    "r2 F4 a variable the command sets for Python is not the session's",
    'r2 F4 code that changes os.environ is not read from the session',
    # rule 1: shell variables bound in ways the guard does not resolve (G-1)
    'fix3 variable used before its assignment',
    'fix3 variable assigned in an if',
    'fix3 variable read from a here-string',
    'fix3 variable then source',
    "fix3 assignment in a pipeline is a subshell's",
    'fix3 while read loop rm (target unresolvable, names the tests)',
    # rule 1: patches, whose files the guard does not read (G-1)
    "fix3 git apply -R of a test's diff (differential #146)",
    'fix3 patch from stdin in a command naming the tests',
    # rule 1: a script file written and run by a form the guard cannot read (G-1)
    'r2 F2 repro 4: chmod +x, cd, then ./name',
    'r2 F2 a python file run by runpy',
    'r2 F2 a python file run by exec(open())',
    'r2 F2 a python file run by uv run',
    'r2 F2 a file with no #! line run by its name',
    'r2 F2 a python file that changes folder into the tests',
    # rule 1: Python writes through a glob, listdir, walk, chdir or a computed path (G-1; ACT-GUARD-FIX-3's F4)
    'r2 F4 Path.glob then write_text',
    'r2 F4 Path.glob then unlink',
    'r2 F4 rglob then write_text',
    'r2 F4 listdir then os.remove(os.path.join)',
    'r2 F4 listdir then os.remove(f-string)',
    'r2 F4 os.walk then os.remove',
    'r2 F4 os.chdir into the tests then open w (heredoc)',
    'r2 F4 os.chdir into the tests then open w (-c)',
    'r2 F4 os.chdir into tests then open acceptance/f',
    'r2 F4 tempfile.mkdtemp in the tests',
    'r2 F4 -c: a path built by %',
    "r2 F4 -c: a path built by '/'.join",
    "r2 F4 -c: a path built by ''.join",
    'r2 F4 -c: a path built with chr',
    'r2 F4 -c: glob.glob of the tests then open w',
    # rule 1: code whose write resolves outside every tree of this repository (cd /tmp, then tests/acceptance/...:
    # /tmp/tests/acceptance/), refused by ACT-GUARD-FIX-3 because the path's words hold tests/acceptance; the shell's
    # own write of the same path passed already (G-1: what resolves into a protected folder is judged)
    'guard4: fix2 engineer inline python writes acceptance after a cd',
    'r2 F2 written after a cd, run by bash name',
    'r2 F2 repro 2: cd, then bash name',
}

PLANTED = [(c[0], c[1], c[2], c[3], "allow" if c[0] in LET_THROUGH else c[4]) for c in FIX3.ALL]


@pytest.mark.parametrize("name,role,tool,tin,want", PLANTED, ids=[c[0] for c in PLANTED])
def test_planted(name, role, tool, tin, want):
    agent = None
    if "subagent" in name:
        agent = "engineer" if "engineer subagent" in name else "general-purpose"
    got, why = _hook(role, tool, tin, agent=agent)
    assert got == want or (want == "deny" and got.startswith("deny")), f"{name}: want {want}, got {got} ({why})"


def test_let_through_names_are_planted_cases():
    names = {c[0] for c in FIX3.ALL}
    assert set(LET_THROUGH) <= names, sorted(set(LET_THROUGH) - names)
    assert all(c[4] == "deny" for c in FIX3.ALL if c[0] in LET_THROUGH)


T = "tests/acceptance/W2-64/t.py"
# Rules 1 and 5 after G-1 and G-2: what resolves is judged; what does not is let through.
RULES = [
    ("rule 1: Write into the tests", E, "Write", {"file_path": f"{ROOT}/{T}", "content": "x"}, "deny"),
    ("rule 1: Edit of a test", E, "Edit", {"file_path": f"{ROOT}/{T}", "old_string": "a", "new_string": "b"}, "deny"),
    ("rule 1: redirect into the tests", E, "Bash", b(f"echo x > {T}"), "deny"),
    ("rule 1: the command's own variable resolves", E, "Bash", b(f"D=tests/acceptance/W2-64; cp /tmp/x $D/t.py"),
     "deny"),
    ("rule 1: a literal loop resolves", E, "Bash", b("for f in a b; do touch tests/acceptance/W2-64/$f.py; done"),
     "deny"),
    ("rule 1: inline Python with a literal path", E, "Bash", b(f"python3 -c \"open('{T}', 'w').write('x')\""),
     "deny"),
    ("rule 1: a heredoc into the tests", E, "Bash", b(f"cat > {T} <<'EOF'\nx\nEOF"), "deny"),
    ("rule 1: rm of a test", E, "Bash", b(f"rm -f {T}"), "deny"),
    ("rule 1: cd into the tests, then a relative write", E, "Bash", b("cd tests/acceptance/W2-64 && touch t.py"),
     "deny"),
    ("rule 1: the test designer writes the tests", TD, "Bash", b(f"echo x > {T}"), "allow"),
    ("rule 1 (G-1): a write through a substitution is let through", E, "Bash",
     b("touch $(pwd)/tests/acceptance/W2-64/t.py"), "allow"),
    ("rule 1 (G-1): a variable the guard cannot resolve is let through", E, "Bash",
     b(f"read D <<< tests; touch $D/acceptance/W2-64/t.py"), "allow"),
    ("rule 1 (G-1): inline code naming the tests, writing elsewhere by a computed path", O, "Bash",
     b("python3 -c \"import os; p=os.environ.get('X','/tmp')+'/o'; open(p,'w'); print('tests/acceptance/')\""),
     "allow"),
    ("rule 1 (G-1): a Python heredoc reading a test, writing its scratch by a computed path", O, "Bash",
     b("python3 - <<'EOF'\nimport tempfile, os\nt = open('tests/acceptance/W2-64/t.py').read()\n"
       "open(os.path.join(tempfile.gettempdir(), 'o.txt'), 'w').write(t)\nEOF"), "allow"),
    ("rule 5: a reviewer's Write to code", A, "Write", {"file_path": f"{ROOT}/src/gov/x.py", "content": "x"}, "deny"),
    ("rule 5: a reviewer's redirect into code", A, "Bash", b("echo x > src/gov/x.py"), "deny"),
    ("rule 5: a reviewer's own variable resolving into code", A, "Bash", b("D=src/gov; touch $D/x.py"), "deny"),
    ("rule 5: a reviewer's record", A, "Bash", b("echo x > docs/probes/W2-64-review.md"), "allow"),
    ("rule 5 (G-2): a reviewer's write through mktemp is let through", A, "Bash",
     b("B=$(mktemp -d); mkdir $B/r && echo x > $B/r/o"), "allow"),
    ("rule 5 (G-2): a reviewer's unmatched glob in /tmp is let through", A, "Bash",
     b("cd /tmp && rm -f gov-fix4-nothing-*.json"), "allow"),
    # rule 5: the CTO's review records (.gov-runtime/scratch/orchestrator/reviews/), where its briefs send reviewers
    ("rule 5: a reviewer's Write of its record into reviews/", A, "Write", {"file_path": f"{REV}/e9-review.md",
                                                                          "content": "x"}, "allow"),
    ("rule 5: a reviewer's subfolder in reviews/", A, "Write", {"file_path": f"{REV}/e9/notes.md", "content": "x"},
     "allow"),
    ("rule 5: a reviewer makes reviews/ and writes its record (the E1 review's form)", A, "Bash",
     b(f"rm -rf /tmp/gov-fix4-rev; mkdir -p {REV}; cat > {REV}/e9-review.md <<'EOF'\n# r\nEOF"), "allow"),
    ("rule 5: a relative write into reviews/ from the CTO's folder", A, "Bash",
     b(f"cd {ROOT}/.gov-runtime/scratch/orchestrator && echo x > reviews/e9.md"), "allow"),
    ("rule 5: reviews/ in a worktree", A, "Write",
     {"file_path": f"{WT}/EMG-queue/.gov-runtime/scratch/orchestrator/reviews/e9.md", "content": "x"}, "allow"),
    ("rule 5: a reviewer deletes reviews/", A, "Bash", b(f"rm -rf {REV}"), "deny"),
    ("rule 5: a reviewer makes then deletes reviews/", A, "Bash", b(f"mkdir -p {REV}; rm -rf {REV}"), "deny"),
    ("rule 5: a reviewer moves reviews/", A, "Bash", b(f"mv {REV} /tmp/gov-fix4-r"), "deny"),
    ("rule 5: out of reviews/ by ..", A, "Write", {"file_path": f"{REV}/../briefs/x.md", "content": "x"}, "deny"),
    ("rule 5: a folder whose name starts with reviews", A, "Write", {"file_path": f"{REV}x/a.md", "content": "x"},
     "deny"),
    ("rule 5: the CTO's briefs", A, "Write",
     {"file_path": f"{ROOT}/.gov-runtime/scratch/orchestrator/briefs/x.md", "content": "x"}, "deny"),
    ("rule 5: the CTO's log", A, "Bash", b(f"echo x >> {ROOT}/.gov-runtime/scratch/orchestrator/log/x.jsonl"),
     "deny"),
    ("rule 5: the CTO's folder made", A, "Bash", b(f"mkdir -p {ROOT}/.gov-runtime/scratch/orchestrator/x"), "deny"),
    ("rule 5: unit tests", A, "Write", {"file_path": f"{ROOT}/tests/unit/x.py", "content": "x"}, "deny"),
    ("rule 5: acceptance tests", A, "Write", {"file_path": f"{ROOT}/{T}", "content": "x"}, "deny"),
    ("rule 5: a worktree's code", A, "Write", {"file_path": f"{WT}/EMG-queue/src/gov/x.py", "content": "x"}, "deny"),
    ("rule 5: the subagent form (GOV_ROLE orchestrator, agent independent-auditor) into reviews/", O, "Write",
     {"file_path": f"{REV}/e9.md", "content": "x", "agent": A}, "allow"),
    ("rule 5: the subagent form into code", O, "Write", {"file_path": f"{ROOT}/src/gov/x.py", "content": "x",
                                                         "agent": A}, "deny"),
    ("rule 5: an engineer's write into reviews/ is not rule 5's", E, "Write", {"file_path": f"{REV}/x.md",
                                                                               "content": "x"}, "allow"),
    # rule 1: code's resolved writes into a tree of this repository, not into any folder named tests/acceptance
    ("rule 1: inline Python into another worktree's tests", E, "Bash",
     b(f"python3 -c \"open('{WT}/EMG-queue/{T}', 'w')\""), "deny"),
    ("rule 1: inline Python into a scratch repository's tests (row 81's form)", E, "Bash",
     b("python3 -c \"import os; os.makedirs('/tmp/gov-fix4-repo/tests/acceptance/W1', exist_ok=True)\""), "allow"),
]


@pytest.mark.parametrize("name,role,tool,tin,want", RULES, ids=[c[0] for c in RULES])
def test_rules_1_and_5_judge_what_resolves(name, role, tool, tin, want):
    tin = dict(tin)
    agent = tin.pop("agent", None)
    got, why = _hook(role, tool, tin, agent=agent)
    assert got == want, f"{name}: want {want}, got {got} ({why})"


# --- rm: free but for the catastrophic (DEC-1050 (8)) --------------------------------------------------------------
CATASTROPHIC = [
    "rm -rf /", "rm -rf /*", "rm -rf ~", "rm -rf ~/", "rm -rf $HOME", "rm -rf \"$HOME\"/", "rm -rf /home",
    "cd / && rm -rf home", f"rm -rf {ROOT}", "rm -rf .", "rm -rf ./", f"cd {ROOT}/.. && rm -rf Dynamic-Agentic-Engineering-OS",
    "rm -rf .git", "rm -f .git/index", f"rm -rf {ROOT}/.git/objects", f"rm -f {WT}/EMG-queue/.git",
    "rm README.md", "rm -rf docs", "rm -rf src/gov", "rm -rf ./*", "rm -f template/governance/kernel/roles/*.md",
    "rm -rf tests", "rm -f -- AGENTS.md",
    f"rm -rf {WT}", "rm -rf ~/gov-os-worktrees/", "rm -rf ~/gov-os-runs", "rm -rf /tmp", "rm -rf /tmp/",
    "rm -rf .gov-runtime", "rm -rf .gov-runtime/scratch",
    "rm -f ~/.bashrc", "rm -rf ~/.claude", "rm -rf ~/.ollama", "rm -rf /etc/hostname", "rm -f ~/.local/bin/gov",
    "rm -rf ~/.config", "rm -rf /usr/lib/x", "rm -rf /dev/shm", "rm -rf /dev",
    "rm -rf \"$GOV_FIX4_UNSET\"/", "rm -rf \"$GOV_FIX4_UNSET\"/*", "rm -rf ${GOV_FIX4_UNSET}/home",
    "rm -rf \"$(cat /tmp/gov-fix4-none)\"/", "for d in /tmp/gov-fix4-a ~; do rm -rf $d; done",
    "bash -c 'rm -rf ~'", "echo $(rm -rf /)", "sh -c \"cd / && rm -rf home\"",
    "cat > /tmp/gov-fix4-x.sh <<'EOF'\nrm -rf ~\nEOF\nbash /tmp/gov-fix4-x.sh",
    "/bin/rm -rf /", "command rm -rf /", "timeout 5 rm -rf /", "nohup rm -rf ~ &", "true && \\rm -rf ~",
    "rm -rf / \"unclosed", "rm -f README.md 'unclosed",
]
HONEST = [
    "rm -rf /tmp/gov-os-emg-e3/nothing", "rm -f /tmp/gov-fix4-x.json", "cd /tmp && rm -f gov-fix4-nothing-*.json",
    "rm -rf .gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/work/none",
    "rm -rf .gov-runtime/scratch/lead/none", "rm -rf ~/gov-os-worktrees/EMG-none/build",
    "rm -rf ~/gov-os-worktrees/EMG-none", "rm -rf ~/gov-os-runs/W2-none-clone", "rm -rf /tmp/gov-fix4-repo/.git",
    "d=$(mktemp -d); echo x > $d/a; rm -rf \"$d\"", "out=$(mktemp -d); rm -f \"$out/x\"", "rm -rf \"${GOV_FIX4_UNSET:?}\"/",
    "for f in a b; do rm -f /tmp/gov-fix4-$f; done", "rm -f \"$TMPDIR/gov-fix4-x\"",
    "grep -rn 'rm -rf' docs/contract | head -3", "echo 'rm -rf /'", "git rm --cached -n README.md",
    "cat > /tmp/gov-fix4-y.sh <<'EOF'\nrm -rf ~\nEOF\necho written",
    "find /tmp/gov-fix4-none -name '*.pyc' -delete", "rm -rf src/gov/__pycache__/nothing.pyc",
    # the project's lock in /dev/shm (rm history: 3 calls of 2026-10-30/31, gov-os-W2-76-held.lock)
    "rm -f /tmp/gov-fix4-held.lock /dev/shm/gov-fix4-held.lock",
]


@pytest.mark.parametrize("command", CATASTROPHIC)
@pytest.mark.parametrize("role", [O, E])
def test_catastrophic_rm_is_refused(role, command):
    got, why = _hook(role, "Bash", b(command), tmpdir="/tmp/gov-os-emg-e3")
    assert got == "deny" and "catastrophic delete" in why, f"{command!r} as {role}: {got} ({why})"


@pytest.mark.parametrize("command", HONEST)
def test_honest_rm_passes(command):
    got, why = _hook(O, "Bash", b(command), tmpdir="/tmp/gov-os-emg-e3")
    assert got == "allow", f"{command!r}: {got} ({why})"


def test_rm_in_a_worktree_of_its_own_files_passes():
    wt = WT + "/EMG-queue"
    if not os.path.isdir(wt):
        pytest.skip("no EMG-queue worktree here")
    for command in ("rm -rf build dist", "rm -f src/gov/none.py", "rm -rf .gov-runtime/scratch/x"):
        got, why = _hook(E, "Bash", b(command), cwd=wt, root=wt)
        assert got == "allow", f"{command!r}: {got} ({why})"
    got, why = _hook(TD, "Bash", b("rm -f tests/acceptance/W2-none/t.py"), cwd=wt, root=wt)
    assert got == "allow", why


def test_rm_in_a_removed_worktree_passes():
    """A session whose tree git cannot read (removed): its scratch rm is not refused for that (rm history: 41 calls
    in worktrees removed since were refused as "could not check" before the main tree fell back to the hook's)."""
    wt = WT + "/EMG-gov-fix4-removed"
    assert not os.path.exists(wt)
    for command in (f"rm -rf {wt}/pytest-of-usain", "rm -f .gov-runtime/scratch/lead/x.exit"):
        got, why = _hook(E, "Bash", b(command), cwd=wt, root=wt)
        assert got == "allow", f"{command!r}: {got} ({why})"
    got, why = _hook(E, "Bash", b(f"rm -f {ROOT}/README.md"), cwd=wt, root=wt)
    assert got == "deny" and "tracked" in why, why


def test_rm_through_a_link(tmp_path):
    """A link is removed, not what it points to; a word ending in / follows it."""
    link = tmp_path / "to-main"
    link.symlink_to(ROOT)
    assert _hook(O, "Bash", b(f"rm -f {link}"))[0] == "allow"
    got, why = _hook(O, "Bash", b(f"rm -rf {link}/"))
    assert got == "deny" and "catastrophic delete" in why, why
    got, why = _hook(O, "Bash", b(f"rm -f {link}/README.md"))
    assert got == "deny" and "tracked" in why, why


def test_the_reason_is_plain():
    got, why = _hook(O, "Bash", b("rm -rf \"$GOV_FIX4_UNSET\"/"))
    assert got == "deny" and "if a variable in it that the guard cannot resolve is empty" in why and ":?" in why
    got, why = _hook(O, "Bash", b("rm README.md"))
    assert "main tree's tracked files" in why and "git rm" in why
    got, why = _hook(O, "Bash", b("rm -f ~/.bashrc"))
    assert "outside the project" in why


# --- the logged refusals ----------------------------------------------------------------------------------------------
# Rows 50-53 carry no tool_use id: replayed as their twins (54, 55, 58, 59), as ACT-GUARD-FIX-3 did.
TWIN = {50: 54, 51: 55, 52: 58, 53: 59}
ROLE = {**{i: O for i in (61, 62, 63, 70, 71, 72)}, **{i: A for i in (64, 67, 68, 69, 75, 76)},
        **{i: E for i in (65, 66, 73, 74, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86)}}
# Refused by this hook, each by a rule this ACT does not change or by a write that resolves:
# - rule 2 (reads), as today: rows 65, 74, 77, 78, 79, 82, 83, 84, 85, 86 (a listing whose start the guard cannot
#   place: W2-42a's patterns) and 73, 80 (the hidden half of an evaluation set, refused as designed);
# - rule 4, as today: row 64 (an auditor's probe whose heredoc text holds "sudo touch ...": has_sudo reads text;
#   ACT-GUARD-FIX-3 refused it first by rule 5's unresolvable write).
# Passed now, refused by today's hook: rows 39, 46, 71, 72 (unresolvable writes, G-1/G-2), 75, 76 (a reviewer's record
# into the CTO's reviews/ folder, labelled "as designed" then; rule 5 now names that folder, the CTO's brief of
# 2026-11-03) and 81 (inline code writing a scratch repository's tests/acceptance in /tmp: not a tree of this
# repository).
STILL_REFUSED = [64, 65, 73, 74, 77, 78, 79, 80, 82, 83, 84, 85, 86]


@pytest.mark.skipif(not os.path.exists(CORPUS), reason="the rebuilt corpus is not here (GUARD_FIX4_CORPUS)")
def test_logged_refusals():
    rows = json.load(open(CORPUS))
    refused = []
    for row in rows:
        src = rows[TWIN.get(row["i"], row["i"])]
        role = (src.get("launch_role") if src.get("from") == "fix-3 corpus" else ROLE.get(src["i"])) or O
        cwd = src.get("cwd") or ROOT
        m = re.match(r"(/home/usain/gov-os-worktrees/[^/]+)", cwd)
        tmpdir = src.get("tmpdir")
        if tmpdir is None and src.get("from") != "fix-3 corpus":
            t = re.search(r"/tmp/gov-launch-[a-z-]+-[a-z0-9]{8}", json.dumps(src.get("input")))
            tmpdir = t.group(0) if t else None
        got, _ = _hook(role, src["tool"], src["input"], cwd=cwd, root=m.group(1) if m else ROOT,
                       agent=src.get("agent_type"), tmpdir=tmpdir)
        if got != "allow":
            refused.append(row["i"])
    assert sorted(refused) == sorted(STILL_REFUSED), refused


@pytest.mark.skipif(not os.path.exists(TODAY), reason="today's recovered calls are not here (GUARD_FIX4_TODAY)")
def test_todays_review_record_refusals_pass():
    """The E1 reviewer's Bash and Write of its own record into reviews/ (2026-11-03, refused twice by today's hook;
    the CTO transcribed the record), replayed from the transcript as they ran."""
    rows = json.load(open(TODAY))
    assert len(rows) == 2
    for r in rows:
        got, why = _hook(r["role"], r["tool"], r["input"], cwd=r["cwd"], agent=r["agent_type"])
        assert got == "allow", f"{r['key']}: {got} ({why})"


# --- the module's new parts ---------------------------------------------------------------------------------------

def _module():
    spec = importlib.util.spec_from_file_location("bash_writes4", os.path.join(os.path.dirname(HOOK), "bash_writes.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_emptied():
    bw = _module()
    os.environ.pop("GOV_FIX4_UNSET", None)
    os.environ["GOV_FIX4_SET"] = "/tmp/s"
    assert bw.emptied("$GOV_FIX4_UNSET/") == "/"
    assert bw.emptied("${GOV_FIX4_UNSET}/x") == "/x"
    assert bw.emptied("${GOV_FIX4_UNSET:-/tmp/d}/x") == "/tmp/d/x"
    assert bw.emptied("$GOV_FIX4_SET/$GOV_FIX4_UNSET") == "/tmp/s/"
    assert bw.emptied("${GOV_FIX4_UNSET:?}/") is None
    assert bw.emptied("${GOV_FIX4_UNSET?}/") is None
    assert bw.emptied("${GOV_FIX4_UNSET#x}/") is None
    assert bw.emptied("`__gov_sub_0__`/") == "/"
    assert bw.emptied("$1/x") == "/x"


def test_deletes_are_listed_with_their_loops_and_folders():
    sys.path.insert(0, os.path.dirname(HOOK))
    code = ("import json, sys\nsys.path.insert(0, sys.argv[1])\nimport bash_writes as bw\n"
            "from gov.guard.decide import _expand_token, _extract_bash_write_targets\n"
            "out = {}\n"
            "for c in json.load(sys.stdin):\n"
            "    out[c] = bw.judge(c, '/r', _extract_bash_write_targets, _expand_token).deletes\n"
            "print(json.dumps(out))\n")
    cases = ["rm -rf a /b", "for d in x y; do rm -r /t/$d; done", "cd /s && rm f", "rm -- -f",
             "cat <<'EOF' > /tmp/x\nrm -rf /\nEOF", "D=/q; rm -rf $D/z", "rm -rf $(pwd)/", "echo rm -rf /"]
    p = subprocess.run([PY, "-E", "-c", code, os.path.dirname(HOOK)], input=json.dumps(cases), capture_output=True,
                       text=True, timeout=60, env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"})
    assert p.returncode == 0, p.stderr[-2000:]
    got = {k: [tuple(x) for x in v] for k, v in json.loads(p.stdout).items()}
    assert got["rm -rf a /b"] == [("a", "/r/a", "names"), ("/b", "/b", "names")]
    assert got["for d in x y; do rm -r /t/$d; done"] == [("/t/$d", "/t/x", "names"), ("/t/$d", "/t/y", "names")]
    assert got["cd /s && rm f"] == [("f", "/s/f", "names")]
    assert got["rm -- -f"] == [("-f", "/r/-f", "names")]
    assert got["cat <<'EOF' > /tmp/x\nrm -rf /\nEOF"] == []
    assert got["D=/q; rm -rf $D/z"] == [("$D/z", "/q/z", "names")]
    assert got["rm -rf $(pwd)/"][0][1:] == ("/", "if-empty")
    assert got["echo rm -rf /"] == []


def test_made_lists_mkdir_folders():
    code = ("import json, sys\nsys.path.insert(0, sys.argv[1])\nimport bash_writes as bw\n"
            "from gov.guard.decide import _expand_token, _extract_bash_write_targets\n"
            "print(json.dumps({c: bw.judge(c, '/r', _extract_bash_write_targets, _expand_token).made\n"
            "                  for c in json.load(sys.stdin)}))\n")
    cases = ["mkdir -p a /b", "mkdir -m 700 c", "cd /s && mkdir d", "D=/q; mkdir -p $D/e", "mkdir $(pwd)/f",
             "echo mkdir g", "bash -c 'mkdir /h'", "mv /i /j"]
    p = subprocess.run([PY, "-E", "-c", code, os.path.dirname(HOOK)], input=json.dumps(cases), capture_output=True,
                       text=True, timeout=60, env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"})
    assert p.returncode == 0, p.stderr[-2000:]
    got = json.loads(p.stdout)
    assert got["mkdir -p a /b"] == ["/r/a", "/b"]
    assert got["mkdir -m 700 c"] == ["/r/c"]
    assert got["cd /s && mkdir d"] == ["/s/d"]
    assert got["D=/q; mkdir -p $D/e"] == ["/q/e"]
    assert got["mkdir $(pwd)/f"] == []
    assert got["echo mkdir g"] == []
    assert got["bash -c 'mkdir /h'"] == ["/h"]
    assert got["mv /i /j"] == []

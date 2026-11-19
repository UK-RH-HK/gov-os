"""S3 and F1 (exit 0 whatever the checks find; 2 only when the pass could not run; nothing refuses on its result).

A planted failing check gives exit 0 and a NOTICE; a root that is no folder, no git work tree, not the top of one, or
without a commit, and a usage error, each give exit 2; a static search of ``src/gov/close``, ``src/gov/launch`` and
``src/gov/queue`` (each where it exists) finds no import or call of the pass but the one S3 allows and DEC-1214 L2
decides: the landing's after-step (``src/gov/queue/after.py``, W2-206; L2-COMMANDS section 2 step 8, section 3 A8),
a notice after the move that refuses nothing.

Usage errors are argparse's (L1). Today ``--structural`` is itself an unrecognised argument, which also ends with exit 2;
so every usage case also requires that the message does not say "unrecognized arguments" (an option's own value error,
or a refused combination, never says it) and that no check ran, which is what makes the cases red today.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import w2_158_support as support
from w2_158_support import BOUND, FAMILIES, OUTPUT_ORDER, ROOT

COULD_NOT_RUN = "gov check: structural pass could not run: "


def assert_notice_not_refusal(outcome, tree, *, notices: tuple[str, ...]) -> list[str]:
    lines = outcome.lines()
    assert len(lines) == len(OUTPUT_ORDER) + 1, outcome.text()
    for name in notices:
        assert lines[OUTPUT_ORDER.index(name)].startswith(f"{name}: NOTICE"), lines
    return lines


# --- S3 / F1: exit 0 whatever the checks find ---------------------------------------------------------------------------

def test_s3_a_failing_planted_check_gives_exit_0_and_a_notice(tree):
    """One check finds a problem (exit 1 and a JSON findings list): the pass exits 0 and the family reads NOTICE with the
    finding; the other families still ran and read ok."""
    tree.declare_all("ok")
    tree.declare_family("graph", "find", messages=["a hard-block finding"])
    tree.commit()
    outcome = tree.structural()
    lines = assert_notice_not_refusal(outcome, tree, notices=("graph",))
    assert outcome.code == 0
    assert "a hard-block finding" in lines[1], lines[1]
    assert lines[0] == "schema: ok", lines
    assert "not a refusal" in lines[-1], lines[-1]


def test_f1_every_check_failing_in_every_way_still_gives_exit_0(tree):
    """Findings as a list, as an object, a bare non-zero exit with output on stdout, one with output on stderr only,
    a not-applicable answer and a sleeper at once: exit 0, a line each, nothing on stdout but the eleven lines."""
    tree.declare_family("schema", "find", messages=["one", "two"])
    tree.declare_family("graph", "findobj", messages=["three"])
    tree.declare_family("claims", "first")
    tree.declare_family("mutation", "stderr")
    tree.declare_family("authority", "sleep")
    tree.declare_family("pathmap", "na", messages=["not here"])
    tree.declare("audit-reproducibility", "no-such-program-w2158", family="audit reproducibility")
    tree.declare_family("skills", "find", messages=["skill problem"])
    tree.commit()
    outcome = tree.structural()
    lines = assert_notice_not_refusal(outcome, tree, notices=("schema", "graph", "claims", "mutation", "authority", "audit", "skills"))
    assert outcome.code == 0
    assert lines[OUTPUT_ORDER.index("pathmap")] == "pathmap: ok (not applicable: not here)"
    assert "not a refusal" in lines[-1]


# --- S3: exit 2 only when the pass could not run -------------------------------------------------------------------------

def _could_not_run(outcome, what: str) -> None:
    assert outcome.code == 2, f"{what}: expected exit 2\n{outcome.text()}"
    assert COULD_NOT_RUN in outcome.err, f"{what}: stderr lacks {COULD_NOT_RUN!r}\n{outcome.text()}"
    assert "unrecognized arguments" not in outcome.err, f"{what}: the option is unknown to gov check\n{outcome.text()}"
    assert outcome.out == "", f"{what}: something on stdout\n{outcome.text()}"


def test_s3_a_folder_that_is_no_git_work_tree_gives_exit_2_with_the_reason_on_stderr(tree):
    """``--root`` a plain folder (no ``.git`` in it or above it): exit 2, ``gov check: structural pass could not run:
    ...`` on standard error, nothing on standard output, no check run."""
    plain = tree.base / "plain"
    plain.mkdir()
    tree.declare_family("schema", "ok")
    tree.commit()
    _could_not_run(tree.structural(root=plain), "a folder that is no git work tree")
    assert tree.started() == []


def test_s3_a_path_that_does_not_exist_gives_exit_2(tree):
    """``--root`` a path that does not exist, and one that is a file: exit 2 as above."""
    _could_not_run(tree.structural(root=tree.base / "no-such-folder"), "a path that does not exist")
    _could_not_run(tree.structural(root=tree.tree / "README.md"), "a path that is a file")
    # the same pass, on a tree that exists, runs: this is what makes the cases above a refusal of the root
    tree.declare_family("schema", "ok")
    tree.commit()
    assert tree.structural().family("schema") == "schema: ok"


def test_s3_a_folder_inside_a_work_tree_but_not_its_top_gives_exit_2(tree):
    """``--root`` a sub-folder of a git work tree is not the top of one: exit 2 as above."""
    tree.declare_family("schema", "ok")
    tree.commit(files={"sub/deeper/file.txt": "x\n"})
    _could_not_run(tree.structural(root=tree.tree / "sub" / "deeper"), "a sub-folder of a work tree")
    assert tree.started() == []


def test_s3_a_work_tree_with_no_commit_gives_exit_2(tree):
    """A git work tree with no commit has no HEAD: exit 2 as above, no check run."""
    other = tree.base / "unborn"
    other.mkdir()
    subprocess.run(["git", "-C", str(other), "init", "-q"], env=tree.git_env(), check=True, timeout=60)
    (other / "checks").mkdir()
    (other / "checks" / "marker.py").write_text(support.MARKER)
    declaration = other / support.DECL_DIR / "core-schema.yaml"
    declaration.parent.mkdir(parents=True)
    declaration.write_text(f'id: "core-schema"\nfamily: "schema/invariants"\ntier: "G1"\nseverity: "hard-block"\n'
                           f'command: "python3 checks/marker.py {tree.marks} core-schema ok"\n')
    _could_not_run(tree.structural(root=other), "a work tree with no commit")
    assert not tree.ran("core-schema")


@pytest.mark.parametrize("args, what", [
    (("--timeout", "0"), "--timeout 0"),
    (("--timeout", "-1"), "--timeout -1"),
    (("--timeout=-3",), "--timeout=-3"),
    (("--timeout", "abc"), "--timeout abc"),
    (("--timeout", ""), "--timeout with an empty value"),
])
def test_s3_a_timeout_that_is_not_a_number_above_zero_is_a_usage_error(tree, args, what):
    """``--timeout`` is a number of seconds above 0: 0, a negative, text and an empty value are usage errors, exit 2,
    with the option's own error (not "unrecognized arguments"), nothing on stdout, no check run."""
    tree.declare_family("schema", "ok")
    tree.commit()
    outcome = tree.gov("check", "--structural", *args, "--root", str(tree.tree))
    assert outcome.code == 2, f"{what}: expected exit 2\n{outcome.text()}"
    assert "unrecognized arguments" not in outcome.err, f"{what}: gov check does not know --structural\n{outcome.text()}"
    assert "--timeout" in outcome.err or "timeout" in outcome.err, f"{what}: the error does not name the option\n{outcome.text()}"
    assert outcome.out == "" and not tree.ran("core-schema"), outcome.text()


def test_s3_structural_with_list_is_a_usage_error(tree):
    """``--structural`` and ``--list`` together are refused (exit 2); ``--list`` alone still lists the declarations."""
    tree.declare_family("schema", "ok")
    tree.commit()
    outcome = tree.gov("check", "--structural", "--list", "--root", str(tree.tree))
    assert outcome.code == 2 and outcome.out == "", outcome.text()
    assert "unrecognized arguments" not in outcome.err, outcome.text()
    assert not tree.ran("core-schema")


def test_s3_a_base_without_structural_is_a_usage_error(tree):
    """A ``<base>`` given without ``--structural`` is refused (exit 2), and ``--structural <base>`` is the same call
    that runs."""
    tree.declare_family("schema", "ok")
    base = tree.commit()
    refused = tree.gov("check", base, "--root", str(tree.tree))
    assert refused.code == 2 and refused.out == "", refused.text()
    assert "unrecognized arguments" not in refused.err, f"gov check takes no <base>\n{refused.text()}"
    ran = tree.structural(base)
    assert ran.code == 0 and ran.family("schema") == "schema: ok", ran.text()


# --- the command module's declarations; the plain command is as before ----------------------------------------------------

def test_s3_the_module_declares_a_child_exit_code_and_keeps_its_exit_codes(tree):
    """L8: ``gov.check.command`` declares ``CHILD_EXIT_CODE = True`` (``gov`` ends with the int ``run`` returns and prints no
    envelope) and keeps ``EXIT_CODES == {3: "checks failed"}`` for the plain ``gov check``."""
    tree._check_source()
    code = "import gov.check.command as c; print(repr(getattr(c, 'CHILD_EXIT_CODE', None))); print(repr(c.EXIT_CODES))"
    done = subprocess.run([sys.executable, "-c", code], env=tree.env(), cwd=str(tree.base), capture_output=True,
                          text=True, timeout=support.COMMAND_TIMEOUT_S)
    assert done.returncode == 0, done.stderr
    assert done.stdout.splitlines() == ["True", "{3: 'checks failed'}"], done.stdout


def test_s3_check_list_still_lists_the_declarations_as_before(tree):
    """Guard (green today): ``gov check --list --json`` still answers the envelope with the declarations of the tree."""
    tree.declare_family("schema", "ok")
    tree.commit()
    outcome = tree.gov("check", "--list", "--json", "--root", str(tree.tree))
    assert outcome.code == 0, outcome.text()
    assert '"ok": true' in outcome.out and "core-schema" in outcome.out, outcome.text()
    assert "structural pass" not in outcome.out


# --- S3 / F1: nothing refuses or waits on the pass ----------------------------------------------------------------------

CALL = re.compile(r"gov\.check\.structural|from\s+gov\.check\s+import[^\n]*\bstructural\b|\bimport\s+structural\b"
                  r"|--structural|\brun_structural\b|check\.structural\b")
# S3: "a landing may call it after the fact and log its lines". DEC-1214 L2 decides the one caller (L2-COMMANDS section
# 2 step 8, section 3 A8; W2-206): the landing's after-step, a module of its own in the queue. Nothing else in the
# commit, close, launch or queue code may refer to the pass, and close and launch may not reach it through the
# after-step either.
AFTER_STEP = "src/gov/queue/after.py"
AFTER_STEP_REFERENCE = re.compile(r"gov\.queue\.after\b|from\s+gov\.queue\s+import[^\n#]*\bafter\b"
                                  r"|from\s+\.+queue\s+import[^\n#]*\bafter\b|\bqueue\.after\b")
# What the search cannot see (when the pass runs, what its result changes) is held by W2-206's own acceptance cases,
# which run a planted landing: the pass ran once, after the move, with the landing's base; a pass that exits 2 leaves
# the exit code 0 and the branch at the landed head; a landing that landed nothing runs no after-step. The allowance
# above stands only while those cases stand.
W2_206_AFTER_CASES = ROOT / "tests" / "acceptance" / "W2-206" / "test_w2_206_after.py"
W2_206_GUARDS = ("test_the_structural_pass_ran_once_after_the_move_with_the_landing_s_base",
                 "test_a_structural_pass_that_exits_2_is_a_notice_and_the_landing_stands",
                 "test_a_landing_that_landed_nothing_runs_neither_after_step")
ENDS_THE_PROCESS = {"exit", "_exit", "abort", "kill", "killpg"}  # sys.exit, exit, os._exit, os.abort, os.kill, ...


def _refusals(source: str) -> list[str]:
    """Each statement of a module's code that could refuse on a result: a ``raise``, an ``assert``, or a call that ends
    the process. Read from the syntax tree, so a word in a comment or a docstring is no finding."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Raise, ast.Assert)):
            found.append(f"line {node.lineno}: {type(node).__name__.lower()}")
        elif isinstance(node, ast.Call):
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            if name in ENDS_THE_PROCESS or name == "SystemExit":
                found.append(f"line {node.lineno}: {name}(...)")
    return found


def test_s3_and_f1_no_commit_close_landing_or_launch_code_calls_the_pass():
    """A static search of ``src/gov/close``, ``src/gov/launch`` and ``src/gov/queue`` (each where it exists; at least one
    must) finds no import or call of ``structural`` / ``gov.check.structural`` / ``--structural`` whose result decides
    a refusal (S3, F1). One caller is allowed, the one S3 names ("a landing may call it after the fact and log its
    lines") and DEC-1214 L2 decides (L2-COMMANDS section 2 step 8 and section 3 A8; W2-206): the landing's after-step,
    ``src/gov/queue/after.py``. The case is red for:

    - any other file of close, launch or queue that refers to the pass;
    - any file of close or launch that refers to the after-step (the pass reached before a commit or inside the
      close's gates by another door);
    - an after-step that holds a ``raise``, an ``assert`` or a call ending the process (its results are notices: it
      has nothing to refuse with);
    - W2-206's acceptance cases for A8 S2 and A8 F1 gone or skipped: they hold, on a planted landing, that the pass
      ran once and only after the move and that its exit code changes neither the landing's exit code nor the branch.
    """
    existing = [ROOT / "src" / "gov" / name for name in ("close", "launch", "queue") if (ROOT / "src" / "gov" / name).is_dir()]
    assert existing, "none of src/gov/close, src/gov/launch, src/gov/queue exists: the search guards nothing"
    scanned, hits, doors, allowed = 0, [], [], []
    for folder in existing:
        for path in sorted(folder.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            scanned += 1
            rel = path.relative_to(ROOT).as_posix()
            for number, line in enumerate(text.splitlines(), 1):
                if CALL.search(line):
                    (allowed if rel == AFTER_STEP else hits).append(f"{rel}:{number}: {line.strip()}")
                if folder.name != "queue" and AFTER_STEP_REFERENCE.search(line):
                    doors.append(f"{rel}:{number}: {line.strip()}")
    assert scanned > 0, "no file was searched"
    assert not hits, ("code of close, launch or queue other than the landing's after-step refers to the structural "
                      "pass:\n" + "\n".join(hits))
    assert not doors, "code of close or launch refers to the landing's after-step:\n" + "\n".join(doors)
    if not allowed:
        return  # no caller at all: nothing can refuse or wait on the pass (the state W2-158 was built in)
    refusals = _refusals((ROOT / AFTER_STEP).read_text(encoding="utf-8"))
    assert not refusals, (f"{AFTER_STEP} calls the structural pass and can refuse (S3: no landing refuses or waits on "
                          f"its result; A8 F1: a notice only): {refusals}")
    assert W2_206_AFTER_CASES.is_file(), (
        f"{AFTER_STEP} calls the structural pass and {W2_206_AFTER_CASES.relative_to(ROOT)}, whose cases hold that it "
        f"runs after the move and changes no exit code, is gone")
    tree = ast.parse(W2_206_AFTER_CASES.read_text(encoding="utf-8"))
    cases = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    missing = [name for name in W2_206_GUARDS if name not in cases]
    assert not missing, f"W2-206's cases that hold the after-step to a notice after the move are gone: {missing}"
    switched_off = [name for name in W2_206_GUARDS
                    if any(mark in ast.unparse(decorator) for decorator in cases[name].decorator_list
                           for mark in ("skip", "xfail"))]
    assert not switched_off, f"W2-206's cases that hold the after-step to a notice are skipped: {switched_off}"

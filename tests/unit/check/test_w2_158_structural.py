"""Unit tests of ``gov check --structural`` (W2-158; S1-S5, F1-F4; Interface items L1-L10).

Planted git trees under ``tmp_path`` with stand-in declared commands; nothing of this repository's own checks runs.
"""
from __future__ import annotations

import io
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check import structural  # noqa: E402
from gov.cli.main import main  # noqa: E402

FAMILY_IDS = {"schema": "core-schema", "graph": "core-graph", "claims": "core-claims", "mutation": "core-mutation",
              "authority": "core-authority", "pathmap": "core-pathmap", "audit": "audit-reproducibility",
              "skills": "skill-regression-a", "portability": "adapter-portability"}
EIGHT = ["schema", "graph", "claims", "mutation", "authority", "pathmap", "audit", "skills"]
GIT_ENV = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_AUTHOR_NAME": "T",
           "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@t", "LC_ALL": "C"}


def py(code: str) -> str:
    """A declared command that runs ``code`` with the interpreter."""
    return "python3 -c " + shlex.quote(code)


OK = py("pass")


def git(tree, *args):
    env = {**os.environ, **GIT_ENV, "HOME": str(Path(tree).parent)}
    return subprocess.run(["git", "-C", str(tree), *args], capture_output=True, text=True, check=True, env=env)


def declaration(command, ident, family="x"):
    return yaml.safe_dump({"id": ident, "family": family, "tier": "T1", "severity": "warning", "command": command})


def plant(tmp_path, commands=None, files=None, layout="template/governance/kernel/checks", commit=True):
    """A git tree ``tmp_path/tree`` with one declaration per ``{id: command}`` and ``files`` ({rel: text})."""
    tree = tmp_path / "tree"
    tree.mkdir()
    git(tree, "init", "-q", "-b", "main")
    for ident, command in (commands or {}).items():
        family = "skill regression" if ident.startswith("skill-regression") else ident
        path = tree / layout / f"{ident}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(declaration(command, ident, family), encoding="utf-8")
    for rel, text in (files or {}).items():
        path = tree / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (tree / "a.txt").write_text("a\n", encoding="utf-8")
    if commit:
        git(tree, "add", "-A")
        git(tree, "commit", "-q", "-m", "plant")
    return tree


def commit_file(tree, rel, text="changed\n"):
    path = tree / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    git(tree, "add", "-A")
    git(tree, "commit", "-q", "-m", f"change {rel}")


def head(tree) -> str:
    return git(tree, "rev-parse", "HEAD").stdout.strip()


def run_pass(tree, base=None, timeout=30):
    out = io.StringIO()
    rc = structural.run_structural(Path(tree), base, timeout, out)
    return rc, out.getvalue().splitlines()


def by_family(lines):
    return {line.split(":", 1)[0]: line for line in lines if ":" in line and not line.startswith("structural")}


def all_ok(tmp_path, **override):
    commands = {ident: OK for family, ident in FAMILY_IDS.items() if family != "portability"}
    commands.update(override)
    return plant(tmp_path, commands)


# ---- S1, S2: one process per family, all at once; one line per family ----------------------------------------

def test_s1_eight_processes_start_together_and_one_line_per_family(tmp_path):
    marks = tmp_path / "marks"
    barrier = (f"import pathlib,sys,time\nd=pathlib.Path({str(marks)!r}); d.mkdir(exist_ok=True)\n"
               "(d/str(time.time_ns())).write_text('x')\nend=time.time()+15\n"
               "while time.time()<end:\n  if len(list(d.iterdir()))>=8: sys.exit(0)\n  time.sleep(0.05)\nsys.exit(3)\n")
    tree = all_ok(tmp_path, **{ident: py(barrier) for f, ident in FAMILY_IDS.items() if f != "portability"})
    rc, lines = run_pass(tree)
    assert rc == 0
    assert len(list(marks.iterdir())) == 8  # eight processes started, and each saw all the others (at once)
    fams = by_family(lines)
    assert [line.split(":")[0] for line in lines[:8]] == EIGHT
    assert all(fams[f] == f"{f}: ok" for f in EIGHT)


def test_output_order_and_last_line(tmp_path):
    tree = all_ok(tmp_path)
    rc, lines = run_pass(tree)
    assert rc == 0
    assert [line.split(":")[0] for line in lines[:-1]] == EIGHT + ["portability", "links"]
    assert lines[8] == "portability: skipped (no base given)"
    assert lines[9] == "links: skipped (no base given)"
    assert lines[-1].startswith(f"structural pass at {head(tree)[:12]}")
    assert "NOTICE" not in lines[-1] and "ok" in lines[-1]
    assert len(lines) == 11


def test_s2_not_applicable_finding_and_plain_exit(tmp_path):
    na = py("import json,sys; print(json.dumps({'not_applicable': True, 'reason': 'no docs here'})); sys.exit(2)")
    msgs = py("import json,sys; print(json.dumps([{'message': 'm1'}, {'message': 'm2'}])); sys.exit(1)")
    found = py("import json,sys; print(json.dumps({'findings': [{'message': 'found-it'}]})); sys.exit(3)")
    plain = py("import sys; print('boom happened'); print('second'); sys.exit(1)")
    err = py("import sys; print('stderr first', file=sys.stderr); sys.exit(4)")
    tree = all_ok(tmp_path, **{"core-schema": na, "core-graph": msgs, "core-claims": found, "core-mutation": plain,
                               "core-authority": err})
    rc, lines = run_pass(tree)
    fams = by_family(lines)
    assert rc == 0
    assert fams["schema"] == "schema: ok (not applicable: no docs here)"
    assert fams["graph"] == "graph: NOTICE m1 | m2"
    assert fams["claims"] == "claims: NOTICE found-it"
    assert fams["mutation"] == "mutation: NOTICE core-mutation exit 1: boom happened"
    assert fams["authority"] == "authority: NOTICE core-authority exit 4: stderr first"
    assert fams["pathmap"] == "pathmap: ok"
    assert "NOTICE" in lines[-1] and "graph" in lines[-1] and "not a refusal" in lines[-1]


def test_s2_at_most_three_findings_and_each_shortened(tmp_path):
    many = py("import json,sys; print(json.dumps([{'message': 'm%d' % i} for i in range(1, 6)])); sys.exit(1)")
    long = py("import json,sys; print(json.dumps([{'message': 'x' * 500}])); sys.exit(1)")
    tree = all_ok(tmp_path, **{"core-schema": many, "core-graph": long})
    _, lines = run_pass(tree)
    fams = by_family(lines)
    assert fams["schema"] == "schema: NOTICE m1 | m2 | m3 (+2 more)"
    assert fams["graph"].startswith("graph: NOTICE xxx") and fams["graph"].endswith("...") and len(fams["graph"]) < 250


def test_s1_s2_a_command_past_the_bound_is_killed_with_its_group_and_reads_not_measured(tmp_path):
    pidfile = tmp_path / "grandchild.pid"
    slow = py("import subprocess,time\n"
              f"p=subprocess.Popen(['sleep','60']); open({str(pidfile)!r},'w').write(str(p.pid))\ntime.sleep(60)")
    tree = all_ok(tmp_path, **{"core-schema": slow})
    started = time.monotonic()
    rc, lines = run_pass(tree, timeout=1)
    took = time.monotonic() - started
    fams = by_family(lines)
    assert rc == 0
    assert took < 8
    assert fams["schema"] == "schema: NOTICE not measured: core-schema did not end within 1 s"
    assert fams["graph"] == "graph: ok"
    pid = int(pidfile.read_text())
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and _alive(pid):
        time.sleep(0.1)
    assert not _alive(pid)  # the grandchild died with the group


def _alive(pid: int) -> bool:
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"
    except OSError:
        return False


def test_fractional_bound_is_named_as_given(tmp_path):
    tree = all_ok(tmp_path, **{"core-schema": py("import time; time.sleep(30)")})
    _, lines = run_pass(tree, timeout=0.5)
    assert by_family(lines)["schema"] == "schema: NOTICE not measured: core-schema did not end within 0.5 s"


# ---- F3: the tree's own declarations only --------------------------------------------------------------------

def test_f3_marker_command_runs_and_a_family_without_declaration_is_skipped(tmp_path):
    marker = tmp_path / "marker"
    tree = plant(tmp_path, {"core-schema": py(f"open({str(marker)!r},'w').write('ran')")})
    rc, lines = run_pass(tree)
    fams = by_family(lines)
    assert rc == 0 and marker.read_text() == "ran"
    assert fams["schema"] == "schema: ok"
    for family in EIGHT[1:]:
        assert fams[family] == f"{family}: skipped (no declaration)"


def test_f3_no_builtin_command_in_the_module():
    text = (REPO / "src/gov/check/structural.py").read_text(encoding="utf-8")
    assert "gov.check.schema" not in text and "gov.check.skill_validator" not in text
    assert "gov.adapters.portability" not in text


def test_declarations_of_the_installed_layout_are_read_and_the_template_one_wins(tmp_path):
    inst = plant(tmp_path, {"core-schema": py("import sys; print('installed'); sys.exit(1)")},
                 layout="governance/kernel/checks")
    assert by_family(run_pass(inst)[1])["schema"] == "schema: NOTICE core-schema exit 1: installed"
    both = tmp_path / "both"
    both.mkdir()
    tree = plant(both, {"core-schema": OK})
    path = tree / "governance/kernel/checks/core-schema.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(declaration(py("import sys; sys.exit(1)"), "core-schema"), encoding="utf-8")
    assert by_family(run_pass(tree)[1])["schema"] == "schema: ok"


def test_a_file_that_cannot_be_read_makes_only_its_own_family_a_notice(tmp_path):
    tree = all_ok(tmp_path)
    (tree / "template/governance/kernel/checks/core-graph.yaml").write_text("id: [unclosed\n  - : :", encoding="utf-8")
    (tree / "template/governance/kernel/checks/core-claims.yaml").write_text("id: core-claims\nfamily: x\n",
                                                                           encoding="utf-8")
    rc, lines = run_pass(tree)
    fams = by_family(lines)
    assert rc == 0
    assert fams["graph"].startswith("graph: NOTICE") and "core-graph.yaml" in fams["graph"]
    assert fams["claims"].startswith("claims: NOTICE") and "core-claims.yaml" in fams["claims"]
    assert fams["schema"] == "schema: ok" and fams["skills"] == "skills: ok"


def test_a_command_that_cannot_be_started_is_a_notice(tmp_path):
    tree = all_ok(tmp_path, **{"core-schema": "no-such-program-w2158 --flag", "core-graph": "python3 -c 'unclosed"})
    rc, lines = run_pass(tree)
    fams = by_family(lines)
    assert rc == 0
    assert fams["schema"].startswith("schema: NOTICE core-schema could not run:")
    assert fams["graph"].startswith("graph: NOTICE core-graph could not run:")


def test_skills_family_is_every_declaration_of_the_skill_regression_family(tmp_path):
    bad = py("import sys; print('skill broke'); sys.exit(1)")
    tree = all_ok(tmp_path, **{"skill-regression-b1": bad, "skill-regression-orchestration": OK})
    fams = by_family(run_pass(tree)[1])
    assert fams["skills"] == "skills: NOTICE skill-regression-b1 exit 1: skill broke"
    ok_tree = tmp_path / "ok"
    ok_tree.mkdir()
    tree2 = all_ok(ok_tree, **{"skill-regression-b1": OK, "skill-regression-orchestration": OK})
    assert by_family(run_pass(tree2)[1])["skills"] == "skills: ok"


# ---- L4: how a command runs -----------------------------------------------------------------------------------

def test_l4_interpreter_environment_cwd_and_stdin(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_W2158_PROBE", "leak")
    monkeypatch.setenv("W2158_KEPT", "kept")
    tree = plant(tmp_path)
    code = ("import os,sys\n"
            f"ok = sys.executable == {sys.executable!r}\n"
            f"ok &= os.getcwd() == {str(tree.resolve())!r}\n"
            f"ok &= os.environ.get('PYTHONPATH') == {str(tree / 'src')!r}\n"
            "ok &= os.environ.get('PYTHONDONTWRITEBYTECODE') == '1'\n"
            "ok &= not [k for k in os.environ if k.startswith('GIT_')]\n"
            "ok &= os.environ.get('W2158_KEPT') == 'kept'\n"
            "ok &= sys.stdin.read() == ''\n"
            "sys.exit(0 if ok else 9)")
    (tree / "template/governance/kernel/checks").mkdir(parents=True)
    (tree / "template/governance/kernel/checks/core-schema.yaml").write_text(
        declaration(py(code), "core-schema"), encoding="utf-8")
    fams = by_family(run_pass(tree)[1])
    assert fams["schema"] == "schema: ok", fams["schema"]


# ---- S4: portability and links need a base --------------------------------------------------------------------

def _portability_tree(tmp_path):
    marks = tmp_path / "port-ran"
    tree = plant(tmp_path, {"adapter-portability": py(f"open({str(marks)!r},'w').write('x')")})
    return tree, marks


@pytest.mark.parametrize("path, runs", [("template/governance/kernel/roles/r.md", True),
                                        ("template/governance/kernel/skills/s/SKILL.md", True),
                                        ("template/governance/kernel/hooks/h.py", True),
                                        (".rulesync/rules/x.md", True),
                                        ("docs/other.md", False),
                                        ("template/governance/kernel/checks/other.yaml", False)])
def test_s4_portability_runs_only_when_the_change_touches_the_kernel(tmp_path, path, runs):
    tree, marks = _portability_tree(tmp_path)
    commit_file(tree, path)
    rc, lines = run_pass(tree, base="HEAD~1")
    line = by_family(lines)["portability"]
    assert rc == 0
    assert marks.exists() is runs
    assert line == ("portability: ok" if runs else "portability: skipped (no such change)")


def test_s4_portability_runs_when_the_base_does_not_resolve_and_is_left_out_without_a_base(tmp_path):
    tree, marks = _portability_tree(tmp_path)
    assert by_family(run_pass(tree, base="no-such-rev")[1])["portability"] == "portability: ok"
    assert marks.exists()
    marks.unlink()
    assert by_family(run_pass(tree)[1])["portability"] == "portability: skipped (no base given)"
    assert not marks.exists()


def test_s4_portability_without_declaration_is_skipped(tmp_path):
    tree = plant(tmp_path)
    assert by_family(run_pass(tree, base="no-such-rev")[1])["portability"] == "portability: skipped (no declaration)"


LINKS_FILES = {"src/gov/__init__.py": "", "src/gov/cli/__init__.py": "", "src/gov/links/__init__.py": ""}


def _links_tree(tmp_path, body):
    marks = tmp_path / "links-argv"
    stub = ("import sys\n" f"open({str(marks)!r}, 'w').write(' '.join(sys.argv[1:]))\n" + body)
    return plant(tmp_path, files={**LINKS_FILES, "src/gov/cli/main.py": stub}, commit=True), marks


def test_s4_links_clean_and_called_as_the_ticket_says(tmp_path):
    tree, argv = _links_tree(tmp_path, "print('gov links: 0 new since HEAD~1, 4 standing (x)')\n")
    commit_file(tree, "docs/other.md")
    rc, lines = run_pass(tree, base="HEAD~1")
    assert rc == 0
    assert by_family(lines)["links"] == "links: ok (0 new since HEAD~1, 4 standing)"
    assert argv.read_text() == "links --since HEAD~1"
    assert lines[-2].startswith("links:")


def test_s4_links_new_findings_are_a_notice_with_the_first_lines(tmp_path):
    body = ("print('gov links: 5 new since HEAD~1, 4 standing (x)')\n"
            "for i in range(5): print('UNLINKED_ID finding %d' % i)\nsys.exit(1)\n")
    tree, _ = _links_tree(tmp_path, body)
    commit_file(tree, "docs/other.md")
    rc, lines = run_pass(tree, base="HEAD~1")
    line = by_family(lines)["links"]
    assert rc == 0
    assert line == "links: NOTICE 5 new: UNLINKED_ID finding 0 | UNLINKED_ID finding 1 | UNLINKED_ID finding 2 (+2 more)"
    assert "links" in lines[-1] and "not a refusal" in lines[-1]


def test_s4_links_that_cannot_run_or_time_out(tmp_path):
    tree, _ = _links_tree(tmp_path, "print('gov links: LINKS_BAD_REV', file=sys.stderr)\nsys.exit(2)\n")
    rc, lines = run_pass(tree, base="HEAD")
    assert rc == 0
    assert by_family(lines)["links"] == "links: NOTICE gov links could not run (exit 2): gov links: LINKS_BAD_REV"
    odd = tmp_path / "odd"
    odd.mkdir()
    tree2, _ = _links_tree(odd, "print('something else')\n")
    assert by_family(run_pass(tree2, base="HEAD")[1])["links"].startswith("links: NOTICE gov links could not run (exit 0)")
    slow = tmp_path / "slow"
    slow.mkdir()
    tree3, _ = _links_tree(slow, "import time; time.sleep(60)\n")
    started = time.monotonic()
    _, lines3 = run_pass(tree3, base="HEAD", timeout=1)
    assert time.monotonic() - started < 8
    assert by_family(lines3)["links"].startswith("links: NOTICE not measured")


def test_s4_links_skipped_without_the_folder_or_without_a_base(tmp_path):
    tree = all_ok(tmp_path)
    assert by_family(run_pass(tree, base="HEAD")[1])["links"] == "links: skipped (no gov links in this tree)"
    other = tmp_path / "o"
    other.mkdir()
    tree2, argv = _links_tree(other, "print('gov links: 0 new since HEAD, 0 standing')\n")
    assert by_family(run_pass(tree2)[1])["links"] == "links: skipped (no base given)"
    assert not argv.exists()


# ---- S3, L8: exit codes ----------------------------------------------------------------------------------------

def test_s3_a_failing_check_gives_exit_0_and_a_notice_through_the_command_line(tmp_path, capsys):
    tree = all_ok(tmp_path, **{"core-schema": py("import sys; print('red'); sys.exit(3)")})
    rc = main(["check", "--structural", "--root", str(tree), "--timeout", "20"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "schema: NOTICE core-schema exit 3: red" in captured.out
    assert '"ok"' not in captured.out  # no envelope: the command's own exit code (CHILD_EXIT_CODE)


def test_s3_json_flag_changes_nothing(tmp_path, capsys):
    tree = all_ok(tmp_path)
    assert main(["check", "--structural", "--json", "--root", str(tree)]) == 0
    assert capsys.readouterr().out.splitlines()[0] == "schema: ok"


@pytest.mark.parametrize("make", ["no_folder", "not_git", "subfolder", "no_head"])
def test_s3_exit_2_when_the_pass_cannot_run(tmp_path, capsys, make):
    if make == "no_folder":
        target = tmp_path / "nope"
    elif make == "not_git":
        target = tmp_path / "plain"
        target.mkdir()
    elif make == "subfolder":
        target = plant(tmp_path) / "src"
        target.mkdir()
    else:
        target = tmp_path / "empty"
        target.mkdir()
        git(target, "init", "-q", "-b", "main")
    out = io.StringIO()
    rc = structural.run_structural(Path(target), None, 5, out)
    captured = capsys.readouterr()
    assert rc == 2
    assert out.getvalue() == "" and captured.out == ""
    assert captured.err.startswith("gov check: structural pass could not run: ")


@pytest.mark.parametrize("argv", [["--timeout", "0"], ["--timeout", "-1"], ["--timeout", "abc"], ["--timeout", "nan"]])
def test_l1_a_bad_timeout_is_argparses_usage_error(argv, capsys):
    with pytest.raises(SystemExit) as stop:
        main(["check", "--structural", *argv])
    assert stop.value.code == 2
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("argv", [["--structural", "--list"], ["HEAD~1"], ["--timeout", "5"]])
def test_l1_other_usage_errors_exit_2_with_nothing_on_stdout(argv, tmp_path, capsys):
    tree = all_ok(tmp_path)
    try:
        rc = main(["check", *argv, "--root", str(tree)])
    except SystemExit as stop:
        rc = stop.code
    captured = capsys.readouterr()
    assert rc == 2 and captured.out == ""
    assert "error" in captured.err or "usage" in captured.err


def test_l1_list_and_plain_check_are_as_before(tmp_path, capsys):
    tree = all_ok(tmp_path)
    assert main(["check", "--list", "--json", "--root", str(tree)]) == 0
    result = json.loads(capsys.readouterr().out)["result"]
    assert {c["id"] for c in result["checks"]} == set(FAMILY_IDS.values()) - {"adapter-portability"}
    from gov.check import command
    assert command.EXIT_CODES == {3: "checks failed"} and command.CHILD_EXIT_CODE is True


# ---- S5, L9: reads and writes nothing else ---------------------------------------------------------------------

def _snapshot(tree):
    return {str(p.relative_to(tree)): (p.stat().st_size, p.stat().st_mtime_ns)
            for p in tree.rglob("*") if p.is_file()}


def test_s5_the_pass_writes_no_file_and_leaves_the_index_alone(tmp_path):
    tree = all_ok(tmp_path, **{"core-schema": py("import helper")})
    (tree / "helper.py").write_text("X = 1\n", encoding="utf-8")
    git(tree, "add", "-A")
    git(tree, "commit", "-q", "-m", "helper")
    os.utime(tree / "a.txt", (1, 1))  # a `git status` would now rewrite the index
    index = (tree / ".git/index").read_bytes()
    before = _snapshot(tree)
    rc, lines = run_pass(tree, base="HEAD~1")
    assert rc == 0 and by_family(lines)["schema"] == "schema: ok"
    assert _snapshot(tree) == before
    assert (tree / ".git/index").read_bytes() == index
    assert not list(tree.rglob("__pycache__"))


# ---- S3, F1: nothing decides on it -----------------------------------------------------------------------------

@pytest.mark.parametrize("folder", ["close", "launch", "queue"])
def test_s3_no_close_launch_or_queue_code_calls_it(folder):
    root = REPO / "src/gov" / folder
    for path in (root.rglob("*.py") if root.is_dir() else ()):
        text = path.read_text(encoding="utf-8")
        assert "structural" not in text, path


def test_f4_the_pass_is_two_product_files_only():
    assert (REPO / "src/gov/check/structural.py").is_file()
    text = (REPO / "src/gov/check/command.py").read_text(encoding="utf-8")
    assert "--structural" in text.split('"""')[1]  # the module docstring names the option

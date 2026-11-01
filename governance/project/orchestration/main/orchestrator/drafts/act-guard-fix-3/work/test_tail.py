

# --- one synthetic case per pattern of the 61 logged refusals (guard-refusals.jsonl), with the rows it stands for --
TD = "independent-test-designer"
CORPUS_PATTERNS = [
    ("rows 0: a brief build whose argument names the tests", O, "Bash",
     b("cd .gov-runtime/scratch/orchestrator && python3 tools/build_lead_brief.py p.md o.md "
       "PATHS=tests/acceptance/W2-90/**"), "allow", None),
    ("rows 1-18, 24-30: grep, ls, find, git diff and pytest on the tests", O, "Bash",
     b("grep -rln wbs_id tests/acceptance/W1-30/ | head -20; ls tests/acceptance/W2-54/; "
       "git diff HEAD~1 -- tests/acceptance/W1-30/x.py | head; python3 -m pytest -q tests/acceptance/W2-76"),
     "allow", None),
    ("rows 21, 22: the import check, then a listing of the tests", O, "Bash",
     b("PYTHONPATH=src python3 -c \"import gov; print(gov.__file__)\"; ls tests/acceptance/W2-05/"), "allow", None),
    ("rows 31, 44: inline Python putting the tests' folder on sys.path", A, "Bash",
     b("PYTHONDONTWRITEBYTECODE=1 python3 -B -c \"\nimport sys; sys.path.insert(0, 'tests/acceptance/W2-81')\n"
       "import w2_81_score as s\nprint(s)\n\""), "allow", None),
    ("row 33: inline Python reading a test's text for a parser", A, "Bash",
     b("PYTHONPATH=src python3 -B -c \"\nfrom pathlib import Path\nfrom gov.accept.runner import parse_map\n"
       "m = parse_map(Path('tests/acceptance/W1-30/README.md').read_text())\nprint(len(m))\n\"; "
       "grep -n '^#' tests/acceptance/W1-30/README.md | sed -n '1,60p'"), "allow", None),
    ("row 49: inline Python reading a support module with a regex", A, "Bash",
     b("python3 -c \"\nimport re\nt=open('tests/acceptance/W2-96/w2_96_support.py').read()\n"
       "m=re.search(r'\\ndef pid_running\\(.*?(?=\\n(?:def |# ---))', t, re.S)\nprint(m)\n\""), "allow", None),
    ("row 57: env vars and PYTHONPATH naming the tests' folder", A, "Bash",
     b("W2_81_PROBE_OUT=/tmp/gov-fix3-r PYTHONPATH=src:tests/acceptance/W2-81 python3 -c "
       "\"import w2_81_run as r; print(r)\""), "allow", None),
    ("rows 23, 45, 59: a Python heredoc editing files elsewhere, text naming the tests", O, "Bash",
     b("cd .gov-runtime/scratch/orchestrator && python3 - <<'EOF'\np='drafts/x/pretooluse.py'; s=open(p).read()\n"
       "s=s.replace('a', 'ACCEPTANCE = \"tests/acceptance/\"', 1)\nopen(p,'w').write(s)\n"
       "p='tools/guard4_check.py'; s=open(p).read()\ns=s.replace('b', '(\"tests/acceptance/x\" ; ls')\n"
       "open(p,'w').write(s)\nEOF"), "allow", None),
    ("rows 55, 58: a Python heredoc reading tickets, then inline Python reading a return", O, "Bash",
     b("python3 - <<'EOF'\nimport yaml, glob\nfor p in glob.glob('.tickets/*.md'):\n    s = open(p).read()\n"
       "print('tests/acceptance/W2-61/')\nEOF\npython3 -c \"\nimport re\nfor m in re.finditer("
       "r'tests/acceptance/W2-61/[\\w./-]+', 'x'): print(m.group(0))\" | sort -u | head"), "allow", None),
    ("rows 40, 50: an unquoted brief heredoc, escaped backticks, nested quotes in a substitution", O, "Bash",
     b("cd /tmp && tail_part=$(sed -n \"$(grep -n '^## How' /tmp/gov-fix3-b.md | cut -d: -f1),\\$p\" "
       "/tmp/gov-fix3-b.md); cat > /tmp/gov-fix3-brief.md <<EOF\nYou are the lead for \\`W2-96\\`; tests in "
       "\\`tests/acceptance/W2-96/\\` (don't edit).\n$tail_part\nEOF\npython3 /tmp/gov-fix3-build.py "
       "\"PATHS=$(python3 -c \"print(', '.join(['tests/acceptance/W2-96/**']))\")\" ROWS=none"), "allow", None),
    ("rows 42, 54: a register or brief appended by a quoted heredoc naming the tests", O, "Bash",
     b("cd /tmp && { cat <<'EOF'\n# W2-11: tests/acceptance/W2-11/ stay the designer's (it's DEC-995)\nEOF\n"
       "cat /tmp/gov-fix3-r.md; } > /tmp/gov-fix3-move.md && cat >> /tmp/gov-fix3-register.md <<'EOF'\n"
       "### DEC-978: W1-27's case in tests/acceptance/W1-27/ (a)\nEOF"), "allow", None),
    ("rows 34, 35, 36, 41, 43, 47, 56: an auditor's own variables naming /tmp", A, "Bash",
     b("B=/tmp/gov-fix3/p8; mkdir -p $B/r && D=/tmp/gov-fix3/pf && git diff --name-only HEAD~1 HEAD | sort > "
       "$D/m.txt; T=/tmp/gov-fix3; HOME=$T/fakehome timeout 5 true > $T/help.txt 2> $T/help.err; "
       "H=$T/p/lxhome && mkdir -p $H && printf 'x\\n' \"$H\" > $H/.gitconfig"), "allow", None),
    ("row 48: an auditor's loop over literal words", A, "Bash",
     b("cd /tmp && for s in term int hup; do python3 /tmp/gov-fix3-probe5.py label=$s > w1-sleep-$s.out 2>&1; "
       "done; cat w1-sleep-*.out"), "allow", None),
    ("row 37: an auditor's substitution with its own quotes inside double quotes", A, "Bash",
     b("cd /tmp && for f in a.xml b.xml; do echo \"$f: $(grep -o '<testsuite [^>]*' $f | grep -o ' "
       "\\(name\\|tests\\)=\"[^\"]*\"' | tr -d '\\n')\"; done"), "allow", None),
    ("row 38: an auditor's probe heredoc with lines the parser read as redirects", A, "Bash",
     b("cat > \"/tmp/gov-fix3-r3/p_pty.py\" <<'EOF'\nimport os\nif x > deadline:\n    pass\nEOF"), "allow", None),
    ("row 32: an auditor's probe heredoc whose text names secret files (rule 3)", A, "Bash",
     b("mkdir -p /tmp/gov-fix3/fa && cat > /tmp/gov-fix3/fa/fa_probe.py <<'PYEOF'\n"
       "# stages .env, x.pem and config/secrets.yaml in a stand-in\ncat .env\nPYEOF\necho written"), "allow", None),
    ("row 60: a fixed-line read loop on the register (research, the hidden set measures it)", "research", "Bash",
     b("cd /home/usain/Dynamic-Agentic-Engineering-OS; for n in 864 7795; do sed -n \"${n},$((n+6))p\" "
       "docs/DECISION_REGISTER.md | cut -c1-700; echo ====; done"), "allow", None),
    # The two left refused, by design (see the package).
    ("row 39 (left refused): an auditor's rm of an unmatched glob, which the product's parser cannot place", A,
     "Bash", b("cd /tmp && rm -f gov-fix3-nothing-*.json"), "deny", None),
    ("row 46 (left refused): an unquoted Python heredoc the shell rewrites, in a command naming the tests", O,
     "Bash", b("n=\"tests/acceptance/W1-33/t.py::x\"; out=$(python3 -m pytest -q \"$n\" 2>&1); python3 - \"$n\" "
               "<<EOF\nimport sys\nprint('''$(echo \"$out\" | sed \"s/'/ /g\")''', sys.argv[1])\nEOF"), "deny", None),
]


def _guard4_cases():
    """guard4_check.py's 54 planted cases (DEC-953 item 2, ACT-GUARD-FIX-1 and -2), read without running its loop."""
    src = open(GUARD4).read()
    ns = {"__name__": "guard4", "sys": sys}
    argv, sys.argv = sys.argv, ["guard4_check.py"]
    try:
        exec(src[:src.index("ok = True")], ns)
    finally:
        sys.argv = argv
    return [(f"guard4: {c[0]}",) + tuple(c[1:]) for c in ns["CASES"]]


def _hook(role, tool, tin, cwd=ROOT, root=ROOT, agent=None, tmpdir=None):
    """The hook's decision, run as Claude Code runs it: event JSON on stdin, the pinned judge's interpreter, -E."""
    role, _, ticket = role.partition("@")
    event = {"tool_name": tool, "tool_input": tin, "cwd": cwd, "session_id": "guard-fix-3", "agent_type": agent}
    env = dict(os.environ, GOV_ROLE=role, GOV_TICKET=ticket or "DAEO-sdxk", CLAUDE_PROJECT_DIR=root)
    env.pop("TMPDIR", None)
    if tmpdir:
        env["TMPDIR"] = tmpdir
    p = subprocess.run([PY, "-E", HOOK], input=json.dumps(event), capture_output=True, text=True, env=env, timeout=90)
    if p.returncode == 2:
        return "deny", p.stderr
    if p.stdout.strip():
        out = json.loads(p.stdout)["hookSpecificOutput"]
        return out["permissionDecision"], out["permissionDecisionReason"]
    return "allow", ""


ALL = _guard4_cases() + CASES + [c[:5] for c in CORPUS_PATTERNS]


@pytest.mark.parametrize("name,role,tool,tin,want", ALL, ids=[c[0] for c in ALL])
def test_case(name, role, tool, tin, want):
    agent = None
    if "subagent" in name:
        agent = "engineer" if "engineer subagent" in name else "general-purpose"
    got, why = _hook(role, tool, tin, agent=agent)
    assert got == want or (want == "deny" and got.startswith("deny")), f"{name}: want {want}, got {got} ({why})"


@pytest.mark.skipif(not os.path.exists(CORPUS), reason="the rebuilt corpus is not here (GUARD_FIX3_CORPUS)")
def test_logged_corpus():
    """The 61 logged refusals, replayed from their transcripts' full commands (rows 50-53, which carry no tool_use
    id, as their twins 54, 55, 58, 59): at most 6 (10 %) refused, and exactly rows 39 and 46."""
    rows = json.load(open(CORPUS))
    twin = {50: 54, 51: 55, 52: 58, 53: 59}
    refused = []
    for row in rows:
        src = rows[twin.get(row["i"], row["i"])]
        cwd = src["cwd"]
        m = re.match(r"(/home/usain/gov-os-worktrees/[^/]+)", cwd)
        got, _ = _hook(src.get("launch_role") or "orchestrator", src["tool"], src["input"], cwd=cwd,
                       root=m.group(1) if m else ROOT, agent=src.get("agent_type"), tmpdir=src.get("tmpdir"))
        if got != "allow":
            refused.append(row["i"])
    assert len(refused) <= 6 and sorted(refused) == [39, 46], refused


# --- the module itself ---------------------------------------------------------------------------------------------

def _module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("bash_writes", os.path.join(os.path.dirname(HOOK), "bash_writes.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_heredoc_bodies_are_cut_and_marked():
    bw = _module()
    text, bodies = bw.heredocs("cat > /tmp/x <<'EOF'\nrm -rf /\nEOF\necho done")
    assert "rm -rf" not in text and "__gov_hdl_0__" in text and "echo done" in text
    assert bodies[0]["text"] == "rm -rf /" and bodies[0]["quoted"]


@pytest.mark.parametrize("command", ["cat <<EOF\nx", "echo 'x", "echo $((1<<2)) <<EOF\nx\nEOF",
                                     "echo \"$(echo 'x\")"])
def test_unreadable_falls_back(command):
    bw = _module()
    with pytest.raises(bw.Unreadable):
        bw.lift(bw.heredocs(command)[0])
        bw.tokens(bw.lift(bw.heredocs(command)[0])[0])


def test_variables_resolve_only_when_safe():
    bw = _module()
    expand = lambda value, env: value  # noqa: E731
    env, loops, drop = bw.variants("B=/tmp/x; mkdir $B/r", expand)
    assert env == {"B": "/tmp/x"} and not drop
    env, loops, drop = bw.variants("mkdir $B/r; B=/tmp/x", expand)
    assert "B" in drop
    env, loops, drop = bw.variants("if true; then B=/tmp; fi; mkdir $B", expand)
    assert "B" in drop
    env, loops, drop = bw.variants("B=/tmp; . ./env.sh; mkdir $B", expand)
    assert "B" in drop
    env, loops, drop = bw.variants("for s in a b; do touch $s; done", expand)
    assert loops == {"s": ["a", "b"]}


def test_python_writes_reads_are_not_writes():
    bw = _module()
    judge = lambda text, cwd, depth: []  # noqa: E731
    assert bw.python_writes("print(open('tests/acceptance/x').read())", "/r", judge, 0) == []
    got = bw.python_writes("p='a'\nopen(p,'w')\np='tests/acceptance/x'\nopen(p,'a')", "/r", judge, 0)
    assert [g[0] for g in got] == ["a", "tests/acceptance/x"]
    assert bw.python_writes("exec('x')", "/r", judge, 0) == [(bw.SENT, None)]


def test_reads_view_cuts_data_bodies_only():
    bw = _module()
    assert ".env" not in bw.reads_view("cat > /tmp/p.py <<'EOF'\ncat .env\nEOF")
    assert ".env" in bw.reads_view("cat > /tmp/p.sh <<'EOF'\ncat .env\nEOF\nsh /tmp/p.sh")
    assert ".env" in bw.reads_view("python3 - <<'EOF'\nprint(open('.env').read())\nEOF")
    assert "$((" not in bw.reads_view("sed -n \"1,$((n+6))p\" f")


_NO_CRASH = """
import json, os, sys
sys.path.insert(0, sys.argv[1])
import bash_writes as bw
from gov.guard.decide import _expand_token, _extract_bash_write_targets
bad = []
for name, command in json.load(sys.stdin):
    try:
        bw.judge(command, sys.argv[2], _extract_bash_write_targets, _expand_token)
        bw.reads_view(command)
    except bw.Unreadable:
        pass
    except Exception as exc:  # a crash would refuse (exit 2): a case must never pass by crashing
        bad.append((name, repr(exc)))
print(json.dumps(bad))
"""


def test_no_case_is_judged_by_a_crash():
    """bash_writes raises nothing but Unreadable on any Bash case: a refusal by a crash (exit 2) would hide a bug."""
    cases = [(c[0], c[3]["command"]) for c in ALL if c[2] == "Bash"]
    p = subprocess.run([PY, "-E", "-c", _NO_CRASH, os.path.dirname(HOOK), ROOT], input=json.dumps(cases),
                       capture_output=True, text=True, timeout=300)
    assert p.returncode == 0, p.stderr[-2000:]
    assert json.loads(p.stdout) == []

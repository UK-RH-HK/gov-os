"""Builder tests for W2-42a: the product's read judge does not misread a literal path as a run-time listing, nor
``$((...))`` for a substitution, nor a data heredoc's body for commands (DEC-1040 item 2, ACT-GUARD-FIX-3 §7 line 6);
every read it refused for a protected file before is still refused.

Regression evidence only (DEC-136). Every project is a temporary one; the session is a research one, which the
stand-in evaluation set measures.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.reads import (HIDDEN_REFUSAL, RUNTIME_REFUSAL, SECRET_REFUSAL,  # noqa: E402
                             _arithmetic, _set_aside, policy_refusal)

TICKET = "DAEO-t42r"
SETS = ("evaluation_sets:\n  m:\n    visible: [docs/q.md]\n"
        "    hidden: [eval/hidden/**]\n    measures:\n      roles: [research]\n")


def _put(root: Path, rel: str, text: str = "x\n") -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


@pytest.fixture()
def project(tmp_path, monkeypatch):
    home = tmp_path / "home"
    root = home / "proj"
    monkeypatch.setenv("HOME", str(home))
    _put(root, f".tickets/{TICKET}.md", f"---\nid: {TICKET}\nwbs_id: W2-97\nstatus: in_progress\n"
                                        "role: research\nallowed_paths:\n- docs/**\n---\n")
    for rel in ("docs/q.md", "docs/n.md", "src/app/main.py", ".env", "eval/hidden/a.yaml", "eval/hidden/7.yaml",
                "eval/visible.md"):
        _put(root, rel)
    _put(root, "governance/project/held-out.yaml", "held_out_paths:\n  - /nowhere/held\n")
    _put(root, "governance/project/path-map.yaml", "namespaces: {}\n" + SETS)
    return root


def why(root, command, cwd=None):
    return policy_refusal("Bash", {"command": command}, str(root), str(cwd or root), "research", TICKET)


# -- the misreadings, now read by the files the command names ---------------------------------------------------

PASS = [
    # A wait loop over $(seq ...) that greps one literal file (row 77's form).
    "for i in $(seq 1 16); do grep -q 'passed\\|failed' docs/q.md 2>/dev/null && break; sleep 0; done; tail -3 docs/q.md",
    # $((...)) is arithmetic (row 60's form).
    'for n in 3 9; do sed -n "${n},$((n+6))p" docs/q.md | cut -c1-80; done',
    'sed -n "1,$(( 2 * 3 ))p" docs/q.md',
    # A data heredoc appended to a file, which the command then reads (row 79's form): its backticks are text.
    "cat >> docs/n.md <<'EOF'\n- the `find eval -type f | xargs cat` form, and `$(ls eval)`\nEOF\ntail -3 docs/n.md",
    # A python3 heredoc editing a file by its literal path (rows 74 and 78's form).
    "cd docs && python3 - <<'EOF'\nimport pathlib\np = pathlib.Path(\"n.md\")\ns = p.read_text()\n"
    "for a, b in [('x', 'y')]:\n    s = s.replace(a, b)  # `$(ls)` and for f in $(find .)\np.write_text(s)\nEOF\n"
    "grep -n x n.md",
    # A git commit message read from a heredoc.
    "git commit -q -F - <<'EOF'\nfor f in $(ls eval); do cat $f; done is the form refused\nEOF",
    # A number from nproc, wc or date as an option's value or a name's part.
    "grep -m $(nproc) x docs/q.md",
    "head -n $(wc -l < docs/n.md) docs/q.md",
    "grep -c x docs/q.md > /tmp/w242a-$(date +%s).txt; cat docs/q.md $(wc -l docs/n.md)",
    # Text in single quotes is no substitution; an apostrophe in double quotes opens no quote (log lines 84, 85).
    "grep -n \"A process's cores\" -A1 docs/q.md; grep -n '| `rerank_gpu_slots` |' docs/q.md",
    "python3 tool.py docs/q.md 'for f in $(cat list.txt); do cat $f; done' 'cat list.txt | xargs cat'",
]


@pytest.mark.parametrize("command", PASS)
def test_a_command_that_names_its_files_literally_passes(project, command):
    assert why(project, command) == ""


# -- what stays refused ---------------------------------------------------------------------------------------

REFUSE = [
    ("for f in $(find eval -type f); do cat $f; done", HIDDEN_REFUSAL),
    ("for f in $(cat list.txt); do eval \"cat \\$f\"; cat docs/q.md; done", RUNTIME_REFUSAL),
    ("for f in $(cat list.txt); do g=$f; cat $g; done", RUNTIME_REFUSAL),
    ("for f in $(cat list.txt); do n=f; cat ${!n}; done", RUNTIME_REFUSAL),
    ("for f in $(cat list.txt); do cat docs/q.md; done; cat $f", RUNTIME_REFUSAL),  # its last name, after it
    ("for f in $(seq -f %g.yaml 1 2); do cat $f; done", RUNTIME_REFUSAL),
    ("cat $(seq -f eval/hidden/%g.yaml 1 2)", None),
    ("cd eval/hidden && for i in $(seq 1 9); do cat $i.yaml; done", None),
    ("echo $(( $(cat eval/hidden/a.yaml) + 1 ))", HIDDEN_REFUSAL),
    ("python3 - <<'EOF'\nprint(open('eval/hidden/a.yaml').read())\nEOF", HIDDEN_REFUSAL),
    ("python3 - <<'EOF'\nprint(open('.env').read())\nEOF", SECRET_REFUSAL),
    ("bash <<'EOF'\ncat eval/hidden/a.yaml\nEOF", HIDDEN_REFUSAL),
    ("cat > s.sh <<'EOF'\ncat eval/hidden/a.yaml\nEOF\nbash s.sh", HIDDEN_REFUSAL),
    ("cat <<EOF\n$(cat eval/hidden/a.yaml)\nEOF", HIDDEN_REFUSAL),
    ("cat <<'EOF' | bash\nfind eval | xargs cat\nEOF", HIDDEN_REFUSAL),
    ("tk create x <<'EOF'\nsee eval/hidden/a.yaml\nEOF", HIDDEN_REFUSAL),
    ("cat 'unbalanced <<EOF\neval/hidden/a.yaml", None),
    ("cat .e\\\nnv", SECRET_REFUSAL),
    ("cat eval/hid\\\nden/a.yaml", HIDDEN_REFUSAL),
    ("cat $(date)", RUNTIME_REFUSAL),
    ("cat $(date +%Y/%m)", RUNTIME_REFUSAL),
    ("cat $(wc -l eval/hidden/a.yaml)", HIDDEN_REFUSAL),
    ("grep -n \"it's\" docs/q.md $(cat list.txt)", RUNTIME_REFUSAL),  # outside the quotes
    ("grep -n \"x$(cat list.txt)'y\" docs/q.md; cat $(cat list.txt)", RUNTIME_REFUSAL),
    ("cat 'a' $(cat list.txt) 'b'", RUNTIME_REFUSAL),
    ("cat $'it\\'s' $(cat list.txt) 'x'", RUNTIME_REFUSAL),  # $'...': unsure, no quote is read
    ("cat \"$(cat list.txt)\"", RUNTIME_REFUSAL),
]


@pytest.mark.parametrize("command,reason", REFUSE)
def test_a_read_of_a_protected_file_is_still_refused(project, command, reason):
    got = why(project, command)
    assert got, command
    if reason is not None:
        assert got == reason


def test_a_numbered_name_in_a_folder_with_a_numbered_protected_file_refuses(project):
    assert why(project, "for i in $(seq 1 9); do cat $i.yaml; done", cwd=project / "eval" / "hidden")


def test_arithmetic_is_no_substitution():
    text, subs = _set_aside('sed -n "${n},$((n+6))p" f')
    assert subs == []
    text, subs = _set_aside("echo $(( $(wc -l < f) + 1 ))")
    assert subs == ["wc -l < f"]
    text, subs = _set_aside("x=$((cd a) && (cat b))")
    assert subs == ["(cd a) && (cat b)"]
    command = "$((1+2))"
    assert _arithmetic(command, 2, len(command) - 1)

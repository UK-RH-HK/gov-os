"""W2-141 (DEC-1093 (2), DEC-1102): an engineer's search that can reach its own ticket's acceptance folder is refused
unless the call keeps the folder out, and the refusal names the folder and says how.

Both sides are tested on the same planted calls: the product's decide function (``gov.guard.reads.policy_refusal``,
through ``gov.guard.decide.decide`` too) and the hook as staged for the operator's ACT
(``docs/changes/W2-141-hook/role_reads.py``, loaded by path; its ``bash_writes`` is the live hook folder's). The
pretooluse copy differs from the live file only by Glob in G-14's tool list, and the hook's matching block is
``reads.py``'s byte for byte. No real session, model or embedder.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.decide import _expand_token, decide  # noqa: E402
from gov.guard.reads import TESTS_REFUSAL, policy_refusal  # noqa: E402

LIVE = REPO / ".claude" / "hooks"
STAGED = REPO / "docs" / "changes" / "W2-141-hook"
TICKET, W = "DAEO-t141", "W2-95"
OWN = f"tests/acceptance/{W}/"
ROLE_PATHS = ('role_paths:\n  engineer:\n    reads_denied: ["{ticket_tests}"]\n'
              '  independent-test-designer:\n    reads_denied: ["{ticket_impl}"]\n')
HOW = {  # a word of each refusal's "how"
    "Grep": f"!tests/acceptance/{W}/**", "grep": f"--exclude-dir={W}", "rg": f"-g '!tests/acceptance/{W}/**'",
    "ag": f"--ignore-dir={W}", "ack": f"--ignore-dir={W}", "find": f"-name {W} -prune -o",
    "Glob": "Glob has no exclusion", "git": f"-- . ':!tests/acceptance/{W}'",
}


def _put(root: Path, rel: str, text: str = "x\n") -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


def _plant(root: Path, files=(f"{OWN}test_feature.py", f"{OWN}README.md")) -> Path:
    _put(root, f".tickets/{TICKET}.md", f"---\nid: {TICKET}\nwbs_id: {W}\nstatus: in_progress\nrole: engineer\n"
                                        "allowed_paths:\n- src/**\n---\n")
    for rel in (*files, "tests/acceptance/W2-96/test_other.py", "tests/unit/test_u.py", "src/app/main.py",
                "docs/q.md"):
        _put(root, rel)
    _put(root, "governance/project/held-out.yaml", "held_out_paths:\n  - /nowhere/held\n")
    _put(root, "governance/project/path-map.yaml", "namespaces: {}\n" + ROLE_PATHS)
    git = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(git + ["init", "-q", "-b", "w2/integrate"], check=True, capture_output=True)
    subprocess.run(git + ["add", "-A"], check=True, capture_output=True)
    subprocess.run(git + ["commit", "-qm", "base"], check=True, capture_output=True)
    return root.resolve()


@pytest.fixture()
def project(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    return _plant(tmp_path / "proj")


@pytest.fixture(scope="module")
def rr():
    sys.path.insert(0, str(LIVE))  # bash_writes, as the hook finds it beside itself
    spec = importlib.util.spec_from_file_location("role_reads_w2_141", STAGED / "role_reads.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _decide(root, role, tool, tin, cwd=None):
    return policy_refusal(tool, tin, str(root), str(cwd or root), role, TICKET, None)


def _hook(rr, root, role, tool, tin, cwd=None, trees=None):
    return rr.refusal(str(root), str(root), tool, tin, str(cwd or root), [role], TICKET,
                      trees or (lambda: [str(root)]), _expand_token) or ""


def _b(command):
    return "Bash", {"command": command}


E, TD, O, A = "engineer", "independent-test-designer", "orchestrator", "independent-auditor"

REFUSED = [  # (name, tool, input, how): S1 and S2, the engineer
    ("Grep from the root", "Grep", {"pattern": "z"}, "Grep"),
    ("Grep from tests/", "Grep", {"pattern": "z", "path": "tests"}, "Grep"),
    ("Grep from tests/acceptance/", "Grep", {"pattern": "z", "path": "tests/acceptance"}, "Grep"),
    ("Grep with the glob **/*.py", "Grep", {"pattern": "z", "glob": "**/*.py"}, "Grep"),
    ("Grep whose later glob takes the folder back", "Grep",
     {"pattern": "z", "glob": f"!tests/acceptance/{W}/** *.py"}, "Grep"),
    ("Glob **/*.py", "Glob", {"pattern": "**/*.py"}, "Glob"),
    ("Glob *.py (a name at any depth)", "Glob", {"pattern": "*.py"}, "Glob"),
    ("Glob tests/**", "Glob", {"pattern": "tests/**"}, "Glob"),
    ("Glob from tests/", "Glob", {"pattern": "**/*", "path": "tests"}, "Glob"),
    ("grep -rn from the root", *_b("grep -rn z ."), "grep"),
    ("grep -rn from tests/", *_b("grep -rn z tests/"), "grep"),
    ("grep -R with no folder", *_b("grep -R z"), "grep"),
    ("grep --exclude-dir with a path (excludes nothing)", *_b(f"grep -rn --exclude-dir=tests/acceptance/{W} z ."),
     "grep"),
    ("grep -r after a cd", *_b("cd tests && grep -r z ."), "grep"),
    ("rg", *_b("rg z"), "rg"),
    ("rg from tests", *_b("rg z tests"), "rg"),
    ("rg whose later glob takes the folder back", *_b(f"rg -g '!tests/acceptance/{W}/**' -g '*.py' z"), "rg"),
    ("ag", *_b("ag z"), "ag"),
    ("ack", *_b("ack z"), "ack"),
    ("find -exec cat", *_b("find . -name '*.py' -exec cat {} +"), "find"),
    ("find -not -path on the folder only", *_b(f"find . -not -path ./tests/acceptance/{W} -exec cat {{}} +"),
     "find"),
    ("find piped into xargs grep", *_b("find . -name '*.py' | xargs grep -n q"), "find"),
    ("find piped into a while-read loop that reads", *_b('find tests -type f | while read f; do cat "$f"; done'),
     "find"),
    ("find in a reader's $(...) word", *_b("cat $(find . -name '*.py')"), "find"),
    ("rg --files piped into xargs cat", *_b("rg --files | xargs cat"), "rg"),
    # the review's round 1 (F1 to F6)
    ("F1 git grep from the root", *_b("git grep -n z"), "git"),
    ("F1 git grep -- .", *_b("git grep -n z -- ."), "git"),
    ("F1 git grep with a revision", *_b("git grep -n z HEAD"), "git"),
    ("F1 git -C tests grep", *_b("git -C tests grep z"), "git"),
    ("F1 git grep whose pathspec glob can reach it", *_b("git grep z -- '*.py'"), "git"),
    ("F1 git grep whose exclusion is another folder", *_b("git grep z -- . ':!tests/acceptance/W2-96'"), "git"),
    ("F2 git ls-files piped into xargs grep", *_b("git ls-files | xargs grep z"), "git"),
    ("F2 git ls-files tests piped into xargs cat", *_b("git ls-files tests | xargs cat"), "git"),
    ("F2 git ls-files in a reader's $(...) word", *_b("grep -n q $(git ls-files '*.py')"), "git"),
    ("F3 a for loop over find's names that reads", *_b("for f in $(find . -name '*.py'); do head -3 $f; done"),
     "find"),
    ("F3 a for loop over rg --files that reads", *_b('for f in $(rg --files); do head -3 "$f"; done'), "rg"),
    ("F3 a for loop over git ls-files that reads", *_b("for f in $(git ls-files); do cat $f; done"), "git"),
    ("F4 grep -rn from */", *_b("grep -rn z */"), "grep"),
    ("F4 grep -rn from tests/*", *_b("grep -rn z tests/*"), "grep"),
    ("F4 rg from tests/*", *_b("rg z tests/*"), "rg"),
    ("F4 grep -rn from tests/acc*", *_b("grep -rn z tests/acc*"), "grep"),
    ("F4 find from tests/* with a reading action", *_b("find tests/* -name '*.py' -exec cat {} +"), "find"),
    ("F5 zgrep -r", *_b("zgrep -r z ."), "grep"),
    ("F5 grep -d recurse", *_b("grep -d recurse z ."), "grep"),
    ("F5 grep --directories=recurse", *_b("grep --directories=recurse z ."), "grep"),
    ("F6 a brace-expanded exclusion of other folders", *_b("grep -rn --exclude-dir={.git,node_modules} z ."),
     "grep"),
]

ALLOWED = [  # (name, role, tool, input): S3
    ("Grep keeping the folder out", E, "Grep", {"pattern": "z", "glob": f"!tests/acceptance/{W}/**"}),
    ("Grep from tests/ keeping it out", E, "Grep", {"pattern": "z", "path": "tests",
                                                    "glob": f"!tests/acceptance/{W}/**"}),
    ("Grep keeping it out from any folder", E, "Grep", {"pattern": "z", "glob": f"!**/{W}/**"}),
    ("Grep whose glob cannot reach it", E, "Grep", {"pattern": "z", "glob": "*.yaml src/**"}),
    ("Grep from src", E, "Grep", {"pattern": "z", "path": "src"}),
    ("Grep in another ticket's tests", E, "Grep", {"pattern": "z", "path": "tests/acceptance/W2-96"}),
    ("Glob under src", E, "Glob", {"pattern": "src/**/*.py"}),
    ("Glob from src", E, "Glob", {"pattern": "**/*.py", "path": "src"}),
    ("Glob of a kind the folder lacks", E, "Glob", {"pattern": "**/*.yaml"}),
    ("grep --exclude-dir by base name", E, *_b(f"grep -rn --exclude-dir={W} z .")),
    ("grep --include of a kind the folder lacks", E, *_b("grep -rn z --include='*.yaml' .")),
    ("rg keeping it out", E, *_b(f"rg -g '!tests/acceptance/{W}/**' z")),
    ("rg after a cd, keeping it out from there", E, *_b(f"cd tests && rg -g '!acceptance/{W}/**' z")),
    ("rg with a glob that cannot reach it", E, *_b("rg z -g '*.yaml'")),
    ("ag --ignore-dir", E, *_b(f"ag --ignore-dir={W} z")),
    ("ack --ignore-dir", E, *_b(f"ack --ignore-dir={W} z")),
    ("find -prune by name", E, *_b(f"find . -name {W} -prune -o -type f -exec cat {{}} +")),
    ("find -prune by path, piped into a reader", E,
     *_b(f"find . -path ./tests/acceptance/{W} -prune -o -name '*.py' -print | xargs grep q")),
    ("find -not -path on its files", E, *_b(f"find . -not -path '*/{W}/*' -name '*.py' -exec cat {{}} +")),
    ("find -maxdepth above the folder", E, *_b("find . -maxdepth 2 -name '*.py' -exec cat {} +")),
    ("find listing names only", E, *_b("find . -name '*.py'")),
    ("rg --files listing names only", E, *_b("rg --files")),
    ("ls -R listing names only", E, *_b("ls -R tests")),
    ("a grep for the tests' name by pattern", E, *_b(f"grep -rn tests/acceptance/{W} src/")),
    ("a search in another ticket's tests", E, *_b("grep -rn z tests/acceptance/W2-96")),
    ("rg fed by a pipe", E, *_b("git log --oneline | rg z")),
    ("a start the guard cannot resolve", E, *_b("grep -rn z $NOWHERE_W2_141")),
    # the review's round 1 (F1 to F6)
    ("F1 git grep -- . with the exclusion pathspec", E, *_b(f"git grep z -- . ':!tests/acceptance/{W}'")),
    ("F1 git grep with the exclusion alone", E, *_b(f"git grep z -- ':^tests/acceptance/{W}'")),
    ("F1 git grep with the long exclusion", E, *_b(f"git grep z -- ':(exclude)tests/acceptance/{W}/*'")),
    ("F1 git grep with an exclusion glob", E, *_b(f"git grep z -- ':!*/{W}/*'")),
    ("F1 git grep -- src", E, *_b("git grep -n z -- src")),
    ("F1 git grep from src", E, *_b("git -C src grep z")),
    ("F1 git grep in another ticket's tests", E, *_b("git grep z -- tests/acceptance/W2-96")),
    ("F2 git ls-files keeping it out, into a reader", E,
     *_b(f"git ls-files -- . ':!tests/acceptance/{W}' | xargs grep z")),
    ("F2 git ls-files src into a reader", E, *_b("git ls-files src | xargs cat")),
    ("F2 git ls-files into a command that does not read", E, *_b("git ls-files | xargs wc -l")),
    ("F3 a for loop over src's names that reads", E, *_b("for f in $(find src -name '*.py'); do head -3 $f; done")),
    ("F3 a for loop over names that does not read", E, *_b("for f in $(find . -name '*.py'); do echo $f; done")),
    ("F4 grep -rn from src/*", E, *_b("grep -rn z src/*")),
    ("F4 grep -rn from a glob that cannot reach it", E, *_b("grep -rn z tests/u*")),
    ("F4 grep -rn from tests/* keeping it out", E, *_b(f"grep -rn --exclude-dir={W} z tests/*")),
    ("F5 zgrep -r keeping it out", E, *_b(f"zgrep -r --exclude-dir={W} z .")),
    ("F5 grep -d recurse from src", E, *_b("grep -d recurse z src")),
    ("F6 a brace-expanded exclusion", E, *_b(f"grep -rn --exclude-dir={{.git,{W}}} z .")),
    ("F6 rg with a brace-expanded glob option", E, *_b(f"rg -g{{'!tests/acceptance/{W}/**','!*.md'}} z")),
    ("the orchestrator's git grep from the root", O, *_b("git grep -n z")),
    ("the orchestrator's search from the root", O, *_b("grep -rn z .")),
    ("the auditor's Grep from the root", A, "Grep", {"pattern": "z"}),
    ("the orchestrator's Glob", O, "Glob", {"pattern": "**/*.py"}),
    ("the test designer's ag", TD, *_b("ag z")),
    ("the test designer's Glob", TD, "Glob", {"pattern": "**/*.py"}),
]


def _check_refused(why, how):
    assert OWN in why, why
    assert HOW[how] in why, why
    assert "DEC-1093 (2)" in why, why


@pytest.mark.parametrize("name,tool,tin,how", REFUSED, ids=[c[0] for c in REFUSED])
def test_decide_refuses_a_search_that_can_reach_the_folder_and_says_how(project, name, tool, tin, how):
    _check_refused(_decide(project, E, tool, tin), how)


@pytest.mark.parametrize("name,tool,tin,how", REFUSED, ids=[c[0] for c in REFUSED])
def test_the_staged_hook_refuses_the_same_and_says_how(rr, project, name, tool, tin, how):
    why = _hook(rr, project, E, tool, tin)
    _check_refused(why, how)
    assert "role_paths.engineer.reads_denied" in why and "DEC-1052 G-14" in why, why


@pytest.mark.parametrize("name,role,tool,tin", ALLOWED, ids=[c[0] for c in ALLOWED])
def test_decide_lets_the_rest_through(project, name, role, tool, tin):
    assert _decide(project, role, tool, tin) == ""


@pytest.mark.parametrize("name,role,tool,tin", ALLOWED, ids=[c[0] for c in ALLOWED])
def test_the_staged_hook_lets_the_rest_through(rr, project, name, role, tool, tin):
    assert _hook(rr, project, role, tool, tin) == ""


def test_a_direct_read_keeps_its_own_refusal(rr, project):
    read = {"file_path": f"{OWN}test_feature.py"}
    assert _decide(project, E, "Read", read) == TESTS_REFUSAL
    assert _decide(project, E, *_b(f"grep -n z {OWN}test_feature.py")) == TESTS_REFUSAL
    assert _decide(project, E, *_b(f"git grep -n z -- {OWN}")) == TESTS_REFUSAL  # a pathspec in it names it
    assert OWN in _hook(rr, project, E, *_b(f"git grep -n z -- {OWN}"))
    assert "role_paths.engineer.reads_denied" in _hook(rr, project, E, "Read", {"file_path": str(project / read[
        "file_path"])})
    assert _decide(project, E, "Read", {"file_path": "tests/acceptance/W2-96/test_other.py"}) == ""


def test_f4_a_glob_start_that_expands_to_the_folder_itself_is_refused(rr, project):
    """grep -rn from tests/acceptance/*: decide says how; the hook expands the glob, so the folder is also named
    directly and either of its reasons may answer."""
    for command, how in (("grep -rn z tests/acceptance/*", "grep"), ("rg z tests/acceptance/*", "rg")):
        _check_refused(_decide(project, E, *_b(command)), how)
        assert OWN in _hook(rr, project, E, *_b(command)), command
    assert _decide(project, E, *_b(f"grep -rn --exclude-dir={W} z tests/acceptance/*")) == ""


def test_a_find_test_naming_a_secret_still_refuses(project):
    from gov.guard.reads import SECRET_REFUSAL
    for role in (E, O):
        assert _decide(project, role, *_b("find . -name .env -exec cat {} +")) == SECRET_REFUSAL, role


def test_the_decide_function_answers_deny_with_the_reason(project):
    decision, why = decide("Grep", {"pattern": "z"}, str(project), E, TICKET, cwd=str(project), flag="absent")
    assert decision == "deny"
    _check_refused(why, "Grep")
    assert decide("Grep", {"pattern": "z", "glob": f"!tests/acceptance/{W}/**"}, str(project), E, TICKET,
                  cwd=str(project), flag="absent") == ("allow", "")


def test_an_empty_or_missing_folder_is_not_reached(rr, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    root = _plant(tmp_path / "bare", files=())
    for tool, tin in (_b("grep -rn z ."), ("Grep", {"pattern": "z"}), ("Glob", {"pattern": "**/*"})):
        assert _decide(root, E, tool, tin) == ""
        assert _hook(rr, root, E, tool, tin) == ""
    (root / OWN).mkdir(parents=True)
    assert _hook(rr, root, E, *_b("grep -rn z .")) == ""


def test_the_hook_judges_the_folder_in_every_tree(rr, tmp_path, monkeypatch):
    """A search from another tree, or from a folder that holds two trees, reaches the folder there too."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    root = _plant(tmp_path / "trees" / "a")
    other = _plant(tmp_path / "trees" / "b")
    trees = lambda: [str(root), str(other)]  # noqa: E731
    _check_refused(_hook(rr, root, E, *_b(f"grep -rn z {other}"), trees=trees), "grep")
    _check_refused(_hook(rr, root, E, "Grep", {"pattern": "z", "path": str(tmp_path / "trees")}, trees=trees),
                   "Grep")
    assert _hook(rr, root, E, *_b(f"grep -rn --exclude-dir={W} z {tmp_path / 'trees'}"), trees=trees) == ""


def test_the_staged_pretooluse_adds_only_glob_to_g14s_tools():
    live = (LIVE / "pretooluse.py").read_text(encoding="utf-8")
    staged = (STAGED / "pretooluse.py").read_text(encoding="utf-8")
    old = 'if tool in ("Read", "NotebookRead", "Grep", "Bash"):'
    assert live.count(old) == 1
    assert staged == live.replace(old, 'if tool in ("Read", "NotebookRead", "Grep", "Glob", "Bash"):')


def test_the_hook_s_block_is_reads_py_s_byte_for_byte():
    def block(path):
        text = path.read_text(encoding="utf-8")
        return text[text.index("# BEGIN W2-141 BLOCK"):text.index("# END W2-141 BLOCK")]
    assert block(STAGED / "role_reads.py") == block(REPO / "src" / "gov" / "guard" / "reads.py")

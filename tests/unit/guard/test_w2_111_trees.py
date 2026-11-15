"""Builder tests for W2-111 (DEC-1184 (3)): a call is judged only against the trees its targets lie in or above,
and every decision is the same as before.

The per-tree judge is the hidden part of one tree (``gov.util.parts._Part`` with the hidden refusal): it is counted
where it is made.  Before W2-111 every registered tree's was made on every call; now a tree's is made only when a
path at, in or above the tree is judged.  Regression evidence only (DEC-136).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gov.guard import reads  # noqa: E402
from gov.util import parts as util_parts  # noqa: E402
from test_w2_111_plant import TICKET, plant  # noqa: E402

H1 = "eval/bench/hidden/q1.txt"
HIDDEN = reads.HIDDEN_REFUSAL


@pytest.fixture(scope="module")
def places(tmp_path_factory):
    return plant(str(tmp_path_factory.mktemp("w2_111_trees")), n=12)


@pytest.fixture()
def judged(places, monkeypatch):
    """judged(tool, input, cwd=P, role) -> (the read rules' answer, the trees whose hidden part was made)."""
    monkeypatch.setenv("HOME", places["H"])
    monkeypatch.chdir(places["P"])
    made: list[str] = []
    real_init = util_parts._Part.__init__

    def counted(self, root, globs, reason, *a, **k):
        if reason == HIDDEN:
            made.append(root)
        real_init(self, root, globs, reason, *a, **k)

    monkeypatch.setattr(util_parts._Part, "__init__", counted)
    runs = os.path.join(places["H"], "gov-os-runs")

    def run(tool, tin, cwd=None, role="engineer"):
        made.clear()
        why = reads.policy_refusal(tool, tin, places["P"], cwd or places["P"], role, TICKET)
        return why, {m for m in made if m != runs}
    return run


def trees_under(places, folder):
    out = reads._trees(places["P"])[0]
    return {t for t in out if t == folder or t.startswith(folder + "/")}


def test_a_read_in_the_project_judges_its_tree_alone(places, judged):
    why, made = judged("Read", {"file_path": os.path.join(places["P"], "README.md")})
    assert why == "" and made == {places["P"]}


def test_a_read_in_another_tree_judges_that_tree_alone(places, judged):
    t = os.path.join(places["TR"], "t003")
    why, made = judged("Read", {"file_path": os.path.join(t, H1)})
    assert why.startswith(HIDDEN) and made == {t}


@pytest.mark.parametrize("command", ["ls", "ls | wc -l"])
def test_a_plain_bash_call_judges_the_tree_it_runs_in_and_the_tree_below_it(places, judged, command):
    why, made = judged("Bash", {"command": command})
    assert why == "" and made == {places["P"], os.path.join(places["P"], ".wt", "n1")}


def test_a_redirect_into_another_tree_judges_no_other_tree(places, judged):
    why, made = judged("Bash", {"command": f"echo x > {places['TR']}/t004/out.txt"})
    assert why == "" and made <= {places["P"]}


def test_a_search_from_above_the_trees_is_refused_by_a_tree_below_it(places, judged):
    why, made = judged("Bash", {"command": f"grep -r x {places['TR']}"})
    assert why.startswith(HIDDEN)
    assert made and made <= trees_under(places, places["TR"])  # the first tree that refuses ends the call


@pytest.mark.parametrize("command", ["grep -r x {TR} --include=*.md", "find {TR} -name '*.md' -exec cat {} +"])
def test_an_allowed_search_from_above_the_trees_judges_every_tree_below_it(places, judged, command):
    why, made = judged("Bash", {"command": command.replace("{TR}", places["TR"])})
    assert why == ""
    below = trees_under(places, places["TR"])
    assert len(below) == 13 and below <= made  # 12, and t900 there through the link
    # find's other words ('*.md', {}, +) are judged from the folder it runs in: the project and its nested tree.
    assert made - below <= {places["P"], os.path.join(places["P"], ".wt", "n1")}


def test_a_search_from_above_that_keeps_the_hidden_out_judges_every_tree_and_allows(places, judged):
    why, made = judged("Grep", {"pattern": "x", "path": places["TR"], "glob": "*.md"})
    assert why == "" and made == trees_under(places, places["TR"])


def test_a_glob_from_above_is_refused_by_a_tree_below_it(places, judged):
    why, made = judged("Bash", {"command": f"cat {places['TR']}/*/{H1}"})
    assert why.startswith(HIDDEN) and made and made <= trees_under(places, places["TR"])


@pytest.mark.parametrize("command", ["ls $X | xargs cat", "cd $X && ls | xargs cat", "cat $(ls $X)",
                                     "while read f; do cat $f; done < list.txt"])
def test_a_listing_from_an_unknown_start_still_refuses(places, judged, command):
    why, _ = judged("Bash", {"command": command})
    assert why == reads.RUNTIME_REFUSAL


def test_a_role_without_a_hidden_part_judges_no_tree(places, judged):
    why, made = judged("Bash", {"command": f"cat {places['TR']}/t003/{H1}"}, role=None)
    assert why == "" and made == set()


# -- the lazy tree part answers as the tree's part made at once ------------------------------------------------------

def paths_about(root, files):
    up = os.path.dirname(root)
    out = [root, root + "/", root + "//", root + "x", root + "x/eval/bench/hidden/q1.txt", up, up + "/", "/", "",
           "eval", os.path.dirname(up), os.path.join(root, "eval"), os.path.join(root, "eval", "bench"),
           os.path.join(root, "eval", "bench", "hidden"), os.path.join(root, "eval", "bench", "hidden") + "/",
           os.path.join(root, "eval", "keys"), os.path.join(root, "eval", "keys", "a.key.txt"),
           os.path.join(root, "eval", "keys", "readme.md"), os.path.join(root, "src"),
           os.path.join(root, "eval", "bench", "hidden", "none", "deeper.txt"),
           os.path.join(up, "t000", H1), os.path.join(root, "..", os.path.basename(root), H1)]
    return out + list(files)


@pytest.mark.parametrize("tree", ["proj", "trees/t003", "trees/t002", "trees/t001", "proj/.wt/n1"])
def test_the_lazy_part_answers_as_the_part_made_at_once(places, tree):
    root = os.path.join(places["B"], tree)
    globs = ["eval/bench/hidden/**", "eval/keys/*.key.txt"]
    eager = util_parts._Part(root, globs, HIDDEN)
    files = eager.files
    for p in paths_about(root, files):
        lazy = reads._TreePart(root, globs, HIDDEN)
        assert lazy.inside(p) == eager.inside(p), p
        assert lazy.under(p) == eager.under(p), p
        assert lazy.below(p) == eager.below(p), p
        assert lazy.rel(p) == eager.rel(p), p
    for rel in [None, "", "eval", "eval/bench/hidden", H1, "eval/keys/a.key.txt", "eval/keys/x", "src/a"]:
        assert reads._TreePart(root, globs, HIDDEN).match(rel) == eager.match(rel), rel
    lazy = reads._TreePart(root, globs, HIDDEN)
    assert (lazy.files, lazy.held(), lazy.strict, lazy.reason, lazy.globs, lazy.base, lazy.root) == (
        eager.files, eager.held(), eager.strict, eager.reason, eager.globs, eager.base, eager.root)
    assert (lazy.lead, lazy.literals) == (eager.lead, eager.literals)
    assert [r[1] for r in lazy.rx] == [r[1] for r in eager.rx]


# -- the listing's real paths: realpath's own answers ----------------------------------------------------------------

def test_the_listing_s_real_paths_are_realpath_s(tmp_path):
    b = tmp_path
    (b / "a" / "b" / "c").mkdir(parents=True)
    (b / "a" / "file").write_text("x")
    (b / "other" / "deep").mkdir(parents=True)
    (b / "lnk").symlink_to(b / "a", target_is_directory=True)              # a linked folder
    (b / "a" / "rel").symlink_to("b", target_is_directory=True)            # a relative link
    (b / "chain").symlink_to(b / "lnk")                                     # a link to a link
    (b / "dangling").symlink_to(b / "nowhere")                              # a link to nothing
    (b / "loop1").symlink_to(b / "loop2")
    (b / "loop2").symlink_to(b / "loop1")                                   # a loop
    (b / "a" / "b" / "up").symlink_to("../..", target_is_directory=True)   # a link up
    names = ["", "a", "a/b", "a/b/c", "a/file", "a/file/x", "lnk", "lnk/b", "lnk/b/c", "lnk/rel/c", "chain",
             "chain/b/c", "dangling", "dangling/x", "loop1", "loop1/x", "a/b/up", "a/b/up/a/b", "missing",
             "missing/x/y", "a/missing/z", "other/deep", "a/./b", "a/../a/b", "a//b", "a/b/", "a/b/../c", "a/b/."]
    paths = [str(b) + ("/" + n if n else "") for n in names]  # as written: a/./b, a//b and a/b/ kept
    paths += ["/", "//", "///x", "relative/path", "", ".", "..", "/tmp", "a"]
    paths += paths[::-1]  # each answered again from what it already resolved
    assert reads._realpaths(paths) == [os.path.realpath(p) for p in paths]


def test_the_listing_names_the_trees_git_names(places):
    out = subprocess.run(["git", "-C", places["P"], "worktree", "list", "--porcelain", "-z"], capture_output=True,
                         text=True, check=True).stdout
    want = [os.path.realpath(f[9:]) for f in out.split("\0") if f.startswith("worktree ")]
    assert reads._worktrees(places["P"], "fault") == want
    assert len(want) == 1 + 12 + 2  # the project, its 12 trees beside it (one gone, one locked), n1 and t900

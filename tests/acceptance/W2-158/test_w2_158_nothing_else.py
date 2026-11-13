"""S5 (bounded and cheap; reads and writes nothing else) and F4 (no change outside the ticket's paths).

S5's filesystem spy snapshots every file (path, size, mtime) under the planted tree, ``.git/`` included, and under the
planted HOME, before and after a run with a base and links; only ``.gov-runtime/links/mark`` (links' own mark) may be new.
The stand-ins' own records are in a folder outside both. The index must not be rewritten (L9: no optional lock), which the
case provokes: a tracked file's mtime is moved on, so a ``git status`` taking the optional lock would refresh and rewrite
the index.
"""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess

import pytest

import w2_158_support as support
from w2_158_support import ROOT, snapshot

TICKET = ROOT / ".tickets" / "DAEO-8a3f.md"
ACCEPTANCE = "tests/acceptance/W2-158/"
PROBES = "docs/probes/DAEO-8a3f/"
OWN_BRANCHES = ("w2/W2-158", "w2/W2-158-tests")


def plant_with_base_and_links(tree) -> str:
    """Eight families and portability (quick markers), the tree's own stand-in links, a base commit and a kernel change."""
    tree.declare_all("ok", delay=0.3)
    tree.declare_family("portability", "ok", delay=0.3)
    tree.plant_links("clean")
    base = tree.commit("the base")
    tree.commit("kernel", files={"template/governance/kernel/skills/x/SKILL.md": "a\n"})
    return base


def stat_dirty(tree) -> None:
    """Move a tracked file's mtime on (same content), so the index's stat data for it is stale."""
    path = tree.tree / "README.md"
    later = path.stat().st_mtime_ns + 7_000_000_000
    os.utime(path, ns=(later, later))


def test_s5_a_pass_with_a_base_and_links_writes_only_links_mark_and_leaves_the_index_alone(tree):
    """Every file under the planted tree (``.git`` included) and the planted HOME, before and after a pass that ran all
    eight families, portability and the tree's own links: the only new file is ``.gov-runtime/links/mark`` (and the two
    folders holding it); nothing changed (the index, the declarations, the sources: no ``__pycache__``, no log, no cache,
    no lock file either) and nothing under the HOME."""
    base = plant_with_base_and_links(tree)
    stat_dirty(tree)
    before = snapshot(tree.tree, tree.home)
    index_before = (tree.tree / ".git" / "index").read_bytes()
    outcome = tree.structural(base)
    lines = support.assert_shape(outcome, tree)
    assert lines[-3].startswith("portability: ok") and lines[-2].startswith("links: ok"), lines   # all of it ran
    after = snapshot(tree.tree, tree.home)
    mark = str(tree.tree / ".gov-runtime" / "links" / "mark")
    new = {path for path in set(after) - set(before) if not path.endswith("/")}
    folders = {path for path in set(after) - set(before) if path.endswith("/")}
    changed = {path for path, value in before.items() if after.get(path) != value}
    assert new == {mark}, f"files written other than links' mark: {sorted(new - {mark})}"
    assert not changed, f"files changed: {sorted(changed)}"
    assert folders <= {str(tree.tree / ".gov-runtime") + "/", str(tree.tree / ".gov-runtime" / "links") + "/"}, (
        f"folders made: {sorted(folders)}")
    assert (tree.tree / ".git" / "index").read_bytes() == index_before, "the git index was rewritten"
    assert not list((tree.tree).rglob("__pycache__")), "a __pycache__ was written in the tree"
    assert tree.home.exists() and not any(tree.home.iterdir()), f"something was written under HOME: {list(tree.home.iterdir())}"


def test_s5_a_pass_without_a_base_writes_nothing_at_all(tree):
    """No ``<base>``: no links, no mark; no file new or changed under the planted tree or HOME (the index included)."""
    tree.declare_all("ok", delay=0.3)
    tree.plant_links("clean")
    tree.commit("the base")
    stat_dirty(tree)
    before = snapshot(tree.tree, tree.home)
    outcome = tree.structural()
    support.assert_shape(outcome, tree)
    after = snapshot(tree.tree, tree.home)
    assert set(after) == set(before), f"new or removed: {sorted(set(after) ^ set(before))}"
    assert after == before, f"changed: {sorted(p for p in before if before[p] != after[p])}"


# --- S5: the time on this repository ---------------------------------------------------------------------------------------

def test_s5_real_pass_on_this_tree_is_bounded(tree):
    """``gov check --structural HEAD~1`` with ``--root`` this repository's tree (the tree this suite sits in), the default
    bound: exits 0 and ends within the bound plus 10 seconds (60 s), the usual eleven lines, the last at this tree's HEAD.
    Named with ``real``: the whole-folder filter leaves it out, ``gov accept`` runs it. The environment is this machine's
    PATH (the declared checks may need programs on it), HOME planted."""
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], env=tree.git_env(), capture_output=True, text=True,
                          timeout=60).stdout.strip()
    assert head, "this tree has no HEAD"
    env = tree.env(PATH=os.environ.get("PATH", support.SAFE_PATH))
    outcome = tree.gov("check", "--structural", "HEAD~1", "--root", str(ROOT), env=env, timeout=150)
    lines = outcome.lines()
    assert len(lines) == len(support.OUTPUT_ORDER) + 1, outcome.text()
    assert lines[-1].startswith(f"structural pass at {head[:12]}"), lines[-1]
    assert outcome.elapsed <= 50 + 10, f"the pass took {outcome.elapsed:.1f} s (limit: bound 50 s + 10 s)"
    print(f"W2-158 S5 measured: {outcome.elapsed:.1f} s on this tree\n{outcome.out}")


# --- F4 ---------------------------------------------------------------------------------------------------------------

def allowed_paths() -> list[str]:
    """The ticket's ``allowed_paths`` (the list in its front matter), without their comments."""
    lines = TICKET.read_text().splitlines()
    found = []
    for line in lines[lines.index("allowed_paths:") + 1:]:
        match = re.match(r"^- (\S+)", line)
        if not match:
            break
        found.append(match.group(1))
    return found


def test_f4_the_branch_changes_only_the_tickets_allowed_paths(tmp_path):
    """``git diff --name-only <merge-base with w2/integrate>...HEAD`` lists only paths matched by the ticket's
    ``allowed_paths``, under ``tests/acceptance/W2-158/`` or under ``docs/probes/DAEO-8a3f/``.

    It judges only this ticket's own branch: when the current branch (``git rev-parse --abbrev-ref HEAD``) is neither
    ``w2/W2-158`` nor ``w2/W2-158-tests`` it skips, naming why (DECIDED-NOT-DONE row 171: otherwise the next ticket in the
    area and the merge queue's batches go red on it). On either branch it is green only when the branch is clean, and it
    fails, naming the gap, where ``w2/integrate`` does not resolve."""
    env = {"PATH": support.SAFE_PATH, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "LC_ALL": "C",
           "HOME": str(tmp_path)}

    def git(*args):
        return subprocess.run(["git", "-C", str(ROOT), *args], env=env, capture_output=True, text=True, timeout=60)

    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch not in OWN_BRANCHES:
        pytest.skip(f"the current branch is {branch!r}, not this ticket's own branch ({' or '.join(OWN_BRANCHES)}): "
                    "F4 judges only that branch's diff (DECIDED-NOT-DONE row 171)")
    base = git("merge-base", "HEAD", "w2/integrate")
    assert base.returncode == 0 and base.stdout.strip(), f"w2/integrate does not resolve: {base.stderr}"
    diff = git("diff", "--name-only", f"{base.stdout.strip()}...HEAD")
    assert diff.returncode == 0, f"git diff failed: {diff.stderr}"
    patterns = allowed_paths()
    assert patterns, f"no allowed_paths read from {TICKET}"
    outside = [path for path in diff.stdout.splitlines()
               if not path.startswith((ACCEPTANCE, PROBES)) and not any(fnmatch.fnmatch(path, pattern) for pattern in patterns)]
    assert not outside, f"changed paths not matched by the ticket's allowed_paths {patterns}: {outside}"

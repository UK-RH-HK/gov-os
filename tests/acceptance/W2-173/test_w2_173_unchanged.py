"""S5 and failure lines 3-4: nothing else about the launch script changes, and the ticket's branch touches only its own
paths (DEC-1112 (3), DEC-1113).

S5's main check is W2-149's own acceptance cases, run unchanged by ``gov accept W2-149``; a diff of the script's text
outside the four changes is the reviewer's, never a test here. What this file adds:
- set-up A's flows keep their stop rule: a set-up A result with a stopped word still ends 20 (W2-149 S29), never S2's 21;
- failure line 3: the branch's ``git diff --name-only <base>...HEAD`` names none of the walls' template files, the path
  map, the guard, an approved list or a set-up A brief;
- failure line 4: it names only paths the ticket's ``allowed_paths`` match, plus ``tests/acceptance/W2-173/**``.

Readings: failure lines 3 and 4 are judged only on W2-173's own branch, ``w2/W2-173`` (HEAD's full ref
``refs/heads/w2/W2-173``, read from the repository this file sits in, never from the current directory or an
environment variable). On any other checkout they are skipped with their reason named, never red and never passed
silently: another ticket's branch (its own paths are not W2-173's), the merge queue's candidate merge (a detached HEAD),
``w2/integrate`` itself, a clone's checkout. The judgements are ``judge_f3_paths(root)`` and ``judge_f4_paths(root)``:
the real cases call them with the repository this file sits in, the planted cases (each in its own ``git init``
repository under ``tmp_path``) call the same functions (revision of W2-180, DAEO-weh2). The base is the merge-base of HEAD with ``w2/integrate`` (``dac438772``, the ticket's claim commit, when no
merge-base is found); the ticket's own process records that ride a ticket's branch (its ticket file
``.tickets/DAEO-qz4p.md``, ``docs/checkpoints/DAEO-qz4p/**``, ``docs/probes/DAEO-qz4p/**``) count as its own paths
(W1-01's reading: a commit may touch its ticket's own file); "the guard" is ``src/gov/guard/**``, ``.claude/hooks/**``
and ``template/governance/kernel/hooks/**``; "an approved list" is any file named ``APPROVED``.
"""

from __future__ import annotations

import fnmatch
import os
import subprocess
from pathlib import Path

import pytest
import yaml

import w2_173_support as s
from w2_173_support import sa, support

FORBIDDEN = ("governance/project/indep-walls/*", "governance/project/path-map.yaml", "src/gov/guard/*",
             ".claude/hooks/*", "template/governance/kernel/hooks/*", "governance/project/indep-briefs/sgx1/*",
             "*/APPROVED", "APPROVED")
OWN_RECORDS = (f".tickets/{s.TICKET_ID}.md", f"docs/checkpoints/{s.TICKET_ID}/*", f"docs/probes/{s.TICKET_ID}/*")


# -- S5: set-up A's stop rule unchanged ------------------------------------------------------------------------------

def test_s5_a_set_up_a_result_with_a_stopped_word_still_ends_20_not_21(world):
    """Green today (W2-149 S29): writer 1's result says it stopped; nothing lands in the half's folder; the code is 20."""
    out = sa.stopped_out(sa.writer_out("writer-tuning"), sa.STOP_WORD["writer-tuning"])
    run = sa.deliver(world, "writer-tuning", "tuning", out=out)
    assert run.code == 20, run.why()
    assert run.line["status"] == "rejected" and run.line["reason"] == "result", run.line
    assert not (world.half("tuning") / "planted" / "cases.jsonl").exists(), "writer 1's cases landed"


# -- failure lines 3 and 4: the branch's names, judged only on W2-173's own branch -----------------------------------

OWN_BRANCH = "w2/W2-173"


def branch_names(root):
    try:
        base = support.git(root, "merge-base", "HEAD", "w2/integrate").strip()
    except RuntimeError:
        base = support.git(root, "rev-parse", "--verify", s.BASE_FALLBACK + "^{commit}").strip()
    names = [x for x in support.git(root, "diff", "--name-only", "--no-renames", f"{base}...HEAD").splitlines()
             if x.strip()]
    return base, names


def ticket_allowed_paths(root):
    text = (Path(root) / ".tickets" / f"{s.TICKET_ID}.md").read_text()
    front = yaml.safe_load(text.split("\n---", 1)[0].lstrip("-\n"))
    paths = front.get("allowed_paths")
    assert isinstance(paths, list) and paths, "the ticket names no allowed_paths"
    return paths


def matched(path, globs):
    return any(fnmatch.fnmatch(path, g) for g in globs)


def _skip_unless_own_branch(root, line):
    """Skip (with the reason named) unless HEAD of ``root`` is the branch ``w2/W2-173`` (its full ref)."""
    try:
        ref = support.git(root, "symbolic-ref", "-q", "HEAD").strip()
    except RuntimeError:
        ref = ""
    if not ref.startswith("refs/heads/"):
        pytest.skip(f"{line} judges only the branch {OWN_BRANCH}; this is a detached HEAD: not judged here")
    branch = ref.removeprefix("refs/heads/")
    if branch != OWN_BRANCH:
        pytest.skip(f"{line} judges only the branch {OWN_BRANCH}; this is the branch {branch}: not judged here")


def judge_f3_paths(root):
    """Failure line 3 on ``root``'s checkout: skipped unless HEAD is ``w2/W2-173``; there, no controlled file changed."""
    _skip_unless_own_branch(root, "F3")
    base, names = branch_names(root)
    hit = [n for n in names if matched(n, FORBIDDEN)]
    assert hit == [], f"the branch (against {base[:12]}) changes controlled files: {hit}"


def judge_f4_paths(root):
    """Failure line 4 on ``root``'s checkout: skipped unless HEAD is ``w2/W2-173``; there, only the ticket's paths."""
    _skip_unless_own_branch(root, "F4")
    base, names = branch_names(root)
    allowed = ticket_allowed_paths(root) + [f"tests/acceptance/{s.W2}/**"] + list(OWN_RECORDS)
    outside = [n for n in names if not matched(n, allowed)]
    assert outside == [], f"the branch (against {base[:12]}) changes paths outside the ticket's: {outside}"


def test_f3_the_branch_changes_no_template_path_map_guard_approved_list_or_set_up_a_brief():
    judge_f3_paths(support.TREE)


def test_f4_the_branch_changes_only_the_ticket_s_paths():
    judge_f4_paths(support.TREE)


# -- the planted cases: each in its own repository under tmp_path, judged by the same functions --------------------

JUDGES = {"f3": judge_f3_paths, "f4": judge_f4_paths}
TICKET_FILE = support.TREE / ".tickets" / f"{s.TICKET_ID}.md"
OUTSIDE = "docs/changes/W2-178-evidence.md"                        # not W2-173's (W2-178's own evidence file); no F3 glob
FORBIDDEN_PATH = "governance/project/path-map.yaml"               # F3's path map (also outside W2-173's paths)
INSIDE = "governance/project/orchestration/tools/indep_launch.py"  # W2-173's own script (an allowed path)


def _plant(tmp_path: Path, *, branch: str, path: str, detach_merge: bool = False) -> Path:
    """A ``git init`` repository: ``w2/integrate`` holds a base commit and W2-173's ticket file (copied from this
    tree); ``branch`` (``w2/integrate`` itself, or a branch off it) holds one more commit adding ``path``. With
    ``detach_merge``: the branch is made, then HEAD is detached at ``w2/integrate`` and ``branch`` merged with
    ``--no-ff`` (the merge queue's candidate merge). Nothing of the true home's git config is read; a planting
    failure raises."""
    if not TICKET_FILE.is_file():
        pytest.skip(f"the planted cases copy the ticket file .tickets/{s.TICKET_ID}.md, absent here: not judged here")
    home = tmp_path / "home"
    home.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    ident = ["-c", "user.name=Planted", "-c", "user.email=planted@example.invalid", "-c", "commit.gpgsign=false",
             "-c", "core.hooksPath=/dev/null"]

    def git(*args):
        done = subprocess.run(["git", "-C", str(repo), *ident, *args], capture_output=True, text=True, env=env,
                              timeout=60)
        if done.returncode != 0:
            raise AssertionError(f"planting failed: git {' '.join(args)}: {done.stderr}")
        return done.stdout

    git("init", "-q")
    git("checkout", "-q", "-b", "w2/integrate")
    (repo / ".tickets").mkdir()
    (repo / ".tickets" / TICKET_FILE.name).write_text(TICKET_FILE.read_text(), encoding="utf-8")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    if branch != "w2/integrate":
        git("checkout", "-q", "-b", branch)
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text("changed\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", f"adds {path}")
    if detach_merge:
        git("checkout", "-q", "--detach", "w2/integrate")
        git("merge", "-q", "--no-ff", "-m", "candidate merge", branch)
    return repo


def _skipped(judge, repo: Path) -> str:
    with pytest.raises(pytest.skip.Exception) as info:
        judge(repo)
    return info.value.msg


def test_planted_paths_are_outside_the_ticket_s_paths_and_inside_it_as_each_case_needs():
    allowed = ticket_allowed_paths(support.TREE) + [f"tests/acceptance/{s.W2}/**"] + list(OWN_RECORDS)
    assert not matched(OUTSIDE, allowed) and not matched(OUTSIDE, FORBIDDEN), OUTSIDE
    assert not matched(FORBIDDEN_PATH, allowed) and matched(FORBIDDEN_PATH, FORBIDDEN), FORBIDDEN_PATH
    assert matched(INSIDE, allowed) and not matched(INSIDE, FORBIDDEN), INSIDE


def test_f4_planted_w2_173_branch_with_a_change_outside_its_paths_fails_naming_it(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-173", path=OUTSIDE)
    with pytest.raises(AssertionError) as info:
        judge_f4_paths(repo)
    assert OUTSIDE in str(info.value)


def test_f3_planted_w2_173_branch_with_a_change_outside_its_paths_but_no_forbidden_one_passes(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-173", path=OUTSIDE)
    judge_f3_paths(repo)


def test_f3_planted_w2_173_branch_with_a_forbidden_path_fails_naming_it(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-173", path=FORBIDDEN_PATH)
    with pytest.raises(AssertionError) as info:
        judge_f3_paths(repo)
    assert FORBIDDEN_PATH in str(info.value)


@pytest.mark.parametrize("line", sorted(JUDGES))
def test_planted_w2_173_branch_with_a_change_inside_its_paths_passes(tmp_path, line):
    repo = _plant(tmp_path, branch="w2/W2-173", path=INSIDE)
    JUDGES[line](repo)


@pytest.mark.parametrize("line", sorted(JUDGES))
def test_planted_other_ticket_branch_with_the_same_change_is_skipped_with_its_reason(tmp_path, line):
    repo = _plant(tmp_path, branch="w2/W2-178", path=OUTSIDE)
    reason = _skipped(JUDGES[line], repo)
    assert "w2/W2-178" in reason and "w2/W2-173" in reason, reason


@pytest.mark.parametrize("line", sorted(JUDGES))
def test_planted_other_ticket_branch_with_a_forbidden_path_is_skipped_with_its_reason(tmp_path, line):
    repo = _plant(tmp_path, branch="w2/W2-178", path=FORBIDDEN_PATH)
    reason = _skipped(JUDGES[line], repo)
    assert "w2/W2-178" in reason, reason


@pytest.mark.parametrize("line", sorted(JUDGES))
def test_planted_candidate_merge_on_a_detached_head_is_skipped_with_its_reason(tmp_path, line):
    repo = _plant(tmp_path, branch="w2/W2-178", path=OUTSIDE, detach_merge=True)
    head = subprocess.run(["git", "-C", str(repo), "symbolic-ref", "-q", "HEAD"], capture_output=True, text=True)
    assert head.returncode != 0, "the planted candidate merge must stand on a detached HEAD"
    merged = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%p"], capture_output=True, text=True)
    assert len(merged.stdout.split()) == 2, "the planted candidate merge must be a merge commit"
    reason = _skipped(JUDGES[line], repo)
    assert "detached HEAD" in reason, reason


@pytest.mark.parametrize("line", sorted(JUDGES))
def test_planted_integrate_branch_itself_is_skipped_with_its_reason(tmp_path, line):
    repo = _plant(tmp_path, branch="w2/integrate", path=OUTSIDE)
    reason = _skipped(JUDGES[line], repo)
    assert "this is the branch w2/integrate" in reason, reason

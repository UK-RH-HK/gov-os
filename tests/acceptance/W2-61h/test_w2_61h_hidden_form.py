"""W2-61h (DAEO-h2k3): the hidden 40 (DEC-1069 (4)), checked for form only -- KPI lines S1, S3 (as DEC-1069 (5)
amends it), S4, S5, S6, F1, F2 and F3.

S5: "The hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree,
run clone, store or commit; no question or answer quoted in a commit message, a return, a log or a ticket note".
S6: "... its form is checked by tests that report counts and pass or fail only, never its contents".
F1: "A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work."

The sets root comes from ``GOV_EVAL_SETS_ROOT`` (``$HOME/gov-os-eval``). Absent, every case here skips, so an
ordinary run never touches it; a session of a measured role (the path map's ``measures.roles``) skips them too.
Every failure goes through ``_fail``, untraced, and names a question by its file name only: never a question, an
answer, a category or a gold path (DEC-820 (d)). Nothing here prints or writes what it reads.
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61h_support as s  # noqa: E402


def _fail(message: str):
    pytest.fail(message, pytrace=False)


@pytest.fixture(scope="module")
def sets_root() -> Path:
    value = os.environ.get(s.SETS_ROOT_VAR)
    if not value:
        pytest.skip(f"{s.SETS_ROOT_VAR} is not set: the hidden half is held outside every tree (G-3), never read "
                    "by an ordinary run")
    if os.environ.get("GOV_ROLE", "") in s.measured_roles():
        pytest.skip("a session of a role the set measures never reads the hidden half (DEC-820 (d))")
    root = Path(value).expanduser().resolve()
    if not (root / s.HIDDEN_REL).is_dir():
        _fail(f"{s.SETS_ROOT_VAR} names no sets root with the set's hidden folder")
    return root


@pytest.fixture(scope="module")
def hidden(sets_root):
    """The hidden files by name, each loaded (None when not a YAML map); loading never raises or prints."""
    files = sorted((sets_root / s.HIDDEN_REL).glob("*.yaml"))
    return {f.name: s.load(f) for f in files}


def _maps(hidden):
    """The hidden files that load as maps (the form case names the others)."""
    return {name: data for name, data in hidden.items() if data is not None}


def _guarded(check):
    """Run a check; any error becomes a failure that names its type only (an error text may quote a file)."""
    try:
        return check()
    except pytest.fail.Exception:
        raise
    except Exception as error:  # noqa: BLE001
        _fail(f"the check stopped on an error: {type(error).__name__}")


def test_s1_the_hidden_half_holds_40_question_files(sets_root):
    """DEC-1069 (4): the hidden half holds 40 question files (W2-61h's 24 and the operator's 16) and nothing else."""
    folder = sets_root / s.HIDDEN_REL
    count = len(list(folder.glob("*.yaml")))
    others = len([p for p in folder.iterdir() if p.suffix != ".yaml"])
    if count != s.HIDDEN_COUNT or others:
        _fail(f"the hidden folder holds {count} question files (want {s.HIDDEN_COUNT}) and {others} other entries")


def test_s1_every_hidden_question_is_in_the_question_form(hidden):
    """Each hidden file is in the measure's question form, with a category of R5's twelve (DEC-1069 (5)); ids are
    distinct across the hidden 40 and the visible 40; each names a commit of this repository, its own or one on every
    source (R10 item 2; a per-source ``commit`` is the operator's form), and every commit it names exists."""
    def check():
        faults = [f"{name}: {', '.join(found)}" for name, data in hidden.items()
                  if (found := s.form_faults(data, set(s.R5_QUOTAS), "R5's twelve"))]
        if faults:
            _fail("hidden files not in the question form:\n" + "\n".join(faults))
        ids = Counter(str(data.get("id") or Path(name).stem) for name, data in _maps(hidden).items())
        visible = {str((s.load(f) or {}).get("id") or f.stem) for f in s.VISIBLE.glob("*.yaml")}
        clash = sorted(name for name, data in hidden.items()
                       if ids[str(data.get("id") or Path(name).stem)] > 1
                       or str(data.get("id") or Path(name).stem) in visible)
        if clash:
            _fail(f"hidden files whose id is not distinct across the set: {clash}")
        no_commit = [f"{name}: {', '.join(found)}" for name, data in sorted(hidden.items())
                     if (found := s.commit_faults(data))]
        if no_commit:
            _fail("hidden files whose commit is not one of this repository's:\n" + "\n".join(no_commit))
    _guarded(check)


def test_s3_the_hidden_40_spread_as_r5_s_quotas_state(hidden):
    """The hidden 40 alone (R5 item 6: the quotas apply in full to a half written wholly in W2-61h's form): R5's
    twelve categories, each at least its quota, save the owner's accepted shortfall of one in decision, callers and
    code-paraphrase (``R5_SHORT``) and no other; each multi-file question needs two or more files (two source entries
    or more, on two paths or more). Only counts per category are shown."""
    def check():
        every = {f"hidden {n}": d for n, d in _maps(hidden).items()}
        counted = Counter((d or {}).get("category") if (d or {}).get("category") in s.R5_QUOTAS else "outside R5"
                          for d in every.values())
        short = {name: want - s.R5_SHORT.get(name, 0) for name, want in s.R5_QUOTAS.items()}
        if any(counted.get(name, 0) < floor for name, floor in short.items()) or counted.get("outside R5"):
            lines = [f"{name}: {counted.get(name, 0)} (R5: at least {want}"
                     + (f", {short[name]} with the accepted shortfall)" if short[name] != want else ")")
                     for name, want in s.R5_QUOTAS.items()]
            if counted.get("outside R5"):
                lines.append(f"outside R5's twelve: {counted['outside R5']}")
            _fail("the hidden 40's spread is not R5's:\n" + "\n".join(lines))
        single = []
        for name, data in every.items():
            if data.get("category") != "multi-file":
                continue
            found = s.entries(data) or []
            if len(found) < 2 or len({a["path"] for e in found for a in e}) < 2:
                single.append(name)
        if single:
            _fail(f"multi-file questions that need fewer than two files: {sorted(single)}")
    _guarded(check)


def test_s4_f3_every_hidden_gold_source_resolves_at_head(hidden):
    """Each gold source is a file of this repository at HEAD, outside the evaluation files; a heading given is a
    line of it or the stated lines are a span of it; a source cited by lines alone holds the same lines at HEAD as at
    the question's commit. Faults name the file and the entry's number only."""
    def check():
        faults = [f"{name}: source entry {n}: {why}" for name, data in _maps(hidden).items()
                  for n, why in s.source_faults(data)]
        if faults:
            _fail(f"{len(faults)} hidden gold sources do not resolve at HEAD:\n" + "\n".join(faults))
    _guarded(check)


def test_f2_no_hidden_question_repeats_a_visible_one(hidden):
    """No hidden question is, case, spacing and punctuation aside, one of the visible half (lens B's 20, q21-q24 and
    q25-q40) or another hidden one. A paraphrase is judged from the record (the README)."""
    def check():
        visible = {s.normalised((s.load(f) or {}).get("question", "")) for f in s.VISIBLE.glob("*.yaml")}
        seen, repeats = set(), []
        for name, data in _maps(hidden).items():
            text = s.normalised(data.get("question", ""))
            if text in visible or text in seen:
                repeats.append(name)
            seen.add(text)
        if repeats:
            _fail(f"hidden files that repeat another question: {repeats}")
    _guarded(check)


def test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root(sets_root):
    """The sets root is outside every worktree of this repository and in no git work tree, its mode lets no group or
    other in; no worktree and no run clone holds a hidden question file of the set; no hidden file is an object of
    this repository's store (every branch, tag, stash and worktree shares it) or of a run clone's."""
    def check():
        faults = []
        trees = s.worktrees()
        if not trees:
            faults.append("git lists no worktree")
        inside = [str(t) for t in trees if sets_root == t.resolve() or t.resolve() in sets_root.parents]
        if inside:
            faults.append(f"the sets root is inside a worktree: {inside}")
        done = subprocess.run(["git", "-C", str(sets_root / s.HIDDEN_REL), "rev-parse", "--is-inside-work-tree"],
                              capture_output=True, text=True, timeout=s.TIMEOUT_S)
        if done.returncode == 0:
            faults.append("the hidden folder is inside a git work tree")
        mode = stat.S_IMODE(sets_root.stat().st_mode)
        if mode & 0o077:
            faults.append(f"the sets root's mode is {mode:o}, not 700")
        ids = [s.blob_id(p.read_bytes()) for p in sorted((sets_root / s.HIDDEN_REL).glob("*.yaml"))]
        held = [str(t) for t in trees if list((t / s.HIDDEN_REL).glob("*.yaml"))]
        if held:
            faults.append(f"worktrees that hold the set's hidden question files: {held}")
        missing = s.missing_objects(s.REPO_ROOT, ids)
        if missing != len(ids):
            faults.append(f"this repository's object store holds {len(ids) - (missing or 0)} of the {len(ids)} "
                          "hidden files" if missing is not None else "this repository's object store cannot be asked")
        runs = s.real_home() / "gov-os-runs"
        clones = sorted({p.parent for pattern in ("*/.git", "*/*/.git", "*/*/*/.git") for p in runs.glob(pattern)})
        for clone in clones:
            if list((clone / s.HIDDEN_REL).glob("*.yaml")):
                faults.append(f"a run clone holds the set's hidden question files: {clone}")
            gone = s.missing_objects(clone, ids)
            if gone is not None and gone != len(ids):
                faults.append(f"a run clone's object store holds {len(ids) - gone} hidden files: {clone}")
        if faults:
            _fail("\n".join(faults))
    _guarded(check)


def test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure(sets_root):
    """The sets root's path map declares the set, its hidden globs cover the hidden folder and it measures at least
    the roles this tree's path map names; the measure, run with ``--sets-root`` as each measured role, is refused the
    hidden part (exit 1, a refusal) before it asks any retriever (``--gov`` names none). Only the exit code and
    whether a refusal was given are shown."""
    def check():
        entry = (yaml.safe_load((sets_root / s.PATH_MAP_REL).read_text(encoding="utf-8")) or {}).get(
            "evaluation_sets", {}).get(s.SET) or {}
        roles = set((entry.get("measures") or {}).get("roles") or [])
        if not set(s.measured_roles()) <= roles:
            _fail("the sets root's path map measures fewer roles than this tree's")
        if not any(glob.rstrip("*/") == s.HIDDEN_REL for glob in entry.get("hidden") or []):
            _fail("the sets root's path map does not declare the hidden folder as the set's hidden part")
        for role in sorted(s.measured_roles()):
            env = {k: v for k, v in os.environ.items() if k not in ("GOV_TICKET",)}
            env["GOV_ROLE"] = role
            done = subprocess.run([sys.executable, "-m", "gov.retrieval.measure", s.SET, "--root", str(s.REPO_ROOT),
                                   "--sets-root", str(sets_root), "--part", "hidden", "--gov", "/nonexistent/gov"],
                                  cwd=s.REPO_ROOT, env=env, capture_output=True, text=True, timeout=s.TIMEOUT_S)
            if done.returncode != 1 or "refused" not in done.stderr or done.stdout:
                _fail(f"the measure run as {role} on the hidden part: exit {done.returncode}, "
                      f"refused {'refused' in done.stderr}, output {bool(done.stdout)}")
    _guarded(check)

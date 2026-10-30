"""KPI success 2 and failure 2: ``gov rebuild`` recreates derived state.

Success: rebuild recreates every derived store; two rebuilds give the same
digest; a fresh clone plus doctor plus rebuild works [CAP-07.a, CAP-20.a,
CAP-46.a].

Failure: rebuild needs anything not in git.

Revised after implementation: rebuild goes through the lexical index's owner
and its secrets filter (DEC-440); the fixture's size, not the behaviour,
made it time out.  Every case now uses a tiny project (~3 tracked files,
~2–3 s per rebuild) with ``run_gov_with_code`` for the code root.
"""

from __future__ import annotations

import shutil

import w1_27_support as support
import w2_67_doctor
import w2_67b_support


# --------------------------------------------------------------------------
# Command identity
# --------------------------------------------------------------------------

def test_rebuild_is_an_act_command(sandbox, tmp_path):
    """``rebuild`` is an act command (DEC-317): it returns an envelope and may change derived state.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion does not read what
    the case's name claims): it accepted any envelope, REBUILD_FAILED
    included.  The rebuild must now succeed, write its store under
    ``.gov-runtime/``, and change nothing else in the project.
    """
    project = w2_67b_support.rebuild_project(tmp_path / "repo")
    before = support.snapshot(project, skip=(".git", ".gov-runtime"))
    run, _ = w2_67b_support.rebuild(project, sandbox)
    assert (project / ".gov-runtime" / "store.db").is_file(), f"rebuild wrote no store\n{run.describe()}"
    changed = support.snapshot_difference(before, support.snapshot(project, skip=(".git", ".gov-runtime")))
    assert not changed, "rebuild changed the project outside .gov-runtime:\n" + "\n".join(changed) + \
        f"\n{run.describe()}"


# --------------------------------------------------------------------------
# KPI success 2: rebuild guarantees
# --------------------------------------------------------------------------

def test_rebuild_recreates_derived_stores(sandbox, tmp_path):
    """After rebuild, the derived stores under ``.gov-runtime/`` exist.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion does not read what
    the case's name claims): it checked that ``.gov-runtime`` exists only.
    The store is now removed after a first rebuild, and the second must
    recreate it: its lexical index holds the project's document, and the
    result names the lexical store recreated.
    """
    project = w2_67b_support.rebuild_project(tmp_path / "repo")
    w2_67b_support.write_committed(project, "docs/guide.md", "a document the lexical index holds\n")
    w2_67b_support.rebuild(project, sandbox)
    shutil.rmtree(project / ".gov-runtime", ignore_errors=True)
    run, result = w2_67b_support.rebuild(project, sandbox)
    assert (result.get("stores") or {}).get("lexical", {}).get("status") == "recreated", (
        f"the result does not name the lexical store recreated\n{run.describe()}"
    )
    assert (project / ".gov-runtime" / "store.db").is_file(), f"rebuild did not recreate the store\n{run.describe()}"
    indexed = {row[0] for row in w2_67b_support.store_rows(project, "SELECT path FROM lexical_file")}
    assert "docs/guide.md" in indexed, (
        f"the recreated lexical index does not hold docs/guide.md: {sorted(indexed)}\n{run.describe()}"
    )


def test_two_rebuilds_give_the_same_digest(rebuild_gov, rebuild_project, interface):
    """The rebuild is idempotent: two consecutive rebuilds produce the same digest (CAP-20.a).

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.
    """
    run1 = rebuild_gov("rebuild", "--json")
    env1 = support.assert_envelope(run1, interface, command="rebuild")
    assert env1["ok"] is True, f"first rebuild failed\n{run1.describe()}"

    run2 = rebuild_gov("rebuild", "--json")
    env2 = support.assert_envelope(run2, interface, command="rebuild")
    assert env2["ok"] is True, f"second rebuild failed\n{run2.describe()}"

    result1 = env1.get("result", {})
    result2 = env2.get("result", {})
    digest1 = result1.get("digest") if isinstance(result1, dict) else None
    digest2 = result2.get("digest") if isinstance(result2, dict) else None
    assert digest1 is not None, f"first rebuild has no digest in result\n{run1.describe()}"
    assert digest2 is not None, f"second rebuild has no digest in result\n{run2.describe()}"
    assert digest1 == digest2, (
        f"two rebuilds give different digests: {digest1} vs {digest2}\n"
        f"run 1:\n{run1.describe()}\nrun 2:\n{run2.describe()}"
    )


def test_fresh_clone_doctor_rebuild(tmp_path):
    """A fresh clone followed by doctor followed by rebuild works (CAP-46.a).

    The sequence is: create a tiny project (simulating a fresh clone), run
    ``gov doctor --json``, then run ``gov rebuild --json``. Both must succeed.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion does not read what
    the case's name claims): it made no clone and did not read doctor's
    verdict.  The tiny project is now committed and cloned with git; doctor
    in the clone reports its sections, with no index yet; rebuild succeeds;
    and doctor then reports the clone's index fresh.
    """
    origin = w2_67b_support.rebuild_project(tmp_path / "origin")
    w2_67b_support.write_committed(origin, "docs/guide.md", "a document of the project\n")
    clone = tmp_path / "clone"
    support.git(tmp_path, "clone", "-q", str(origin), str(clone))
    sandbox = support.make_sandbox(tmp_path / "sandbox")

    first = w2_67_doctor.doctor(clone, sandbox)
    freshness = w2_67_doctor.section(first, "index_freshness")
    assert freshness.get("index_status") != "fresh", (
        f"doctor in a fresh clone reports an index no rebuild has built: {freshness}\n{first.describe()}"
    )
    w2_67b_support.rebuild(clone, sandbox)
    second = w2_67_doctor.doctor(clone, sandbox)
    freshness = w2_67_doctor.section(second, "index_freshness")
    assert (freshness.get("index_status"), freshness.get("status")) == ("fresh", "pass"), (
        f"doctor does not report the clone's index fresh after the rebuild: {freshness}\n{second.describe()}"
    )


# --------------------------------------------------------------------------
# Failure KPI 2: rebuild needs anything not in git
# --------------------------------------------------------------------------

def test_rebuild_needs_only_git(sandbox, tmp_path, monkeypatch):
    """Rebuild works with only the content in git, nothing else.

    A fresh tiny project (no .gov-runtime, no external state) must
    rebuild successfully. This proves rebuild draws only from git.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion does not read what
    the case's name claims): the folder it deleted never existed, and it ran
    with every tool of the machine on PATH.  A first rebuild now leaves a
    ``.gov-runtime``, which is removed, and the second runs with a PATH that
    holds git and the secrets filter's gitleaks alone (the lexical index's
    owner runs that filter on every file and fails closed without it,
    DEC-440); it must succeed and recreate the lexical store.
    """
    project = w2_67b_support.rebuild_project(tmp_path / "repo")
    w2_67b_support.rebuild(project, sandbox)
    shutil.rmtree(project / ".gov-runtime")
    tools_only = tmp_path / "git-only-bin"
    tools_only.mkdir()
    for tool in ("git", "gitleaks"):
        binary = shutil.which(tool)
        assert binary, f"{tool} is not on PATH"
        (tools_only / tool).symlink_to(binary)
    monkeypatch.setenv("PATH", str(tools_only))
    run, result = w2_67b_support.rebuild(project, sandbox)
    assert (result.get("stores") or {}).get("lexical", {}).get("status") == "recreated", (
        f"rebuild with git and gitleaks alone on PATH and no earlier state does not recreate the lexical store\n"
        f"{run.describe()}"
    )


def test_rebuild_digest_matches_store_loader(sandbox, tmp_path):
    """The digest reported by rebuild matches what the store loader computes (CAP-07.a).

    After rebuild, running ``gov status --json`` (which loads the store) and comparing its session digest with
    the rebuild's reported digest confirms they agree.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion does not read what
    the case's name claims): the envelope's session is a string, so the
    digests were never compared.  The rebuild's digest is now compared with
    the one the store loader computes from the store it left
    (``gov.store.digest``, this worktree's code).
    """
    project = w2_67b_support.rebuild_project(tmp_path / "repo")
    run_reb, result = w2_67b_support.rebuild(project, sandbox)
    rebuild_digest = result.get("digest")
    assert rebuild_digest is not None, f"rebuild has no digest\n{run_reb.describe()}"

    loaded = support.run_python_snippet(
        support.REPO_ROOT, sandbox,
        f"from pathlib import Path\nfrom gov.store import digest\nprint(digest(Path({str(project)!r})))\n")
    assert loaded.returncode == 0, f"the store loader failed: {loaded.stderr}"
    store_digest = loaded.stdout.strip()
    assert rebuild_digest == store_digest, (
        f"rebuild digest {rebuild_digest} does not match store digest {store_digest}\n"
        f"rebuild:\n{run_reb.describe()}"
    )

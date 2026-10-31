"""The last round (DEC-761): cases added after the second review of W2-16 (R2-F1, R2-F2, R2-F3) and the role check.

Written from the KPI lines and DEC-761's described behaviour (DEC-136), without reading the implementation:

- **R2-F1 (KPI success 4, the failure line).** Once a project's lock records a release, ``gov release --lock-from``
  run by hand at the project root never rewrites it into a lock without a release, and never makes an edited
  kernel pass.
- **R2-F3, the part built in this round.** A source whose history holds release records, and whose later commit
  removed them, is refused by ``copier copy``, ``copier update`` and ``gov release --lock-from``. A source that
  never held a record waits for the owner (README, "Open: a source that never held a record"): no case here.
- **R2-F2 (KPI success 4: "a project cannot silence the lock comparison").** A lock whose release entries were
  deleted fails doctor's lock part.
- **The role check (KPI success 2, "agents never tag"; DEC-761, DEC-365).** ``gov release --lock-from`` runs only
  for the orchestrator (``GOV_ROLE=orchestrator``) or the owner (``GOV_ROLE`` unset: a plain terminal). The build
  form ``gov release <version>`` is the owner's alone from a plain terminal with a typed code (DEC-772 item 1,
  replacing DEC-761 item 1's line; round 3): from these runs it refuses for every ``GOV_ROLE`` value and unset. Only
  the cases of this check set ``GOV_ROLE``; every other ``gov`` and Copier run of the suite has it unset.

Every repository and project is a temporary one (``w2_16_support``); every tag is made by the case, unsigned,
standing for the owner.
"""

from __future__ import annotations

import base64
import binascii
import shutil
import subprocess
import sys

import pytest
import yaml

import w2_16_support as support
import w1_39_support as w139

TAMPERED = support.normalise_path(support.TAMPERED_REL)   # governance/kernel/schemas/ticket.schema.json
REMOVED_RECORDS_TAG = "v1.6.0"                             # the owner's tag on the commit that removed the records
_UNSET = object()


def _gov(cwd, sandbox, *args, role=_UNSET):
    """``gov <args>`` as ``support.run_gov`` runs it, with ``GOV_ROLE`` set to ``role`` (left unset by default)."""
    assert cwd.resolve() != support.REPO_ROOT.resolve(), "no gov command of these tests runs in this worktree"
    env = support.gov_environment(sandbox)
    assert "GOV_ROLE" not in env
    if role is not _UNSET:
        env["GOV_ROLE"] = role
    try:
        done = subprocess.run((sys.executable, "-m", "gov.cli.main", *args), cwd=str(cwd), env=env,
                              capture_output=True, text=True, timeout=support.GOV_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {support.GOV_TIMEOUT_S:.0f} s") from None
    return support.Run(tuple(args), done.returncode, done.stdout, done.stderr)


def _lock_from(project, sandbox, source, role=_UNSET):
    """``gov release --lock-from <source>`` at the project root, by hand: the command the template's task runs."""
    return _gov(project, sandbox, "release", "--lock-from", str(source), role=role)


def _checked_out(origin, destination, ref):
    """A copy of a temporary repository with ``ref`` checked out (as Copier hands the task its source)."""
    repo = support.clone_folder(origin, destination)
    support.git(repo, "checkout", "-q", "--detach", ref)
    return repo


def _edit_a_kernel_file(project, sandbox):
    """One byte appended to a kernel file; doctor reports DRIFT naming it (the case's precondition)."""
    support.append_one_byte(project / TAMPERED)
    w139.assert_drift_naming(support.doctor(project, sandbox), TAMPERED,
                             f"this case needs doctor to fail first, naming {TAMPERED}")


def _assert_refused(run, why):
    assert run.returncode != 0, f"`gov {' '.join(run.args)}` was not refused although {why}\n{run.describe()}"
    assert "Traceback" not in run.output, f"the refusal ({why}) ended in a traceback\n{run.describe()}"


@pytest.fixture(scope="session")
def first_release_source(releases, tmp_path_factory):
    """The stand-in Gov OS repository with ``v1.4.0`` checked out: the genuine source of the first release. Never
    changed."""
    return _checked_out(releases.repo, tmp_path_factory.mktemp("w2-16-first-release-source") / "gov-os",
                        support.FIRST_TAG)


# --------------------------------------------------------------------------
# R2-F1: --lock-from in a project whose lock records a release
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kind", ("a plain folder", "a git repository with a version tag"))
def test_lock_from_a_source_with_no_release_record_is_refused_where_the_lock_records_a_release(
        own_release_project, plain_source, sandbox, tmp_path, kind):
    """A project installed from release 1.4.0, a kernel file edited (doctor fails naming it); `gov release
    --lock-from` run by hand with a source that holds no release record (`copier.yml` and `template/` alone, as a
    plain folder, or as W1-39's git source tagged v0.1.0): refused, the lock byte for byte as it was, doctor still
    fails naming the file."""
    project = own_release_project
    source = support.clone_folder(plain_source, tmp_path / "source")
    if kind == "a plain folder":
        shutil.rmtree(source / ".git")
    assert not (source / support.RELEASES_REL).exists(), "this case needs a source with no release record"
    _edit_a_kernel_file(project, sandbox)
    before = support.lock_bytes(project)
    run = _lock_from(project, sandbox, source)
    why = (f"the project's lock records release {support.FIRST_VERSION} and the source ({kind}) holds no release "
           f"record")
    _assert_refused(run, why)
    assert support.lock_bytes(project) == before, f"a refused --lock-from ({why}) changed the lock\n{run.describe()}"
    w139.assert_drift_naming(support.doctor(project, sandbox), TAMPERED,
                             f"{TAMPERED} is still edited after a refused --lock-from")


def test_lock_from_the_installed_release_s_own_source_never_makes_an_edited_kernel_pass(
        own_release_project, first_release_source, sandbox):
    """The same, with the genuine source of the release the lock records (`v1.4.0` checked out): rewriting the
    installed release's lock from the edited kernel is refused (the lock as it was), or, if the command writes,
    doctor still fails naming the edited file, never MATCH."""
    project = own_release_project
    _edit_a_kernel_file(project, sandbox)
    before = support.lock_bytes(project)
    run = _lock_from(project, sandbox, first_release_source)
    assert "Traceback" not in run.output, f"`gov release --lock-from` ended in a traceback\n{run.describe()}"
    if run.returncode != 0:
        assert support.lock_bytes(project) == before, f"a refused --lock-from changed the lock\n{run.describe()}"
    w139.assert_drift_naming(
        support.doctor(project, sandbox), TAMPERED,
        f"{TAMPERED} was edited after release {support.FIRST_VERSION} was installed and `gov release --lock-from` "
        f"was run with that release's source (exit {run.returncode})")


# --------------------------------------------------------------------------
# R2-F3, the part built in this round: a source whose release records were removed
# --------------------------------------------------------------------------

def _remove_the_records(repo):
    """On w2/integrate of a stand-in that holds both releases: a commit removes docs/releases/ and edits a kernel
    file; the case tags it REMOVED_RECORDS_TAG (unsigned, standing for the owner)."""
    assert support.git(repo, "log", "--format=%H", support.INTEGRATION_BRANCH, "--", support.RELEASES_REL).strip(), \
        "this case needs release records in w2/integrate's history"
    support.git(repo, "rm", "-r", "-q", "--", support.RELEASES_REL)
    support.append_one_byte(repo / support.TAMPERED_REL)
    support.commit_all(repo, "the release records removed and a kernel file edited")
    support.git(repo, "tag", REMOVED_RECORDS_TAG)
    assert not (repo / support.RELEASES_REL).exists() and not support.porcelain_paths(repo)


@pytest.mark.parametrize("how", ("copier copy", "copier update from 1.4.0", "gov release --lock-from by hand"))
def test_a_source_whose_release_records_were_removed_is_refused(copier_bin, releases, release_repo,
                                                                own_release_project, sandbox, tmp_path, how):
    """The stand-in's w2/integrate holds release records in its history; a later commit removes docs/releases/
    and edits a kernel file, tagged v1.6.0. Installing from it is refused: by `copier copy` (no lock written that
    passes doctor), by `copier update` from 1.4.0 (the lock still records 1.4.0, never a lock without a release),
    and by `gov release --lock-from` run by hand in a project of 1.4.0 (the lock byte for byte as it was)."""
    why = (f"the source's history holds release records and {REMOVED_RECORDS_TAG} is a commit that removed them "
           f"and edited {TAMPERED}")
    if how == "copier copy":
        _remove_the_records(release_repo)
        destination = tmp_path / "copied-from-v1.6.0"   # a fresh folder: tmp_path / "product" is filled (DEC-767)
        done = support.copy(copier_bin, sandbox, release_repo, destination, REMOVED_RECORDS_TAG)
        assert done.returncode != 0, f"Copier installed {REMOVED_RECORDS_TAG} although {why}\n" \
                                     f"{support.copier_report(done)}"
        assert "Traceback" not in done.stdout + done.stderr, \
            f"the refusal ended in a traceback\n{support.copier_report(done)}"
        if support.lock_bytes(destination) is not None:
            result = support.doctor(destination, sandbox)
            assert not result.claims_match and result.section.get("status") != "pass", \
                f"a refused copy left a lock that passes doctor\n{result.describe()}"
    elif how == "copier update from 1.4.0":
        project = support.create_project(copier_bin, sandbox, release_repo, tmp_path / "product", support.FIRST_TAG)
        _remove_the_records(release_repo)
        done = support.update(copier_bin, sandbox, project, REMOVED_RECORDS_TAG)
        assert done.returncode != 0, f"Copier updated to {REMOVED_RECORDS_TAG} although {why}\n" \
                                     f"{support.copier_report(done)}"
        assert "Traceback" not in done.stdout + done.stderr, \
            f"the refusal ended in a traceback\n{support.copier_report(done)}"
        assert support.lock_bytes(project) is not None, "a refused update removed the lock"
        scalars = support.lock_scalars(project)
        assert support.FIRST_VERSION in scalars and releases.first.manifest_hash in scalars, (
            f"after a refused update to {REMOVED_RECORDS_TAG} the lock no longer records release "
            f"{support.FIRST_VERSION}\n{support.lock_bytes(project).decode()[:3000]}")
    else:
        _remove_the_records(release_repo)
        project = own_release_project
        before = support.lock_bytes(project)
        run = _lock_from(project, sandbox, release_repo)
        _assert_refused(run, why)
        assert support.lock_bytes(project) == before, f"a refused --lock-from changed the lock\n{run.describe()}"


# --------------------------------------------------------------------------
# R2-F2: a lock whose release entries were deleted
# --------------------------------------------------------------------------

def _records_the_release(value, record):
    """Whether a value of the lock is the release's version, holds its manifest hash, or is the release manifest
    (as a map, as its text, or as its bytes in base64). Found by value: no key name is fixed. A value that only
    holds the version inside a longer text (the template tag ``v1.4.0``) is not a release entry."""
    if isinstance(value, dict):
        return value == record.manifest
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        return False
    text = str(value).strip()
    if text == record.version or record.manifest_hash in text.lower():
        return True
    if text == record.manifest_bytes.decode("utf-8", "replace").strip():
        return True
    try:
        decoded = base64.b64decode("".join(text.split()), validate=True)
    except (binascii.Error, ValueError):
        return False
    return bool(decoded) and (decoded == record.manifest_bytes or support.parse_structured(decoded) == record.manifest)


def _without_the_release(value, record):
    """``value`` with every entry that records the release taken out, and a map or list emptied by that taken out
    too; nothing else changed."""
    if isinstance(value, dict):
        kept = {}
        for key, item in value.items():
            if _records_the_release(item, record):
                continue
            pruned = _without_the_release(item, record)
            if isinstance(item, (dict, list)) and item and not pruned:
                continue
            kept[key] = pruned
        return kept
    if isinstance(value, list):
        kept = []
        for item in value:
            if _records_the_release(item, record):
                continue
            pruned = _without_the_release(item, record)
            if isinstance(item, (dict, list)) and item and not pruned:
                continue
            kept.append(pruned)
        return kept
    return value


@pytest.mark.parametrize("with_kernel_edit", (False, True),
                         ids=("the release entries alone", "and a kernel file with its lock hash edited together"))
def test_a_lock_whose_release_entries_were_deleted_fails(releases, own_release_project, sandbox, with_kernel_edit):
    """A project installed from release 1.4.0: every entry of the lock that records the release (its version, its
    manifest hash, the release manifest the lock holds) deleted, nothing else changed; and the same with one kernel
    file edited and its hash in the lock's manifest edited to match. Doctor's lock part fails."""
    project = own_release_project
    record = releases.first
    result = support.doctor(project, sandbox)
    assert result.section.get("status") == "pass", f"this case needs a project that passes first\n{result.describe()}"
    path = project / support.LOCK_REL
    lock = support.lock_data(project)
    stripped = _without_the_release(lock, record)
    assert stripped != lock, f"the lock holds no entry that records release {record.version}"
    left = support.scalars(stripped)
    assert record.version not in left and record.manifest_hash not in left
    assert stripped.get(support.MANIFEST_KEY) == lock[support.MANIFEST_KEY], \
        "this case changes nothing but the release entries (the file manifest kept)"
    if with_kernel_edit:
        old = support.sha256(project / TAMPERED)
        support.append_one_byte(project / TAMPERED)
        assert stripped[support.MANIFEST_KEY].get(TAMPERED) == old
        stripped[support.MANIFEST_KEY][TAMPERED] = support.sha256(project / TAMPERED)
    header = w139.lock_header(project)
    path.write_text((header + "\n" if header else "") + yaml.safe_dump(stripped, sort_keys=False), encoding="utf-8")
    support.commit_all(project, "the lock's release entries deleted"
                       + (f"; {TAMPERED} and its lock hash edited together" if with_kernel_edit else ""))
    support.assert_lock_part_fails(
        support.doctor(project, sandbox),
        f"every entry that records release {record.version} was deleted from the lock of a project installed from it"
        + (f", and {TAMPERED} was edited with its hash in the lock" if with_kernel_edit else ""))


# --------------------------------------------------------------------------
# The role check: only the orchestrator or the owner releases (DEC-761, DEC-365)
# --------------------------------------------------------------------------

REFUSED_ROLES = ("engineer", "independent-auditor", "independent-test-designer", "product-spec", "research",
                 "ticket-lead", "w2-16-unknown-role", "")
ALLOWED_ROLES = ("orchestrator", _UNSET)
BUILD, LOCK_FROM = "gov release <version>", "gov release --lock-from"
FORMS = (BUILD, LOCK_FROM)
# DEC-772 item 1 (Rewrite-Reason: DEC-772): the build form refuses for every GOV_ROLE value, `orchestrator`
# included, and with GOV_ROLE unset without a terminal (these runs have none). Its two earlier positive controls are
# refusals now; the seam's positive control (`test_w2_16_owner_terminal.py`) replaces them. `--lock-from` unchanged.
REFUSED_CALLS = [(BUILD, role) for role in REFUSED_ROLES + ALLOWED_ROLES] + [(LOCK_FROM, role) for role in REFUSED_ROLES]
ALLOWED_CALLS = [(LOCK_FROM, role) for role in ALLOWED_ROLES]
# What a refusal of the build form says (DEC-772: which reason is given, where several hold, is not fixed).
BUILD_REASON_WORDS = ("gov_role", "role", "terminal", "tty", "claude", "session", "ancest", "process")


def _role_id(role):
    if role is _UNSET:
        return "GOV_ROLE unset (the owner)"
    return f"GOV_ROLE={role}" if role else "GOV_ROLE set and empty"


def _call_id(call):
    form, role = call
    return f"{form}-{_role_id(role)}"


@pytest.fixture()
def copy_time_project(own_release_project):
    """A project of release 1.4.0 as a Copier copy leaves it when the lock task runs: every file written, the lock
    not yet (the case's copy of the session's project, its lock taken away)."""
    (own_release_project / support.LOCK_REL).unlink()
    support.commit_all(own_release_project, "the state a copy is in when its lock task runs")
    return own_release_project


def _where(form, request):
    """A clean stand-in on w2/integrate with no release (to build 1.4.0), or a project of 1.4.0 at copy time."""
    return request.getfixturevalue("repo" if form == "gov release <version>" else "copy_time_project")


def _release_in(form, where, request, sandbox, role):
    """Run the form as ``role`` in ``where``: `gov release 1.4.0`, or `--lock-from` the genuine source of 1.4.0."""
    if form == "gov release <version>":
        return _gov(where, sandbox, "release", support.FIRST_VERSION, role=role)
    return _lock_from(where, sandbox, request.getfixturevalue("first_release_source"), role=role)


@pytest.mark.parametrize("call", REFUSED_CALLS, ids=_call_id)
def test_gov_release_refuses_every_role_but_the_orchestrator_and_the_owner(request, sandbox, call):
    """Engineers, auditors, test designers and every other role never cut or rewrite a release: non-zero exit, no
    traceback, nothing written (the whole snapshot; for --lock-from, the project's lock as it was: absent).
    `--lock-from`: the role named (or: only the orchestrator or the owner may release); the same call releases as the
    orchestrator and as the owner (the next case).

    **Rewritten (DEC-772 item 1, which replaces DEC-761 item 1's line for the build form; Rewrite-Reason: DEC-772).**
    The build form `gov release <version>` is the owner's alone, from a plain terminal: these runs (an agent's
    session or none, no terminal) are refused for every GOV_ROLE value, `orchestrator` included, and with GOV_ROLE
    unset, with the code RELEASE_REFUSED and a reason said in words (which one is not fixed). Its earlier positive
    controls (`orchestrator`, unset) are refusals here; the seam's positive control replaces them
    (`test_w2_16_owner_terminal.py::test_the_owner_in_person_builds_the_release`). The `--lock-from` half is as it
    was."""
    form, role = call
    where = _where(form, request)
    before, lock_before = support.snapshot(where), support.lock_bytes(where)
    run = _release_in(form, where, request, sandbox, role)
    text = run.output.lower()
    if form == BUILD:
        why = f"the build form is the owner's alone from a plain terminal (DEC-772), and {_role_id(role)}, no terminal"
        _assert_refused(run, why)
        assert support.RELEASE_REFUSED in run.output, \
            f"the refusal ({why}) does not give the code {support.RELEASE_REFUSED}\n{run.describe()}"
        assert any(word in text for word in BUILD_REASON_WORDS), \
            f"the refusal ({why}) does not say its reason in words\n{run.describe()}"
    else:
        why = f"{_role_id(role)} is neither the orchestrator nor the owner"
        _assert_refused(run, why)
        assert (role and role in run.output) or ("orchestrator" in text and "owner" in text), \
            f"the refusal ({why}) names neither the role nor who may release\n{run.describe()}"
    changed = support.snapshot_difference(before, support.snapshot(where))
    assert not changed, f"a refused release ({why}) wrote or changed: {changed[:10]}\n{run.describe()}"
    assert support.lock_bytes(where) == lock_before, f"a refused --lock-from ({why}) wrote the lock"


@pytest.mark.parametrize("call", ALLOWED_CALLS, ids=_call_id)
def test_gov_release_runs_for_the_orchestrator_and_the_owner(request, sandbox, releases, call):
    """Positive controls: `gov release --lock-from` writes the lock with GOV_ROLE=orchestrator and with GOV_ROLE
    unset.

    **Rewritten (DEC-772; Rewrite-Reason: DEC-772):** the build form's two controls left this case (they are
    refusals in the case above); the build form's positive control is the seam's, the owner in person
    (`test_w2_16_owner_terminal.py::test_the_owner_in_person_builds_the_release`). The `--lock-from` half is as
    it was."""
    form, role = call
    where = _where(form, request)
    run = _release_in(form, where, request, sandbox, role)
    assert run.returncode == 0 and "Traceback" not in run.output, \
        f"`gov {' '.join(run.args)}` did not run for {_role_id(role)}\n{run.describe()}"
    scalars = support.lock_scalars(where)
    assert support.FIRST_VERSION in scalars and releases.first.manifest_hash in scalars, \
        f"the lock written by --lock-from does not record release {support.FIRST_VERSION}\n{run.describe()}"


def test_the_suite_runs_gov_and_copier_with_gov_role_unset(sandbox):
    """Guard: outside the role cases, every `gov` and Copier run of the suite has GOV_ROLE unset (the owner), even
    when the session that runs the tests has one."""
    for name, env in (("gov", support.gov_environment(sandbox)),
                      ("a Copier task", support.copier_environment(sandbox)),
                      ("a Copier task without python3's gov", support.copier_environment(sandbox, True))):
        assert "GOV_ROLE" not in env, f"{name} runs with GOV_ROLE set"

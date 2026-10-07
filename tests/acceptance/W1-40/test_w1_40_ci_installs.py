"""What the CI workflow puts on the hosted runner: gitleaks and the ``gov`` package, nothing else (DEC-494,
DEC-497; DEC-083, DEC-287) [CAP-39.a].

- gitleaks: one step of its own fetches the address the tool registry records as ``archive`` and verifies the
  download against the registry's ``archive_sha256`` before it is unpacked; a mismatch fails the step. The
  version, the address and the checksum are the registry's: the step reads them from the registry file of the
  checkout, or the workflow's text holds exactly the registry's values. The text case accepts either and
  refuses a value that differs.
- the ``gov`` package: installed from the checkout itself. Judged as text; never run here.
- nothing else is installed: not pytest, not openspec, not rulesync, not lefthook.

No case downloads anything. The two cases that run the gitleaks step give the simulated runner a stand-in
downloader under the names ``curl`` and ``wget``, which hands out one local file for the registry's address and
refuses every other address (``w1_40_support.Machine.serve``). The local file is an archive built by the case;
its ``gitleaks`` is a script that leaves a mark. The real gitleaks is withheld from that runner.
"""

from __future__ import annotations

import re
import shlex

import pytest
import yaml

import w1_40_support as support

NOT_INSTALLED = ("pytest", "openspec", "rulesync", "lefthook")   # DEC-497: "installs nothing else"
REGISTRY_NAME = support.REGISTRY_REL.rsplit("/", 1)[-1]

_PACKAGE_INSTALL = re.compile(r"\b(?:pipx?3?|uv\s+pip|uv\s+tool)\s+install\b(.*)")
_WORKSPACE = re.compile(r"\$\{\{\s*github\.workspace\s*\}\}")
LOCAL = (".", "./", "$GITHUB_WORKSPACE", "${GITHUB_WORKSPACE}", "$PWD", "${PWD}")
FROM_ELSEWHERE = ("-r", "--requirement", "-i", "--index-url", "--extra-index-url", "-f", "--find-links")
_VERIFY = re.compile(r"(?:^|[\s;&|(])(?:sha256sum|shasum)\s", re.MULTILINE)
_UNPACK = re.compile(r"(?:^|[\s;&|(])(?:tar|unzip|gunzip|bsdtar)\s", re.MULTILINE)


def _steps():
    try:
        return support.download_steps()
    except support.Absent as absent:
        pytest.fail(str(absent), pytrace=False)


def _gitleaks_step():
    try:
        return support.gitleaks_install_step()
    except support.Absent as absent:
        pytest.fail(str(absent), pytrace=False)


def _package_targets(step):
    """What the package installers of a step are told to install: every argument that is no option."""
    run = _WORKSPACE.sub("$GITHUB_WORKSPACE", str(step["run"]).replace("\\\n", " "))
    targets = []
    for rest in _PACKAGE_INSTALL.findall(run):
        rest = re.split(r"&&|\|\||;|\|", rest)[0]
        targets.extend(arg for arg in shlex.split(rest) if not arg.startswith("-"))
        assert not any(arg in FROM_ELSEWHERE or arg.split("=")[0] in FROM_ELSEWHERE for arg in shlex.split(rest)), (
            f"a step installs packages from a list or an index of its own: {rest.strip()!r}")
    return targets


def _installs_the_checkout(step):
    targets = _package_targets(step)
    return bool(targets) and all(target in LOCAL for target in targets)


def _registry_file(entry):
    """A tool registry for the temporary project: the one entry the step can need, with the fields it reads."""
    return yaml.safe_dump({"tools": [{key: entry[key] for key in ("name", "version", "archive", "archive_sha256")}]},
                          sort_keys=False)


def _push_registry(project, machine, entry):
    dev = machine()
    done, moved = project.commit(dev, support.REGISTRY_REL, _registry_file(entry))
    assert moved, f"the fixture cannot be built: the hook refused the commit\n{support.said(done)}"
    done, arrived = project.push(dev)
    assert arrived, f"the fixture cannot be built: the hook refused the push\n{support.said(done)}"


def _downloads(project):
    mark = project.marks / "download"
    return mark.read_text().split() if mark.is_file() else []


# -- gitleaks ----------------------------------------------------------------

def test_the_gitleaks_step_takes_its_version_address_and_checksum_from_the_registry():
    """A workflow whose address, version or checksum differs from the registry is red here."""
    name, step = _gitleaks_step()
    entry = support.registry()["gitleaks"]
    text = str(step["run"]) + "\n" + "\n".join(
        str(value) for _, workflow in support.push_workflows()
        for scope in [workflow, *(workflow.get("jobs") or {}).values(), step]
        for value in (scope.get("env") or {}).values())
    addresses = set(re.findall(r"https?://[^\s\"'\\)]+", text))
    checksums = set(re.findall(r"\b[0-9a-fA-F]{64}\b", text))
    own = str(step["run"]) + "\n" + "\n".join(str(value) for value in (step.get("env") or {}).values())
    versions = set(re.findall(r"\b\d+\.\d+\.\d+\b", own))
    assert addresses <= {entry["archive"]}, (
        f"{name}: the gitleaks step names an address that is not the registry's archive: {sorted(addresses)}")
    assert checksums <= {entry["archive_sha256"]}, (
        f"{name}: the gitleaks step names a checksum that is not the registry's archive_sha256: {sorted(checksums)}")
    assert versions <= {str(entry["version"]).lstrip("v")}, (
        f"{name}: the gitleaks step names a version that is not the registered one: {sorted(versions)}")
    if not (addresses and checksums):
        assert REGISTRY_NAME in text, (
            f"{name}: the gitleaks step neither holds the registry's address and checksum nor reads "
            f"{support.REGISTRY_REL}")
    assert not _package_targets(step), f"{name}: the gitleaks step also installs packages: it is no step of its own"


def test_a_download_that_does_not_match_the_checksum_fails_the_step_and_is_not_unpacked(
        project, machine, ci, tmp_path):
    """The stand-in downloader hands out a file that is not the registered archive. The project's own registry
    holds the registered address and checksum, for a step that reads them from the checkout."""
    _, step = _gitleaks_step()
    entry = support.registry()["gitleaks"]
    archive, checksum = support.build_archive(tmp_path / "served")
    assert checksum != entry["archive_sha256"]
    _push_registry(project, machine, entry)
    result = ci(gitleaks=False, serve=(entry["archive"], archive))
    ran = result.of(step)
    assert ran.kind == "run" and entry["archive"] in _downloads(project), (
        "the gitleaks step did not ask curl or wget for the registry's archive: it cannot be run offline, or it "
        f"fetches another address (asked for: {_downloads(project)}):\n{result}")
    assert ran.returncode != 0, (
        f"the step ended with exit 0 for a download whose sha256 is not the registry's archive_sha256:\n{ran.output}")
    assert not support.unpacked_copies(result, archive), (
        f"the download was unpacked although its checksum does not match: {support.unpacked_copies(result, archive)}")
    assert not (project.marks / support.DOWNLOADED_MARK).is_file(), (
        f"a later step ran the gitleaks of a download that was not verified:\n{result}")
    assert not result.green


def test_a_download_is_verified_before_it_is_unpacked_and_a_verified_one_is_the_gitleaks_of_the_job(
        project, machine, ci, tmp_path):
    """The control of the mismatch case: a step that fails whatever it is given would pass that case.

    Where the step reads the checksum from the registry of the checkout, the case runs it: the project's registry
    holds the checksum of the local archive, the step passes, and the gitleaks scan of the same run is done by
    the gitleaks that came out of the archive. Where the workflow's text holds the registry's checksum, no local
    file can match it offline: the case then holds as text that the checksum is verified before anything is
    unpacked (README, residual R-17).
    """
    name, step = _gitleaks_step()
    entry = support.registry()["gitleaks"]
    run = str(step["run"])
    if entry["archive_sha256"] in yaml.safe_dump(step):
        verify, unpack = _VERIFY.search(run), _UNPACK.search(run)
        assert verify and unpack and verify.start() < unpack.start(), (
            f"{name}: the gitleaks step does not verify a sha256 before it unpacks the download")
        return
    archive, checksum = support.build_archive(tmp_path / "served")
    _push_registry(project, machine, dict(entry, archive_sha256=checksum))
    result = ci(gitleaks=False, serve=(entry["archive"], archive))
    ran = result.of(step)
    assert ran.kind == "run" and ran.returncode == 0, (
        f"the gitleaks step failed for a download whose sha256 is the one the checkout's registry records:\n{result}")
    assert (project.marks / support.DOWNLOADED_MARK).is_file(), (
        f"the gitleaks scan of the job was not done by the gitleaks the step installed:\n{result}")
    assert result.green, f"the job is red with a verified gitleaks, every check passing and the record there:\n{result}"


# -- the gov package -----------------------------------------------------------

def test_a_step_installs_the_gov_package_from_the_checkout():
    """Not by name from an index: what the job checks is the commit it builds (DEC-494, DEC-497)."""
    found = [(name, step) for name, step in _steps() if _package_targets(step)]
    assert found, "no step of a push workflow installs a package: the gov package is not put on the runner"
    for name, step in found:
        assert _installs_the_checkout(step), (
            f"{name}: a step installs {_package_targets(step)}: the gov package comes from the checkout itself "
            f"(one of {LOCAL}), with no extras")
    assert len(found) == 1, f"{len(found)} steps install packages: DEC-494 asks for one step for the gov package"
    assert not support._FETCH.search(str(found[0][1]["run"])), "the step for the gov package also downloads a file"


# -- nothing else ---------------------------------------------------------------

def test_no_step_installs_anything_but_gitleaks_and_the_gov_package():
    """A guard: green before the two install steps exist (the workflow installs nothing) and after."""
    try:
        workflows = support.push_workflows()
    except support.Absent as absent:
        pytest.fail(str(absent), pytrace=False)
    for path, workflow in workflows:
        for _, _, step in support.steps_of(workflow):
            uses = str(step.get("uses", ""))
            for tool in NOT_INSTALLED + ("gitleaks",):
                assert tool not in uses.lower(), f"{path.name}: the action {uses!r} puts {tool} on the runner"
            if "run" not in step or not support.is_download(step):
                continue
            run = str(step["run"])
            if _package_targets(step):
                assert _installs_the_checkout(step), (
                    f"{path.name}: a step installs {_package_targets(step)}, not the checkout alone")
                continue
            assert support.can_be_served(step) and re.search(r"\bgitleaks\b", run), (
                f"{path.name}: a step installs something that is neither gitleaks nor the gov package:\n{run}")
            for tool in NOT_INSTALLED:
                assert not re.search(rf"\b{tool}\b", run), f"{path.name}: the gitleaks step also names {tool}"

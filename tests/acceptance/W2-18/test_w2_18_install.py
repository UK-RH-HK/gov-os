"""Success 1 [CAP-43]: `gov install <version>` installs the release's gov into the repository's own tool environment
from the release's wheel, verified against the manifest's sha256, never an editable install."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import w2_18_support as s


def _installed(installed_a):
    done = installed_a.run
    assert done.returncode == 0, (
        f"`gov install {s.VERSION_A}` in a product adopted from {s.TAG_A} (its source holding release "
        f"{s.VERSION_A} and its record) does not exit 0\n{done.describe()}")
    return installed_a.project


def test_install_exits_zero_and_pin_json_names_the_release_and_its_verified_wheel(installed_a, releases):
    project = _installed(installed_a)
    pin = s.read_pin(project)
    release = releases.a
    assert pin.get("version") == s.VERSION_A, f"pin.json names version {pin.get('version')!r}, not {s.VERSION_A}"
    wheel = pin.get("wheel") or {}
    assert wheel.get("name") == release.wheel_name and wheel.get("sha256") == release.wheel_sha256, (
        f"pin.json names the wheel {wheel}, the manifest {release.manifest['wheel']}")
    assert pin.get("hash_check") == "passed", f"pin.json's hash_check is {pin.get('hash_check')!r}, not 'passed'"


def test_the_pinned_gov_prints_the_release_s_cli_version(installed_a, releases, sandbox):
    project = _installed(installed_a)
    gov = s.pin_folder(project) / "bin" / "gov"
    assert gov.exists(), f"there is no {gov}"
    done = s.run((gov, "--version"), project, s.base_env(sandbox))
    cli_version = releases.a.manifest["cli_version"]
    assert done.returncode == 0 and s.prints_version(done.stdout, cli_version), (
        f"`<common>/gov/bin/gov --version` does not print release {s.VERSION_A}'s CLI version {cli_version}\n"
        f"{done.describe()}")


def test_the_pinned_gov_lies_in_the_environment_s_own_site_packages_never_editable(installed_a, sandbox):
    project = _installed(installed_a)
    environment = Path(s.read_pin(project).get("environment") or "")
    pin = s.pin_folder(project)
    assert environment.is_absolute() and environment.is_dir() and environment.is_relative_to(pin), (
        f"pin.json's environment {environment} is not a folder of the repository's own {pin}")
    packages = s.site_packages(environment)
    done = s.run((environment / "bin" / "python", "-I", "-c", "import gov; print(gov.__file__)"), sandbox.tmpdir,
                 s.base_env(sandbox))
    imported = Path(done.stdout.strip() or ".")
    assert done.returncode == 0 and imported.is_relative_to(packages / "gov"), (
        f"the environment's gov is not imported from its own site-packages {packages}\n{done.describe()}")
    dists = sorted(packages.glob("gov-*.dist-info"))
    assert len(dists) == 1, f"the environment holds {len(dists)} installed gov distributions: {dists}"
    direct = dists[0] / "direct_url.json"
    if direct.is_file():
        marked = json.loads(direct.read_text(encoding="utf-8"))
        assert not (marked.get("dir_info") or {}).get("editable"), f"{direct} marks gov editable: {marked}"
    editable = sorted(path.name for path in packages.iterdir() if path.name.startswith("__editable__"))
    assert not editable, f"the environment holds an editable install's files: {editable}"


def test_a_wheel_given_by_wheel_that_does_not_hash_to_the_manifest_is_refused_and_nothing_is_written(
        adopted, releases, tmp_path, sandbox):
    project = s.copy_project(adopted, tmp_path / "product")
    release = releases.a
    wrong = tmp_path / "given" / release.wheel_name
    wrong.parent.mkdir()
    shutil.copyfile(releases.b.wheel, wrong)  # another release's wheel, under this release's name
    actual = s.sha256(wrong)
    assert actual != release.wheel_sha256
    pin = s.pin_folder(project)
    before = s.tree_state(pin)
    done = s.worktree_gov(project, sandbox, "install", s.VERSION_A, "--wheel", wrong)
    assert done.returncode != 0, f"a wheel that does not hash to the manifest's sha256 is installed\n{done.describe()}"
    output = done.output
    assert ("wheel" in output.lower() or release.wheel_name in output) and release.wheel_sha256 in output \
        and actual in output, (
        f"the refusal does not name the wheel with the manifest's sha256 {release.wheel_sha256} and the wheel's "
        f"actual sha256 {actual}\n{done.describe()}")
    after = s.tree_state(pin)
    assert after == before, f"the refused install changed {pin}: {s.state_difference(before, after)}"
    right = tmp_path / "right" / release.wheel_name
    right.parent.mkdir()
    shutil.copyfile(release.wheel, right)
    done = s.worktree_gov(project, sandbox, "install", s.VERSION_A, "--wheel", right)
    assert done.returncode == 0 and s.read_pin(project).get("version") == s.VERSION_A, (
        f"the release's own wheel, given the same way, is not installed\n{done.describe()}")


def test_a_release_whose_wheel_built_from_its_commit_does_not_hash_to_the_manifest_is_refused_and_the_pin_kept(
        adopted, releases, tmp_path, sandbox):
    project = s.copy_project(adopted, tmp_path / "product")
    s.plant_pin(project, releases, s.VERSION_A, sandbox)  # the pin as it was before the refused install
    source, false = s.tamper_wheel_hash(releases, tmp_path / "gov-os-tampered")
    pin = s.pin_folder(project)
    before = s.tree_state(pin)
    done = s.worktree_gov(project, sandbox, "install", s.VERSION_A, "--source", source)
    assert done.returncode != 0, (
        f"a release whose manifest names a wheel sha256 the wheel built from its commit does not have is "
        f"installed\n{done.describe()}")
    output = done.output
    assert "wheel" in output.lower() and false in output and releases.a.wheel_sha256 in output, (
        f"the refusal does not name the wheel with the manifest's sha256 {false} and the built wheel's sha256 "
        f"{releases.a.wheel_sha256}\n{done.describe()}")
    after = s.tree_state(pin)
    assert after == before, f"the refused install changed {pin}: {s.state_difference(before, after)}"

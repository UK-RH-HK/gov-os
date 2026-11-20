"""W2-18 (DAEO-057v): the pinned install, the pin dispatch and doctor's section ``install``. Builder regression evidence.

The interface: ``<common>/gov/`` holds ``envs/<version>/`` (a venv with the system's packages, the release's wheel
installed ``--no-deps --no-index``), ``bin/gov`` (a link switched by an atomic rename) and ``pin.json``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from gov import release
from gov.install import dispatch, locate, pin, probe
from gov.doctor import install as doctor_install

from .conftest import git, new_project


def _tree(path: Path) -> dict:
    """Every entry under ``path`` by type, link target, sha256 and mode; ``None`` when absent."""
    if not os.path.lexists(path):
        return None
    found = {}
    for top, names, files in os.walk(path):
        for name in names + files:
            entry = Path(top) / name
            rel = entry.relative_to(path).as_posix()
            if entry.is_symlink():
                found[rel] = ("link", os.readlink(entry))
            elif entry.is_file():
                found[rel] = ("file", hashlib.sha256(entry.read_bytes()).hexdigest(), entry.stat().st_mode)
            else:
                found[rel] = ("dir", entry.stat().st_mode)
    return found


def _no_pythonpath() -> dict:
    return {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}


# --------------------------------------------------------------------------
# The git common dir, found without a subprocess
# --------------------------------------------------------------------------

def test_common_dir_of_a_main_tree_is_its_dot_git_from_any_subfolder(tmp_path):
    repo = tmp_path / "repo"
    (repo / "a" / "b").mkdir(parents=True)
    git(repo, "init", "-q")
    assert locate.common_dir(repo / "a" / "b") == (repo / ".git").resolve()


def test_common_dir_of_a_linked_worktree_is_the_main_tree_s(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "commit", "-q", "--allow-empty", "-m", "first")
    git(repo, "worktree", "add", "-q", str(tmp_path / "linked"), "-b", "side")
    assert locate.common_dir(tmp_path / "linked") == (repo / ".git").resolve()


def test_common_dir_outside_a_repository_is_none(tmp_path):
    assert locate.common_dir(tmp_path) is None


# --------------------------------------------------------------------------
# The dispatch
# --------------------------------------------------------------------------

def _fake_pin(repo: Path) -> tuple[Path, Path]:
    env = repo / ".git" / "gov" / "envs" / "1.0.0"
    (env / "bin").mkdir(parents=True)
    (env / "bin" / "gov").write_text("#!/bin/sh\n", encoding="utf-8")
    (repo / ".git" / "gov" / "bin").mkdir()
    os.symlink(env / "bin" / "gov", repo / ".git" / "gov" / "bin" / "gov")
    return env, repo / ".git" / "gov" / "bin" / "gov"


def test_dispatch_targets_the_pin_without_pythonpath(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    env, link = _fake_pin(repo)
    found = dispatch.target(str(repo), {"PYTHONPATH": "/x/src", "HOME": "/h"}, "/usr")
    assert found is not None
    program, environ = found
    assert program == str(link)
    assert "PYTHONPATH" not in environ and environ["HOME"] == "/h"


def test_dispatch_never_reruns_the_pin_s_own_gov(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    env, _ = _fake_pin(repo)
    assert dispatch.target(str(repo), {}, str(env)) is None


def test_dispatch_is_off_with_gov_pin_off_or_without_a_pin(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    assert dispatch.target(str(repo), {}, "/usr") is None
    _fake_pin(repo)
    assert dispatch.target(str(repo), {"GOV_PIN": "off"}, "/usr") is None


def test_dispatch_does_not_follow_a_link_whose_environment_is_gone(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    env, link = _fake_pin(repo)
    os.unlink(env / "bin" / "gov")
    assert dispatch.target(str(repo), {}, "/usr") is None


def test_dispatch_breaks_a_loop_through_a_pin_that_is_not_its_environment_s(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    _, link = _fake_pin(repo)
    _, environ = dispatch.target(str(repo), {}, "/usr")
    assert dispatch.target(str(repo), environ, "/usr") is None


def test_dispatch_hands_nothing_over_for_update_rollback(tmp_path):
    """W2-17 S7: the rollback is run by the gov that was started, not by the pin's (B's, the one in doubt)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    _fake_pin(repo)
    for argv in (["update", "--rollback"], ["--root", ".", "update", "--rollback", "--json"],
                 ["update", "--json", "--rollback"]):
        assert dispatch.target(str(repo), {}, "/usr", argv) is None
    # a version, a plain update, or --rollback after a bare -- are handed over as before
    for argv in (["update", "0.9.1"], ["doctor", "--rollback"], ["update", "--", "--rollback"], []):
        assert dispatch.target(str(repo), {}, "/usr", argv) is not None
    assert dispatch.target(str(repo), {}, "/usr") is not None


def test_gov_started_in_a_subfolder_of_a_pinned_repository_reruns_the_pin_with_its_arguments(tmp_path):
    repo = tmp_path / "repo"
    (repo / "sub").mkdir(parents=True)
    git(repo, "init", "-q")
    env, link = _fake_pin(repo)
    (env / "bin" / "gov").write_text('#!/bin/sh\necho "pinned $* PYTHONPATH=${PYTHONPATH-unset}"\n', encoding="utf-8")
    (env / "bin" / "gov").chmod(0o755)
    run = lambda **extra: subprocess.run(  # noqa: E731
        [sys.executable, "-m", "gov.cli.main", "--version"], cwd=str(repo / "sub"), capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(REPO / "src"), **extra})
    done = run()
    assert done.returncode == 0 and done.stdout.strip() == "pinned --version PYTHONPATH=unset", done.stderr
    done = run(GOV_PIN="off")
    assert done.stdout.startswith("gov ") and "pinned" not in done.stdout


# --------------------------------------------------------------------------
# The release: the wheel kept, the record verified at its tag
# --------------------------------------------------------------------------

def test_the_wheel_is_kept_when_asked_and_reproduces_the_manifest_s(tiny_source, tmp_path):
    manifest = tiny_source["manifests"]["1.0.0"]
    built = release._wheel(tiny_source["source"], manifest["commit"], keep=tmp_path)
    assert built["name"] == manifest["wheel"]["name"] and built["sha256"] == manifest["wheel"]["sha256"]
    assert hashlib.sha256(Path(built["path"]).read_bytes()).hexdigest() == built["sha256"]


def test_verify_at_reads_the_record_and_the_template_at_the_tag(tiny_source):
    data, digest, manifest = release.verify_at(tiny_source["source"], "1.0.1")
    assert manifest["version"] == "1.0.1" and hashlib.sha256(data).hexdigest() == digest


def test_verify_at_refuses_a_version_with_no_tag(tiny_source):
    with pytest.raises(release.ReleaseError) as refused:
        release.verify_at(tiny_source["source"], "9.9.9")
    assert refused.value.reason == "no_release" and "v9.9.9" in str(refused.value)


def test_verify_at_refuses_a_manifest_that_does_not_hash_and_a_changed_template_file(tmp_path, tiny_source):
    source = tmp_path / "copy"
    git(tmp_path, "clone", "-q", str(tiny_source["source"]), str(source))
    record = source / "docs/releases/1.0.1/manifest.json"
    record.write_text(record.read_text() + " ", encoding="utf-8")
    git(source, "commit", "-q", "-am", "tamper the manifest")
    git(source, "tag", "-f", "v1.0.1")
    with pytest.raises(release.ReleaseError) as refused:
        release.verify_at(source, "1.0.1")
    assert refused.value.reason == "manifest" and "manifest.sha256" in str(refused.value)
    git(source, "reset", "-q", "--hard", "HEAD~1")
    (source / "template/governance/kernel/note.md").write_text("changed\n", encoding="utf-8")
    git(source, "commit", "-q", "-am", "tamper a template file")
    git(source, "tag", "-f", "v1.0.1")
    with pytest.raises(release.ReleaseError) as refused:
        release.verify_at(source, "1.0.1")
    assert refused.value.reason == "files" and "governance/kernel/note.md" in str(refused.value)


# --------------------------------------------------------------------------
# gov install
# --------------------------------------------------------------------------

def test_install_refuses_a_version_the_source_has_no_tag_for_and_writes_nothing(tiny_source, tmp_path):
    project = new_project(tmp_path, tiny_source["source"])
    with pytest.raises(pin.InstallRefused) as refused:
        pin.install(project, "7.0.0")
    assert refused.value.reason == "no_release" and "no release v7.0.0" in str(refused.value)
    assert _tree(project / ".git" / "gov") is None


def test_install_refuses_a_wheel_file_that_does_not_hash_to_the_manifest(tiny_source, tmp_path):
    project = new_project(tmp_path, tiny_source["source"])
    name = tiny_source["manifests"]["1.0.0"]["wheel"]["name"]
    other = tmp_path / name
    other.write_bytes(b"not the wheel")
    with pytest.raises(pin.InstallRefused) as refused:
        pin.install(project, "1.0.0", wheel=other)
    text = str(refused.value)
    assert refused.value.reason == "wheel"
    assert tiny_source["manifests"]["1.0.0"]["wheel"]["sha256"] in text
    assert hashlib.sha256(b"not the wheel").hexdigest() in text and name in text
    assert _tree(project / ".git" / "gov") is None


def test_install_refuses_a_release_whose_built_wheel_is_not_the_manifest_s(tiny_source, tmp_path):
    project = new_project(tmp_path, tiny_source["source"])
    with pytest.raises(pin.InstallRefused) as refused:
        pin.install(project, "1.0.2")
    assert refused.value.reason == "wheel" and "0" * 64 in str(refused.value)
    assert _tree(project / ".git" / "gov") is None


def test_install_pins_the_release_then_reinstalls_and_switches(tiny_source, tmp_path):
    project = new_project(tmp_path, tiny_source["source"])
    common = (project / ".git").resolve()
    result = pin.install(project, "1.0.0")
    manifest = tiny_source["manifests"]["1.0.0"]
    env = common / "gov" / "envs" / "1.0.0"
    assert result == {"version": "1.0.0", "environment": str(env), "wheel": manifest["wheel"],
                      "hash_check": "passed", "link": str(common / "gov" / "bin" / "gov")}
    record = json.loads((common / "gov" / "pin.json").read_text())
    assert record["version"] == "1.0.0" and record["wheel"] == manifest["wheel"]
    assert record["hash_check"] == "passed" and record["environment"] == str(env)
    assert record["commit"] == manifest["commit"] and record["source"] == str(tiny_source["source"])
    data = git(tiny_source["source"], "show", "v1.0.0:docs/releases/1.0.0/manifest.json").encode()
    assert record["manifest_sha256"] == hashlib.sha256(data).hexdigest()
    out = subprocess.run([str(common / "gov" / "bin" / "gov"), "--version"], capture_output=True, text=True,
                         env=_no_pythonpath())
    assert out.stdout.split()[:2] == ["gov", "1.0.0"]
    dist = probe.distribution(env)
    assert dist is not None and not dist["editable"]

    again = pin.install(project, "1.0.0")
    assert again["environment"] == str(env)
    pin.install(project, "1.0.1")
    assert os.readlink(common / "gov" / "bin" / "gov") == str(common / "gov" / "envs" / "1.0.1" / "bin" / "gov")
    out = subprocess.run([str(common / "gov" / "bin" / "gov"), "--version"], capture_output=True, text=True,
                         env=_no_pythonpath())
    assert out.stdout.split()[:2] == ["gov", "1.0.1"]

    before = _tree(common / "gov")
    with pytest.raises(pin.InstallRefused):
        pin.install(project, "1.0.2")
    assert _tree(common / "gov") == before


def test_a_failed_environment_leaves_the_pin_folder_as_it_was(tiny_source, tmp_path, monkeypatch):
    project = new_project(tmp_path, tiny_source["source"])
    monkeypatch.setattr(pin, "_pip_install", lambda env, wheel: (_ for _ in ()).throw(
        pin.InstallRefused("environment", "pip failed")))
    with pytest.raises(pin.InstallRefused) as refused:
        pin.install(project, "1.0.0")
    assert refused.value.reason == "environment"
    assert _tree(project / ".git" / "gov") is None


# --------------------------------------------------------------------------
# The probe and doctor's section install
# --------------------------------------------------------------------------

def _dist(site: Path, editable: bool | None) -> None:
    info = site / "gov-1.0.0.dist-info"
    info.mkdir(parents=True)
    (info / "METADATA").write_text("Metadata-Version: 2.1\nName: gov\nVersion: 1.0.0\n", encoding="utf-8")
    if editable is not None:
        (info / "direct_url.json").write_text(json.dumps(
            {"url": "file:///somewhere", "dir_info": {"editable": editable}}), encoding="utf-8")


def test_probe_reads_an_editable_and_a_wheel_install(tmp_path):
    wheel_env, editable_env = tmp_path / "w", tmp_path / "e"
    _dist(wheel_env / "lib/python3.12/site-packages", None)
    _dist(editable_env / "lib/python3.12/site-packages", True)
    assert probe.distribution(wheel_env)["editable"] is False
    assert probe.distribution(editable_env)["editable"] is True
    assert probe.distribution(tmp_path / "none") is None


def test_probe_names_a_source_tree(tmp_path):
    (tmp_path / "tree/src/gov").mkdir(parents=True)
    (tmp_path / "tree/pyproject.toml").write_text("", encoding="utf-8")
    assert probe.source_tree(tmp_path / "tree/src/gov")
    (tmp_path / "flat/gov").mkdir(parents=True)
    (tmp_path / "flat/pyproject.toml").write_text("", encoding="utf-8")
    assert not probe.source_tree(tmp_path / "flat/gov")


def _project_with_pin(tmp_path: Path, *, version="1.0.0", sha="a" * 64, lock_version="1.0.0", lock_sha="a" * 64,
                      editable=None, release=True) -> tuple[Path, Path]:
    project = tmp_path / "p"
    project.mkdir()
    git(project, "init", "-q")
    env = project / ".git" / "gov" / "envs" / version
    site = env / "lib/python3.12/site-packages"
    _dist(site, editable)
    (site / "gov").mkdir()
    (project / ".git/gov/pin.json").write_text(json.dumps(
        {"version": version, "wheel": {"name": f"gov-{version}-py3-none-any.whl", "sha256": sha},
         "environment": str(env), "hash_check": "passed"}), encoding="utf-8")
    manifest = json.dumps({"version": lock_version, "wheel": {"name": "w", "sha256": lock_sha}, "files": {}}).encode()
    entry = {"version": lock_version, "manifest_sha256": hashlib.sha256(manifest).hexdigest(),
             "manifest": base64.b64encode(manifest).decode()} if release else None
    import yaml
    (project / "governance").mkdir()
    (project / "governance/framework.lock").write_text(yaml.safe_dump({"release": entry}), encoding="utf-8")
    return project, env


def test_doctor_install_is_unmeasured_without_a_pin(tmp_path):
    git(tmp_path, "init", "-q")
    section = doctor_install.check(tmp_path)
    assert section["status"] == "unmeasured" and "gov install" in section["reason"]


def test_doctor_install_passes_from_the_pin_that_matches_the_lock(tmp_path):
    project, env = _project_with_pin(tmp_path)
    section = doctor_install.check(project, prefix=str(env), package=env / "lib/python3.12/site-packages/gov")
    assert section == {"status": "pass", "version": "1.0.0", "environment": str(env)}


@pytest.mark.parametrize("kwargs", [{"lock_version": "0.9.0"}, {"lock_sha": "b" * 64}, {"release": False}])
def test_doctor_install_fails_lock_when_the_pin_differs_from_the_lock(tmp_path, kwargs):
    project, env = _project_with_pin(tmp_path, **kwargs)
    section = doctor_install.check(project, prefix=str(env), package=env / "lib/python3.12/site-packages/gov")
    assert section["status"] == "fail" and section["case"] == "lock"


def test_doctor_install_fails_editable_also_when_it_is_a_source_tree(tmp_path):
    project, env = _project_with_pin(tmp_path, editable=True)
    tree = tmp_path / "tree"
    (tree / "src/gov").mkdir(parents=True)
    (tree / "pyproject.toml").write_text("", encoding="utf-8")
    section = doctor_install.check(project, prefix=str(env), package=tree / "src/gov")
    assert section["status"] == "fail" and section["case"] == "editable"


def test_doctor_install_fails_source_tree_naming_the_imported_path(tmp_path):
    project, env = _project_with_pin(tmp_path)
    tree = tmp_path / "tree"
    (tree / "src/gov").mkdir(parents=True)
    (tree / "pyproject.toml").write_text("", encoding="utf-8")
    section = doctor_install.check(project, prefix="/usr", package=tree / "src/gov")
    assert section["status"] == "fail" and section["case"] == "source_tree"
    assert str(tree / "src/gov") in section["reason"]


def test_doctor_install_fails_session_for_another_installed_gov(tmp_path):
    project, env = _project_with_pin(tmp_path)
    other = tmp_path / "other/lib/python3.12/site-packages/gov"
    other.mkdir(parents=True)
    section = doctor_install.check(project, prefix=str(tmp_path / "other"), package=other)
    assert section["status"] == "fail" and section["case"] == "session" and str(other) in section["reason"]


def test_doctor_reports_the_install_section_and_its_failure_fails_doctor(tmp_path, monkeypatch):
    from gov.cli.errors import GovError
    from gov.doctor import command
    for name in dir(command):
        if name.startswith("_check_") and name not in ("_check_adoption_level", "_check_install"):
            monkeypatch.setattr(command, name, lambda *args: {"status": "pass"})
    monkeypatch.setattr(command, "_check_install", lambda root: {"status": "unmeasured", "reason": "r"})
    assert command.run(tmp_path, None, {})["install"] == {"status": "unmeasured", "reason": "r"}
    monkeypatch.setattr(command, "_check_install", lambda root: {"status": "fail", "case": "lock", "reason": "r"})
    with pytest.raises(GovError) as failed:
        command.run(tmp_path, None, {})
    assert failed.value.exit_code == 3 and failed.value.details["install"]["case"] == "lock"


# --------------------------------------------------------------------------
# The kernel hooks: the template's command lines and the hook files
# --------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[3]
HOOKS_SOURCE = REPO / "template" / ".rulesync" / "hooks.jsonc"
HOOK_FILES = REPO / "template" / "governance" / "kernel" / "hooks"


def _hook_lines() -> list[tuple[str, str]]:
    text = "\n".join(line for line in HOOKS_SOURCE.read_text(encoding="utf-8").splitlines()
                     if not line.lstrip().startswith("//"))
    return [(f"{event}:{entry['command'].split('/hooks/')[1].split(chr(34))[0]}", entry["command"])
            for event, entries in json.loads(text)["hooks"].items() for entry in entries]


def _box(tmp_path: Path) -> dict:
    home, project, bin_dir = tmp_path / "home", tmp_path / "project", tmp_path / "bin"
    for folder in (home, project / "governance/kernel/hooks", bin_dir):
        folder.mkdir(parents=True)
    git(project, "init", "-q", "-b", "main")
    git(project, "commit", "-q", "--allow-empty", "-m", "first")
    return {"home": home, "project": project, "bin": bin_dir}


def _interpreter(folder: Path, name: str) -> Path:
    """A stand-in interpreter: records its name and arguments, then exits 0."""
    path = folder / name
    path.write_text(f"#!/bin/sh\necho \"{name} $*\" >> \"{folder}/ran\"\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def _gov_script(path: Path, interpreter: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!{interpreter}\nimport sys\n", encoding="utf-8")
    path.chmod(0o755)


def _run_line(line: str, box: dict, cwd: Path | None = None, project: Path | None = None):
    env = {"PATH": f"{box['bin']}:/usr/bin:/bin", "HOME": str(box["home"]), "LANG": "C.UTF-8",
           "CLAUDE_PROJECT_DIR": str(project or box["project"]), "GOV_TICKET": "DAEO-test"}
    return subprocess.run(["bash", "-c", line], input="{}", capture_output=True, text=True, env=env,
                          cwd=str(cwd or box["project"]), timeout=60)


@pytest.mark.parametrize("name,line", _hook_lines(), ids=[name for name, _ in _hook_lines()])
def test_each_hook_line_without_any_gov_exits_zero_saying_so_in_one_line(name, line, tmp_path):
    box = _box(tmp_path)
    done = _run_line(line, box)
    lines = [text for text in done.stderr.splitlines() if text.strip()]
    assert done.returncode == 0, f"{name}: exit {done.returncode}; {done.stderr!r}"
    assert len(lines) == 1 and lines[0].startswith("gov hook: no gov"), f"{name}: {done.stderr!r}"
    assert "bin/gov" in lines[0] and "PATH" in lines[0]


@pytest.mark.parametrize("name,line", _hook_lines(), ids=[name for name, _ in _hook_lines()])
def test_each_hook_line_runs_the_pin_s_interpreter_before_the_home_gov(name, line, tmp_path):
    box = _box(tmp_path)
    _gov_script(box["project"] / ".git/gov/bin/gov", _interpreter(tmp_path, "pinpy"))
    _gov_script(box["home"] / ".local/bin/gov", _interpreter(tmp_path, "homepy"))
    done = _run_line(line, box)
    program = name.split(":")[1]
    assert done.returncode == 0, f"{name}: {done.stderr!r}"
    assert (tmp_path / "ran").read_text().split() == [
        "pinpy", "-E", str(box["project"] / "governance/kernel/hooks" / program)]


@pytest.mark.parametrize("name,line", _hook_lines(), ids=[name for name, _ in _hook_lines()])
def test_each_hook_line_reads_the_interpreter_of_a_long_path_console_script(name, line, tmp_path):
    """pip writes a console script whose interpreter path is longer than a shebang allows as distlib's /bin/sh
    trampoline: the interpreter is on its second line."""
    box = _box(tmp_path)
    interpreter = _interpreter(tmp_path, "pinpy")
    script = box["project"] / ".git/gov/bin/gov"
    script.parent.mkdir(parents=True)
    script.write_text(f"#!/bin/sh\n'''exec' {interpreter} \"$0\" \"$@\"\n' '''\nimport sys\n", encoding="utf-8")
    script.chmod(0o755)
    done = _run_line(line, box)
    assert done.returncode == 0, f"{name}: {done.stderr!r}"
    assert (tmp_path / "ran").read_text().split()[:2] == ["pinpy", "-E"], done.stderr


def test_a_hook_line_in_a_linked_worktree_finds_the_pin_through_the_common_dir(tmp_path):
    box = _box(tmp_path)
    _gov_script(box["project"] / ".git/gov/bin/gov", _interpreter(tmp_path, "pinpy"))
    linked = tmp_path / "linked"
    git(box["project"], "worktree", "add", "-q", str(linked), "-b", "side")
    line = dict(_hook_lines())["stop:stop.py"]
    done = _run_line(line, box, cwd=linked, project=linked)
    assert done.returncode == 0 and (tmp_path / "ran").read_text().split()[0] == "pinpy", done.stderr


def test_without_a_pin_a_hook_line_runs_the_home_gov_s_interpreter(tmp_path):
    box = _box(tmp_path)
    _gov_script(box["home"] / ".local/bin/gov", _interpreter(tmp_path, "homepy"))
    done = _run_line(dict(_hook_lines())["preCompact:precompact.py"], box)
    assert done.returncode == 0 and (tmp_path / "ran").read_text().split()[0] == "homepy", done.stderr


MARKER_RECORD = "import os\nopen(os.environ['W218_MARKER'], 'w').close()\ndef write(*a, **k):\n    pass\n" \
                "def brief(*a, **k):\n    return {}\n"


def _product_gov(root: Path) -> None:
    for rel, text in (("src/gov/__init__.py", ""), ("src/gov/checkpoint/__init__.py", ""),
                      ("src/gov/checkpoint/record.py", MARKER_RECORD)):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")


@pytest.mark.parametrize("hook", ["precompact.py", "stop.py"])
def test_a_hook_file_never_imports_the_product_s_own_gov(hook, tmp_path):
    project = tmp_path / "product"
    _product_gov(project)
    marker = tmp_path / "marker"
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "CLAUDE_PROJECT_DIR": str(project),
           "GOV_TICKET": "DAEO-test", "W218_MARKER": str(marker), "PYTHONPATH": str(REPO / "src")}
    subprocess.run([sys.executable, str(HOOK_FILES / hook)], input="{}", capture_output=True, text=True, env=env,
                   cwd=str(project), timeout=60)
    assert not marker.exists(), f"{hook} imported the product's own src/gov"


def test_precompact_still_puts_src_first_in_the_gov_os_source_tree(tmp_path):
    tree = tmp_path / "gov-os"
    _product_gov(tree)
    (tree / "copier.yml").write_text("", encoding="utf-8")
    (tree / "template").mkdir()
    marker = tmp_path / "marker"
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "CLAUDE_PROJECT_DIR": str(tree),
           "GOV_TICKET": "DAEO-test", "W218_MARKER": str(marker), "PYTHONPATH": str(REPO / "src")}
    subprocess.run([sys.executable, str(HOOK_FILES / "precompact.py")], input="{}", capture_output=True, text=True,
                   env=env, cwd=str(tree), timeout=60)
    assert marker.exists()


@pytest.mark.parametrize("hook", ["precompact.py", "stop.py"])
def test_a_hook_file_that_cannot_import_gov_says_so_in_one_line_and_exits_zero(hook, tmp_path):
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "CLAUDE_PROJECT_DIR": str(tmp_path),
           "GOV_TICKET": "DAEO-test"}
    done = subprocess.run([sys.executable, "-I", str(HOOK_FILES / hook)], input="{}", capture_output=True,
                          text=True, env=env, cwd=str(tmp_path), timeout=60)
    lines = [text for text in done.stderr.splitlines() if text.strip()]
    assert done.returncode == 0 and len(lines) == 1 and lines[0].startswith("gov hook: no gov"), done.stderr

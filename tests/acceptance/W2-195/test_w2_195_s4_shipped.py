"""success-4 (S4, Shipped; DEC-1204 (5); P-GOLDEN-RULE-1 section 3 S4; the lead's interface item 7).

- The kernel skill and its rulesync mirror are the approved text with its ``description`` quoted (sha256 ``3fd8864b...``,
  3683 bytes, version 1.0.0).
- ``gov.adopt.fabric.PACKAGED`` names ``template/governance/kernel/skills/judging-work`` once, and ``fabric.KERNEL_FOLDERS``
  holds the pair ``(template/governance/kernel/skills/judging-work, .claude/skills/judging-work)`` once.
- A wheel built from HEAD (``git archive`` of ``src/`` and ``pyproject.toml``, ``pip wheel --no-deps --no-build-isolation
  --no-index``, as W2-88's release form) carries ``gov/_shipped/template/governance/kernel/skills/judging-work/SKILL.md`` with
  the kernel bytes.
- The kit: ``copier copy`` from a clone of HEAD's ``copier.yml`` and ``template/`` delivers
  ``governance/kernel/skills/judging-work/SKILL.md`` and ``.rulesync/skills/judging-work/SKILL.md`` with the kernel bytes; after
  ``gov adapters generate``, ``.claude/skills/judging-work/SKILL.md`` is there, named ``judging-work``, version 1.0.0, its body
  the kernel's (rulesync rewrites the front matter and drops the blank line after it, so not the kernel's whole bytes:
  README, "The generated copy"), and so sections 1 to 3 byte for byte.

The wheel and the kit cases build from HEAD, so only committed work is in them.
"""

from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

import w2_195_support as s

SKILL_FOLDER = "template/governance/kernel/skills/judging-work"
TAG = "v0.0.0-w2-195"
IDENT = ["-c", "user.name=W2-195 acceptance", "-c", "user.email=w2-195@example.invalid", "-c", "commit.gpgsign=false",
         "-c", "core.hooksPath=/dev/null"]


def _run(argv, cwd: Path, what: str, env: dict | None = None, timeout: int = 600) -> subprocess.CompletedProcess:
    done = subprocess.run([str(a) for a in argv], cwd=str(cwd), env=env or s.child_env(cwd), capture_output=True,
                          timeout=timeout, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, (f"{what} failed (exit {done.returncode}):\n{done.stdout[-1500:]!r}\n"
                                  f"{done.stderr[-2500:]!r}")
    return done


def _export(names: list[str], dest: Path, scratch: Path) -> None:
    """Each named folder or file of HEAD (never the working tree, never the whole tree) into ``dest``."""
    dest.mkdir(parents=True, exist_ok=True)
    for name in names:
        if (s.REPO / name).is_dir():
            data = _run(["git", "-C", s.REPO / name, "archive", "--format=tar", f"--prefix={name}/", "HEAD"], scratch,
                        f"git archive HEAD of {name}").stdout
            with tarfile.open(fileobj=io.BytesIO(data)) as handle:
                handle.extractall(dest, filter="data")
        else:
            data = _run(["git", "-C", s.SRC, "show", f"HEAD:{name}"], scratch, f"git show HEAD:{name}").stdout
            (dest / name).write_bytes(data)


@pytest.mark.parametrize("rel", [s.KERNEL_SKILL_REL, s.MIRROR_REL], ids=["kernel", "rulesync-mirror"])
def test_s4_the_kernel_skill_and_its_mirror_are_the_approved_bytes(rel):
    """success-4: ``<rel>`` exists and is the approved text with its description quoted: sha256 ``3fd8864b...``, 3683 bytes,
    front matter ``version: "1.0.0"``."""
    path = s.REPO / rel
    assert path.is_file(), f"{rel} does not exist: the skill is not in the kernel"
    data = path.read_bytes()
    assert s.sha256(data) == s.KERNEL_SHA256 and len(data) == s.KERNEL_SIZE, (
        f"{rel} is not the approved bytes: sha256 {s.sha256(data)[:12]}, {len(data)} bytes")
    assert s.version_of(data.decode("utf-8")) == s.VERSION


def test_s4_fabric_packaged_and_kernel_folders_name_the_skill_once(tmp_path):
    """success-4 (the shipped-folder lists, exactly): ``fabric.PACKAGED`` holds ``template/governance/kernel/skills/
    judging-work`` once; ``fabric.KERNEL_FOLDERS`` holds ``(that, ".claude/skills/judging-work")`` once and no other pair
    with either side."""
    probe = ("import json; from gov.adopt import fabric; "
             "print(json.dumps({'packaged': list(fabric.PACKAGED), 'folders': [list(p) for p in fabric.KERNEL_FOLDERS]}))")
    done = _run([sys.executable, "-B", "-c", probe], tmp_path, "reading gov.adopt.fabric's lists")
    lists = json.loads(done.stdout.decode("utf-8").strip().splitlines()[-1])
    assert lists["packaged"].count(SKILL_FOLDER) == 1, f"fabric.PACKAGED names {SKILL_FOLDER} {lists['packaged'].count(SKILL_FOLDER)} times"
    pairs = [pair for pair in lists["folders"] if SKILL_FOLDER in pair or ".claude/skills/judging-work" in pair]
    assert pairs == [[SKILL_FOLDER, ".claude/skills/judging-work"]], f"fabric.KERNEL_FOLDERS' judging-work pairs: {pairs}"


def test_s4_a_wheel_built_from_head_carries_the_skill_bytes(tmp_path):
    """success-4 (the release): the wheel built from HEAD's ``src/`` and ``pyproject.toml`` holds
    ``gov/_shipped/template/governance/kernel/skills/judging-work/SKILL.md``, byte for byte the approved kernel bytes."""
    export, wheels = tmp_path / "export", tmp_path / "wheelhouse"
    _export(["src", "pyproject.toml"], export, tmp_path)
    wheels.mkdir()
    env = s.child_env(tmp_path, {"PIP_NO_INDEX": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1", "TMPDIR": str(tmp_path)})
    env.pop("PYTHONPATH", None)
    _run([sys.executable, "-m", "pip", "wheel", "-q", "--no-deps", "--no-build-isolation", "--no-index", "-w", wheels, export],
         tmp_path, "building the wheel", env=env)
    built = sorted(wheels.glob("gov-*.whl"))
    assert len(built) == 1, f"the wheel was not built: {list(wheels.iterdir())}"
    member = f"gov/_shipped/{SKILL_FOLDER}/SKILL.md"
    with zipfile.ZipFile(built[0]) as wheel:
        names = wheel.namelist()
        assert member in names, f"the wheel of HEAD does not carry {member}"
        data = wheel.read(member)
    assert s.sha256(data) == s.KERNEL_SHA256, f"the wheel's {member} is not the kernel bytes (sha256 {s.sha256(data)[:12]})"


def test_s4_the_kit_delivers_the_skill_and_adapters_generate_preloads_it(tmp_path):
    """success-4 (the kit): ``copier copy --trust --defaults --skip-tasks`` of a clone of HEAD's ``copier.yml`` and
    ``template/`` (a planted tag) installs the kernel skill and its rulesync mirror with the kernel bytes; ``gov adapters
    generate --json`` then exits 0 and writes ``.claude/skills/judging-work/SKILL.md``: name ``judging-work``, version
    1.0.0, its body the kernel's, so sections 1 to 3 byte for byte."""
    copier = shutil.which("copier", path=s.search_path())
    if copier is None:
        pytest.skip("copier is not installed on this machine")
    if shutil.which("rulesync", path=s.search_path()) is None:
        pytest.skip("rulesync is not installed on this machine")
    clone, project = tmp_path / "clone", tmp_path / "project"
    _export(["copier.yml", "template"], clone, tmp_path)
    for step in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the kit"], ["tag", TAG]):
        _run(["git", "-C", clone, *IDENT, step[0], *step[1:]], tmp_path, f"git {step[0]} in the clone")
    project.mkdir()
    _run([copier, "copy", "--trust", "--defaults", "--skip-tasks", "--overwrite", "--quiet", "--vcs-ref", TAG, clone, project],
         tmp_path, "copier copy of the kit")
    kernel = s.kernel_text()
    for rel in ("governance/kernel/skills/judging-work/SKILL.md", ".rulesync/skills/judging-work/SKILL.md"):
        path = project / rel
        assert path.is_file(), f"copier copy of the kit installed no {rel}"
        assert s.sha256(path.read_bytes()) == s.KERNEL_SHA256, f"the kit's {rel} is not the kernel bytes"
    done = subprocess.run([sys.executable, "-B", "-m", "gov.cli.main", "adapters", "generate", "--json", "--root", str(project)],
                          cwd=str(project), env=s.child_env(tmp_path), capture_output=True, text=True, timeout=600,
                          stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"gov adapters generate failed on the kit: {s.describe(done)}"
    generated = project / s.PRELOADED_REL
    assert generated.is_file(), f"gov adapters generate wrote no {s.PRELOADED_REL}"
    text = generated.read_text(encoding="utf-8")
    assert s.front_matter(text).get("name") == s.SKILL, f"the generated copy is named {s.front_matter(text).get('name')!r}"
    assert s.version_of(text) == s.VERSION, f"the generated copy's version is {s.version_of(text)!r}"
    assert s.body(text) == s.body(kernel), "the generated copy's body is not the kernel's"
    assert s.sections(kernel) in text, "the generated copy does not hold sections 1 to 3 byte for byte"

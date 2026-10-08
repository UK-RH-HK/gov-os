"""KPI success 1 [CAP-44.a]: ``copier copy`` creates ``governance/``, the overlay (``_skip_if_exists``),
``.rulesync/``, the hooks and ``framework.lock`` with a file-hash manifest; ``gov doctor`` passes on the result.

With it, what the decisions add to the copy: the overlay is a path map that doctor's path-map part accepts
(DEC-493), the copy does not run the adapter generation and needs neither rulesync nor Node (DEC-488), and
the created project ignores ``.gov-runtime/`` and ``__pycache__/`` (DEC-493).

Every case creates its project with the registered Copier from a temporary
template source (``copier.yml`` and ``template/`` alone). The lock is read as a
file of the project; ``gov doctor`` is run as a command.
"""

from __future__ import annotations

import shutil

import w1_39_support as support


# --------------------------------------------------------------------------
# What copy creates
# --------------------------------------------------------------------------

def test_copy_installs_the_kernel_exactly_as_the_template_holds_it(installed, pristine_source):
    """``governance/kernel/`` of the project holds every kernel file of the template, byte for byte, and no other."""
    shipped = pristine_source.plain_files(support.KERNEL_REL)
    assert shipped, "the template source has no kernel file"
    different = [rel for rel, origin in shipped.items()
                 if not (installed / rel).is_file() or support.sha256(installed / rel) != support.sha256(origin)]
    assert not different, f"kernel files missing from the project or changed by the copy: {different[:10]}"
    rendered = {rel for rel in support.files_under(installed, support.KERNEL_REL)} - set(shipped)
    suffix = pristine_source.suffix()
    unexplained = sorted(rel for rel in rendered if not (pristine_source.template / (rel + suffix)).is_file())
    assert not unexplained, f"the project's kernel holds files the template does not ship: {unexplained[:10]}"


def test_copy_installs_the_hooks_and_keeps_them_executable(installed, pristine_source):
    """Every hook of the template is at ``governance/kernel/hooks/`` with the permission bits it has in the template."""
    hooks = pristine_source.plain_files(support.HOOKS_REL)
    assert hooks, "the template source has no hook"
    missing = [rel for rel in hooks if not (installed / rel).is_file()]
    assert not missing, f"hooks missing from the project: {missing}"
    lost = [rel for rel, origin in hooks.items()
            if support.is_executable(origin) and not support.is_executable(installed / rel)]
    assert not lost, f"hooks that are executable in the template and not in the project: {lost}"


def test_copy_installs_the_rulesync_sources(installed, pristine_source):
    """``.rulesync/`` of the project holds every adapter source of the template, byte for byte (W1-38)."""
    shipped = pristine_source.plain_files(support.RULESYNC_REL)
    assert shipped, "the template source has no .rulesync/ file"
    different = [rel for rel, origin in shipped.items()
                 if not (installed / rel).is_file() or support.sha256(installed / rel) != support.sha256(origin)]
    assert not different, f".rulesync/ files missing from the project or changed by the copy: {different[:10]}"


def test_copy_creates_the_overlay(installed):
    """The created project has its overlay, ``governance/project/``: a path map, and nothing else (DEC-493).

    The path map lies where ``gov`` reads a project's path map: ``governance/project/path-map.yaml``.
    """
    files = support.files_under(installed, support.OVERLAY_REL) if (installed / support.OVERLAY_REL).is_dir() else []
    assert support.PATH_MAP_REL in files, \
        f"`copier copy` created no {support.PATH_MAP_REL} (the overlay of KPI success 1; DEC-493). It created: {files}"
    assert files == [support.PATH_MAP_REL], \
        f"`copier copy` created more in the overlay than the path map DEC-493 names: {files}"


def test_the_path_map_of_a_fresh_project_is_one_doctors_path_map_part_accepts(project, sandbox):
    """Minimal and valid: ``gov doctor`` reads the shipped path map and measures zero unclassified paths.

    Doctor's path-map part passes only when every tracked path of the project matches a pattern of the path
    map; with a path map present it is measured, and a failed part fails doctor (KPI success 1: doctor passes).
    The project's tracked paths are everything the copy wrote, committed.
    """
    result = support.doctor(project, sandbox)
    part = result.part(support.DOCTOR_PATH_MAP_SECTION)
    assert part.get("status") == "pass" and part.get("unclassified_count") == 0 and not part.get("unclassified"), \
        (f"gov doctor's path-map part does not accept the path map of a freshly created project "
         f"(wanted: measured, zero unclassified paths): {part}\n{result.run.describe()}")


def test_a_freshly_created_project_is_at_the_minimal_adoption_level(project, sandbox):
    """CAP-54: a repository with only the kernel installed passes ``gov doctor`` at the minimal level."""
    result = support.doctor(project, sandbox)
    part = result.part(support.DOCTOR_LEVEL_SECTION)
    assert part.get("level") == "MINIMAL" and result.run.returncode == 0, \
        f"gov doctor does not pass at the level MINIMAL on a freshly created project: {part}\n{result.run.describe()}"


def test_copy_into_a_folder_that_has_an_overlay_file_keeps_it(copier_bin, source, sandbox, tmp_path):
    """``_skip_if_exists`` at install: an overlay file the folder already holds is not replaced by the template's."""
    rel = "governance/project/notes/local.md"
    support.write_template_file(source, rel, "the template's own text\n")
    support.git(source.path, "tag", "-d", support.FIRST_TAG)
    support.release(source.path, support.FIRST_TAG, "a release that ships an overlay file")
    destination = tmp_path / "product"
    (destination / rel).parent.mkdir(parents=True)
    (destination / rel).write_text("the project's own text\n", encoding="utf-8")
    done = support.copy(copier_bin, sandbox, source, destination)
    assert done.returncode == 0, f"`copier copy` failed\n{done.describe()}"
    assert (destination / rel).read_text(encoding="utf-8") == "the project's own text\n", \
        f"`copier copy` replaced the existing overlay file {rel}\n{done.describe()}"
    assert (destination / support.KERNEL_REL).is_dir(), "the kernel was not installed beside the existing overlay"


def test_copy_into_a_folder_that_has_a_path_map_keeps_it(copier_bin, source, sandbox, tmp_path, installed):
    """The same for the one overlay file the template ships: a path map the folder already holds is not replaced."""
    own = support.edited_by_the_project(support.path_map_text(installed))
    destination = tmp_path / "product"
    (destination / support.PATH_MAP_REL).parent.mkdir(parents=True)
    (destination / support.PATH_MAP_REL).write_text(own, encoding="utf-8")
    done = support.copy(copier_bin, sandbox, source, destination)
    assert done.returncode == 0, f"`copier copy` failed\n{done.describe()}"
    assert (destination / support.PATH_MAP_REL).read_text(encoding="utf-8") == own, \
        f"`copier copy` replaced the existing {support.PATH_MAP_REL}\n{done.describe()}"
    assert (destination / support.KERNEL_REL).is_dir(), "the kernel was not installed beside the existing overlay"


def test_copy_writes_the_answers_file_that_names_the_release(installed):
    """Copier's standard answers file is in the project and records the release it was created from (DEC-023)."""
    rel = support.ANSWERS_REL
    path = installed / rel
    assert path.is_file(), f"the project has no answers file {rel}: `copier update` has nothing to start from"
    assert support.FIRST_TAG in path.read_text(encoding="utf-8"), f"{rel} does not name the release {support.FIRST_TAG}"


# --------------------------------------------------------------------------
# What copy does not do: the adapter generation (DEC-488)
# --------------------------------------------------------------------------

def test_copy_writes_nothing_that_rulesync_generates(installed):
    """No ``.claude/``, ``CLAUDE.md`` or ``AGENTS.md`` after the copy: generating them is a step of its own."""
    present = [name for name in support.GENERATED_BY_RULESYNC if (installed / name).exists()]
    assert not present, \
        f"`copier copy` wrote {present}, which are generated from {support.RULESYNC_REL}/ by a step after the copy"


def test_copy_succeeds_where_rulesync_and_node_are_absent(copier_bin, source, sandbox, tmp_path):
    """An install does not fail where rulesync or Node is absent: neither is on the ``PATH`` the tasks find."""
    path = support.copier_environment(sandbox, without=support.ADAPTER_TOOLS)["PATH"]
    found = [name for name in support.ADAPTER_TOOLS if shutil.which(name, path=path)]
    assert not found, f"this case needs a PATH without {found}"
    assert shutil.which("git", path=path) and shutil.which("python3", path=path), \
        "this case needs git and python3 on the PATH it builds"
    project, done = support.create_project_and_run(copier_bin, sandbox, source, tmp_path / "product",
                                                   without=support.ADAPTER_TOOLS)
    assert support.manifest_of(project) and support.kernel_files(project), \
        f"`copier copy` without rulesync and node left no kernel or no lock manifest\n{done.describe()}"
    present = [name for name in support.GENERATED_BY_RULESYNC if (project / name).exists()]
    assert not present, f"`copier copy` wrote {present} although neither rulesync nor node was there to generate them"


# --------------------------------------------------------------------------
# The ignore file (DEC-493)
# --------------------------------------------------------------------------

def test_a_created_project_ignores_the_runtime_folder_and_bytecode_folders(project):
    """Files under ``.gov-runtime/`` and under a ``__pycache__/`` at any depth leave the tree clean; others do not."""
    ignored = (".gov-runtime/store.db", ".gov-runtime/snapshots/one.json", "__pycache__/top.cpython-312.pyc",
               "src/app/__pycache__/app.cpython-312.pyc", f"{support.HOOKS_REL}/__pycache__/hook.cpython-312.pyc")
    shown = ("src/app/app.py", "notes.md")
    assert not support.untracked(project), \
        f"the created project, committed, still shows untracked files: {support.untracked(project)}"
    for rel in (*ignored, *shown):
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_bytes(b"content\n")
    not_ignored = [rel for rel in ignored if not support.is_ignored(project, rel)]
    assert not not_ignored, f"the created project does not ignore {not_ignored} (DEC-493)"
    assert support.untracked(project) == sorted(shown), \
        f"git status of the created project shows {support.untracked(project)}, wanted exactly {sorted(shown)}"


def test_the_ignore_file_hides_no_installed_kernel_file(installed):
    """Every installed kernel file is tracked once the project is committed: the shipped ignore rules hide none."""
    tracked = set(support.git(installed, "ls-files", "-z").split("\0")) - {""}
    hidden = sorted(set(support.kernel_files(installed)) - tracked)
    assert not hidden, f"installed kernel files that the project's ignore rules keep out of git: {hidden[:10]}"


# --------------------------------------------------------------------------
# The lock and its manifest
# --------------------------------------------------------------------------

def test_copy_writes_the_lock_where_the_product_layout_places_it(installed):
    """``governance/framework.lock`` exists in the created project and is one YAML map (ADR-0002 section 5)."""
    assert support.read_lock(installed), f"{support.LOCK_REL} is empty"


def test_the_manifest_lists_every_installed_kernel_file_with_its_sha256(installed):
    """Each file under ``governance/kernel/`` is in the manifest, by its path from the project root, with its hash."""
    manifest = support.manifest_of(installed)
    wrong = []
    for rel in support.kernel_files(installed):
        recorded = manifest.get(rel)
        if recorded != support.sha256(installed / rel):
            wrong.append((rel, recorded))
    assert not wrong, f"kernel files absent from the manifest, or listed with another hash than their sha256: {wrong[:5]}"


def test_every_manifest_entry_is_a_file_of_the_project_with_that_sha256(installed):
    """No entry names a file that is not there, and every hash is the sha256 of the file it stands beside."""
    wrong = []
    for rel, recorded in support.manifest_of(installed).items():
        path = installed / str(rel)
        if not (isinstance(recorded, str) and support.SHA256_RE.fullmatch(recorded)) or not path.is_file() \
                or support.sha256(path) != recorded:
            wrong.append((rel, recorded))
    assert not wrong, f"manifest entries that are not the sha256 of an existing file: {wrong[:5]}"


def test_the_manifest_leaves_out_the_overlay_and_the_lock_itself(installed):
    """The overlay is the project's to change, so it is not locked; the lock and the answers file are not kernel files."""
    listed = [str(rel) for rel in support.manifest_of(installed)]
    overlay = [rel for rel in listed if rel == support.OVERLAY_REL or rel.startswith(support.OVERLAY_REL + "/")]
    assert not overlay, f"the manifest lists overlay files, which a project may change: {overlay[:5]}"
    own = [rel for rel in listed if rel in (support.LOCK_REL, support.ANSWERS_REL)]
    assert not own, f"the manifest lists the lock or the answers file: {own}"


# --------------------------------------------------------------------------
# gov doctor passes on the result
# --------------------------------------------------------------------------

def test_doctor_passes_on_a_freshly_created_project(project, sandbox):
    """``gov doctor`` exits 0 on the project, no part of it fails, and its lock part is measured: MATCH."""
    result = support.doctor(project, sandbox)
    failed = sorted(name for name, part in result.report.items()
                    if isinstance(part, dict) and part.get("status") in ("fail", "drift"))
    assert result.run.returncode == 0 and result.run.envelope().get("ok") is True and not failed, \
        f"gov doctor does not pass on a freshly created project (failed parts: {failed})\n{result.run.describe()}"
    assert result.claims_match and result.section.get("status") == "pass" and not result.reports_drift, \
        f"gov doctor's lock part is not a measured MATCH on a freshly created project\n{result.describe()}"


def test_doctor_reads_the_lock_and_leaves_it_as_it_was(project, sandbox):
    """Doctor only reads: the lock and the kernel are byte for byte what they were before it ran."""
    before = {rel: support.sha256(project / rel) for rel in [support.LOCK_REL, *support.kernel_files(project)]}
    support.doctor(project, sandbox)
    after = {rel: support.sha256(project / rel) for rel in before if (project / rel).is_file()}
    assert after == before, "gov doctor changed the lock or a kernel file"

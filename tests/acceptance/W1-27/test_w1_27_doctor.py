"""KPI success 1 and failure 1: ``gov doctor`` reports installation health.

Success: doctor reports pinned vs found tool versions, hooks wired, path map
with zero unclassified paths, index freshness, canaries, framework.lock
MATCH/DRIFT, per-repository isolation; non-zero on any failure
[CAP-02.a, CAP-06.a, CAP-25.a].

Failure: doctor passes with a tool at the wrong version.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import w1_27_support as support
import w2_67_doctor
import w2_67b_support

# Section names the doctor report must contain (the contract does not fix their
# spelling, so the tests look for a recognisable substring in the result keys or
# in the JSON-serialised result).
REPORT_SECTIONS = (
    "tool",           # pinned vs found tool versions
    "hook",           # hooks wired
    "path",           # path-map coverage / unclassified paths
    "index",          # index freshness
    "canar",          # canaries
    "framework",      # framework.lock MATCH/DRIFT
    "isolation",      # per-repository isolation
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _doctor_sections(envelope):
    """Extract doctor's full result dict from either a healthy or unhealthy envelope."""
    if envelope.get("ok"):
        return envelope.get("result", {})
    return envelope.get("error", {}).get("details", {})


def _make_real_home_sandbox(tmp_path):
    """A sandbox with HOME pointing to the real user's home."""
    base = tmp_path / "real-home-sandbox"
    for name in ("tmp", "bin", "pycache", "elsewhere"):
        (base / name).mkdir(parents=True, exist_ok=True)
    return support.base.Sandbox(
        home=Path.home(),
        tmpdir=base / "tmp",
        bin=base / "bin",
        pycache=base / "pycache",
        elsewhere=base / "elsewhere",
    )


# --------------------------------------------------------------------------
# Command identity
# --------------------------------------------------------------------------

def test_doctor_is_a_read_command(gov, project, interface, tmp_path):
    """``doctor`` is a read command (CAP-27, DEC-317): it returns an envelope and never changes the working tree.

    Revised after implementation: doctor verifies every registry entry under
    the session's home (DEC-452); the case built its healthy project from
    this repository's registry and so depended on the real machine.
    """
    tool_dir = tmp_path / "fake-tools" / "bin"
    tool_dir.mkdir(parents=True)
    _, sha = support.fake_tool(tool_dir, "read-cmd-tool", "1.0.0")
    registry = support.tool_entry_with_location_yaml(
        "read-cmd-tool", "1.0.0", sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)

    before = support.snapshot(project)
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert isinstance(envelope, dict), run.describe()
    after = support.snapshot(project)
    diff = support.snapshot_difference(before, after)
    assert not diff, (
        f"doctor changed the project:\n" + "\n".join(diff) + f"\n{run.describe()}"
    )


def test_doctor_envelope_is_valid_on_healthy_project(gov, project, interface, tmp_path):
    """A project with all health indicators met gives ok=true, exit 0.

    Revised after implementation: doctor verifies every registry entry under
    the session's home (DEC-452); the case built its healthy project from
    this repository's registry and so depended on the real machine.
    """
    tool_dir = tmp_path / "fake-tools" / "bin"
    tool_dir.mkdir(parents=True)
    _, sha = support.fake_tool(tool_dir, "healthy-tool", "2.0.0")
    registry = support.tool_entry_with_location_yaml(
        "healthy-tool", "2.0.0", sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)
    support.write_path_map(project, support.minimal_valid_path_map())
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert envelope["ok"] is True, f"doctor is not ok on a healthy project\n{run.describe()}"
    assert run.returncode == 0, f"exit code is not 0 on a healthy project\n{run.describe()}"


# --------------------------------------------------------------------------
# Machine-dependent: real registry, real home
# --------------------------------------------------------------------------

def test_doctor_real_registry_every_entry_reported(project, tmp_path, interface):
    """Machine-dependent: runs doctor against this repository's real
    registry with the real home.  Asserts only what holds on any machine:
    the tools section lists every registry entry by name, and every entry
    is either ok with the way it passed or not ok with a reason.  It does
    not assert that the machine is healthy.

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion matches a key name
    that doctor always emits): its "not ok with a reason" half was met by
    ``pinned_version``, which every entry carries.  A not-ok entry now
    names its cause: a reason, a version read other than the pin, or a
    hash not matched; an ok entry shows a version read or the hash matched
    (DEC-452).
    """
    reg_path = project / "governance" / "project" / "tool-registry.yaml"
    if not reg_path.is_file():
        pytest.skip("no tool-registry.yaml in the project")

    reg_text = reg_path.read_text(encoding="utf-8")
    expected_names = set()
    for m in re.finditer(r"^\s*-\s*name:\s*(.+)$", reg_text, re.MULTILINE):
        expected_names.add(m.group(1).strip())
    assert expected_names, "no tool names found in the registry"

    sandbox = _make_real_home_sandbox(tmp_path)
    run = support.run_gov(project, sandbox, "doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    sections = _doctor_sections(envelope)

    tools_section = sections.get("tools", {})
    entries = tools_section.get("tools", [])
    reported = {}
    for entry in entries:
        if isinstance(entry, dict) and "name" in entry:
            reported[entry["name"]] = entry

    # "claude code" has its own dedicated section (claude_code) in the
    # doctor report, separate from the tools list.
    tools_expected = expected_names - {"claude code"}
    missing = tools_expected - set(reported.keys())
    assert not missing, (
        f"registry entries not reported by doctor: {sorted(missing)}\n"
        f"reported: {sorted(reported.keys())}\n{run.describe()}"
    )

    if "claude code" in expected_names:
        assert "claude_code" in sections, (
            f"'claude code' is in the registry but doctor has no "
            f"claude_code section\n{run.describe()}"
        )

    for name, entry in reported.items():
        assert "ok" in entry, (
            f"entry '{name}' has no 'ok' field: {entry}"
        )
        found, pinned = entry.get("found_version"), entry.get("pinned_version")
        if entry["ok"] is True:
            # The way it passed (DEC-452): a version read, or the hash matched. (Whether the version read must
            # equal the pin as text is a finding for doctor's owner: reranker-venv passes with torch 2.14.1
            # read against a pin of 2.14.1+cu130, W2-67 batch 1b.)
            assert found is not None or entry.get("sha256_match") is True, (
                f"entry '{name}' is ok but shows neither a version read nor the hash matched (DEC-452): "
                f"{entry}\n{run.describe()}"
            )
        else:
            # A not-ok entry names its cause: a reason, a version read that is not the pin, or a hash not matched.
            assert (entry.get("reason") or (found is not None and found != pinned)
                    or entry.get("sha256_match") is False), (
                f"entry '{name}' is not ok but says nothing about why (no reason, no version read other than "
                f"the pin, no hash mismatch): {entry}\n{run.describe()}"
            )


# --------------------------------------------------------------------------
# Report contents: each section is present
#
# Revised (W2-67, I4 F1; Rewrite-Reason: the assertion matches a key name that doctor always emits): each case
# found one word anywhere in the output, and doctor prints every section key on every run. Each now reads its
# section's typed fields (w2_67_doctor.section: in result, or in error.details when doctor is unhealthy) on small
# committed projects of its own with this worktree's code, with one input that makes the section measure something
# and, where the section can pass, one that it must not pass.
# --------------------------------------------------------------------------

def _tool_entries(run):
    """The tools section's entries by name."""
    tools = w2_67_doctor.section(run, "tools")
    entries = tools.get("tools")
    assert isinstance(entries, list), f"the tools section has no list of entries: {tools}\n{run.describe()}"
    return tools, {entry["name"]: entry for entry in entries if isinstance(entry, dict) and "name" in entry}


def test_doctor_report_mentions_tool_versions(sandbox, tmp_path):
    """The doctor result mentions tool version information (CAP-25.a): pinned and found, per entry."""
    project = w2_67_doctor.small_project(tmp_path / "repo")
    tool_dir = tmp_path / "fake-tools" / "bin"
    tool_dir.mkdir(parents=True)
    _, sha_pinned = support.fake_tool(tool_dir, "pinned-tool", "2.0.0")
    _, sha_drifted = support.fake_tool(tool_dir, "drifted-tool", "9.9.9")
    support.write_tool_registry(project, "\n".join((
        support.tool_entry_with_location_yaml("pinned-tool", "2.0.0", sha_pinned, str(tool_dir)),
        support.tool_entry_with_location_yaml("drifted-tool", "1.0.0", sha_drifted, str(tool_dir)),
    )))
    run = w2_67_doctor.doctor(project, sandbox)
    tools, entries = _tool_entries(run)
    pinned, drifted = entries.get("pinned-tool", {}), entries.get("drifted-tool", {})
    assert (pinned.get("pinned_version"), pinned.get("found_version"), pinned.get("ok")) == ("2.0.0", "2.0.0", True), (
        f"the tool at its pinned version is not reported as pinned 2.0.0, found 2.0.0, ok: {pinned}\n{run.describe()}"
    )
    assert (drifted.get("pinned_version"), drifted.get("found_version")) == ("1.0.0", "9.9.9"), (
        f"the tool at another version is not reported as pinned 1.0.0, found 9.9.9: {drifted}\n{run.describe()}"
    )
    assert drifted.get("ok") is not True and tools.get("status") != "pass", (
        f"a tool found at 9.9.9 against a pin of 1.0.0 passes: {tools}\n{run.describe()}"
    )


def test_doctor_report_mentions_hooks(sandbox, tmp_path):
    """The doctor result mentions hooks (wired or not): config_present follows the project's lefthook.yml."""
    bare = w2_67_doctor.small_project(tmp_path / "bare")
    hooked = w2_67_doctor.small_project(tmp_path / "hooked")
    w2_67b_support.write_committed(hooked, "lefthook.yml", 'pre-commit:\n  commands:\n    noop:\n      run: "true"\n')
    bare_run = w2_67_doctor.doctor(bare, sandbox)
    bare_hooks = w2_67_doctor.section(bare_run, "hooks")
    assert bare_hooks.get("config_present") is False and bare_hooks.get("status") != "pass", (
        f"doctor reports hooks wired on a project with no lefthook.yml: {bare_hooks}\n{bare_run.describe()}"
    )
    hooked_run = w2_67_doctor.doctor(hooked, sandbox)
    hooked_hooks = w2_67_doctor.section(hooked_run, "hooks")
    assert hooked_hooks.get("config_present") is True, (
        f"doctor does not see the project's lefthook.yml: {hooked_hooks}\n{hooked_run.describe()}"
    )
    assert isinstance(hooked_hooks.get("binary_installed"), bool), (
        f"the hooks section does not say whether the hook binary is installed: {hooked_hooks}\n{hooked_run.describe()}"
    )


def test_doctor_report_mentions_path_map_coverage(sandbox, tmp_path):
    """The doctor result mentions path-map coverage (CAP-06.a): zero unclassified paths."""
    covered = w2_67_doctor.small_project(tmp_path / "covered")
    w2_67b_support.write_committed(covered, "docs/guide.md", "covered by **\n")
    covered_run = w2_67_doctor.doctor(covered, sandbox)
    covered_map = w2_67_doctor.section(covered_run, "path_map")
    assert (covered_map.get("unclassified_count"), covered_map.get("unclassified")) == (0, []), (
        f"doctor does not report zero unclassified paths under a path map of `**`: {covered_map}\n"
        f"{covered_run.describe()}"
    )
    narrow = w2_67_doctor.small_project(tmp_path / "narrow")
    w2_67b_support.write_committed(narrow, "docs/guide.md", "outside src/**\n")
    support.write_path_map(narrow, support.minimal_valid_path_map().replace('paths: ["**"]', 'paths: ["src/**"]'))
    narrow_run = w2_67_doctor.doctor(narrow, sandbox)
    narrow_map = w2_67_doctor.section(narrow_run, "path_map")
    assert "docs/guide.md" in (narrow_map.get("unclassified") or []) and narrow_map.get("unclassified_count", 0) >= 1, (
        f"doctor does not count docs/guide.md as unclassified under a path map of `src/**`: {narrow_map}\n"
        f"{narrow_run.describe()}"
    )


def test_doctor_report_mentions_index_freshness(sandbox, tmp_path):
    """The doctor result mentions index freshness: missing before a rebuild, fresh after it, stale after a change."""
    project = support.make_rebuild_project(support.REPO_ROOT, tmp_path / "repo")
    w2_67b_support.write_committed(project, "docs/kept.md", "a document that does not change\n")
    w2_67b_support.write_committed(project, "docs/changed.md", "a document that changes\n")
    before_run = w2_67_doctor.doctor(project, sandbox)
    before = w2_67_doctor.section(before_run, "index_freshness")
    assert before.get("index_status") != "fresh" and before.get("status") != "pass", (
        f"doctor reports a fresh index before any index was built: {before}\n{before_run.describe()}"
    )
    rebuild = support.run_gov_with_code(support.REPO_ROOT, project, sandbox, "rebuild", "--json")
    assert rebuild.returncode == 0, f"gov rebuild failed\n{rebuild.describe()}"
    fresh_run = w2_67_doctor.doctor(project, sandbox)
    fresh = w2_67_doctor.section(fresh_run, "index_freshness")
    assert (fresh.get("index_status"), fresh.get("stale"), fresh.get("status")) == ("fresh", [], "pass"), (
        f"doctor does not report the index fresh right after a rebuild: {fresh}\n{fresh_run.describe()}"
    )
    w2_67b_support.write_committed(project, "docs/changed.md", "the changed text\n", "change a document")
    stale_run = w2_67_doctor.doctor(project, sandbox)
    stale = w2_67_doctor.section(stale_run, "index_freshness")
    assert "docs/changed.md" in (stale.get("stale") or []) and stale.get("status") != "pass", (
        f"doctor does not name docs/changed.md stale after it changed: {stale}\n{stale_run.describe()}"
    )
    assert "docs/kept.md" not in stale.get("stale"), (
        f"doctor names docs/kept.md stale although it did not change: {stale}\n{stale_run.describe()}"
    )


# revised after implementation (DEC-913 item 3; Rewrite-Reason: DEC-835): the canary runner reads its declarations
# from the project, never from its install path, so the canaries case's project carries the kernel's declarations,
# one named file per index, under governance/kernel/canaries/ where an adopted project holds them (DEC-579). Only
# that case calls it: every other case's project is as it was. The files stay untracked: a committed declaration
# holds its own queries, so the rebuilt index would hold them without the case's docs/canary.md and the case's
# second half would test nothing.
KERNEL_CANARIES_TEMPLATE_REL = "template/governance/kernel/canaries"
KERNEL_CANARIES_ADOPTED_REL = "governance/kernel/canaries"


def _carry_kernel_canaries(project):
    """The kernel's canary declarations in the project, where an adopted project holds them (DEC-579), untracked."""
    for index in ("lexical", "semantic"):
        target = project / KERNEL_CANARIES_ADOPTED_REL / f"{index}.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((support.REPO_ROOT / KERNEL_CANARIES_TEMPLATE_REL / f"{index}.yaml").read_text(
            encoding="utf-8"), encoding="utf-8")


def test_doctor_report_mentions_canaries(sandbox, tmp_path):
    """The doctor result mentions canaries: the lexical canary misses before an index holds its query, and
    passes once a rebuilt index holds it.

    Revised after implementation (DEC-913 item 3; Rewrite-Reason: DEC-835): the project carries the kernel's
    canary declarations (``_carry_kernel_canaries``); the assertions are unchanged."""
    project = support.make_rebuild_project(support.REPO_ROOT, tmp_path / "repo")
    _carry_kernel_canaries(project)
    before_run = w2_67_doctor.doctor(project, sandbox)
    before = w2_67_doctor.section(before_run, "canaries")
    lexical = (before.get("indices") or {}).get("lexical") or {}
    misses = lexical.get("misses")
    assert lexical.get("passed") is False and isinstance(misses, list) and misses, (
        f"the lexical canary does not miss on a project with no index: {before}\n{before_run.describe()}"
    )
    assert before.get("status") != "pass", f"canaries pass with no index: {before}\n{before_run.describe()}"
    w2_67b_support.write_committed(project, "docs/canary.md", "".join(f"{query}\n" for query in misses))
    rebuild = support.run_gov_with_code(support.REPO_ROOT, project, sandbox, "rebuild", "--json")
    assert rebuild.returncode == 0, f"gov rebuild failed\n{rebuild.describe()}"
    after_run = w2_67_doctor.doctor(project, sandbox)
    after = (w2_67_doctor.section(after_run, "canaries").get("indices") or {}).get("lexical") or {}
    assert after.get("passed") is True and after.get("misses") == [], (
        f"the lexical canary does not pass once the rebuilt index holds its queries {misses}: {after}\n"
        f"{after_run.describe()}"
    )


def test_doctor_report_mentions_framework_lock(sandbox, tmp_path):
    """The doctor result mentions framework.lock with MATCH or DRIFT (CAP-02.a): with nothing compared it says
    neither, and it never passes."""
    plain = w2_67_doctor.small_project(tmp_path / "plain")
    plain_run = w2_67_doctor.doctor(plain, sandbox)
    plain_lock = w2_67_doctor.section(plain_run, "framework_lock")
    assert plain_lock.get("match") not in ("MATCH", "DRIFT") and plain_lock.get("status") == "unmeasured", (
        f"a project with no framework.lock is not unmeasured (DEC-425): {plain_lock}\n{plain_run.describe()}"
    )
    installed = w2_67_doctor.small_project(tmp_path / "installed")
    w2_67b_support.write_committed(installed, ".copier-answers.yml", "_commit: v0.1.0\n")
    installed_run = w2_67_doctor.doctor(installed, sandbox)
    installed_lock = w2_67_doctor.section(installed_run, "framework_lock")
    assert installed_lock.get("match") != "MATCH" and installed_lock.get("status") == "fail", (
        f"an installed project without its framework.lock does not fail: {installed_lock}\n{installed_run.describe()}"
    )
    assert installed_lock.get("reason"), f"the failure gives no reason: {installed_lock}\n{installed_run.describe()}"


def test_doctor_report_mentions_isolation(sandbox, tmp_path):
    """The doctor result mentions per-repository isolation: unmeasured without a runtime folder, isolated with
    the project's own."""
    bare = w2_67_doctor.small_project(tmp_path / "bare")
    bare_run = w2_67_doctor.doctor(bare, sandbox)
    bare_isolation = w2_67_doctor.section(bare_run, "isolation")
    assert bare_isolation.get("status") == "unmeasured" and bare_isolation.get("isolated") is not True, (
        f"isolation is reported with no .gov-runtime to measure (DEC-425): {bare_isolation}\n{bare_run.describe()}"
    )
    own = w2_67_doctor.small_project(tmp_path / "own")
    (own / ".gov-runtime").mkdir()
    own_run = w2_67_doctor.doctor(own, sandbox)
    own_isolation = w2_67_doctor.section(own_run, "isolation")
    assert own_isolation.get("isolated") is True and own_isolation.get("status") == "pass", (
        f"the project's own .gov-runtime is not reported isolated: {own_isolation}\n{own_run.describe()}"
    )
    assert Path(own_isolation.get("git_root", "")).resolve() == own.resolve(), (
        f"the isolation section does not name the project's git root: {own_isolation}\n{own_run.describe()}"
    )


# --------------------------------------------------------------------------
# Exit code on failure
# --------------------------------------------------------------------------

def test_doctor_exit_nonzero_on_any_failure(gov, project, interface):
    """When any health check fails, exit code is non-zero."""
    registry = support.tool_entry_yaml("fake-tool", "99.99.99", "0" * 64,
                                       install="echo fake", uninstall="echo fake",
                                       date="2026-01-01", approved_by="test")
    support.write_tool_registry(project, registry)
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert run.returncode != 0, f"doctor exits 0 despite a health failure\n{run.describe()}"


# --------------------------------------------------------------------------
# Failure KPI 1: doctor passes with a tool at the wrong version
# --------------------------------------------------------------------------

def test_doctor_does_not_pass_with_wrong_tool_version(gov, project, interface):
    """A tool in the registry at a version that does not match what is found must cause doctor to report not-ok.

    The test writes a registry entry with a version that no real tool has, then asserts that doctor is not ok.
    """
    registry = support.tool_entry_yaml("node", "0.0.1-fake", "0" * 64,
                                       install="echo fake", uninstall="echo fake",
                                       date="2026-01-01", approved_by="test")
    support.write_tool_registry(project, registry)
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert envelope["ok"] is not True, \
        f"doctor passes with a tool at the wrong version\n{run.describe()}"

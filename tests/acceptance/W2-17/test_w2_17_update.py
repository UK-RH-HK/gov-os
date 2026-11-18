"""S2: `gov update <B>` moves an adopted project to release B without re-adopting (CAP-45.a, W2-M176)."""

from __future__ import annotations

import json
import subprocess

import w2_17_support as support


def _result(updated):
    run = updated.run
    assert run.returncode == 0, f"`gov update {support.B} --json` did not exit 0\n{run.describe()}"
    result = run.result()
    assert result.get("check") in (False, None) and result.get("to") == support.B, (
        f"the update's report is not that of the update to {support.B}\n{run.describe()}")
    return result


def test_update_gives_every_unchanged_shipped_file_release_b_bytes(updated, source):
    result = _result(updated)
    project = updated.project
    wrong = []
    for rel in source.shipped(support.TAG_B):
        if rel.endswith(".jinja") or support.w216.under(rel, support.OVERLAY) or rel in support.LOCALLY_CHANGED:
            continue
        path = project / rel
        if not path.is_file() or path.read_bytes() != source.template_bytes(support.TAG_B, rel):
            wrong.append(rel)
    assert not wrong, f"shipped files the project had not changed do not hold release B's bytes: {wrong[:20]}"
    assert not (project / support.REMOVED).exists(), f"{support.REMOVED}, removed by release B, is still there"
    support.assert_outcomes(result.get("files"), "the update's report")


def test_update_keeps_the_projects_change_and_every_overlay_file(updated):
    result = _result(updated)
    project = updated.project
    assert (project / support.KEPT).read_bytes() == updated.before_bytes[support.KEPT], (
        f"{support.KEPT}, changed by the project and not by release B, is not byte-identical to before")
    assert support.KEPT in support.outcome_lists(result.get("files"))["kept"], (
        f"{support.KEPT} is not reported kept\n{updated.run.describe()}")
    after = support.overlay_hashes(project)
    differing = sorted(rel for rel in set(after) | set(updated.before_overlay)
                       if after.get(rel) != updated.before_overlay.get(rel))
    assert not differing, f"files under {support.OVERLAY}/ are not byte-identical to before: {differing}"
    assert support.OVERLAY_CHANGED in updated.before_overlay, "fixture: the overlay file B changes was not there"


def test_update_writes_answers_and_lock_and_doctor_drifts_only_on_kept_files(updated, source):
    result = _result(updated)
    project = updated.project
    answers = support.read_yaml(project / support.ANSWERS_REL)
    assert answers.get("_commit") == support.TAG_B, f"{support.ANSWERS_REL} does not name {support.TAG_B}: {answers!r}"
    release = support.lock_release(project) or {}
    assert release.get("version") == support.B and release.get("manifest_sha256") == source.manifest_b_sha256, (
        f"{support.LOCK_REL} does not name release {support.B} with its manifest sha256 "
        f"{source.manifest_b_sha256}: version {release.get('version')!r}, sha256 {release.get('manifest_sha256')!r}")
    doctor = support.pinned(project, updated.sandbox, "doctor", "--json")
    envelope = doctor.envelope()
    report = envelope.get("result") or (envelope.get("error") or {}).get("details") or {}
    section = report.get("framework_lock")
    assert isinstance(section, dict), f"the pinned gov's doctor has no framework_lock part\n{doctor.describe()}"
    assert section.get("match") in ("MATCH", "DRIFT") and not section.get("reason"), (
        f"the pinned gov's doctor does not compare the lock with the files (or the lock and the answers differ): "
        f"{section!r}")
    lists = support.outcome_lists(result.get("files"))
    allowed = lists["kept"] | lists["merged"] | lists["conflicts"]
    drifted = sorted(set(section.get("drifted_files") or ()) - allowed)
    assert not drifted, (
        f"the pinned gov's doctor reports drifted files the update did not report kept, merged or conflict: "
        f"{drifted} (section {section!r})")


def test_update_installs_the_pinned_gov_of_release_b(updated, source):
    _result(updated)
    version = support.pinned(updated.project, updated.sandbox, "--version")
    cli = source.manifest_b.get("cli_version")
    assert version.returncode == 0 and cli == support.B and cli in version.stdout and support.A not in version.stdout, (
        f"<common>/gov/bin/gov --version does not print release B's CLI version {cli}\n{version.describe()}")


def test_update_regenerates_the_skill_release_b_changed(updated):
    _result(updated)
    generated = updated.project / support.SKILL_GENERATED
    assert generated.is_file() and support.SKILL_MARKER in generated.read_text(encoding="utf-8"), (
        f"{support.SKILL_GENERATED} does not hold release B's change to {support.SKILL}: the adapters were not "
        f"regenerated")


def test_update_refreshes_the_memory_store_at_the_update_commit(updated):
    result = _result(updated)
    assert result.get("store") == "refreshed", (
        f"the update does not say the memory store was refreshed: {result.get('store')!r}\n{updated.run.describe()}")
    retrieved = support.pinned(updated.project, updated.sandbox, "retrieve", "--json", "audit skill")
    store = retrieved.result().get("store") or {}
    assert store.get("commit") == support.head(updated.project), (
        f"the memory store was not rebuilt at the update commit {support.head(updated.project)}: {store!r}")


def test_update_is_one_commit_holding_its_record(updated, source):
    result = _result(updated)
    project = updated.project
    before = updated.before["head"]
    new = support.git(project, "rev-list", f"{before}..HEAD").split()
    assert len(new) == 1 and support.git(project, "rev-parse", "HEAD^").strip() == before, (
        f"the update is not one new commit on top of {before}: {new}")
    assert result.get("commit") == new[0], f"the report's commit {result.get('commit')!r} is not HEAD {new[0]}"
    assert result.get("record") == support.RECORD_REL, f"the report's record is not {support.RECORD_REL}"
    shown = subprocess.run(["git", "-C", str(project), "show", f"HEAD:{support.RECORD_REL}"], capture_output=True)
    assert shown.returncode == 0, f"the update commit does not hold {support.RECORD_REL}"
    record = json.loads(shown.stdout)
    assert (record.get("from"), record.get("to")) == (support.A, support.B), f"the record does not name A and B: {record}"
    assert record.get("manifest_sha256") == source.manifest_b_sha256, (
        f"the record does not name B's manifest sha256 {source.manifest_b_sha256}: {record.get('manifest_sha256')!r}")
    support.assert_outcomes(record.get("files"), f"the record {support.RECORD_REL}")
    assert support.porcelain_paths(project) == [], (
        f"`git status --porcelain` is not empty after the update: {support.porcelain_paths(project)}")

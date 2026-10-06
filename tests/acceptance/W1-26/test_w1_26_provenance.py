"""KPI S5 (CAP-39.d): provenance recording.

Each check result records its provenance: the commit (HEAD), the check version,
and the inputs hash. Two runs on the same commit with the same inputs give the
same provenance.
"""

from __future__ import annotations

import w1_26_support as support


PROVENANCE_KEYS = ("commit", "check_version", "inputs_hash")


# --------------------------------------------------------------------------
# Each result records provenance
# --------------------------------------------------------------------------

def test_each_check_result_has_provenance(project, sandbox, interface):
    """Every check result in the output carries commit, check_version, inputs_hash."""
    project.add_core_declarations()
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    entries = support.checks_of(result)
    assert entries, f"no check results in the output\n{run.describe()}"
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        prov = support.provenance_of(entry)
        for key in PROVENANCE_KEYS:
            assert key in prov, \
                f"check result {entry.get('id', '?')} has no provenance key {key!r}: {prov}"
            assert isinstance(prov[key], str) and prov[key].strip(), \
                f"provenance key {key!r} is empty in {entry.get('id', '?')}: {prov}"


def test_provenance_commit_is_head(project, sandbox, interface):
    """The provenance commit matches the HEAD of the project at check time."""
    project.add_core_declarations()
    head = project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    for entry in support.checks_of(result):
        if not isinstance(entry, dict):
            continue
        prov = support.provenance_of(entry)
        if "commit" in prov:
            assert prov["commit"] == head, \
                f"provenance commit {prov['commit']!r} != HEAD {head!r} for {entry.get('id', '?')}"


# --------------------------------------------------------------------------
# Determinism: same commit + same inputs -> same provenance
# --------------------------------------------------------------------------

def test_two_runs_same_commit_same_provenance(project, sandbox, interface):
    """Two runs on the same commit with the same inputs give identical provenance."""
    project.add_core_declarations()
    project.commit()

    run1 = support.run_check(project, sandbox)
    envelope1 = support.envelope_of(run1, interface)
    result1 = envelope1.get("result") or envelope1.get("error", {}).get("details", {})

    run2 = support.run_check(project, sandbox)
    envelope2 = support.envelope_of(run2, interface)
    result2 = envelope2.get("result") or envelope2.get("error", {}).get("details", {})

    entries1 = {e.get("id"): support.provenance_of(e) for e in support.checks_of(result1)
                if isinstance(e, dict) and e.get("id")}
    entries2 = {e.get("id"): support.provenance_of(e) for e in support.checks_of(result2)
                if isinstance(e, dict) and e.get("id")}
    for check_id in entries1:
        if check_id in entries2:
            assert entries1[check_id] == entries2[check_id], \
                f"provenance differs for {check_id}: {entries1[check_id]} vs {entries2[check_id]}"


def test_provenance_changes_with_a_new_commit(project, sandbox, interface):
    """A new commit changes at least the provenance commit."""
    project.add_core_declarations()
    head1 = project.commit()
    run1 = support.run_check(project, sandbox)
    envelope1 = support.envelope_of(run1, interface)
    result1 = envelope1.get("result") or envelope1.get("error", {}).get("details", {})

    project.write("new-file.txt", "changed\n")
    head2 = project.commit("second commit")
    assert head1 != head2
    run2 = support.run_check(project, sandbox)
    envelope2 = support.envelope_of(run2, interface)
    result2 = envelope2.get("result") or envelope2.get("error", {}).get("details", {})

    entries1 = {e.get("id"): support.provenance_of(e) for e in support.checks_of(result1)
                if isinstance(e, dict) and e.get("id")}
    entries2 = {e.get("id"): support.provenance_of(e) for e in support.checks_of(result2)
                if isinstance(e, dict) and e.get("id")}
    changed = any(entries1.get(cid, {}).get("commit") != entries2.get(cid, {}).get("commit")
                  for cid in entries1 if cid in entries2)
    assert changed, "a new commit did not change any provenance commit field"

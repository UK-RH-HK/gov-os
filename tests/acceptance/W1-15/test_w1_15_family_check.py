"""KPI success 4 and failure 1: the secrets-indexing family check [CAP-38.b].

The ticket registers the check as a declaration under
``template/governance/kernel/checks/`` (DEC-186), so ``gov check --list --json``
lists it. Running checks through ``gov check`` is W1-26; until then the tests
run the declared ``command`` themselves, in the root of a project, and read its
exit code: 0 when no derived store holds a secret, another code when one does.
The derived stores are everything under ``.gov-runtime/`` (CAP-03 acceptance).
"""

from __future__ import annotations

import pytest

import w1_15_support as support

# Where derived state could stand. The folder names are the tests' own: the check looks at all of ``.gov-runtime/``.
TEXT_STORES = {
    "packet": ".gov-runtime/packets/DAEO-0000/packet.md",
    "bundle": ".gov-runtime/bundles/evidence-0001.json",
    "code-index": ".gov-runtime/codebase-memory/index/symbols.txt",
}
DATABASE = ".gov-runtime/index/lexical.sqlite"
PLANTED = {**support.FORMS,"private-key": support.PRIVATE_KEY}


def test_the_check_is_registered_in_the_kernel_template(family_check):
    """One listed check of the family, with the five fields of a declaration and a command to run."""
    for field in support.CHECK_FIELDS:
        assert isinstance(family_check.get(field), str) and family_check[field].strip(), \
            f"the listed secrets-indexing check has no {field}: {family_check!r}"
    assert family_check["severity"] in ("hard-block", "warning"), family_check


def test_the_check_passes_when_there_is_no_derived_store(family_check, store_project, sandbox):
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode == 0, f"the check fails on a project with no .gov-runtime/\n{run.describe()}"


def test_the_check_passes_on_stores_without_a_secret(family_check, store_project, sandbox):
    for rel in TEXT_STORES.values():
        store_project.write(rel, support.CLEAN_PROSE)
    store_project.store_database(DATABASE, "Ordinary text about tokens and canaries.")
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode == 0, f"the check fails on stores that hold no secret\n{run.describe()}"


@pytest.mark.parametrize("place", list(TEXT_STORES))
def test_the_check_fails_on_a_canary_in_a_store_packet_or_bundle(family_check, store_project, sandbox, place):
    store_project.write(TEXT_STORES[place], support.in_prose(support.TIER_FORM))
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode != 0, f"a canary in {TEXT_STORES[place]} and the check passes\n{run.describe()}"


@pytest.mark.parametrize("kind", list(PLANTED))
def test_the_check_fails_on_a_planted_secret_in_a_database_store(family_check, store_project, sandbox, kind):
    """The Wave 1 stores are SQLite files: the secret is a row of a table, not a line of a text file."""
    store_project.store_database(DATABASE, support.in_prose(PLANTED[kind]))
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode != 0, f"a planted {kind} in {DATABASE} and the check passes\n{run.describe()}"


def test_one_bad_store_among_clean_ones_fails_the_check(family_check, store_project, sandbox):
    for rel in TEXT_STORES.values():
        store_project.write(rel, support.CLEAN_PROSE)
    store_project.write(".gov-runtime/packets/DAEO-0001/packet.md", support.in_prose(support.KPI_FORM))
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode != 0, run.describe()


def test_a_failing_check_names_the_store_and_does_not_repeat_the_secret(family_check, store_project, sandbox):
    """The output of a check is kept as evidence: it says where, and it must not carry the secret further."""
    rel = store_project.write(TEXT_STORES["packet"], support.in_prose(support.TIER_FORM))
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode != 0, run.describe()
    assert "packet.md" in run.output, f"the check does not say which file holds the secret ({rel})\n{run.describe()}"
    assert support.TIER_FORM not in run.output, "the check printed the secret it found"
    left = support.files_holding(store_project.root, [support.TIER_FORM])
    assert sorted(left) == [rel], f"the check left a copy of the secret in the project: {sorted(left)}"
    for place in (sandbox.home, sandbox.tmpdir):
        assert not support.files_holding(place, [support.TIER_FORM]), f"the check left the secret in {place}"


def test_a_secret_in_a_source_file_is_not_a_store_finding(family_check, store_project, sandbox):
    """The check's subject is derived state. A source file with a secret is the filter's work, not a red check."""
    store_project.write("notes/planted.md", support.in_prose(support.TIER_FORM))
    store_project.write(TEXT_STORES["packet"], support.CLEAN_PROSE)
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode == 0, \
        f"the stores are clean and the check fails on a source file\n{run.describe()}"

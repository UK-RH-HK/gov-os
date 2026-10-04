"""Second test design batch: behaviours a review after green described (DEC-136) [CAP-03.a, CAP-03.b, CAP-38.b].

B1  a link is judged by what it points to, for its namespace too (KPI success 3)
B2  a scanner configuration without rules is "cannot decide", not "no secret" (DEC-285)
B3  the check is not green on a store it cannot read (KPI success 4)
B4  the check follows a linked store folder (KPI success 4)
B5  a secret in UTF-16 text is found (KPI failure 1)
B6  the check sees the whole content of a SQLite store, not only table rows (DEC-290)

The interfaces are the two of the first batch: ``gov.secrets.indexable(root, paths)`` and the check's declared
``command``, run by ``sh -c`` in the project root.
"""

from __future__ import annotations

import os
import sqlite3

import pytest

import w1_15_support as support

CLEAN = "notes/clean.md"
PRODUCT_FILE = "tenant-exports/2026/customers.csv"
ROWS = "id,name,city\n1,Ada,Leeds\n2,Grace,York\n"
PACKET = ".gov-runtime/packets/DAEO-0000/packet.md"
DATABASE = ".gov-runtime/index/lexical.sqlite"
ENCODINGS = {"with-bom": True, "without-bom": False}


# --------------------------------------------------------------------------
# B1: a link is judged by what it points to, for its namespace too
# --------------------------------------------------------------------------

@pytest.mark.parametrize("target", ["relative", "absolute"])
def test_a_governance_link_to_a_product_file_is_not_indexable(project, sandbox, target):
    """The file holds no secret: only the namespace of what the link points to can keep it out."""
    project.write(CLEAN, support.CLEAN_PROSE)
    project.write(PRODUCT_FILE, ROWS)
    points_to = "../" + PRODUCT_FILE if target == "relative" else project.root / PRODUCT_FILE
    linked = project.link("notes/customers.csv", points_to)
    run = support.allowed(project.root, [linked, CLEAN], sandbox)
    assert linked not in run.allowed, \
        f"a link in notes/ to a product-data file is let through: the indexer reads product data\n{run.describe()}"
    assert CLEAN in run.allowed, f"the clean neighbour was dropped too\n{run.describe()}"


def test_a_file_reached_through_a_governance_link_to_the_product_folder_is_not_indexable(project, sandbox):
    project.write(CLEAN, support.CLEAN_PROSE)
    project.write(PRODUCT_FILE, ROWS)
    project.link("notes/exports", "../tenant-exports")
    through = "notes/exports/2026/customers.csv"
    run = support.allowed(project.root, [through, CLEAN], sandbox)
    assert through not in run.allowed, \
        f"notes/exports is a link to the product folder, and a file through it is let through\n{run.describe()}"
    assert CLEAN in run.allowed, f"the clean neighbour was dropped too\n{run.describe()}"


def test_a_governance_link_to_a_file_outside_the_project_is_not_indexable(project, sandbox, tmp_path):
    """What stands outside the root has no namespace in the project's path map: default deny (CAP-03.a)."""
    outside = tmp_path / "outside" / "plain.md"
    outside.parent.mkdir()
    outside.write_text(support.CLEAN_PROSE, encoding="utf-8")
    project.write(CLEAN, support.CLEAN_PROSE)
    linked = project.link("notes/outside.md", outside)
    run = support.allowed(project.root, [linked, CLEAN], sandbox)
    assert linked not in run.allowed, \
        f"a link to a file outside the project root is let through\n{run.describe()}"
    assert CLEAN in run.allowed, f"the clean neighbour was dropped too\n{run.describe()}"


@pytest.mark.parametrize("kind", ["file-link", "folder-link"])
def test_a_governance_link_to_clean_governance_content_is_indexable(project, sandbox, kind):
    """Keep true: a link is not refused for being a link."""
    project.write(CLEAN, support.CLEAN_PROSE)
    project.write("app/docs/guide.md", support.CLEAN_PROSE)
    if kind == "file-link":
        asked = project.link("notes/alias.md", "clean.md")
    else:
        project.link("notes/shelf", "../app/docs")
        asked = "notes/shelf/guide.md"
    run = support.allowed(project.root, [asked, CLEAN], sandbox)
    assert list(run.allowed) == [asked, CLEAN], \
        f"a link to a clean file of a governance namespace is dropped\n{run.describe()}"


# --------------------------------------------------------------------------
# B2: a scanner configuration without rules is "cannot decide"
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ruleless", list(support.RULELESS_CONFIGS))
def test_the_filter_lets_no_canary_through_when_the_configuration_has_no_rules(project, sandbox, ruleless):
    """With no rule the scanner finds nothing in anything: that is no verdict. The call may fail instead."""
    project.write(support.ROOT_CONFIG_REL, support.RULELESS_CONFIGS[ruleless])
    project.write(CLEAN, support.CLEAN_PROSE)
    planted = project.write("notes/planted.md", support.in_prose(support.TIER_FORM))
    run = support.run_filter(project.root, [CLEAN, planted], sandbox)
    if run.allowed is None:
        return  # the call refused to decide: nothing was let through
    assert planted not in run.allowed, \
        f"the project's .gitleaks.toml holds no rules ({ruleless}) and the canary is let through\n{run.describe()}"


@pytest.mark.parametrize("ruleless", list(support.RULELESS_CONFIGS))
def test_the_check_is_not_green_when_the_configuration_has_no_rules(family_check, store_project, sandbox, ruleless):
    store_project.write(support.ROOT_CONFIG_REL, support.RULELESS_CONFIGS[ruleless])
    store_project.write(PACKET, support.in_prose(support.TIER_FORM))
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode != 0, \
        f"the project's .gitleaks.toml holds no rules ({ruleless}), a store holds the canary, and the check is " \
        f"green\n{run.describe()}"


# --------------------------------------------------------------------------
# B3: the check is not green on a store it cannot read
# --------------------------------------------------------------------------

@pytest.fixture()
def closed():
    """Take every permission from a folder for the length of a test, and give it back so pytest can remove it."""
    if os.geteuid() == 0:
        pytest.skip("root enters every folder: the premise cannot hold")
    taken = []

    def close(path):
        taken.append((path, path.stat().st_mode))
        path.chmod(0)
        try:
            os.listdir(path)
        except PermissionError:
            return path
        pytest.skip(f"this file system lets the folder be read with mode 0: {path}")

    yield close
    for path, mode in reversed(taken):
        path.chmod(mode)


@pytest.mark.parametrize("folder", [".gov-runtime/packets", ".gov-runtime"], ids=["a-store-folder", "the-runtime-folder"])
def test_the_check_is_not_green_on_a_store_it_cannot_enter(family_check, store_project, sandbox, closed, folder):
    """A store the check could not look into is not a store without a secret.

    Keep true, in the first batch: ``test_the_check_passes_when_there_is_no_derived_store``.
    """
    store_project.write(PACKET, support.in_prose(support.TIER_FORM))
    store_project.write(".gov-runtime/bundles/evidence-0001.json", support.CLEAN_PROSE)
    closed(store_project.root / folder)
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode != 0, \
        f"{folder}/ cannot be entered, the canary stands inside it, and the check is green\n{run.describe()}"


# --------------------------------------------------------------------------
# B4: the check follows a linked store folder
# --------------------------------------------------------------------------

def test_the_check_fails_on_a_canary_in_a_linked_store_folder(family_check, store_project, sandbox, tmp_path):
    shared = tmp_path / "shared-store"
    (shared / "DAEO-0000").mkdir(parents=True)
    (shared / "DAEO-0000" / "packet.md").write_text(support.in_prose(support.TIER_FORM), encoding="utf-8")
    store_project.write(".gov-runtime/bundles/evidence-0001.json", support.CLEAN_PROSE)
    store_project.link(".gov-runtime/packets", shared)
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode != 0, \
        f".gov-runtime/packets is a link to a folder that holds the canary, and the check is green\n{run.describe()}"


# --------------------------------------------------------------------------
# B5: a secret in UTF-16 text is found
# --------------------------------------------------------------------------

@pytest.mark.parametrize("encoding", list(ENCODINGS))
def test_a_utf16_file_with_the_canary_is_not_indexable(project, sandbox, encoding):
    bom = ENCODINGS[encoding]
    neighbour = project.write_bytes("notes/clean-utf16.md", support.utf16(support.CLEAN_PROSE, bom))
    planted = project.write_bytes("notes/planted-utf16.md", support.utf16(support.in_prose(support.TIER_FORM), bom))
    assert not support.files_holding(project.root, [support.TIER_FORM]), "premise: the canary is not there as UTF-8"
    run = support.allowed(project.root, [neighbour, planted], sandbox)
    assert planted not in run.allowed, \
        f"a UTF-16 file ({encoding}) with the canary is let through to the indexer\n{run.describe()}"
    assert neighbour in run.allowed, f"the UTF-16 neighbour without a secret was dropped too\n{run.describe()}"


@pytest.mark.parametrize("encoding", list(ENCODINGS))
def test_the_check_fails_on_a_canary_in_a_utf16_store(family_check, store_project, sandbox, encoding):
    bom = ENCODINGS[encoding]
    store_project.write_bytes(PACKET, support.utf16(support.in_prose(support.TIER_FORM), bom))
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode != 0, \
        f"a UTF-16 text store ({encoding}) holds the canary and the check is green\n{run.describe()}"


def test_the_check_passes_on_a_utf16_store_without_a_secret(family_check, store_project, sandbox):
    """Keep true: UTF-16 text is not a finding by itself."""
    for name, bom in ENCODINGS.items():
        store_project.write_bytes(f".gov-runtime/packets/{name}/packet.md", support.utf16(support.CLEAN_PROSE, bom))
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode == 0, f"the check fails on UTF-16 stores that hold no secret\n{run.describe()}"


# --------------------------------------------------------------------------
# B6: the check sees the whole content of a SQLite store
# --------------------------------------------------------------------------

def _database(project, rel, removed, view_text):
    """A SQLite store with one row kept, one row holding ``removed`` deleted without vacuum, and one view."""
    path = project.root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute("PRAGMA secure_delete = OFF")
        connection.execute("CREATE TABLE chunks (id INTEGER PRIMARY KEY, path TEXT, body TEXT)")
        connection.execute("INSERT INTO chunks (path, body) VALUES (?, ?)", ("notes/clean.md", support.CLEAN_PROSE))
        connection.execute("INSERT INTO chunks (path, body) VALUES (?, ?)", ("notes/other.md", removed))
        connection.commit()
        connection.execute("DELETE FROM chunks WHERE path = ?", ("notes/other.md",))
        connection.execute("CREATE VIEW labels AS SELECT id, '" + view_text + "' AS label FROM chunks")
        connection.commit()
        rows = connection.execute("SELECT path, body FROM chunks").fetchall()
    finally:
        connection.close()
    return rows


def test_the_check_fails_on_a_canary_left_in_the_bytes_of_a_deleted_row(family_check, store_project, sandbox):
    rows = _database(store_project, DATABASE, support.in_prose(support.TIER_FORM), "ordinary label")
    assert not any(support.TIER_FORM in str(value) for row in rows for value in row), "premise: no row holds it"
    assert sorted(support.files_holding(store_project.root, [support.TIER_FORM])) == [DATABASE], \
        "premise: the deleted row's bytes are still in the SQLite file (secure_delete off, no vacuum)"
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode != 0, \
        f"the canary is in the bytes of {DATABASE} (a deleted row) and the check is green\n{run.describe()}"


def test_the_check_fails_on_a_canary_in_the_text_of_a_view(family_check, store_project, sandbox):
    rows = _database(store_project, DATABASE, "Ordinary text, later removed.", support.TIER_FORM)
    assert not any(support.TIER_FORM in str(value) for row in rows for value in row), "premise: no row holds it"
    assert sorted(support.files_holding(store_project.root, [support.TIER_FORM])) == [DATABASE], \
        "premise: the view's definition is in the SQLite file"
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode != 0, \
        f"the canary is in the definition of a view of {DATABASE} and the check is green\n{run.describe()}"


def test_the_check_passes_on_a_database_with_a_deleted_row_and_a_view_and_no_secret(family_check, store_project,
                                                                                   sandbox):
    """Keep true: a deleted row and a view are not findings by themselves."""
    _database(store_project, DATABASE, "Ordinary text about tokens and canaries, later removed.", "ordinary label")
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode == 0, f"the check fails on a SQLite store that holds no secret\n{run.describe()}"

"""KPI success 3 and failure 2: indexers skip every namespace the path map classes as product data [CAP-03.b].

The rule comes from ``governance/project/path-map.yaml`` of the project
(``memory_class``, DEC-225), never from paths written into the code: each test
changes the map and sees the filter follow. The files hold no secret, so only
the path map can keep them out.
"""

from __future__ import annotations

import pytest

import w1_15_support as support

GOVERNANCE_FILE = "notes/decision.md"
PRODUCT_FILE = "tenant-exports/2026/customers.csv"
ROWS = "id,name,city\n1,Ada,Leeds\n2,Grace,York\n"


def _namespaces(**changes):
    namespaces = dict(support.NAMESPACES)
    namespaces.update(changes)
    return namespaces


def _files(project):
    project.write(GOVERNANCE_FILE, support.CLEAN_PROSE)
    project.write(PRODUCT_FILE, ROWS)
    return [GOVERNANCE_FILE, PRODUCT_FILE]


def test_a_file_in_a_product_namespace_is_not_indexable(project, sandbox):
    run = support.allowed(project.root, _files(project), sandbox)
    assert PRODUCT_FILE not in run.allowed, f"a planted product-data file is let through\n{run.describe()}"
    assert GOVERNANCE_FILE in run.allowed, f"the governance file was dropped too\n{run.describe()}"


def test_the_same_file_is_indexable_once_the_map_classes_its_namespace_as_governance(project, sandbox):
    """The folder and the file are unchanged; only ``memory_class`` in the map changes."""
    asked = _files(project)
    before = support.allowed(project.root, asked, sandbox)
    assert PRODUCT_FILE not in before.allowed, before.describe()
    project.set_namespaces(_namespaces(**{"tenant-exports": (["tenant-exports/**"], "governance")}))
    after = support.allowed(project.root, asked, sandbox)
    assert list(after.allowed) == asked, \
        f"the map now classes tenant-exports/** as governance, and the file is still dropped\n{after.describe()}"


def test_a_namespace_the_map_turns_into_product_data_is_skipped(project, sandbox):
    asked = _files(project)
    before = support.allowed(project.root, asked, sandbox)
    assert GOVERNANCE_FILE in before.allowed, before.describe()
    project.set_namespaces(_namespaces(notes=(["notes/**"], "product")))
    after = support.allowed(project.root, asked, sandbox)
    assert list(after.allowed) == [], \
        f"the map now classes notes/** as product data, and its file is still let through\n{after.describe()}"


def test_the_product_folder_of_this_repository_has_no_special_place(project, sandbox):
    """This repository's own map classes ``fixtures/**`` as product data. Another project's map decides for itself."""
    project.set_namespaces(_namespaces(fixtures=(["fixtures/**"], "governance")))
    inside = project.write("fixtures/sample/readme.md", support.CLEAN_PROSE)
    run = support.allowed(project.root, [inside, *_files(project)], sandbox)
    assert inside in run.allowed, \
        f"fixtures/** is governance memory in this project's map, and its file is dropped\n{run.describe()}"
    assert PRODUCT_FILE not in run.allowed, run.describe()


def test_every_product_namespace_and_every_pattern_of_it_is_skipped(project, sandbox):
    project.set_namespaces(_namespaces(
        runtime=(["runtime-logs/**", "var/customer/**"], "product"),
    ))
    product = [project.write("runtime-logs/app.log", "started\nstopped\n"),
               project.write("var/customer/a/b/record.json", '{"name": "Ada"}\n'),
               project.write(PRODUCT_FILE, ROWS)]
    governance = project.write(GOVERNANCE_FILE, support.CLEAN_PROSE)
    run = support.allowed(project.root, [*product, governance], sandbox)
    assert list(run.allowed) == [governance], \
        f"expected only the governance file to be let through\n{run.describe()}"


def test_the_patterns_are_read_as_the_path_map_writes_them(project, sandbox):
    """``*`` stays inside one folder and ``**`` crosses folders (the language of ticket ``allowed_paths``)."""
    project.set_namespaces(_namespaces(
        exports=(["exports/*"], "product"),
        archive=(["exports/archive/**"], "governance"),
    ))
    product = project.write("exports/customers.csv", ROWS)
    governance = [project.write("exports/archive/2025/index.md", support.CLEAN_PROSE),
                  project.write("exports-notes.md", support.CLEAN_PROSE)]
    run = support.allowed(project.root, [product, *governance], sandbox)
    assert list(run.allowed) == governance, \
        f"exports/* is product data; exports/archive/** and the root file are governance\n{run.describe()}"


@pytest.mark.parametrize("memory_class", [None, "customer"], ids=["no-memory-class", "unknown-memory-class"])
def test_a_namespace_the_map_does_not_class_as_governance_is_not_let_through(project, sandbox, memory_class):
    """Default deny (CAP-03.a): a namespace whose class cannot be read is not indexed; the call may fail instead."""
    asked = _files(project)
    project.set_namespaces(_namespaces(**{"tenant-exports": (["tenant-exports/**"], memory_class)}))
    run = support.run_filter(project.root, asked, sandbox)
    if run.allowed is None:
        return  # the call refused the map: nothing was let through
    assert PRODUCT_FILE not in run.allowed, \
        f"a file of a namespace with memory_class {memory_class!r} is let through\n{run.describe()}"


def test_a_secret_in_a_governance_file_is_dropped_whatever_the_map_says(project, sandbox):
    """The two rules are independent: governance memory is still filtered by content."""
    project.set_namespaces(_namespaces(**{"tenant-exports": (["tenant-exports/**"], "governance")}))
    planted = project.write("tenant-exports/2026/keys.txt", support.in_prose(support.TIER_FORM))
    asked = [planted, *_files(project)]
    run = support.allowed(project.root, asked, sandbox)
    assert list(run.allowed) == asked[1:], run.describe()

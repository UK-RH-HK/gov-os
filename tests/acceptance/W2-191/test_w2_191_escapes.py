"""F1: a target that escapes the project (absolute, ``..``, a symlink out) or names no existing folder or file is not
accepted (DEC-1199 (2)); S1's refusals (an absolute path, a path with ``..``, a path outside the project).

An escape is refused by the schema or the loader: asserted through ``gov.close.select.load_map`` (``(None, reason)``,
a non-empty reason; no reason name is pinned), which judges by both. A target that names nothing is never selected
as resolved: refused by the loader or by the selection, either (``select.scoped`` raises ``SelectionRefused``;
``select.plan`` goes to the full run), as the tree's existing cases pin for ``tests/`` targets.

Every refusal is tried in each place a target may stand (record_reading, every_close, a coupling's suites).
"""
import yaml

from gov.close import select

import w2_191_support as support


def _refused_in_every_place(tmp_path, target_of, extra=None, links=None):
    """The places in which the loader does not refuse the map holding ``target_of(project)``: empty when it does
    everywhere."""
    taken = []
    for position in support.POSITIONS:
        project = support.plant(tmp_path / position, support.map_data(), extra=extra)
        for rel, target in (links or {}).items():
            project.link(rel, target(project))
        project.commit("links", files={})
        project.write({"governance/project/test-map.yaml": yaml.safe_dump(
            support.with_target(position, target_of(project)), sort_keys=False)})
        project.commit("the map", files={})
        given, why = select.load_map(project.root)
        if given is not None:
            taken.append(position)
        else:
            assert isinstance(why, str) and why, f"{position}: refused with no reason: {why!r}"
    return taken


# --- the escapes a tests/ beginning lets through the schema's pattern today (red on the base) -------------------

def test_f1_a_target_beginning_tests_that_climbs_out_of_the_project_is_refused(tmp_path):
    """``tests/../..`` is the folder holding the project (it exists, and is outside), ``tests/../../outside/suite``
    a real suite outside: both begin with ``tests/``, so the beginning decides nothing."""
    forms = {"the folder above": lambda p: "tests/../..",
             "a suite beside the project": lambda p: "tests/../../outside/suite",
             "a file beside the project": lambda p: "tests/../../outside/suite/test_o.py::test_ok"}
    taken = {name: _refused_in_every_place(tmp_path / str(i), form) for i, (name, form) in enumerate(forms.items())}
    assert not any(taken.values()), f"the loader takes an escaping target in: {taken}"


def test_f1_a_target_with_a_dot_dot_segment_is_refused_even_where_it_stays_inside(tmp_path):
    """S1: 'a path with ..' is refused; ``tests/../product/tests`` is a folder of the project, spelled with ``..``."""
    taken = _refused_in_every_place(tmp_path, lambda p: "tests/../product/tests",
                                    extra={"product/tests/test_in.py": support.PASS})
    assert not taken, f"the loader takes a target with a .. segment in: {taken}"


def test_f1_a_symlink_under_tests_that_points_out_of_the_project_is_refused(tmp_path):
    """``tests/linked`` is a symlink to a real suite outside the project: the name begins ``tests/``, the folder it
    names is not the project's."""
    taken = {}
    for form in ("tests/linked", "tests/linked/test_o.py", "tests/linked/test_o.py::test_ok"):
        taken[form] = _refused_in_every_place(
            tmp_path / str(len(taken)), lambda p, form=form: form,
            links={"tests/linked": lambda p: p.outside / "suite"})
    assert not any(taken.values()), f"the loader takes a symlink out of the project in: {taken}"


# --- guard cases: the pattern refuses these today, and they must stay refused (green by design) --------------------

def test_f1_an_absolute_path_is_refused_guard(tmp_path):
    """Guard case: an absolute path is refused, inside the project (it exists there) as outside it."""
    forms = {"inside, a real folder": lambda p: str(p.root / support.SCRIPTS_SUITE),
             "inside, a real file": lambda p: str(p.root / support.PRODUCT_FILE),
             "outside, a real suite": lambda p: str(p.outside / "suite"),
             "the root": lambda p: "/"}
    taken = {name: _refused_in_every_place(tmp_path / str(i), form) for i, (name, form) in enumerate(forms.items())}
    assert not any(taken.values()), f"the loader takes an absolute target in: {taken}"


def test_f1_a_path_climbing_out_without_a_tests_beginning_is_refused_guard(tmp_path):
    """Guard case: ``..`` first, or after a folder of the project, to a real suite outside the project."""
    forms = {"first": lambda p: "../outside/suite", "after a folder": lambda p: "governance/../../outside/suite",
             "at the end of a suite": lambda p: f"{support.SCRIPTS_SUITE}/.."}
    taken = {name: _refused_in_every_place(tmp_path / str(i), form) for i, (name, form) in enumerate(forms.items())}
    assert not any(taken.values()), f"the loader takes a .. target in: {taken}"


def test_f1_a_symlink_out_of_the_project_is_refused_where_the_name_is_not_under_tests_guard(tmp_path):
    """Guard case: a symlinked folder, and a symlinked folder above the suite, both to a real suite outside."""
    taken = {}
    for name, form, links in (
            ("the folder", "governance/scripts/linked", {"governance/scripts/linked": lambda p: p.outside / "suite"}),
            ("the folder above", "linkedproduct/tests", {"linkedproduct": lambda p: p.outside})):
        taken[name] = _refused_in_every_place(tmp_path / str(len(taken)), lambda p, form=form: form, links=links)
    assert not any(taken.values()), f"the loader takes a symlink out of the project in: {taken}"


# --- a target that names nothing is never selected as resolved (guard cases: the pattern refuses them today) -------

def _project_with_a_missing_target(tmp_path, position, target):
    """The planted project, at a green base, with the map naming ``target`` in ``position`` and a change that
    selects every place: a record (record_reading, every_close) and the coupled input (the coupling)."""
    if position == "couplings":
        test_map = support.map_data(couplings=[support.coupling([target])])
    else:
        test_map = support.map_data(**{position: [target]})
    project = support.plant(tmp_path, test_map)
    project.green_night()
    project.work({"docs/notes.md": "# notes, changed\n", support.COUPLED_INPUT: "a rule, changed\n"})
    return project


MISSING = ["governance/scripts/missing_suite", "governance/scripts/tests/test_absent.py",
           "governance/scripts/tests/test_records.py::test_gone"]


def test_f1_a_target_naming_nothing_is_not_selected_as_resolved_guard(tmp_path):
    """Guard case: the selection of a project whose map names a folder, a file or a case that is not there is
    refused (by the loader or by the selection), in every place."""
    taken = []
    for position in support.POSITIONS:
        for i, target in enumerate(MISSING):
            project = _project_with_a_missing_target(tmp_path / f"{position}{i}", position, target)
            refused, how = support.never_resolved(project)
            if not refused:
                taken.append(f"{position}: {target} -> {how}")
    assert not taken, "a target that names nothing was taken:\n" + "\n".join(taken)


def test_f1_the_strict_close_does_not_scope_on_a_target_naming_nothing_guard(tmp_path):
    """Guard case: ``plan`` widens to the full run where a selected target names nothing (as for ``tests/`` targets)."""
    scoped = []
    for position in support.POSITIONS:
        for i, target in enumerate(MISSING):
            project = _project_with_a_missing_target(tmp_path / f"{position}{i}", position, target)
            plan = select.plan(project.root, support.WBS, ticket=support.TICKET)
            if plan["scope"] != "full" or not plan["why_full"]:
                scoped.append(f"{position}: {target} -> scope {plan['scope']}")
    assert not scoped, "the plan scoped on a target that names nothing:\n" + "\n".join(scoped)

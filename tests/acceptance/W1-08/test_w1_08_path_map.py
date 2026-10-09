"""The path-map schema and this repository's path map: the namespaces.

Success 2, second half: this repository's path map classifies every tracked path [CAP-06.a].
Success 3, first part: each namespace has a sensitivity class, permitted roles, retention, export policy, embedding
policy, provenance and deletion/rebuild behaviour [CAP-03.a, CAP-03.c].
Success 4: every namespace is governance/development memory or customer/runtime product data, never both [CAP-03.b].

The good document is the committed `governance/project/path-map.yaml`; each bad one is that document with one
change. `namespaces` maps a name to a map (DEC-189). A namespace lists its paths under `paths`, in the pattern
language of ticket `allowed_paths`, and every tracked path matches exactly one namespace; `memory_class` is
`governance` or `product` (DEC-225). No source names the seven fields of Framework §16, so each is found by the
KPI's own word in the key name, at any depth inside the namespace.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib

import pytest

import w1_08_support as support

# KPI wording -> words of which one must be in the key name
NAMESPACE_FIELDS = {
    "sensitivity class": ("sensitiv",),
    "permitted roles": ("role",),
    "retention": ("retention", "retain"),
    "export policy": ("export",),
    "embedding policy": ("embed",),
    "provenance": ("provenance",),
    "deletion/rebuild behaviour": ("delet", "rebuild"),
}
MEMORY_CLASSES = ("governance", "product")
SHOWN = 10  # names shown in a failure message


@pytest.fixture
def path_map():
    schema = support.schema_path("path-map")
    document = support.load_path_map()
    return schema, document


def _first_namespace(document):
    return sorted(support.namespaces(document))[0]


# --- the committed path map [CAP-06.a] --------------------------------------------------------------------------

def test_this_repository_has_a_committed_path_map_with_namespaces():
    support.namespaces(support.load_path_map())
    assert support.PATH_MAP_REL in support.tracked_files(), f"{support.PATH_MAP_REL} is not committed"


@pytest.mark.local_only
def test_the_path_map_validates_against_the_path_map_schema(path_map, check):
    schema, document = path_map
    check.accepts(schema, document, support.PATH_MAP_REL)


@pytest.mark.local_only
def test_the_path_map_validates_as_it_is_written(path_map, check):
    schema, _ = path_map
    text = (support.REPO_ROOT / support.PATH_MAP_REL).read_text(encoding="utf-8")
    check.accepts_file(schema, text, support.PATH_MAP_REL)


def test_every_namespace_lists_its_paths():
    spaces = support.namespaces(support.load_path_map())
    wrong = [name for name, value in spaces.items()
             if not (isinstance(value.get("paths"), list) and value["paths"]
                     and all(isinstance(pattern, str) and pattern for pattern in value["paths"]))]
    assert not wrong, f"{support.PATH_MAP_REL}: `paths` is not a non-empty list of patterns in namespace(s) {wrong}"


def test_every_tracked_path_matches_exactly_one_namespace():
    """The names come from `git ls-files`; no tracked file is opened."""
    spaces = support.namespaces(support.load_path_map())
    patterns = {name: [pattern for pattern in value.get("paths") or [] if isinstance(pattern, str)]
                for name, value in spaces.items()}
    tracked = support.tracked_files()
    nowhere, twice = [], []
    for path in tracked:
        found = [name for name, own in patterns.items() if any(support.matches(pattern, path) for pattern in own)]
        if not found:
            nowhere.append(path)
        elif len(found) > 1:
            twice.append(f"{path} -> {found}")
    assert not nowhere, (f"{len(nowhere)} of {len(tracked)} tracked paths are in no namespace of "
                         f"{support.PATH_MAP_REL}, for example {nowhere[:SHOWN]}")
    assert not twice, (f"{len(twice)} of {len(tracked)} tracked paths are in more than one namespace of "
                       f"{support.PATH_MAP_REL}, for example {twice[:SHOWN]}")


@pytest.mark.local_only
@pytest.mark.parametrize("paths", (None, 42, [42]))
def test_a_namespace_whose_paths_are_not_a_list_of_patterns_is_refused(paths, path_map, check):
    schema, document = path_map
    name = _first_namespace(document)
    check.good(schema, document, support.PATH_MAP_REL)
    if paths is None:
        bad = support.delete_at(document, ("namespaces", name, "paths"))
    else:
        bad = support.set_at(document, ("namespaces", name, "paths"), paths)
    check.refuses(schema, bad, f"a path map whose namespace {name!r} has `paths` {paths!r}")


# --- the seven fields of a namespace [CAP-03.a, CAP-03.c] -------------------------------------------------------

@pytest.mark.parametrize("field", sorted(NAMESPACE_FIELDS))
def test_every_namespace_of_the_path_map_declares_the_field(field):
    spaces = support.namespaces(support.load_path_map())
    missing = [name for name, value in spaces.items() if support.find_key(value, NAMESPACE_FIELDS[field]) is None]
    assert not missing, f"{support.PATH_MAP_REL}: no {field} in namespace(s) {missing}"


@pytest.mark.local_only
@pytest.mark.parametrize("field", sorted(NAMESPACE_FIELDS))
def test_a_namespace_without_the_field_is_refused(field, path_map, check):
    schema, document = path_map
    name = _first_namespace(document)
    trail = support.find_key(document["namespaces"][name], NAMESPACE_FIELDS[field])
    assert trail is not None, f"{support.PATH_MAP_REL}: no {field} in namespace {name!r}"
    check.good(schema, document, support.PATH_MAP_REL)
    bad = support.delete_at(document, ("namespaces", name) + trail)
    check.refuses(schema, bad, f"a path map whose namespace {name!r} has no {field} ({'.'.join(trail)})")


@pytest.mark.local_only
@pytest.mark.parametrize("value", ({}, 42))
def test_a_namespace_that_declares_nothing_is_refused(value, path_map, check):
    schema, document = path_map
    check.good(schema, document, support.PATH_MAP_REL)
    bad = support.set_at(document, ("namespaces", "w1-08-wrong"), value)
    check.refuses(schema, bad, f"a path map with a namespace that is {value!r}")


@pytest.mark.local_only
def test_a_path_map_that_is_not_a_map_is_refused(path_map, check):
    schema, good = path_map
    check.good(schema, good, support.PATH_MAP_REL)
    check.refuses(schema, ["namespaces"], "a list as a path map")
    check.refuses(schema, support.without(good, "namespaces"), "a path map without `namespaces`")


# --- the memory class of a namespace [CAP-03.b] -----------------------------------------------------------------

def test_every_namespace_is_governance_memory_or_product_data():
    spaces = support.namespaces(support.load_path_map())
    wrong = {name: value.get("memory_class") for name, value in spaces.items()
             if value.get("memory_class") not in MEMORY_CLASSES}
    assert not wrong, f"{support.PATH_MAP_REL}: `memory_class` is not one of {MEMORY_CLASSES} in {wrong}"


@pytest.mark.local_only
def test_each_memory_class_is_accepted(path_map, check):
    schema, document = path_map
    name = _first_namespace(document)
    for memory_class in MEMORY_CLASSES:
        check.accepts(schema, support.set_at(document, ("namespaces", name, "memory_class"), memory_class),
                      f"a path map whose namespace {name!r} has memory class {memory_class}")


@pytest.mark.local_only
@pytest.mark.parametrize("memory_class", (["governance", "product"], "governance,product", "both", None))
def test_a_namespace_cannot_be_both_or_neither(memory_class, path_map, check):
    """One namespace is one class: both at once, a third word and no class at all are refused."""
    schema, document = path_map
    name = _first_namespace(document)
    check.good(schema, document, support.PATH_MAP_REL)
    if memory_class is None:
        bad = support.delete_at(document, ("namespaces", name, "memory_class"))
    else:
        bad = support.set_at(document, ("namespaces", name, "memory_class"), memory_class)
    check.refuses(schema, bad, f"a path map whose namespace {name!r} has memory class {memory_class!r}")


# --- state_class of the path map [CAP-07.b] ---------------------------------------------------------------------

def test_the_path_map_records_its_state_class():
    """DEC-229: the path map is AUTHORITATIVE."""
    value = support.load_path_map().get("state_class")
    assert value == "AUTHORITATIVE", f"{support.PATH_MAP_REL}: `state_class` is {value!r}, not AUTHORITATIVE"


@pytest.mark.local_only
def test_the_path_map_schema_takes_the_six_state_classes_and_no_other(path_map, check):
    schema, document = path_map
    for value in support.STATE_CLASSES:
        check.accepts(schema, support.replaced(document, "state_class", value),
                      f"a path map whose `state_class` is {value}")
    check.refuses(schema, support.replaced(document, "state_class", "OFFICIAL"),
                  "a path map whose `state_class` is 'OFFICIAL'")
    check.refuses(schema, support.without(document, "state_class"), "a path map without `state_class`")


# --- the gov CLI still loads it (DEC-185, DEC-228) --------------------------------------------------------------

def test_the_gov_cli_loads_the_committed_path_map(tmp_path):
    """DEC-185: every gov command loads governance/project/path-map.yaml and refuses an invalid one. DEC-228: W1-08
    does not change the loader in `src/gov/config/`, so the committed path map must also fit the minimal shape that
    loader accepts, and must not turn every command of this repository into CONFIG_INVALID."""
    source = support.REPO_ROOT / support.PATH_MAP_REL
    assert source.is_file(), f"this repository has no path map: {support.PATH_MAP_REL} does not exist"
    project = tmp_path / "project"
    (project / "governance" / "project").mkdir(parents=True)
    (project / support.PATH_MAP_REL).write_bytes(source.read_bytes())
    register = support.load_path_map().get("decision_register")
    if isinstance(register, str):  # the project holds the register file its path map names
        (project / register).parent.mkdir(parents=True, exist_ok=True)
        (project / register).write_text("# Decisions\n", encoding="utf-8")
    home = tmp_path / "home"
    home.mkdir()
    scripts = tomllib.loads((support.REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["scripts"]
    module, _, attribute = scripts["gov"].partition(":")
    launcher = tmp_path / "run_gov.py"  # not `gov.py`: the script's folder is first on sys.path
    launcher.write_text(
        "import sys\n"
        f"import {module.strip()} as _module\n"
        "_target = _module\n"
        f"for _name in {attribute.strip()!r}.split('.'):\n"
        "    _target = getattr(_target, _name)\n"
        "sys.argv[0] = 'gov'\n"
        "sys.exit(_target())\n",
        encoding="utf-8",
    )
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(support.REPO_ROOT / "src"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    done = subprocess.run([sys.executable, str(launcher), "status", "--json", "--root", str(project)],
                          cwd=str(project), env=env, capture_output=True, text=True, timeout=30,
                          stdin=subprocess.DEVNULL)
    assert "CONFIG_INVALID" not in done.stdout, f"gov refuses the committed path map:\n{done.stdout}\n{done.stderr}"
    assert done.returncode == 0, f"gov status ends with {done.returncode}:\n{done.stdout}\n{done.stderr}"

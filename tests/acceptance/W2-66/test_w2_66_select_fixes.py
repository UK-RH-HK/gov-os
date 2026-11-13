"""W2-66c (DAEO-btcs): the live test map's fixes of DEC-1100 (1) (ACT-SELECT-FIXES-1), pinned from the ticket's lines.

Written by the independent test designer from the KPI lines S1-S6 and F1-F3 and the README's "Interface" (no
implementation read). The product is ``gov.close.select``: ``load_map(root)`` reads the live test map, ``match(path,
pattern)`` reads a pattern with the ``allowed_paths`` grammar, ``plan(root, wbs, ticket=...)`` makes the selection.

What a change of a path reaches "through a coupling" is the union of the ``suites`` of every coupling one of whose
``paths`` the path matches. A target covers a node id when it is that node id (or its beginning at a ``::``), its file,
or a folder above it.

F3: no case runs pytest or starts a ``gov`` command; ``subprocess`` runs ``git`` only (``git ls-files`` in this
repository, and the planted repository under ``tmp_path``); nothing outside this repository's tracked files and the
cases' own temporary folders is read. No network; deterministic.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest
import yaml

from gov.close import select

ROOT = Path(__file__).resolve().parents[3]

# S1
SETTINGS_PATHS = (".claude/settings.json", ".rulesync/hooks.jsonc", ".rulesync/permissions.jsonc")
SETTINGS_SUITES = ("tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py",
                   "tests/acceptance/W1-46/test_w1_46_research_installs.py",
                   "tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py")
# S2
CHECKS_FOLDER = "template/governance/kernel/checks"
TIME_LIMIT_FILE = "tests/acceptance/W2-54/test_w2_54_time_limit.py"
NO_WEAKENING = f"{TIME_LIMIT_FILE}::test_no_hard_block_check_is_weakened"
# S3
W1_01_MERGES = ("tests/acceptance/W1-01/test_w1_01_integration_merges.py::"
                "test_the_integration_merges_of_this_repository_pass")
W1_50_FOUND = "tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py::test_the_two_whole_tree_fixtures_are_found"
W1_28_CHECK = "tests/acceptance/W1-28/test_w1_28_fixture_copies.py"
# S4
LIVE_MAP_FILE = "tests/acceptance/W2-66/test_w2_66_live_test_map.py"
RECORD_ONLY_FUNCTION = "test_every_record_of_each_of_dec_891_s_places_is_record_only"
RECORD_ONLY_CASE = f"{LIVE_MAP_FILE}::{RECORD_ONLY_FUNCTION}"
TEST_MAP_REL = "governance/project/test-map.yaml"
TEST_MAP_SCHEMA_REL = "template/governance/kernel/schemas/test-map.schema.json"
TICKETS = ".tickets"


# -- helpers: the live map read by the product ----------------------------------

def _tracked_files():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, text=True, check=True)
    return [path for path in out.stdout.split("\0") if path]


def _tracked_under(folder):
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", "--", folder],
                         capture_output=True, text=True, check=True)
    return [path for path in out.stdout.split("\0") if path]


@pytest.fixture(scope="module")
def tracked():
    return set(_tracked_files())


@pytest.fixture(scope="module")
def live_map():
    test_map, why = select.load_map(ROOT)
    assert why is None and isinstance(test_map, dict), f"the product cannot read the live test map: {why}"
    return test_map


def _couplings(test_map):
    couplings = test_map.get("couplings") or []
    assert isinstance(couplings, list) and couplings, "the live test map declares no couplings"
    return couplings


def _matched_couplings(test_map, path):
    """Every coupling one of whose ``paths`` the path matches, by the product's matcher."""
    return [c for c in _couplings(test_map) if any(select.match(path, pattern) for pattern in c.get("paths") or [])]


def reached(test_map, path):
    """The union of the targets of every coupling whose patterns the path matches."""
    return [t for c in _matched_couplings(test_map, path) for t in c.get("suites") or []]


def _file_and_rest(target):
    path, _, rest = target.partition("::")
    return path.rstrip("/"), rest


def covers_node(target, node):
    """Whether running ``target`` runs the case ``node`` (the node id itself or its beginning, its file, a folder)."""
    t_path, t_rest = _file_and_rest(target)
    n_path, n_rest = _file_and_rest(node)
    if t_rest:
        return t_path == n_path and (n_rest == t_rest or n_rest.startswith(t_rest + "::"))
    return n_path == t_path or n_path.startswith(t_path + "/")


def covers_file(target, file):
    """Whether ``target`` runs the whole file: the file itself or a folder above it (a node id does not)."""
    t_path, t_rest = _file_and_rest(target)
    return not t_rest and (file == t_path or file.startswith(t_path + "/"))


def _function(rest):
    return rest.split("::")[0].split("[")[0]


# -- S5's helper: every target exists, read as text -------------------------------

_DEF = re.compile(r"^(?P<indent>[ \t]*)(?:async[ \t]+)?(?P<kind>def|class)[ \t]+(?P<name>\w+)")


def _definitions(text):
    """``(indent, kind, name, line number)`` of every ``def`` and ``class`` line of a source text."""
    found = []
    for number, line in enumerate(text.splitlines()):
        match = _DEF.match(line)
        if match:
            found.append((len(match.group("indent").expandtabs()), match.group("kind"), match.group("name"), number))
    return found


def _defines(text, names):
    """Whether the text defines what the node id's parts name: a top-level function or class, or a class with the
    method named after it (a parameter set read as its function)."""
    lines = text.splitlines()
    defs = _definitions(text)
    names = [name.split("[")[0] for name in names]
    if len(names) == 1:
        return any(indent == 0 and name == names[0] for indent, _, name, _ in defs)
    if len(names) != 2:
        return False
    for indent, kind, name, number in defs:
        if indent != 0 or kind != "class" or name != names[0]:
            continue
        end = len(lines)
        for later in range(number + 1, len(lines)):
            line = lines[later]
            if line.strip() and not line.startswith((" ", "\t")):
                end = later
                break
        if any(number < n < end and i > 0 and kind2 == "def" and name2 == names[1]
               for i, kind2, name2, n in defs):
            return True
    return False


def unresolved_targets(targets, tracked, root=ROOT):
    """Every target that names no tracked file or folder, or a node id whose file is not tracked or does not define
    the function (with its class, when named): ``[(target, FILE_GONE | CASE_GONE)]``. No collection, no run."""
    out = []
    for target in targets:
        path, rest = _file_and_rest(target)
        is_file = path in tracked
        is_folder = any(p.startswith(path + "/") for p in tracked)
        if not rest:
            if not (is_file or is_folder):
                out.append((target, "FILE_GONE"))
            continue
        if not is_file:
            out.append((target, "FILE_GONE"))
            continue
        text = (root / path).read_text(encoding="utf-8")
        if not _defines(text, rest.split("::")):
            out.append((target, "CASE_GONE"))
    return out


# -- S1: settings and hook wiring --------------------------------------------------

@pytest.mark.parametrize("path", SETTINGS_PATHS)
def test_s1_a_settings_or_hook_wiring_change_reaches_the_three_suites(live_map, path):
    targets = reached(live_map, path)
    missing = [suite for suite in SETTINGS_SUITES if not any(covers_file(t, suite) for t in targets)]
    assert not missing, f"no coupling the live map declares takes a change of {path} to {missing}"


# -- S2: the declared checks reach W2-54's no-weakening case alone -------------------

def _checks_files():
    return _tracked_under(CHECKS_FOLDER)


@pytest.mark.parametrize("path", _checks_files())
def test_s2_a_declared_check_change_reaches_w2_54_s_no_weakening_case_alone(live_map, path):
    targets = reached(live_map, path)
    assert any(covers_node(t, NO_WEAKENING) for t in targets), \
        f"no coupling takes a change of {path} to {NO_WEAKENING}"
    wider = [t for t in targets if covers_file(t, TIME_LIMIT_FILE)
             or (_file_and_rest(t)[0] == TIME_LIMIT_FILE and _function(_file_and_rest(t)[1])
                 != NO_WEAKENING.split("::")[1])]
    assert not wider, f"a coupling a change of {path} matches names more of {TIME_LIMIT_FILE} than the case: {wider}"


# -- S3: the history rule and the fixture scans ----------------------------------------

PLANTED = {
    "py": "tests/acceptance/W3-98/test_w3_98_planted.py",
    "md": "tests/acceptance/W3-98/notes_planted.md",
    "conftest": "tests/acceptance/W3-98/conftest.py",
}


@pytest.mark.parametrize("kind", list(PLANTED))
def test_s3_an_acceptance_change_reaches_the_history_rule_and_a_python_one_the_fixture_scans(live_map, kind):
    path = PLANTED[kind]
    targets = reached(live_map, path)
    assert any(covers_node(t, W1_01_MERGES) for t in targets), \
        f"no coupling takes a change of {path} ({kind}) to {W1_01_MERGES}"
    reaches_w1_50 = any(covers_node(t, W1_50_FOUND) for t in targets)
    if path.endswith(".py"):
        assert reaches_w1_50, f"no coupling takes a change of {path} ({kind}) to {W1_50_FOUND}"
        assert any(covers_file(t, W1_28_CHECK) for t in targets), \
            f"no coupling takes a change of {path} ({kind}) to {W1_28_CHECK}"
    else:
        assert not reaches_w1_50, f"a change of {path} ({kind}), not a Python source, reaches {W1_50_FOUND}"


# -- S4: W2-66's record-only case is always run ------------------------------------------

def test_s4_the_record_reading_set_holds_w2_66_s_record_only_case(live_map):
    targets = live_map.get("record_reading") or []
    assert any(covers_node(t, RECORD_ONLY_CASE) for t in targets), \
        f"the live map's record_reading does not hold {RECORD_ONLY_CASE}"


def _root_conftest(config):
    want = (ROOT / "tests" / "conftest.py").resolve()
    for plugin in config.pluginmanager.get_plugins():
        where = getattr(plugin, "__file__", None)
        if where and Path(where).resolve() == want and hasattr(plugin, "optin_entries"):
            return plugin
    raise AssertionError("the fixture is wrong: tests/conftest.py (its optin_entries) is not loaded in this run")


def _names_the_function(target):
    path, rest = _file_and_rest(target)
    if not rest:
        return LIVE_MAP_FILE == path or LIVE_MAP_FILE.startswith(path + "/")
    return path == LIVE_MAP_FILE and _function(rest) == RECORD_ONLY_FUNCTION


def test_s4_no_opt_in_list_leaves_a_row_of_the_record_only_case_out(request):
    entries = _root_conftest(request.config).optin_entries(ROOT / "tests")
    assert entries, "the fixture is wrong: the opt-in lists hold no entry"
    naming = [f"{kind}: {target} ({name})" for kind, target, name in entries if _names_the_function(target)]
    assert not naming, f"opt-in list entries name {RECORD_ONLY_CASE}, so a plain run leaves rows of it out: {naming}"


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), "-c", "user.name=planted", "-c", "user.email=planted@example.invalid",
                    "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                   capture_output=True, text=True, check=True)


def _head(root):
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


def _write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _stubs(test_map):
    """A one-line stand-in for every target the map names (record-reading, every-close, couplings), so that each
    resolves in the planted repository: a folder gets a test file, a node id's file the function or class it names."""
    targets = list(test_map.get("record_reading") or []) + list(test_map.get("every_close") or [])
    targets += [t for c in test_map.get("couplings") or [] for t in c.get("suites") or []]
    files = {}
    for target in targets:
        path, rest = _file_and_rest(target)
        if not path.endswith(".py"):
            files.setdefault(f"{path}/test_planted_stub.py", set()).add(("test_planted_stub",))
            continue
        names = files.setdefault(path, set())
        if rest:
            names.add(tuple(part.split("[")[0] for part in rest.split("::")))
    out = {}
    for path, names in files.items():
        functions = sorted(n[0] for n in names if len(n) == 1)
        classes = {}
        for n in names:
            if len(n) == 2:
                classes.setdefault(n[0], set()).add(n[1])
        text = "".join(f"def {f}():\n    pass\n\n\n" for f in functions)
        text += "".join(f"class {c}:\n" + "".join(f"    def {m}(self):\n        pass\n\n" for m in sorted(ms)) + "\n"
                        for c, ms in sorted(classes.items()))
        out[path] = text or "def test_planted_file():\n    pass\n"
    return out


def _plant(root):
    """A git repository under ``tmp_path``: the live test map, its schema and the tickets (read from this repository's
    tracked files), a stand-in for every target the map names, a closing ticket of its own with a suite; a green night
    naming that base; then one commit holding only a record under governance/project/orchestration/."""
    root.mkdir()
    _git(root, "init", "-q")
    map_text = (ROOT / TEST_MAP_REL).read_text(encoding="utf-8")
    _write(root, TEST_MAP_REL, map_text)
    _write(root, TEST_MAP_SCHEMA_REL, (ROOT / TEST_MAP_SCHEMA_REL).read_text(encoding="utf-8"))
    tickets = _tracked_under(TICKETS)
    assert tickets, "the fixture is wrong: no tracked ticket"
    for rel in tickets:
        _write(root, rel, (ROOT / rel).read_text(encoding="utf-8"))
    for rel, text in _stubs(yaml.safe_load(map_text) or {}).items():
        _write(root, rel, text)
    _write(root, f"{TICKETS}/PLANT-own.md", "---\nid: PLANT-own\nwbs_id: W9-own\nallowed_paths:\n- src/planted/**\n---\n")
    _write(root, "src/planted/own.py", "OWN = 1\n")
    _write(root, "tests/acceptance/W9-own/test_w9_own.py", "def test_own():\n    pass\n")
    _write(root, "tests/unit/test_planted_unit.py", "def test_unit():\n    pass\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    base = _head(root)
    _write(root, f"docs/close/nightly/NR-20261111T000000Z-{base[:12]}.json",
           json.dumps({"branch": "w2/integrate", "head": base, "verdict": "green", "scope": "full"}) + "\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "a green night naming the base")
    _write(root, "governance/project/orchestration/planted-record-w2-66c.md", "# A planted orchestration record\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "one record under governance/project/orchestration/")
    return root


def test_s4_a_scoped_selection_of_a_records_only_change_selects_the_record_only_case(tmp_path):
    root = _plant(tmp_path / "planted")
    plan = select.plan(root, "W9-own", ticket="PLANT-own")
    why_full = plan.get("why_full")
    assert plan.get("scope") == "scoped", f"the planted records-only change is not selected scoped: {why_full}"
    selected = [(entry["target"], [w.get("reason") for w in entry.get("why") or []]) for entry in plan["selected"]]
    held = [target for target, reasons in selected
            if covers_node(target, RECORD_ONLY_CASE) and "RECORD_READING" in reasons]
    assert held, f"the scoped selection of a records-only change does not select {RECORD_ONLY_CASE} as record-reading"


# -- S5: every coupling's target exists ----------------------------------------------------

def test_s5_every_coupling_target_of_the_live_map_exists(live_map, tracked):
    targets = [t for c in _couplings(live_map) for t in c.get("suites") or []]
    gone = unresolved_targets(targets, tracked)
    assert not gone, f"coupling targets of the live map that name nothing in this tree: {gone}"


def test_s5_a_planted_map_with_a_misspelt_node_id_reds_the_same_helper(tracked):
    misspelt = W1_01_MERGES + "s"
    planted = {"couplings": [{"paths": ["planted/**"], "why": "planted",
                              "suites": [W1_01_MERGES, misspelt, f"{W1_01_MERGES.split('::')[0]}::Nope::{'x'}",
                                         "tests/acceptance/W9-none/", "tests/acceptance/W1-01/"]}]}
    targets = [t for c in _couplings(planted) for t in c["suites"]]
    gone = unresolved_targets(targets, tracked)
    assert gone == [(misspelt, "CASE_GONE"), (f"{W1_01_MERGES.split('::')[0]}::Nope::x", "CASE_GONE"),
                    ("tests/acceptance/W9-none/", "FILE_GONE")], gone

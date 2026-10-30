"""Part 2: this repository's test map, its schema and the template's copy (KPI 2, 3, 5, 8, 9; DEC-896 item 2).

Read only. The lists are judged by the paths they place in this repository's tracked tree, read with the
grammar of a ticket's ``allowed_paths`` (README, "Interface"). README, "Part 2".
"""

import json
import re
import subprocess

import pytest
import yaml

import w2_66_support as support

ROOT = support.REPO_ROOT

RETRIEVAL_CORE = tuple(f"src/gov/retrieval/{name}.py" for name in
                       ("__init__", "chunking", "lexical", "semantic", "ollama", "rerank", "fusion", "retrieve"))
WIDEST = ("src/gov/config/loader.py", "src/gov/tasks/tickets.py", "src/gov/store/loader.py")
# ``src/gov/errors.py`` of the KPI line does not exist; the envelope's error module is ``src/gov/cli/errors.py``
# (I4 F12 counts it under the CLI). README, "Discoveries".
CLI_CORE = ("src/gov/cli/main.py", "src/gov/cli/errors.py")
SHARED_CORE_FOLDERS = ("src/gov/close", "src/gov/guard", "src/gov/check", "src/gov/records",
                       "template/governance/kernel/hooks", "src/gov/hooks")
MAPS = (support.PATH_MAP_REL, support.TEST_MAP_REL)

# DEC-891's record places. "The plan files" are the plan's documents, not the code kept beside them.
RECORD_PLACES = (".tickets/", "docs/checkpoints/", "docs/close/", "docs/probes/", "docs/DECISION_REGISTER.md",
                 "docs/plan/", "governance/project/orchestration/")
# DEC-891's code, tests and kernel.
CODE_PLACES = ("src/", "tests/", "template/", ".rulesync/", ".claude/", "schemas/", "fixtures/")
CODE_SUFFIXES = (".py", ".sh", ".js", ".ts", ".toml", ".cfg", ".ini")

# The record-reading set's first list: DEC-889 item 2's start, and lens I's readers of a DEC-891 record path
# (I2 F6, I3 F5, I4 F6, I1 §4.1), filtered by KPI 5's rule. ``(target, whole)``: ``whole`` targets must be held
# whole; the others by any entry within them (the reports name only some of their cases).
RECORD_READERS = (
    ("tests/acceptance/W1-06/test_w1_06_approvals.py", True),          # gate (f): the register's approvals
    ("tests/acceptance/W1-08/test_w1_08_path_map.py", True),           # gate (f)
    ("tests/acceptance/W1-27/test_w1_27_path_compliance_r2.py", True), # gate (f): scans the tree
    ("tests/acceptance/W1-07/test_w1_07_envelope.py", True),           # gate (f): every command on the tree
    ("tests/acceptance/W2-54/test_w2_54_green_here.py", True),         # DEC-889 item 2
    ("tests/acceptance/W1-33/test_w1_33_agent_definitions.py", True),  # DEC-889 item 2
    ("tests/acceptance/W1-49/test_w1_49_threshold.py", True),          # DEC-889 item 2: W1-49's window
    ("tests/acceptance/W1-10/test_w1_10_register.py::"
     "test_every_heading_of_this_repositorys_register_is_one_record_and_none_fails", True),   # I3 F5
    ("tests/acceptance/W1-10/test_w1_10_completeness.py::"
     "test_every_committed_ticket_and_adr_of_this_repository_is_in_the_graph", True),          # I3 F5
    ("tests/acceptance/W2-02/test_w2_02_green_here.py", True),         # I4 F6: .tickets/ and docs/
    ("tests/acceptance/W1-08/test_w1_08_ticket.py", True),             # I4 F6: the ticket files
    ("tests/acceptance/W1-08/test_w1_08_probe.py", True),              # I4 F6: the probe records
    ("tests/acceptance/W1-06/test_w1_06_install_approvals.py", True),  # I4 F6: the register's approvals
    ("tests/acceptance/W1-07/test_w1_07_config.py", True),             # I4 F6: the tickets
    ("tests/acceptance/W1-07/test_w1_07_config_details.py", True),     # I4 F6: the tickets
    ("tests/acceptance/W1-27/test_w1_27_doctor.py", True),             # I4 F6: the whole tree's text
    ("tests/acceptance/W1-42", False),                                 # I2 F6: the tickets, the exit record
    ("tests/acceptance/W1-26/test_w1_26_probe_records.py", False),     # I2 F6: docs/probes
    ("tests/acceptance/W1-48", False),                                 # I2 F6: the register's approvals
)

EVERY_CLOSE = ("tests/acceptance/W1-07/test_w1_07_envelope.py", "tests/acceptance/W1-07/test_w1_07_read_act.py",
               "tests/acceptance/W1-07/test_w1_07_registry.py")

# KPI 3's couplings and the synthesis's §4 lines: (a tracked path the coupling reads, the suites it must reach).
COUPLINGS = (
    ("src/gov/cli/main.py", ("tests/acceptance/W1-42",)),                                  # text read
    ("template/governance/kernel/templates/brief-lead.md", ("tests/acceptance/W1-42",)),   # text read
    (support.SERIAL_ONLY_REL, ("tests/acceptance/W1-30/test_w1_30_r11_declared_here.py",)),  # text read
    ("src/gov/retrieval/rerank_worker.py", ("tests/acceptance/W1-19/test_w1_19_real_models.py",
                                             "tests/acceptance/W1-21/test_w1_21_dev_tier.py",
                                             "tests/unit/semantic/test_rerank_process.py")),  # its own process
    ("src/gov/hooks/stop.py", ("tests/acceptance/W1-29", "tests/acceptance/W1-49", "tests/acceptance/W2-62",
                               "tests/unit/hooks")),
    ("template/governance/kernel/hooks/stop.py", ("tests/acceptance/W1-29", "tests/acceptance/W1-49",
                                                  "tests/acceptance/W2-62", "tests/unit/hooks")),
    ("template/governance/kernel/hooks/sessionstart.py", ("tests/acceptance/W1-31", "tests/acceptance/W1-37",
                                                          "tests/acceptance/W1-38", "tests/unit/telemetry")),
    ("template/governance/kernel/hooks/precompact.py", ("tests/acceptance/W1-31", "tests/acceptance/W1-37",
                                                        "tests/acceptance/W1-38", "tests/unit/telemetry")),
    (support.PATH_MAP_REL, tuple(f"tests/acceptance/{w}" for w in
                                 ("W1-16", "W1-17", "W1-19", "W1-20", "W1-21", "W1-22", "W1-24", "W2-54"))),
    (".gitleaks.toml", tuple(f"tests/acceptance/{w}" for w in
                             ("W1-16", "W1-17", "W1-19", "W1-20", "W1-21", "W1-22", "W1-24", "W2-54"))),
    ("template/.gitleaks.toml", tuple(f"tests/acceptance/{w}" for w in
                                      ("W1-16", "W1-17", "W1-19", "W1-20", "W1-21", "W1-22", "W1-24", "W2-54"))),
    ("src/gov/checkpoint/record.py", ("tests/acceptance/W1-30", "tests/acceptance/W1-31")),
    ("src/gov/decisions/checker.py", ("tests/acceptance/W1-30",)),
    ("src/gov/closure/command.py", ("tests/acceptance/W1-30",)),
    ("src/gov/adapters/portability.py", ("tests/acceptance/W1-30", "tests/acceptance/W1-26")),
    ("src/gov/context/command.py", ("tests/acceptance/W1-31",)),
    ("src/gov/secrets/__init__.py", ("tests/acceptance/W1-40",)),
    ("src/gov/retrieval/validate.py", ("tests/unit/validate",)),
    ("src/gov/retrieval/canary.py", ("tests/unit/validate",)),
    ("template/governance/kernel/roles/engineer.md", ("tests/acceptance/W1-38",)),
    ("template/governance/kernel/skills/planning/SKILL.md", ("tests/acceptance/W1-38",)),
)


def _tracked():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, text=True, check=True)
    return [path for path in out.stdout.split("\0") if path]


@pytest.fixture(scope="module")
def tracked():
    return _tracked()


def _load(rel):
    path = ROOT / rel
    assert path.is_file(), f"{rel} does not exist"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{rel} is not a YAML mapping"
    return data


_MISSING = "__missing__"


@pytest.fixture(scope="module")
def test_map():
    """The live test map; a marker where it cannot be read, so that each case fails on it (not an error)."""
    try:
        return _load(support.TEST_MAP_REL)
    except (AssertionError, yaml.YAMLError) as e:
        return {_MISSING: str(e)}


def _need(test_map):
    assert _MISSING not in test_map, test_map.get(_MISSING)
    return test_map


def _patterns(test_map, key):
    _need(test_map)
    patterns = test_map.get(key)
    assert isinstance(patterns, list) and patterns, f"the test map has no list under {key!r}"
    unread = [p for p in patterns if not support.readable_pattern(p)]
    assert not unread, f"{key} holds patterns outside the allowed_paths grammar (README, 'Interface'): {unread}"
    return patterns


def _placed(patterns, path):
    return any(support.matches(pattern, path) for pattern in patterns)


def _targets(test_map, key):
    _need(test_map)
    targets = test_map.get(key)
    assert isinstance(targets, list) and all(isinstance(t, str) and t for t in targets), \
        f"the test map has no list of pytest targets under {key!r}: {targets!r}"
    return targets


def _held(targets, target, whole=True):
    if any(support.covers(entry, target) for entry in targets):
        return True
    return not whole and any(support.covers(target, entry) for entry in targets)


# -- the files exist and are valid ---------------------------------------------

def _schema():
    path = ROOT / support.TEST_MAP_SCHEMA_REL
    assert path.is_file(), f"{support.TEST_MAP_SCHEMA_REL} does not exist"
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_schema_exists_and_is_a_valid_json_schema():
    jsonschema = pytest.importorskip("jsonschema")
    schema = _schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema.get("$schema", "").endswith("2020-12/schema"), "the schema is not draft 2020-12, as its siblings"


@pytest.mark.parametrize("rel", [support.TEST_MAP_REL, support.TEMPLATE_TEST_MAP_REL])
def test_the_test_map_and_the_template_s_copy_are_valid_against_the_schema(rel):
    jsonschema = pytest.importorskip("jsonschema")
    schema = _schema()
    errors = sorted(e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(_load(rel)))
    assert not errors, f"{rel} is not valid against {support.TEST_MAP_SCHEMA_REL}: {errors}"


def test_the_schema_refuses_a_map_without_a_shared_core_or_with_a_wrong_type():
    jsonschema = pytest.importorskip("jsonschema")
    schema = _schema()
    validator = jsonschema.Draft202012Validator(schema)
    good = _load(support.TEST_MAP_REL)
    for bad in ({k: v for k, v in good.items() if k != "shared_core"}, {**good, "shared_core": 7},
                {**good, "record_only": "docs/close/**"}):
        assert list(validator.iter_errors(bad)), f"the schema accepts a map it must refuse: {sorted(bad)}"


# -- KPI 2: the shared core ------------------------------------------------------

def test_the_shared_core_holds_every_named_member(test_map, tracked):
    core = _patterns(test_map, "shared_core")
    missing = []
    for folder in SHARED_CORE_FOLDERS:
        files = [p for p in tracked if p.startswith(folder + "/")]
        assert files, f"the fixture is wrong: no tracked file under {folder}"
        missing += [p for p in files if not _placed(core, p)]
    missing += [p for p in RETRIEVAL_CORE + WIDEST + CLI_CORE + MAPS if not _placed(core, p)]
    assert not missing, f"the shared core does not hold: {missing}"


ROOT_CONFTEST = "tests/conftest.py"
# The folders above every acceptance suite: a conftest in one is loaded by every run of each suite under it.
ABOVE_EVERY_SUITE = ("", "tests", "tests/acceptance")


def _conftests_above_every_suite():
    return [p for p in _tracked() if p.rsplit("/", 1)[-1] == "conftest.py"
            and (p.rsplit("/", 1)[0] if "/" in p else "") in ABOVE_EVERY_SUITE]


@pytest.mark.parametrize("path", _conftests_above_every_suite())
def test_a_conftest_every_run_of_the_suites_loads_is_shared_core(test_map, path):
    """``tests/conftest.py`` is loaded by every pytest run under ``tests/`` (and ``tests/acceptance/conftest.py``
    by every run of an acceptance suite): a change to it can reach every suite, so it runs the full regression.
    From the FULL review of 9174e358 (README, "Interface", item 1)."""
    assert ROOT_CONFTEST in _conftests_above_every_suite(), f"the fixture is wrong: {ROOT_CONFTEST} is not tracked"
    held = _placed(_patterns(test_map, "shared_core"), path)
    assert held, f"{path}, loaded by every run of the suites below it, is not in the shared core"


def test_the_retrieval_core_is_its_eight_modules_not_the_whole_package(test_map, tracked):
    core = _patterns(test_map, "shared_core")
    wider = [p for p in tracked if p.startswith("src/gov/retrieval/") and p not in RETRIEVAL_CORE
             and _placed(core, p)]
    assert not wider, f"the shared core holds retrieval files beyond the eight modules (P-IS-1 (a)): {wider}"


# -- DEC-891: the record-only paths ----------------------------------------------

def test_the_record_only_paths_are_dec_891_s_places_and_nothing_else(test_map, tracked):
    records = _patterns(test_map, "record_only")
    outside = [p for p in tracked if _placed(records, p) and not p.startswith(RECORD_PLACES)]
    assert not outside, f"record-only patterns place paths outside DEC-891's list: {outside[:20]}"


def test_the_record_only_list_hides_no_code_path(test_map, tracked):
    """Failure line 3: a code file kept in a record place (``sync_context.py``, the plan's tools) is code."""
    records = _patterns(test_map, "record_only")
    hidden = [p for p in tracked if _placed(records, p) and (p.endswith(CODE_SUFFIXES) or p.startswith(CODE_PLACES))]
    assert not hidden, f"the record-only list hides code paths: {hidden}"


@pytest.mark.parametrize("place", RECORD_PLACES)
def test_every_record_of_each_of_dec_891_s_places_is_record_only(test_map, tracked, place):
    records = _patterns(test_map, "record_only")
    files = [p for p in tracked if p.startswith(place) and not p.endswith(CODE_SUFFIXES)
             and (place != "docs/plan/" or re.fullmatch(r"docs/plan/[^/]+\.md", p))]
    assert files, f"the fixture is wrong: no tracked record under {place}"
    unplaced = [p for p in files if not _placed(records, p)]
    assert not unplaced, f"records of {place} the record-only list leaves out: {unplaced[:20]}"


@pytest.mark.parametrize("path", ["governance/project/tool-registry.yaml", support.PATH_MAP_REL,
                                  "governance/project/roster.yaml", "docs/adr/ADR-0001-threat-model.md"])
def test_paths_dec_891_does_not_name_are_not_record_only(test_map, path):
    assert not _placed(_patterns(test_map, "record_only"), path), f"{path} is record-only, against DEC-891's list"


# -- KPI 5: the record-reading set -----------------------------------------------

@pytest.mark.parametrize("target,whole", RECORD_READERS, ids=[t for t, _ in RECORD_READERS])
def test_the_record_reading_set_holds_each_reader_of_a_record_path(test_map, target, whole):
    assert (ROOT / target.split("::")[0]).exists(), f"the fixture is wrong: {target} does not exist"
    assert _held(_targets(test_map, "record_reading"), target, whole), \
        f"the record-reading set does not hold {target}"


def test_every_record_reading_target_exists(test_map):
    missing = [t for t in _targets(test_map, "record_reading") if not (ROOT / t.split("::")[0]).exists()]
    assert not missing, f"the record-reading set names targets that do not exist: {missing}"


# -- KPI 3: the every-close files and the couplings ------------------------------

def test_w1_07_s_three_contract_files_run_on_every_close(test_map):
    every = _targets(test_map, "every_close")
    missing = [t for t in EVERY_CLOSE if not _held(every, t)]
    assert not missing, f"the every-close list does not hold W1-07's contract files: {missing}"


def _couplings(test_map):
    _need(test_map)
    couplings = test_map.get("couplings")
    assert isinstance(couplings, list) and couplings, "the test map declares no couplings"
    for entry in couplings:
        assert isinstance(entry, dict) and entry.get("paths") and entry.get("suites") and entry.get("why"), \
            f"a coupling lacks paths, suites or why: {entry!r}"
        assert all(support.readable_pattern(p) for p in entry["paths"]), f"a coupling's pattern: {entry!r}"
    return couplings


@pytest.mark.parametrize("path,suites", COUPLINGS, ids=[p for p, _ in COUPLINGS])
def test_each_coupling_imports_cannot_see_is_declared(test_map, path, suites):
    assert (ROOT / path).exists(), f"the fixture is wrong: {path} does not exist"
    reached = [t for entry in _couplings(test_map) if _placed(entry["paths"], path) for t in entry["suites"]]
    missing = [s for s in suites if not _held(reached, s, whole=False)]
    assert not missing, f"no coupling takes a change of {path} to {missing}"


# W1-27's ``test_w2_67_copies.py`` loads these conftests by file path (``conftest_of``), which no import shows.
W2_67_COPIES = "tests/acceptance/W1-27/test_w2_67_copies.py"
LOADED_BY_FILE_PATH = ("W1-07", "W1-25", "W1-27")


def _suite_folder_of(path):
    """The suite folder that holds ``path`` (README, "Interface", item 3: a suite holding a changed file runs)."""
    parts = path.split("/")
    if parts[:2] == ["tests", "unit"]:
        return "tests/unit"
    return "/".join(parts[:3]) if parts[:2] == ["tests", "acceptance"] and len(parts) > 3 else None


@pytest.mark.parametrize("suite", LOADED_BY_FILE_PATH)
def test_a_conftest_loaded_by_file_path_reaches_the_file_that_loads_it(test_map, suite):
    """KPI 3: a change to W1-07's, W1-25's or W1-27's ``conftest.py`` reaches ``test_w2_67_copies.py``, through a
    declared coupling (W1-27's own conftest also through its suite folder). From the FULL review of 9174e358."""
    path = f"tests/acceptance/{suite}/conftest.py"
    assert (ROOT / path).is_file() and (ROOT / W2_67_COPIES).is_file(), f"the fixture is wrong: {path}"
    text = (ROOT / W2_67_COPIES).read_text(encoding="utf-8")
    assert "spec_from_file_location" in text and f'"{suite}"' in text, \
        f"the fixture is wrong: {W2_67_COPIES} no longer loads {path} by file path"
    reached = [t for entry in _couplings(test_map) if _placed(entry["paths"], path) for t in entry["suites"]]
    reached += [folder for folder in (_suite_folder_of(path),) if folder]
    held = _held(reached, W2_67_COPIES)
    assert held, f"no coupling takes a change of {path} to {W2_67_COPIES}, which loads it by file path"


# W1-28's held-out copy check (DEC-385) scans every Python source under ``tests/acceptance/``
# (``w1_28_copy_check.functions``: ``rglob("*.py")``, ``__pycache__`` aside) and runs the copying fixtures it finds:
# a file scan, which no import shows. Its cases that read the scan of the live tree.
W1_28_SUITE = "tests/acceptance/W1-28"
W1_28_CHECK = f"{W1_28_SUITE}/test_w1_28_fixture_copies.py"
W1_28_SCAN = f"{W1_28_SUITE}/w1_28_copy_check.py"
W1_28_SCANNING_CASES = ("test_the_check_finds_the_copying_fixtures_of_the_earlier_suites",
                        "test_a_fixture_that_copies_from_the_repository_leaves_the_held_out_file_out",
                        "test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs",
                        "test_the_reading_route_does_not_flag_this_suite_or_a_named_folder")
# Each kind of file the scan reads, of another ticket's suite, of a new suite folder, and at a depth below a suite
# folder: (kind, path, whether the path is tracked today).
W1_28_SCANNED = (
    ("conftest", "tests/acceptance/W1-05/conftest.py", True),
    ("test-file", "tests/acceptance/W1-05/test_w1_05_live_hooks.py", True),
    ("support-module", "tests/acceptance/W1-05/w1_05_support.py", True),
    ("other-module", "tests/acceptance/W1-47/w1_47_hook_time_limit.py", True),
    ("new-suite-folder", "tests/acceptance/W3-99/test_w3_99_first.py", False),
    ("new-suite-folder-conftest", "tests/acceptance/W3-99/conftest.py", False),
    ("below-a-suite-folder", "tests/acceptance/W1-05/fixtures/w1_05_tree.py", False),
)


def _w1_28_fixture_holds():
    scan = (ROOT / W1_28_SCAN).read_text(encoding="utf-8")
    check = (ROOT / W1_28_CHECK).read_text(encoding="utf-8")
    assert 'rglob("*.py")' in scan and '"__pycache__"' in scan, \
        f"the fixture is wrong: {W1_28_SCAN} no longer scans every Python source under tests/acceptance/"
    missing = [case for case in W1_28_SCANNING_CASES if f"def {case}(" not in check]
    assert not missing, f"the fixture is wrong: {W1_28_CHECK} no longer holds {missing}"


def _reached_by(test_map, path):
    """What a change of ``path`` selects, read from the map's public form (README, "Interface", items 1 and 3):
    ``None`` for the full regression (the shared core), else the targets of every coupling whose ``paths`` match
    it and the suite folder that holds it."""
    if _placed(_patterns(test_map, "shared_core"), path):
        return None
    reached = [t for entry in _couplings(test_map) if _placed(entry["paths"], path) for t in entry["suites"]]
    return reached + [folder for folder in (_suite_folder_of(path),) if folder]


def _runs_w1_28_s_check(reached):
    return reached is None or all(_held(reached, f"{W1_28_CHECK}::{case}") for case in W1_28_SCANNING_CASES)


def _resolves(target):
    """Whether the tree holds ``target``: its file or folder and, for a node id, the function or class it names
    after the file (a parameter set read as its function)."""
    path, _, rest = target.partition("::")
    if not (ROOT / path).exists():
        return False
    if not rest:
        return True
    name = rest.split("::")[0].split("[")[0]
    text = (ROOT / path).read_text(encoding="utf-8") if (ROOT / path).is_file() else ""
    return re.search(rf"^\s*(?:async\s+)?(?:def|class)\s+{re.escape(name)}\b", text, re.MULTILINE) is not None


@pytest.mark.parametrize("kind,path,tracked_today", W1_28_SCANNED, ids=[kind for kind, _, _ in W1_28_SCANNED])
def test_a_change_to_each_kind_of_file_w1_28_s_scan_reads_selects_its_check(test_map, kind, path, tracked_today):
    """KPI 15 (DEC-912 item 3, P2): W1-28's held-out copy check is coupled to every file under tests/acceptance/
    that its scan reads, so a change to any of them runs it; the target the live map names for it exists.
    From the second FULL review (DEC-136). README, "Part 5"."""
    _w1_28_fixture_holds()
    assert (ROOT / path).is_file() == tracked_today, f"the fixture is wrong: {path} exists: {not tracked_today}"
    # Boolean asserts: a failure names the path and the check, never the map's entries.
    reached = _reached_by(test_map, path)
    selects = _runs_w1_28_s_check(reached)
    assert selects, \
        f"a change to {path} ({kind}), which W1-28's scan reads, does not select {W1_28_CHECK}'s scanning cases"
    named = [t for t in reached or [] if support.within(t, W1_28_SUITE) or support.covers(t, W1_28_CHECK)]
    unresolved = sum(1 for t in named if not _resolves(t))
    assert unresolved == 0, f"{unresolved} target(s) the live map names for {W1_28_CHECK} do not resolve in this tree"


def test_every_python_source_w1_28_s_scan_reads_selects_its_check(test_map, tracked):
    """KPI 15 over the whole tracked tree: every ``*.py`` under tests/acceptance/ (``__pycache__`` aside)."""
    _w1_28_fixture_holds()
    scanned = [p for p in tracked if p.startswith("tests/acceptance/") and p.endswith(".py")
               and "__pycache__" not in p.split("/")]
    assert len(scanned) > 100, f"the fixture is wrong: only {len(scanned)} Python sources under tests/acceptance/"
    missed = [p for p in scanned if not _runs_w1_28_s_check(_reached_by(test_map, p))]
    every = not missed
    assert every, (f"{len(missed)} of the {len(scanned)} Python sources W1-28's scan reads do not select "
                   f"{W1_28_CHECK}, among them {missed[:6]}")


@pytest.mark.parametrize("unit", ["deploy/gov-index.service", "gov.socket", "a/b/gov-nightly.timer"])
def test_w1_18_s_listing_of_the_tree_s_unit_files_is_declared(test_map, unit):
    """W1-18 lists every service, socket and timer unit of the working tree (I3 §4.1 item 6): a new one, at any
    depth, reaches it. The tree holds none today, so the paths are examples."""
    reached = [t for entry in _couplings(test_map) if _placed(entry["paths"], unit) for t in entry["suites"]]
    assert _held(reached, "tests/acceptance/W1-18", whole=False), f"no coupling takes a change of {unit} to W1-18"


def _declared_modules():
    """The source file of every module a kernel check declaration runs (``python3 -m gov.<module>``)."""
    found = set()
    for declaration in sorted((ROOT / "template/governance/kernel/checks").glob("*.yaml")):
        command = str((yaml.safe_load(declaration.read_text(encoding="utf-8")) or {}).get("command", ""))
        match = re.search(r"-m\s+(gov(?:\.\w+)+)", command)
        if not match:
            continue
        base = ROOT / "src" / match.group(1).replace(".", "/")
        for candidate in (base.with_suffix(".py"), base / "__main__.py", base / "__init__.py"):
            if candidate.is_file():
                found.add(candidate.relative_to(ROOT).as_posix())
                break
    return sorted(found)


def test_every_module_a_declared_check_runs_reaches_w1_26(test_map):
    core = _patterns(test_map, "shared_core")
    modules = _declared_modules()
    assert modules, "the fixture is wrong: no declared check runs a gov module"
    missing = []
    for module in modules:
        if _placed(core, module):
            continue
        reached = [t for entry in _couplings(test_map) if _placed(entry["paths"], module) for t in entry["suites"]]
        if not _held(reached, "tests/acceptance/W1-26", whole=False):
            missing.append(module)
    assert not missing, f"modules a declared check runs that reach neither the shared core nor W1-26: {missing}"


# -- DEC-896 item 2: test_inputs moved; KPI 8 and 9: the settings -----------------

def test_the_path_map_s_test_inputs_are_in_the_test_map(test_map):
    inputs = yaml.safe_load((ROOT / support.PATH_MAP_REL).read_text(encoding="utf-8")).get("test_inputs")
    if inputs is None:
        pytest.skip("the path map no longer holds test_inputs (the orchestrator's edit is done)")
    moved = _need(test_map).get("test_inputs")
    assert isinstance(moved, list) and set(inputs) <= set(moved), \
        f"the test map does not hold the path map's test_inputs {inputs}: {moved!r}"


def test_the_per_test_limit_is_above_the_slowest_test_measured(test_map):
    limit = _need(test_map).get(support.PER_TEST_TIMEOUT_KEY, support.DEFAULT_PER_TEST_TIMEOUT)
    assert isinstance(limit, (int, float)) and not isinstance(limit, bool) and limit >= 900, \
        f"the per-test limit is not above the slowest measured test (900 s held in the trial): {limit!r}"


def test_the_distribution_mode_stays_the_default_and_is_not_worksteal(test_map):
    mode = _need(test_map).get(support.DISTRIBUTION_KEY, support.DEFAULT_DISTRIBUTION)
    assert mode == support.DEFAULT_DISTRIBUTION, \
        f"the distribution mode is {mode!r}: worksteal waits until the nested reruns are gone (DEC-892 a)"

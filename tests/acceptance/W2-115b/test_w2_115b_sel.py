"""A trustworthy impact selection (plan item 1-0, DEC-1244 X-1; ``.tickets/DAEO-j9z6.md`` "Fix: a trustworthy impact
selection, SEL-1 to SEL-3").

SEL-1: ``gov queue <T>=<branch> --select`` counts the branch's own change alone, never what the base added since the
green record nor the ticket's earlier landed commits. SEL-2: the live test map holds the edges it lacked, each read by
``select.scoped`` on a planted tree. SEL-3: a path the selection places nowhere is named (under ``unplaced``) and refuses
with the line to add; a record-only document passes with its notice.

SEL-1 and SEL-3 plant a project per case (``w2_115b_sel_support.plant``) and run ``gov queue`` as a program. SEL-2 plants
one project holding this repository's live test map (read at test time) and a stub for every target the map names, and
calls ``select.scoped`` in the test's process: the call is read-only, takes a second, and needs no branch per edge.
"""

from __future__ import annotations

import os

import pytest
import yaml

import w2_115b_sel_support as sel
import w2_115b_support as support
from w2_115b_sel_support import chosen_object, plant, refused, select
from w2_115b_support import A, B

DOC = "docs/emergency-2/briefs/LEAD-plan.md"    # outside record_only, placed by nothing: base-side noise
SCRIPT = "repin.sh"
SUITES_OWN = sel.OWN_SUITES
BASE_NOISE = [{sel.GIZMO: "# the gizmo, moved on the base\nVALUE = 1\n"}, {sel.GADGET: "# B's gadget, moved on the base\nVALUE = 1\n"},
              {DOC: "# a lead brief\n"}, {SCRIPT: "#!/bin/sh\necho repin\n"}]


# -- SEL-1: the branch's own change ------------------------------------------------------------------------------------

def test_sel1_what_the_base_added_after_the_green_record_selects_nothing(planted):
    p = plant(planted, BASE_NOISE)
    chosen = chosen_object(select(p))
    assert sorted(chosen.get("suites", [])) == SUITES_OWN, \
        f"the branch changes the widget alone; suites: {chosen.get('suites')}"
    assert support.node(support.GIZMO[0]).split("::")[0] not in chosen["suites"]


def test_sel1_the_base_s_unplaced_paths_are_neither_refused_nor_listed(planted):
    p = plant(planted, BASE_NOISE)
    run = select(p)
    chosen = chosen_object(run)
    assert chosen.get("unplaced_base") == [], f"unplaced_base: {chosen.get('unplaced_base')!r}"
    assert DOC not in run["stdout"] and SCRIPT not in run["stdout"], support.describe(run)


def test_sel1_the_ticket_s_earlier_landed_commit_is_not_counted(planted):
    earlier = ({sel.HELPER: "# the helper, changed by an earlier landing of the ticket\nVALUE = 2\n"},
               ["Task: PROJ-aaaa", "Role: engineer"])
    p = plant(planted, [earlier])
    chosen = chosen_object(select(p))
    assert sorted(chosen.get("suites", [])) == SUITES_OWN, \
        f"an earlier commit of the ticket on the base is not this landing's change; suites: {chosen.get('suites')}"


def test_sel1_an_unplaced_path_of_the_ticket_s_earlier_commit_does_not_refuse(planted):
    earlier = ({"tools/earlier.sh": "#!/bin/sh\necho earlier\n"}, ["Task: PROJ-aaaa", "Role: engineer"])
    p = plant(planted, [earlier])
    chosen = chosen_object(select(p))
    assert sorted(chosen.get("suites", [])) == SUITES_OWN, f"suites: {chosen.get('suites')}"


# -- SEL-2: the live map's edges ---------------------------------------------------------------------------------------

EDGES = [   # (a changed path, a suite its change must select)
    ("governance/project/release-authority.yaml", "tests/acceptance/W2-209/"),
    ("governance/project/indep-walls/wall_hook.py", "tests/acceptance/W2-178/"),
    ("governance/project/indep-walls/wall_hook.py", "tests/acceptance/W2-149/"),
    ("governance/project/indep-walls/settings.json.tmpl", "tests/acceptance/W2-178/"),
    ("governance/project/indep-walls/settings.json.tmpl", "tests/acceptance/W2-149/"),
    ("governance/project/orchestration/tools/indep_launch.py", "tests/acceptance/W2-178/"),
    ("governance/project/orchestration/tools/indep_launch.py", "tests/acceptance/W2-149/"),
    ("src/gov/rebuild/command.py", "tests/acceptance/W2-116/"),
    ("src/gov/rebuild/seed.py", "tests/acceptance/W2-116/"),
    ("governance/project/rebuild.yaml", "tests/acceptance/W2-116/"),
    ("template/lefthook.yml.jinja", "tests/acceptance/W2-16/"),
    ("template/lefthook.yml.jinja", "tests/acceptance/W2-208/"),
    ("template/lefthook.yml.jinja", "tests/unit/update"),
    ("template/openspec/config.yaml", "tests/acceptance/W2-16/"),
    ("template/openspec/config.yaml", "tests/acceptance/W2-208/"),
    ("template/openspec/config.yaml", "tests/unit/update"),
    ("template/KIT-FILE-OF-SEL2.txt", "tests/acceptance/W2-16/"),
    ("template/KIT-FILE-OF-SEL2.txt", "tests/acceptance/W2-208/"),
    ("template/KIT-FILE-OF-SEL2.txt", "tests/unit/update"),
]
LIVE_MAP = support.REPO_ROOT / support.TEST_MAP_REL


def _stub(target: str) -> dict:
    """The planted file that makes a map-named target resolve: a folder's one test file, or a ``.py`` file defining
    the names of its node id."""
    path, _, case = target.partition("::")
    if not path.endswith(".py"):
        return {f"{path.rstrip('/')}/test_stub.py": "def test_stub():\n    pass\n"}
    names = [n.split("[")[0] for n in case.split("::")] if case else []
    if len(names) >= 2:
        body = f"class {names[0]}:\n    def {names[1]}(self):\n        pass\n"
    else:
        body = f"def {names[0] if names else 'test_stub'}():\n    pass\n"
    return {path: body}


@pytest.fixture(scope="module")
def live(tmp_path_factory):
    """A planted project (A and B) holding the live test map and a stub for every target it names, and the paths of
    EDGES, committed."""
    assert LIVE_MAP.is_file(), f"fixture: no live test map at {LIVE_MAP}"
    text = LIVE_MAP.read_text(encoding="utf-8")
    test_map = yaml.safe_load(text)
    targets = [s for c in test_map.get("couplings") or [] for s in c.get("suites") or []]
    targets += list(test_map.get("record_reading") or []) + list(test_map.get("every_close") or [])
    files = {support.TEST_MAP_REL: text, **{rel: "x\n" for rel, _ in EDGES}}
    for target in targets:
        files.update({rel: body for rel, body in _stub(target).items() if rel not in files})
    base = tmp_path_factory.mktemp("sel2")
    p = support.Planted(base / "project", base / "told", extra=files)
    from gov.close import select as scoped_module

    previous = {k: os.environ.get(k) for k in ("GIT_CONFIG_GLOBAL", "GOV_ROLE")}
    os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
    os.environ.pop("GOV_ROLE", None)
    try:
        yield p, scoped_module
    finally:
        for k, v in previous.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _selected(suites, target):
    folder = target.rstrip("/")
    return any(s.rstrip("/") == folder or s.startswith(folder + "/") for s in suites)


@pytest.mark.parametrize("path,suite", EDGES, ids=[f"{p}->{s}" for p, s in EDGES])
def test_sel2_a_change_to_the_path_selects_the_suite_the_live_map_couples_to_it(live, path, suite):
    p, scoped_module = live
    try:
        chosen = scoped_module.scoped(p.root, A.id, change=[path])
    except scoped_module.SelectionRefused as refusal:
        assert not refusal.reason.startswith("the head does not hold"), f"fixture: {refusal.reason}"
        pytest.fail(f"the live map places {path} nowhere ({refusal.reason})")
    assert _selected(chosen["suites"], suite), f"a change to {path} does not select {suite}: {chosen['suites']}"


# -- SEL-3: coverage named ---------------------------------------------------------------------------------------------

UNMAPPED = "src/app/unmapped_script.sh"
NOTE = "docs/x/note.md"


def test_sel3_a_branch_adding_an_unmapped_script_is_refused_naming_it_and_the_line_to_add(planted):
    p = plant(planted, branch_files={**sel.WIDGET, UNMAPPED: "#!/bin/sh\necho unmapped\n"})
    run = select(p)
    refused(run, UNMAPPED)
    said = run["stderr"].lower()
    assert support.TEST_MAP_REL in run["stderr"], f"the refusal does not name the map to edit\n{support.describe(run)}"
    assert "coupling" in said, f"the refusal does not name the line to add (a coupling)\n{support.describe(run)}"


def test_sel3_every_unplaced_path_is_named(planted):
    other = "tools/second_unmapped.sh"
    p = plant(planted, branch_files={**sel.WIDGET, UNMAPPED: "#!/bin/sh\n", other: "#!/bin/sh\n"})
    run = select(p)
    refused(run, UNMAPPED, other)
    assert support.TEST_MAP_REL in run["stderr"], support.describe(run)


def test_sel3_the_landing_is_refused_with_the_same_line_and_moves_nothing(planted):
    p = plant(planted, branch_files={**sel.WIDGET, UNMAPPED: "#!/bin/sh\necho unmapped\n"})
    before = p.state()
    run = support.run_queue(p, f"{A.id}=topic/aa")
    assert run["code"] != 0, support.describe(run)
    assert "SELECTION_REFUSED" in run["stderr"] and UNMAPPED in run["stderr"], support.describe(run)
    assert support.TEST_MAP_REL in run["stderr"] and "coupling" in run["stderr"].lower(), support.describe(run)
    assert p.state() == before, "a refused landing moved something"


def test_sel3_a_selection_that_places_every_path_holds_unplaced_as_an_empty_list(planted):
    p = plant(planted)
    chosen = chosen_object(select(p))
    assert "unplaced" in chosen, f"the object has no `unplaced` key: {sorted(chosen)}"
    assert chosen["unplaced"] == [], f"unplaced: {chosen['unplaced']!r}"


def test_sel3_a_record_only_document_passes_with_its_notice(planted):
    p = plant(planted, branch_files={**sel.WIDGET, NOTE: "# a note\n"})
    chosen = chosen_object(select(p))
    assert f"RECORD_PLACED {NOTE}" in (chosen.get("notices") or []), f"notices: {chosen.get('notices')!r}"
    assert chosen.get("records") == [NOTE], f"records: {chosen.get('records')!r}"
    assert chosen.get("unplaced") == [], f"unplaced: {chosen.get('unplaced')!r}"

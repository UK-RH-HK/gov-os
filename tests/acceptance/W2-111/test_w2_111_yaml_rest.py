"""W2-111 failure-4 and success-9: P-W2-111-YAML-REST (a) as a described behaviour (DEC-136; brief td-8). The guard's
other reads of YAML, the path map's ``role_paths:`` block and the session ticket's front matter, answer as the
pure-Python ``yaml.SafeLoader`` does: where it refuses the text (a tab inside or after a plain value or after ``key:``,
a ``? `` inside a flow item, a byte order mark after a line break), the role-checked call decided from it is refused
(fail closed); where it reads it, the decision is the pure loader's. One case per read: ``gov.util.role_paths``' block
read and its front-matter read (the role filter, ``role_paths.caller``), ``gov.util.parts``' front-matter read (the
product's hook) and the live hook's ``role_reads.py`` at both reads (the patched copy). Support:
``w2_111_yaml_rest.py``.
"""

from __future__ import annotations

import json

import pytest

import w2_111_live_hook as live
import w2_111_yaml_rest as rest

CLASSES = set(rest.CLASSES)


def _texts():
    out = []
    for t in rest.BLOCK_IDS:
        out.append(pytest.param("block", t, id=f"block-{t}"))
    for t in rest.FRONT_IDS:
        out.append(pytest.param("front", t, id=f"front-{t}"))
        out.append(pytest.param("front-quoted-wbs", t, id=f"front-quoted-wbs-{t}"))
    return out


def _source(placement, text_id):
    if placement == "block":
        return rest.BLOCKS[text_id]
    return rest.front_head(text_id, quoted_wbs=placement == "front-quoted-wbs")


# -- the fixture is sound: the pure loader refuses each class text and reads the clean one ---------------------------

@pytest.mark.parametrize("placement, text_id", _texts())
def test_yaml_rest_pure_safe_loader_refuses_each_class_text_and_reads_the_clean_one(placement, text_id):
    source = _source(placement, text_id)
    got = rest.pure_answer(source)
    lenient = rest.libyaml_answer(source)
    if text_id in CLASSES:
        assert got[0] == "refused", (
            f"{placement} {text_id}: the pure SafeLoader read the text (the fixture is not sound): {got!r}")
    else:
        assert got[0] == "data" and isinstance(got[1], dict), (
            f"{placement} {text_id}: the pure SafeLoader did not read the clean text: {got!r}")
        if placement == "block":
            assert set(got[1]["role_paths"]) == {rest.ENG, rest.TD}, got
        else:
            assert got[1]["wbs_id"] == rest.WBS and got[1]["allowed_paths"] == ["src/app/**", "docs/app/**"], got
    # for information: what libyaml's CSafeLoader makes of it (None: libyaml is not installed here)
    print(f"{placement} {text_id}: pure {got[0]}; libyaml {lenient[0] if lenient else 'not installed'}")


# -- the product: gov.util.role_paths' block read (the role filter) ---------------------------------------------------

def _assert_as_oracle(what, text_id, got, oracle):
    if text_id in CLASSES:
        assert oracle[0] == "refused", (
            f"{what} {text_id}: the oracle (the same code, libyaml absent) did not refuse: {oracle!r} (the harness is "
            "not sound)")
        if got[0] != "refused":
            pytest.fail(f"{what} {text_id}: decided from a text the pure SafeLoader refuses: it answered {got!r}; "
                        f"with the pure loader the call is refused: {oracle!r}", pytrace=False)
    assert got == oracle, f"{what} {text_id}: answered {got!r}; with the pure loader (libyaml absent) {oracle!r}"


@pytest.mark.parametrize("text_id", rest.BLOCK_IDS)
def test_yaml_rest_role_paths_block_is_read_by_the_role_filter_as_the_pure_loader_reads_it(text_id, tmp_path):
    """An engineer's search on the planted repository: ``role_paths.caller`` refuses (``RolePathsError``) where the
    pure loader refuses the block, as it does today for a block the pure loader cannot read."""
    repo = rest.plant_repo(tmp_path / "repo", rest.BLOCKS[text_id], rest.front_head(rest.CLEAN))
    home = tmp_path / "home"
    home.mkdir()
    probes = [rest.ORDINARY_REL, rest.TESTS_REL]
    got = rest.caller_answer(repo, rest.ENG, home, tmp_path / "run", probes)
    oracle = rest.caller_answer(repo, rest.ENG, home, tmp_path / "run-pure", probes, pure=True)
    if text_id == rest.CLEAN:
        assert oracle == ("filter", {rest.ORDINARY_REL: False, rest.TESTS_REL: True}), (
            f"the clean block: the engineer's filter is not the expected one: {oracle!r}")
    _assert_as_oracle("role_paths.caller (the engineer, the path map's role_paths: block)", text_id, got, oracle)


# -- the product: gov.util.role_paths' ticket front-matter read (the role filter) -------------------------------------

@pytest.mark.parametrize("text_id", rest.FRONT_IDS)
def test_yaml_rest_role_paths_ticket_front_matter_is_read_by_the_role_filter_as_the_pure_loader_reads_it(text_id,
                                                                                                          tmp_path):
    """A test designer's search of the engineer's tree (``~/gov-os-worktrees/<WBS>``, its branch adding a file under
    the ticket's allowed_paths): where the pure loader refuses the ticket's front matter the search is refused
    (``RolePathsError``), never handed the engineer's new code; the clean front matter withholds that file."""
    home = tmp_path / "home"
    tree = rest.plant_engineer_tree(home, rest.BLOCKS[rest.CLEAN], rest.front_head(text_id))
    probes = [rest.ORDINARY_REL, rest.IMPL_REL]
    got = rest.caller_answer(tree, rest.TD, home, tmp_path / "run", probes)
    oracle = rest.caller_answer(tree, rest.TD, home, tmp_path / "run-pure", probes, pure=True)
    if text_id == rest.CLEAN:
        assert oracle == ("filter", {rest.ORDINARY_REL: False, rest.IMPL_REL: True}), (
            f"the clean front matter: the test designer's filter is not the expected one: {oracle!r}")
        assert got == oracle, f"clean: answered {got!r}; with the pure loader {oracle!r}"
        return
    if got[0] != "refused":
        pytest.fail(f"role_paths.caller (the test designer, the ticket's front matter) {text_id}: decided from front "
                    f"matter the pure SafeLoader refuses: it answered {got!r} (the engineer's new code "
                    f"{rest.IMPL_REL} {'withheld' if got[0] == 'filter' and got[1].get(rest.IMPL_REL) else 'handed'}"
                    f"); the call must be refused (fail closed). With libyaml absent the code answers {oracle!r}",
                    pytrace=False)
    assert got == oracle, f"{text_id}: answered {got!r}; with the pure loader (libyaml absent) {oracle!r}"


# -- the product's hook: gov.util.parts' ticket front-matter read -----------------------------------------------------

def _decided(result):
    """(decision, reason) of one product-hook call."""
    reason = None
    try:
        specific = json.loads(result.stdout.strip() or "{}").get("hookSpecificOutput") or {}
        reason = specific.get("permissionDecisionReason")
    except (ValueError, AttributeError):
        reason = result.stderr.strip()[-200:] or None
    return result.decision, reason


@pytest.mark.parametrize("text_id", rest.FRONT_IDS)
def test_yaml_rest_product_hook_reads_the_ticket_front_matter_as_the_pure_loader_reads_it(text_id, tmp_path):
    """W1-02's project with the session ticket's front matter holding the text (its WBS id quoted, so the guard's line
    reader cannot stand in): an engineer's Read and a test designer's Read of an ordinary file are decided, with the
    same reason, as the same hook decides them with libyaml absent: refused where the pure loader refuses."""
    project = rest.product_project(tmp_path, rest.front_head(text_id, quoted_wbs=True))
    sandbox = rest.guard.make_sandbox(tmp_path / "sandbox")
    for role in (rest.ENG, rest.TD):
        got = _decided(rest.product_read(project, sandbox, role, rest.ORDINARY_REL))
        with rest.pure_hook(project):
            oracle = _decided(rest.product_read(project, sandbox, role, rest.ORDINARY_REL))
        what = f"the product hook, the {role}'s Read of {rest.ORDINARY_REL} (the ticket's front matter)"
        if text_id in CLASSES:
            assert oracle[0] == "deny", f"{what} {text_id}: the oracle did not refuse: {oracle!r} (not sound)"
            if got[0] != "deny":
                pytest.fail(f"{what} {text_id}: decided {got!r} from front matter the pure SafeLoader refuses; with "
                            f"the pure loader the call is refused: {oracle!r}", pytrace=False)
        else:
            assert oracle[0] == "allow", f"{what}: the clean front matter was not allowed: {oracle!r}"
        assert got == oracle, f"{what} {text_id}: decided {got!r}; with the pure loader (libyaml absent) {oracle!r}"


# -- the live hook's patched copy: role_reads.py at both reads --------------------------------------------------------

@pytest.fixture(scope="module")
def live_rest(tmp_path_factory):
    try:
        copies, interpreter = rest.make_live(tmp_path_factory.mktemp("w2-111-yaml-rest-live"))
    except live.LiveHookUnavailable as exc:
        return {"error": str(exc)}
    return {"copies": copies, "interpreter": interpreter}


def _live_calls(world):
    return {"the engineer's Read of an ordinary file": (rest.ENG, world.project / rest.ORDINARY_REL),
            "the engineer's Read of its ticket's acceptance test": (rest.ENG, world.project / rest.TESTS_REL),
            "the test designer's Read of an ordinary file": (rest.TD, world.project / rest.ORDINARY_REL),
            "the test designer's Read of the engineer's code": (rest.TD, world.impl)}


CLEAN_EXPECTED = {"the engineer's Read of an ordinary file": "allow",
                  "the engineer's Read of its ticket's acceptance test": "deny",
                  "the test designer's Read of an ordinary file": "allow",
                  "the test designer's Read of the engineer's code": "deny"}


def _live_case(live_rest, tmp_path, block, head, text_id, reading):
    """The class texts: each call in ``reading`` (those that read the text) refused by the patched copy. The clean
    control: every call decided alike by both copies, as the role rule has it."""
    if "error" in live_rest:
        pytest.fail(live_rest["error"], pytrace=False)
    copies, interpreter = live_rest["copies"], live_rest["interpreter"]
    world = rest.live_world(tmp_path / "world", block, head)
    for what, (role, target) in _live_calls(world).items():
        after = rest.run_live(interpreter, copies.after, world.project, world.home, tmp_path / "after", role, target)
        if text_id == rest.CLEAN:
            before = rest.run_live(interpreter, copies.before, world.project, world.home, tmp_path / "before", role,
                                   target)
            assert (before[0], after[0]) == (CLEAN_EXPECTED[what],) * 2, (
                f"clean control: {what} decided {after[0]} by the patched copy and {before[0]} by the applied copy, "
                f"expected {CLEAN_EXPECTED[what]}: after {after[1]!r}; before {before[1]!r}")
        elif what in reading:
            assert after[0] == "deny", (
                f"{text_id}: {what} was decided {after[0]} by the patched copy from a text the pure SafeLoader "
                f"refuses; it must be refused (fail closed): {after[1]!r}")


@pytest.mark.parametrize("text_id", rest.BLOCK_IDS)
def test_yaml_rest_live_hook_patched_copy_refuses_calls_on_a_role_paths_block_the_pure_loader_refuses(live_rest,
                                                                                                      text_id,
                                                                                                      tmp_path):
    _live_case(live_rest, tmp_path, rest.BLOCKS[text_id], rest.front_head(rest.CLEAN), text_id,
               reading=set(CLEAN_EXPECTED))


@pytest.mark.parametrize("text_id", rest.FRONT_IDS)
def test_yaml_rest_live_hook_patched_copy_refuses_calls_on_ticket_front_matter_the_pure_loader_refuses(live_rest,
                                                                                                       text_id,
                                                                                                       tmp_path):
    _live_case(live_rest, tmp_path, rest.BLOCKS[rest.CLEAN], rest.front_head(text_id), text_id,
               reading={"the test designer's Read of an ordinary file",
                        "the test designer's Read of the engineer's code"})

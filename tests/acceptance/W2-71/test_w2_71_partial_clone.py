"""Run 2 (DEC-911 item 4, KPI 4 "the matches are held in memory only"; the orchestrator's decision P1-MORNING-2026-10-29
item 4): in a partial clone, a match of row W2-L423's rule gets no exemption and git is asked about no object, so no
candidate (which may be a real token) is sent to the promisor remote by a lazy fetch.

The project is a real partial clone, built at test time: a bare source repository built from scratch that serves
filters (``uploadpack.allowFilter``, ``uploadpack.allowAnySHA1InWant``), cloned with ``git clone --filter=blob:none
file://<source>``. After the clone, the source gains a commit the clone does not have. The project quotes, after each
keyword, in a log under ``.gov-runtime/`` (the check) and a page under ``docs/`` (the filter):

- ``own-commit``: a commit of the clone's own history (present in its object store);
- ``random``: 40 hex digits drawn from a hash, naming no object anywhere;
- ``source-only``: the commit only the source has.

Every request the remote serves goes through a logging ``uploadpack`` program (``remote.origin.uploadpack``): the
count of what left the clone. A control, after the runs, has the test itself look up an old blob the filter left out
with a plain ``git cat-file``: the counter sees that lazy fetch and the blob lands in the clone, so a zero count during
the runs means something. A recording ``git`` first on ``PATH`` shows which git calls the check and the filter made.

Red on run 1's code: it exempts the own commit, fetches while it verifies the random and the source-only ids, then
exempts the fetched commit (README, run 2).
"""

from __future__ import annotations

import os

import pytest

import w2_71_support as support

pytestmark = [support.needs_gitleaks, support.needs_git, pytest.mark.local_only]

KEYWORD_CASES = {"vendor-keyword": support.VENDOR, "prefix-keyword": support.PREFIX}
KINDS = ["own-commit", "random", "source-only"]


class Scene:
    """One partial clone, its runtime folder and indexable folder quoting the three kinds of id after each keyword;
    the check and the filter run once each, through a recording git, with the remote's requests counted."""

    def __init__(self, sandbox):
        self.sandbox = sandbox
        self.clone = support.make_clone(sandbox, "partial-clone", label="partial", partial=True)
        root = self.clone.root
        self.later = support.push_source_only_commit(self.clone, label="partial")
        self.random = support.hex_of("run-2-partial-clone-random")
        self.old_blob = support.git(self.clone.seed.root, "rev-parse", f"{self.clone.seed.first}:src/notes.txt").strip()
        self.values = {"own-commit": self.clone.head, "random": self.random, "source-only": self.later}
        self.check_rels, self.filter_rels = {}, {}
        for kind, value in self.values.items():
            for name, keyword in KEYWORD_CASES.items():
                line = support.vendor_line(keyword, value)
                self.check_rels[(kind, name)] = f".gov-runtime/scratch/{kind}-{name}.log"
                support.write(root / self.check_rels[(kind, name)], "a lead's review log\n" + line)
                self.filter_rels[(kind, name)] = f"docs/{kind}-{name}.md"
                support.write(root / self.filter_rels[(kind, name)], "# A review\n\n" + line)
        self.env = support.base_environment(sandbox)
        self.config_code, self.config = support.config_list(root, self.env)
        self.objects_before = support.local_objects(root)
        check_git, self.check_calls_log = support.recording_git(sandbox, "partial-recording-git-check")
        filter_git, self.filter_calls_log = support.recording_git(sandbox, "partial-recording-git-filter")
        before = self.clone.request_count()
        self.check = support.run_check(sandbox, root, env=support.base_environment(
            sandbox, path=f"{check_git}{os.pathsep}{self.env['PATH']}"))
        after_check = self.clone.request_count()
        self.filter = support.run_filter(sandbox, root, sorted(self.filter_rels.values()), env=support.base_environment(
            sandbox, path=f"{filter_git}{os.pathsep}{self.env['PATH']}"))
        after_filter = self.clone.request_count()
        self.check_requests, self.filter_requests = after_check - before, after_filter - after_check
        self.objects_after = support.local_objects(root)
        # the control: the test's own plain lookup of an old blob the filter left out (no run asks about it)
        self.control_code = support.lookup_by_the_test(root, self.old_blob, self.env, kind=None)
        self.control_requests = self.clone.request_count() - after_filter
        self.objects_after_control = support.local_objects(root)


@pytest.fixture(scope="module")
def scene(module_sandbox):
    return Scene(module_sandbox)


PLACES = [(kind, name) for kind in KINDS for name in KEYWORD_CASES]
IDS = [f"{kind}-{name}" for kind, name in PLACES]


# ---- premises ----------------------------------------------------------------------------------------------------

def test_premise_the_clone_is_a_partial_clone_of_the_source(scene):
    config = set(scene.config)
    flags = {"promisor": "remote.origin.promisor=true" in config,      # git 2.43 sets these two, not the extension
             "filter": "remote.origin.partialclonefilter=blob:none" in config,
             "an old blob is missing": scene.old_blob not in scene.objects_before,
             "the own commit is present": scene.clone.head in scene.objects_before,
             "the source-only commit is missing": scene.later not in scene.objects_before,
             "the random id names nothing": scene.random not in scene.objects_before}
    assert scene.config_code == 0 and all(flags.values()), f"the clone is not partial as the cases need: {flags}"


def test_premise_the_source_holds_the_source_only_commit_and_not_the_random_id(scene):
    held = (support.is_object(scene.clone.source, scene.later, "commit"),
            support.is_object(scene.clone.source, scene.random, None))
    assert held == (True, False), f"the source holds (the source-only commit, the random id): {held}"


@pytest.mark.parametrize("place", PLACES, ids=IDS)
def test_premise_the_line_is_a_finding_of_row_w2_l423s_rule_and_of_no_other(scene, place):
    kind, name = place
    line = support.vendor_line(KEYWORD_CASES[name], scene.values[kind])
    toml = support.gitleaks_toml()
    extended = support.gitleaks_finds(line, toml)
    alone = support.gitleaks_finds(line, support.project_rules_alone(toml))
    ok = extended == [support.RULE_ID] and alone == []
    assert ok, support.say(f"{kind}, {name}: the rule sets find {extended} and {alone}, not row W2-L423's rule alone")


def test_premise_the_counter_sees_a_lazy_fetch_in_the_clone(scene):
    fetched = scene.old_blob in scene.objects_after_control
    ok = scene.control_code == 0 and scene.control_requests >= 1 and fetched
    assert ok, (f"the test's own lookup of an old blob the filter left out: exit code {scene.control_code}, "
                f"{scene.control_requests} requests counted, the blob fetched: {fetched}")


# ---- the check: no exemption in a partial clone --------------------------------------------------------------------

@pytest.mark.parametrize("place", PLACES, ids=IDS)
def test_in_a_partial_clone_the_match_stays_a_finding_of_the_check(scene, place):
    rel = scene.check_rels[place]
    assert scene.check.ended, f"the check did not end within its declared limit\n{scene.check.describe()}"
    found = support.finds(scene.check, rel)
    assert found, (f"in a partial clone the check passes {rel} ({place[0]} after the rule's keyword) as clean\n"
                   f"{scene.check.describe()}")


@pytest.mark.parametrize("place", PLACES, ids=IDS)
def test_in_a_partial_clone_the_match_is_left_out_by_the_filter(scene, place):
    rel = scene.filter_rels[place]
    assert scene.filter.ended, f"the filter did not end within its declared limit\n{scene.filter.describe()}"
    passes = scene.filter.passes(rel)
    assert not passes, (f"in a partial clone the filter lets {rel} ({place[0]} after the rule's keyword) through\n"
                        f"{scene.filter.describe()}")


# ---- nothing leaves the clone --------------------------------------------------------------------------------------

def test_in_a_partial_clone_the_check_sends_nothing_to_the_remote(scene):
    assert scene.check.ended, f"the check did not end\n{scene.check.describe()}"
    assert scene.check_requests == 0, (f"in a partial clone the check's run reached the promisor remote "
                                       f"{scene.check_requests} times (a lazy fetch sends the candidate off the "
                                       "machine)")


def test_in_a_partial_clone_the_filter_sends_nothing_to_the_remote(scene):
    assert scene.filter.ended, f"the filter did not end\n{scene.filter.describe()}"
    assert scene.filter_requests == 0, (f"in a partial clone the filter's run reached the promisor remote "
                                        f"{scene.filter_requests} times")


def test_the_commit_only_the_remote_has_is_not_fetched_into_the_clone(scene):
    fetched = scene.later in scene.objects_after
    added = len(scene.objects_after - scene.objects_before)
    assert not fetched and added == 0, (f"after the check and the filter, the source-only commit is in the clone's "
                                        f"object store: {fetched}; objects added by the runs: {added}")


def test_in_a_partial_clone_the_check_asks_git_about_no_object(scene):
    lookups = support.lookups_named(support.read_git_calls(scene.check_calls_log))
    assert not lookups, f"in a partial clone the check asked git about objects, {len(lookups)} calls: {lookups}"


def test_in_a_partial_clone_the_filter_asks_git_about_no_object(scene):
    lookups = support.lookups_named(support.read_git_calls(scene.filter_calls_log))
    assert not lookups, f"in a partial clone the filter asked git about objects, {len(lookups)} calls: {lookups}"

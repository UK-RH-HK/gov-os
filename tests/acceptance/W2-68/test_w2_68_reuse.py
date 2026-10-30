"""Same code, no repeat regression (DEC-883 item 3, DEC-889 item 2, I4 F2), and the path map counted as code
(DEC-880, DEC-899).

Every case: ticket C's work is committed, then a batch closes ticket A alone (a fully passing run with its JUnit
XML, on head H). After it, ticket C's checkpoint is committed (a record-only commit) and ``gov close PROJ-cccc``
runs.

- With nothing else between them, C's code fingerprint (record-only paths left out, the test map's
  ``record_only`` list read) equals the batch's: C's close reuses the batch's run, cites it, runs its own
  acceptance suite and the record-reading set and nothing else of the regression, and states the reused run's
  skip (W2-zz holds one planted skip).
- With a code commit, a change of the path map (listed as record-only in that case's test map), the batch's JUnit
  XML gone, or no test map to read the record-only list from, C's close runs fresh and does not cite the batch.

Red reason (README): ``gov.close.batch`` does not exist (``No module named gov.close.batch``: no envelope).
"""

import json

import pytest

import w2_68_support as support

scoped = support.scoped


class Reuse:
    """The batch of A, then C's checkpoint, then C's close; ``plant`` runs between the batch and the checkpoint."""

    def __init__(self, base, plant=None, test_map=support.TEST_MAP):
        self.sandbox = support.make_sandbox(base)
        self.env = support.env_without_endpoint(self.sandbox)
        self.project = support.Project(base / "project", base / "told", test_map=test_map, plant_skip=True)
        project = self.project
        project.work({support.GADGET: "# the gadget, changed\n"}, ticket=support.C)
        project.work({support.WIDGET: "# the widget, changed\n"}, ticket=support.A)
        project.ready(self.sandbox, ticket=support.A)
        self.head = project.head()
        self.answer = support.batch(project, self.env, support.A)
        self.close = None
        if self.answer.data is None:
            return  # nothing to build on: each case fails on the batch's answer
        project.commit_left()
        self.planted = plant(self) if plant else None
        project.ready(self.sandbox, ticket=support.C)
        self.before = project.runs()
        self.close = project.close(self.sandbox, ticket=support.C, env=self.env)

    def batch_passed(self):
        self.answer.ok()
        assert self.close is not None

    def evidence(self):
        return scoped_evidence(self.close)


def scoped_evidence(run):
    evidence = support.evidence_of_any(run)
    assert evidence is not None, f"C's close states no evidence block\n{run.describe()}"
    return evidence


@pytest.fixture(scope="module")
def same_code(tmp_path_factory):
    return Reuse(tmp_path_factory.mktemp("w2_68_same_code"))


# --------------------------------------------------------------------------
# Same code: the batch's run reused
# --------------------------------------------------------------------------

def test_a_close_on_the_same_code_after_a_record_only_commit_reuses_the_passing_run(same_code):
    same_code.batch_passed()
    scoped.passed(same_code.close)
    evidence = same_code.evidence()
    scope, block = support.cited_run(evidence)
    assert scope == support.REUSED, f"C's close on the batch's code states scope {scope!r}, not reused"
    assert block is not None, f"C's evidence has no {support.REUSED_KEY!r} block: {sorted(evidence)}"
    fingerprint = evidence.get(support.CODE_FINGERPRINT)
    assert isinstance(fingerprint, str) and fingerprint and fingerprint in json.dumps(block), \
        f"C cites a run of another code fingerprint than its own ({fingerprint!r}): {json.dumps(block)[:1500]}"
    assert support.names_commit(block, same_code.head), \
        f"C does not cite the batch's run on {same_code.head}: {json.dumps(block)[:1500]}"
    named = support.xml_files(same_code.project, block)
    assert named and all(path.is_file() for _, path in named), \
        f"C's reused block names no JUnit XML of the reused run that exists: {json.dumps(block)[:1500]}"
    _, record, text = support.the_batch_record(same_code.project)
    assert fingerprint in text, "the reused run's record states another code fingerprint than C's"
    assert support.close_evidence(same_code.project, support.C).get("scope") == support.REUSED, \
        "C's close record does not state the scope its answer states"


def test_a_reused_close_runs_its_own_suite_and_the_record_reading_set_and_nothing_else(same_code):
    same_code.batch_passed()
    scoped.passed(same_code.close)
    since = same_code.project.runs_since(same_code.before)
    expected = {support.CASE(support.C_WBS): 1, support.RR_CASE: 1}
    assert since == expected, (f"after a record-only commit on the same code, C's close ran {since}; its own "
                               f"acceptance suite and the record-reading set alone are expected: {expected}")


def test_reused_evidence_states_the_reused_run_s_skip_count_and_its_skip(same_code):
    same_code.batch_passed()
    evidence = same_code.evidence()
    _, block = support.cited_run(evidence)
    assert block is not None, f"C's evidence has no {support.REUSED_KEY!r} block: {sorted(evidence)}"
    counts = list(support.values_of(block, lambda key: "skip" in key and "count" in key))
    assert 1 in counts, (f"the reused block does not state the reused run's skip count (1, the planted skip): "
                         f"{json.dumps(block)[:1500]}")
    stated = json.dumps(block)
    assert support.SKIP_CASE in stated and support.SKIP_REASON in stated, \
        f"the reused block does not name the reused run's skip and its reason: {stated[:1500]}"


# --------------------------------------------------------------------------
# Different code, or a run that cannot be reused: a fresh run, and no citation
# --------------------------------------------------------------------------

def _code_commit(reuse):
    return reuse.project.work({support.GADGET: "# the gadget, changed again\n"}, ticket=support.C)


def _path_map(reuse):
    return reuse.project.path_map_commit()


def _junit_gone(reuse):
    """The batch's JUnit XML files removed (and the removal committed where they were tracked)."""
    rel, record, _ = support.the_batch_record(reuse.project)
    named = support.xml_files(reuse.project, record)
    assert named and all(path.is_file() for _, path in named), \
        f"the batch's run record {rel} names no JUnit XML file that exists: {[n for n, _ in named]}"
    for _, path in named:
        path.unlink()
    return reuse.project.commit_left()


PATH_MAP_RECORD_ONLY = {**support.TEST_MAP,
                        "record_only": [*support.TEST_MAP["record_only"], support.PATH_MAP_REL]}

FRESH = {
    "code-commit": (_code_commit, support.TEST_MAP),
    "path-map-change": (_path_map, PATH_MAP_RECORD_ONLY),
    "junit-xml-gone": (_junit_gone, support.TEST_MAP),
    "no-record-only-list": (None, None),
}


@pytest.mark.parametrize("planted", list(FRESH))
def test_a_close_that_cannot_reuse_the_run_runs_fresh_and_does_not_cite_it(planted, tmp_path):
    plant, test_map = FRESH[planted]
    reuse = Reuse(tmp_path, plant=plant, test_map=test_map)

    reuse.batch_passed()
    support.assert_does_not_cite(reuse.close, reuse.head, f"C's close after {planted}")
    since = reuse.project.runs_since(reuse.before)
    assert since.get(support.UNIT_CASE), (f"C's close after {planted} did not run fresh: tests/unit did not run "
                                          f"(it ran {since})\n{reuse.close.describe()}")


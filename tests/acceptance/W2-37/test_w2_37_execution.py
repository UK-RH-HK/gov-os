"""KPI 2: after apply or archive, the CIT-E record matches the proposal or lists the differences [CAP-33's
acceptance line; the ticket cites W2-L319, see package P-2].

Reading R6: ``gov impact --compare <CIT-E path>`` reads the change-execution record, finds the change-impact
proposal its ``proposal`` names (by id, through the record store), and compares the five lists of ``affected``
that each carries in its frontmatter. The result holds ``proposal`` and ``execution`` (the two ids), ``matches``
(true or false) and ``differences``: one entry per item, with its ``id`` and ``only_in`` (``proposal``: proposed and
not done; ``execution``: done and not proposed).
"""

from __future__ import annotations

import copy

import pytest

import w2_37_support as support

CITE_REL = f"docs/changes/{support.CITE}.md"
CITP_REL = f"docs/changes/{support.CITP}.md"


def records(project, box, execution=None, proposal=None):
    """Write the CIT-P and the CIT-E, commit them, and load the store again."""
    project.write(CITP_REL, proposal if proposal is not None else support.proposal_file())
    project.write(CITE_REL, execution if execution is not None else support.execution_file())
    project.commit("the change's records")
    support.load_store(project.root, box)


def compared(project, box, rel=CITE_REL):
    run = support.compare(project.root, rel, box)
    found = support.result(run)
    show = run.describe()
    assert isinstance(found.get("matches"), bool), f"`matches` is not true or false\n{show}"
    assert isinstance(found.get("differences"), list), f"`differences` is not a list\n{show}"
    for entry in found["differences"]:
        assert isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry.get("only_in") in support.ONLY_IN, \
            f"a difference is not a map with an `id` and an `only_in` of {support.ONLY_IN}: {entry!r}\n{show}"
    return found


def differences(found):
    return sorted((entry["id"], entry["only_in"]) for entry in found["differences"])


def done(**change):
    """The proposal's lists with ``change``: ``kind=(removed, added)``."""
    affected = copy.deepcopy(support.PROPOSED)
    for kind, (removed, added) in change.items():
        affected[kind] = [item for item in affected[kind] if item not in removed] + list(added)
    return affected


def test_an_execution_record_that_agrees_with_its_proposal_is_reported_as_matching(project, box):
    records(project, box)
    found = compared(project, box)
    assert found["matches"] is True and found["differences"] == [], f"agreeing records: {found}"
    assert found.get("proposal") == support.CITP and found.get("execution") == support.CITE, \
        f"the result does not name the two records: {found.get('proposal')!r}, {found.get('execution')!r}"


def test_the_order_of_the_lists_does_not_matter(project, box):
    reordered = {kind: list(reversed(ids)) for kind, ids in support.PROPOSED.items()}
    reordered["specifications"] = [support.CAP, support.SPEC]
    records(project, box, execution=support.execution_file(affected=reordered))
    assert compared(project, box)["matches"] is True


def test_an_item_proposed_and_not_done_is_a_listed_difference(project, box):
    records(project, box, execution=support.execution_file(affected=done(decisions=([support.OTHER_DECISION], []))))
    found = compared(project, box)
    assert found["matches"] is False, "a CIT-E that leaves out a proposed item is reported as matching"
    assert differences(found) == [(support.OTHER_DECISION, "proposal")], f"differences: {found['differences']}"


def test_an_item_done_and_not_proposed_is_a_listed_difference(project, box):
    records(project, box, execution=support.execution_file(affected=done(specifications=([], ["SPEC-099"]))))
    found = compared(project, box)
    assert found["matches"] is False, "a CIT-E that adds an item is reported as matching"
    assert differences(found) == [("SPEC-099", "execution")], f"differences: {found['differences']}"


def test_every_difference_is_listed(project, box):
    affected = done(decisions=([support.OTHER_DECISION], []), tickets=([], ["PROJ-zz99"]),
                    code=([support.SYMBOL], [support.ENTRY]))
    records(project, box, execution=support.execution_file(affected=affected))
    found = compared(project, box)
    assert found["matches"] is False
    assert differences(found) == sorted([(support.OTHER_DECISION, "proposal"), ("PROJ-zz99", "execution"),
                                         (support.SYMBOL, "proposal"), (support.ENTRY, "execution")]), \
        f"differences: {found['differences']}"


def test_an_execution_record_that_lists_nothing_never_matches(project, box):
    records(project, box, execution=support.execution_file(affected=False))
    run = support.compare(project.root, CITE_REL, box)
    document = support.envelope(run)
    if document["ok"] is True:
        assert document["result"].get("matches") is not True, f"a CIT-E with no lists matches\n{run.describe()}"
    else:
        support.assert_refused(run)


@pytest.mark.parametrize("proposal,named", [(None, "proposal"), ("CITP-404", "CITP-404"),
                                            (support.CHANGED, support.CHANGED)],
                         ids=["no-proposal-key", "unknown-proposal", "proposal-is-no-cit-p"])
def test_an_execution_record_without_its_proposal_is_refused(project, box, proposal, named):
    records(project, box, execution=support.execution_file(proposal=proposal))
    support.assert_refused(support.compare(project.root, CITE_REL, box), named)


def test_a_record_that_is_no_execution_record_is_refused(project, box):
    records(project, box)
    support.assert_refused(support.compare(project.root, CITP_REL, box), support.CITP)


def test_a_missing_execution_record_is_refused(project, box):
    records(project, box)
    support.assert_refused(support.compare(project.root, "docs/changes/CITE-404.md", box), "CITE-404")


def test_comparing_writes_nothing(project, box):
    records(project, box, execution=support.execution_file(affected=done(tickets=([], ["PROJ-zz99"]))))
    before = support.snapshot(project.root)
    support.compare(project.root, CITE_REL, box)
    after = support.snapshot(project.root)
    changed = sorted(k for k in set(before[0]) | set(after[0]) if before[0].get(k) != after[0].get(k))
    assert not changed and before[1] == after[1], f"gov impact --compare changed {changed or 'git'}"


def test_the_proposal_gov_impact_writes_is_what_the_execution_record_is_checked_against(project, box):
    """KPI 1 then KPI 2: the CIT-P ``--out`` writes, and a CIT-E that records just what it lists, match."""
    out = project.root / "docs" / "changes" / "CITP-900.md"
    support.assessment(support.impact(project.root, support.CHANGED, box, out=out))
    front, _ = support.read_frontmatter(out)
    project.write(CITE_REL, support.execution_file(proposal=front["id"], affected=front["affected"]))
    project.commit("the written proposal and its execution record")
    support.load_store(project.root, box)
    found = compared(project, box)
    assert found["matches"] is True and found.get("proposal") == front["id"], f"{found}"

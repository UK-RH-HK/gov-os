"""S3: the lite checks. A committed AS record that leaves out a spec or a top-level code module the inventory holds, or
holds a gap with no (or an empty) question, is refused when ``gov adopt`` reads it (A3 runs on it). The refusal's code is
not stated (it is an ``ADOPT_`` code that is none of the stage chain's and A3's existing ones); it names the spec, the
module or the gap's subject; no A3 record is written. Each case builds its record by running AS, editing the front
matter, committing it with a plain git commit, and running A3 with the all-KEEP proposal."""

from __future__ import annotations

import pytest

import w2_192_support as support

base = support.base
ALPHA, OMEGA, GAMMA_PY = support.ALPHA, support.OMEGA, support.GAMMA_PY


def refused_by_the_lite_checks(done, named):
    error = base.refusal(done)
    code = str(error.get("code", ""))
    assert code.startswith("ADOPT_"), f"the refusal's code is not an ADOPT_ code: {code}"
    assert code not in support.NOT_THE_LITE_CHECKS, f"the refusal is {code}, one the chain or A3 already gives: {support.said(error)}"
    assert named in support.said(error), f"the refusal does not name {named}: {support.said(error)}"


def test_s3_a_record_that_leaves_out_a_module_is_refused_naming_it(after_as):
    def drop_module(front):
        front["modules"] = [rel for rel in front["modules"] if rel != GAMMA_PY]
        front["code_without_spec"] = [rel for rel in front["code_without_spec"] if rel != GAMMA_PY]
        front["gaps"] = [gap for gap in front["gaps"] if gap.get("subject") != GAMMA_PY]

    text = support.rewrite_record(after_as, drop_module)
    assert GAMMA_PY not in text, "planting fault: the edited record still names the module"
    before = base.head(after_as.root)
    done = support.a3_keep_all(after_as)
    refused_by_the_lite_checks(done, GAMMA_PY)
    support.assert_no_record(after_as.root, support.A3_RECORD, before, done)


def test_s3_a_record_that_leaves_out_a_spec_is_refused_naming_it(after_as):
    def drop_spec(front):
        front["specs"] = [item for item in front["specs"] if item.get("path") != ALPHA]

    text = support.rewrite_record(after_as, drop_spec)
    assert ALPHA not in text, "planting fault: the edited record still names the spec"
    before = base.head(after_as.root)
    done = support.a3_keep_all(after_as)
    refused_by_the_lite_checks(done, ALPHA)
    support.assert_no_record(after_as.root, support.A3_RECORD, before, done)


@pytest.mark.parametrize("how", ["empty-string", "key-absent"])
def test_s3_a_gap_with_no_question_is_refused_naming_its_subject(after_as, how):
    def blank_question(front):
        for gap in front["gaps"]:
            if gap.get("subject") == OMEGA:
                if how == "empty-string":
                    gap["question"] = ""
                else:
                    del gap["question"]

    support.rewrite_record(after_as, blank_question)
    before = base.head(after_as.root)
    done = support.a3_keep_all(after_as)
    refused_by_the_lite_checks(done, OMEGA)
    support.assert_no_record(after_as.root, support.A3_RECORD, before, done)


def test_s3_a_record_rewritten_without_a_defect_is_accepted(after_as):
    """The control of the three refusals above: the same edit and commit with nothing removed is accepted by A3, so the
    refusals come from the defect and not from the rewrite."""
    support.rewrite_record(after_as, lambda front: None)
    base.succeeded(support.a3_keep_all(after_as))
    assert support.front_of(after_as.root, support.A3_RECORD) is not None, "A3 recorded nothing"

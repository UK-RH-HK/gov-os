"""Tests for the retrieval skill (S1, F1).

S1: Retrieval runs facets in disposable subagents and returns only the
    validated bundle [CAP-16.b, CAP-56.a, DEC-032].
F1: Intermediate retrieval batches must not appear in the main context.
"""


class TestRetrievalSubagents:
    """S1: facets in disposable subagents, only the validated bundle returns."""

    def test_the_skill_mentions_facets(self, retrieval_skill):
        body = retrieval_skill["body"].lower()
        assert "facet" in body, \
            "the retrieval skill must mention facets"

    def test_the_skill_says_subagents_are_disposable(self, retrieval_skill):
        body = retrieval_skill["body"].lower()
        assert "subagent" in body, \
            "the retrieval skill must say facets run in subagents"
        assert "disposable" in body or "throwaway" in body, \
            "the retrieval skill must say the subagents are disposable (DEC-032)"

    def test_the_skill_cites_dec_032(self, retrieval_skill):
        assert "DEC-032" in retrieval_skill["body"], \
            "the retrieval skill must cite DEC-032 (retrieval in disposable context)"

    def test_the_skill_says_only_the_validated_bundle_returns(self, retrieval_skill):
        body = retrieval_skill["body"].lower()
        has_bundle = "bundle" in body
        has_return = "return" in body
        assert has_bundle and has_return, \
            "the retrieval skill must say only the validated/cited bundle returns"

    def test_the_skill_references_cap_16(self, retrieval_skill):
        assert "CAP-16" in retrieval_skill["body"], \
            "the retrieval skill must reference CAP-16 (parallel facet retrieval)"

    def test_the_skill_references_cap_56(self, retrieval_skill):
        assert "CAP-56" in retrieval_skill["body"], \
            "the retrieval skill must reference CAP-56 (retrieval in disposable subagent)"


class TestRetrievalFailure:
    """F1: intermediate retrieval batches must not leak to the main context."""

    def test_the_skill_addresses_the_main_context_boundary(self, retrieval_skill):
        body = retrieval_skill["body"].lower()
        names_boundary = (
            "main context" in body
            or "implementing context" in body
            or "main session" in body
            or "caller" in body
        )
        assert names_boundary, (
            "the retrieval skill must name the main/implementing context "
            "as the boundary that intermediate batches do not cross"
        )

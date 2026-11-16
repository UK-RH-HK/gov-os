"""``gov brief``: a filled brief from the ticket and the facts file, refused when the ticket is not READY (W2-152).

The role -> role-template map and the lead's run kinds (the ticket's "Interface"); the builder is ``gov.brief.build``,
and the judging-work skill a brief that judges work carries is ``gov.brief.judging``'s (W2-195).
"""

ROLE_TEMPLATES = {
    "engineer": "role-engineer",
    "independent-test-designer": "role-test-designer",
    "independent-auditor": "role-reviewer",
    "qa-engineer": "role-reviewer",  # W2-195: the QA engineer's brief, on the reviewer's template (it judges work)
    "product-spec": "role-product-spec",
    "research": "role-research",
    "lead": "role-lead",
}
RUN_KINDS = ("tests", "build", "review", "resume", "land")

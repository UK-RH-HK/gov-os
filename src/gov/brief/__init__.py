"""``gov brief``: a filled brief from the ticket and the facts file, refused when the ticket is not READY (W2-152).

The role -> role-template map and the lead's run kinds (the ticket's "Interface"); the builder is ``gov.brief.build``.
"""

ROLE_TEMPLATES = {
    "engineer": "role-engineer",
    "independent-test-designer": "role-test-designer",
    "independent-auditor": "role-reviewer",
    "product-spec": "role-product-spec",
    "research": "role-research",
    "lead": "role-lead",
}
RUN_KINDS = ("tests", "build", "review", "resume", "land")

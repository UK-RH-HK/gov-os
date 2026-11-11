# replaces cuts 1, 7, 8 of the earlier files: the five retired names stay (a W1-35 case pins them)
CUTS[0] = (" The retired texts `brief-test-designer.md`, `brief-engineer.md`, `brief-reviewer.md`, `brief-product-spec.md` and `brief-lead.md` are one-line pointers to these templates (DEC-1050).",
           " The retired `brief-test-designer.md`, `brief-engineer.md`, `brief-reviewer.md`, `brief-product-spec.md` and `brief-lead.md` point to these (DEC-1050).")
CUTS += [
    ("Each rule names the decision it follows; a rule that only an orchestrator's prompt held is cited with DEC-537, which ordered it stated here.",
     "Each rule names its decision; a rule only an orchestrator's prompt held is cited with DEC-537, which ordered it stated here."),
    ("a fresh test designer and a fresh implementer at the same time, from the spec, neither reading the other's work (DEC-959 item 7); the tests checked red against the ticket's base for the stated reason;",
     "a fresh test designer and a fresh implementer at the same time, neither reading the other's work (DEC-959 item 7); the tests checked red against the ticket's base;"),
    ("A lead returns one of these forms: DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED (DEC-236), then `brief_gaps:` (DEC-943 item 1).",
     "A lead returns one of these forms: DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED (DEC-236)."),
    ("The model `<model>` is named on every launch (DEC-460); no launch sets a compaction threshold (DEC-838).",
     "The model `<model>` is named on every launch (DEC-460)."),
    ("Of every part marked not read it says that the part was not read, and of a share not measured that it was not measured. A status question is never answered from recall (CAP-28, DEC-541).",
     "Of a part marked not read it says it was not read, and of a share not measured, that it was not measured. A status question is never answered from recall (CAP-28, DEC-541)."),
]

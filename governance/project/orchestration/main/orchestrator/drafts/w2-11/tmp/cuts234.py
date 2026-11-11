CUTS += [
    # 4 the temp-folder line: the next line is where reads are stated; drop the pointer
    ("nothing is left in another session's folders, and reading them is open as the next line states (DEC-386, DEC-537, DEC-820).",
     "nothing is left in another session's folders (DEC-386, DEC-537)."),
    # 5 the held-out line folds into the reads line
    ("the held-out material's contents, the counterpart's work on the same ticket and the hidden half of an evaluation set (DEC-820, DEC-1052).\n- The held-out material's contents are never read, by any role; its file names may be seen (DEC-525, DEC-820).\n",
     "the held-out material's contents (its file names may be seen), the counterpart's work on the same ticket and the hidden half of an evaluation set (DEC-820, DEC-525, DEC-1052).\n"),
    # 6 followed by hand
    ("These rules are followed by hand: they are not enforced by a mechanism yet (DEC-537). The resource gate is not a command; the launcher does not refuse a launch without a model; `AUTH_REQUIRED` is a stop the orchestrator names, not a mechanism; and leads are not started through the launcher, which starts workers alone.",
     "These rules are followed by hand, not enforced by a mechanism yet (DEC-537): the resource gate is not a command; the launcher does not refuse a launch without a model; `AUTH_REQUIRED` is a stop the orchestrator names; leads are not started through the launcher, which starts workers alone."),
]
CUTS += [
    # 7 W2-11's own ceiling line: the gate and the limits decide; the clause the cases pin stays
    ("No fixed number of tickets in flight: the eligible tickets, the resource gate and the owner's usage limits decide, each time a slot could open; every countdown says how many and why (DEC-847).",
     "No fixed number of tickets in flight: the resource gate and the owner's usage limits decide (DEC-847)."),
    # 8 the role templates by pattern
    ("with the role's template, `role-research.md`, `role-product-spec.md`, `role-test-designer.md`, `role-engineer.md`, `role-reviewer.md`, `role-lead.md` or `role-cto.md` (DEC-1050, DEC-1052).",
     "with the role's template (`role-research.md`, `role-product-spec.md`, `role-test-designer.md`, `role-engineer.md`, `role-reviewer.md`, `role-lead.md`, `role-cto.md`; DEC-1050, DEC-1052)."),
    # 11 the second-review line
    ("For a FULL ticket a second review is the last. After it only fail-open holes and losses of work are fixed (DEC-413 names silent changes to tests or ticket files); the rest are residuals (DEC-413).",
     "For a FULL ticket a second review is the last: after it only fail-open holes and losses of work are fixed, the rest are residuals (DEC-413)."),
]
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

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
     "No fixed number of tickets in flight: the resource gate and the owner's usage limits decide each time a slot could open (DEC-847)."),
    # 8 the role templates by pattern
    ("with the role's template, `role-research.md`, `role-product-spec.md`, `role-test-designer.md`, `role-engineer.md`, `role-reviewer.md`, `role-lead.md` or `role-cto.md` (DEC-1050, DEC-1052).",
     "with the role's template (`role-research.md`, `role-product-spec.md`, `role-test-designer.md`, `role-engineer.md`, `role-reviewer.md`, `role-lead.md`, `role-cto.md`; DEC-1050, DEC-1052)."),
    # 11 the second-review line
    ("For a FULL ticket a second review is the last. After it only fail-open holes and losses of work are fixed (DEC-413 names silent changes to tests or ticket files); the rest are residuals (DEC-413).",
     "For a FULL ticket a second review is the last: after it only fail-open holes and losses of work are fixed, the rest are residuals (DEC-413)."),
]

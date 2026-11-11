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

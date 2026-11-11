CUTS[2] = ("Merge queue, red nightly, Emergency: [integration-queue.md](integration-queue.md), [nightly-sheriff.md](nightly-sheriff.md), [incident-response.md](incident-response.md).",
           "Merge queue: `integration-queue.md`; red nightly: `nightly-sheriff.md`; Emergency: `incident-response.md`.")
CUTS[2] = (CUTS[2][0].replace("Merge queue, red nightly, Emergency: ", "Merge queue, red nightly, Emergency: "), CUTS[2][1])
CUTS[2] = ("The merge queue: [integration-queue.md](integration-queue.md). A red nightly: [nightly-sheriff.md](nightly-sheriff.md). An Emergency: [incident-response.md](incident-response.md).",
           "Merge queue: `integration-queue.md`; red nightly: `nightly-sheriff.md`; Emergency: `incident-response.md`.")
CUTS += [
    ("Detail: [briefs-and-returns.md](briefs-and-returns.md).", "Detail: `briefs-and-returns.md`."),
    ("a full regression runs (DEC-536), which since DEC-968 is the next nightly's; a close runs the scoped set.",
     "a full regression runs (DEC-536), since DEC-968 the next nightly's; a close runs the scoped set."),
    (" and health (the doctor summary).", " and health."),
    ("Reads are open: the whole repository, the governance folder included, other worktrees and git history, by any search, glob or listing, apart from secrets and keys,",
     "Reads are open: the whole repository (the governance folder included), other worktrees and git history, by any search, glob or listing, apart from secrets and keys,"),
]
CUTS += [
    ("confidence is medium or higher (for a P2 also medium-low, where the owner has widened it as in DEC-416);",
     "confidence is medium or higher (medium-low too for a P2, DEC-416);"),
    ("a lead with the absolute path of the CLI, `<absolute path of the CLI>`, a worker through the launcher;",
     "a lead with the CLI's absolute path `<absolute path of the CLI>`, a worker through the launcher;"),
    ("; leads are not started through the launcher, which starts workers alone.", "; leads are not started through the launcher."),
    ("; the tests checked red against the ticket's base;", "; the tests checked red;"),
    ("filled from the ticket and the project's facts file,", "filled from the ticket and the facts file,"),
]

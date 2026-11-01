"""Build briefs/rev-2.md (the second and last review) from rev-1.md (as filled) and design-r1.md."""

base = "/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/"
text = open(base + "briefs/rev-1.md", encoding="utf-8").read()
addendum = open(base + "design-r1.md", encoding="utf-8").read()

text = text.replace("review 1\n", "review 2 (the second and last, DEC-413)\n", 1)
text = text.replace("# Brief: reviewer (FULL, read-only), W2-96 (DAEO-ouet), review 1",
                    "# Brief: reviewer (FULL, read-only), W2-96 (DAEO-ouet), review 2, the second and last (DEC-413)")
start = text.index("Then run `printenv GOV_ROLE GOV_TICKET`")
end = text.index("## Standing rules")
text = text[:start] + (
    "Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-ouet`) and "
    "`git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96` and `w2/W2-96`), "
    "and `git rev-parse --short=12 HEAD` (expect `HEAD12`; the full id `git rev-parse HEAD` gives is the probe "
    "record's `probed_commit`). If anything differs, stop and say so. Over review 1's head `6ec6cbd6e158` the head adds: "
    "the engineer's fixes `d8ac34ff71de` (review 1's addendum, below) LATER_COMMITS, the test designer's review cases "
    "`3955f72177b6` merged by the lead in `382ef3b6`.\n\n") + text[end:]
text = text.replace(
    "- **Tests run no more than this (DEC-959 item 1):**",
    "- Never `cd` into a subfolder of the repository: the sandbox leaves a `.claude/` folder there (review 1 left one "
    "in `tests/acceptance/`). Work from the worktree's top with full paths. `rm` is refused by the permission layer "
    "in this non-interactive session: do not try it; name your probe folders in your return instead.\n"
    "- **Tests run no more than this (DEC-959 item 1):**")
text = text.replace(
    "- The lead's design note, given to both workers: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design.md`.",
    "- The lead's design note, given to both workers: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design.md`, "
    "and review 1's addendum, `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design-r1.md` (repeated below).\n"
    "- Review 1's record (a failing draft): `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/rev-1-result.md`.")
start = text.index("## What you probe for")
end = text.index("## Judgement rules")
text = text[:start] + """## What you probe for

Review 1 failed on F2 (SIGTERM or SIGHUP left the run's report in the caller's `TMPDIR`), F3 (map rows in forms the reader did not take were dropped, their failing tests hidden behind a pass) and F6 (a folder without permissions outlived the clean-up), and found F1 (`gov accept` crashed on every acceptance folder of this repository, whose `tests/conftest.py` refuses a per-run base folder). The lead's addendum, built by the engineer and tested by the designer:

""" + addendum + """

Probe the head for:
- whether each of F1, F2, F3 and F6 is closed, in ordinary use and at its edges (SIGTERM and SIGHUP at every phase of a run — before the child starts, while it runs, while the report is read, during the clean-up; a second signal; a folder without permissions at several depths; README rows in today's forms, the 70 acceptance READMEs of this repository read-only through copies of single README files);
- whether the fixes opened a new path by which test content reaches the caller (stdout, stderr, the envelope, an error, a traceback, a file left in the repository or the given `TMPDIR`), or a result that fails open (a failing, erroring or uncollected mapped test reported as pass; a line with no test passing; an exit code 0 when a mapped line fails);
- **any write in the repository** (`git status --porcelain --ignored` of the planted project before and after);
- `gov accept DAEO-ouet --json` on this worktree, read-only: a sane per-line result.

Not findings of this review (already with the orchestrator or recorded): the rule that a test the README never names never changes the exit code (KPI 3 and 5; package PKG-1 asks whether to change it); `gov accept` missing from the command list (package, DEC-747); review 1's rows F4, F8, F9, F10, unless the head changed them. Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

""" + text[end:]
text = text.replace("**Fail.**", "**Fail.**")
open(base + "briefs/rev-2.md", "w", encoding="utf-8").write(text)
print(len(text), text.count("HEAD12"), text.count("LATER_COMMITS"))

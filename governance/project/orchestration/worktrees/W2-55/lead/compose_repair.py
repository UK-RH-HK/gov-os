from pathlib import Path

base = Path("/home/usain/gov-os-worktrees/W2-55/.gov-runtime/scratch/lead/briefs")
first = (base / "eng-1.md").read_text(encoding="utf-8")
repair = (base / "eng-2-repair.md").read_text(encoding="utf-8")
head, _, rest = first.partition("## What you read")
commit = "## Commit" + rest.partition("## Commit")[2]
head = head.replace("# Brief: engineer, DAEO-arrl (W2-55), profile STANDARD, run 1",
                    "# Brief: engineer (a repair batch), DAEO-arrl (W2-55), profile STANDARD, run 1")
head = head.replace("You build the ticket to its specification and its KPIs, never to the tests.",
                    "You make one repair, below, to the ticket's code; you build to the specification, never to the "
                    "tests, and you never read `tests/acceptance/W2-55/`.")
head = head.replace("Use `TMPDIR=/tmp/gov-os-lead-W2-55` for your runs unless the sandbox sets its own temp folder "
                    "(keep that one).", "Keep the sandbox's own `TMPDIR`; do not set `TMPDIR` yourself.")
read = ("## What you read\n\n- The ticket file `.tickets/DAEO-arrl.md` (read-only) and its card in "
        "`docs/plan/WAVE_2_WBS.md` §2 (`#### W2-55`).\n- The code: `src/gov/decisions/` (`register.py` and its "
        "callers), `src/gov/context/`, `src/gov/retrieve/command.py`.\n\n")
commit = commit.replace("Your commits' hashes (12 digits); the files changed; the lines added and removed; the builder "
                        "tests and the acceptance tests you ran with their results; KPI 5's findings on this repository "
                        "and the register check's count;",
                        "Your commit's hash (12 digits); the files changed; the lines added and removed; the builder "
                        "tests and the acceptance tests you ran with their results; the timings asked for;")
(base / "eng-2.filled.md").write_text(head + read + repair + "\n" + commit, encoding="utf-8")
print("written", len(head + read + repair + commit))

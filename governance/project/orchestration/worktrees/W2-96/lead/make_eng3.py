"""Build briefs/eng-3.md (review 1's fixes) from eng-2.md and design-r1.md."""

base = "/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/"
eng2 = open(base + "briefs/eng-2.md", encoding="utf-8").read()
addendum = open(base + "design-r1.md", encoding="utf-8").read()

text = eng2.replace("# Brief: engineer, W2-96 (DAEO-ouet), run 1, second engineer",
                    "# Brief: engineer, W2-96 (DAEO-ouet), run 1, review 1's fixes")
start = text.index("**Where things stand.**")
end = text.index("## Step 0")
text = text[:start] + (
    "**Where things stand.** `gov accept` is built (`9859695c8fcc`: `src/gov/accept/__init__.py`, `command.py`, "
    "`runner.py`, `tests/unit/accept/test_w2_96_accept.py`), the acceptance tests are merged (`986fa7cf4b1e`) and "
    "pass (54), and the unit tests pass (25). An independent reviewer then probed it and found behaviour that fails "
    "open or misses a KPI; the lead turned the findings into the addendum below, which overrides the design note "
    "where they differ. Your job: build the addendum, test-first in your own unit tests, inside your paths. A test "
    "designer is writing review cases for it in parallel; the lead merges them after you return.\n\n") + text[end:]
marker = "Points that make this fail closed, never open:"
text = text.replace(marker, addendum + "\n" + marker)
start = text.index("## The acceptance tests (already merged)")
end = text.index("## Return")
text = text[:start] + (
    "## The acceptance tests\n\n"
    "The tests merged so far are in `tests/acceptance/W2-96/`; you never open them (DEC-820 (c)). Review 1's new "
    "cases are not on this branch yet.\n\n"
    "1. Build the addendum, R1 to R7, with unit tests for each point (R2: send the signal to a `gov accept` process "
    "you start on a planted project; R3: a planted test that leaves a folder without permissions). Commit.\n"
    "2. Then run the merged acceptance tests once, **through pytest**, reading results only, as a regression check: "
    "`PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/acceptance/W2-96 -q "
    "-p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`. A case the addendum changes may now fail "
    "by design (the README's old reading): name it with its one-line message, and do not bend the code back. Any "
    "other failure: fix the code to the specification, commit, and run again; at most three runs in all.\n"
    "3. Run `gov accept` on this ticket once and quote its JSON: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src "
    "python3 -m gov.cli.main accept DAEO-ouet --json` (after R1 it must run in this repository and report per line).\n"
    "4. Run your unit tests again (`tests/unit/accept`) and return.\n\n") + text[end:]
open(base + "briefs/eng-3.md", "w", encoding="utf-8").write(text)
print(len(text), text.count("R7"))

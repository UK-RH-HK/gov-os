"""Fill rev-3.md: the head to probe, run 2's commits and the lead's results for review 3."""
import re

path = "/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/briefs/rev-3.md"
head = "382e6d8fba8c"
text = open(path, encoding="utf-8").read()
text = text.replace("@@HEAD12@@", head)
changes = (
    "the engineer's `41b9fdddf109` (R8 to R13: any failed case fails the run; SIGINT held during the clean-up with "
    "SIGTERM and SIGHUP; a removal without recursion; inherited ignores kept; exit 128+N; `accept` in "
    "`RECORDED_GOV_COMMANDS`) and `917aba42cd9c` (once a stop is decided the three signals are ignored, so a signal after "
    "the clean-up never kills `gov`); the test designer's `1bf0c1d2e18f` (`accept` in W1-07's and W1-32's command lists, "
    "`Rewrite-Reason: DEC-959 item 6`) and `a5ad2254e97b` (21 run-2 cases in `test_w2_96_at_run_2.py`, 7 run-1 cases "
    "revised for R8, `Rewrite-Reason: DEC-970 ...`), merged by the lead in `7bc8a0303e0d`; the lead's checkpoint record "
    "`" + head + "` (no code). `git diff --stat 549dd29b1c6f " + head + "`: 14 files, +1052/-59."
)
text = text.replace("@@CHANGES@@", changes)
results = (
    "the lead's red check of run 2's suite on run 1's code (the tests branch): 23 failed, 77 passed, each red for its "
    "README's reason (R8 exit or outcome, R9/R10 leftovers holding the marker, R11 a stop on an ignored signal, R12 death "
    "by the signal); the engineer's runs on this branch: `tests/unit/accept` 62 passed; the first `gov accept DAEO-ouet "
    "--json` after the merge exit 3 (2 failed, R9's Ctrl-C cases: a signal after the clean-up killed `gov`), fixed in "
    "`917aba42cd9c`; the second exit 0, `outcome: pass`, all nine lines pass, `unmapped` 20 passed, `totals` 100 passed; "
    "W1-07's, W1-32's and W1-26's recorded-command files 21 passed. The lead's rebuild and scoped run (select_tests.py, "
    "scope `scoped`, `core_changed` [`src/gov/check/commands.py`]) run beside you; they do not change the code you probe. "
    "The test designer kept one case of its own reading (P-W2-96-R11-GROUP, decided by the lead as P3: keep): R11's "
    "SIGHUP also sent to `gov`'s process group."
)
text = text.replace("@@RESULTS@@", results)
open(path, "w", encoding="utf-8").write(text)
print(text.count(head), "@@" in text, re.findall(r"[0-9a-f]{40}", text))

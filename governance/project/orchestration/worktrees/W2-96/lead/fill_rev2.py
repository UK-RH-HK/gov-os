"""Fill rev-2.md: the head to probe, the later commits and the lead's results for review 2."""
import re

path = "/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/briefs/rev-2.md"
head = "ea5728df2d9a"
text = open(path, encoding="utf-8").read()
text = text.replace("HEAD12", head)
text = text.replace("LATER_COMMITS", "and `720a26fd4d7d` (a line's counts are only of tests that ran), the lead's checkpoint record `" + head + "`, and")
text = text.replace("at the head `6ec6cbd6e158`, and its acceptance tests pass.", "at the head `" + head + "`, and its acceptance tests pass.")
text = text.replace("`git diff --stat ab1ea26c5585 6ec6cbd6e158`", "`git diff --stat ab1ea26c5585 " + head + "`; review 1's fixes: `git diff 6ec6cbd6e158 " + head + " -- src tests/unit`")
start = text.index("- The lead's suite results:")
end = text.index("\n", start)
results = ("- The lead's suite results: the fourth engineer's run on this branch after review 1 (`tests/acceptance/W2-96`: "
           "79 passed, review 1's 18 cases and 7 premises included; `tests/unit/accept`: 41 passed); `gov accept DAEO-ouet --json` "
           "on this worktree: `outcome: pass`, all nine lines pass, `unmapped` 17 passed, `totals` 79 passed, exit 0; the test "
           "designer's run of review 1's cases on the base code (red: `gov accept` absent). The command-list red (W1-32, "
           "`accept` not recorded) is the lead's package, not a finding. The lead's scoped run (select_tests.py) waits for the "
           "machine's load and runs after you; it does not change the code you probe.")
text = text[:start] + results + text[end:]
open(path, "w", encoding="utf-8").write(text)
print(text.count(head), "6ec6cbd6e158" in text, re.findall(r"[0-9a-f]{40}", text))

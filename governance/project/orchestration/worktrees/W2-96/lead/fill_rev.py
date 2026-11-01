"""Fill rev-1.md's placeholders: the head to probe and the lead's results so far."""
import subprocess

path = "/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/briefs/rev-1.md"
head = subprocess.run(["git", "-C", "/home/usain/gov-os-worktrees/W2-96", "rev-parse", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
results = (
    "the test designer's red run on the base code (44 failed because `gov accept` did not exist, 10 premises "
    "passed); the second engineer's run on this branch (`tests/acceptance/W2-96`: 54 passed; `tests/unit/accept`: "
    "25 passed); the first engineer's run of W1-07, W1-26 and W1-32's command-set cases (17 passed, 1 failed: "
    "W1-32's `test_the_command_set_is_the_twelve_and_the_three_recorded_ones`, red because `accept` is not yet "
    "recorded in the command list, which the lead returns as a package; not a finding of this review); the lead's "
    "whole-tree collection (17387/17389 collected, no error). The lead's scoped run (select_tests.py) waits for the "
    "machine's load and runs after you; it does not change the code you probe"
)
text = open(path, encoding="utf-8").read().replace("HEAD_TO_PROBE", head).replace("LEAD_RESULTS", results)
open(path, "w", encoding="utf-8").write(text)
print(head, text.count(head))

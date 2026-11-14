"""Assemble the round-2 auditor brief: head (placeholders filled) + JUDGEMENT.md word for word + tail."""
B = "/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/briefs/"
head = open(B + "rev-2-head.md").read()
results = (
    "`gov accept W2-101`: 271 passed, 6 failed (success-6 and failure-5, the same six cases counted under both). "
    "`lead_verify` (6328 tests, `.gov-runtime/scratch/lead/log/verify/parallel.xml`): 9 failed, all `.claude/skills/` "
    "copies absent: `test_w2_101_copies.py::test_the_claude_copy_matches_the_kernel_source[*]` (3), "
    "`::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[*]` (3, GENERATED_DIFFERS), and W2-11's "
    "`test_the_skill_carries_one_version_in_all_four_places[*]` (3). `.claude/skills/<skill>/` is placed only by the "
    "copies ACT after the owner's yes (DEC-315, DEC-1112 (3); out of the ticket's paths). W2-11's output-class cases "
    "(L1) pass. Judge for yourself whether any of these is caused by this change."
)
head = head.replace("{HEAD12}", "1ef54a70037a").replace("{RESULTS}", results)
assert "{" not in head.replace("{\"", "").replace("`{", ""), "an unfilled slot remains"
judgement = open("/home/usain/gov-os-worktrees/W2-101/governance/project/briefs/JUDGEMENT.md").read()
tail = open(B + "rev-2-tail.md").read().split("\n", 7)[7]  # drop the convergence bullet: JUDGEMENT.md now carries it
open(B + "rev-2.md", "w").write(head.rstrip("\n") + "\n\n" + judgement.rstrip("\n") + "\n\n" + tail)
print("wrote", B + "rev-2.md")

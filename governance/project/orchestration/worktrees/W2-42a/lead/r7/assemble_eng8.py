"""Assemble eng-8's brief: eng-7's head with the second batch's rules, and the red log on 4692b61ddac6."""
D = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/"
head = open(D + "r7/eng-7-head.md").read()
head = head.replace("{HEAD}", "4692b61ddac6").replace(
    "{FILES}", "tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs.py "
               "tests/acceptance/W2-42a/test_w2_42a_r5_error_path.py")
head = head.replace("(DEC-1157 (12), DEC-1180 (4))\n", "(DEC-1157 (12), DEC-1180 (4)): second batch\n", 1)
extra = open(D + "r7/eng-8-extra.md").read()
head = head.replace("Also run the whole acceptance folder", extra + "Also run the whole acceptance folder", 1)
log = open(D + "log/r4b-red.log").read()
open(D + "r7/eng-8.md", "w").write(head + log + "```\n")
print("ok", len(head + log))

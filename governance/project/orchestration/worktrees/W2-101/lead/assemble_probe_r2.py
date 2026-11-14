"""The round-2 probe record: the lead's head + the reviewer's REVIEW_MD verbatim + its verdict block verbatim."""
L = "/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/"
res = open(L + "log/rev-2-result.md").read()
review = res.split("REVIEW_MD_BEGIN\n", 1)[1].split("REVIEW_MD_END", 1)[0]
verdict = "```verdict" + res.split("```verdict", 1)[1].split("```", 1)[0] + "```\n"
out = open(L + "probe-r2-head.md").read() + review.rstrip("\n") + "\n\n## The reviewer's verdict block (verbatim)\n\n" + verdict
open("/home/usain/gov-os-worktrees/W2-101/docs/probes/DAEO-6icv/PR-DAEO-6icv-r2.md", "w").write(out)
print("ok", len(out.splitlines()))

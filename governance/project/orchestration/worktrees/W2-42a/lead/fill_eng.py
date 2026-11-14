B = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/briefs/"
t = open(B + "eng-1.md").read()
t = t.replace("FAILED_LIST", open(B + "eng-failed.txt").read().rstrip())
errs = [l for l in open(B + "eng-errors.txt").read().splitlines()]
seen, uniq = set(), []
for l in errs:
    if l not in seen:
        seen.add(l); uniq.append(l)
t = t.replace("ERROR_LINES", "\n".join(uniq))
open(B + "eng-1.md", "w").write(t)
print(t.count("FAILED tests"), "failed lines;", len(uniq), "error lines")

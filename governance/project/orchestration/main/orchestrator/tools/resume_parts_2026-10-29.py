"""Makes the resume parts of the three leads the orchestrator's chain stop killed at 16:57 on 2026-10-29 (W2-61,
W2-03, W2-05): each part's head check is replaced by the worktree's current head and state, with a note on what the
killed lead had done. Writes <part>-r.md beside each part (the W2-61 part from its filled copy)."""
import pathlib
import re
import subprocess

B = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs")
KILLED = ("**Restarted (2026-10-29):** the previous lead of this run was stopped at 16:57, about 20 minutes in, by "
          "the orchestrator's own mistake (stopping its launch queue also stopped the leads it had started). "
          "It returned nothing. ")
NOTES = {
    "W2-61": ("W2-61-part-run1.filled.md",
              "Its test designer was stopped mid-work: `git status --short` shows `?? tests/acceptance/W2-61/` "
              "(uncommitted, unfinished). Launch a fresh test designer as planned, and tell it these files are an "
              "unfinished draft by an earlier designer of this ticket: it may keep, revise or replace them, and "
              "commits only what it stands behind. Nothing else is in the tree."),
    "W2-03": ("W2-03-part-mergeback.md",
              "It had committed step 1, the merge of `w2/integrate` (`b23bf1ac`, no conflict, as the dry merge "
              "said): check that commit's trailers and that `grep -c '^### DEC-941' docs/DECISION_REGISTER.md` "
              "shows 1, then go on from step 2. Note: `w2/integrate` gained DEC-942 since (records only); do not "
              "merge again unless `git diff --stat b23bf1ac w2/integrate -- src tests` is non-empty."),
    "W2-05": ("W2-05-part-mergeback.md",
              "It had committed the merge of `w2/integrate` (`1814315f`), with its conflicts resolved: before "
              "anything else, check that commit (`git show --stat 1814315f`, and the two files that conflicted, "
              "`src/gov/check/runner.py` and `src/gov/retrieval/retrieve_check.py`, against the rules of step 1: "
              "both sides kept, W2-59's `PYTHONPATH` removal kept). If the resolution breaks a rule, revert that "
              "merge commit with `git revert -m 1` and return PACKAGES. Otherwise go on from the step after the "
              "merge. Do not merge again unless `git diff --stat 1814315f w2/integrate -- src tests` is non-empty."),
}
for w2, (part, note) in NOTES.items():
    wt = "/home/usain/gov-os-worktrees/" + w2
    head = subprocess.run(["git", "-C", wt, "rev-parse", "--short=12", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()
    status = subprocess.run(["git", "-C", wt, "status", "--short"], capture_output=True, text=True,
                            check=True).stdout.strip()
    text = (B / part).read_text(encoding="utf-8")
    want = "`git status --short` must show " + ("only `" + status + "`" if status else "nothing")
    new, n = re.subn(r"`git rev-parse --short=12 HEAD` must show `[0-9a-f]{12}`, and `git status --short` must show "
                     r"nothing\.", "`git rev-parse --short=12 HEAD` must show `" + head + "`, and " + want + ".", text,
                     count=1)
    if n != 1:
        raise SystemExit(w2 + ": head check line not found")
    new = new.replace("\n\n", "\n\n" + KILLED + note + "\n\n", 1)
    (B / part.replace(".filled.md", ".md").replace(".md", "-r.md")).write_text(new, encoding="utf-8")
    print(w2, head, repr(status))

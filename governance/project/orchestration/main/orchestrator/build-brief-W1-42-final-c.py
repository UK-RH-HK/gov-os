"""Assemble the lead brief of the final pass's third part on W1-42 (run 8c): run 8b committed and merged, then the WSL restart killed it at the start of its verify; the /tmp clones are gone (archived). Verify, checkpoint, return."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
b = open(B + "W1-42-A5-final-b.md", encoding="utf-8").read()

# The opening paragraph, the check and the reading list.
top_end = b.index("**The guard in this worktree refuses")
TOP = """You are a fresh ticket lead continuing ticket `DAEO-gjjf` (`W1-42`, "Wave 1 exit run on the dev tiers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-42` on branch `w1/W1-42`. You are a headless session: nobody answers questions while you work, and only your final message is read. **This is the third part of the final pass (run 8c). Your predecessor (run 8b) did steps 1 to 3 below and committed them; the machine (WSL) was then restarted while its verify (step 4) was starting, which killed it before any suite ran and before its checkpoint. You do steps 4 and 5 and return.** No worker is launched; no `gov close` runs; no clone is touched.

**Check first:** the branch head is `da6fb889` ("W1-42 run 8b: the adoption-readiness block and the owner's intended exit in the exit report (DEC-710 to DEC-714)"), its parent `8d119104` (the merge of `w1/integrate` at `3d87550e` into `7217bfa9`, run 8's report and evidence); `git status --short` is empty. Anything else: return PACKAGES with it as the first line. Run 8b's logs are under `.gov-runtime/scratch/lead/log/` (`m1.*`, `c2.*`; `verify8-parallel.txt` is empty from the killed start: overwrite it).

**Read:** `.gov-runtime/scratch/lead/CHECKPOINT.md` (run 8's, superseded by this brief where they differ), `verify8a.sh`, `verify8b.sh`, `regress.py`, and in `docs/DECISION_REGISTER.md`: DEC-710 to DEC-714.

"""
b = TOP + b[top_end:]

# The clones: gone with /tmp.
c0 = b.index("## The clones")
c1 = b.index("## Decided ground")
CLONES = """## The clones

The restart cleared `/tmp`, so the two live clones under it are gone. Their last state is archived by the owner (a-dev feature `127227c`, main `736669f`; b-dev `fc28272`, main `3b1ad56`), the same heads run 8 measured. **You need neither clone for steps 4 and 5: do not look for them, do not recreate them, and never read or list `~/gov-os-workbench/`.** Report the clones' heads as "archived at the heads above (the /tmp copies cleared by the restart)".

"""
b = b[:c0] + CLONES + b[c1:]

# The steps: 1 to 3 done.
s0 = b.index("1. **Commit run 8's six files")
s1 = b.index("4. **Verify:**")
DONE = """1. Done by run 8b: `7217bfa9` (run 8's six files, after the hook check and the rebuild).
2. Done by run 8b: `8d119104` (merge of `w1/integrate` `3d87550e`).
3. Done by run 8b: `da6fb889` (the adoption-readiness block, the verdict beside the owner's intended exit, the auditor's lines for DEC-710 to DEC-714, the deviations, the three red cases under DEC-713). Read the report's new sections to quote them in your return; change nothing in it unless a check below needs it, and then return PACKAGES rather than edit.
"""
b = b[:s0] + DONE + b[s1:]

b = b.replace("**Deviations:** run 8's stop on the hook refusal, the foreign commits, the restore, and this run 8b.",
              "**Deviations:** run 8's stop on the hook refusal, the foreign commits, the restore, and run 8b.")
assert "run 8c" in b and "/tmp/claude-1000" not in b
open(B + "W1-42-A5-final-c.md", "w", encoding="utf-8").write(b)
print(len(b))

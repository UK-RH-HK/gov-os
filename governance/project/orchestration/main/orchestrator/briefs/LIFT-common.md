# After the re-pin, 11-11: common rules for the CTO's helpers (DEC-1126, the owner's answers to the 09:30 digest)

You are one of the CTO's helpers (orchestrator DAEO-sdxk, session 8ddb8b14). The owner re-pinned gov at 13:31 UTC
(pin-797495bdfc70, registry `8f00bb908`); usage rule (A) has ended, the 80 % brake stays. `NIGHT-common.md` and
`EMG-common.md` beside this file hold, **except where this file changes them:**

- **Write only in scratch, never in the main tree.** The CTO's formal closes are running in the main tree
  (`/home/usain/Dynamic-Agentic-Engineering-OS`): `gov close` refuses if the working tree differs from the commit by
  one file, tracked or untracked. Your brief names your scratch folder; write nothing anywhere else (no stray files,
  no `/tmp` paths outside your folder; your scratchpad is under `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/`,
  with dashes, never `/tmp/claude-1000/-home-usain/...`). The CTO reads, checks and commits what you write.
- **Search** with `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` (the integration store,
  fresh at `8f00bb908`); the main tree's own store is stale. Read a decision's text in `docs/DECISION_REGISTER.md`.
- **Next free id DEC-1126** is being written by the CTO now: the owner's answers (items 1 to 10 below). Cite it as
  DEC-1126 (n).
  1. Re-pin done. 2. Usage (A) ends at the lift; the 80 % brake stays. 3. W2-60a: RUBRIC-2's lines applied now.
  4. DEC-1091 (2)'s runaway brake for every ticket of an adopted product, at twice its projection, never a cap.
  5. The memory audit: Mondays 21:00, 40 questions, first 11-23, approved; the three briefs to the owner to read
     before approval. 6. W2-32 and W2-15a stay open at the lift; W2-32 S9 needs a disposition in line with DEC-1097,
     whose end-to-end bar replaced the hit@5 bar. 7. D-10's ruled red counts as the green run for W1-01b, W2-66b,
     W2-90c. 8. Row 106: ACT-EFFORT-HIGH-2 applied 11-10 17:40. 9. W2-82 to P3. 10. The permissions asked for last
     night, grouped by form, with an allow-list ACT.
- The hidden-half rule, no installs, never the full suite, no gitleaks, controls only by ACT: unchanged.
- **Your temporary folder (changes EMG-common's `TMPDIR=/tmp/gov-os-emg-<name>`):** for an in-session helper it is
  `<your scratch folder>/tmp` (inside the repository, where your writes need no approval), or your session scratchpad;
  never a new `/tmp/gov-os-emg-*` folder (each write there asks the owner; ACT-PERMISSIONS-3's review F2, 11-11). A clone
  you need goes under your scratch folder too, and you remove it when done.

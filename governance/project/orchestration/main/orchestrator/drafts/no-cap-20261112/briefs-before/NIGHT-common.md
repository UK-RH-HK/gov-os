# The night of 11-10/11 to the re-pin: common rules for the CTO's helpers (DEC-1125 (3))

You are one of the CTO's helpers (orchestrator DAEO-sdxk, session 8ddb8b14). The owner sleeps; at about 08:00-09:30
UTC the owner reads the 09:30 digest and re-pins gov by hand. Tonight's work, all on the lift's critical path under
usage (A) (DEC-1122, DEC-1115 (4)): the re-pin ACT (rehearsed in a clone, independently reviewed), the formal closes
prepared, a full anti-drift audit before the re-pin, and the first ready lists for after the lift. Your brief says
which part is yours.

`EMG-common.md` beside this file holds, **except where this file changes it:**
- **You do not commit and you do not use a worktree branch unless your brief says so.** You write only the paths your
  brief lists, in the main tree (`/home/usain/Dynamic-Agentic-Engineering-OS`, branch `w2/integrate`) or in scratch;
  the CTO reads, checks and commits them. Never `git add`, `git commit`, `git stash`, `git checkout`, `git reset`,
  `git merge`, `git push` in the main tree. Other helpers write other paths in the same tree at the same time: touch
  nothing outside your list, and never revert a change you did not make.
- **Never `src/`, `tests/`, `governance/project/path-map.yaml`, `class-rules.yaml`, the guard, the hooks, `.claude/`,
  the crontab, the servers, `~/.local/`.** The CTO freezes `src/` tonight so the re-pin candidate's wheel stays fixed.
  Anything that needs code, a control or an ACT: list it in your return with your recommendation for the morning.
- **The hidden-half rule, strictly:** never open `~/gov-os-eval/`, `~/gov-os-runs/`, any folder named `hidden`,
  `memory-verdict` or `memory-verdict-2`, or any held-out material. No installs. Never the full suite. No gitleaks.
- **Decisions:** the register (`docs/DECISION_REGISTER.md`, next free id DEC-1126) is the CTO's; you propose, never
  add. A decision's text is read in the register, not from memory. Today's: DEC-1120 (RUBRIC-2), DEC-1121/1122
  (ticket template 1.0.1 with `class`), DEC-1123 (D-10 run 2; trailers a warning until W2-115; stand-by expiry),
  DEC-1124 (Q23), DEC-1125 (the latency a named red; the memory audit weekly; tonight).
- **Plain language** in what the owner reads (`docs/style/PLAIN-LANGUAGE.md` if present): short sentences, no
  invented jargon, figures with units.
- **Context:** hand over past about 200k tokens (DEC-1118): write what you have and what remains in your return.
- **Return** the twelve fields as in `EMG-common.md`, short; the payload after.


## W1-38: rulesync adapters and the adapter-portability check (DEC-468, DEC-469, DEC-471, DEC-481; 2026-10-07)

Merged at `ca5889c9` (87 cases; `src/gov/adapters/portability.py` 202 lines against an estimate of 50, the
rest adapter source text and one check declaration). `adapter-portability` (family adapter/model portability,
tier G1, severity hard-block) makes three comparisons: the installed rulesync version with the registered
one; the kernel's roles and skills with their `.rulesync/` sources, tools included; and the project's
generated files, byte for byte, with a fresh generation.

- `gov check` on the branch before the merge (`log/check-at-W1-38-premerge.json`): `adapter-portability` is
  red with 43 findings and joins the baseline with that state (DEC-481): this repository's `.claude/`,
  `CLAUDE.md` and `AGENTS.md` are hand-kept until the owner applies the generated output at the exit (28
  findings under `.claude/skills`, 6 agents, 6 commands, the settings file, `CLAUDE.md`, `AGENTS.md`).
  `product-traceability-trailers` 735 as recorded (DEC-482); the twelve earlier baseline reds.
- Full regression at `ca5889c9` (`log/reg/at-W1-38-merge.txt`): every suite passed, `RESULT: ALL PASS`; no
  suite needed a run alone.
- Own runs (`log/W1-38-own.txt`): W1-38 87, W1-33 113, W1-35 112, W1-36 84, W1-29 45, W1-28 149, W1-26 212 and
  1 skipped, W1-04 336, W1-07 219, unit 1094; again at the merged branch head: W1-38 87, W1-33 113, W1-30 204,
  unit 1251.
- **The check generates.** It runs `rulesync generate` from the project's `.rulesync/` into an empty
  temporary folder of its own and writes nothing in the project (within the owner's rule, DEC-481). It needs
  rulesync and Node where it runs; where they are absent it reports an error, not a match.
- **One edit can give many findings:** a change in a skill that has supporting files gave 11 findings in a
  case; the 43 here are one cause.
- Where the check can still say "matches" without having compared (for the Wave 2 list, DEC-466): paths under
  `.claude/` other than the three generated folders and the settings file are not judged (what a live session
  writes there is looked at in W1-42, DEC-471); `settings.local.json` and `worktrees/` are other owners'; a
  generated file is compared with what the installed rulesync produces, so a wrong but registered rulesync
  gives a wrong reference.
- **For W1-40:** a CI step that runs the same comparison (the first lead's package). **For W1-42:** whether a
  live session loads the generated roles, skills and commands.
- History of the branch, for the exit auditor: the lead's second run (`a95e54a3`) edited eight kernel skill
  files outside the ticket's paths (flagged by containment, left in history); the orchestrator restored them
  from `b8137e35` in `deead8f9`. The lead's two runs were read and not accepted (the version checked only if
  a configuration named one; the kernel never compared with the source copies; cases that held only that a
  file exists); the behaviour was then built by direct designer and engineer turns. One engineer session
  checked out another commit in the worktree and repaired it itself; briefs now forbid it.
- Learning metrics: KPI disputes raised by the designer: two, settled by DEC-468, DEC-469 and DEC-471;
  acceptance cases rewritten after implementation began: the round-3 and round-4 batches, for comparisons
  the lead's code claimed without making.

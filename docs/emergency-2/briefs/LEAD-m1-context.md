# Lead brief: retire `gov context` and its module; the close records decisions from the ticket's sources (M1, W2-200)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/NIGHT-COMMON.md` first and follow it.
Branch `e2/m1-context` from `w2/integrate`, worktree `/home/usain/gov-os-worktrees/E2-m1-context`. **C3** (the close):
the test designer and engineer run Opus. `Task: DAEO-<your new ticket id>`, `Class: F`.

**The owner's decision (DEC-1214 M1 (c)):** "retire the module too; the close (inside the landing) records decisions
from the ticket's sources. Everything that depended on `gov context` is replaced by something tested and proven; no
ceiling anywhere."

**Read:** audit 2 `docs/emergency-2/audits/02-memory-in-use.md` Table 1a (every caller of `gov context`: the command,
the library `gov.context`, its check, `gov close`, adopt's facts entry, `--in-force`, EXAMIN's copy); EMERGENCY-2 §5.5;
`src/gov/context/`, `src/gov/close/`, `src/gov/cli/main.py`, `gov check`'s context-reproducibility family, the adopt
facts entry, `gov decisions`.

**Your feature (a ticket first, wbs_id W2-200, KPI lines each with its verify):** the command, its check and the module
are gone; `gov close` records the decisions that govern the change from the ticket's own sources (its `sources`,
`decisions` and KPI lines' citations, the register by id), with no size ceiling; `--in-force` lives in `gov decisions`;
adopt writes no context facts entry; `gov check` has no context family (or one that measures what replaces it); every
test that asserted `gov context` is retired or rewritten with a Rewrite-Reason naming DEC-1214 M1. Keep the change
inside the close, the CLI, the check and adopt; G1's lead removes other retired code tonight and leaves `gov context`
to you.
**Flow:** test designer (Opus) writes `tests/acceptance/W2-200/`, red on the base, and retires or rewrites the cases that
assert `gov context` (W2-54's context-reproducibility case among them); engineer (Opus) builds until `gov accept W2-200`
is green; then `tests/unit/close`, `tests/unit/check`, `tests/unit/adopt` and every acceptance folder you touched.

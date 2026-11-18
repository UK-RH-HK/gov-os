# Lead brief: L2's command table (what stays, merges, retires) for the owner's yes; the landing-and-close design

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/NIGHT-COMMON.md` first and follow it.
You are a research lead (docs only, no code). Branch `e2/l2-table` from `w2/integrate`, worktree
`/home/usain/gov-os-worktrees/E2-l2-table`. `Task: emergency-2`, `Class: Q`, `Role: research`.

**The owner's decision (DEC-1214 L2):** "the landing and the close are one deterministic action. The landing writes the
close record itself; no separate close step carries weight of its own. The CTO proposes which `gov` commands stay and
which retire on that basis: practical, fast, cheap, high quality, records kept, nothing duplicated." Also Q-CLOSE: the
landing records a red from an untrailered first commit as a known base red; M1: `gov context` retired (tonight, another
lead).

**Read:** audit 1 `docs/emergency-2/audits/01-landing-templates-briefs.md`; `gov --help` and every subcommand's help
(`PYTHONPATH=<worktree>/src python3 -m gov.cli.main <cmd> --help`); `src/gov/cli/main.py` (the command list),
`src/gov/check/commands.py` (GOV_COMMANDS); the landing today (`src/gov/close/`, `src/gov/queue/`, the scratch
`land.py` under `.gov-runtime/scratch/orchestrator/tools/` if present); EMERGENCY-2 §4.3, §6.

**Write `docs/emergency-2/L2-COMMANDS.md`:**
1. **The table:** one row per `gov` command (and each subcommand that is a separate action): what it does today, who
   calls it (agents, the landing, adopters, the owner), the verdict (stays / merges into X / retires), the reason in the
   owner's terms (practical, fast, cheap, quality, records, duplication), what replaces it, and the tests and docs it
   takes with it. Count the result (commands before and after).
2. **The landing-and-close design:** the one deterministic action from the merge to the closed ticket: its steps, what
   record it writes (the close record's fields), how it treats base reds (Q-CLOSE), what `gov queue` and `gov close`
   become, and what an adopter runs. Name each code change as a ticket-sized item with its KPI lines (observable, each
   with its verify), and mark which need the owner's yes (the table's retirements) and which do not (the merge itself,
   decided by L2).
3. **The owner's page:** at the top, a short list he answers with codes ("L2-1 yes, L2-2 no, ...").
Commit on your branch. Return the page's path and the counts.

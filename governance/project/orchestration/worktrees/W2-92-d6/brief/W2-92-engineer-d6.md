Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-92-d6/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-92 — the engineer's brief, D-6 part 2: S11, the register's verbless change labels (DAEO-n0wb)

You are a fresh engineer for **W2-92** (`.tickets/DAEO-n0wb.md`). Read it, with its new line **S11**, its new failure
line and its "D-6 part 2 placed here" note. W2-92 is merged into `w2/integrate`. **One small pass, S11 only.**

## The point
The function is `gov.store.loader.register_statements` (`src/gov/store/loader.py`, `_entry_statements`). Today, a
change label with no "<verb> ... by" counts **every** id in its value as a changer. The labels are `**Changed by:**`,
`**Amended by:**`, `**Lifted by:**`, `**Superseded by:**` and `**Amended:**`. See the branch
`if not by:  # "**Changed by:** DEC-953 (item 3)": a change with no verb`.

S11 counts only the ids at the head of its clauses:
- (1) the value ends at ` · ` and at any line break that starts a list item, at any indentation (`\n   - ...`);
- (2) it splits into clauses at each `;` outside parentheses;
- (3) a clause's head is its text before its first `:` outside parentheses, or the whole clause when it has none;
- (4) the changers are the ids in a head that stand outside parentheses.

Each head gives `amend`, or `supersede` for `**Superseded by:**`, as today. Labels with a verb, and every other
statement form, give exactly what they give today: the same six keys per statement. Check whether rule (1)'s cut
should also apply to the verb branch of in-labels and to the out-labels. **Do not change them:** S11 is the verbless
branch only. If the cut must be shared, keep the others' results identical. The designer's guard compares them.

**The CTO's probe on this repository's register** (record it before and after in your evidence):
- **Wrong pairs that must go:**
  - DEC-208, DEC-237 and DEC-838 → DEC-281;
  - DEC-880 and DEC-913 → DEC-608;
  - DEC-843 → DEC-880;
  - DEC-891 → DEC-896;
  - DEC-866 → DEC-492;
  - DEC-723 → DEC-728;
  - DEC-775 → DEC-780.
- **Heads that stay:**
  - DEC-900 and DEC-899 → DEC-757;
  - DEC-882, DEC-884 and DEC-889 → DEC-880;
  - DEC-868 and DEC-908 → DEC-455;
  - DEC-1057 and DEC-522 → DEC-511.
- Also record `gov links --all`'s UNMARKED_CHANGE count before and after (9 today). DEC-780 ← DEC-775 should leave.

## Where you work
- `/home/usain/gov-os-worktrees/W2-92-d6`, branch `w2/W2-92-d6`. It was made from `w2/integrate` at `49885f32b`, with
  the designer's cases merged at `decf83278`.
- Your paths: `src/gov/store/loader.py`, `tests/unit/store/**` and `docs/research/W2-92-memory-measure.md`. Put a short
  "S11 (D-6 part 2, DEC-1109 (2))" section there, with the probe before and after.
- **You never read `tests/acceptance/W2-92/`** (G-14; DEC-820 (c)). You see only `gov accept`'s results.
- **The exclusion line (DEC-1093 (2)):**
  - every recursive grep carries `--exclude-dir=W2-92`;
  - every Grep or Glob call that could reach the folder carries `!tests/acceptance/W2-92/**`;
  - find carries `-path '*/W2-92' -prune`.

  If a search shows you a line of the cases, stop and say so.

## Verify
Run everything through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-d6/src`, a scratch HOME (link `.local` into it) and
`PYTHONUSERBASE=/home/usain/.local`.
1. Your unit cases in `tests/unit/store/`, with new cases for the four rules.
2. `python3 -m gov.cli.main accept W2-92 --root /home/usain/gov-os-worktrees/W2-92-d6`. Every S11 and failure-6 case
   must be green. Name any other red, and say whether it was red before your change. Real-model or store cases you
   cannot run in the sandbox: say so.
3. The scoped set from `select_tests.py`, as `EMG-common.md` says. Never the full suite.

Commit as you go.

## Rules
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- No GPU, model, network, installs or service. No store rebuild is needed.
- **DEC-1080:** use the Read and Grep tools, one simple command per Bash call, and no `cd … &&` chains.
- Waits and stops by pid or pgid only. Do not merge `w2/integrate`.
- Never touch `tests/acceptance/**`, `.tickets/`, `.claude/` or any file outside your paths.
- **Commit** on `w2/W2-92-d6` with
  `--trailer "Task: DAEO-n0wb" --trailer "Implements: DEC-1109" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message**, in full. It holds:
- the twelve labelled fields of `EMG-common.md` (the sandbox and `ps` checks first);
- the commits and unit cases;
- `gov accept W2-92`'s counts per line;
- the probe and the UNMARKED_CHANGE count, before and after;
- every red, named.

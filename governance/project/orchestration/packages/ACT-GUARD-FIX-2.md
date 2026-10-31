# ACT-GUARD-FIX-2 / P1: the inline-code rule judges each part of a command, not the whole (DEC-958)

For the owner. DEC-958's trigger is met: the same false-refusal pattern has occurred four times since 01:21.

## 1. Context
ACT-GUARD-FIX-1 (`c3392f46`) kept one cautious part of rule 1: a Bash command that holds inline interpreter code (`python3 -c`, `perl -e` or `-i`, `node -e`, `ruby -e`) and names the acceptance tests is refused. The write parser cannot see inside inline code. The rule judges the whole command line.

## 2. What happened (`log/guard-refusals.jsonl`; 24 refusals since ACT 1, all false positives)
- **The four refusals:**
  - 01:21, a helper: a read-only `python3 -c` reading the settings, then `ls` of an acceptance folder;
  - 02:40, W2-05's lead: the import check the common brief requires, `python3 -c "import gov; print(gov.__file__)"`, then `ls` of its acceptance folder;
  - 02:42, W2-95's lead: the same import check, then reads of its tests;
  - 02:52, the CTO: a command whose text carried the new planted cases.
- **Why:** the inline code and the acceptance path sat in different parts of the command, `a; b` or `a && b`, and only one part could ever write.
- **Cost:** about 6 minutes so far. Every lead meets this in its first minutes, because the brief asks for the import check.

## 3. Why it matters
Ordinary work hits it in every ticket. It fails closed, so nothing gets through, but it costs time and brief gaps.

## 4. Options
- **(a) Recommended:** judge each simple command alone. The command is split at `;`, `&&`, `||`, `|` and newlines, with quotes kept, so a `;` inside `python3 -c "…"` stays in its part. A part is refused only when it holds inline code and names the acceptance tests itself. A command that cannot be split (unbalanced quotes) is judged whole, as today.
  - **Size:** one file, 25 lines added and 2 removed (`packages/ACT-GUARD-FIX-2.patch`).
  - **Checked:** 54 of 54 planted cases pass on the candidate: ACT-GUARD-FIX-1's 49, plus 5 new ones. The 2 new "allow" cases are tonight's refusals. The 3 new "deny" cases are an inline-Python write into the tests after `cd`, `perl -i` on a test, and unbalanced quotes naming the tests. On the live hook the 2 new "allow" cases fail.
  - **Remaining gap (a Wave 3 row, as ACT-GUARD-FIX-1's):** an inline program that builds the acceptance path from pieces still passes. That needs a deliberate construction.
- **(b) Change the brief instead:** the import check runs on its own line. This is cheaper, but every lead and worker must remember it, and the helper's and my cases would still be refused.
- **(c) Wait:** about 1 minute per lead per refusal.

## 5. Recommendation
**(a), confidence high.** Classification: ordinary work yes; consequence: other (fails closed, costs time).

## 6. What it blocks, and what waiting costs
It blocks nothing. Waiting costs a minute or two per lead, every lead. A lead starts with the fix after `w2/integrate` is merged into its worktree.

## The commands (your operator, in the main tree)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git status --short -- .claude/
git apply governance/project/orchestration/packages/ACT-GUARD-FIX-2.patch
python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py
git add .claude/hooks/pretooluse.py
git commit -m "ACT-GUARD-FIX-2: the inline-code rule judges each part of a command (DEC-958)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-958, DEC-953" --trailer "Role: owner"
```
- `git status --short -- .claude/` must show nothing before `git apply`.
- `guard4_check.py` must end with `PASS` (54 cases).
- **Undo:** `git revert <the commit>`.

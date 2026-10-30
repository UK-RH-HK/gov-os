# ACT-GUARD-FIX-1 / P1: the five-rule hook refuses read-only commands (DEC-958's first package)

For the owner. Your rule DEC-958 asks for a package with a hook fix when false refusals keep happening. Two of its triggers are met: the same pattern has refused four times in an hour, and it stops leads' and reviewers' work.

## 1. Context
ACT 1 (`6c36c7b5`) wired this repository's five-rule hook, `.claude/hooks/pretooluse.py`. Rules 1 and 5 judge Bash commands with the product's parser, `gov.guard.decide._extract_bash_write_targets`. The parser returns `None` for a **read-only** command, a list of write targets otherwise, and a sentinel path inside that list for a write it cannot resolve (`src/gov/guard/decide.py:431`, "or None when the command is read-only").

## 2. What happened
- **The hook reads the parser backwards.** Rule 1 takes `None` as "a command it cannot read", and refuses it if the command names `tests/acceptance/`. Rule 5 takes `None` as unreadable and refuses it outright.
- **The effect, reproduced by planted cases on the live hook:**
  - every role but the test designer is refused **any read-only Bash command that names the acceptance tests**: `ls`, `grep`, and `pytest tests/acceptance/<W2>`, which leads and engineers must run to verify;
  - independent reviewers and auditors are refused **every read-only Bash command**: `git log`, `pytest`, `grep`. The FULL reviews due on W2-05, W2-84, W2-60a, W2-52, W2-67 and W2-16 could not run a single command.
- **Logged** (`log/guard-refusals.jsonl`; 4 refusals, 4 false positives, about 7 minutes lost so far):
  - 21:45, the CTO building a lead brief;
  - 22:35, W2-90's lead running `grep … tests/acceptance/W1-05/conftest.py`;
  - 22:39, W2-64's lead running `grep -rln … tests/acceptance/W1-30/ | head`;
  - 22:39, W2-64's lead running `ls tests/acceptance/W2-54/ tests/acceptance/W1-30/`.
- **Why the 38 planted cases of ACT 1 missed it:** they tested reads only through the Read tool, never a read through Bash.

## 3. Why it matters
- **It fails closed, not open:** nothing unsafe gets through. But it stops the work order DEC-957 sets.
- **Leads cannot verify their tickets by the plain command.** They can work round it with the Read and Grep tools or a script file, at a cost each time.
- **Reviewers and auditors, the QA step, cannot run anything.**
- Every lead now running (W2-87, W2-90, W2-64) and the eight queued will hit it.

## 4. Options
- **(a) Apply the fix now (recommended).** The hook reads the parser as it is written.
  - `None` (read-only) passes.
  - A write the parser cannot resolve, or inline interpreter code (`python -c`, `perl -e`/`-i`, `node -e`, `ruby -e`), is still refused when it names the acceptance tests.
  - A reviewer or auditor is still refused any unresolvable write.
  - **Size:** one file, 15 lines added and 9 removed (`packages/ACT-GUARD-FIX-1.patch`).
  - **Checked:** 49 of 49 planted cases pass on the candidate: ACT 1's 38, plus 11 new. The 7 new "allow" cases are the false refusals: running and listing the acceptance tests, grep through a pipe, a brief build, an auditor's `git log` and `pytest`. The 4 new "deny" cases are writes into the acceptance tests by inline Python, `tee`, `sed -i` and `cp`.
  - **Tests:** no test reads this repository's own hook file (swept), so no test changes. Every permission and setting is unchanged.
  - **Risk:** a write into the acceptance tests that the parser misses and that is not inline interpreter code (for example a script file that writes there) now passes rule 1. Under ADR-0001 that needs a deliberate construction: a Wave 3 hardening row, never a round. The tests' authorship is still checked at review, by the trailers, and by the close.
- **(b) Refuse only for the implementer roles (engineer, product-spec).** This narrows rule 1 to "the implementer", as its own name says. It does not fix rule 5's reviewers, so it must be done together with (a). It is more change for no gain.
- **(c) Wait.** Leads and workers keep working round it with Read, Grep and script files; each refusal costs minutes and a brief gap, and the FULL reviews cannot run. Not recommended.

This changes no Contract item, no standing decision and no permission rule. It restores the five rules as DEC-953 item 2 and DEC-954 state them.

## 5. Recommendation
**(a), confidence high.** Classification of the findings: ordinary work: yes (every lead's verification); consequence: other (fails closed, stops work; nothing fails open).

## 6. What it blocks, and what waiting costs
- **Blocks:** the FULL reviews of six tickets in the queue, and the plain verification command of every lead.
- **Waiting costs:** minutes per lead per refusal now. Once reviews start, a review round is lost each time until the fix lands.
- **Sessions:** running sessions keep the hook they started with, so the fix reaches each lead at its next start.

## The commands (your operator, in the main tree)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git status --short -- .claude/
git apply governance/project/orchestration/packages/ACT-GUARD-FIX-1.patch
python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py
git add .claude/hooks/pretooluse.py
git commit -m "ACT-GUARD-FIX-1: the five-rule hook reads the write parser as written (read-only commands pass; DEC-958)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-958, DEC-953" --trailer "Role: owner"
```
- `git status --short -- .claude/` must show nothing before `git apply`.
- `guard4_check.py` must end with `PASS` (49 cases).
- Stop at the first line that differs, and tell the orchestrator.
- **Undo:** `git revert <the commit>`.

Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-92-d6-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-92 — the independent test designer's brief, D-6 part 2: S11, the register's verbless change labels (DAEO-n0wb)

You are the independent test designer for **W2-92** (`.tickets/DAEO-n0wb.md`: read it, with its new line **S11**,
its new failure line and its "D-6 part 2 placed here" note). W2-92 is merged into `w2/integrate`. Its acceptance tests
are in `tests/acceptance/W2-92/`: read the README first, with its interface and support module. This round adds S11
only. DEC-1109 (2) restarted D-6 part 2. The row comes from the W2-130 sitting (DEC-1098 (3); DECIDED-NOT-DONE row 24:
"the loader's 8 wrong pairs").

## What S11 says, briefly
The public function is `gov.store.loader.register_statements(text, entries=None)`. It returns
`{source, target, cls, form, whole, where}` statements. `gov links` (W2-129) and the store's stated links read it.

S11 covers a change label with no "<verb> ... by" in its value:
- the labels: `**Changed by:**`, `**Amended by:**`, `**Lifted by:**`, `**Superseded by:**`, `**Amended:**`;
- an example: `**Changed by:** DEC-953 (item 3)`.

For such a label, only the ids at the head of its clauses are changers:
- (1) the value ends at ` · ` and at any line break that starts a list item, at any indentation (`\n   - ...`);
- (2) the value splits into clauses at each `;` outside parentheses;
- (3) a clause's head is its text before its first `:` outside parentheses, or the whole clause when it has none;
- (4) the changers are the ids in a head that stand outside parentheses.

An id in the prose after a clause's colon, inside parentheses, or on a sub-item below the label is not a changer.
Labels with a verb, and every other statement form, give what they give today.

**The register shapes it fixes** (the CTO's probe on this repository; the sitting counted 8):
- `**Changed by:** DEC-901: the default is kept ..., replacing its basis DEC-208 and DEC-237, which DEC-838 changed.`
  → only DEC-901.
- `**Changed by:** DEC-917: the three lines take the form of DEC-880 item 3 and DEC-913; the four lines keep this
  entry's form` → only DEC-917.
- `**Changed by:** DEC-882: DEC-843 is superseded in its items 1 and 2 only; its item 3 ... stands; DEC-884: the
  settings ...; DEC-889: ...` → DEC-882, DEC-884 and DEC-889, not DEC-843.
- `**Changed by:** DEC-868 item 3 and DEC-899 (P-IS-4 (a)): the gates refuse at once; "every gate asked; one counted
  refusal" holds only within the regression (marked under DEC-866 from W2-07 run 1).` → DEC-868 and DEC-899, not
  DEC-866.
- `**Changed by:** DEC-953 (item 2)` followed by an indented sub-item `\n   - DEC-723 moves ...` → only DEC-953.
- **Heads that stay:**
  - `DEC-1057 (lifted: no committed record, R-6), DEC-522 (its expiry)` → both;
  - `DEC-900: ...; DEC-899 item 3: ...` → both;
  - `DEC-868 item 3 and DEC-908 (for one part): ...` → both;
  - `DEC-1084 (W2-66b, W2-90c); DEC-1098 (1) (K9's memory line met)` → both.

## What the cases must show (3 to 8 cases; add them first, the engineer then builds)
Use a planted register text, or a planted repository through your support module.
- **The wrong changers gone:** prose after a colon; an id inside parentheses; an indented sub-item. One case each, or
  one parametrised table. The source must not be among the statements whose target is the entry.
- **Heads kept:** several heads split by `;`, and heads joined by `,` and `and` before a colon. Each head yields an
  amend statement, or a supersede statement for `**Superseded by:**`, with target the entry.
- **Unchanged:** a label with a verb (`**Changed by:** amended by DEC-x`) gives what it gives today. Guard it, green.
- **Where it shows:** `gov links --all` in a planted repository no longer reports UNMARKED_CHANGE for a pair made only
  by prose ids. If that is cheap, put it in one case.

Map the cases to **S11** and the new failure line. For each case, say what it expects and whether it is red today:
the "gone" cases red, the guards green. Update the README with S11's line and a note for DEC-1109.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-92-d6-tests`, branch `w2/W2-92-d6-tests`, made from `w2/integrate`
  at `d48639954`. Write only `tests/acceptance/W2-92/`.
- **Your record:** your whole return is your session's **final message**, in full.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):**
  - never open, grep or list `src/gov/store/loader.py`, `src/gov/retrieval/graph_route.py`,
    `src/gov/retrieval/code_route.py`, `tests/unit/store/` or `tests/unit/retrieval/test_w2_92*`, nor the engineer's
    worktree (base name `W2-92-d6`);
  - never run `git show`, `git log -p` or `git diff` on them;
  - you work from the ticket, this brief and the register's text (`docs/DECISION_REGISTER.md`, which you may read).
- **The exclusion line (DEC-1093 (2)):**
  - every recursive grep carries `--exclude-dir=store` and `--exclude=loader.py`;
  - every Grep or Glob call that could reach them carries `!src/gov/store/**` and `!tests/unit/store/**`;
  - keep searches inside your worktree.

  If a search shows you a line of the implementation, stop reading it and say so.
- **Search again once (DEC-1092 (1)).**
- **Planted folders only.** No GPU, model, network or installs.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Run your cases through the heavy slot that `EMG-common.md` names,** with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-d6-tests/src` and a scratch HOME. Then run
  `python3 -m gov.cli.main accept W2-92 --root /home/usain/gov-os-worktrees/W2-92-d6-tests`. Never the full suite.
- **DEC-1080:** use the Read and Grep tools, one simple command per Bash call, and no `cd … &&` chains.
- **Commit** on `w2/W2-92-d6-tests`, only `tests/acceptance/W2-92/`, with
  `--trailer "Task: DAEO-n0wb" --trailer "Implements: DEC-1109" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only.

## Return
- The twelve labelled fields of `EMG-common.md` (the sandbox and `ps` checks first).
- The new cases: node id, KPI line, expectation, red or green today and why.
- The README's changed lines, quoted.
- The commit, `gov accept`'s counts and `TESTS-READY`.
- `discoveries`.

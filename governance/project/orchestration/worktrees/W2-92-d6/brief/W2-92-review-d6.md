Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-92-d6/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-92 — the narrow review of S11, the register's verbless change labels (D-6 part 2; DEC-1109 (2)) (DAEO-n0wb)

You are a fresh, read-only independent reviewer. **Narrow scope: one line, S11,** and its new failure line (failure-6)
in `.tickets/DAEO-n0wb.md`. Read the line, the failure line and the "D-6 part 2 placed here" note. The rest of W2-92
was reviewed READY and merged, and is not re-opened here. READY is computed by `verdict.py` from your block.

S11, briefly: a `**Changed by:**`, `**Amended by:**`, `**Lifted by:**`, `**Superseded by:**` or `**Amended:**` value
with no "<verb> ... by" names as changers only the ids at the head of its clauses:
- (1) the value ends at ` · ` and at any line break that starts a list item, at any indentation;
- (2) clauses split at `;` outside parentheses;
- (3) a head is the text before the clause's first `:` outside parentheses;
- (4) the changers are the ids in a head outside parentheses.

Labels with a verb, and every other form, are unchanged.

## What to review
- **The branch:** `w2/W2-92-d6` in `/home/usain/gov-os-worktrees/W2-92-d6`, head `27d9ecaa3`, made from `w2/integrate`
  at `49885f32b`. Read `git diff 49885f32b..27d9ecaa3`.
  - The designer's cases: `tests/acceptance/W2-92/test_w2_92_verbless_labels.py`, the README's S11 section and
    `w2_92_support.py` (`cc6d5609`, merged at `decf83278`).
  - The engineer's change: `6bc41bbca` (`src/gov/store/loader.py`, `tests/unit/store/`) and `27d9ecaa3`
    (`docs/research/W2-92-memory-measure.md`, the probe before and after).
- **The runs** (the CTO's, outside the sandbox at `27d9ecaa3`, scratch HOME):
  - `gov accept W2-92` 143/1: success-11 28/0, failure-6 27/0.
  - The one red is `test_w2_92_unchanged.py::test_u1_a_question_naming_no_record_or_symbol_gets_todays_bundle[unknown symbol]`
    (success-4 and failure-1). It is **red on the base code too** (the designer's tree at `cc6d5609`, without the
    change): the bundle now holds `governance/project/path-map.yaml`. It is out of S11's scope and goes to D-10's
    list.
  - The engineer's unit run: `tests/unit/store` 67/67.

## Check
1. **The wrong pairs gone, the heads kept:** read the code, not only the tests. On this repository's register,
   compute `register_statements` before (the base loader at `49885f32b`, for example with `git show` into your
   scratch TMPDIR) and after (the branch). List every pair that changed. The CTO's probe expects these to go:
   - DEC-208, DEC-237 and DEC-838 → DEC-281;
   - DEC-880 and DEC-913 → DEC-608;
   - DEC-843 → DEC-880;
   - DEC-891 → DEC-896;
   - DEC-866 → DEC-492;
   - DEC-723 → DEC-728;
   - DEC-775 → DEC-780.

   And these to stay:
   - DEC-900 and DEC-899 → DEC-757;
   - DEC-882, DEC-884 and DEC-889 → DEC-880;
   - DEC-868 and DEC-908 → DEC-455;
   - DEC-1057 and DEC-522 → DEC-511.

   Is any other pair lost or gained? Is any real changer now dropped?
2. **Nothing else moves:** the verb labels, the out-labels, free text and the change log give identical statements
   before and after, on the whole register.
3. **The cut at list items:** could it cut a value too early in an ordinary entry? Consider numbered items, `*` and
   `+`, a line break inside a value, and an unclosed `(`.
4. **Consumers:** `gov links` (UNMARKED_CHANGE) and the store's stated links (AMENDS/SUPERSEDES edges) follow. Is any
   downstream count or edge change unexpected?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding is `scope: in` only if it
concerns S11 or failure-6.

## Write and return
- **You write nothing** in any tree. Scratch files go only in your TMPDIR.
- You may run tests read-only (`-p no:cacheprovider`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-d6/src` and an empty scratch HOME (`PYTHONUSERBASE=/home/usain/.local`).
- No GPU. Single simple Bash commands (DEC-1080).
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- **Search again once (DEC-1092 (1)).**
- **Your record is your session's final message**, in full. It holds:
  - the twelve labelled fields of `EMG-common.md` (the sandbox and `ps` checks first);
  - your answers to checks 1-4, with the before/after pair list;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "S11", "verdict": "pass|fail", "findings": [...]}, {"kpi": "F6", "verdict": "pass|fail", "findings": [...]}]}`,
    each finding `{"id", "scope", "ordinary_work", "consequence"}`.

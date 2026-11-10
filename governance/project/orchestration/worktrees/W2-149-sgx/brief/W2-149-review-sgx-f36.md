Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-149-sgx/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-149 — the narrow review of F36 and F38 closed (DAEO-52ku)

You are a fresh, read-only independent reviewer. **Narrow scope.** The CTO decided (DEC-1112 (3); DEC-1113 (2): the
overlap auditor decides "from the decisions alone", blind) to close two rows of the last review. Both rows are
described in `.gov-runtime/scratch/ref/ACT-W2-149-INSTALL-1/ACT-W2-149-INSTALL-1-review-v3-r1.md` (F38) and
`W2-149-sgx-review-f18.md` (F36):
- **F36:** every dispute's reasons are blanked in what the auditor receives;
- **F38:** the overlap auditor entry's `tree_exclude` leaves out every file that states which side is which labeller's.

Read the ticket's changed lines **S23** and **S27** and its last note. Everything else was reviewed READY and merged;
re-open it only where this change touches it. READY is computed by `verdict.py` from your block.

## What to review
- **The branch:** `w2/W2-149-sgx` at `bdda27d28`. The change is the diff from `9699bbbc9` (`w2/integrate`) to the head.
  - The designer's `be77be65a`.
  - The engineer's `c49799f77` and `bdda27d28` (`indep_launch.py`, the template's `kinds.yaml`, the unit tests, the
    evidence).
- **The runs:** the lead's, at `bdda27d28`, outside the sandbox (13:2x UTC), with `GOV_W2_149_BWRAP=1` and
  `--optin=lifted --optin=breadth`: the acceptance folder (but `live`) and the two unit files, **362 passed, 0 failed**.
  The 3 live cases passed. The designer's red check: 6 red for their stated reasons, none needing `bwrap`.
- **Check:**
  1. **F36:** is every side's `reason` empty in `disputes.jsonl`, with x/y still in the seeded order? Can the auditor
     still tell the sides apart from anything it receives (the `clauses` form, key order, the `rule_class` form, line
     order)? Say what remains, if anything.
  2. **F38:**
     - does the auditor's tree at the merged head still hold any file that states the tell? Search the files that
       survive its exclusions, using the launch script's own exclusion code and the real template entry, for the
       tell's wording (the script's side, class-14, an empty or blanked reason, labeller 1's script);
     - do the labellers' and writers' trees still hold what their briefs need (the packages SANDBOX-GUARD-EXP-1 and the
       declaration, `.tickets/`)?
  3. **No regression:** only the auditor entry changed in `kinds.yaml`; S1-S22, S24-S26 and S28-S31 hold; the revised
     cases weaken nothing.

## Judgement and return
- `governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …`
  and `Consequence: fails open|loses work|other`. Mark it `scope: in` only if it concerns F36's or F38's fix.
- **You write nothing in any tree.** You may run the tests read-only through the heavy slot that `EMG-common.md`
  names. No real `claude` session, GPU or network. Single simple Bash commands. The hidden-half rule holds. Read the
  template folder with the Read tool only, never naming it in a Bash line, and name no git revision range in a Bash
  line beyond one `git diff`.
- **Your record is your final message:**
  - the twelve labelled fields of `EMG-common.md`, each a single-line labelled field, with the sandbox and `ps` checks
    first;
  - checks 1-3;
  - the findings (ids from F40);
  - the fenced `verdict` block:
    `{"kpis": [{"kpi": "S23", "verdict": "pass|fail", "findings": [...]}, {"kpi": "S27", "verdict": "pass|fail", "findings": [...]}]}`,
    with each finding `{"id", "scope", "ordinary_work", "consequence"}`.

Refused twice for the same call: stop and say so.

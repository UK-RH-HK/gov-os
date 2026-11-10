# ACT-W2-149-INSTALL-1, fourth build — the independent review of an ACT package (one round; READY by verdict.py)

You are a fresh, read-only independent reviewer, and not the ACT's author. Review the **fourth build of
ACT-W2-149-INSTALL-1**. The third build was reviewed READY (`ACT-W2-149-INSTALL-1-review-v3-r1.md`, beside the
package). Then the CTO closed F36 and F38 (DEC-1112 (3); DEC-1113 (2)):
- every dispute reason is blanked for the overlap auditor;
- its tree also leaves out the ticket files, the packages, the launch script, and W2-149's tests and evidence.

These are merged at `2f98aecbc` (narrow review READY: `W2-149-sgx-review-f36.md`, row F40). The launch script (now
`90b943aef8be…`) and the template's `kinds.yaml` line (now `ddd84ae25910…`) changed, so `freeze.py` and `rehearse.sh`
rebuilt the list, `apply.sh`'s pins and the rehearsal.

Everything is in your worktree under `.gov-runtime/scratch/ref/ACT-W2-149-INSTALL-1/`:
- the package `ACT-W2-149-INSTALL-1.md`. Read it in full. `@SHA8@` and `@REVIEW@` are filled after this review;
- `drafts/` (this build) and `drafts-v3-reviewed/` (the third build's);
- the references and reviews.

The tree is `w2/integrate` at `2f98aecbc`. Read the template with the Read tool only, never naming its folder in a Bash
line.

## Check (each a KPI line of your verdict block)
- **K1** the touched set is exact.
- **K2** the list is right: the before list with exactly the two template lines changed (`kinds.yaml` now
  `ddd84ae25910…`), the comments naming `90b943aef8be…` at `2f98aecbc`, the seven brief lines; the parser reads 6
  template lines and 7 brief lines. Does §1 state the auditor's wider exclusion, which the yes approves?
- **K3** the undo is real.
- **K4** the rehearsal is real: `rehearsal.log` (`7d25071d1b5f`), 0 failures, the five briefs pass stage 10 and build
  dry walls.
- **K5** the order holds: `check` refuses unless the script, `kinds.yaml` and `tree-exclude.txt` are this build's.
- **K6** the class.
- **K7** the account is true: §3 on F36 and F38 closed, on what remains, and on F37 and F40; §8 item 1.
- **K8** independence: at `2f98aecbc`, does the overlap auditor's dry-built tree hold any file that states which
  dispute side is which labeller's? Search it with the launch script's own exclusion code and the real template, and
  fold line breaks. Do the labellers' and writers' trees still hold what their briefs need?
- **The diff from the third build:** compare `drafts/` with `drafts-v3-reviewed/`. Name every change.

## Judgement and return
- `governance/project/briefs/JUDGEMENT.md`, word for word, with the two lines on every finding, and `scope: in` only
  for this ACT's change.
- **You write nothing in any tree.** Run `apply.sh` and the launch script only in your own temporary clone, with a
  planted HOME and a planted sets root: never the real sets root, never the main tree. No real `claude` session, GPU or
  network. Single simple Bash commands. The hidden-half rule holds.
- **Your record is your final message:**
  - the twelve labelled fields of `EMG-common.md`, each a single-line labelled field, with the sandbox and `ps` checks
    first;
  - K1-K8 and the diff;
  - the findings (ids from F41);
  - the fenced `verdict` block:
    `{"act": "ACT-W2-149-INSTALL-1", "class": "a|b|O", "apply_sh_sha256": "<sha256 of drafts/apply.sh>", "kpis": [{"kpi": "K1", "verdict": "pass|fail", "findings": [...]}, ... "K8"]}`.

Refused twice for the same call: stop and say so.

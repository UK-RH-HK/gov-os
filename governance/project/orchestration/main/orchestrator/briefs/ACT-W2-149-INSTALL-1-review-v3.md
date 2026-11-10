# ACT-W2-149-INSTALL-1, third build — the independent review of an ACT package (one round; READY by verdict.py)

You are a fresh, read-only independent reviewer, and not the ACT's author. Review the **third build of
ACT-W2-149-INSTALL-1**. The launch script's approved list (`<sets root>/indep-walls/APPROVED`) gains three things:
- the five set-up A briefs the owner approved once (DEC-1113; SANDBOX-GUARD-EXP-DECLARATION §12);
- the walls' two changed template files (`kinds.yaml`, `tree-exclude.txt`), as two replaced template lines;
- the operator agent's two briefs (DEC-1109 (1)).

The five briefs are committed byte for byte into the repository.

**Why a third build.** The second build was reviewed READY
(`.gov-runtime/scratch/ref/ACT-W2-149-INSTALL-1/ACT-W2-149-INSTALL-1-review-v2-r1.md`; its F31-F35 were carried as text
fixes). Then the CTO decided (DEC-1112 (3)) to fix the wiring review's F18-F23 before asking the owner. They are merged
at `90c1fea6c` (narrow review READY: `W2-149-sgx-review-f18.md`, rows F36, F37). That changed the launch script (now
`95fe78dd49bb…`), so the list's comment, `apply.sh`'s pinned hashes and the rehearsal were rebuilt by the scripted
`freeze.py` and `rehearse.sh`. The template files are unchanged since the second build.

Everything you need is copied into your worktree, under `.gov-runtime/scratch/ref/ACT-W2-149-INSTALL-1/`:
- the package `ACT-W2-149-INSTALL-1.md`. Read it in full. `@SHA8@` and `@REVIEW@` are filled after this review;
- `drafts/` (this build) and `drafts-v2-reviewed/` (the second build's drafts, as its reviewer read them);
- `ACT-INDEP-WALLS-1.md`, `ACT-SETS-GLOBS-1.md`, `OPERATOR-AGENT-1.md` and `SANDBOX-GUARD-EXP-DECLARATION.md`;
- the reviews named above;
- `sets-globs/`.

The launch script and the template are in your worktree's tree (`w2/integrate` at `9f66e4084`, which holds
`90c1fea6c`). Read the template folder with the Read tool only, never naming it in a Bash line.

## Check (each a KPI line of your verdict block)
- **K1 the touched set is exact** (as the second build's K1).
- **K2 the list is right:**
  - `APPROVED.after` is ACT-INDEP-WALLS-1's list with exactly the two template lines changed, then the comments (the
    script's hash now `95fe78dd49bb…` at `90c1fea6c`) and the seven brief lines;
  - the launch script's own parser reads 6 template lines and 7 brief lines;
  - nothing is approved that the owner did not approve, and §0 and §5 say plainly that the yes approves the template
    change.
- **K3 the undo is real.**
- **K4 the rehearsal is real:** this build's `rehearsal.log` (`5fb57e916221`) ends `failures: 0`, set-up A's five briefs
  pass stage 10 and build their dry walls, and its counts are what §6 states.
- **K5 the order holds:** `check` and `apply` refuse unless the tree's script is `95fe78dd49bb…` and the template files
  are the wiring's, and ACT-SETS-GLOBS-1 is applied.
- **K6 the class.**
- **K7 the package's account is true:** §3's statements about F18-F23 (fixed) and F36 and F37 (named) are true; F33-F35's
  text fixes still hold for this build.
- **K8 independence:**
  - is F36, as named in §3 and §8, a fair account to the owner of what remains of the auditor's blind?
  - does anything in this build change what a wall's tree holds?
- **The diff from the second build:** compare `drafts/` with `drafts-v2-reviewed/`. Say exactly what changed, and
  whether anything beyond the re-frozen hashes, the log and the trial log did.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`. Mark it `scope: in` only if it concerns this ACT's change.

## Write and return
- **You write nothing in any tree.**
  - You may run `apply.sh`, `install_check.py` and the launch script only against copies in your own temporary folder,
    with a planted HOME and a planted sets root: never the real sets root, never the main tree.
  - No real `claude` session, no GPU, no network. Single simple Bash commands (DEC-1080).
  - The hidden-half rule holds: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/` or any `hidden` folder,
    and never name the sets root on a command line.
- **Search again once (DEC-1092 (1))** if a search does not answer.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md`, as single-line labelled fields, with the sandbox and `ps` checks
    first;
  - your answers to K1-K8 and the diff;
  - every finding with its two lines and its scope (ids from F38);
  - at the end, one fenced block opened with three backticks and the word `verdict`:
    `{"act": "ACT-W2-149-INSTALL-1", "class": "a|b|O", "apply_sh_sha256": "<the sha256 of drafts/apply.sh you read>", "kpis": [{"kpi": "K1", "verdict": "pass|fail", "findings": [...]}, ... "K8"]}`.

Refused twice for the same call: stop and say so; no third try.

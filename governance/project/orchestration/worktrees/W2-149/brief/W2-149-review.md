Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-149/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-149 — the independent review (DAEO-52ku), round 1

You are a fresh, read-only independent reviewer. Review **W2-149** (`.tickets/DAEO-52ku.md`: read it in full, with its
body's "Readings settled by the CTO"): the independent sessions' launch script, which builds one walled folder per job
(writer, checker, auditor, labeller) from an owner-approved brief and template, chooses the content by rule from a seed
recorded first, guards the wall's settings with a canary, starts one closed headless `claude -p` session in it,
delivers its product by its own code and returns only counts (the owner's DEC-1101 (2)-(3) step 2, DEC-1109 (2)). The
specification is `.gov-runtime/scratch/ref/LAUNCH-SPEC.md` in the worktree (§1 to §5), with the ticket's reading 1
correcting its canary. Profile FULL. This script decides what an independent session sees and what reaches the CTO: a
check that fails open, or free text that leaks to the CTO, is the fault that matters most.

## What to review
- **The branch:** `w2/W2-149` in `/home/usain/gov-os-worktrees/W2-149`, head `8d4569bfef3c`, against `w2/integrate`
  (`git diff w2/integrate...w2/W2-149`): `governance/project/orchestration/tools/indep_launch.py`,
  `governance/project/orchestration/tools/indep-schemas/`, the engineer's unit tests
  `tests/unit/orchestration/test_w2_149*`, the designer's cases `tests/acceptance/W2-149/` (and their README's
  interface), `docs/changes/W2-149-evidence.md`.
- **The runs:** the CTO's `gov accept W2-149` outside the sandbox: **77 passed, 0 failed, 3 skipped (live)**; the three live cases run by the CTO outside the sandbox (`GOV_W2_149_LIVE=1`, model haiku, planted sets root, runs and trees, the real HOME for the login): **3 passed** (S9 live: the real canary refused with valid settings, and with `hooks.PreToolUse` corrupted not refused, code 16, no session; S11: every outside Read refused, its brief and tree read, no marker out, nothing written outside `out/`; S12: 0 traces by session id). The engineer's: unit `tests/unit/orchestration/test_w2_149_indep_launch.py` 64 passed.
- The walls' template it builds from: `governance/project/indep-walls/` (read its files with the Read tool; the
  guard's line rule refuses a Bash line naming that folder next to a path) and `ACT-INDEP-WALLS-1.md` under
  `governance/project/orchestration/packages/`.

## Check, against each KPI line S1 to S21 and the ten failure lines
- **Every refusal fails closed:** for each code (10 to 17, 20 to 22), can an exception, a missing or malformed input
  (APPROVED, the brief's front matter, `kinds.yaml`, the path map, `AUDITS.log`, the session's JSON), an unreadable
  file or a timeout ever be read as a pass, or let the build go on? Read each check's code path, not only its test.
  After every refusal, can a later run build into what was left?
- **The approved bytes (S1, S2):** are the brief and the template read from git at `--commit` and hashed before any
  write; can a working-tree file, a different path spelling, a second `brief` line or a comment line pass?
- **The seed and the content (S4 to S6, S20):** can content be chosen, or a tree or input file written, before the seed
  and its ledger line; can the caller steer the selection (an argument, an environment variable, `AUDITS.log` written
  by hand, a commit off the main line)?
- **The tree (S7):** links, submodules, `..` and absolute members; the exclusions applied to files and folders; modes.
- **The canary (S9, reading 1):** is its target inside a folder only the canary's command adds, and outside the wall,
  its tree and every root above, so `--restricted` alone would allow the Read; does anything but a `Read` of exactly
  that target in `permission_denials` refuse; do garbage, a timeout and an error refuse?
- **The session (S10, S15, S21):** the flags against the ticket, flag by flag; the environment exactly `HOME PATH LANG
  USER`; tools, budget, timeout and model never from the caller; the stop by process group, the waits by pid; no name
  match anywhere.
- **Only counts (S13):** can any string from `out/`, the session's JSON or a file name under the wall reach
  `counts.json`, stdout, stderr or `launch.log`? Is every schema object closed and every string an enum, a const or an
  anchored pattern?
- **The delivery (S14, S16, S17):** all or nothing; only the kind's destination; packed to one file; writer round 2.
- **The CTO's reading to judge (in scope or not):** the destinations of LAUNCH-SPEC §4 are hidden from the guarded
  roles only where the path map's `sets_root_hidden` names them. Today it names `memory-retrieval/hidden/**` and
  `sandbox-guard-exp-1/hidden/**` but not a new set's `fixtures/evaluation/<set>/hidden/`, the checker's
  `XCHECK-r<round>.md` or `runs/<audit>/miss-classes.json`. Say whether the script itself should refuse a destination
  that no hidden glob covers (a fail-open in this ticket), or whether it is the path map's (an ACT outside it).
- **Nothing live by default (failure line 10):** does any default path make a test write a real place when an override
  or a planted HOME is left out?
- **S19:** do the documented lines pass the tree's guard hook as the orchestrator, and the same with `indep-walls/...`
  refuse?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **You write nothing** in any tree. Run nothing that writes outside your own temporary folder. You may run the tests
  read-only (with `-p no:cacheprovider`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149/src`. Never run anything against the real `~/gov-os-eval/`,
  `~/gov-os-runs/`, `~/gov-os-wall-trees/`, `~/.claude/` or a real `claude` session. No GPU. Single simple Bash
  commands (DEC-1080). The hidden-half rule holds: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder of a real tree.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own, different words;
  then answer from both, with path and lines, or say "not found".
- **Your record is your session's final message**, in full (the launcher keeps it in this worktree's log; the CTO
  transcribes it): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), your verdict per
  line, every finding with its two lines and `scope: in|out`, and at the end the fenced `verdict` block:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "S21"]}`.

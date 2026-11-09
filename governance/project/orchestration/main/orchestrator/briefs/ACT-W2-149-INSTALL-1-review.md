# ACT-W2-149-INSTALL-1 — the independent review of an ACT package (one round; READY by verdict.py)

You are a fresh, read-only independent reviewer. You are not the ACT's author. Review **ACT-W2-149-INSTALL-1**: the
launch script's approved list (`<sets root>/indep-walls/APPROVED`) gains the five set-up A briefs the owner approved
once (DEC-1113; SANDBOX-GUARD-EXP-DECLARATION §12) and the operator agent's two (DEC-1109 (1)), and the five briefs are
committed byte for byte into the repository, where the launch script reads them at `--commit`. It is built to apply
after W2-149's F11 follow-up is merged and after ACT-SETS-GLOBS-1 is applied.

Everything you need is copied into your worktree, under `.gov-runtime/scratch/ref/ACT-W2-149-INSTALL-1/`:
- `ACT-W2-149-INSTALL-1.md` (the package: read it in full), `ACT-SETS-GLOBS-1.md`, `ACT-INDEP-WALLS-1.md` (the list as
  first written), `OPERATOR-AGENT-1.md` (§2 classes, §5 what stays the owner's), `LAUNCH-SPEC.md`,
  `SANDBOX-GUARD-EXP-DECLARATION.md` (§12 the approved hashes) and the sandbox experiment's `README.md` (what set-up A
  asks of the launch script);
- `drafts/`: `apply.sh`, `freeze.py`, `install_check.py`, `rehearse.sh`, `rehearsal.log`, `APPROVED.before`,
  `APPROVED.after`, `briefs/` (the five);
- `sets-globs/`: ACT-SETS-GLOBS-1's drafts (`apply.sh`, the candidate hook and map), as the rehearsal applied them first.
The launch script is in your worktree's tree (`governance/project/orchestration/tools/indep_launch.py`, `w2/integrate`
with the F11 follow-up merged), with its template `governance/project/indep-walls/` (read it with the Read tool only,
never naming it in a Bash line) and the operator's briefs `governance/project/operator/brief.md`, `reviewer-brief.md`.

## Check (each a KPI line of your verdict block)
- **K1 the touched set is exact:** `apply.sh apply` writes only the five brief files under
  `governance/project/indep-briefs/sgx1/` (each byte for byte the approved brief: compute the sha256s against §12) and
  `<sets root>/indep-walls/APPROVED` (0400), plus its own `backup/`; it reads nothing else under the sets root; the
  operator's commit holds exactly the five files.
- **K2 the list is right:** `APPROVED.after` keeps ACT-INDEP-WALLS-1's six template lines byte for byte as its head, and
  adds the comment and seven `brief <kind> <path>` lines; the launch script's own `parse_approved` reads 6 template and 7
  brief lines; each line's kind is the brief's front-matter `kind` (or `operator`, which no launch accepts); no line
  approves anything the owner did not approve.
- **K3 the undo is real:** `apply.sh undo` puts the list back byte for byte (`331e48fa…`) from a checked backup and
  removes only the five files; the rehearsal shows it.
- **K4 the rehearsal is real:** the log is a run of this `apply.sh` in a clone with a planted HOME and sets root, ends
  `failures: 0`, and its counts are what the package states; say where it differs from the live run.
- **K5 the order holds:** `check`/`apply` refuse before ACT-SETS-GLOBS-1 is applied and before the F11 merge (read
  `order_ok`); the package states the order; nothing here breaks if W2-141's hook (rebuilt on ACT-SETS-GLOBS-1's) lands
  later.
- **K6 the class:** by OPERATOR-AGENT-1 §2 and §5, the class you find, whatever the package claims, with the reason.
- **K7 the package's finding is true:** the five approved briefs cannot launch through the merged script today (stage 10:
  front matter without `model` and `result_schema`, and without `sample` for the labellers and the auditor; the
  labellers' rounds, the overlap auditor's inputs and the deliveries' names unbuilt). Read `build_and_run` and
  `plan_inputs`. Say whether applying this ACT before the wiring follow-up does any harm, and what it does not do.
- **K8 independence:** committing the briefs into the repository puts them in every worktree and, unless excluded, in
  every wall's tree (`git archive` less `tree-exclude.txt`). Does any brief there let one independent session see what
  its brief says it must not (the labellers' blindness to each other, the held-out writer and the tuner)? Is the
  package's residual on it right?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this ACT's change.

## Write and return
- **You write nothing** in any tree. You may run `apply.sh`, `install_check.py` and the launch script only against
  copies you make in your own temporary folder with a planted HOME and a planted sets root (never the real one, never
  the main tree), and the tests read-only through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with
  `PYTHONPATH=<your worktree>/src` and an empty scratch HOME (`PYTHONUSERBASE=/home/usain/.local`). No real `claude`
  session, no GPU, no network. Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything
  under `~/gov-os-eval/`, `~/gov-os-runs/` or any `hidden` folder, and never name the sets root on a command line.
- **Search again once (DEC-1092 (1))** if a search does not answer.
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (task,
  status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action; sandbox and `ps` checks first), your answer to K1-K8, every finding with its two lines and
  scope (ids F1, F2, …), and at the end one fenced block opened with three backticks and the word `verdict`:
  `{"act": "ACT-W2-149-INSTALL-1", "class": "a|b|O", "apply_sh_sha256": "<the sha256 of drafts/apply.sh you read>", "kpis": [{"kpi": "K1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "K8"]}`.
Refused twice for the same call: stop and say so; no third try.

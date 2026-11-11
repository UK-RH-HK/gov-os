# The review of ACT-LOAD-BALANCER-A: the dispatcher's launcher checks the resource gate and registers each lead (DEC-1133 (3))

You are a fresh, read-only independent reviewer of an ACT before it goes to the owner for a yes and then to the
operator (class (b); DEC-1104 (2): rehearsal, a READY review and matching hashes). READY is computed by `verdict.py`
from your block.

## The ACT
- **The package:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-a/ACT-LOAD-BALANCER-A.md`
  (read it whole; sections 4, 6, 8 and 9 matter most).
- **The bundle:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-a/acts/ACT-LOAD-BALANCER-A/`
  (`apply.sh`, `list.txt`, `manifest.json` sha256 `0b40f1bfd84b65d043a7e7e2599d0717139461885f8f73462a3f24751b7a8e5f`,
  `rehearsal.log`, `before/`, `after/`); the rehearsal script `.../drafts/act-a/tools/rehearse.sh`.
- **The one live file:** `governance/project/orchestration/tools/dispatch/launch_now.sh` (the committed launcher the
  dispatcher runs for every lead). Sources: DEC-1133 (3), DEC-1105, DEC-1073 (pids only), DEC-898, DEC-1008 item 5,
  `governance/project/orchestration/packages/LOAD-BALANCER-1.md` §3.
- **The prerequisite has landed:** the companion test change (a stand-in `gov` in the two launcher test beds) is merged
  into `w2/integrate` as `792b92923` (`git show 792b92923^2`; `drafts/act-a/companion-tests.diff` was its plan).

## Check
1. **Hashes and scope:** `before/` equals the live `launch_now.sh` on `w2/integrate` today; `after/` differs only by the
   gate check, the registration and their refusal words, before an unchanged `exec` line; recompute every hash in the
   package, `list.txt` and `manifest.json`.
2. **Fail closed and nothing lost:** a shut gate, a missing or failing `gov`, or a failed registration stops the start
   (exit 3 `LAUNCH_GATE_SHUT`, exit 4 `LAUNCH_NOT_REGISTERED`) with nothing started and nothing registered; the
   registered pid is the lead's own (the `exec` keeps it); no wrapper, background job or `wait`, so a stop by pid or
   process group still reaches the lead; nothing matches a process by name. Can an honest lead start ever be lost
   silently (section 9's "started but never ran" item: is it raised, and is the reason findable)?
3. **The four manifest checks,** each run as written with `bash -c` from a clone's root: 0 to 3 exit 0 on the after
   copy with the companion merged; checks 1 and 2 red on the before copy; check 3 green now that `792b92923` is in.
4. **The companion's effect:** with the ACT applied in a clone of today's `w2/integrate`, the 30 launcher tests
   (`tests/unit/launch/test_w2_153_template.py`, `tests/acceptance/W2-153/test_w2_153_dispatch.py`) are green, and green
   on the old launcher too; through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
   `-p no:cacheprovider -o tmp_path_retention_policy=failed`, `PYTHONUSERBASE=/home/usain/.local` if HOME is empty.
5. **Class and route:** `governance/project/operator/class-rules.yaml` row `watchers` gives (b); the operator applies it
   on the owner's `yes ACT-LOAD-BALANCER-A 0b40f1bf`. Right? Is the undo (`apply.sh undo`, byte for byte, only from the
   after state) safe while leads run?
Never run the live launcher, the dispatcher, a real claude session or `gov resources --register` against the real
`~/.gov-os`; a planted HOME and the package's reading overrides (`GOV_RESOURCES_*`) only.

KPI id for the verdict block: `act-load-balancer-a`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this ACT.

## Write and return
- **You write nothing** in any tree; never the live launcher.
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080). Every wait by pid only
  (`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`).
  Row W2-L423's rule: under `.gov-runtime/`, commit hashes as 12 digits and none of that rule's keywords.
- Scratch budget 30 GB and 2,000,000 files and folders, in your own TMPDIR; remove your clone; report `du -sh` and
  `du -s --inodes` in `evidence`.
- The hidden-half rule holds: never open anything under `~/gov-os-eval/`, or any `hidden`, `memory-verdict` or
  `memory-verdict-2` folder.
- Refused twice for the same call: stop and say so; no third try.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields first (task, status, work_completed, files_changed, evidence, tests, discoveries, risks,
    lessons, proposed_decisions, unresolved, recommended_next_action), the sandbox and `ps` checks in `evidence`;
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - then `REVIEW_MD_BEGIN`, a review record in markdown for `review.md`, `REVIEW_MD_END`;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "act-load-balancer-a", "verdict": "pass|fail", "findings": [...]}]}`, each finding
    `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 25 minutes.

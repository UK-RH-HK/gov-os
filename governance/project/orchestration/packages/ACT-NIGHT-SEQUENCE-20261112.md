# ACT-NIGHT-SEQUENCE-20261112: four ACTs by hand tonight, in one order, before the nightly (the owner, chat, 2026-11-12 ~01:50)

**For:** the owner's operator, by hand (the operator agent does not run 01:00-08:00). About 10 minutes in the main tree,
all four done before 03:00 UTC (the landing hold) and well before the nightly at 04:00.

**The four, in this order** (no two touch the same file; each `apply.sh` checks only its own files, so none holds another):

| # | ACT | Files | Manifest | Review |
|---|---|---|---|---|
| 1 | ACT-LOAD-BALANCER-A (option 2, by hand) | `governance/project/orchestration/tools/dispatch/launch_now.sh` | `0b40f1bf` | READY (`reviews/ACT-LOAD-BALANCER-A-review.md`) |
| 2 | ACT-DISPATCH-1 | `dispatch/dispatcher.py`, `dispatch/balancer.py`, `tests/unit/orchestration/test_dispatcher.py`, `test_balancer.py` | `a20754dd` | READY for its line (`reviews/ACT-DISPATCH-1-review.md`) |
| 3 | ACT-IDLE-GUARD-2 (round 2) | `governance/project/orchestration/tools/stop_idle_check.py`, `tests/unit/orchestration/test_stop_idle_check.py` | `a3fe076c` | READY (`reviews/ACT-IDLE-GUARD-2-review-r2.md`); F3 stays a row |
| 4 | ACT-CLAUDE-COPIES-4 | 19 files: `.claude/templates/role-*.md` x7, `.rulesync/subagents/*.md` x6, `.claude/agents/*.md` x6 | `6ab06e85` | READY (`reviews/ACT-CLAUDE-COPIES-4-review.md`) |

**Not tonight, by the owner's word:** ACT-CLAUDE-COPIES-5 (`e602d596`) applies only after W2-11 merges (its before state is
W2-11's bytes; applied first it costs four merge conflicts), and W2-11 merges only after the owner's CAP-33 approval of
its K3 CIT-P, which the owner reads in the morning. ACT-4 tonight keeps the order right: it must precede W2-11's merge.

**Why this order:** ACT A and ACT-DISPATCH-1 are both dispatcher files but different ones, and the cron tick reads its files
whole each minute, so either order is safe; ACT A first because it is the oldest yes. ACT-IDLE-GUARD-2 is the Stop hook,
independent. ACT-CLAUDE-COPIES-4 last: the largest, and the CTO then lands W2-175 on it (S6, CIT-P §4-5 ACCEPTED, merge
and close, by the queue, before 03:00 if time allows, else after the nightly's start).

**The CTO's freeze:** `.gov-runtime/scratch/orchestrator/log/act-in-progress.txt` names these paths; the CTO makes no
commit on `w2/integrate` until the owner says "done", so the main tree stays clean for each `git status` check.

## The yes lines (the owner sends them in the chat first)

```
yes ACT-LOAD-BALANCER-A 0b40f1bf
yes ACT-DISPATCH-1 a20754dd
yes ACT-IDLE-GUARD-2 a3fe076c
yes ACT-CLAUDE-COPIES-4 6ab06e85
```
(ACT A's yes was given at 23:38 and stands; repeated here so the four are in one place.)

## The message for the owner's operator

> **Four ACTs by hand, in this order, in the main tree. Stop at the first step that does not show what is expected, send
> that line to the CTO, and apply nothing further.**
>
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> test -z "$(git status --porcelain)" && test ! -e .git/MERGE_HEAD && echo clean      # expect: clean
> ```
>
> **1. ACT-LOAD-BALANCER-A** (the launcher checks the resource gate and registers each lead; DEC-1133 (3))
> ```
> A=.gov-runtime/scratch/orchestrator/acts/ACT-LOAD-BALANCER-A
> sha256sum $A/manifest.json     # expect 0b40f1bfd84b65d043a7e7e2599d0717139461885f8f73462a3f24751b7a8e5f
> bash $A/apply.sh check         # expect: state before (sha256 03b93044ff98)
> bash $A/apply.sh apply         # exit 0
> bash $A/apply.sh verify        # exit 0
> git diff --name-status         # expect exactly one M: governance/project/orchestration/tools/dispatch/launch_now.sh
> git commit -m "ACT-LOAD-BALANCER-A: the dispatcher's launcher checks the resource gate and registers each lead (DEC-1133 (3))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1133, DEC-1105" --trailer "Role: owner" -- governance/project/orchestration/tools/dispatch/launch_now.sh
> ```
> (The agent's frozen copy `~/gov-os-operator/acts/ACT-LOAD-BALANCER-A-0b40f1bfd84b` may stay; it was never applied.)
>
> **2. ACT-DISPATCH-1** (the dispatcher enforces the lead cap, one idle item per cause, a held slot counted by its measured load)
> ```
> A=.gov-runtime/scratch/orchestrator/acts/ACT-DISPATCH-1
> sha256sum $A/manifest.json     # expect a20754dd1e9f88db984a467d65bfb2b346e7c94d61cd00b520bca99ac8351070
> bash $A/apply.sh check         # exit 0 (all four files as frozen)
> bash $A/apply.sh apply         # exit 0
> bash $A/apply.sh verify        # exit 0
> git diff --name-status         # expect exactly four M: dispatch/dispatcher.py, dispatch/balancer.py, test_dispatcher.py, test_balancer.py
> git commit -m "ACT-DISPATCH-1: the dispatcher enforces max_leads, sends one idle item per cause (reminder after 6 h), counts a held slot by its measured load (DEC-1140 (1)(a), (2))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1140, DEC-1118" --trailer "Role: owner" -- governance/project/orchestration/tools/dispatch/dispatcher.py governance/project/orchestration/tools/dispatch/balancer.py tests/unit/orchestration/test_dispatcher.py tests/unit/orchestration/test_balancer.py
> ```
>
> **3. ACT-IDLE-GUARD-2** (the idle check leaves out a returned lead's line and merged tickets, keeps claimed ones, cuts a slow plan at 5 s)
> ```
> A=.gov-runtime/scratch/orchestrator/acts/ACT-IDLE-GUARD-2
> sha256sum $A/manifest.json     # expect a3fe076cf3339f5da0fcd54462f8270467d731d08805215b394f66c725737422
> bash $A/apply.sh check         # exit 0 (both files as frozen)
> bash $A/apply.sh apply         # exit 0
> bash $A/apply.sh verify        # exit 0
> git diff --name-status         # expect exactly two M: stop_idle_check.py and test_stop_idle_check.py
> git commit -m "ACT-IDLE-GUARD-2: the idle check leaves out a returned lead's line and merged plan tickets, and cuts a slow plan at 5 s (DEC-1140 (2); ACT-IDLE-GUARD-1 review F1-F3)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1140, DEC-1110" --trailer "Role: owner" -- governance/project/orchestration/tools/stop_idle_check.py tests/unit/orchestration/test_stop_idle_check.py
> ```
>
> **4. ACT-CLAUDE-COPIES-4** (the 19 generated copies of W2-175's approved 1.0.1 role templates; DEC-1139)
> ```
> G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-4
> sha256sum $G/manifest.json      # expect 6ab06e85cae2d566c9da540c9ef0ec60c9edc366b6d5e5ccb7401a7d6d99fd17
> bash $G/apply.sh check && bash $G/apply.sh apply
> F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 19
> git commit -m "ACT-CLAUDE-COPIES-4: the .claude/templates role copies, the six .rulesync/subagents sources and the six .claude/agents for W2-175's 1.0.1 templates (19 files)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1139, DEC-1116" --trailer "Role: owner"
> ```
>
> ```
> git status --porcelain          # expect empty
> git log --oneline -4            # the four commits, in this order
> ```
> Then tell the CTO "done" (the CTO lifts its freeze, runs the landing checks and lands W2-175).
>
> **Undo, any one:** `bash <its bundle>/apply.sh undo`, then commit the same paths with the subject `<ACT> undone` and
> `--trailer "Role: owner"`. Undo in reverse order if more than one.

## After "done" (the CTO)
End the freeze (`mv` the act-in-progress file); a landing check after each of the four commits (the scoped selection for
the changed paths); the first dispatcher pass shows `lead cap:` waits and "N of them at their measured load" in its
status; W2-175: merge integrate into `w2/W2-175`, S6 (expect 254 passed, 0 failed), CIT-P §4-5 ACCEPTED (DEC-1139), land
by the queue and close; the morning: W2-11's CIT-P to the owner, then W2-11's hand merge and ACT-CLAUDE-COPIES-5.

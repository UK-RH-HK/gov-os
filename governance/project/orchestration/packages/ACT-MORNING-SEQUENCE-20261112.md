# ACT-MORNING-SEQUENCE-20261112: every by-hand ACT of the morning, in one order (the owner, chat, 2026-11-12 ~02:40)

**For:** the owner's operator, by hand, in the main tree, from 08:00 UTC. It replaces ACT-NIGHT-SEQUENCE-20261112 (not run: the
owner called off the night's operator run). **Part 1** is eight ACTs, about 20 minutes. **Part 2** is two ACTs after the CTO's
hand merges (W2-11, W2-175, W2-176), about 5 minutes. Each `apply.sh` checks only its own files, so no ACT holds another; where one
must follow another, its `check` refuses until the earlier one is in (named below).

**Before Part 1:** tell the CTO "starting". The CTO then writes `log/act-in-progress.txt` (no commit on `w2/integrate`, the merge
queue held) so `git status` stays clean between steps; the CTO lifts it at your "done".

| # | ACT | Files | Manifest | Review | Order rule |
|---|---|---|---|---|---|
| 1 | ACT-LOAD-BALANCER-A (option 2) | `dispatch/launch_now.sh` | `0b40f1bf` | READY | none |
| 2 | ACT-CLAUDE-COPIES-4 | 19 files under `.claude/` and `.rulesync/subagents/` | `6ab06e85` | READY | before W2-11's merge |
| 3 | ACT-DISPATCH-1 | `dispatch/dispatcher.py`, `balancer.py` and their two unit tests | `a20754dd` | READY (F2 for you) | none |
| 4 | ACT-IDLE-GUARD-2 (round 2) | `tools/stop_idle_check.py` and its unit test | `a3fe076c` | READY | none |
| 5 | ACT-EXAMIN-SETS-1 (round 2) | `governance/project/path-map.yaml`; step 2 the sets root's own map | `e8020292` | READY | first of the path-map chain |
| 6 | ACT-ACCEPTED-REDS-1 (round 2) | `governance/project/path-map.yaml` | `b8df21d8` | READY | after 5 |
| 7 | ACT-PATHMAP-EXP-1 | `governance/project/path-map.yaml` | `9a945c99` | READY | after 6 |
| 8 | ACT-OPERATOR-HOURS-2 (round 2) | the operator's `opcommon.py` and `APPROVED`; four repository paths; then its own `acceptance_exemptions` line | `7acf0243` | round 2 FAIL on F1 (the undo), fixed as text by the reviewer's option (a); forward path verified | after 7 (its second commit changes the path map) |
| — | ACT-OPERATOR-HOURS-1 | the crontab (line 7) | `9cbccb82` | READY | the CTO applies it after 8 |
| 9 | ACT-CLAUDE-COPIES-5 | the six `.claude/skills` copies | `e602d596` | READY | after W2-11's merge (Part 2) |
| 10 | ACT-CONTEXT-WATCH-1 (round 2) | `.claude/settings.json`, `.rulesync/hooks.jsonc` | `5bdfa098` | READY | after W2-176's merge (Part 2) |

**Why 5-7 by hand now:** the operator agent's path-map replay refuses until about 21:17 UTC today (DECIDED-NOT-DONE row 124),
and EXAMIN-SETS-1 is on EXAMIN's path (W2-93 and W2-94 wait on it). **Why 8 is last in Part 1:** DEC-1136 (2) makes it add its own
commit to `acceptance_exemptions` (its first commit changes `tests/acceptance/W2-148/`); that changes the path map, and 5-7 have
fixed before hashes. If you hold any of 5-7, 8 still applies on the live map (its `exempt` step allows both befores).

## The yes lines (in the chat first)
```
yes ACT-LOAD-BALANCER-A 0b40f1bf
yes ACT-CLAUDE-COPIES-4 6ab06e85
yes ACT-DISPATCH-1 a20754dd
yes ACT-IDLE-GUARD-2 a3fe076c
yes ACT-EXAMIN-SETS-1 e8020292
yes ACT-ACCEPTED-REDS-1 b8df21d8
yes ACT-PATHMAP-EXP-1 9a945c99
yes ACT-OPERATOR-HOURS-2 7acf0243
yes ACT-OPERATOR-HOURS-1 9cbccb82
yes ACT-CLAUDE-COPIES-5 e602d596
yes ACT-CONTEXT-WATCH-1 5bdfa098
```
(Given already: ACT A 23:38, COPIES-4 02:33, COPIES-5 02:34; repeated so all are in one place.)

## Part 1: the message for the owner's operator

> **Eight ACTs by hand, in this order, in the main tree. Stop at the first step that does not show what is expected, send that
> line to the CTO, and apply nothing further.**
>
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> test -z "$(git status --porcelain --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean      # expect: clean
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
>
> **2. ACT-CLAUDE-COPIES-4** (the 19 generated copies of W2-175's approved 1.0.1 role templates; DEC-1139)
> ```
> G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-4
> sha256sum $G/manifest.json      # expect 6ab06e85cae2d566c9da540c9ef0ec60c9edc366b6d5e5ccb7401a7d6d99fd17
> bash $G/apply.sh check && bash $G/apply.sh apply
> F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 19
> git commit -m "ACT-CLAUDE-COPIES-4: the .claude/templates role copies, the six .rulesync/subagents sources and the six .claude/agents for W2-175's 1.0.1 templates (19 files)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1139, DEC-1116" --trailer "Role: owner"
> ```
>
> **3. ACT-DISPATCH-1** (the dispatcher enforces the lead cap, one idle item per cause, a held slot counted by its measured load)
> ```
> A=.gov-runtime/scratch/orchestrator/acts/ACT-DISPATCH-1
> sha256sum $A/manifest.json     # expect a20754dd1e9f88db984a467d65bfb2b346e7c94d61cd00b520bca99ac8351070
> bash $A/apply.sh check         # exit 0
> bash $A/apply.sh apply         # exit 0
> bash $A/apply.sh verify        # exit 0
> git diff --name-status         # expect exactly four M: dispatch/dispatcher.py, dispatch/balancer.py, test_dispatcher.py, test_balancer.py
> git commit -m "ACT-DISPATCH-1: the dispatcher enforces max_leads, sends one idle item per cause (reminder after 6 h), counts a held slot by its measured load (DEC-1140 (1)(a), (2))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1140, DEC-1118" --trailer "Role: owner" -- governance/project/orchestration/tools/dispatch/dispatcher.py governance/project/orchestration/tools/dispatch/balancer.py tests/unit/orchestration/test_dispatcher.py tests/unit/orchestration/test_balancer.py
> ```
>
> **4. ACT-IDLE-GUARD-2** (the idle check leaves out a returned lead's line and merged tickets, keeps claimed ones, cuts a slow plan at 5 s)
> ```
> A=.gov-runtime/scratch/orchestrator/acts/ACT-IDLE-GUARD-2
> sha256sum $A/manifest.json     # expect a3fe076cf3339f5da0fcd54462f8270467d731d08805215b394f66c725737422
> bash $A/apply.sh check         # exit 0
> bash $A/apply.sh apply         # exit 0
> bash $A/apply.sh verify        # exit 0
> git diff --name-status         # expect exactly two M: stop_idle_check.py and test_stop_idle_check.py
> git commit -m "ACT-IDLE-GUARD-2: the idle check leaves out a returned lead's line and merged plan tickets, and cuts a slow plan at 5 s (DEC-1140 (2); ACT-IDLE-GUARD-1 review F1-F3)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1140, DEC-1110" --trailer "Role: owner" -- governance/project/orchestration/tools/stop_idle_check.py tests/unit/orchestration/test_stop_idle_check.py
> ```
>
> **5. ACT-EXAMIN-SETS-1** (the path map declares EXAMIN's set and the proving ground's held-out half; DEC-1130 (3))
> ```
> A=.gov-runtime/scratch/orchestrator/acts/ACT-EXAMIN-SETS-1
> sha256sum $A/manifest.json     # expect e80202922e72b3e55767efceef315b8ead863de443fb4036aab24cb6f9e8674f
> bash $A/apply.sh check         # expect: state before (sha256 f4029cfb4942)
> bash $A/apply.sh apply         # expect: state applied (sha256 0ec1d20da86a)
> bash $A/apply.sh verify        # exit 0
> PYTHONPATH=src python3 -m gov.check.pathmap; echo $?   # expect: 0, with no output before it
> git commit -m "ACT-EXAMIN-SETS-1: the path map declares EXAMIN's set and the proving ground's held-out half (DEC-1130 (3))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1130, DEC-1101" --trailer "Role: owner" -- governance/project/path-map.yaml
> bash .gov-runtime/scratch/orchestrator/drafts/examin-sets/tools/sets_root_map.sh check   # step 2, the sets root's own map: expect state before
> bash .gov-runtime/scratch/orchestrator/drafts/examin-sets/tools/sets_root_map.sh apply   # exit 0; the old map kept beside it as .pre-ACT-EXAMIN-SETS-1
> ```
>
> **6. ACT-ACCEPTED-REDS-1** (`accepted_reds` lists the two warm real-model latency cases until W2-155 closes; DEC-1134)
> ```
> A=.gov-runtime/scratch/orchestrator/acts/ACT-ACCEPTED-REDS-1
> sha256sum $A/manifest.json     # expect b8df21d891600ff4701ff264ff94f32257c4c9150ae4eb4a3254af2662248ea7
> bash $A/apply.sh check         # expect: state before (sha256 0ec1d20da86a)
> bash $A/apply.sh apply         # expect: state applied (sha256 5654eca4c139)
> bash $A/apply.sh verify        # silent, exit 0
> PYTHONPATH=src python3 -m gov.check.pathmap; echo $?   # expect: 0, with no output before it
> git diff --numstat -- governance/project/path-map.yaml  # expect: 9  1  governance/project/path-map.yaml
> git commit -m "ACT-ACCEPTED-REDS-1: accepted_reds lists the two warm real-model latency cases (W1-19, W2-13) until W2-155 closes (DEC-1134)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1134, DEC-1125" --trailer "Role: owner" -- governance/project/path-map.yaml
> ```
>
> **7. ACT-PATHMAP-EXP-1** (the experiments root in exactly one namespace of the path map; frees W2-40)
> ```
> A=.gov-runtime/scratch/orchestrator/acts/ACT-PATHMAP-EXP-1
> sha256sum $A/manifest.json     # expect 9a945c99201d4c2c49cbd522c38b3ebee5b2fa0c09dbb5f9e62f852721b6e93c
> bash $A/apply.sh check         # expect: state before (sha256 5654eca4c139)
> bash $A/apply.sh apply         # expect: state applied (sha256 d50884e3633e)
> bash $A/apply.sh verify        # exit 0
> PYTHONPATH=src python3 -m gov.check.pathmap; echo $?   # expect: 0, with no output before it
> git commit -m "ACT-PATHMAP-EXP-1: the experiments root is in exactly one namespace of the path map (DEC-333, DEC-273)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-333, DEC-273" --trailer "Role: owner" -- governance/project/path-map.yaml
> ```
>
> **8. ACT-OPERATOR-HOURS-2** (G9 holds only while the night hold is on; DEC-1141 (6)). Not at a :x0 minute (the cron's launch).
> The CTO already holds integrate ("starting" above), so nothing lands between its two commits. Note step 2's `H` (the first commit's id): an undo uses it (the package's section 5).
> ```
> G=.gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-2
> sha256sum $G/manifest.json      # expect 7acf024359d6cdbd87c1d487e5d0dc5b64236a45c1ca4e7ce427bcf9db696697
> bash $G/apply.sh check     # exit 0: "check: ready to apply ..." (every listed file is the before; the operator holds nothing)
> bash $G/apply.sh apply     # exit 0: six lines "apply: ...", "the install's own APPROVED check: ok", "APPROVED 1e557c49...", "state applied"
> bash $G/apply.sh verify    # exit 0: "verify: every listed file is the after ..."
> sha256sum ~/gov-os-operator/install/APPROVED    # expect 1e557c49be5802256efa1906753964b53893a2eb507701fac02ebfe4f60914bc
> git status --short         # 3 M and 1 ?? (opcommon.py, test_w2_148_gates.py, its README.md; the new test_act_operator_hours_2.py)
> git add governance/project/operator/opcommon.py tests/acceptance/W2-148/test_w2_148_gates.py tests/acceptance/W2-148/README.md tests/unit/operator/test_act_operator_hours_2.py
> git commit -m "ACT-OPERATOR-HOURS-2: G9 holds only while the night hold is on (DEC-1141 (6)); the fixed quiet hours and the nightly window gone" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1141" --trailer "Role: owner" -- governance/project/operator/opcommon.py tests/acceptance/W2-148/test_w2_148_gates.py tests/acceptance/W2-148/README.md tests/unit/operator/test_act_operator_hours_2.py
> # step 2, straight after step 1 (nothing committed between; W1-01 is red until it is in):
> bash $G/apply.sh exempt           # exit 0: "exempt: added the entry for <12 digits>", then "exempt-verify: the map is the allowed before (sha256 f4029cfb4942 or d50884e3633e) plus exactly the entry for <12 digits> ..."
> git diff --numstat -- governance/project/path-map.yaml   # expect: 2  0  governance/project/path-map.yaml
> H=$(git rev-parse HEAD)           # the first commit's full id (exempt wrote it into the map)
> git add governance/project/path-map.yaml
> git commit -m "ACT-OPERATOR-HOURS-2: acceptance_exemptions lists its own commit ${H:0:12} (DEC-1136 (2))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1136, DEC-1141" --trailer "Role: owner" -- governance/project/path-map.yaml
> bash $G/apply.sh exempt-verify    # exit 0: the committed map is the allowed before plus exactly the entry
> ```
>
> ```
> git status --porcelain --untracked-files=no     # expect empty
> git log --oneline -10                           # the commits, in this order (8 has two)
> ```
> Then tell the CTO "done" with the last line of `git log --oneline -1`.

**Undo, any one:** `bash <its bundle>/apply.sh undo`, then commit the same paths with the subject `<ACT> undone` and
`--trailer "Role: owner"`. Undo in reverse order if more than one (the path-map chain: 8's exemption, then 7, 6, 5).

## After "done" (the CTO)
End the freeze; apply ACT-OPERATOR-HOURS-1 (the crontab, class (b), P-ACT-SPLIT; its `check` refuses until 8 is in); a landing
check after the commits; the first dispatcher pass shows `lead cap:` and "N of them at their measured load"; then the hand merges
(DEC-1141 (4)): W2-11 (the K3 CIT-P approved at `dca382f3069f`), W2-175 (S6, expect 254 passed, 0 failed, and the unit suites
first), and W2-176 once you approve its new bytes; each by `git merge --no-ff` in one command with its ticket trailer, then its close.

## Part 2: after the CTO says "merged" (about 5 minutes)

> **Two ACTs by hand, in this order.**
>
> **9. ACT-CLAUDE-COPIES-5** (the six `.claude/skills` copies for W2-11's round-2 kernel skills)
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> test -z "$(git status --short --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean
> G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-5
> sha256sum $G/manifest.json      # expect e602d5960dccf62100cb8bc151ae3363fe3e8eb4d96ed8c9e29fe045450f0c91
> bash $G/apply.sh check && bash $G/apply.sh apply
> F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 6
> git commit -m "ACT-CLAUDE-COPIES-5: the six .claude/skills copies for W2-11's round-2 kernel skills (6 files)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-315, DEC-992" --trailer "Role: owner"
> ```
>
> **10. ACT-CONTEXT-WATCH-1** (register W2-176's context watch as a PostToolUse hook, matcher Bash; DEC-1140 (1)(b), DEC-1141)
> ```
> sha256sum template/governance/kernel/hooks/context_watch.py   # expect 213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242 (W2-176 merged)
> A=.gov-runtime/scratch/orchestrator/acts/ACT-CONTEXT-WATCH-1
> sha256sum $A/manifest.json     # expect 5bdfa0981808513db3d9fceeb30f13ba11ea72ea28528ef40664bfe9a931da5a
> bash $A/apply.sh check         # exit 0: "state before; ... in place as approved"
> bash $A/apply.sh apply         # exit 0
> bash $A/apply.sh verify        # exit 0
> git diff --name-status         # expect exactly two M: .claude/settings.json and .rulesync/hooks.jsonc
> git commit -m "ACT-CONTEXT-WATCH-1: register context_watch.py as a PostToolUse hook, matcher Bash, so every session hands over before compaction (DEC-1140 (1)(b), DEC-1141)" --trailer "Task: DAEO-ktiw" --trailer "Implements: DEC-1140, DEC-1141" --trailer "Role: owner" -- .claude/settings.json .rulesync/hooks.jsonc
> ```
> Then tell the CTO "done". Running sessions pick up the new hook at their next start.

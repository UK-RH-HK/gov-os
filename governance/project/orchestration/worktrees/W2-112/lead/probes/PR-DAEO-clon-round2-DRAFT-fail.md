---
type: probe
task: DAEO-clon
reviewer_session: 466fc8b2-409a-46e3-ba15-b92368fc2655
implementer_session: f828ddfe-8d6f-4c83-80f7-210571776dfc
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 03b97eb1728476a3a6b4449464077d1c0165e570
---

## Probe record: DAEO-clon (W2-112) at 03b97eb17284, review round 2 (the last)

**What was probed.**
- **Head:** 03b97eb17284, the lead's checkpoint over the engineer's 431552ce21ca.
- **Change:** from be02bb012537 over the allowed paths. `rerank.py`, `rerank_service.py`, `rerank_worker.py`, `retrieve.py`, `status/command.py`, four unit test files and the research document.
- **Since round 1:** only the research document's §5 (f59c9ba5560e, 431552ce21ca) and the designer's F1 test (ed0891667f46).
- **Code under test:** `/home/usain/gov-os-worktrees/W2-112/src/gov/__init__.py`, set per command.

**How it was probed** (each run, not read, unless marked):

| Probe | What was run or read |
|---|---|
| q1 | §5's precondition 1 on the real machine (with `-B` added so nothing is written into the pin) |
| q2 | §5's precondition 2 over `$HOME` and `/tmp`, pruning `~/gov-os-workbench`, every `governance/project`, `.claude`, `fixtures/evaluation/*/hidden` and `.git` (DEC-508, DEC-820) |
| q3 | §5's removal, check and undo targets, read-only: files, `cmp`, the check lines |
| p1r | The state after the ACT against the state before it: an old tree's search and this head's, with both slots held |
| p2r | Round 1's sound probes re-run: a cold start with 20 searches, the module beside the rule, SIGTERM, SIGKILL |
| p3n | New cases: a hung (stopped) service mid-request; a storm of refused service starts; the idle-end race; 30 searches racing a slow cold start; no reranker environment |
| p4s | `gov status`'s reranker part with the log absent, large, holding a bad byte, or replaced by a folder |
| p5m | The socket's and its folder's modes; the service's network sockets |
| — | The bundle acceptance file, run alone |
| — | One `gov retrieve` |
| — | The pin across 77 trees and pins (F2); W2-127's ticket (F3); branch, resume and worktree paths (read) |

### F1's repair: §5 read as an operator who follows it literally
- **Precondition 1 is correct for this machine.** `~/.local/bin/gov` is a link into `pin-a7182f6c/bin`. The check printed that pin's worker path and `0`, so the precondition does not hold, as §5 says.
- **Precondition 2 works today.** It found 648 worker files, 633 without the rule:
  - 67 worktree checkouts and 51 code-graph copies;
  - the four pins;
  - the merge queue's clone, the nightly and close folders;
  - re-pin dry runs and test temporary folders.

  So the precondition does not hold. Two kinds of OLD line are not runnable trees: five temporary files that vanished during the scan, and the code-graph copies. Both err on the safe side.
- **The removal step names exactly the installed files** (`gov-reranker-gpu-slot.pth`, `gov_reranker_gpu_slot.py`). The installed module is identical to this tree's copy and to the main checkout's, which is the undo's source. The `.dec1031` backup is inert. The check prints the module's spec today; by reading, it will print `None None None` afterwards.
- **The lock files are never removed,** and §5 says why.
- **Not durable (F9):** both checks describe the machine at one moment, and later ordinary work undoes them.
- **The undo's check is stale (F10).**

### Found sound at this head (run)
1. **Cold start:**
   - 20 searches together: one model load, one service, every search with its own scores, no fallback (p2r a).
   - 30 searches against a 3 s load: the same, slowest 3.16 s (p3n d).
2. **Module beside the product's rule,** three slots configured: the service loaded holding 1 slot, and the private fallback loaded with 2 held in all. It took exactly one slot, never two (p2r b).
3. **SIGTERM** removes the socket and logs END; the next search starts one fresh service (p2r c).
4. **SIGKILL** leaves a stale socket. Six searches together were then all scored in 0.19 s by one new service, with one listener (p2r d).
5. **A stopped (hung) service mid-request,** time limit 3 s (p3n a):
   - 4 searches together were all scored by private rerankers in 3.0 to 6.0 s.
   - None raised; none got another search's scores.
   - After SIGCONT the service answered again.
6. **Both slots held, 10 searches together** (p3n b): one service start (one REFUSED), 10 FALLBACK lines, all unranked and named, no model loaded anywhere.
7. **No reranker environment:** unranked at once, nothing logged, no socket (p3n e).
8. **`gov status`'s reranker part** (p4s):
   - An absent log reads 0/0, with the log's path.
   - 37 MB of log (400,000 lines) is counted in 0.17 s, 106 MiB peak.
   - A bad byte, or a folder at the log's place, gives "not read" with the reason.
9. **Socket permissions:** `srw-------` in a `drwx------` folder; the service has no network socket (p5m).
10. **The bundle file passes alone:** 8 passed. Round 1's CLI run (p11) stands; the code is unchanged.
11. **Scope and roles:**
    - The engineer wrote only `docs/research/`; the designer only `tests/acceptance/W2-112/`.
    - Every acceptance commit carries `Role: independent-test-designer`, and no implementer touched the tests.
    - The worktree is clean.

### Findings

**F9: After the ACT, any tree at a commit older than W2-112 runs its private reranker with no GPU slot. §5's precondition is checked once, and nothing keeps it true.** Severity: high (F1's consequence), latent until the ACT is applied. KPI: success-7.
- **Done:**
  - p1r, in a box with no interim module (the state after the ACT) and both slots held: one search through the base's code (be02bb012537), one through this head's.
  - The same with the module installed (the state before the ACT).
  - Precondition 2 run over the box's trees before and after the old tree appeared.
  - Counted the local branches without the rule; read how a resumed lead gets its worktree.
- **Happened:**
  - Precondition 2 printed nothing before the old tree appeared, and nothing re-runs it afterwards.
  - Without the module, the old tree's search loaded its model on the GPU in 0.12 s while both slots were held: a third reranker.
  - This head's search waited and went unranked (10.2 s, no load).
  - With the module, the old tree's search waited 5.1 s and went unranked.
- **How old trees appear after the ACT, in ordinary work:**
  - §5 lets the operator clear an OLD worktree by removing it, but the branch stays. 70 of the 71 local branches with a worker lack the rule. A resumed lead works "in the same worktree", so a removed one returns from its old branch.
  - Older commits are also checked out for red checks on a ticket's base, for comparisons and for bisects.
  - DEC-1037 (1) keeps the old pin for rollback, and all four kept wheels predate W2-112.
  - Under DEC-732, such a tree's first `gov retrieve` or `gov check` runs its own old worker.
  - §5's "removing it changes nothing in behaviour" is then false.
- **Reproduction:** the mechanism was reproduced in a box. The path on the real machine (a re-created worktree after the ACT) was not, since that needs the ACT applied.
- **Should have happened:** the cap holds for every reranker the environment can start, whatever the tree's commit. Either the module stays, old code fails closed without it, or §5 states the residual and closes its paths.
- Scope: in. KPI 7 makes this ACT the ticket's deliverable, and §5 is in the ticket's research document.
- Ordinary work: yes, because after the ACT an honest agent re-creates a parked ticket's worktree from its branch (the removal §5 offers), checks out an older base for a red check, compares a failure on another commit, or rolls the pin back; its first search runs the old worker.
- Consequence: fails open. The GPU slot rule is bypassed. DEC-1043 puts the two embedders at about 5.6 GB, the service at 4.8 to 6.4 GB and a private at about 3.5 GB, so one uncapped reranker more passes the card's budget: DEC-1031's crash state.

**F10: The undo's check no longer matches the installed module.** Severity: low. KPI: success-7.
- **Done:** ran ACT-RERANK-GPU-SLOTS-1 §3's last line read-only, with the module installed. §5's Undo points to it.
- **Happened:** it printed `slot None CUDA_VISIBLE_DEVICES None`. That ACT lists only `slot 0`, `slot 1` or `CUDA_VISIBLE_DEVICES -1` as proof. Since ACT-RERANK-WAIT-1, every Python other than the worker is left untouched, so the line can never show the module.
- **Should have happened:** the Undo names ACT-RERANK-WAIT-1's stand-in-worker check, which does show it.
- Scope: in.
- Ordinary work: yes, because an operator who undoes the ACT runs its commands to the last line.
- Consequence: other. A good undo may look failed; the module is in force either way.

**F11: With both slots busy, a search waits twice before it goes unranked.** Severity: low. KPI: success-4, success-7.
- **Done:** p3n (b).
- **Happened:** one service started and was refused. Every search then waited again for a private reranker and went unranked after 10.1 s at the box's 5 s waits; at the defaults, about 40 s. Bounded and named.
- **Should have happened:** after the service's refusal for want of a slot, the search goes unranked at once, or waits only once.
- Scope: in.
- Ordinary work: yes, because both slots are busy whenever the service is down and two rerankers hold them (today: old trees' privates, through the module).
- Consequence: other.

### Round 1's placed findings at this head
- **F2** (entry criterion of W2-32 and of any pin or service change): unchanged. All 77 trees and pins pin `e61197ed…`, and only this tree has the service.
- **F3** (a KPI line for W2-127): placed. It is `.tickets/DAEO-1vka.md` line 28, so for W2-112 it is now out of scope. The code is unchanged.
- **F4** (row): code unchanged.
- **F5** (row): re-confirmed by p3n (c). The search at the idle end fell back to a private, logged as "ended before it listened", and no new service started.
- **F6** (row): re-confirmed by p3n (a). A stopped service stays alive holding its slot; every search pays the time limit, then falls back.
- **F7, F8** (rows): code unchanged; not re-run.
- **O1 to O4:** unchanged.

### For the KPI revision (DEC-1043 (2); for information, not findings at this head)
- **Keeping privates off the GPU while the service lives:** the service holds every slot itself, or the private worker refuses while `rerank.lock` is held. The cost: a hung service (F6), or a sandboxed session until W2-127, then goes unranked.
- **The service's share:** its start threshold assumes 3.5 GiB plus 2 GiB headroom. DEC-1043 records 4.8 to 6.4 GB under load, against 3.26 GB in the research document. The share should be derived from the measured peak at the cap (512 texts), or the service's growth bounded. I did not measure it.
- **Tests:** the designer's slot cases that expect one private beside the service change with the KPI.

**Classification:**
- 1 blocking: F9 (in scope, ordinary work yes, fails open).
- 2 new rows: F10 and F11 (other).
- F1's two defects repaired.
- F2 to F8 as the moderator placed them, unchanged at this head: F5 and F6 re-confirmed by run; F3 now W2-127's.

**Recommendation:** round 2 is the last, so F9 goes to the owner once, with options (DEC-1010, DEC-105). The fix is in §5, within the ticket's own paths, and rides along in the resume already due for DEC-1043 (2) (DEC-802). Nothing is at risk meanwhile: both preconditions fail today.
- **(a) Apply now:**
  - Every open branch merged with a head holding W2-112 before the ACT; no "remove first" while a branch is open.
  - The pre-W2-112 pins and wheels removed.
  - A standing rule: the module goes back before an older commit runs with the real reranker environment.
  - The residual stated in §5.
  - Cost: about 20 lines; the residual still rests on people.
- **(b) Defer:** the module stays until old code fails closed by construction. For example, the environment moves to a path only W2-112-or-later code knows, so an old tree finds none and keeps the fused order (DEC-374). Cost: nothing now.
- **(c) Re-baseline KPI 7:** the module stays as the machine-wide guard (§5 itself calls it "harmless beside W2-112's worker"). Cost: one KPI wording change.
- **Recommended:** (c), or (b). Confidence medium-high: the module is the only control that covers every tree whatever its commit.

```verdict
{"kpis": [
 {"kpi": "success-1", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F8", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "success-2", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "success-3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "success-4", "verdict": "fail", "findings": [{"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F11", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "success-5", "verdict": "pass", "findings": []},
 {"kpi": "success-6", "verdict": "pass", "findings": []},
 {"kpi": "success-7", "verdict": "fail", "findings": [{"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F10", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F11", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "failure-1", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "failure-2", "verdict": "pass", "findings": [{"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "failure-3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}
]}
```

Success-4 is marked fail only for the sandboxed-session clause, now W2-127's line; all its findings are "other". Success-7 is marked fail for F9.

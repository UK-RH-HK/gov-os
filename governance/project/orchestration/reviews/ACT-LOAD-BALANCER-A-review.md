# Review: ACT-LOAD-BALANCER-A (DEC-1133 (3)), r1

- **Reviewer:** fresh, read-only independent session, 2026-11-11. Judged by `governance/project/briefs/JUDGEMENT.md`.
- **Bundle:** `manifest.json` sha256 `0b40f1bfd84b65d043a7e7e2599d0717139461885f8f73462a3f24751b7a8e5f` (yes line `yes ACT-LOAD-BALANCER-A 0b40f1bf`).
- **Verdict:** pass, READY. 3 findings, all scope in; F1 and F2 ordinary work yes with consequence other, F3 ordinary work no with consequence other; none blocks.

## Checks
| # | Check | Result |
|---|---|---|
| 1 | Hashes and scope | Every hash recomputed and matching. before = live `w2/integrate` and main tree (`03b93044ff98`). after = before + 18 lines (header, gate check, registration, refusal words); `exec` line unchanged. |
| 2 | Fail closed, nothing lost | Shut gate, `gov` missing (127), check exit 1: exit 3 `LAUNCH_GATE_SHUT`. Registration failure: exit 4 `LAUNCH_NOT_REGISTERED`. Nothing started, nothing registered, no lead log. Open gate: the registered pid = the lead's pid. No wrapper, background job, `wait` or name match. A refused start raises the dispatcher's never-ran item after 300 s; the reason is in `log/<W2>-<time>-launch.txt`. |
| 3 | Manifest checks via `bash -c` from the clone's root | before: 0/1/1/0 (exits of checks 0-3); after: 0/0/0/0. Check 3 green (companion `792b92923` in). |
| 4 | 30 launcher tests (heavy slot, planted HOME) | 30 passed with the ACT applied; 30 passed on the old launcher after `apply.sh undo`. |
| 5 | Class, route, undo | `act_class.py`: class b, row `watchers`, one script hit (`session`, the stub `claude`; known false hit). Undo is byte for byte, only from the after hash, file replaced with `mv`: safe while leads run. A changed file is refused by apply and undo (exit 3, untouched). |

Also: real pinned `gov resources --register` from a real git tree under a planted HOME: exit 0, the entry holds boot and start ticks (section 8's untried case).

## Findings
- **F1 (in):** the launcher's check and registration are two calls outside the machine-wide start lock that `gov launch` holds, so a lead start and a worker launch in the same second or two can each be judged without the other.
  - Ordinary work: yes, because leads launch workers while the dispatcher starts other leads.
  - Consequence: other (at most one working size overcommitted; leads were unchecked before the ACT).
  - Would reverse it: evidence that the product gate is the only memory protection for lead starts.
  - Suggestion: wrap both calls in `flock` on `~/.gov-os/machine/launch.lock`.
- **F2 (in):** the never-ran inbox item does not name the launch log or the refusal word; a refused start counts as a pending lead for up to 10 minutes and waits for the CTO to re-list it.
  - Ordinary work: yes, because any shut gate at a start produces it.
  - Consequence: other (reported; reason findable; nothing lost).
  - Would reverse it: a dispatcher path that already copies the launch log's tail into the item.
- **F3 (in):** the missing-`gov`, other-exit and failed-registration paths are covered by no committed test (only the scratch `test_launch_now_gate.py` and this review's probes); all three are correct today.
  - Ordinary work: no, because a regression needs a later reviewed ACT on a class (b) path.
  - Consequence: other.
  - Would reverse it: a committed test covering those paths.

## Scratch and trees
Clone 201M with 9861 inodes, removed. Both trees `git status --porcelain` empty. No model process.

## The reviewer's verdict block (as returned; READY computed by verdict.py)

```verdict
{"kpis": [{"kpi": "act-load-balancer-a", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```

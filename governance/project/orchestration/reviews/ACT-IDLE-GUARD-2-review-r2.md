# Review r2: ACT-IDLE-GUARD-2 (independent auditor, DAEO-8s85, 2026-11-12)

task: ACT-IDLE-GUARD-2
decisions: DEC-1140, DEC-1110, DEC-1104, DEC-1010, DEC-801, DEC-808, DEC-1014, DEC-1073
Classification: no finding blocks; F1 and F2 are rows (F2 for Wave 3), F3 is an out-of-scope row.

## ACT-IDLE-GUARD-2 (manifest a3fe076cf333…): pass
- **Hashes:** all match: the manifest, the seven `files` entries and `list.txt`. `before/` equals `w2/integrate` b7a4e93a574a and the main tree. `apply.sh` is identical to round 1's. ACT-DISPATCH-1's manifest is unchanged (a20754dd1e9f…).
- **Round 1's F1 is fixed.** In a planted repo, a claimed ticket at integrate's head is named, and so is one that integrate has moved past. A ticket merged with `--no-ff` is left out and logged "to close".
- **Red then green, through the heavy slot:**
  - the new test file on today's hook: 11 failed, 45 passed
  - on round 1's hook: 2 failed, 54 passed
  - on round 2's hook: 56 passed
  - the old test file on round 2's hook: 31 passed
- **Manifest checks:** all three pass as written; check 1 prints 4. `apply` leaves exactly the two files changed, and `verify` exits 0.
- **Timeouts:** with a hanging git and a 4.5 s plan the hook ends in 7.55 to 7.65 s, names every ticket and logs the cause. A failing git also names every ticket. The worst case is about 8.2 s, inside `timeout: 10`. The hook never fails the session: exit 0 and empty standard error in every run.

## Rows
- **F1:** a ticket whose tip is on integrate's first-parent line is named as launchable. This covers a fast-forward landing, or a sync after the landing (`w2/W2-149-sgx` today).
  - Ordinary work: yes, because a landed worktree's sync to integrate is ordinary.
  - Consequence: other. A false block once per turn, with the IDLE-REASON escape.
  - Reverse if: fast-forward landings become common, or a false block costs more than one turn.
- **F2 (Wave 3):** a sub-ticket branch made from a merged ticket's tip, with no commit of its own, is left out as merged.
  - Ordinary work: no, because ticket branches are made from `w2/integrate`; all 26 unmerged branches fork from its line.
  - Consequence: fails open.
  - Reverse if: a ticket branch is made from another ticket's branch in ordinary work.
- **F3 (scope out):** a ticket that landed part of its work and has more to do is logged "to close", not named.
  - Ordinary work: yes.
  - Consequence: fails open, narrowly: the plan arm only, and the log names the ticket.
  - Out of scope: this is the design decided under DEC-1140 (2) and passed in round 1. It needs the parked or close list (section 7).
  - Reverse if: the owner rules that landed tickets stay named until closed.
- **Text:** "2 on it" counts `w2/integrate` itself. Only one ticket branch is on the line.

## The reviewer's verdict block
```verdict
{"kpis": [{"kpi": "act-idle-guard-2", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```

# ACT-OPERATOR-HOURS-2: independent review, round 1

- **ACT:** ACT-OPERATOR-HOURS-2 (DEC-1141 (6)). Manifest `d3d292378b7bda8c4339fcbcaa77025a53dd40b91aefad0eef8a686f3ad8e6f2`. Class claimed O; class found **O**.
- **Reviewer:** an independent auditor session, read only; I wrote none of the bundle. 2026-11-12, about 03:30 to 03:50 UTC.
- **Verdict:** **pass**. Nothing is in scope, ordinary work and failing open or losing work.
- **Decisions:** DEC-1141 (6), DEC-1104 (2) (4), DEC-1138 (3), DEC-1057, DEC-801, DEC-808, DEC-1010, DEC-430, DEC-136.

## What I probed and found sound
- **Hashes:** all 16 bundle files, `list.txt`, `keep.txt` and `manifest.json` match the package. `before/` equals the live install (`e392d8a0e177`, `97c9a3a5bd22`, all 13 kept files) and the main tree's three files today; the head moved to `9bbef27f1`, the files did not. `after/` differs only as section 2 says, and the `opcommon.py` line is the only `APPROVED` line that changes.
- **G9 on a stub clock:** 20 times by 15 states, old code and new. 0 disagreements with the rule; nothing goes from free to held. Held to free: 02:00 to 02:09, and 03:10 to 07:59 with a fresh false only. A missing, stale (301 s and more), malformed, empty, odd (`"false"`, 0, null, `[false]`, no key) or directory file holds, each with its reason.
- **Other holds:** `NIGHTLY-RUNNING`, the close queue, both `act-in-progress.txt` files, an unreadable clock and a configured `nightly_window` all still hold.
- **The nightly is protected three ways:**
  - The night hold is true from 03:00 until the nightly's real end. The run executes once a night under a lock, and a killed or refused run is the real end.
  - `nightly.sh`'s flag covers the suites and the solo re-runs.
  - The 04:00 wrapper waits for 5 quiet minutes, counting `operator_run.py` and the operator's commit freeze as not quiet.
- **Sessions begun before 02:10:** they end by 02:55:30, so they are no nightly risk.
- **Shared reading:** G9 and ACT-OPERATOR-HOURS-1's guard use the same boundaries (02:10, 03:10, 08:00, 300 s), the same `is False` test and the same file. G9's default path equals `night_hold.py`'s file.
- **`apply.sh`:** it refuses moved or tampered files, works under the launch lock, writes by temp file and rename with `APPROVED` last, and runs the install's own `APPROVED` check. I found no way for it to lose work.
- **Class and route:** class O (`operator-own` and the catch-all `unknown`). The owner's by-hand route is right.

## Findings
| id | finding (behaviour) | scope | ordinary work | consequence | reversed by |
|---|---|---|---|---|---|
| F1 | A future-dated `holding: false` file releases G9 from 03:10 to 07:59 | in | no: the clock must step backwards after the writer stops, or the time be set by hand | fails open | the clock stepping backwards in normal running while the writer is down |
| F2 | 07:30 to 07:59 is free once the hold's 07:30 cap releases; only the flag covers a nightly still waiting to write it | in | no: the latest starts fall well before 07:30 at today's 1.5 to 3 h estimates | fails open | an estimate under 30 min, or the flag written after 07:30 |
| F3 | Section 7 / risk 4 give a 03:04:30 worst case; the true bound is 02:55:30 | in | yes: every reader | other | a G9 call I missed, or a session not timed by the launcher |
| F4 | The S13 acceptance case is rewritten by the builder, not the test designer; the owner's commit is the route | in | no: a one-off the owner commits | other | a rule against owner-committed acceptance edits, or S13 contradicting DEC-1141 (6) |
| F5 | Unit cases pin constant names and reason wording | in | yes: a later refactor | other | reason wording ruled part of the interface |
| F6 | A run that reaches G9 after 02:10 waits until the session timeout; its request goes to `done/` unapplied (behaviour this ACT leaves as it was) | out | yes | other | an automatic re-queue I missed |

Classification: 6 findings: 0 blocking; F1 and F2 are in scope but not ordinary work (Wave 3 rows); F3, F4 and F5 are in scope with consequence other; F6 is out of scope.

## Recommendation
Take it to the owner as it stands. F3 and F5 are wording fixes for any later rebuild; no new round (DEC-802).

## The reviewer's verdict block (as returned; READY computed by verdict.py)

```verdict
{"kpis": [{"kpi": "act-operator-hours-2", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```

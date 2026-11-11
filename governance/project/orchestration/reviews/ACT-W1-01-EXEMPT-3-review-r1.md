## Round 1

Reviewer: independent-auditor, a `claude -p` session (round 1) started by the CTO (launch_worker.sh, DAEO-r30l); not the author. Brief sha256 e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a (checked). Manifest sha256 6af6bdeb15b018d37f8b11b451b783dbb959ea33e762c89cefaa1033f01cba5e (computed). The work ran in my own `--no-hardlinks` single-branch clone of `w2/integrate` (4193812cbf93), with HOME planted.

**Checks (all pass)**
1. **Touched list, relative script: pass.** The bundle touches one file, `governance/project/path-map.yaml`, from fb52ab2dc756 to f4029cfb4942, as listed. After the apply, `git status` lists only the map, with no temp file and nothing in HOME or crontab. The only `cd` in `apply.sh` is to its own folder. The checks are relative and `commands` is empty.
2. **Undo: pass.** In my clone, undo from the committed state gave the frozen before copy byte for byte, and a second undo said "nothing to undo". The rehearsal log shows the same (G1–G5).
3. **Rehearsal: pass.** `rehearsal.log` hashes as listed (3359eb2c49d5), comes from this `apply.sh` in a clone and ends with `failures: 0`.
4. **Checks: pass.** Both manifest checks exit 0 on the after map. Check 2 exits 1 on the before map (rehearsal D3). Neither prints a count.
5. **Class: (O).** `act_class.classify` votes O (path-map row, ratchet `acceptance_exemptions`). The manifest claims O. G6 refuses O, and every commit the operator makes is `Role: operator`, so the operator agent cannot apply this ACT.
6. **Guard replay: no calls.** Under `src/gov`, only `gov/close/gates.py` reads `acceptance_exemptions`; the guard does not. `replay_refused` is [].

**The six extra checks**
- **(1) Class:** (O) is right, and the operator agent cannot apply it (see check 5).
- **(2) The entry:** it is exactly DEC-1136 (1)'s. The full id 6fbe73b1adde40571f00d490b4b478cf86b70a52 exists, is on integrate, carries `Role: owner`, is ACT-OPERATOR-ROUNDS-1 and changed `tests/acceptance/W2-148/w2_148_support.py`. The entry has the same shape as the existing ones (`- commit: "<40 hex>"`, then `decision: DEC-1136  # …`), is added at the end of the list, and nothing else in the map changes. Since the last listed id, 15952bbfa576, the only commit that touches `tests/acceptance/` without `Role: independent-test-designer` (merges excluded) is 6fbe73b1adde. W1-01's merge case passes on integrate. DEC-1136 (2) needs no second entry, because this ACT's commit touches only the map.
- **(3) apply.sh:** it decides the state by sha256 alone (before, applied or other) and also refuses a link. On a moved map, check, apply, undo and verify all exit 3 and the bytes are untouched.
- **(4) §5 as written:** run in my clone, it gave check "state before", apply "state applied (f4029cfb4942)", verify silent, pathmap 0, numstat `2 0`, and commit 82a88db29827 with `Task: DAEO-sdxk`, `Implements: DEC-1136, DEC-906, DEC-253` and `Role: owner`. The clone was clean after it and the reader line printed True. W1-01's two cases were 1 failed and 1 passed before, naming only 6fbe73b1adde, and 2 passed after.
- **(5) validate_entry:** the pin's python with `-E`, run on my own diff, printed PASS, 0 placeholder hits and exit 0.
- **(6) The other two ACTs:** after this apply, ACT-EXAMIN-SETS-1 and ACT-ACCEPTED-REDS-1 both refuse: check, apply, undo and verify all exit 3 and the map is untouched. Rebuilt by hand on the new map, EXAMIN gives 0ec1d20da86a, then REDS gives 5654eca4c139. The reverse order gives the same final map, and the inserted lines are byte-identical. Neither bundle touches `tests/acceptance/`, so DEC-1136 (2) adds nothing to them.

**Findings (all rows, none blocking)**
- **F1.** KPI 5; scope out; ordinary_work no; consequence fails open (in principle).
  - What: W1-01's history case and `gates.owner_listed` accept an `acceptance_exemptions` entry by full id and decision only. They never read the role of the commit that added the entry.
  - Ordinary work: no, because an honest agent's route for this entry is the class table and G6 (O). The operator agent is refused at G6 and every commit it makes is `Role: operator`. The author also discloses the gap (rehearsal F4).
  - Evidence: rehearsal F4; `gates.owner_listed` lines 118–132.
  - Fix: out of this ACT. Optionally a later ticket so W1-01 or gate (h) checks that the entry came from a `Role: owner` commit.
- **F2.** KPI 3; scope in; ordinary_work no; consequence other.
  - What: §6's table lists an F5 row (§5 run as written, via `tools/run_section5.sh`), but `rehearsal.log` has no F5 section; that run's output is not in the bundle.
  - Ordinary work: no, because I ran §5 as written myself and got 2 passed.
  - Fix: keep `section5.out` beside the log next time, or append it to the log.
- **F3.** KPI 1; scope in; ordinary_work no; consequence other.
  - What: `apply.sh`'s header comment names `make_manifest.py`, which is not in `tools/` (it holds `build.py`).
  - Ordinary work: no, because it is a comment and nothing runs it.
  - Fix: correct the comment in the next build.
- **F4.** KPI 5 (the validate step); scope out; ordinary_work no; consequence other.
  - What: `validate_entry.py`'s section regex has no `acceptance_exemptions`, so it labels this entry "accepted_history". The reader it applies, `history._refused_because`, is the one `gates.owner_listed` uses for the exemptions, so the PASS still holds.
  - Ordinary work: no, because the result is right; only the label is wrong.
  - Fix: add `acceptance_exemptions` to the tool's section regex.
- **F5.** KPI 3; scope in; ordinary_work yes; consequence other.
  - What: the by-hand commit under the main tree's own hooks (the freeze gate, the landing check, the trailer gate) is not rehearsed.
  - Ordinary work: yes, because the operator agent may be running an ACT when the owner commits.
  - Consequence: other. A refusal leaves the map applied but uncommitted. §5 says to wait for the run to end and run the commit line again, or to run `apply.sh undo`; no work is lost. The same commit form passed for 3428f659f095 and 6fbe73b1adde.
  - Fix: none needed.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "4", "verdict": "pass", "findings": []},
          {"kpi": "5", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F4", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "6af6bdeb15b018d37f8b11b451b783dbb959ea33e762c89cefaa1033f01cba5e",
 "class": "O",
 "reviewer": "independent-auditor, claude -p session (round 1) started by the CTO (launch_worker.sh, DAEO-r30l); not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-11T19:03:22+00:00",
 "replay_refused": []}
```

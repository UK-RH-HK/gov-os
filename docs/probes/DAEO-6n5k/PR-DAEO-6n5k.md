---
type: probe
task: DAEO-6n5k
reviewer_session: a65d85e6-f34a-4d57-90e5-81ffef3ba6b8
reviewer_model: claude-opus-5-5 (high, class C2)
implementer_session: eng-3 (log/eng-3.json; commit 81f9d8c3d)
test_designer_session: f80af5b6-18d0-4d0c-ab35-6f4932fa4ac0 (commit 269d5f658)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 65e8c076873d565b85a9f3f4dd0ba9873fd626c9
rounds: review 1 (6b5640b0, fail), review 2 (2ff873b2, fail), this resume's fresh probe (65e8c076, pass), DEC-812 (1), DEC-1010
---

# Probe record: W2-37 `gov impact`, the resume's fresh probe (DEC-812 (1))

- **What was probed.** Head `65e8c076` on `w2/W2-37`. That head is: the merge of w2/integrate (`64ccbd0cc`); the engineer's fix `81f9d8c3d` for the second review's A, B, C, E and F4 and the depth source (DEC-812, DEC-815); and the test designer's batch `269d5f658`, merged at `65e8c0768`.
- **The reviewer.** A fresh read-only independent-auditor on Opus, high: session `a65d85e6-f34a-4d57-90e5-81ffef3ba6b8`, 2026-11-13, launched sandboxed with `launch_worker.sh`.
- **No writes.** The tripwire shows no change in W2-37, and `git status --porcelain` was empty at the end. The only changes it shows are the lead's removal of W2-37-tests and W2-88's own workers.
- **Scope judged.** S1 (the plain-language question runs `gov impact`) and S2 (G-16 id mapping, G-24 deletable join). The CIT-P and CIT-E lines were lifted by DEC-1083. DEC-812 (4)'s readings were kept, and the depths are DEC-815's.
- **Tests.**
  - The reviewer, sandboxed: 126 passed, 2 failed, 21 deselected (`local_only`).
  - The lead, outside the sandbox with the code-graph tool on PATH: 147 passed, 2 failed.
  - lead_verify at `65e8c076`: 4959 tests, 2 failed, 27 skipped.
  - The 2 failures are the same in every run: `test_w2_37_skill_routing.py::test_the_skill_runs_gov_impact_for_the_question[template]` and `[claude-copy]`. They are P-1 (DEC-816): the change skill's files are outside the ticket's allowed paths.

## Re-probes of the second review's findings
- **A: sound.** With CITP-001 edited to drop DEC-002, unstaged or staged, the compare reads HEAD's proposal. It gives `matches: false`, with DEC-002 `only_in: proposal`.
- **B: sound.** The register has no entry at HEAD, and a first entry is added uncommitted or staged:
  - `graphs.record` reads `stale: records/decision-log.md differ from HEAD`, and DEC-050 is not deletable.
  - The same holds when the register is in a `product` namespace.
  - After a commit and a reload, DEC-090 is listed.
- **C: sound.** The compare carries the proposal's `complete` and gaps:
  - A proposal that does not state its completeness gives `complete: false` with `COMPLETENESS_NOT_STATED`.
  - `complete: true` with no gaps gives `complete: true`.
- **E: sound.** Each refusal names its real cause, and none writes anything:
  - `IMPACT_OUT_EMPTY` for an empty or blank `--out`.
  - `IMPACT_OUT_IS_FOLDER` for a folder.
  - `IMPACT_OUT_EXISTS` for an existing file.
  - `IMPACT_PROPOSAL_MISSING` for a CIT-P deleted from the working tree.
- **F4: sound for the stem.** `docs/impact/SPEC-300.md` and `docs/impact/DEC-001.md` give `IMPACT_OUT_ID_TAKEN`.

## Probed and found sound
- **S1.** Seven question forms each give the result of `gov impact DEC-001`: R3, depth 8, `depth_source: DEC-815`, the same lists and gaps. The forms are "what is", "What's", the typographic apostrophe, capitals, a backticked id, a quoted id and a trailing newline.
  - DEC-070 reads R1 and DEC-050 reads R0.
  - Without `--json` the full result is printed.
  - These are refused with exit 1 and no traceback: an unknown id, a lower-case id, "What would be the impact of changing…", two ids, and no subject.
- **S2, G-16 record side.** The DEC-001 to `w37_apply` edge is the gap `CODE_GRAPH_MISSING` when no code index exists. The code side was run by the lead outside the sandbox: 21 `local_only` cases, all green.
- **S2, G-24.** DEC-050 is deletable at R0 only on a current record graph. Each of these reads `stale` and makes it not deletable: an untracked, staged or committed-but-not-loaded record naming it; an uncommitted path map; a register's first entry.
- **No regression.** Refusals still write nothing. The baseline radii are unchanged (DEC-001 R3, DEC-050 R0).
- **Commit scope and trailers.**
  - `81f9d8c3d` (engineer) touches only `src/gov/impact/**` and `tests/unit/impact/**`.
  - `269d5f658` (test designer, with `Rewrite-Reason:`) touches only `tests/acceptance/W2-37/**`; no existing case changed.
  - Every commit carries `Task: DAEO-6n5k`. Nothing under `src/gov/closure/` changed.

## Findings (moderated under DEC-1010)
- **F1: a decision cited only by stated links reads deletable, R0, with nothing affected.**
  - Setup: a ticket with `sources:`/`closes: [DEC-050]`, and a register entry with `**Under:**`/`**Changes:** DEC-050`.
  - The store now holds these in `stated_links` (W2-92 S7, DEC-1072 (1)). `gov impact` reads only the typed edges.
  - Classification: scope **out**, because DEC-812 (7) made this row W2-M380. Ordinary work yes; fails open.
  - It would turn in scope and blocking only by an owner reading that G-24's "no record names the item" includes stated links. That question is package PKG-W2-37-F1 in the lead's return.
- **F2: `--compare` after a committed but not reloaded CIT-P edit gives `matches: true` with no graph state.**
  - Scope **out**: `--compare` was lifted by DEC-1083. Ordinary work yes; fails open (the compare only). A row.
- **F3: a second `--out` for the same change derives the same `CITP-<hash>` id as a stored CIT-P.**
  - Scope **out**: `--out` was lifted. Ordinary work yes; other. A row.
- **F4: "What is the impact of DEC-001." (a full stop) is refused with `IMPACT_CHANGE_UNKNOWN 'DEC-001.'`.**
  - Scope **in** (S1). Ordinary work yes; other (fails closed and names the cause). Not blocking; a low row, or it rides along with P-1's change.

## Judgement
**pass.** A, B, C, E and F4 are fixed as the second review stated them, and S1 and S2 hold end to end. No finding is in scope, reachable in ordinary work, and failing open or losing work.

## Guard note
- The reviewer's two parallel Write calls to its sandbox TMPDIR were refused. The rule given was "Quiet hours (02:00 to 07:30) … needs the owner's approval … (DEC-991)".
- It did not retry the Write. It ran its probes as inline Python in Bash instead, inside its TMPDIR.
- Whether that counts as another form of the refused call is for the owner. The night holds were removed by DEC-1157, so the quiet-hours rule firing may be a false positive.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```

---
type: probe
task: DAEO-rd0g
status: final
reviewer_session: 24fe8f83-c537-45c0-b0e7-5f9f67d69970
implementer_session: b7cdd573-fb34-40eb-a66c-d19cad4526cd
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: 293df50f9f9ced8a3bb3c2593e52eb4da263927c
reviewed_range: "883e1ba6b152a8f7101641e194daddccfaa5db80..293df50f9f9ced8a3bb3c2593e52eb4da263927c"
decisions_applied: [DEC-954, DEC-957, DEC-1171, DEC-1186, DEC-074, DEC-1083, DEC-801, DEC-808, DEC-1010, DEC-820]
scope: "Narrow check before the land of W2-15a's two commits (28fef4a99: EXP-003 section 2, the revised metric; 6b6003af4: the recorded refused probe) and of the merge 293df50f9; no measure run"
---

# PR-DAEO-rd0g-close-narrow: the narrow independent check of W2-15a's section 2 and refused probe

## Summary

A fresh independent-auditor session (`GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-rd0g`) checked the range `883e1ba6b..293df50f9` at head `293df50f9`. It read the range's two ticket commits and the merge that follows them, and judged them against the ticket's four KPI lines (S1 to S4) and against DEC-954 Q9, DEC-957, DEC-1171 (3), DEC-1186 (3), DEC-074 Q3 and DEC-1083. It ran no measure, pytest, `gov` command or network call. It did not open, list or stat the evaluation sets root.

**Verdict: pass.** Section 2 states everything S1's `Verify:` clause requires, as DEC-1171 (3) decides Q-2 (a). Nothing of the close run is dated before section 2's commit. The probe record holds the refusal text and no hidden content. The range says nothing about S2, S3 or S4 that is wrong or that weakens them. There are five findings (N1 to N5). All are rows and none blocks.

## Step 0: the sandbox check (EMG-d4b-launched.md)

- **(a)** `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-rd0g','w').write('x')"` **failed** as required: `OSError: [Errno 30] Read-only file system`, exit 1. A follow-up `ls` confirmed the file does not exist.
- **(b1)** `echo sandbox-trial | git hash-object -w --stdin` **worked**: exit 0, blob `1ae28402a109c3397a44b19239a00adfa9472eb0`.
- **(b2)** `git update-index --refresh` **worked**: exit 0.
- **Head:** `git rev-parse HEAD` = `293df50f9f9ced8a3bb3c2593e52eb4da263927c`, on `w2/W2-15a`.

## What was checked and found sound

### The range and the merge

- **The ticket's commits:** the first-parent history of `883e1ba6b..293df50f9` is exactly `28fef4a99` (parent `883e1ba6b`), then `6b6003af4` (parent `28fef4a99`), then the merge `293df50f9` (parents `6b6003af4` and `4bc0399fb`).
- **The merge brings nothing of this ticket's:** `git diff --stat 4bc0399fb 293df50f9` touches only `docs/research/EXP-003/w2-15a-baseline.md` (+50/−1) and `docs/research/EXP-003/w2-15a/probe-refusal.md` (+22).
- **Section 2's sources are unchanged across the range:** `git diff 883e1ba6b 293df50f9` is empty for `fixtures/evaluation/`, `src/gov/retrieval/measure.py` and `tests/acceptance/W2-61h/`.

### 1. Section 2 against S1's line

Each item S1's `Verify:` clause requires, as DEC-1171 (3) decides Q-2 (a), with where section 2 states it (lines at the head):

- **What counts as a hit:** lines 39–41. This matches the measure's own rule in `src/gov/retrieval/measure.py`:
  - path equal and lines overlapping, a found heading governing over `lines` (lines 20–26);
  - a family member counting only when its text holds the gold span's text (lines 36–43);
  - hit@5 as `rank <= 5` over the stacked items (lines 387, 390).
- **Who labelled the needed evidence, blind to the system's answers:** stated at lines 30–34. The attribution is incomplete for 20 of the 40 visible questions (N1).
- **Per-question recall in the stacked context:** `pieces_found` / `pieces_needed`, and `full_evidence` when every source is matched (lines 42–44). This matches `measure.py` lines 388 and 392–393.
- **The stacked context and its budgets:** lines 35–38 match `measure.py` lines 51–56 and 361–373:
  - an item's size is its text's length / 4, rounded up;
  - a call continues the last while a continuation exists and the budget is not reached;
  - defaults: batch size 10, bundle budget 6,000 tokens, stack budget 24,000 tokens (`measure.py` lines 522–524).
- **The corpus mean:** stated at lines 47–49. The table script that the section says computes it does not compute it yet (N2).
- **W2-61's measure, both figures, on the current set:**
  - **40 visible:** `git ls-tree --name-only 883e1ba6b fixtures/evaluation/memory-retrieval/visible/` lists 40 files, `q01.yaml` to `q40.yaml`, and the head has the same 40.
  - **39 hidden:** `HIDDEN_COUNT = 39` at `tests/acceptance/W2-61h/w2_61h_support.py:36`. h10's retirement is DEC-1171 (2).
- **The pass lines:**
  - hit@5 against 95 %, with CAP-10's 85 % the floor, and the all-evidence share against 99 % (lines 45–47). This matches DEC-1171 (3), DEC-957's MEMORY-SPEC-MAP ("95 % or more; 85 % is the floor") and `measure.py`'s `FLOOR, TARGET = 85, 99` (line 78).
  - The memory proof: mode `rerank` at a hidden hit@5 of at least 34 of 39, or 35 of 40 once the hidden half is back at 40 (lines 50–51), as DEC-1171 (3) decides. Naming the shipped path as the judged mode is a reasonable reading; neither S1 nor DEC-1171 (3) names a mode.
- **The hidden half in the record:** counts only, copied from the owner's operator's walled-run record, and never a question, an answer or a hidden file's text (lines 55–58). This is stricter than S1 allows (counts, ids, ranks and pass or fail), and matches DEC-1186 (3) Q3 (a). The walled run follows the recorded refused probe (line 58).
- **The five modes:** `rerank`, `lexical`, `semantic` and `fused`; the lighter reranker stands as "not installed", the line met in part (lines 52–54). This is DEC-1186 (3) Q1 (a).
- **On a miss:** at most three gaps named for W2-15b, each with the misses it is meant to reach, and S1's memory clause re-worded to "recorded against 34 of 39" (lines 59–61). This is DEC-1171 (3) and DEC-1186 (3) Q2 (a).
- **Pass 1's metric is kept, not rewritten:** the diff's one deleted line is the old heading. It became `### 2.0 Pass 1's metric … kept as history`, and the old text below it is unchanged.

### 2. Dating

- **Section 2's commit:** `28fef4a99`, author and committer date 2026-11-15T16:13:50Z. It is an ancestor of `6b6003af4` and of the head.
- **The range adds no raw output.** `git log --name-status 293df50f9 -- docs/research/EXP-003/w2-15a/` shows two adding commits only:
  - `fd637510d` (2026-11-03T22:36:51Z, "EXP-003 pass 1") added 27 files: the harness and every file under `raw/`. The record files' names carry their run times (`…20261103T214050Z`, `…T215033Z`, `…T220952Z`, `…T222922Z`).
  - `6b6003af4` added `probe-refusal.md`.
- **No branch holds anything else:** `git log --all -- docs/research/EXP-003/w2-15a/raw/` shows only `fd637510d`.
- **The five untracked, empty `raw/*.err` files** are dated 2026-11-03 21:30–22:29 UTC. They match pass 1's run times and `run_modes.sh`'s `2> "$RAW/measure-$MODE.err"`, so they are pass 1's empty stderr files.
- **Conclusion:** everything under `raw/` belongs to pass 1 (2026-11-03). Nothing in the record is close-run output dated before section 2. Section 6's `raw/stack-q14.json` is pass 1's, and S3's `Verify:` names it as the one baseline run.

### 3. The probe record

Read only, without following its path.

- **Content:** it holds the one call (a Read of a file name chosen not to exist), the time (16:13:58Z, after `28fef4a99`), the session, and the refusal text, whole: "File is in a directory that is denied by your permission settings."
- **No hidden content:** it records no name, count or text of the hidden folder, and no question, answer or count.
- **It is what S1's `Verify:` asks for:** a recorded refused probe read of the sets root's hidden folder, from a worktree (`/home/usain/gov-os-worktrees/W2-15a`).
- **It states its own limit:** the permission settings refused the call before the live hook ran (N4).

### 4. S2, S3 and S4

- **S2:** section 2 names the five modes, one run per mode and part, and the lighter reranker as "not installed". S2's `Verify:` says a missing row leaves the line "unmet"; DEC-1186 (3) Q1 (a) says "met in part". Both mean not fully met, so this is no contradiction. Section 2 cites the owner's decision.
- **S3:** section 2 keeps section 6 as S3's one baseline run, not re-run. This is S3's `Verify:` word for word.
- **S4:** section 2 names at most three gaps for W2-15b, each with the misses it is meant to reach, and the table script's re-derivation of the visible cells. Two caveats are rows: the table script does not yet do this re-derivation (N2), and the output folder is unnamed (N3).
- **No weakening:** nothing in the range states a lower bar or drops a measure.

## Findings

### N1: the visible half's labellers are named incompletely

- **What it is:** Section 2 (lines 32–34) says the visible half's labels were written by W2-61's question authors (Lens B), with the label fixes of DEC-1060 and DEC-1069 (1). Git history shows more authors than that:
  - Lens B wrote only q01–q20 (`8d09eb40d`).
  - W2-61h (D-8) wrote q21–q24 (`6dca09f0a`).
  - A session independent of the retrieval work, blind to results, wrote q25–q40 under DEC-1069 (4) and (8) (`c17dba7d8`, `b14015c34`).
  - Later blind re-labels and re-wordings go unnamed:
    - DEC-1066 (4) for Q09 (`f1a01dfe2`);
    - DEC-1067 (c) for Q03, Q16 and Q19 (`a9ef6f820`, `429a53ca2`);
    - DEC-1070 (13) for Q07 and Q14 (`55d1c0297`);
    - DEC-1124 for Q23 (`53affe533`);
    - q12's re-label by an independent test designer (`c48d7ce80`).
  - Every one of these commit messages asserts blind or independent authorship, so the blindness likely holds; the naming is what is incomplete.
- **How:** `git log --diff-filter=A 883e1ba6b -- fixtures/evaluation/memory-retrieval/visible/<q>.yaml` for q01, q24, q25, q33 and q40; `git log 883e1ba6b -- fixtures/evaluation/memory-retrieval/visible/`.
- **KPI line:** S1 ("who labelled each question's needed evidence, blind to the system's answers").
- **Scope:** in.
- **Ordinary work:** yes, because a section written from pass 1's text carries pass 1's 24-question attribution forward.
- **Consequence:** other (the record names its labellers incompletely; no figure, wall or work is affected).
- **Recommendation:** name the q21–q24 and q25–q40 authors and the later blind re-labels, preferably before the close run's first raw output. This is a factual correction, not a change of metric (DEC-802).
- **What would reverse it:** a source showing that q21–q40 and those re-labels were written by W2-61's Lens B authors.

### N2: the table script does not yet compute what section 2 says it computes

- **What it is:** Section 2 says the corpus mean of per-question recall "is computed by the record's table script" (lines 47–48), and that the visible cells "are re-derived from the raw records by `w2-15a/table.py`" (lines 57–58). At the head, `docs/research/EXP-003/w2-15a/table.py` (28 lines) does this:
  - it prints only hit@5 and full-evidence counts, and the first gold ranks;
  - it never reads `pieces_found` or `pieces_needed`;
  - it takes exactly one record per mode (`mode=path`).

  The ticket's claim note (step 3, "prepares the record's table") makes this work still to come.
- **How:** read `table.py` lines 1–28.
- **KPI line:** S1 (the corpus mean) and S4 (each figure re-derived by the record's table script).
- **Scope:** in.
- **Ordinary work:** yes, because the section describes the table script as it must be at the close, not as it is.
- **Consequence:** other (without the change, the corpus mean would be missing at the close; this is visible and fails closed, not open).
- **Recommendation:** update `table.py` before the close's table is built.
- **What would reverse it:** a `table.py` at the probed head that computes the mean of `pieces_found / pieces_needed`.

### N3: the documented harness and the output folder do not match section 2

- **What it is:** Section 4.1 still documents `bash run_modes.sh lexical semantic fused rerank`, and `run_modes.sh` has not changed since pass 1:
  - it targets `$HOME/gov-os-runs/D4B/m1/repo`;
  - it runs `--part all`, so it would run the hidden half from the CTO's own session (lines 20–23);
  - it writes `raw/measure-<mode>.txt`, `raw/measure-<mode>.err`, `raw/rerank-<mode>.log` and `raw/records-<mode>/`, the names pass 1's committed files already use.

  Section 2 says something different: one run per mode and part (`--part visible|hidden`), with the hidden figures copied from the operator's walled run. It names no separate output folder for the close run.

  So an honest re-run of §4.1 as written would do two things. It would overwrite pass 1's text files in the working tree (git keeps them, so no work is lost). And it would mix pass 1's 2026-11-03 records with the close run's in one folder, which makes "every raw output dated after it" harder to show. The five untracked pass 1 `.err` files would also be committed by a `git add raw/`.
- **How:** read `run_modes.sh`; `stat` of the five untracked `raw/*.err` files.
- **KPI line:** S1 (dating; the hidden half only from the walled run), S2 and S4 (raw output under `raw/`).
- **Scope:** in, but outside this range: the range does not change the harness.
- **Ordinary work:** yes, because §4.1 is the record's own documented command.
- **Consequence:** other (provenance and dating are muddied; the measure prints only ids, counts, ranks and digests for the hidden part, and `table.py`'s one-record-per-mode form refuses a mixed folder loudly).
- **Recommendation:** for the close run, use a fresh output folder (for example `raw/close/`) and a visible-only harness.
- **What would reverse it:** a close-run harness and output folder, named at the probed head, that differ from pass 1's.

### N4: the probe shows the permission-settings layer, not the live hook's sets-root rule

- **What it is:** The probe record says this itself (lines 19–22): the refusal came from the harness's `Read` deny (ACT-PERMISSIONS-2), which decides before `.claude/hooks/pretooluse.py` runs. So the probe shows the wall holds for that session, but it does not exercise the hook's own sets-root rule.
  - S1's original line text says "used only once the five-rule hook and W2-84 refuse it from every worktree".
  - S1's changed `Verify:` (DEC-1171 (3)) asks only for "a recorded refused probe read of the sets root's hidden folder from a worktree". That is met.
- **How:** read `probe-refusal.md` lines 11–22; this session's sandbox configuration also lists the hidden folder under read deny.
- **KPI line:** S1.
- **Scope:** in.
- **Ordinary work:** no, because reaching the hidden folder past the settings deny would need that layer removed or bypassed; that is a deliberate act, not ordinary work.
- **Consequence:** other (the record is honest about which layer refused).
- **Recommendation:** a row for the Wave 3 hardening pass (DEC-801).
- **What would reverse it:** evidence that the settings deny is absent in the sessions S1's wall must cover.

### N5: the commits were made by the lead as orchestrator, not by a research session

- **What it is:** DEC-1186 (3) ("a research session commits the revised metric section and the refused probe") and the ticket's claim note ("A research session (1) rewrites section 2 … (2) records one refused probe … from its own worktree") both name a research session. Both commits carry `Role: orchestrator`, and the probe record names its session as the ticket lead with `GOV_ROLE=orchestrator`.
- **How:** `git log -1 --format=%B` of `28fef4a99` and `6b6003af4`; `probe-refusal.md` line 5.
- **KPI line:** S1.
- **Scope:** in.
- **Ordinary work:** yes, because a lead doing a small record change itself is an ordinary shortcut.
- **Consequence:** other (S1's `Verify:` asks for a probe from a worktree, not a research role, and the content is unaffected; it is a departure from the owner's named order).
- **Recommendation:** record it for the CTO's or the owner's reading.
- **What would reverse it:** a CTO routing under DEC-1164 (18) or the owner's word that lets the lead make these commits.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "N1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "N2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "N3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "N4", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "N5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "N3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "N2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "N3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```

task: DAEO-rd0g
status: done (narrow check: pass, 0 blocking findings)
work_completed: step 0 (a refused, b1 and b2 worked); the range and the merge confirmed; section 2 checked item by item against S1's Verify, DEC-1171 (3), DEC-1186 (3), DEC-957, measure.py, HIDDEN_COUNT and the visible count at 883e1ba6b; the raw outputs dated from git history; the probe record read; S2 to S4 judged against what the range states
files_changed: none (read-only session; one git blob written by step 0's hash-object, as that check requires)
evidence: git diff --stat 4bc0399fb 293df50f9 (two files); git ls-tree at 883e1ba6b (40 visible); w2_61h_support.py:36 (HIDDEN_COUNT = 39); measure.py lines 20-56, 78, 341-412, 516-527; table.py lines 1-28; run_modes.sh; git log --name-status of w2-15a/ (fd637510d 2026-11-03 for every raw file); DECISION_REGISTER DEC-954 Q9, DEC-957, DEC-1171 (2)(3), DEC-1186 (3), DEC-074 Q3, DEC-1083
tests: none run (no pytest, measure or gov command, per the brief)
discoveries: table.py does not yet compute the corpus mean (N2); run_modes.sh and pass 1's raw file names would collide with a close run that reuses them (N3); 20 of the 40 visible questions were written by sessions other than Lens B (N1)
risks: a close run that reuses §4.1's harness unchanged would mix pass 1 and close-run outputs in raw/ and run the hidden part outside the walled run (N3)
lessons: a metric section revised for a larger set should re-check its provenance lines (labellers, scripts) against the new set's history, not carry the old set's forward
proposed_decisions: none
unresolved: none blocking; N1 to N5 recorded as rows
recommended_next_action: land; before the close run's first raw output, consider correcting N1's attribution, updating table.py (N2) and naming a fresh output folder and a visible-only harness for the close run (N3); these ride along under DEC-802, with no new round

```
?? docs/research/EXP-003/w2-15a/raw/measure-fused.err
?? docs/research/EXP-003/w2-15a/raw/measure-lexical.err
?? docs/research/EXP-003/w2-15a/raw/measure-rerank.err
?? docs/research/EXP-003/w2-15a/raw/measure-semantic.err
?? docs/research/EXP-003/w2-15a/raw/stack-q14.err
```

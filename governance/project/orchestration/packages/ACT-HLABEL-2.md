# ACT-HLABEL-2: the blind check and correction of hidden questions h03 and h08, and the re-anchor records (DEC-1069 (1), (6))

For the owner's operator, acting as the independent checker, in a plain terminal outside any Claude session. The
guard does not apply there (DEC-1068 (c), DEC-1069 (1)). **Nothing about these questions reaches the CTO's session.**
Report back only "done" and the dry run's counts line.

## Why
W2-61h's role audited the hidden half blind on 2026-11-04, against the rubric
`docs/research/memory-measure-audit/RUBRIC.md`. Its report is `docs/research/memory-measure-audit/HIDDEN.md`, in
general terms only. **Its general findings, to confirm or refute yourself:**
- **h03:** R1-INCOMPLETE, major, plus R1-DETAIL. A later standing decision, still in force, is the governing source
  for part of the answer and is not a source; and the answer holds a stale list. Recommendation: re-label.
- **h08:** R1-INCOMPLETE, major, plus R1-DETAIL; R7-MISSING-PIECE, major; R10-RECORD, minor. One caller in the same
  module is missing (it was there at the question's commit too), so the count is wrong; and a line number is stale.
  Recommendation: re-label, and record the re-anchor.
- **R10-RECORD, minor, on h08, h12, h16, h17 and h23:** these were re-anchored to the same fact at a new span, with no
  written reason. The old copies are only in dated backups, not in a retired folder.
  - Those re-anchors were the CTO's measure script (`repin_gold.py --write`, run before each measure). It moved a
    cited block's lines when the block moved unchanged, and kept a mode-700 backup each time.
  - From now on the script writes a reason line itself, into `REANCHOR-LOG-hidden.md` beside the folder (DEC-1069 (6)).

## The check (blind: read no measure result, no search result, nothing under `~/gov-os-runs/`)
1. Read `~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/h03.yaml` and `h08.yaml`.
2. For each, decide from the repository at `w2/integrate`'s head (`/home/usain/Dynamic-Agentic-Engineering-OS`,
   read-only) and its governing records (the Contract, the register with its superseding entries, the tickets, the
   code):
   - (1) Is the gold answer correct and complete today?
   - (2) Are the gold sources the places that state it? The governing source comes first, and is never a superseded
     decision.
   - (3) Does each entry hold one whole piece of evidence (R7)?
   - (4) Is the question answerable as asked?
   - Also check R11 (DEC-1069 (6)): if a question's answer changes with ordinary work (a count, a list that grows),
     note it in the file as `# volatile: its answer changes with ordinary work (DEC-1069 (6)); gold as at <commit>`.
3. **A label changes only where it is wrong, never to fit any result.** The form is DEC-1060's (see ACT-HLABEL-1).

## The correction
```
H=~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden
R=~/gov-os-eval/fixtures/evaluation/memory-retrieval/retired-hidden
cp -p "$H/h03.yaml" "$R/h03-pre-dec1069.yaml"; cp -p "$H/h08.yaml" "$R/h08-pre-dec1069.yaml"
# edit $H/h03.yaml and $H/h08.yaml in place, the format kept exactly; one README line each in $R/README.md
```

## The re-anchor records (R10)
The CTO's backups are `~/gov-os-eval/fixtures/evaluation/memory-retrieval/backup-hidden-<timestamp>/`, one per
measure since 2026-11-03.
- For h08, h12, h16, h17 and h23: find the earliest backup that holds the question's previous `lines:`.
- Add one line per re-anchor to `~/gov-os-eval/fixtures/evaluation/memory-retrieval/REANCHOR-LOG-hidden.md` (mode
  600), in the script's own form:
  `- <date> <id> entry <n>: lines [a, b] -> [c, d] at <commit>: the cited block moved unchanged (automatic re-anchor by repin_gold.py before a measure; backup <folder>)`.
- Write no question, answer or source text.

## The check after
```
python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b/repin_gold.py \
  ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden /home/usain/Dynamic-Agentic-Engineering-OS
```
It must print `unresolved: 0`. Send the CTO "done" and that one line.

## Rollback
`cp -p "$R/h03-pre-dec1069.yaml" "$H/h03.yaml"` (and the same for h08).

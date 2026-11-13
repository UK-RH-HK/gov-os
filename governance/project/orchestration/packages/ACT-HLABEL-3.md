# ACT-HLABEL-3: three minor fixes to the new hidden questions h26, h28 and h29 (DEC-1069 (8), the cross-check)

For the owner's operator, as the independent checker, in a plain terminal outside any Claude session. **Nothing about
these questions reaches the CTO's session.** Report back only "done" and the dry run's counts line.

## Why
W2-61h's role cross-checked h25-h40 blind against the rubric, version 2. Its report is
`docs/audit/memory-measure-new-hidden.md` in the repository, in ids and general reasons only.
- 13 may enter as written. None should be dropped, and no fault is major.
- **Three minor fixes, to confirm and apply yourself:**
  - **h26:** R3, minor. Re-word, so it is unambiguous and answerable as asked.
  - **h28:** R1, minor. Re-label the gold answer's text: it is incomplete or stale in part. Its sources stand.
  - **h29:** R3, minor. Re-word, as h26.
- A re-word changes what the search is asked, so these come before m6. The answer text of h28 is not scored.

## The fix (DEC-1060's form, as in ACT-HLABEL-1 and -2)
```
H=~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden
R=~/gov-os-eval/fixtures/evaluation/memory-retrieval/retired-hidden
for q in h26 h28 h29; do cp -p "$H/$q.yaml" "$R/$q-pre-xcheck.yaml"; done
# edit $H/h26.yaml, h28.yaml and h29.yaml in place, keeping the format exactly; one README line each in $R/README.md
```
- A label changes only where it is wrong, never to fit any result.
- Read no measure result, no search result, nothing under `~/gov-os-runs/`.

## The check after
```
python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b/repin_gold.py \
  ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden /home/usain/Dynamic-Agentic-Engineering-OS
```
It must print `unresolved: 0`.
- `re-pinned: 3` is expected: h02 entry 2, h16 entry 1 and h23 entry 1 moved unchanged. m6's own re-pin writes them,
  with a reason line each.
- Send the CTO "done" and that one line.

## Rollback
`cp -p "$R/<id>-pre-xcheck.yaml" "$H/<id>.yaml"`.

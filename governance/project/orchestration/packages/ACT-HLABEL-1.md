# ACT-HLABEL-1: the blind check and correction of hidden questions h02 and h24 (DEC-1068 (c))

For the owner's operator, acting as the independent checker, in a plain terminal outside any Claude session (the
guard does not apply there; DEC-1068 (c)). **Nothing about these two questions reaches the CTO's session:** the CTO
has never read them. Report back only "done" and the dry run's counts line.

## Why
- On 2026-11-04 at about 01:55, an independent auditor (W2-61h's role) checked four hidden questions blind under
  DEC-1067 (c). h07 and h11 were right; h02 and h24 were wrong.
- The guard refused that auditor's write to the sets root (DEC-953 item 2), so nothing was changed.
- **The auditor's general findings, to confirm or refute yourself:**
  - **h02:** wrong in its answer and its sources. A later standing decision brought back, in another form, what the
    gold answer says has ended; the gold source states only the earlier rule, so a second governing source is needed.
    The answer's "No" about the lock itself still holds, and the wording can stay.
  - **h24:** wrong in its alternatives. A standing decision names one form of the Contract as its authority, and that
    form is not among the gold sources; its two places that state the answer should be added, ahead of the two kept.
    The answer and the wording are correct.

## The check (blind: read no measure result, no search result, nothing under `~/gov-os-runs/`)
1. Read `~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/h02.yaml` and `h24.yaml`.
2. For each, decide from the repository at `w2/integrate`'s head (`/home/usain/Dynamic-Agentic-Engineering-OS`,
   read-only) and its governing records: the Contract `docs/contract/`, the register `docs/DECISION_REGISTER.md` with
   its superseding entries, and the tickets.
   - (1) Is the gold answer correct today?
   - (2) Are the gold sources the places that state it? The governing source comes first. A superseded decision is
     never gold.
   - (3) Should other sources that state it as fully be alternatives?
   - (4) Is the question answerable as asked?
3. **A label changes only where it is wrong, never to fit any result.** The form is DEC-1060's: see `git show
   68252f5c`, `git show 429a53ca` and `fixtures/evaluation/memory-retrieval/retired/README.md` in the repository.

## The correction (only for what you find wrong)
```
H=~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden
R=~/gov-os-eval/fixtures/evaluation/memory-retrieval/retired-hidden
mkdir -p "$R" && chmod 700 "$R"
cp -p "$H/h02.yaml" "$R/h02-pre-dec1068.yaml"     # the old label, byte for byte, before any edit
cp -p "$H/h24.yaml" "$R/h24-pre-dec1068.yaml"
# edit $H/h02.yaml and $H/h24.yaml in place, keeping the file's format exactly (the measure parses it)
# add one line per retired file to $R/README.md: the id, the date, the reason in general terms (no question or answer text)
chmod 700 "$H"                                    # the folder was found at mode 755 inside the root's 700
```

## The check after
```
python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b/repin_gold.py \
  ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden /home/usain/Dynamic-Agentic-Engineering-OS
```
It is a dry run that prints counts only. It must print `unresolved: 0`. Send the CTO "done" and that one line.

## Rollback
`cp -p "$R/h02-pre-dec1068.yaml" "$H/h02.yaml"` (and the same for h24).

**After it:**
- The CTO re-scores every kept run from its per-question ranks, without running again (DEC-1068 (4)).
- The next measure scores the new labels.

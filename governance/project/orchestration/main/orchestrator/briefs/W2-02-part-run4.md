You are the ticket lead for ticket `DAEO-zflj` (`W2-02`, "Record types: decision entry, audit report, adoption verdict, close record; core-schema green here"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-02` on branch `w2/W2-02`. You run the ticket loop for this one ticket and return one summary. You are a headless session: nobody answers questions while you work, and only your final message is read.

**This is run 4, the resume.** `git log --oneline -1` must show `2a35fd7b`, and `git status --short` must show nothing but sandbox placeholder files, if any (anything else: stop and return PACKAGES naming it). Read `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree: its "What the resume lead must do" holds, and this brief adds to it.

## Why you resume now: every close needs your close-record type

On 2026-10-20 at 15:53 W2-53 closed through `gov close`, the first clean close of Wave 2, and the close wrote its record `docs/close/DAEO-7rr2/CL-DAEO-7rr2.md` (frontmatter `id: CL-DAEO-7rr2`, `type: close`, `status: ACTIVE`, `state_class: AUTHORITATIVE`, `task: DAEO-7rr2`, `created`, `outputs`). On `w2/integrate`, `core-schema` (hard-block) is now RED on it: "unknown record type 'close'". Your branch defines the type (`template/governance/kernel/schemas/close.schema.json`), so until you merge, every later close is refused by its own `gov check`. W2-54's close stopped at the pre-close gate for this reason.

## The decision for this run (DEC-872, delegated, 2026-10-20; in the register after step 1's merge)

Your resume keeps its original scope: the merge-back, its re-verification, the `STANDALONE_TYPES` line, and a fresh probe. **The plan's widening of W2-02** (the full validator through check-jsonschema, lens G's planted ticket as a case, and DEC-844's `docs/imported/` out of the schema check) **moves to a follow-on ticket, W2-64, on the same paths after your merge.** Do not start it here.

## This run's order

1. **Merge `w2/integrate` into this branch** (DEC-750's form: `--no-ff`, `Task: DAEO-zflj`, `Role: orchestrator`, `Implements: DEC-441`; never `-s ours`; never drop a side). W2-54 (merged) copied your `audit-report` lines into `src/gov/check/schema.py`; if the `STANDALONE_TYPES` line conflicts, **resolve it to your line**, keeping every type both sides name. A conflict you cannot resolve keeping both sides is PACKAGES.
2. **The close record:** with the merge, `docs/close/DAEO-7rr2/CL-DAEO-7rr2.md` is in this tree. Check your close type against it, as the checkpoint's step 4 asks: `core-schema` must be GREEN on it with no schema change; if a field `gov close` writes is refused, that is a package (DEC-737 item 6), not a quiet widening.
3. **Verify in full:** one full rebuild, every suite in its own process (W1-41 and W1-30 alone), `tests/unit`, `gov check` (**`core-schema` GREEN here** is the point), and the pre-close gate's collection: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m pytest tests --collect-only -q -p no:cacheprovider` with no collection error (DEC-868).
4. **A fresh probe** (brief A3 with `JUDGEMENT.md`, `--effort max`, read-only) on the merged head: the close type, the standalone-types resolution and the merge-back. Commit its probe record under `docs/probes/DAEO-zflj/` only if it passes.
5. Return DONE.

---


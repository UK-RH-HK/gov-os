---
task: W2-94 (DAEO-g87r)
subject: q02 writer variant, version 2 (draft), judged against version 1
decisions: [DEC-1180, DEC-1178, DEC-1175, DEC-801, DEC-808, DEC-820, DEC-136, DEC-1014]
v1_sha256: 0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173
v2_sha256: 7aa6d88c3a7769c1abe34ffd54b8ced4f4110fb2208ed1f316d1a7c000b021b6
fixed_brief_sha256: d37834e08c86e24c0fdb1884c4f11164d734af4dcb4b3a5536bd20e3efc0085f
script: w2/W2-94-fix at 66dd6e77abbdc1d2b0a304991bf3cdb5e119d3f3 (indep_launch.py; indep-schemas/writer-result.schema.json)
---
# Review: the q02 writer variant, version 2

Reviewer: an independent session that wrote none of these files. This record is the only file I wrote. I opened
nothing under ~/gov-os-eval, no hidden folder and no guard-call log.

The guard refused this record at the requested path, `.gov-runtime/scratch/orchestrator/drafts/q02-variant-v2/review.md`
("a reviewer or auditor writes only its own review or audit record … (DEC-953 item 2)"). I did not retry or work
around the refusal. This copy is in the session scratchpad, which the guard allows. Copying it to the drafts folder,
or to `.gov-runtime/scratch/orchestrator/reviews/`, is the orchestrator's call.

Note on a path: the schema is at `governance/project/orchestration/tools/indep-schemas/writer-result.schema.json`
on w2/W2-94-fix, not at `governance/project/indep-schemas/`. That is the folder the script's `SCHEMAS` constant reads.

Classification: 8 findings, 0 blocking, 8 rows (all ordinary work, none fails open or loses work).

## 1. Verbatim copies (question 1): sound

I extracted each section from the fixed brief (`EXAMIN-writer.md`, d37834e0…; the copy in EXAMIN's launch clone has
the same hash) and from v2's §6, leaving out headings and the "(For this run …)" notes, and diffed them.
- §3, §4 (table and closing paragraph), §5 (items 1 to 8, with the category table and R1 to R10), §8 and §9: byte-identical.
- §7: the YAML question form is identical except for its 2-space indent, which comes from its position inside a list
  item in the fixed brief. v1 binds "section 7's question form" only. The fixed §7's other bullets (the visible and
  hidden halves, DRAW.txt) are rightly left out.

v2 says it copies §3, §4, §5, §7's form, §8 and §9, and it copies exactly those.

A sentence-level diff of v1 against v2's §1 to §5 and its last paragraph shows six changes and no others: the
version line and its new sentence; §1's binding list; §2's added input sentence; step 3's parenthesis; §5's output;
the last paragraph. Each is judged below.

## 2. Does an addition change v1's meaning (question 2)?

Sound: necessary or faithful.
- **The opening sentence, "You cannot read the fixed writer brief itself":** true. The walls' `tree-exclude.txt` in
  the launch clone leaves out `governance/project/indep-briefs/**`, and the wall stages only the variant as brief.md.
- **§1 adds "section 8's words for your result":** faithful. v1's `{"by_kind": {...}, "by_area": {...}}` can only be
  filled with §8's words. The schema's closed `by_kind` and `by_area` objects refuse any other key (20 "schema").
- **§2's input list:** necessary, and corrects v1's account. `plan_fix` stages `input/sample.json` on every fix
  run, not "for this case only". `input/selection.json` is always written (WALL_FIXED). Its `sample` is `[]`,
  because `resolve_brief` sets `sample_n` to 0 when the variant names no `sample:`. "Only its `last_audit` matters"
  stops the writer from taking selection.json's `commit` (the launch PIN) as the question's `commit`, which agrees
  with §2's COPY-HEAD rule.
- **Step 3, "use it for this case only":** keeps v1's restriction on use; only the statement about staging changed,
  to match the script.
- **§5's word lists:** the same as fixed §8 and the schema. "`contract` and `kernel` 0 or left out" is equivalent
  to "stay 0", because the schema requires no key inside either object and the sums do not change.
- **"Nothing else in `out/` when you deliver":** necessary. `deliver_fix` refuses with 20 "entries" unless `out/`
  holds exactly `q02.yaml` and `result.json`. v1 already said "conflicts.md only if you stop".
- **§5's stop form:** necessary. The fixed brief names no `stopped` word anywhere. The script ends a run with 21 only
  on a word from `STOPPED[1:]`. v1's form (`questions: 0`, no word) ends with 20 "fix_result" (reproduced, below).
- **The §9 word mapping:** a one-question reading of each fixed condition. The conditions themselves are unchanged
  ("fewer than 14" becomes "neither step 2 nor step 3"). The words matter only for the counts.
- **"Step 3 first, then `decisions-conflict`":** faithful. v1's step 3 itself names "two documents conflict with
  nothing to settle it" as a reason to replace, so for q02 v1 already put the replacement before fixed §9's conflict
  stop. For a replacement path, R1's "do not use the fact" means skip it and go on down `sample`, which is what
  "no further fitting path" encodes.
- **The §4 note, "a file opened by mistake and left unused does not make you stop":** faithful. The fixed §4 says
  "even if you go on", and fixed §9 stops only when a forbidden read would be *needed*.
- **The last paragraph:** necessary. DEC-1180 (2) says "There is no checker run". `deliver_fix` itself replaces
  `hidden/q02.yaml`, and `pack` keeps the old file in the run's tar as `replaced-hidden/q02.yaml`. The paragraph
  informs; it directs nothing.

No addition is a new rule that changes what the writer may read, what it writes, or when it delivers or stops,
beyond what the wall, the script or DEC-1180 (2) force. F1 to F3 below are the places where a note puts a forced
narrowing in words. Each is a row.

## 3. Result words and stop form against the script (question 3): sound

I ran the branch's own `check_result` and `deliver_fix` on hand-made `out/` folders in a scratch folder, with a
planted `hidden/q02.yaml` (no real set content):

| out/ as v2 directs | outcome |
|---|---|
| `q02.yaml` + `{"questions":1,"action":"corrected","by_kind":{"location":1},"by_area":{"code":1}}` | delivered; hidden q02 replaced |
| the same with `replaced`, and `fact:0`, `contract:0`, `kernel:0` | delivered |
| `conflicts.md` + stop form, for each of `form-not-writable`, `input-missing`, `input-malformed`, `decisions-conflict`, `forbidden-read-needed` | refused 21 "stopped"; hidden q02 unchanged |
| delivery plus `conflicts.md` (what fixed §4 alone would produce) | refused 20 "entries"; unchanged |
| v1's stop form (no word) | refused 20 "fix_result"; unchanged |

In `build_and_run`, a Refuse 21 from `check_result` becomes status `stopped` with exit 21. The schema leaves the
top level open, so `action` passes.

## 4. Walls (question 4): sound

Every read v2 directs is inside the wall folder (`input/q02.yaml`, `verdict.txt`, `sample.json`,
`selection.json`) or inside the tree (`REPO`, and `COPY-HEAD.txt` in the scaffold, which the tree keeps). Every write
v2 directs is `out/q02.yaml`, `out/result.json`, or `out/conflicts.md` on a stop. Round 1 drew `sample.json`'s paths
from tracked paths minus the tree's exclusions, so every path in it exists in the tree. The copied §4 table and v1's
§4 "Never" are unchanged and still forbid the rest of the set, the sets root, the CTO's scratch and memory's search.
Nothing in v2 leads outside the folder and the tree.

## Findings

**F1 (row): the §5 note says items 1 and 3 and R5 are kept "by changing no other question and keeping q02's
category".** The note tells the writer to take item 3's set-wide counts as met. They may not be met: a q02 marked
`keyword: true`, or a replacement whose governing source is not code, can push the set past "at most 4 keyword" or
below "at least 8 code". The writer cannot see the set, which v1's §4 also forbids, so v1 bound a rule the writer
could not check either; v2 makes that explicit as a claim.
- Ordinary work: yes, because a corrected or replaced q02 may need `keyword: true` under R2.
- Consequence: other (the set's spread, not a wall or a delivery).
- Reversed by: evidence that the round-1 set has slack on each count (fewer than 4 keyword, more than 8 code), or
  that the post-run check counts the spread.

**F2 (row): the §5 note reads "a path is the governing source of at most one question" as "not the governing source
of q02 as delivered".** A replacement drawn by step 3 may take a path that already governs another question of the
set. This is forced by the wall, since the writer may not read the other questions, but it narrows the fixed rule.
- Ordinary work: yes, because step 3 is a normal branch of the order.
- Consequence: other (possible duplicate source; R8 is at risk only if the same fact is asked).
- Reversed by: a reading of v1's "the next path of the original set's `sample`" as "after the last path round 1
  used", with that point knowable to the writer. Under that reading every later path is unused.

**F3 (row): when the writer delivers, a file opened by mistake is recorded nowhere.** The fixed §4 asks for its
path class in `conflicts.md` "even if you go on". v2's note drops that record on delivery, because `deliver_fix`
refuses 20 "entries" for any extra file (reproduced). v1's own "conflicts.md only if you stop" already said the same,
so the change is from the fixed brief, not from v1.
- Ordinary work: yes, because a sample path can carry an eval-like name.
- Consequence: other (a lost audit note; a mistaken read is still neither used nor delivered).
- Reversed by: a top-level count key accepted by the schema and named by the brief, which would make the record
  possible without a third file.

**F4 (row): v2 makes the `last_audit` stop live.** v1 bound fixed §9's condition 2 only by reference, which the
writer could not read; v2 states it and points the writer at selection.json. The copy is faithful, and today
`~/gov-os-runs/indep/AUDITS.log` does not exist, so `last_audit` is null. If an auditor delivery appends to
AUDITS.log before the fix run, v2's writer stops with `input-malformed` for a reason unrelated to q02.
- Ordinary work: yes, because memory-audit auditor runs share that runs folder.
- Consequence: other (fails closed: exit 21, nothing lands, the run is repeated).
- Reversed by: AUDITS.log still absent when the fix run starts, or the operator's commands checking for it first.

**F5 (row): the §9 mapping overlaps.** When q02's fact conflicts and every later fitting path in `sample.json` also
conflicts, both "neither step 2 nor step 3" (`form-not-writable`) and the `decisions-conflict` line apply. Either
word ends with 21 and only the counts differ.
- Ordinary work: yes, because the case is rare but reachable.
- Consequence: other (a counts label only).
- Reversed by: evidence that nothing reads the `stopped` word beyond the counts.

**F6 (row): a cross-reference points at a section that was not copied.** The copied §5 item 2 says "A scaffold path
(section 2)". By §6's preamble, that means the fixed brief's §2, which the writer cannot read. v2's own §2 names the
same scaffold, so the writer can resolve it.
- Ordinary work: yes.
- Consequence: other (wording only; the wall's tree still holds the scaffold, and §2 says it is never a source).
- Reversed by: the preamble read as letting v2's own §2 stand in for the fixed §2.

**F7 (row, for the orchestrator): DEC-1180 (2) names v1 (0703aebf, DEC-1178 (5)), to run "byte for byte
unchanged".** Running v2 needs the owner's approval of v2 recorded against DEC-1180 (2) and DEC-1178 (5), its line in
the walls' APPROVED file, and a new launch-clone commit for `--commit`. Without the APPROVED line the launcher refuses
with 10, so this fails closed.
- Ordinary work: yes, because the CTO could bring v2 as a plain re-run.
- Consequence: other (governance precondition; fails closed).
- Reversed by: an owner decision already recorded that approves v2 or changes DEC-1180 (2).

**F8 (row, unchanged from v1): §1 says an ignored instruction is "counted in your result", but the result form has
no key for it.** The text is unchanged from v1 and the fixed brief. A writer that adds a top-level key still passes,
because the top level is open.
- Ordinary work: yes.
- Consequence: other (a count that may go unrecorded).
- Reversed by: a named key in the form, or that sentence removed.

## What I probed and found sound

- v1's hash is 0703aebf…, which matches the approved one.
- The fixed brief is the same file in both places.
- §3, §4, §5, §8 and §9 are byte-identical copies; §7 differs only in indent.
- Every v1-to-v2 change is accounted for by the wall, `plan_fix`, `check_result`, `deliver_fix`, `pack` or
  DEC-1180 (2).
- `selection.json`'s empty `sample` and null `last_audit` hold today.
- The delivery passes and every stop word ends with 21 (reproduced).
- v2 directs no read outside the folder and the tree, and no write outside `out/`.

```verdict
verdict: PASS
blocking: 0
reviewed_sha256: 7aa6d88c3a7769c1abe34ffd54b8ced4f4110fb2208ed1f316d1a7c000b021b6
```

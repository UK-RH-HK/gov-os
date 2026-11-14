# DEC-1164 final: patches for the CTO to review and apply

Built 2026-11-13 by a product-spec helper from `drafts/dec-1164-dif-supersede.md` (the draft; its §4 pairs are read from it by
`build.py`) and the owner's six corrections ("yes DEC-1164, with your five corrections and one more"). Nothing here is applied or
committed; the helper wrote only in this folder (patched copies for the checks went to the session's scratchpad).
`python3 build.py --tmp <empty folder>` rebuilds every file below from the current tree and stops, naming it, if any target text is gone.

All patches are checked with `git apply --check` from `/home/usain/Dynamic-Agentic-Engineering-OS` against the tree as it stands
(branch `w2/integrate`, with the uncommitted register, DIF and ticket edits in it): each applies cleanly. They are plain unified
diffs with `a/` and `b/` paths: `git apply <file>` from the repository root.

## The files

| File | What it is | How it is used |
|---|---|---|
| `entry.md` | DEC-1164's final entry (status ACCEPTED), then the version row `0.551`, "Next free id: DEC-1171" | Paste the entry into `docs/DECISION_REGISTER.md` after DEC-1163's entry and **before the line `### DEC-1165 — gov context's ceiling`** (DEC-1164 keeps its id; DEC-1163 now sits directly before DEC-1165), with a blank line either side. Append the row after the register's last row (0.549 now; your 0.550 for DEC-1170 first). |
| `marks.patch` | The DEC-866 marks: 31 hunks on 31 entries' status lines, matched by heading and text, not line number | `git apply` in the same commit as the entry. Includes DEC-1157's mark for (23) (joined to its (4) mark in one `Changed by`) and DEC-1093's mark (see correction 1). |
| `marks-extra.patch` | Optional, two lines outside the draft's list (see Discoveries 2) | Apply if the CTO agrees; independent of `marks.patch` (checked in either order). |
| `dif.patch` | `DECISIONS-IN-FORCE.md` (the draft's §3 plus the (23) lines and the DEC-1093 change) and `ARCHIVE-SUPERSEDED.md` (a new section D at its end) | `git apply`; one patch, two files. The DEC-1164 line goes after the DEC-1159 bullet (before DEC-1168's), so lines the CTO appends at the end of the DIF later (DEC-1160 to DEC-1163) do not collide. |
| `prompt.patch` | `governance/project/prompts/w2-orchestrator.md` at `e93d846a8`: §4's 30 pairs plus corrections 4, 5, 6; three lines of context | For the owner's operator (`operator-message.md`). 11 hunks; 29 insertions, 39 deletions. |
| `prompt-U1-phone.diff` | The same change with one line of context, for the owner to read | Reading only (it also applies cleanly). |
| `operator-message.md` | The exact steps: checks, `git apply --check`, `git apply`, the grep checks (expect 1, 2, 1, 0, 9), the commit with the four trailers, the undo | Send to the owner's operator. Rehearsed in a throwaway repository. |
| `build.py` | The builder (reads the draft and the tree; asserts each old text occurs once) | Rerun it if the tree moves before you apply. |

## Where each correction is

1. **W2-139 and W2-140 closed, so DEC-1093 (1)'s close form is spent.** `entry.md` item (1) (the sentence replaced as you worded it; it is in
   "Not kept (spent)"), and, because "spent" entries get marks and DIF lines in this entry's own scheme, also: item (7)'s list, the status line's
   "Changes (spent)", `marks.patch` (DEC-1093, `Changed by: DEC-1164 (1), (7)`), `dif.patch` (the DEC-1093 bullet no longer says they "merge and
   close in one batch"; the marker "recommended to supersede" removed; the DEC-1164 line in "Lifted"; section D of the archive).
2. **The cache-write ACT withdrawn.** `entry.md` item (3): "the cache-write ACT of DEC-1163 (9) was withdrawn by DEC-1167 (7) (it changed
   only the error text); sandboxed searches name the true cause since the reranker log fix (79159cd44)." The DIF line for A15 never named the
   cache ACT, so `dif.patch` needed no change for it.
3. **Status ACCEPTED, version row, Basis.** `entry.md` line 2 (status as you worded it, with `(4), (5), (9)-(19), (23) standing`: see Discoveries 1), line 28
   (the Basis quotes the owner's words verbatim), line 34 (`| 0.551 | 2026-11-13 | ... DEC-1164 (...) ... Next free id: DEC-1171. |`).
4. **"Nothing else starts" paragraph deleted** with DEC-946's priorities: `prompt.patch`, the hunk at HEAD line 92 (the 475-character line is a `-` line;
   the new "Order (DEC-1088, ...; DEC-946's priorities superseded by DEC-1164 (6))" bullet stays and already carries "an idea not filed goes to
   `docs/plan/WAVE_3_PARKING.md`" and "If 18 November is at risk, bring what to cut"). What goes with it: "the tools review's auditor, the STATE
   spot-check and W2-83b run in spare capacity only" and "stagger lead launches by a minute or two (`tools/lead_chain2.sh`)". The entry's (6) already
   lists "nothing else starts", the staggered launches and the frozen nightly as superseded, so entry and patch agree.
5. **The pre-close gate paragraph reduced to one line**, as you worded it: `prompt.patch`, HEAD line 361 (patched line 351):
   `- **The pre-close gate (DEC-868):** lifted on this repository with the close windows (DEC-953; DECISIONS-IN-FORCE, "Lifted"); built into `gov close` in the product (W2-07).`
   **"Your own record edits (owner, standing, DEC-868), until the hooks are back on (W2-08)"** (HEAD line 362, patched line 352) **is left unchanged.** Which:
   the DIF does not list that paragraph as lifted; but its "Lifted" section (line 146, DEC-953) lists `record_checks.sh` among what **ended**, and DEC-868's
   status says "Lifted by DEC-953 (item 1) as a gate on this repository's own development" for the whole entry. The paragraph is therefore half live:
   its record-checks half (`record_checks.sh` before a record commit) conflicts with the DIF, while its placeholder-scan half (DEC-893, `placeholder_scan.py`)
   and the "close once" sentence are named nowhere as lifted. Per your rule (keep unless the DIF lists it as lifted) I kept it whole and say so here for your decision (Unresolved 1).
6. **The owner's asleep clause**, "unless the owner has said they are asleep (DEC-1156 (8)); then it waits for the morning package":
   - In the prompt after the edit (2 places; the third check string of `operator-message.md` counts them): **patched line 223** (HEAD 230), "Decisions during the day":
     "Every decision that stops or delays a lead goes at once, at any hour (DEC-1157 (1)), unless the owner has said they are asleep (DEC-1156 (8)); then it waits for the morning package; any other blocking P1 goes between 07:30 and 02:00 ..."; and **patched line 208** (HEAD 215), "The morning package":
     "From the end of the owner's day to 07:30, nothing pings but an emergency and a decision that stops or delays a lead (DEC-1157 (1)), unless the owner has said they are asleep (DEC-1156 (8)); then it waits for the morning package." (I put the emergency first so the "unless" binds only the lead decision: an emergency still pings at any hour.)
   - In the prompt, **checked and not changed** (they do not say a lead-stopping decision goes or pings at once at any hour): HEAD line 207 (the package cap: "any package a lead waits on bypasses the cap"), 211 (the (b) ACT in the quiet hours, "once the owner's yes is recorded"), 210 and 231 ("a ping only when work waits on the owner"; the general ping rule), 224 and 229 (emergencies, which do ping at any hour). Say if you want the clause in 210/231 as well.
   - In `entry.md`: item (17) (the call a lead waits on: the push, then the clause); item (11) (one added sentence outside the quoted rule: "Where a lead waits on the owner's yes itself, the push is DEC-1157 (1)'s, subject to (23)"; (11) itself does not push, the yes being already recorded); item (23) as you gave it; the Under (DEC-1156 (8)), Changes (DEC-1157 (1)) and Basis; item (21) (the prompt places).
   - In the marks: DEC-1157's mark (23), DEC-991's mark and DEC-949's mark (their texts now carry "unless the owner has said they are asleep").
   - In `dif.patch`: the DIF's R-11 line ("Every decision that stops or delays a lead comes to the owner at once", DIF line 36), the quiet-hours line (38), the "call a lead waits on" line (B17, 42), "Lifted" (161, DEC-1156 (8): "the asleep clause restored"), DEC-1156's line (679, "restored by DEC-1164 (23)"), DEC-1157's summary line (688), and the DEC-1164 line.

## The draft's §2 and §3 items I could not apply

None. All 30 marks found their entry once by heading, and each status line took its append (the register has moved since the draft: DEC-1164's heading
is absent and DEC-1163 sits at line 14924, directly before DEC-1165). All 23 §3a replacements, the DEC-1086 deletion, the DEC-1087 replacement, B9's added bullet
and the two §3b additions applied, each old text found once. Differences from the draft's text, all consequences of the corrections: the DEC-1093 line (correction 1);
DIF line 4 now says register v0.551; B17's line carries the asleep clause; the DIF/archive carry DEC-1093.

## Discoveries

1. **(23) standing.** Your correction 3 reads "(4), (5), (9)-(19) standing"; item (23) says "(standing)" in your words, so the status line and the heading read
   "(4), (5), (9)-(19), (23) standing". Drop ", (23)" in three places if you meant it otherwise (status line, heading, DIF's DEC-1164 line).
2. **Two stale lines outside the draft's list** (`marks-extra.patch`): DEC-1156's status ("Changed by: DEC-1157 (1) (item (8) superseded)") gets
   ", DEC-1164 (23) (item (8) restored ...)" because (23) restores (8)'s clause; and DEC-1165's status ends "DEC-1164 is held: drafted, PROPOSED, waiting for the owner's reading", which
   is false once DEC-1164 is accepted: it becomes "DEC-1164 was held until the owner accepted it (2026-11-13, ~16:00)". Your call; both are marks of the kind DEC-866 asks for.
3. **START-NEXT-SESSION.md line 70** also states the rule ("Decisions that stop a lead go to the owner at once, at any hour (DEC-1157 (1)), as a full package with a push; no quiet-hours wait for them.") and is the CTO's, uncommitted in the tree, outside my paths: add "unless the owner has said they are asleep (DEC-1156 (8)); then it waits for the morning package". Its line 6 (next free id: DEC-1171) and its item 2 (the draft's §3c) are also yours.
4. **Remaining DEC-946 mention in the prompt:** the re-plan line (patched line 86) says "ordered by DEC-946"; the re-plan blocks it heads are DEC-941's and spent in practice, but the sweep did not list them and I left them.
5. **The marks count.** The draft said 30; with DEC-1093 (correction 1) it is 31 entries; (23) rides in DEC-1157's existing row, so no extra hunk. The version row says "31 entries".
6. **Checks.** `git apply --check` on the tree: marks, marks-extra, dif, prompt, prompt-U1-phone all clean; marks then marks-extra applied in sequence on a copy: clean. `placeholder_scan.py`: `entry.md` 0 hits; patched copies of the register (entry inserted, row appended, marks applied), DIF, archive and prompt: 0 hits each (and 0 on the originals). Run directly on the `.patch` files the tool also looks for angle slots and reports template words that were already in the lines the patches rewrite (`<id>`, `<W2 id>`, `<port>`, `<manifest sha8>`, `<ticket>`...); none is in text written here (`entry.md` has no `<`).
   Prompt after the patch: the greps of `operator-message.md` give 1, 2, 1, 0, 9; the prompt is 370 lines (379 before).

## Unresolved (for the CTO)

1. The "Your own record edits (DEC-868)" paragraph: keep whole (done, per your rule), or trim to its placeholder-scan and "run the close once" parts because the DIF lists `record_checks.sh` as ended (DEC-953)? I recommend asking the owner in the same message; the trim is a three-line change in one more pair if wanted.
2. Whether to apply `marks-extra.patch`.
3. The order of commits: the register entry (and marks, DIF, archive) first, then the owner's operator commit of the prompt (it cites DEC-1164).

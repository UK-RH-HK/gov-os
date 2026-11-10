- **sandbox_check:** Passed. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-149` failed with `OSError: [Errno 30] Read-only file system`, as required. (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109…` and `git update-index --refresh` exited 0.
- **ps_check:** I ran `ps -eo pid,args` on its own, without the pipe (DEC-1080). It shows only my shell and `ps`: no ollama or llama-server process of mine.
- **task:** DAEO-52ku (W2-149): the narrow, independent, read-only review of F36 and F38 closed (S23 and S27 changed; DEC-1112 (3), DEC-1113 (2)), on `w2/W2-149-sgx` from `9699bbbc9bc1` (w2/integrate, which has not moved since) to the head `bdda27d28148`.
- **status:** DONE. READY by `verdict.py`. There is one finding (F40): in scope, ordinary work yes, consequence other. Nothing blocks.
- **work_completed:** I read the ticket's S23 and S27 lines and its notes; JUDGEMENT.md, EMG-common.md, the step-0 file, INTENT-DEC-1052.md and the register's DEC-1065, DEC-1112 and DEC-1113; the two earlier reviews (f18 for F36, v3-r1 for F38); the approved briefs of the overlap auditor and both labellers; the diffs of the three commits; the launch script's staging, merge, labeller-2 check, delivery, tree build and manifest code; the template's `kinds.yaml`, `tree-exclude.txt`, settings template, `CLAUDE.md.tmpl` and hook; and the new and revised acceptance cases with their helpers. I ran five in-memory probes using the launch script's own code.
- **files_changed:** None in any tree. `git status --porcelain` was empty at the start and is empty at the end; HEAD was `bdda27d28148` both times. Outside the trees I wrote only step 0's blob and index refresh.
- **evidence:** At the head the launch script is `90b943aef8be`, `kinds.yaml` is `ddd84ae25910` and `tree-exclude.txt` is `e8395088167e`, as the evidence states. The range touches only the script (one line), the template's auditor entry, the unit file, the evidence and `tests/acceptance/W2-149/**`. Of 3,867 tracked files, the auditor's tree holds 3,149, each other set-up A tree 3,647, and a brief with no entry 3,725. My `$TMPDIR` at the end: `du -sh` 20K, `du -s --inodes` 8, all the harness's own entries.
- **tests:** I ran no pytest case, because the role says to re-run nothing the lead ran; so the DEC-1012 exclusion left nothing out. I accepted the lead's run outside the sandbox at `bdda27d28148`: 362 passed, 0 failed, and the 3 live cases passed. The 362 reconciles: 206 non-live acceptance cases (the earlier 197 plus the 9 in the new file) and 156 unit cases. The designer's 6 red cases are each red for the reason the README states.
- **discoveries:** (1) No file in the auditor's tree states the tell at the head. (2) W2-149's review records live in the main tree's `.gov-runtime/scratch/orchestrator/reviews/`, outside every tree. Other reviews are committed in `governance/project/orchestration/reviews/`, which every tree holds. (3) The script's hash changed as well as the `kinds.yaml` line: `95fe78dd49bb` → `90b943aef8be`.
- **risks:** (1) F40. (2) The rebuild of ACT-W2-149-INSTALL-1 must move both hashes: the `kinds.yaml` line and the pinned script hash, meaning `apply.sh`'s order check and the after-list's comment. The third build moved both, but the ticket's last note names only the `kinds.yaml` line. Moving only that line makes `check` refuse, so the mistake fails closed. (3) What remains of F36 is the labels' own content (check 1). The package should say that, not that "no side can be told apart".
- **lessons:** A word search over a tree has to fold line breaks. My first pass missed DECISIONS-IN-FORCE.md's "rule / script", which is split across two lines; the second pass found it.
- **proposed_decisions:** For the CTO, F40 is a row and needs no round. Two options. (a) Before the overlap auditor's first real run, dry-build its wall at the real pin and search its tree for the tell, as I did here. This is my recommendation, with medium-high confidence: it is a one-off, read-only check. (b) Build the auditor's tree from the four places its brief reads, which needs a script and template change and another ACT rebuild. In either case, keep every record that describes the dispute sides, this one included, under `.gov-runtime/`, `.tickets/` or `packages/`.
- **unresolved:** Whether a real auditor would guess that "the class-14 side with no clause is a script's" without any file saying so cannot be tested without a live session.
- **recommended_next_action:** READY by `verdict.py`, no round (DEC-1010, DEC-802); merge in one command. Then rebuild ACT-W2-149-INSTALL-1 with both hashes moved (`kinds.yaml` `ddd84ae25910`, script `90b943aef8be`) and carry F40 into its procedure as a row, with option (a).

---

**Identity:** HEAD `bdda27d28148` on `w2/W2-149-sgx`, clean at the start and at the end. w2/integrate is still `9699bbbc9bc1`, so the merged tree will equal the head's.
**task:** DAEO-52ku
**decisions:** DEC-1112 (3), DEC-1113 (2), DEC-1099 (1) Q5, DEC-1101 (2)-(3), DEC-820, DEC-801, DEC-802, DEC-808, DEC-1010, DEC-1014, DEC-1064, DEC-1065 (1), DEC-1073, DEC-1080. I found no superseded or PROPOSED rule in use.

**Deviations from the brief's rules, named:**
- My one `git diff` was the range's `--stat`. I read the three commits with `git show`, one commit per call, never a range.
- I read the template folder with the Read tool, except for one Grep tool call over two of its files (`CLAUDE.md.tmpl` and `wall_hook.py`).
- No Bash line named the template folder; my programs took its name from the launch script's own constant.
- Step 0's pipe is the brief's own command.
- The probes were inline `python3 -I -B -c` programs. I made no Write tool call, and nothing was refused.
- I did not run `gov retrieve`; I searched the register with Grep instead.
- The hidden-half rule held. I read file contents only for files that survive `tree-exclude.txt` (which leaves out `fixtures/evaluation/**`), and skipped every path with a `hidden` part. Elsewhere I listed names only.

## Checks 1–3

**1. F36: every side's reason is empty and x/y stays in the seeded order. Pass.**
- **The staging:** for every dispute, both sides' `reason` is set to `""`, on copies of the two labels. The x/y draw is unchanged: `random.Random(seed)`, one draw per case, in id order.
- **The probe:** I drove the script's own merge, labeller-2 check and staging (800 actions, 32 disputes).
  - Every reason is `""`, and neither labeller's reason text appears in the file.
  - No `how` field appears.
  - Each side equals its labeller's label, `rule_class` and `clauses`, in the seeded order, and the map matches.
- **The forms are the same on both sides, in all 32 disputes:**
  - key order `label, rule_class, clauses, reason`, even when labeller 2 wrote its keys in another order;
  - `rule_class` an integer on both sides (labeller 2's string `"14"` is stored as 14);
  - `clauses` a list of strings;
  - the same JSON spacing and escaping;
  - lines in id order.
- **The labels files keep the real reasons:** the blanking works on copies, so the flagged lines in `owner.jsonl` still carry both reasons.
- **What remains:**
  - **(i) The labels' own content.** In a dispute over a line the first labeller's script kept, that side is class 14 with whatever clauses the script writes, often none. The other side is a hand label of class 1–13.
    - In my model, the only class-14 side in a dispute was labeller 1's in 25 disputes and labeller 2's in 7. With every reason blanked, class 14 no longer marks the script's side for certain.
    - If the script writes no clause and both hand labellers always cite one, the only side with no clause was labeller 1's in 23 of 23 disputes. Neither labeller's brief requires a clause for class 14, so whether this happens depends on the labellers.
    - The auditor's input is both labels with their clauses (DEC-1113 (2); its brief, sections 2 and 4), so the launcher cannot remove this.
    - To name a labeller from this pattern, the auditor would need the merge rule, and nothing it holds or may read states that rule (check 2).
  - **(ii) The seed.** `seed.txt` is in the wall, and the brief says the order is drawn from it. The exact rule appears only in excluded files, and the auditor has no tool that runs code.

**2. F38. Pass.**
- **The auditor's tree at the merged head:**
  - I applied the launch script's own exclusion code, `tree-exclude.txt` and the real template entry: 3,149 files survive.
  - None of them lies under the six globs. Left out: 218 tickets, 270 package files, the launcher, 18 W2-149 acceptance files, 2 unit files and the evidence.
- **The search:** I searched all 3,149 files for the tell's wording, first line by line, then with line breaks folded.
  - Terms: the script's side, a class-14 side, `label_rules`, rule script, labeller 1's script, an empty or blanked reason, which side or which labeller, sides told apart, `how` with script, no clause, x is labeller, the map file, F21, F36 and F38.
  - Nothing states which dispute side is which labeller's.
  - The only set-up A lines left:
    - DECISIONS-IN-FORCE.md's wiring entry: "labeller 1's round-2 delivery refused (20) unless every hand-label action has one" and "exit 18 for a rule script that cannot run confined";
    - the counts schema's `label_rules.py` key;
    - the register's DEC-1099 Q5, DEC-1101 and DEC-1113, which name the labellers and the 10 % overlap.
  - These say that the first labeller has hand labels and a rule script. They do not say what its lines look like or which side is whose. Every other hit is unrelated.
- **The auditor's wall:** its brief, `CLAUDE.md`, hook, settings, `WALL.json`, `half.json` and `tickets.jsonl` hold nothing of the labellers except the two labels. The map is written only at delivery.
- **The other trees:**
  - Writer 1, writer 2, labeller 1 and labeller 2 are unchanged, at 3,647 files each.
  - Each holds what its brief names: `packages/SANDBOX-GUARD-EXP-1.md`, the declaration, all 218 tickets, the 6 role files and the 286 Contract files.
  - A brief with no entry keeps every file under the six globs.
- **What the auditor keeps:** the register, the Contract, the path map and the held-out list. Its `input/tickets.jsonl` is still read from git at the commit, not from the tree.

**3. No regression. Pass.**
- **The change:** in `kinds.yaml`, only the auditor entry changed: its `tree_exclude` and one comment line. The other four entries are byte for byte the same, and so are `tree-exclude.txt` and the schemas. The script change is one line in the auditor's staging.
- **S1–S22, S24–S26 and S28–S31 hold:**
  - stage 10 still validates the auditor entry's globs;
  - S5's selection is still "less `tree-exclude.txt`";
  - S16's delivery still lands the real reasons in `owner.jsonl`;
  - the rest of S27 is unchanged: the 40-case split, the map, the tickets and the decision check.
- **The revised cases weaken nothing:**
  - The shared blinding helper is stricter. Through it, the two audit cases and the new case still compare the whole disputes file.
  - The renamed fixes case lost only its "both reasons kept" half, which S27 now contradicts, and its whole-file comparison, which the new case keeps. It gained checks of label, class and clauses in the seeded order.
  - S22's template case is stricter for the auditor and unchanged for the other four entries.
  - The planted `kinds.yaml` copies the real template entries, so if a glob went missing from the auditor's entry, the tree case and both template cases would fail.
  - The planted files sit in commit A, so the diff the earlier cases depend on is unchanged.
  - The F21 unit test was replaced by a stricter one, and a tree case was added.
- **Roles:** the designer's commit stays inside `tests/acceptance/W2-149/**` and carries `Rewrite-Reason`. The engineer's two commits stay inside `allowed_paths` and touch no acceptance file.

## Findings

**F40: the auditor's blind now rests on a fixed list of six places. A record written later that restates the tell somewhere else would put it back, and nothing checks the auditor's tree at the real pin.**
- **What was done:** check 2's search at the head, plus a look at where this ticket's records are kept.
- **What happened:**
  - Today the tree holds no statement of the tell. The closest is DECISIONS-IN-FORCE.md's wiring entry, which says the first labeller has a rule script and hand labels, but not what the script's lines look like.
  - The files the CTO writes as a matter of routine all lie outside the six places, and the auditor's tree holds each of them:
    - DECISIONS-IN-FORCE.md, where delegated decisions are recorded;
    - the register, where the owner's yes is recorded, and which the auditor may read and search;
    - `governance/project/orchestration/reviews/`, where some review records are committed.
  - The ticket's 12:35 note shows what happens when a decision about F36 is recorded: it states the tell in plain words ("it is the class-14, no-clause side"). That note is now excluded with `.tickets/**`; the same sentence in one of those three places would not be.
  - The cases test planted files at the six places only. No step of the install ACT looks at the auditor's tree at the real pin.
- **What should have happened:** either the auditor's tree is searched for the tell at the real pin before its first run, or the tree is built from only the four places its brief reads.
- Ordinary work: yes, because the CTO records delegated decisions, the owner's yes and review records in those files as routine, and its own 12:35 note shows the wording that results.
- Consequence: other. Nothing lands wrongly and no guard is touched. The labeller blind would again rest on the brief's prohibition, and for the register not even on that.
- Scope: in (S23, F38's fix).
- **What would reverse it:** the CTO's procedure already dry-builds the auditor's wall at the pin and searches it before the run, or keeps every record that describes the dispute sides under `.tickets/`, `packages/` or `.gov-runtime/` until the auditor has run.

## Probed and found sound
- The blanking works on copies: the labels files and `owner.jsonl` keep both reasons.
- `how` never enters the wall.
- The x/y draw is unchanged, and the map is written only at delivery.
- Key order, the `rule_class` form, the clauses form, spacing and line order are the same on both sides.
- The exclusion matches prefixes the way the tree build does: all 218 tickets and both unit files are left out.
- Excluding `.tickets/` leaves `input/tickets.jsonl` untouched.
- The six places cost the auditor nothing its brief allows it to read.
- The other four entries, and a brief with no entry, are unchanged.
- Until the ACT is applied, a launch is refused with code 11, so the change fails closed.
- The lead's count of 362 reconciles.
- Every role stayed within its paths.

## Classification
One finding: F40, in scope, ordinary work yes, consequence other. Nothing fails open or loses work, so nothing blocks. Recommendation: READY, no round; F40 is a row carried into the install ACT's procedure.

```verdict
{"kpis": [{"kpi": "S23", "verdict": "pass", "findings": [{"id": "F40", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S27", "verdict": "pass", "findings": []}]}
```
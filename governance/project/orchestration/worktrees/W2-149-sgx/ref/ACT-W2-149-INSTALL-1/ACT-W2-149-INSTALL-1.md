# ACT-W2-149-INSTALL-1: the launch script's approved list: set-up A's five fixed briefs, the walls' two changed template files and the operator's two briefs (DEC-1101 (2)-(3), DEC-1112 (3), DEC-1113)

- **For:** the owner's yes, then the owner's operator by hand, as the message in §5 (DEC-1104 (4)). About one minute in
  the main tree.
- **By:** a ticket lead for the CTO (orchestrator `DAEO-sdxk`). Built 2026-11-09, **rebuilt 2026-11-10 on the merged
  set-up A wiring** (W2-149, `7f0e71519`), **and again on its review's F18-F23 fixes** (`90c1fea6c`), as the CTO decided
  before asking you. Rehearsed in a clone with a planted HOME and a planted sets root. **Nothing
  live changes** until the operator runs §5, and the real sets root was never opened. Reviewed independently (§7).
- **Under:**
  - DEC-1101 (2)-(3): fixed briefs the owner approves once, hashed; the launch script checks them and the walls'
    template against the owner's list.
  - DEC-1113 and the owner's approval of 2026-11-09: set-up A's five briefs at labeller v3 `bbff1249…`, labeller-2 v3
    `e13b5f96…`, writer-tuning v3 `82134b3d…`, writer-heldout v3 `137a73d1…` and overlap-auditor v1 `b212a424…`.
    DECISIONS-IN-FORCE says "the approved list the launch script checks is written by the launch script's install ACT".
  - DEC-1112 (3), the CTO's delegated rulings (`4fd701aba`): the wiring, the template change, the seeds (declaration
    amendment A5).
  - DEC-1109 (1): the operator agent's two briefs, `51c459cf…` and `e8670330…`.
  - DEC-1057: rehearsed.
- **Sources:**
  - W2-149 (`DAEO-52ku`): merged `b4de529b`; F11 `ff1865184`; set-up A's wiring `7f0e71519` (review READY round 1,
    `.gov-runtime/scratch/orchestrator/reviews/W2-149-sgx-review-r1.md`; `gov accept W2-149` pass, 146/0/3); its
    review's F18-F23 fixed `90c1fea6c` (review READY, `reviews/W2-149-sgx-review-f18.md`; `gov accept W2-149` pass,
    197/0/3).
  - ACT-INDEP-WALLS-1: the list as first written, `331e48fa…`, with six template lines.
  - ACT-SETS-GLOBS-1, applied `9cce7430d`.
  - SANDBOX-GUARD-EXP-DECLARATION §12 and its amendment A5.
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/w2-149-install/` (§4). The first and second builds' reviewed
  drafts are kept in `drafts/w2-149-install-v1/` and `drafts/w2-149-install-v2/`.

## 0. Class: (O); your yes, then your operator by hand
**(O), with your yes, then your operator by hand.** The yes line: **`yes ACT-W2-149-INSTALL-1 @SHA8@`** (`@SHA8@`: the commit that records this package ready)

**Your yes also approves the walls' `kinds.yaml` and `tree-exclude.txt` as set-up A's wiring changed them** (§1's
table: what each change turns on). The template's own header says a change to it needs your approval. The CTO's
delegated ruling took the change into the repository (`4fd701aba`, merged `7f0e71519`), and this list is where it is
approved.

- **The code's vote is (O).** `class-rules.yaml`'s `walled-sessions` row names both paths this ACT writes as (O):
  `gov-os-eval/**` (so `<sets root>/indep-walls/APPROVED`) and `governance/project/indep-briefs/**`. That is
  OPERATOR-AGENT-1 §2's "the blind writers and checkers: walled sessions under DEC-1101, not the operator". The agent's
  brief forbids the sets root altogether.
- **By effect it is at least (b).** The list decides what the launch script will start. Its seven brief lines and two
  changed template lines let set-up A's walls be built under briefs and a template that the script refuses today. Its
  only tightening is `tree-exclude.txt`'s new line (and the set-up A entries' tree exclusions).
- The higher vote applies: (O). It never goes to the agent's queue. It changes what may launch independent sessions,
  so the CTO asks your yes before your operator runs §5 (as with ACT-SETS-GLOBS-1, DEC-1115 (1)).

## 1. What lands
1. **The five briefs in the repository,** byte for byte as you approved them, at
   `governance/project/indep-briefs/sgx1/{labeller,labeller-2,writer-tuning,writer-heldout,overlap-auditor}.md`. The
   launch script reads a brief only from the repository at `--commit` (`git show`, W2-149 reading 3), never from a
   working copy. Your operator commits them (`Role: owner`).
2. **The list** `<sets root>/indep-walls/APPROVED` (0400, written by your operator only). It is ACT-INDEP-WALLS-1's
   text, with **two of its six template lines changed** to the set-up A wiring's template files:

   | Template file | Before (ACT-INDEP-WALLS-1) | After (W2-149, `7f0e71519`) | What changed |
   |---|---|---|---|
   | `governance/project/indep-walls/kinds.yaml` | `8b50a78f01b3…` | `734b26e261fa…` | a `model` per kind (`claude-opus-5-5`); a `briefs:` entry per set-up A brief (its flow, result schema, `sample`, and its tree exclusions: `.claude/**`, `src/gov/guard/**`, `src/gov/launch/**`, the template folder) |
   | `governance/project/indep-walls/tree-exclude.txt` | `21660e1ee5ad…` | `e8395088167e…` | `governance/project/indep-briefs/**` left out of every wall's tree and every writer's sample (review F7 of the first build) |

   **What the `kinds.yaml` change turns on** (the rebuilt ACT's review, K2 and F35):
   - **a default model for every kind:** a brief of any kind, the memory sets' included, that names no model now runs
     on `claude-opus-5-5` instead of being refused 10;
   - **the labeller kind becomes launchable,** for set-up A's two labeller briefs only (any other labeller brief is
     refused 10);
   - **set-up A's five flows.** The script stages each half's material into the wall: the tuning half from
     `~/gov-os-runs/SANDBOX-GUARD-EXP-1/tuning/`, the held-out half from the sealed folder under the sets root. It
     delivers each wall's products by its own code into that half's folder; for the held-out half that is the sealed
     folder (planted cases, round-1 files, labels, the overlap auditor's decisions and x/y map, a rewritten
     `labels.jsonl`, `owner.jsonl`);
   - **at labeller 1's round-1 delivery and again at its round 2, the script runs that session's own rule script on
     this machine,** confined by `bwrap` (no network, no files, no process, capped; a failure rejects round 1's delivery
     with 20, and refuses round 2 with 18);
   - **a set-up A wall's tree loses** `.claude/`, `src/gov/guard/`, `src/gov/launch/` and the template folder (a
     tightening).

   `tree-exclude.txt`'s change lets a wall do nothing new.

   The other four template lines are unchanged. After the six template lines come:
   ```
   # ACT-W2-149-INSTALL-1 … the two template lines above … replace 8b50a78f01b3 and 21660e1ee5ad (ACT-INDEP-WALLS-1's).
   # ACT-W2-149-INSTALL-1 … for the launch script governance/project/orchestration/tools/indep_launch.py
   # 95fe78dd49bb493194e33cc6a832bc3674b6998ac06010cc5a5d4f7aade5f1d0 (W2-149 with set-up A's wiring, 90c1fea6c7e5) …
   bbff1249…  brief labeller governance/project/indep-briefs/sgx1/labeller.md
   e13b5f96…  brief labeller governance/project/indep-briefs/sgx1/labeller-2.md
   82134b3d…  brief writer governance/project/indep-briefs/sgx1/writer-tuning.md
   137a73d1…  brief writer governance/project/indep-briefs/sgx1/writer-heldout.md
   b212a424…  brief auditor governance/project/indep-briefs/sgx1/overlap-auditor.md
   # The operator agent's two fixed briefs (DEC-1109 (1)) …
   51c459cf…  brief operator governance/project/operator/brief.md
   e8670330…  brief operator governance/project/operator/reviewer-brief.md
   ```
   `drafts/w2-149-install/APPROVED.after` gives it in full: 23 lines, sha256
   `32f1aab70bc24ac7133f720f4fab071426400e081b8727f4908513fa172de5f6`. A template line must be replaced, not added
   beside the old one: the launch script requires exactly one hash per template file.
   - Each brief's kind is its front matter's `kind`.
   - The operator's two briefs are kept on the one list of what you approved. The launch script knows no kind
     `operator` (its `--kind` refuses with 17), so no wall can be built under them. **If you meant something else by
     "the operator's two"** (row 75 of DECIDED-NOT-DONE), say so before your yes: the CTO drops the two lines and
     re-rehearses.
3. **Nothing else.** The launch script, the template files and the schemas are already in the repository (the wiring's
   merges, `7f0e71519` and `90c1fea6c`). The guard, the path map and the settings are untouched.

## 2. The order
1. **W2-149 with set-up A's wiring and its F18-F23 fixes merged** (`90c1fea6c`). `apply.sh` refuses unless the tree's
   launch script hashes `95fe78dd49bb` and its `kinds.yaml` and `tree-exclude.txt` hash `734b26e261fa` and `e8395088167e` ("merge it
   first"). After the apply, the list holds the template and the briefs by their template and brief lines. **It holds
   the script only until the apply:** the script's hash in the list is a comment, which the launch script's parser
   skips (the rebuilt ACT's review, F34).
2. **ACT-SETS-GLOBS-1 applied.** Done: your operator applied it at `9cce7430d` on 2026-11-09. `apply.sh` refuses unless
   the map's `sets_root_hidden` holds its four globs and the hook has its line keys (rehearsed: refused before, applied
   after).
3. **This ACT.** W2-141's hook (row 78), rebuilt on ACT-SETS-GLOBS-1's hook, keeps both checks true whenever it lands.
4. **Then the declaration's pin amendment** (§3), before the extractor runs.

## 3. What it does, and what it does not do
- **Set-up A launches through the merged script once this is applied.** The rehearsal (§6) applies it, and then a dry
  launch under each of the five briefs (`--seed 17`) passes stage 10 and builds its wall (exit 0, `dry`):
  - `model` comes from the kind (`claude-opus-5-5`);
  - `result_schema` comes from the brief's entry (`sgx1-<brief>-result.schema.json`);
  - `sample` comes from the front matter for the writers (400) and from the entry for the others (0);
  - each wall's `input/` is exactly what its brief names;
  - each wall's `brief.md` is the approved bytes;
  - each tree holds no `governance/project/indep-briefs/`, `.claude/` or `src/gov/guard/`.

  Before this ACT, every launch at the merged commit is refused with **11**: the two changed template files are not yet
  on the list.
- **Before the apply,** a change to the launch script or to either template file makes `check` refuse ("merge it
  first"), and the ACT is rebuilt, re-reviewed and asked again (first build's review F4).
- **After the apply, the two differ** (the rebuilt ACT's review, F34):
  - a later change to either template file is refused 11 at launch until a new list approves it;
  - a later change to the launch script launches under this list unchanged, as reviewed code without a new yes (the
    list's comment then names an older script). `check` then says "merge it first", though the ACT is applied; `undo`
    still works.
- **The wiring's review rows F18 to F23 are fixed** (`90c1fea6c`; the CTO's decision, DEC-1112 (3), to fix them before
  asking you), so this build's script holds them:
  - the rule script is checked at round 1's delivery, and a broken one never lands (F18);
  - a result that says it stopped delivers nothing (F19);
  - labeller 2's labels are checked before they land (F20);
  - when either side's reason is empty, both are blanked in the auditor's disputes (F21);
  - a settled case takes the auditor's whole decision (F22);
  - `rule_class` is accepted as an integer or a decimal string 1-14 and stored as an integer (F23).
- **Two rows of that fix's review stay** (W2-149's file; neither in scope, reachable in ordinary work and fail-open or
  work-losing):
  - **F36, named to you here.** In the disputes F21 blanks, the first labeller's script side can still be picked out:
    it is the class-14 side with no clause, against the second labeller's refuse or ask. The auditor cannot name a
    labeller from anything it may read, but its brief says it does not know which wrote which. Blanking every
    dispute's reasons would hide it, at the cost of the second labeller's arguments; that would be a script change and
    one more rebuild. The reviewer recommends accepting it as a named limit (confidence medium), and so does the lead.
  - **F37:** a round-1 rejection by the rule check logs `rejected rules` without the check's own word, so a missing
    `bwrap` looks like a broken script until it is checked by hand.
- **The experiment's pin moves** (first build's review F6). The launch script reads each brief and template file at
  `--commit`, the same commit it builds each wall's tree from. The declaration pins every tree at `f000adda4`, where no
  brief exists and the template is the old one. A launch there is refused with 10 today, and with **11** once this list
  is applied, since its `kinds.yaml` and `tree-exclude.txt` are the two lines this list replaces (the rebuilt ACT's
  review, F33). The new pin is the first `w2/integrate` commit at or after both the wiring's last merge
  (`90c1fea6c`) and your operator's commit of §5 (and after W2-141's hook, if that lands first). The CTO records it as
  an amendment before the extractor runs.

## 4. The files (drafts; checked by hash before they apply)
| File (`drafts/w2-149-install/`) | sha256 (first 12) |
|---|---|
| `briefs/` the five, byte for byte §12's | `bbff1249953b`, `e13b5f96d0e0`, `82134b3dd6b5`, `137a73d1df4c`, `b212a424062e` |
| `APPROVED.before` (rebuilt from ACT-INDEP-WALLS-1's own text; equals its recorded `331e48fa…`), `APPROVED.after` | `331e48fa336e`, `32f1aab70bc2` |
| `apply.sh`: `check`, `apply`, `undo` | `e3943ad4e243` (the second build's reviewed `53c2c68122d2` with only `LAUNCH_SHA` and `LIST_AFTER` re-frozen by `freeze.py`; the first build's reviewed `871d2c9db3dc`) |
| `freeze.py` (builds the two lists and writes the hashes into `apply.sh`), `install_check.py` (stage 10's values and their source per brief line), `rehearse.sh`, `rehearsal.log` | `2843bd193cc8`, `0dc77d5ce966`, `e0da436ef120`, `5fb57e916221` (the first three unchanged since the second build's review) |

- **What `check` and `apply` require.** They stop unless:
  - every draft hashes as built;
  - `APPROVED.after`'s head is `APPROVED.before` with exactly the two template lines changed;
  - the order of §2 holds;
  - the tree and the list are both in the before state (no brief file, the list `331e48fa…`) or both applied ("already
    applied").
- **What `apply` does.** It backs up the list with its sha256 and writes the five files. It writes the new list beside
  the old one and renames it over (0400). It then reads the list back with the launch script's own parser: 6 template
  lines and 7 brief lines, every hash matching its file in the tree.
- **What `undo` does.** It checks the backup, puts the list back byte for byte, and removes the five files only. The
  tree's template files stay as merged, so after an undo every launch is refused with 11 again.
- **The live check is the operator's.** The CTO's sessions never open the sets root, so `check` meets the real list for
  the first time at your apply. If the real list is not `331e48fa…`, it stops and changes nothing.

## 5. The operator's steps: the message
> **ACT-W2-149-INSTALL-1 (DEC-1101, DEC-1112 (3), DEC-1113): the launch script's approved list.** Class (O), by hand:
> your yes first: **`yes ACT-W2-149-INSTALL-1 @SHA8@`** (the form of DEC-1115 (1)). **Your yes also approves the walls'
> `kinds.yaml` and `tree-exclude.txt` as set-up A's wiring changed them** (§1). It comes after ACT-SETS-GLOBS-1 and
> after W2-149's set-up A wiring and its F18-F23 fixes are merged (`7f0e71519`, `90c1fea6c`). In the main tree, about one minute:
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=.gov-runtime/scratch/orchestrator/drafts/w2-149-install
> bash $G/apply.sh check     # "state: before (the list 331e48fa336e)", then "check: ready to apply" (exit 0)
> bash $G/apply.sh apply     # backup; the five briefs; the list; "6 template lines, 7 brief lines …"; "state applied"
> git add governance/project/indep-briefs/sgx1
> git diff --cached --name-status    # expect exactly 5 A: the five briefs
> git commit -m "ACT-W2-149-INSTALL-1: set-up A's five fixed briefs as the owner approved them (DEC-1113), and the launch script's approved list (the five, the walls' two changed template files, the operator agent's two)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1112" --trailer "Role: owner" -- governance/project/indep-briefs/sgx1
> ```
> - **If `check` stops** (the order, a script or template that is not the merged one, or a list that is not as first
>   written), send its line to the CTO and apply nothing.
> - **If `git diff --cached` lists anything besides the five,** commit anyway: the `--` path limits the commit to them
>   (first build's review F2).
> - **If the commit stops,** nothing is committed and nothing launches under the briefs (the script reads them only at
>   `--commit`). Send the output to the CTO (first build's review F9).
>
> **Undo:** `bash $G/apply.sh undo` puts the list back byte for byte and removes the five files. Then run
> `git commit -m "ACT-W2-149-INSTALL-1 undone" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1112" --trailer "Role: owner" -- governance/project/indep-briefs/sgx1`.

**Then the CTO, the same day:**
- record the apply here;
- record the declaration's pin amendment (§3);
- merge `w2/integrate` into the worktrees that will build walls;
- set-up A's steps follow the declaration's order (§13: the extractor, the writers, the labellers, the overlap
  auditor).

## 6. The rehearsal (DEC-1057): `rehearsal.log`
One clean run, 2026-11-10 12:30:47–12:30:53 UTC, from a fresh `env -i` shell. **Failures: 0.**
- **Where:** a `--no-hardlinks` clone of the main tree at `067a8b79c` (W2-149 with set-up A's wiring and its F18-F23
  fixes merged at `90c1fea6c`; later commits by other sessions, which touch neither the script nor the template).
- **What was already live:** ACT-SETS-GLOBS-1 applied by your operator at `9cce7430d` (hook `74f8dbea4761`, map
  `44f99ea563cb`).
- **What was planted:** a HOME, and a sets root whose `indep-walls/APPROVED` is ACT-INDEP-WALLS-1's list rebuilt
  (`331e48fa…`). Under the planted runs folder, set-up A's tuning half: 3 actions, 2 cases, and the two labellers'
  labels with one dispute.
- The real sets root was never opened.

Trials at each branch head before its merge gave the same results: `rehearsal-trial-7df7c35e3.log` (the second build)
and `rehearsal-trial-d388da2f2.log` (this build), beside the log. Their drafts were frozen at those heads, so their
hashes differ.

| Step | Result |
|---|---|
| **Order:** the clone's hook and map put back to before ACT-SETS-GLOBS-1 (`97a84e770058`, `40085090306e`) | `check` **refused**: "ACT-SETS-GLOBS-1 is not applied (its globs are not in the map's sets_root_hidden): apply it first". The files were then put back (`74f8dbea4761`, `44f99ea563cb`) |
| Before this ACT: a launch under writer-tuning | refused **11** (template: the two changed files are not on the list) |
| `apply.sh` | check: "ready to apply" (also from a folder holding `runs/x/misses.jsonl`, first build's F3). Apply: "6 template lines, 7 brief lines (auditor, labeller, operator, writer); template mismatches 0; brief mismatches 0", the list `32f1aab70bc2`, "state applied", no `__pycache__` in the tree (F1). A second apply was refused. Check: "already applied" |
| The operator's commit | exactly **5 A** (the five briefs), with §5's three trailers |
| The list on disk | folder 0700, file 0400 |
| **Stage 10 per line** (`install_check.py`) | **7 of 7** lines match their bytes at the commit. The five set-up A briefs' front matter is ok: model from the kind, result schema from the entry, sample from the front matter (writers) or the entry. The operator's two are a record only (`--kind operator` is refused with 17) |
| **Dry launches under each of the five**, `--seed 17` | each **0 (dry)**: `brief_id`, `flow`, `model` `claude-opus-5-5` and `result_schema` as above. `input/`: labeller `actions.jsonl cases.jsonl half.json`; labeller-2 `half.json`; writer-tuning `selection.json`; writer-heldout `seal.json selection.json`; the auditor `disputes.jsonl half.json tickets.jsonl`. Each `brief.md` is byte for byte the approved brief, and no tree holds `indep-briefs/`, `.claude/` or `src/gov/guard/`. The operator's `brief.md` named as a writer was refused 10 |
| `apply.sh undo`, the removal committed | the list byte for byte `331e48fa…`; 5 D; check "ready to apply" again; a launch refused again |
| Live files (the hook, the map, `.claude/settings.json`, the launch script, the walls' template, the schemas, `~/.claude/settings.json`, the operator folder but its log) | **unchanged** (23 lines hashed) |

**Where the real run differs:**
- `apply.sh` checks the real list at your apply, never before: the CTO's sessions do not open the sets root.
- The real sets root holds the hidden sets (4,560 hidden files at ACT-SETS-GLOBS-1's check), which this ACT neither
  reads nor adds to.
- The real halves are written later, by the extractor and the writers.
- The rehearsal's undo commit runs `git add -A` first; §5's undo does not (first build's F8). The rebuilt ACT's
  reviewer ran §5's undo commit exactly as written and got 5 D.
- The main tree is shared and runs its git hooks at the commit; the clone had none. `apply.sh` needs a writable temp
  folder (`mktemp`); without one, it stops on mktemp's own message (it fails closed).
- The launches were dry, with seed 17, at the ACT's own commit. Real launches draw their own seed, start sessions, and
  are made at the amended pin.

## 7. The review
- **The first build** (2026-11-09; `reviews/ACT-W2-149-INSTALL-1-review-r1.md`, `-r2.md`): READY by `verdict.py` in
  round 2, class vote (O), findings F1 to F9. Its fixes are carried into this build: F1 `-B`, F2 the `--` path, F3 the
  globs quoted. F4, F6 and F7 are answered by the wiring and §3. F9 is answered in §5.
- **This build (the third, on F18-F23's fixes):** @REVIEW@
- **The second build** (`.gov-runtime/scratch/orchestrator/reviews/ACT-W2-149-INSTALL-1-review-v2-r1.md`): **READY by
  `verdict.py` in round 1.**
  - A fresh read-only session (`independent-auditor` on `DAEO-52ku`, effort max), class vote **(O)**. It read
    `apply.sh` `53c2c68122d2…` and found all 12 drafts as §4 states, byte for byte as in the main tree.
  - It re-ran everything on its own sparse clone, with planted roots and no `fixtures/evaluation/`: 17 refusal cases,
    check and apply under `bash -x`, §5's commit with another session's changes staged (exactly 5 A), the parser, the
    five dry walls, launches at the declared pin, undo and its refusals, §5's undo commit (5 D), and a launch-script
    change after the apply.
  - K1-K6 and K8 pass. K7 was marked fail with no blocking finding.
  - Five findings, all in scope and ordinary work, consequence "other". **Carried as text fixes** to §0, §1, §2, §3,
    §5, §6 and §8, as the reviewer proposed (DEC-802). `apply.sh`, the drafts and §5's commands are unchanged (the
    same hashes):
    - **F33:** a launch at the declared pin is refused 11 after the apply, not 10 (§3);
    - **F34:** after the apply, the list does not hold the launch script (§2, §3, §8);
    - **F35:** your yes approving the template change is now said in §0 and §5, with what `kinds.yaml` turns on (§1);
    - **F31:** copies of the guard's code, its suites and the harness stay in set-up A's trees, under the briefs' "leave
      them unread" (§8);
    - **F32:** the operator agent's two briefs are in every wall's tree (§8).
  - Its other notes: F21's tell seen in a planted wall; the writers' sample names 9 paths left out of the tree (names
    only); the trial's log, now beside the log.

## 8. Residuals
1. **F36 and F37 of the F18-F23 fix's review** (§3). F36 is named to you as a limit of the overlap auditor's blind.
   Any later change to the launch script runs under this list without a new yes, because the list holds the script
   only until the apply (F34).
2. **The declaration's pin amendment** (§3): recorded by the CTO after your operator's commit, before the extractor.
3. **The list's live state is checked only at your apply** (§4): the CTO never opens the sets root.
4. **The briefs in every worktree:** once committed, the five briefs are in every worktree (reads there are open by
   DEC-820, as for any committed file). They are no longer in any wall's tree: `tree-exclude.txt` now leaves out
   `governance/project/indep-briefs/**` (first build's F7, closed by the wiring).
5. **What set-up A's trees still hold** (the rebuilt ACT's review, F31). Every set-up A wall's tree still holds:
   - copies of the guard's code outside the excluded folders: `docs/changes/W2-141-hook/` (the staged hook and its
     `role_reads.py`) and `template/governance/kernel/hooks/pretooluse.py`;
   - the guard's suites: `tests/unit/guard/`, `tests/unit/hooks/test_live_hook.py` and `tests/acceptance/W2-141/`;
   - the launch script.

   Every brief forbids reading them ("your tree holds some of these; you leave them unread"), so the labellers' and
   the auditor's blindness to the guard rests there for these copies. Widening the entries' `tree_exclude` is a
   template change, and so a rebuild of this ACT. Whether `docs/changes/W2-141-hook/` is still in the tree at the
   amended pin is to be checked when the pin is recorded.
6. **The operator agent's two briefs are in every wall's tree** (F32). `tree-exclude.txt` leaves out only
   `indep-briefs/**`. These two briefs say nothing of set-up A's labels, cases or the guard. Leaving them out is a
   template change, and so a rebuild.

**What it costs:** five files in the repository; in the list, two template lines changed and fifteen lines added. No install, no GPU. Your
yes and one minute.

**Basis:** question 2: the sets' independence is enforced by the owner's list, not by trust. Only briefs and a template
you approved can start an independent session.

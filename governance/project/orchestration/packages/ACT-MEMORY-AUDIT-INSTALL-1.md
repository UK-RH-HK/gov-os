# ACT-MEMORY-AUDIT-INSTALL-1: the memory audit's three fixed briefs and their lines in the launch script's approved list (DEC-1129 (2))

- **For:** the owner's yes, then the owner's operator by hand, as the message in §5 (DEC-1104 (4)). About one minute in
  the main tree.
- **By:** a helper of the CTO (orchestrator `DAEO-sdxk`), 2026-11-11. **Nothing live changes** until the operator runs
  §5. The real sets root was never opened; the live list is read for the first time by `apply.sh check` at your apply.
  Rehearsed in a clone with a planted HOME and sets root (§6). **Reviewed READY, round 1** (11-11 15:55 UTC, §7).
- **Under:**
  - DEC-1129 (2): the three briefs approved as written at `8c18fa300`; their hashes go into the approved list by this ACT.
  - DEC-1101 (1)-(2), DEC-1125 (2): fixed briefs approved once, hashed; the launch script starts a walled session only
    under a brief on the owner's list. DEC-1057: rehearsed.
  - The model: ACT-W2-149-INSTALL-1 (applied 11-10 15:41, `baac0b2c2`).
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/memaudit-install-1/` (§4).

## 0. Class: (O); your yes, then your operator by hand
The yes line: **`yes ACT-MEMORY-AUDIT-INSTALL-1 <8 hex of the commit that records this package ready>`** (the CTO fills
the commit in when it records the package; the form of DEC-1115 (1)).

- **The code's vote is (O).** `governance/project/operator/class-rules.yaml`'s `walled-sessions` row (class O,
  `control: false`) names both paths this ACT writes: `gov-os-eval/**` (so `<sets root>/indep-walls/APPROVED`) and
  `governance/project/indep-briefs/**` (the three brief files). **What that means for who applies it:** the operator
  agent never takes it (OPERATOR-AGENT-1 §2: "the blind writers and checkers: walled sessions under DEC-1101, not the
  operator"; the agent's brief forbids the sets root altogether). Only **your operator, by hand**, writes the list and
  commits the briefs (`Role: owner`). The CTO's sessions neither open the sets root nor commit the briefs.
- **By effect it is at least (b):** the list decides what the launch script will start. It only adds three lines; no
  template line, no existing brief line and no control file changes. The higher vote applies.

## 1. What lands
1. **Three files in the repository,** byte for byte the briefs you approved, at
   `governance/project/indep-briefs/memory-audit/{writer,checker,auditor}.md`:

   | File | sha256 (DEC-1129 (2)) | Source at `8c18fa300` |
   |---|---|---|
   | `writer.md` | `bc0894230e3181e5be27726d60e9fb781f9355da1c4f8e76f69b400af97d379b` | `packages/MEMORY-AUDIT-1/briefs/writer.md` |
   | `checker.md` | `cea517b8da7d4834bb2a698b9c7023670da36f0ceca6b3350656c6db77c45248` | `.../checker.md` |
   | `auditor.md` | `37be41c3fb2fea1654d68f71f1ecfc5ad4b41faaed9356a27ce1f01d8ef94245` | `.../auditor.md` |

   **Why the folder is `indep-briefs/memory-audit/` and not where you approved them.** The launch script reads a brief
   from any repository path at `--commit` (`git show`) and only checks that the list's line names that path, the kind
   and the hash. The briefs themselves say "your tree leaves the briefs out"; only `governance/project/indep-briefs/**`
   is left out of every wall's tree by `tree-exclude.txt`. The path map already names that folder (ACT-PATHMAP-NS-2),
   so the new files sit in a namespace (rehearsed: `gov.check.pathmap` exits 0). The bytes, so the hashes, are the same;
   `packages/MEMORY-AUDIT-1/briefs/` stays as the record of what you read.
2. **The list** `<sets root>/indep-walls/APPROVED` (0400, written by your operator only): the list as
   ACT-W2-149-INSTALL-1 left it (23 lines, sha256 `6b923cb4d552077f99924fd5df38f1a448b21f863c4755c9ff4e0dcfb28ed959`),
   unchanged, then a four-line comment and three lines:
   ```
   bc0894230e31…  brief writer  governance/project/indep-briefs/memory-audit/writer.md
   cea517b8da7d…  brief checker governance/project/indep-briefs/memory-audit/checker.md
   37be41c3fb2f…  brief auditor governance/project/indep-briefs/memory-audit/auditor.md
   ```
   `drafts/memaudit-install-1/APPROVED.after`: 30 lines, sha256
   `41e3969aa969cec58bf6bc09e770f037acf97ca0ebdd2e8d893e8a1ac2d938e0`. After the apply the launch script's parser reads
   6 template lines and 10 brief lines.
3. **Nothing else.** The walls' template, the launch script, the schemas, the path map, the guard and the settings are
   untouched.

**How `APPROVED.before` was built** (the records give the exact list): ACT-W2-149-INSTALL-1's reviewed
`APPROVED.after` (its sha256 equals the `6b923cb4d552` that DECIDED-NOT-DONE row 75 and MEMORY-AUDIT-1 §2 record as
applied, "0 mismatches"), each of its 13 template, brief and operator lines re-checked against the repository
(`freeze.py`). No later ACT changed the list (searched: the register, the packages, DECIDED-NOT-DONE after DEC-1113;
ACT-PATHMAP-NS-2 changed the path map only; the walls' template files and the operator briefs hash as the list has
them). What the records cannot show is whether anything wrote the live file since 11-10 15:41. So `apply.sh` **refuses
unless the live file's sha256 is exactly `6b923cb4d552…`** and changes nothing otherwise.

## 2. The order
1. ACT-W2-149-INSTALL-1 applied (its five set-up A briefs in the tree: `check` refuses otherwise). Done 11-10.
2. ACT-SETS-GLOBS-1 applied (the map's four globs and the hook's `sets_line_keys`: `check` refuses otherwise). Done.
3. ACT-PATHMAP-NS-2 applied (the map names `governance/project/indep-briefs/**`: `check` refuses otherwise; without it
   `gov check` goes red on the three new paths).
4. **This ACT**, in the window MEMORY-AUDIT-1 §6 gives (11-18 to 11-19), before the dry cycle and the live canary under
   each brief, and before the cron (ACT-MEMORY-AUDIT-CRON-1, class (b), a later ACT).
5. The six template files in the tree must be the six the list names (`check` refuses otherwise, "its own ACT first").
   The launch script is **not** pinned: W2-173 may change it as reviewed code under the list in force (ACT-W2-149-INSTALL-1
   §3, F34); this ACT's `check` reads the list with whatever script the tree holds.

## 3. What it does, and what it does not do
- **After the apply** a launch under each brief passes the script's approved check (stage 10) and builds its wall
  (rehearsed dry: writer rounds 1 and 2, checker, auditor; each `brief.md` the approved bytes; no wall tree holds
  `indep-briefs/`). The model, result schema and sample come from each brief's front matter (writer `claude-sonnet-5-5`,
  checker and auditor `claude-opus-5-5`; writer sample 300; budgets and timeouts within `kinds.yaml`'s caps).
- **Before the apply** the same launches are refused 10.
- **A changed byte is refused 10:** in a brief (the old hash against new bytes, or the new hash, which no list line
  holds), in a list line, or a brief under a kind its line does not give.
- **The operator must commit the three files** before the first audit; the audit's `--commit` must be at or after that
  commit (the script reads the brief at `--commit`).
- **It does not** start a session, write a cron line, create W2-170 to W2-173's code, or touch the sets root beyond
  the one file.

## 4. The files (drafts; checked by hash before they apply)
| File (`drafts/memaudit-install-1/`) | sha256 (first 12) |
|---|---|
| `briefs/{writer,checker,auditor}.md` (byte for byte DEC-1129 (2)'s) | `bc0894230e31`, `cea517b8da7d`, `37be41c3fb2f` |
| `APPROVED.before` (rebuilt, equals the recorded list), `APPROVED.after` | `6b923cb4d552`, `41e3969aa969` |
| `apply.sh`: `check`, `apply`, `undo` | `dea29d869ca0` |
| `freeze.py` (rebuilds the two lists, checks every line against the repository, writes the hashes into `apply.sh`) | `e4eeb32db2ca` |
| `install_check.py` (stage 10's reading per brief line; ACT-W2-149-INSTALL-1's, header line only changed), `rehearse.sh`, `rehearsal.log` | `69b5f39eadda`, `f2035ea05c86`, `c8841eb1cce8` |

- **What `check` and `apply` require.** They stop unless: every draft hashes as built; `APPROVED.after` is
  `APPROVED.before` byte for byte plus comments and exactly three lines; the order of §2 holds; the live list is
  exactly `6b923cb4d552…` (else it names the sha256 it found); and the tree and list are both before (no brief file)
  or both applied ("already applied").
- **What `apply` does.** It backs up the list with its sha256 (`drafts/memaudit-install-1/backup/`), writes the three
  files, writes the new list beside the old and renames it over (0400), then reads the list back with the launch
  script's own parser: 6 template lines, 10 brief lines, every hash matching its file; the three memory lines present.
- **What `undo` does.** It checks the backup, puts the list back byte for byte, removes the three files only (set-up
  A's folder stays).
- **The live check is the operator's.** The CTO's sessions never open the sets root.

## 5. The operator's steps: the message
> **ACT-MEMORY-AUDIT-INSTALL-1 (DEC-1129 (2)): the memory audit's three briefs and their lines in the launch script's
> approved list.** Class (O), by hand: your yes first: **`yes ACT-MEMORY-AUDIT-INSTALL-1 <8 hex>`**. It comes after
> ACT-W2-149-INSTALL-1, ACT-SETS-GLOBS-1 and ACT-PATHMAP-NS-2 (all applied). In the main tree, about one minute:
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=.gov-runtime/scratch/orchestrator/drafts/memaudit-install-1
> sha256sum ~/gov-os-eval/indep-walls/APPROVED   # expect 6b923cb4d552077f99924fd5df38f1a448b21f863c4755c9ff4e0dcfb28ed959
> bash $G/apply.sh check     # "state: before (the list 6b923cb4d552)", then "check: ready to apply" (exit 0)
> bash $G/apply.sh apply     # backup; the three briefs; the list; "6 template lines, 10 brief lines ..."; "state applied"
> stat -c '%a %n' ~/gov-os-eval/indep-walls ~/gov-os-eval/indep-walls/APPROVED   # expect 700 and 400
> sha256sum ~/gov-os-eval/indep-walls/APPROVED   # expect 41e3969aa969cec58bf6bc09e770f037acf97ca0ebdd2e8d893e8a1ac2d938e0
> git add governance/project/indep-briefs/memory-audit
> git diff --cached --name-status    # expect exactly 3 A: writer.md, checker.md, auditor.md
> git commit -m "ACT-MEMORY-AUDIT-INSTALL-1: the memory audit's three fixed briefs as the owner approved them (DEC-1129 (2)), and their lines in the launch script's approved list" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1129" --trailer "Role: owner" -- governance/project/indep-briefs/memory-audit
> ```
> - **If the first `sha256sum` is not `6b923cb4d552…`,** or `check` stops, send its line to the CTO and apply nothing
>   (`apply.sh` refuses by itself and changes nothing).
> - **If `git diff --cached` lists anything besides the three,** commit anyway: the `--` path limits the commit.
> - **If the commit stops,** nothing is committed and nothing launches under the briefs. Send the output to the CTO.
> - **0400 kept:** `apply` writes the list 0400 and leaves the folder 0700; the `stat` line is the check.
>
> **Undo:** `bash $G/apply.sh undo` puts the list back byte for byte (`6b923cb4d552…`) and removes the three files. Then
> run `git commit -m "ACT-MEMORY-AUDIT-INSTALL-1 undone" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1129" --trailer "Role: owner" -- governance/project/indep-briefs/memory-audit`.
> If the commit was never made, the undo needs no commit.

**Rollback in short:** `undo` restores the list from the backup (checked by its sha256) and removes the three files;
set-up A's briefs and list lines are never touched. After an undo a launch under the memory briefs is refused 10 again.

**Then the CTO, the same day:** record the apply here; run the dry cycle and the live canary (MEMORY-AUDIT-1 §6).

## 6. The rehearsal (DEC-1057): `rehearsal.log`
One clean run, 2026-11-11 14:17:44 to 14:18:21 UTC, from a fresh `env -i` shell. **57 checks, 0 failures.**
- **Where:** a `--no-hardlinks` clone of the main tree at `bb9d29093fd5` (the main tree's head then; the launch script `90b943aef8be`, the template, the
  five set-up A briefs and the path map as live), inside `drafts/memaudit-install-1/work/` (removed after the run).
  A planted HOME, planted runs and wall-trees folders, and a planted sets root `planted-sets/` whose `indep-walls/APPROVED`
  is `APPROVED.before`. Every launch is `indep_launch.py --dry --seed 17`, which starts no session. The real sets root
  and the real runs were never opened.
- **Results:**

| Step | Result |
|---|---|
| Before the ACT: a launch of each brief at its approved path under the packages folder | writer, checker, auditor: each refused **10** |
| `check` refusals | **6 of 6 refuse and change nothing:** the planted list with one byte added (names its sha256; apply refuses too, no backup, no files); a draft brief changed by one byte; a template file changed; the path map without the indep-briefs namespace; set-up A's labeller brief absent; and the clean clone after them is "ready to apply" |
| `apply.sh` | check "ready to apply" (also from a folder holding `runs/x/misses.jsonl`); apply: "6 template lines, 10 brief lines ... the memory audit's: auditor, checker, writer; template mismatches 0; brief mismatches 0"; the list is `APPROVED.after` byte for byte (`41e3969aa969`), file 0400, folder 0700; no `__pycache__` in the tree; a second apply refused; check "already applied" |
| The operator's commit | exactly **3 A** with §5's three trailers |
| Stage 10 per line (`install_check.py`) | **10 of 10** lines match their bytes at the commit; the eight launch-kind briefs pass front matter; the operator's two are a record only |
| **Dry launches under the three memory briefs** | **each exit 0:** writer round 1 (input `selection.json`), writer round 2 (`notes.md selection.json set`), checker (`selection.json set`), auditor (`misses.jsonl selection.json set`; `--audit e0`). Models: writer `claude-sonnet-5-5`, checker and auditor `claude-opus-5-5`; result schemas `writer-`, `checker-`, `auditor-result.schema.json`. Each `brief.md` byte for byte the approved brief; no tree holds `indep-briefs/` |
| Set-up A's five briefs | each still **0 (dry)** |
| A changed byte | the old sha256 against changed bytes: refused 10; the new sha256: refused 10 (the bytes hash to it and no list line holds it, read with the script's own functions); `checker.md` under `--kind writer`: refused 10 (under its own kind: 0); a list line with one hex digit changed: refused 10; control: the restored brief launches again (0) |
| Path map | `python3 -m gov.check.pathmap` at the commit with the three briefs tracked: exit 0, no finding |
| `undo`, the removal committed as §5 says (no `git add`) | the list byte for byte `6b923cb4d552`; **3 D**; set-up A's folder still there; check "ready to apply" again; a launch refused 10 again |
| Live files (hook, map, settings, launch script, template, schemas, class rules, the register; the main tree's status and head) | **unchanged** (24 lines hashed) |

**Counts:** 57 checks passed, 0 failed; 9 dry launches exit 0 (3 memory briefs in 4 launches, 5 set-up A); 8 launches
refused 10 (3 before the install, 2 changed byte, 1 kind mismatch, 1 changed list line, 1 after the undo); 6 `check`
refusals.

**Where the real run differs:**
- `apply.sh` meets the real list only at your apply (the first `sha256sum` and `check`).
- The dry launches plant their inputs: the real set, notes and misses come from W2-170 to W2-172's cycle, not built yet.
- The rehearsal's brief wall for the held-out half is not launched (the sealed folder is planted empty); the
  memory audit does not use it.
- The main tree runs its git hooks at the commit; the clone had none.
- Real launches draw their own seed, start sessions, and take `effort` only once W2-173 makes it real (MEMORY-AUDIT-1 §10).

## 7. The review
**READY, round 1** (2026-11-11 15:55 UTC): a fresh read-only independent auditor (claude -p, launch_worker.sh, DAEO-r30l; not the author), reviewed together with ACT-OPERATOR-ROUNDS-1; full text `governance/project/orchestration/reviews/ACT-OPERATOR-ROUNDS-1-and-MEMORY-AUDIT-INSTALL-1-review.md` ("Package 2"). Its rerun: 57 checks passed, 0 failures, on the same head. Two rows, no change to this ACT: P2-F1 (the six `MEMORY-AUDIT-1/` paths can enter the writer's 300-path sample; take the `tree-exclude.txt` change before the first live cycle, 11-23: DECIDED-NOT-DONE row 151); P2-F2 (a failure between the briefs and the list's rename leaves the state "other", which undo refuses, and may leave a stray `.APPROVED.act-memaudit-install.<pid>` in `indep-walls/`: it fails closed; send the output to the CTO, who gives the hand clean-up).
Suggested focus: `apply.sh`'s `check` against a list that is not `6b923cb4d552`; that `APPROVED.before` equals the applied
list (the one thing the records cannot prove is the live file); the choice of `indep-briefs/memory-audit/`.

## 8. Residuals and what else MEMORY-AUDIT-1 §6 names (listed only; nothing here is built)
1. **The list's live state is checked only at your apply** (§4).
2. **The cron is a later ACT** (ACT-MEMORY-AUDIT-CRON-1, class (b): your yes, then the operator agent), after W2-170 to W2-173 are merged.
3. **W2-170 to W2-173 are not built yet.** The install needs none of them to apply; the first live launch needs them
   (the runner, the cycle's driver, W2-173's `effort`). Until W2-173 the sessions run at the CLI's default effort.
4. **The blindness the briefs alone hold** (MEMORY-AUDIT-1 §9 item 3): every memory wall's tree still holds
   `governance/project/orchestration/packages/MEMORY-AUDIT-1/` (the package and the three brief copies; rehearsed,
   observed: yes), which the briefs forbid reading. Putting the package and its briefs under `tree-exclude.txt` is a
   template change (a new hash and a rebuilt list, class (O)); the package recommends taking it with the next
   template change. Moving nothing now is the cheapest; say so if you want it before 11-23.
5. **The launch script's docstring examples** name `indep-briefs/{writer,checker,auditor}.md`, not `indep-briefs/memory-audit/`.
   A comment only; a unit test (`test_documented_lines_name_only_the_sets_root`) checks only the set-up A paths.
6. **The set must be declared in the sets root's own path map** for the measure (MEMORY-AUDIT-1 §10); W2-170 S4 has the
   runner add it. Not checked here (the sets root is not opened).
7. **Before 11-23:** the baseline line, the pool import, one dry cycle on planted roots and one live canary under each
   brief (§6 of the package) follow this ACT; the CTO does them.

**What it costs:** three files in the repository; in the list, four comment lines and three lines added. No install, no
GPU. Your yes and one minute.

**Basis:** question 2: the sets' independence is enforced by the owner's list, not by trust. Only briefs you approved
can start an independent session; these three are the ones you approved on 11-11.

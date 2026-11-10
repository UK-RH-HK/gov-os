# ACT-W2-149-INSTALL-1: the launch script's approved list: set-up A's five fixed briefs and the operator's two (DEC-1101 (2)-(3), DEC-1113)

- **For:** the owner's yes, then the owner's operator by hand, as the message in §5 (DEC-1104 (4)). About one minute in
  the main tree.
- **By:** a helper agent for the CTO (orchestrator `DAEO-sdxk`, session `ad44f5fe`), 2026-11-09. Built and rehearsed in
  a clone with a planted HOME and a planted sets root. **Nothing live is changed** until the operator runs §5; the real
  sets root was never opened. Reviewed independently (§7).
- **Under:** DEC-1101 (2)-(3) (fixed briefs the owner approves once, hashed; the launch script checks them against the
  owner's list); DEC-1113 and the owner's approval of 2026-11-09 (set-up A's five briefs at labeller v3 `bbff1249…`,
  labeller-2 v3 `e13b5f96…`, writer-tuning v3 `82134b3d…`, writer-heldout v3 `137a73d1…`, overlap-auditor v1
  `b212a424…`; DECISIONS-IN-FORCE: "the approved list the launch script checks is written by the launch script's install
  ACT"); DEC-1109 (1) (the operator agent's two briefs, `51c459cf…`, `e8670330…`); DEC-1112 (3) (delegated to the CTO);
  DEC-1057 (rehearsed).
- **Sources:** W2-149 (`DAEO-52ku`; merged `b4de529b`, its F11 follow-up merged `ff1865184`); ACT-INDEP-WALLS-1 (the list as
  first written, `331e48fa…`, six template lines); ACT-SETS-GLOBS-1 (the hidden globs for a new set's destinations,
  W2-149 review F2, DEC-803's entry criterion of step 4); SANDBOX-GUARD-EXP-DECLARATION §12; the sandbox experiment's
  `README.md` (`drafts/sandbox-exp/`).
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/w2-149-install/` (§4).

## 0. Class: (O); your yes, then your operator by hand
**(O) (review F5), with your yes `yes ACT-W2-149-INSTALL-1 <sha8>`, then your operator by hand.**
- **The code's vote is (O):** `class-rules.yaml`'s `walled-sessions` row names both paths this ACT writes
  (`gov-os-eval/**`, so `<sets root>/indep-walls/APPROVED`, and `governance/project/indep-briefs/**`) as (O): OPERATOR-AGENT-1
  §2's "the blind writers and checkers: walled sessions under DEC-1101, not the operator". The agent's brief forbids the
  sets root altogether (§1).
- **By effect it is at least (b):** the list decides what the launch script will start, and seven brief lines let it
  build walls under briefs it refuses today; it adds no check and tightens nothing.
- The higher vote applies: (O). It never goes to the agent's queue. It changes what may launch independent sessions,
  so the CTO asks your yes before your operator runs §5 (as ACT-SETS-GLOBS-1, DEC-1115 (1)).

## 1. What lands
1. **The five briefs in the repository**, byte for byte as you approved them, because the launch script reads a brief
   only from the repository at `--commit` (`git show`, W2-149 reading 3), never from a working copy:
   `governance/project/indep-briefs/sgx1/{labeller,labeller-2,writer-tuning,writer-heldout,overlap-auditor}.md`.
   Your operator commits them (`Role: owner`).
2. **The list** `<sets root>/indep-walls/APPROVED` (0400, written by your operator only): ACT-INDEP-WALLS-1's text kept
   byte for byte (`331e48fa…`, its six template lines), then:
   ```
   # ACT-W2-149-INSTALL-1 … for the launch script governance/project/orchestration/tools/indep_launch.py
   # b04db4547eec791c2d7d4575cfe541f3744b7235280d03383474ac52d44affd5 (W2-149 with its F11 follow-up, `ff1865184`) …
   bbff1249…  brief labeller governance/project/indep-briefs/sgx1/labeller.md
   e13b5f96…  brief labeller governance/project/indep-briefs/sgx1/labeller-2.md
   82134b3d…  brief writer governance/project/indep-briefs/sgx1/writer-tuning.md
   137a73d1…  brief writer governance/project/indep-briefs/sgx1/writer-heldout.md
   b212a424…  brief auditor governance/project/indep-briefs/sgx1/overlap-auditor.md
   # The operator agent's two fixed briefs (DEC-1109 (1)) …
   51c459cf…  brief operator governance/project/operator/brief.md
   e8670330…  brief operator governance/project/operator/reviewer-brief.md
   ```
   (`drafts/w2-149-install/APPROVED.after` in full: 20 lines, sha256 `9e9d6f212a1ebd54e8bcb6c0c0c691fbb23c8aefbb70e359a9b5a61dba44b56f`.) Each brief's kind is its
   front matter's `kind`. The operator's two are kept on the one list of what you approved; the launch script knows no
   kind `operator` (its `--kind` refuses with 17), so no wall can be built under them. **If you meant something else by
   "the operator's two"** (row 75 of DECIDED-NOT-DONE), say so before your yes: the CTO drops the two lines and
   re-rehearses.
3. **Nothing else:** the template, the launch script, the guard, the path map and the settings are untouched.

## 2. The order
1. **W2-149's F11 follow-up merged** (`--setting-sources project`, `ff1865184`): `apply.sh` refuses unless the tree's launch
   script hashes `b04db4547eec`, so the list names the script that will run.
2. **ACT-SETS-GLOBS-1 applied** (done: your operator applied it at `9cce7430d`, 2026-11-09): `apply.sh` refuses unless the map's
   `sets_root_hidden` holds its four globs and the hook has its line keys (rehearsed: refused before, applied after).
   The deliveries of the walls these briefs start (a new set's `hidden/`, the checker's notes, an audit's miss classes
   and misses) are hidden from every guarded session only after it (W2-149 review F2, DEC-803).
3. **This ACT.** W2-141's hook (row 78), rebuilt on ACT-SETS-GLOBS-1's hook, keeps both checks true whenever it lands.

## 3. What it does not do yet: set-up A cannot launch through the merged script
**Found while building this ACT (rehearsed, §6):** with the list applied, each of the five briefs passes the list's
check and is then refused by the launch script's own stage 10, on its front matter:
- no brief names `model` or `result_schema`, which the script requires (W2-149 reading 4); the two labellers and the
  overlap auditor name no `sample` either (`is_count` needs one; 0 would do for them);
- beyond the front matter, the sandbox experiment's README lists what set-up A asks of the script that W2-149 did not
  build: the labellers' two rounds with `label_rules.py` run confined and its sample staged; the overlap auditor's
  inputs (`disputes.jsonl` with `x`/`y` in a seeded order, `tickets.jsonl` with each ticket's `allowed_paths`) and its
  `decisions.jsonl` delivery; the labellers' deliveries to the scorer's names (`labels.jsonl`, `labels-2.jsonl`) and the
  tuning half's to `EXP/tuning/`; the declaration's overlap rule (`sha256(SEED + "overlap" + id) mod 10 = 0`) where S20
  draws 10 % with `random.Random`.
- **So row 66 (set-up A beside D-10) waits on a W2-149 follow-up for set-up A's wiring**, tests first, as well as on this
  ACT. **This ACT stands only if it is applied before the follow-up changes the launch script** (review F4): `apply.sh`
  pins the script's sha256 and the list's comment names it, so any later change to `indep_launch.py` makes `check`
  refuse ("merge it first") and the ACT is rebuilt, re-reviewed and asked again. The follow-up may also change the
  template (`kinds.yaml` for `model` and `result_schema`; `tree-exclude.txt`, below) or the briefs (new versions for your
  approval), and each changes this list again. Applying this ACT first does no harm: every launch under these briefs is
  refused at stage 10 until then, and a control brief with complete front matter builds its wall under the same list
  (§6).
- **And the experiment's pin moves** (review F6): the launch script reads the brief at `--commit`, the same commit it
  builds each wall's tree from. The declaration pins every tree at `f000adda4`, where no brief exists (a launch there is
  refused 10). Its §2 already requires a new pin, since the live hook and map changed with ACT-SETS-GLOBS-1; the new pin
  is at or after this ACT's commit and the follow-up's merge, recorded as an amendment before the extractor runs.

## 4. The files (drafts; checked by hash before they apply)
| File (`drafts/w2-149-install/`) | sha256 (first 12) |
|---|---|
| `briefs/` the five, byte for byte §12's | `bbff1249953b`, `e13b5f96d0e0`, `82134b3dd6b5`, `137a73d1df4c`, `b212a424062e` |
| `APPROVED.before` (rebuilt from ACT-INDEP-WALLS-1's own text; equals its recorded `331e48fa…`), `APPROVED.after` | `331e48fa336e`, `9e9d6f212a1e` |
| `apply.sh`: `check`, `apply`, `undo` | `871d2c9db3dc` (round 1 reviewed `e52f548e979a`; round 2's fixes: F1 `-B`, F3 the globs quoted) |
| `freeze.py` (builds the two lists and writes the hashes into `apply.sh`), `install_check.py`, `rehearse.sh`, `rehearsal.log` | `1f65c76bb05a`, `164136c6d8ea`, `9d07a23cb26f`, `b6c47925f15a` |

`apply.sh check` and `apply` stop unless every draft hashes as built, the order of §2 holds, and the tree and the list
are both before (no brief file, the list `331e48fa…`) or both applied ("already applied"). `apply` backs up the list
with its sha256, writes the five files, writes the new list beside the old and renames it over (0400), then reads it
back with the launch script's own parser (6 template lines, 7 brief lines, every hash matching its file). `undo` checks
the backup, puts the list back byte for byte and removes the five files only. **The live check is the operator's:** the
CTO's sessions never open the sets root, so `check` meets the real list for the first time at your apply; if the real
list is not `331e48fa…` it stops and changes nothing.

## 5. The operator's steps: the message
> **ACT-W2-149-INSTALL-1 (DEC-1101, DEC-1113): the launch script's approved list.** Class (O), by hand: your yes first
> (`yes ACT-W2-149-INSTALL-1 <sha8>`, the sha8 of the commit that records this package ready, as the CTO's ping gives it, the form of DEC-1115 (1)). After ACT-SETS-GLOBS-1. In the main tree, about one minute:
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=.gov-runtime/scratch/orchestrator/drafts/w2-149-install
> bash $G/apply.sh check     # "state: before (the list 331e48fa336e)", then "check: ready to apply" (exit 0)
> bash $G/apply.sh apply     # backup; the five briefs; the list; "6 template lines, 7 brief lines …"; "state applied"
> git add governance/project/indep-briefs/sgx1
> git diff --cached --name-status    # expect exactly 5 A: the five briefs
> git commit -m "ACT-W2-149-INSTALL-1: set-up A's five fixed briefs as the owner approved them (DEC-1113), and the launch script's approved list (the five and the operator agent's two)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1112" --trailer "Role: owner" -- governance/project/indep-briefs/sgx1
> ```
> If `check` stops (the order, or a list that is not as first written), send its line to the CTO and apply nothing. If
> `git diff --cached` lists anything besides the five, commit anyway: the `--` path limits the commit to them (review F2).
> **Undo:** `bash $G/apply.sh undo` puts the list back byte for byte and removes the five files; then
> `git commit -m "ACT-W2-149-INSTALL-1 undone" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1112" --trailer "Role: owner" -- governance/project/indep-briefs/sgx1`.

**Then the CTO**, the same day: record the apply here; open (or carry on) the set-up A wiring follow-up of §3; merge
`w2/integrate` into the worktrees that will build walls; nothing launches under these briefs until that follow-up lands.

## 6. The rehearsal (DEC-1057): `rehearsal.log`
One clean run, 2026-11-09 23:54:31–23:54:34 UTC, from a fresh `env -i` shell, **failures: 0**, in a `--no-hardlinks`
clone of the main tree at `74767736e` (W2-149 with F11 merged, `ff1865184`; ACT-SETS-GLOBS-1 applied live by your
operator at `9cce7430d`, hook `74f8dbea4761`, map `44f99ea563cb`), with a planted HOME and a planted sets root whose
`indep-walls/APPROVED` is ACT-INDEP-WALLS-1's list rebuilt (`331e48fa…`). The real sets root was never opened. Earlier
runs the same evening: a trial on `w2/W2-149-f11` before the merge (one fault of the rehearsal's own: the auditor's
launch needs `--audit`; fixed, then 0 failures), and one at `9cce7430d` that found ACT-SETS-GLOBS-1 already applied in
the clone (the order step adapted, below).

| Step | Result |
|---|---|
| **Order:** the clone's hook and map put back to before ACT-SETS-GLOBS-1 (`97a84e770058`, `40085090306e`) | `check` **refused**: "ACT-SETS-GLOBS-1 is not applied (its globs are not in the map's sets_root_hidden): apply it first"; the files back (`74f8dbea4761`, `44f99ea563cb`) |
| Before this ACT: a launch under writer-tuning | refused **10** (no brief file at the commit, no line) |
| `apply.sh` | check "ready to apply"; apply: "6 template lines, 7 brief lines (auditor, labeller, operator, writer); template mismatches 0; brief mismatches 0", the list `9e9d6f212a1e`, "state applied"; a second apply refused; check "already applied" |
| The operator's commit | exactly **5 A** (the five briefs), the three trailers as §5 |
| The list on disk | folder 0700, file 0400 |
| **The launch script's own stage-10 checks** (`install_check.py`, its code) | **7 of 7** lines match their bytes at the commit; the five set-up A briefs then refused on their front matter (labellers and auditor: `sample`, `model`, `result_schema`; writers: `model`, `result_schema`); the operator's two: a record only (`--kind operator` refused with 17) |
| Dry launches under each of the five, `--seed 17` | each refused **10** (§3); the operator's `brief.md` named as a writer: refused 10 (its line is kind `operator`) |
| **A control** (rehearsal only): a brief with complete front matter, its line added to the planted list for one launch | dry launch **0** ("dry"): template check passed, the wall built; the list then put back to the ACT's bytes, the control commit and wall removed |
| `apply.sh undo`, the removal committed | the list byte for byte `331e48fa…`; 5 D; check "ready to apply" again |
| Live files (the hook, the map, `.claude/settings.json`, the launch script, the walls' template, the schemas, `~/.claude/settings.json`, the operator folder but its log) | **unchanged** |

**Round 2's re-run** (after review round 1's F1, F2, F3), 2026-11-10 00:23:39–00:23:45 UTC, **failures: 0**, at
`f73e72d4a`: the same steps, plus: `check` run from a folder holding `runs/x/misses.jsonl` still "ready to apply" (F3);
no `__pycache__` written into the tree's tools by `apply` (F1); the commit and the undo commit limited by `--` to the
five files ("5 files changed, 654 insertions") (F2).

Where the real run differs: the real list is checked by `apply.sh` at your apply, never before (the CTO's sessions do
not open the sets root); the real sets root holds the hidden sets (4,560 hidden files at ACT-SETS-GLOBS-1's check), which
this ACT neither reads nor adds to.

## 7. The review
`.gov-runtime/scratch/orchestrator/reviews/ACT-W2-149-INSTALL-1-review-r1.md`: round 1 **READY by `verdict.py`** (a fresh read-only session, `independent-auditor` on `DAEO-52ku`, effort max; class
vote **(O)**; it reviewed `apply.sh` `e52f548e979a…`, re-ran the rehearsal's steps on its own clone and planted roots).
K1 and K6 were marked fail with no blocking finding; seven findings, all in scope, none both ordinary work and fail-open
or work-losing:
- **F1** (K1; yes, other): `parse_check` wrote a `__pycache__` into the tree's tools: fixed (`python3 -I -B`).
- **F2** (K1; yes, other): the §5 commit took everything staged in the shared main tree: fixed (`-- governance/project/indep-briefs/sgx1`).
- **F3** (K5; no, other): the four globs were unquoted, so a caller's folder could make `check` refuse falsely: fixed (an array, quoted).
- **F4** (K5; yes, other): the pinned script hash means this ACT stands only if applied before the wiring follow-up: §3.
- **F5** (K6; yes, other): the class is (O) by the `walled-sessions` row, not (b): §0.
- **F6** (K7; yes, other): the declaration's pin `f000adda4` holds no brief; re-pin at or after this ACT and the follow-up: §3.
- **F7** (K8; yes, other): the briefs' exclusion from the walls' trees is an entry criterion of the follow-up: §8 item 2.
Round 2 (`-r2.md`, the narrow re-check of the fixes in `apply.sh` `871d2c9db3dc` and this text): **READY by `verdict.py`, K1-K6 all pass** (a fresh read-only session, class vote **(O)**, `apply.sh`
`871d2c9db3dc…`; it ran both §5 commits as written in a tree with another session's staged and unstaged changes: each
limited to the five files). Two findings, neither ordinary work, both other: **F8** the rehearsal's own F2 step could
not show the `--` limit (no foreign staged change in the clone), and its undo commit staged first where §5 does not;
**F9** §5 has no step for a commit that stops (it fails closed: nothing is committed, and the launch script reads briefs
only at `--commit`, so nothing launches under them; send the output to the CTO).

## 8. Residuals
1. **Set-up A's wiring** (§3): a W2-149 follow-up, tests first; it rebuilds this ACT unless this ACT is applied first
   (review F4); the declaration's pin moves to a commit at or after both (review F6).
2. **The briefs in every tree:** once committed, the five briefs are in every worktree and, because `tree-exclude.txt`
   does not exclude `governance/project/indep-briefs/`, in every wall's tree: the tuning writer's tree holds the
   held-out writer's brief, and each labeller's holds the other's (an ordinary tree-wide Grep for a decision id would
   surface it). Each brief stages its own copy as `brief.md`, so excluding the folder costs nothing. **An entry criterion
   of the wiring follow-up (DEC-803; review F7):** `governance/project/indep-briefs/**` added to `tree-exclude.txt` (with
   the guard's code, which the sandbox experiment's README already asks to exclude), an owner-approved template change
   landing at or before the new pin. Until then no wall runs under these briefs (§3), so nothing is exposed to a wall;
   reads in the worktrees are open by DEC-820 as for any committed file.
3. **The list's live state is checked only at your apply** (§4): the CTO never opens the sets root.

**What it costs:** five files in the repository, nine lines in the list; no install, no GPU; your yes and one minute.

**Basis:** question 2 (the sets' independence enforced by the owner's list, not by trust: only briefs you approved can
start an independent session).

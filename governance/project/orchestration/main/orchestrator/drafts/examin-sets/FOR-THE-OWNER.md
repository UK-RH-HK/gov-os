# For the owner: EXAMIN's question set and the proving ground's held-out half, by the walled writer (DEC-1130 (3))

Everything is in `.gov-runtime/scratch/orchestrator/drafts/examin-sets/`. Nothing is installed, committed or launched. Nobody
opened the sets root or the run folders.

## What you approve
1. **Two fixed writer briefs** (read them; each is about 160 to 200 lines):
   - `EXAMIN-writer.md` for W2-94. sha256 `d37834e08c86e24c0fdb1884c4f11164d734af4dcb4b3a5536bd20e3efc0085f`.
   - `PROVING-GROUND-writer.md` for W2-93. sha256 `57820503b56948bf9e6ebe41abb2182c9a81db234e685218f21f71c69076549c`.
   These two hashes go into the approved list (`<sets root>/indep-walls/APPROVED`) by a later install ACT, as
   ACT-MEMORY-AUDIT-INSTALL-1 does for the memory audit's three. Each line reads
   `<sha256>  brief  writer  governance/project/indep-briefs/<name>`, and the briefs sit at those two repository paths
   (the walls' trees leave that folder out). If your answers below change a number in a brief, the hash is taken again
   and you approve the new one.
2. **ACT-EXAMIN-SETS-1** (`ACT-EXAMIN-SETS-1.md` and the bundle): class (a), tightening only. It needs no yes from you; if you
   want to give one, the line is `yes ACT-EXAMIN-SETS-1 e8020292` (round 2, on the map `f4029cfb4942`; the r1 line `97d45565` is superseded). It adds two entries to the path map. **The guard
   already refuses any new set's hidden folder** (ACT-SETS-GLOBS-1's wildcard), so this ACT closes no guard gap: it makes the
   sets declared. The measure needs the declaration in the sets root's own map, which is yours by hand (step 3).

## The order
1. You read the two briefs and answer C1 to C8 below. The CTO re-hashes if a number changes.
2. The independent review of ACT-EXAMIN-SETS-1; then the operator applies it (`apply.sh check`, `apply`; `undo` is ready).
3. **Your hand, once:** `bash tools/sets_root_map.sh check`, then `apply`, on `~/gov-os-eval/governance/project/path-map.yaml`
   (keeps `path-map.yaml.pre-ACT-EXAMIN-SETS-1`; `undo` puts it back while the map is as the step left it).
4. The install ACT: the two lines in the approved list, and the two briefs committed under
   `governance/project/indep-briefs/` (both are yours: class O). The CTO writes it after step 1.
5. W2-93 waits for W2-81 to merge: the writer reads W2-81's README and builders from the launch commit, which must be on
   `w2/integrate`. W2-94 waits for C1 (the copy's exact path) and its own dependency.
6. The CTO launches each writer (counts only come back). For W2-94 the CTO first makes the launch clone (below).
7. **Your hand, once, after W2-94's delivery:** `bash tools/release_visible.sh ~/gov-os-eval examin` copies the development
   half (`hidden/visible/q*.yaml`) into `visible/`, where the measure reads it and the guard leaves it open. `--undo` removes
   the copies. Rehearsed on a planted folder (release, refuse a second release, undo, refuse a stray file).

## How the wall gives each writer its repository
- **W2-93:** the walled tree is a plain copy of Gov OS at the launch commit (it holds `tests/acceptance/W2-81/`). The brief
  names the eight W2-81 files the writer may read, and the ones it may not (the self-tests, stand-ins, judge, runner, W2-93's
  own tests).
- **W2-94 (the owner's copy):** the launch script builds the tree from the git repository it is run in, and reads the
  walls' template and the brief from that repository's commit. It cannot take another repository as its tree today.
  **Recommended (C2, no code):** the CTO makes the launch clone of the owner's copy by exact path (DEC-723 (3):
  `git clone --no-hardlinks <exact path> ~/gov-os-runs/W2-94/examin`), checks that `governance/project/` is not already
  there (if it is, stop and ask you), cuts the branch `w2/integrate` (the name the script accepts as the main line), and
  adds **one commit**: the six template files byte for byte, `governance/project/indep-walls/COPY-HEAD.txt` (the copy's own
  40-digit commit), a `governance/project/path-map.yaml` holding only `sets_root_hidden` (the script refuses without it), and
  the brief. The wall's tree is then `git archive` of that commit less `tree-exclude.txt`: only what the copy's commit
  tracks (no uncommitted edit, no untracked file) plus that scaffold, which the brief tells the writer to ignore. Nothing
  is written in the owner's copy, in `~/gov-os-workbench`, or in EXAMIN's real repository. Rehearsed end to end on a
  invented repository with the real launch script's `--dry` (`launch-rehearsal.log`, 14 checks, `failures: 0`).

## Choices only you can make
| # | Question | Recommendation |
|---|---|---|
| C1 | **Which copy of EXAMIN, at which commit?** The brief says "the owner's copy". | `~/gov-os-workbench/examin/` (DEC-723), at its current committed HEAD. Give the CTO the exact path, and say if the copy is current. Only committed files are used, so the copy's uncommitted edits (DEC-736 names `CLAUDE.md` modified and `AGENTS.md` untracked) are not in any question. |
| C2 | **How the wall gets the copy.** | The launch clone with one scaffold commit (above, no code). The other way is a `--repo` option in the launch script (code, tests first, one review, days): cleaner, slower. |
| C3 | **W2-94's size.** The ticket says 10 to 20. | 20: ten categories, two each, ten visible and ten hidden. Fewer than 14 and the writer writes none. Ten hidden questions give a coarse figure (one miss is 10 points); more is not allowed by the ticket. |
| C4 | **The visible half.** The script delivers only into `hidden/`, so the development half lands in `hidden/visible/` and your step 7 releases it. The draw is the writer's by rule: for each category, the seed plus the category's number decides which of its two questions is visible, and `DRAW.txt` records it (the seed is recorded before the writer starts). | Keep the release step. The other way is no visible half, using W2-88's tuning set (S12) instead; that changes the ticket's first line. |
| C5 | **W2-93's size.** The ticket says at least 10 per repository, and at least one variant per kind the visible builders do not produce, and the validator's line asks for it per repository. | 10 questions per repository (60) and 13 variants: one for each core kind a repository's visible builder does not plant in it (11) plus one legacy-document and one large-file (2); none in the clean twin. This meets both lines. 12 questions per repository costs a little more and risks one refused template (a bad template refuses the whole run). A minimum of 7 variants meets the second line only. |
| C6 | **Two lines of W2-93 no session without a shell can meet:** "checked on a built copy" and `validate_hidden.py` (run before every commit, recorded). Also W2-81's runner takes `--hidden <folder>`, and a folder under the sets root cannot be named on the CTO's line (the guard's line rule). | The writer writes the data only. A generic `validate_hidden.py` (it holds no hidden content) is written under W2-93 by an independent test designer, and both it and the W2-81 runner gain a `--sets-root <root>` option so a line names only the root. W2-81 is still open, so that line can be added now (a row for the CTO). Until then the check is run by your operator, counts only. |
| C7 | **`measures` by roles or by tickets.** The tickets say by tickets. | By roles, as `memory-verdict-2` and the three entries before it. Any session of the set's roles is refused in a tree too; the wildcard covers every set anyway. |
| C8 | **A checker for W2-94.** The memory audit has a checker pass (rubric tests on each question, the other places that state each answer). This package has none: one writer, one round. | One checker run is worth having, because line 4 ("holds the answer") is the ticket's own bar and one Sonnet pass is not independent of itself. It needs a variant of the audit's checker brief for a repository with no decisions or contract (W2-88 S19's two replaced parts) and your approval. Not written here: the lines bound this package. |

## Risks and things to know
- **No real writer session was run.** The launch script built both walls and trees (`--dry`, planted sets root); the
  sessions themselves (Claude, headless) are untried with these briefs.
- **The `effort: high` line in a brief is not enforced** until W2-173 S1 (the script passes the model only). The sessions
  run at the CLI's default effort until then; the digest should say so, as the memory audit's does.
- **The launch script reads one audit log for every set** (`<runs>/indep/AUDITS.log`, written only when an auditor delivers). After
  the first memory audit (11-23) its last line holds a Gov OS commit that the EXAMIN launch clone lacks, and the script
  refuses (code 14). Launch W2-94 before then, or put `GOV_INDEP_RUNS_DIR=<an absolute folder outside the sets root>` before
  the command (the script allows it).
- **The writer's sample is drawn from the tree**, scaffold files included; the brief tells it to skip those.
- **EXAMIN is your product.** The brief tells the writer to skip any secret, key, `.env` file or real person's data, and the
  walls give it no shell or network. The questions are read by sessions measuring memory on EXAMIN's copy, so read the
  visible half before step 7's release if you want to.
- **The ticket texts need new wording** (the CTO brings it, DEC-757 (6)): W2-94's lines 2 and 3 name a clone and a session
  under the old route, and "sends half to the visible folder" becomes the release step; W2-93's line 5 names a script the
  walled writer does not write.
- **Whoever commits the two briefs and the approved-list lines** is yours (class O rows `walled-sessions`).

## Files
`ACT-EXAMIN-SETS-1.md`; `acts-r2/ACT-EXAMIN-SETS-1/` (round 2: manifest, apply.sh, list, before/after, rehearsal.log); `ACT-EXAMIN-SETS-1.r1/` (round 1, superseded); `EXAMIN-writer.md`;
`PROVING-GROUND-writer.md`; `rehearsal.r2.log` (the chain, 124 checks, `failures: 0`; `rehearsal.r1.log` is round 1's); `launch-rehearsal.log` (14 checks, `failures: 0`);
`tools/` (`insert_entries.py`, `entries.yaml`, `sets_root_map.sh`, `release_visible.sh`, `examin_check.py`, `store_check.py`,
`rehearse_r2.sh`, `build_r2.py`, `apply_r2.sh.tpl`, `rehearse.sh` (r1), `launch_rehearsal.sh`, `mk_fake_examin.py`, `make_manifest.py`).

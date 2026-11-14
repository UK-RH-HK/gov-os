# The re-pin from release 0.1.0: the preparer's notes (2026-11-14; DEC-1178 (3), P-RELEASE-1 §6)

For the CTO and the reviewer. The operator's page is `README.md` beside this file. Modelled on window 5's bundle
(`pin/REPIN-COMMANDS-W5.sh`, `repin7_checks.sh`, `repin7_registry.py`, `rehearse_repin7.sh`, its review
`reviews/ACT-REPIN-W5-review.md` READY, and the `log/repin-w5-rehearsal-*` logs).

## 1. The files
| file | what | from |
|---|---|---|
| `REPIN-COMMANDS-REL.template.sh` | the operator's script with four slots: `C`, `EPOCH`, `SHA` (the record's wheel sha256), `RECORD` (manifest.json's sha256); VERSION `0.1.0`, TAG `v0.1.0`, OLD `797495bdfc70` fixed | window 5's script, plus part R; built-from-C check now against the record's sha256; §5's two lines and P-2's line after the switch; the registry commit cites DEC-1178 |
| `fill_release.sh` | the CTO's step at "released": `bash fill_release.sh <C>` first checks `sha256sum -c BUNDLE.sha256` (the reviewed files; review F6), then reads the tag and the record, refuses unless they agree with C, writes `REPIN-COMMANDS-REL-0.1.0.sh` and the hash list `REPIN-REL-0.1.0.sha256` (18 files, absolute paths; 13 in the review's version) | new (RL-1: nothing copied by hand) |
| `rel_checks.sh` | part B's checks | `repin7_checks.sh` unchanged but: the old pin `797495bdfc70`; section 3d (the builds since window 5: `gov adapters`, `wait`, `dispatch`, `impact`, `session-watch`, `skilleval`, `release` answer `--help`; `gov.release` build/verify and `gov.wait.liveness` import) |
| `rel_registry.py` | part E's registry edit | `repin7_registry.py`: replaces window 5's entry (`797495bdfc70`, `04b094fb…7c3`); six arguments (adds version, tag, record sha256); the note names the release and the record; `approved_by: DEC-1178` (see 4, R-1) |
| `rehearse_rel.sh` | the rehearsal: the scratch mirror plus a scratch release in a scratch clone | `rehearse_repin7.sh` plus the scratch release, fill and three new negative modes |
| `README.md` | the operator's page (draft) | `ACT-REPIN-W5.md`'s form |
| `pin/smoke_repin5.sh` and the 9 CTO tools | used by path; in the hash list `fill_release.sh` writes | 9 of these 10 files are window 5's reviewed bytes (`sha256sum -c pin/REPIN-W5.sha256`: 12 of its 13 lines OK). **`tools/heavy_slot.sh` is not:** it is the DEC-1157 version (11-12 23:46, `heavy_slot.sh.pre-dec1157` beside it), which no review record covers. This bundle's rehearsals ran with it, and `fill_release.sh` hashes whatever is there at fill time, so the post-fill review covers its bytes (review F3) |
| the 5 files part B also runs, **now in the hash list** (18 files; the CTO's decision on review F3, 2026-11-14) | read or run by path | `drafts/act-guard-fix-4/test_guard_fix_4.py`, `drafts/g14/test_g14.py`, `tools/heavy_slots.conf`, the staged W2-141 pair `docs/changes/W2-141-hook/{pretooluse.py,role_reads.py}`. Window 5 left them outside its list. Part B also runs files that stay outside the list because they are the main tree's committed files: `tests/unit/hooks/test_live_hook.py`, `tests/unit/guard/test_w2_141_search.py` and the live `.claude/hooks/` |

## 2. Part R (RL-1), in order; each failure is `STOP`, nothing built
1. `v0.1.0` is an annotated tag (`git cat-file -t` = `tag`) in the release repository (live: the main tree).
2. Its commit has exactly one parent, and that parent is C in full (§4 step 6 tags the record commit; a tag on C itself
   is refused, as the install path would refuse it, `release/__init__.py:307-309`).
3. `git diff --name-only C <tag>` is exactly `docs/releases/0.1.0/manifest.json` and `manifest.sha256`.
4. `sha256sum -c --strict manifest.sha256` on the two files read from the tag.
5. manifest.json's sha256 = `RECORD`.
6. The manifest's `version` 0.1.0, `commit` = C in full, `cli_version` 0.1.0, `wheel.name`
   `gov-0.1.0-py3-none-any.whl`, `wheel.sha256` = `SHA`.
7. `EPOCH` = C's commit time.
8. `gov.release.verify` (the old pin's, the code `gov release` ran; §4 step 3 says it is the head's own) on the tag's
   `template/` tree and record: the shipped files hash to the record's list.
9. The tag's commit is in `w2/integrate`'s history (live only: in the rehearsal the record commit is in the scratch
   clone and the branch in the main tree).
Then part A's two builds must equal `SHA`, the record's, so the pin is the release's wheel; after the switch the script
prints §5's two added lines (wheel sha256 = the record's; `readlink -f ~/.local/bin/gov` names `pin-<C12>`).

## 3. The rehearsal (`rehearse_rel.sh`; stand-in C = the main tree's `w2/integrate` head when each run started)
Each run builds a scratch release in a shared clone under `/tmp/gov-os-rel-repin/<mode>/release`, using the live
pin's own `gov.release.build` (what `gov release 0.1.0` runs, without the typed code). It commits the record as
§4 step 5 does, puts an annotated scratch tag `v0.1.0` on the record commit, fills the script with `fill_release.sh`,
checks the hash list, and runs the filled script against the mirror. The main tree got no tag, ref or commit: every
log's "main tree tags v*" and "docs/releases" lines are the same before and after.

**Final logs, after the review's fixes (`-f7`; all 8 modes on stand-in C `f2f28ed4ef40`, 2026-11-14 16:47 to 17:23).**
Provenance (review r2 F2). The f7 runs ran the bundle of 16:45 (BUNDLE before 5dae7e86), and their logs show the
13-file list. Files changed after every f7 run:
- `fill_release.sh` (17:25, the 18-file list) and README.md (17:25, "18 OK lines"). `-neg-sha-h18` ran with that
  fill_release.sh.
- After review r2, these changed again: the template (the trap: polling, HUP, the pid of an early signal), `rel_checks.sh`
  (FIX-3 refuses an error), `rehearse_rel.sh` (neg-int times the STOP) and README.md (the Ctrl-C line).
  `-neg-int-r2` and the hand logs below ran with them.
- `rel_registry.py` is unchanged since every f7 run. The template's parts 0, R, A, B, C, D, H and E are unchanged since
  run f7. The FIX-3 change does not alter run f7's outcome: its kept outputs pass the new check
  (`log/repin-rel-hand-checks-dry.txt`). So run f7 still stands for the full run, and the other f7 negatives for theirs.
- The neg-check log postdates every change to its path (review F4).

| log | outcome |
|---|---|
| `log/repin-rel-rehearsal-run-f7.txt` | **REHEARSAL OK, exit 0, 2,142 s.** R: tag on the record commit `d49f63081ab2`, record only, record sha256 `88c7df9abd06`, `verify` holds. A: both builds `cb69013f7c04…7250` = the record's wheel sha256. S: 1,786 s, nearly all of it waiting for a heavy-job slot (R-6). B: ALL CHECKS PASS: guard4 453; FIX-4 2 failed, **both named** ("fix3 python heredoc reading .env (gap as today)", "fix3 unterminated heredoc naming acceptance judged as before"); live hook 267; g14 151, and the staged pair's 4 red by name; FIX-3 49 failed under both pins, 48 under both, **the two differing cases named** (F1, F2). C: the reranker has the new pin's bytes. D: §5's two lines; P-2. E: trailers `Task: decision-record`, `Implements: DEC-1178`, `Role: owner`; one gov entry, `approved_by` DEC-1178. Live fixed paths UNCHANGED; the live store moved with the CTO's W2-188 landing `28acb676c` (no `src/` change). |
| `-neg-check-f7.txt` | NEGATIVE RUN OK: STOP at part B (171 s), "the store link is back on W2-00-store-a", gov link unchanged |
| `-neg-int-f7.txt` (new, F7) | NEGATIVE RUN OK: TERM 1,911 s in, while part S's refresh ran (after its GPU-slot wait). "the store refresh (pid 294354, its process group) was stopped", "STOP: interrupted (TERM) before the switch", exit 1. 20 s later the store link was still on W2-00-store-a and the group was gone; gov link unchanged |
| `-neg-tag-f7.txt` | NEGATIVE RUN OK: STOP at part R (the tag on C itself); `fill_release.sh` REFUSED too; nothing built |
| `-neg-manifest-f7.txt` | NEGATIVE RUN OK: STOP at part R (manifest.json does not match manifest.sha256); `fill_release.sh` REFUSED too |
| `-neg-sha-f7.txt` | NEGATIVE RUN OK: the hash list fails on the edited script; run anyway, STOP at part R (the manifest's wheel sha256 is not the one filled in) |
| `-neg-src-f7.txt` | NEGATIVE RUN OK: STOP at part 0 (src differs), before R |
| `-neg-uncommitted-f7.txt` | NEGATIVE RUN OK: STOP at part 0 (uncommitted src) |

F6 tested by hand (`log/repin-rel-hand-f6-refusal.txt`): a copy of the bundle with one byte added to `rel_checks.sh`
gave "rel_checks.sh: FAILED" and "REFUSED, nothing written", exit 1, with no file written.

**The 18-file hash list (the CTO's decision on F3, after run f7; the template unchanged, so run f7 stands):**
- Positive (`log/repin-rel-hand-fill-positive.txt`): `fill_release.sh f2f28ed4ef40` on `run-f7`'s scratch release wrote
  an 18-line list, and `sha256sum -c` printed 18 OK. The filled script carries run f7's four values; it differs from
  the template only in the four value lines.
- Changed byte (`log/repin-rel-hand-changed-byte.txt`): a copy of `test_g14.py` with one byte added, named in a copy of the list in place of the real file
  (the real file was not touched). The operator's line printed "FAILED" and exit 1, so the script would not run.
  `fill_release.sh` itself hashes these 14 files as they stand at fill time; they are not in BUNDLE.sha256, so the
  operator's check and the post-fill review cover them.
- Unreadable file (`log/repin-rel-hand-unreadable.txt`): in a scratch copy of the bundle with its root moved, `fill_release.sh` printed "REFUSED, nothing
  written: a file the script runs cannot be read", exit 1, with neither the script nor the list written.
- `log/repin-rel-rehearsal-neg-sha-h18.txt`: NEGATIVE RUN OK. The 18-file list fails only on the edited script, then
  STOP at part R.

**After review r2 (`review-r2.md`, PASS, 0 blocking; its F1, F5 and F7 folded in):**
- `log/repin-rel-rehearsal-neg-int-r2.txt` (stand-in C `41ab6597992d`, the head then; the slots were free): NEGATIVE
  RUN OK. TERM 20 s in, while part S's refresh ran. The script ended **1 s after the TERM**, saying "the store refresh
  (pid 751100, its process group) was stopped, 0 s after the signal", then "STOP: interrupted (TERM) before the switch",
  exit 1. 20 s later the link was still on W2-00-store-a and the group was gone; live paths unchanged.
  (`-neg-int-f7` took about 72 s: its watchdog inherited the ignored TERM, review r2 F1.)
- `log/repin-rel-hand-signal.txt`: the template's handler lines, word for word, in a harness with a fake refresh in
  its own session:
  - a refresh that dies on TERM: STOP 0 s after the signal;
  - a signal between the fork and `rp=$!` (review r2 F5): the handler takes `$!` and stops the group, 0 s;
  - a refresh that ignores TERM: KILLed after 60 s, then STOP.
- `log/repin-rel-hand-checks-dry.txt`: the FIX-4 and FIX-3 blocks cut from `rel_checks.sh` as it stands, on run f7's
  kept outputs: the positive passes, naming the differing cases. Six planted variants each fail part B:
  - an unnamed FIX-4 refusal;
  - a FIX-4 error;
  - an unnamed FIX-3 new-only refusal;
  - the named old-only case in the wrong direction;
  - a FIX-3 error under the new pin;
  - a FIX-3 error under the old pin (review r2 F7).
- Not rehearsed, shown by reading only (review r2 F6):
  - a real Ctrl-C to the whole foreground group;
  - the link put back after the refresh flipped it;
  - a signal after the switch;
  - the move-aside of an earlier folder.
- Review r2 F4 (BUNDLE.sha256 itself is not checked against the reviewed value) is for the hand-over: before handing
  over, the CTO compares BUNDLE.sha256's own sha256 with the last review's `reviewed_sha256`.
- Since run f7's stand-in, `src/gov/launch/` changed (W2-184 `f2f76a154`, 3 files). Run f7 shows the method, not the
  wheel at the real C; the rehearsal at the real C is required in any case.

**The logs the review read (before its fixes; kept):**

| log | stand-in C | outcome |
|---|---|---|
| `log/repin-rel-rehearsal-run-r5.txt` | `bf04ed69c893` | **REHEARSAL OK, exit 0, 1,008 s.** R: tag on the record commit, record only, `manifest.sha256` OK, record sha256 `71e998f490e1`, `verify` holds. A: both builds `59cfc7237dae…2df7b` = the record's wheel sha256. S: 183 s. B: ALL CHECKS PASS (3d included; FIX-4 2 stricter, FIX-3 48 both + 1 + 1 stricter; g14 151 and 4 red by name; live hook 267; guard4 453; hook 0.16 to 0.20 s). C: the reranker has the new pin's bytes, so no restart. D: the smoke calls; the search 3.2 s; §5's two lines; P-2. H. E: the registry commit has trailers `Task: decision-record`, `Implements: DEC-1178`, `Role: owner`; one gov entry. The live fixed paths are UNCHANGED; the live store moved with the CTO's landings, as shown. |
| `-neg-src.txt` | `18a279055d99` | NEGATIVE RUN OK: STOP at part 0 (src differs), before R |
| `-neg-uncommitted.txt` | `18a279055d99` | NEGATIVE RUN OK: STOP at part 0 (uncommitted src) |
| `-neg-tag.txt` | `18a279055d99` | NEGATIVE RUN OK: STOP at part R ("not on the record commit whose parent is C"); `fill_release.sh` REFUSED too; nothing built |
| `-neg-manifest.txt` | `18a279055d99` | NEGATIVE RUN OK: STOP at part R (manifest.json does not match manifest.sha256); `fill_release.sh` REFUSED too |
| `-neg-sha.txt` | `18a279055d99` | NEGATIVE RUN OK: the hash list fails on the edited script (the operator's line would stop there); run anyway, STOP at part R (the manifest's wheel sha256 is not the one filled in) |
| `-neg-check.txt` | `4ac8f7955359` | NEGATIVE RUN OK: STOP at part B (the staged pair's planted import), "the store link is back on W2-00-store-b", gov link unchanged. It ran 15:17 to 15:24, before rel_checks.sh's last change (15:30, section 7, after the stop); `-neg-check-f7.txt` replaces it (F4) |

**Earlier runs (kept, each fixed before the final logs):**
- `-run-r1-stopped.txt`: stopped by me at part S. I had edited the rehearsal script during the run, and bash reads a
  script as it runs. Every later edit was an atomic replace.
- `-run-r2.txt`: STOP at B. The 3d check's pattern missed `session-watch`, whose help line wraps. Fixed. The STOP path
  worked: the store link went back.
- `-run-r3.txt`: STOP at B, `test_guard_fix_4.py` 2 failed. This is W2-42a's stricter guard (R-5); the checks were
  changed. `log/repin-rel-checks-direct.txt` is the direct run that found the FIX-3 difference of the same kind.
- `-run-r4.txt`: ALL CHECKS PASS, then STOP at C because the CTO's merge queue was landing (R-7).
- `-neg-check-r1-verdict-bug.txt`: the script stopped correctly. The rehearsal's verdict wrongly required that no pin
  was built (B comes after A). Fixed.
- In runs r2, r4 and r5, two separate commits gave the same bytes from the release's build and from the re-pin's:
  `494d5c9335fa` gave `4376c78ba335…`, `eb63df3c349c` gave `e68caaa25c6d…` and `bf04ed69c893` gave `59cfc7237dae…`
  (R-4). In run f7, a fourth commit, `f2f28ed4ef40`, gave `cb69013f7c04…`. The two scratch releases of `run-f7` and
  `neg-int-f7`, each built separately, gave the same filled script (sha256 `e735535d10c6…`), so the record at a given C
  is reproducible.

## 4. Open points for the review and the owner
- **R-1, `approved_by` in the registry entry.** Every window's gov entry so far cites DEC-1037 (the re-pin windows).
  This one cites DEC-1178 (the owner's decision of the release and the re-pin from it). Within the CTO's purpose; the
  reviewer may ask for DEC-1037 kept. No owner question.
- **R-2, the registry commit's trailers:** `Task: decision-record`, `Implements: DEC-1178`, `Role: owner`, the form of
  window 5's identical commit `8f00bb908` (`Implements: DEC-1125`). What carries the commit is `Role: owner`, which the
  landing check passes (P-RELEASE-1 §4, `landing_check.py:10-13`). Gate (h) does not measure it: its governance-record
  list does not include `governance/project/tool-registry.yaml` (`src/gov/close/gates.py:27-30, 144-165`). The record
  commit of §4 step 5 takes `Task: DAEO-sdxk` (P-RELEASE-1's proposal). (Review F5 corrected the reason given here.)
- **R-3, the restart of the reranker** stays unrehearsed (the live service is never restarted in a rehearsal), as in
  windows 4 and 5.
- **R-5, the guard is stricter under the new pin (W2-42a, landed since `797495bdfc70`).** Its fail-closed shell
  reading refuses two forms window 5's pin let through: "fix3 unterminated heredoc naming acceptance judged as before"
  and "fix3 python heredoc reading .env (gap as today)". Window 5's checks required ACT-GUARD-FIX-4's suite to pass in
  full and FIX-3's failures to equal the old pin's; both stopped run r3 (a correct STOP: the store link went back).
  `rel_checks.sh` accepts these differences **by name only** (review F1, as `G14_RED`): `FIX4_ACCEPT` holds FIX-4's two
  `test_planted` cases, each only as "want allow, got deny"; `FIX3_NEWONLY_ACCEPT` holds the one case failing only
  under the new pin ("fix3 python heredoc reading .env (gap as today)", "want allow, got deny"), and
  `FIX3_OLDONLY_ACCEPT` the one failing only under the old pin ("fix3 unterminated heredoc naming acceptance judged as
  before", "want deny, got allow" there). Any other failure fails part B: a lost refusal, and also a new false refusal
  of ordinary work (such as "rule 5: a reviewer's record"). Both ok lines print the case names, so the logs keep them
  (review F2). A dry run on r5's kept outputs passed, and three planted variants failed: an unnamed FIX-4 refusal, an
  unnamed FIX-3 new-only refusal, and the named old-only case in the wrong direction (now kept:
  `log/repin-rel-hand-checks-dry.txt`). g14, FIX-4 and FIX-3 (under both pins) also fail on a pytest error now, not
  only on a failure (window 5's review F6; review r2 F7).
- **R-8, an interrupt, a rerun (review F7, window 5's F5; review r2 F1, F5).** An INT/TERM/HUP trap (`on_signal`).
  Before the switch it stops part S's store refresh by its process group: TERM, re-sent at each half-second poll until
  no live process is left, KILL after 60 s. The refresh runs under `setsid`, so a Ctrl-C does not reach it. It also
  takes `$!` as the refresh's pid when the signal came before `rp=$!`. It puts the store link back if the refresh moved
  it, and STOPs. After the switch it rolls back. An
  earlier run's `/tmp/repin-rel-0.1.0` is moved aside with its time, never removed, and the operator's line uses
  `tee -ai` (it appends, and tee keeps logging through a Ctrl-C). The new mode `neg-int` rehearses the trap: a TERM
  while the refresh runs. A refresh stopped part-way leaves the spare half unfinished; the next forced refresh rebuilds
  it, and the link never names it.
- **R-6, the heavy slots.** In runs r2 and r3, part S waited for a free heavy-job slot (other sessions' tests): the
  rebuild took 1,013 and 695 s wall, nearly all of it waiting; with the slots free (r4) it took 71 s. Part B's suites
  wait the same way. At the owner's sitting the CTO's hold should also leave the slots free (no worker test runs from
  the hand-over), or the act runs long.
- **R-7, the quiet point is live.** Run r4 passed every check (ALL CHECKS PASS) and then STOPped at part C because the
  CTO's own merge queue was landing (`merge_queue.py run`): the right stop (the store link went back, nothing
  switched). At the sitting the hold keeps the merge queue still; the CTO checks no landing runs before the hand-over.
- **R-4, the epoch:** the release's own build (`gov.release._wheel`, setuptools' `build_wheel` on `git archive C
  pyproject.toml src`) and the re-pin's (`pip wheel --no-build-isolation` on `git archive C`) gave the same bytes in the
  rehearsal (part A against the scratch record). This is P-RELEASE-1 §5's claim, now shown on one commit; the rehearsal
  at the real C shows it again.

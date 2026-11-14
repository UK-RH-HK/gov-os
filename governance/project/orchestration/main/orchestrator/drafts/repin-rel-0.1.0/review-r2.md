# Review r2: ACT-REPIN-REL-0.1.0, narrow check of the fixes after review.md

task: ACT-REPIN-REL-0.1.0
decisions: DEC-1178, DEC-801, DEC-808, DEC-1010, DEC-1014

**Scope.** I checked only the change since BUNDLE.sha256 75ab992b…. That covers the round-1 rows F1 to F7, the trap, the moved-aside earlier folder, `tee -ai` and the 18-file hash list. I read the bundle at BUNDLE.sha256 5dae7e86…b36e, and the eight `-f7` logs plus `-neg-sha-h18`. I ran none of the bundle's scripts and read nothing hidden or held out. The guard refused one scratch reproduction ("could not decide"); I did not retry it. This is the second review round (DEC-1010).

**Classification.** 0 blocking, 7 rows (F1 to F7). None of them both fails open or loses work and can be reached in ordinary work.

## The round-1 rows

| row | asked | now |
|---|---|---|
| F1 | accept by name only | **Resolved.** `FIX4_ACCEPT` (rel_checks.sh:243-244) accepts only the two names it lists, each only as "want allow, got deny" (:250-255). `FIX3_NEWONLY_ACCEPT` and `FIX3_OLDONLY_ACCEPT` (:295-296) accept one name each, in one direction each (:301-313). Any other failure fails part B. |
| F2 | print the names in the ok lines | **Resolved.** The ok lines print them (:257, :315). run-f7 log:83 and :87 name both cases. |
| F3 | NOTES wording | **Resolved.** NOTES.md:16 says plainly that heavy_slot.sh is not window 5's copy. NOTES.md:17 names the 5 extra files. They are now hashed (fill_release.sh:51-55). |
| F4 | NOTES wording | **Resolved for neg-check.** neg-check-f7 started at 16:47:02, after the last edits to rel_checks.sh (16:44:48) and the template (16:45:20). There is a new wording slip; see row F2. |
| F5 | NOTES wording | **Resolved.** NOTES.md:106-110 now gives `Role: owner` and the landing check as the reason, and says gate (h) does not measure the commit. |
| F6 | `sha256sum -c` first, "REFUSED, nothing written" | **Resolved.** fill_release.sh:13 runs `sha256sum -c --strict --quiet BUNDLE.sha256` before anything else is read. On failure it prints "REFUSED, nothing written: …" and exits 1. |
| F7 | move aside, `tee -ai`, trap | **Resolved in the code.** template:62 moves the earlier folder aside with `mv -T` to a name with its time; nothing is removed. template:12 and README:56 use `tee -ai`. `on_signal` (template:104-121) stops part S's refresh by its process group (TERM, 60 s, then KILL). It puts the store link back if the refresh moved it (:113), then STOPs before the switch or rolls back after it. See rows F1 and F5. |

## Findings

**F1 (row): the trap's 60-second watchdog cannot be cancelled. Every interrupt during part S's refresh prints nothing for about 60 s before STOP, even when the refresh died at once.**
- `on_signal` first sets INT, TERM and PIPE to ignored (template:105). Only then does it start the watchdog subshell (:108). The subshell inherits the ignored TERM, so the `kill` that should cancel it (:109) has no effect. The `wait` on the watchdog then lasts the full 60 s, and the watchdog's KILL always goes out to the refresh's old group id.
- The log agrees. neg-int-f7:39 sends TERM at 1,911 s. The script ends at 2,003 s (:66), and the rehearsal's own 20 s sleep comes before that line (rehearse_rel.sh:198-209). So the handler took about 72 s.
- My scratch reproduction was refused by the guard. The evidence here is the log timing plus bash's rule that signals ignored in a parent stay ignored in its subshells.
- Effect: README:59 tells the operator "Ctrl-C is safe", then shows nothing for a minute. An operator who closes the terminal then sends a hang-up, which the script does not trap.
- Even then: the gov link is untouched. The store link is untouched unless the refresh had already flipped it, and the refresh only flips to a complete half (refresh_integration_store.sh:32). The new pin folder is left behind, so the next run stops at "already exists".
- After 60 s the KILL goes to a group id that may have been reused. Hitting that needs a pid reused within 60 s.
- Ordinary work: yes, because a Ctrl-C during part S, the longest part, is ordinary.
- Consequence: other. It fails closed; nothing fails open and no work is lost.
- What would reverse this: a neg-int log where STOP follows the TERM by well under 60 s, with the refresh group gone.

**F2 (row): NOTES §3 says the `fill_release.sh` and README that ran in the f7 runs are the bundle's bytes, and that only NOTES changed after. Both files changed after every f7 run.**
- NOTES.md:44-46 makes the claim. fill_release.sh is dated 17:25:32 and README.md 17:25:43. The f7 runs ran from 16:47 to 17:22, and their logs show "13 files" (run-f7:30, :38).
- NOTES.md:62-64 explains the fill_release.sh change in part. The README change is not mentioned.
- NOTES.md:16 says "12 of them are window 5's reviewed bytes" for a row of 10 files. It is 9 of these 10 (or 12 of window 5's 13-line list).
- The outcomes still hold. The template, rel_checks.sh and rel_registry.py are unchanged since the runs, and neg-sha-h18, run at 17:26:40, used today's fill_release.sh.
- Ordinary work: yes, because a reader relies on the stated provenance.
- Consequence: other (wording).
- What would reverse this: f7 logs dated after 17:25:43, or NOTES wording that names both later changes.

**F3 (row): several new claims rest on tests done by hand, with no kept log.**
- The by-hand tests are:
  - F6's changed-byte refusal (NOTES.md:59-60);
  - the 18-OK positive run, with a filled script identical to run f7's (:63-64);
  - the changed byte in test_g14.py (:65-66);
  - the unreadable-file refusal (:69-70);
  - the F1 dry run with three planted variants (:122-124).
- Only neg-sha-h18 is a log. It shows the 18-file list and one FAILED line for the edited script (h18:30, :39-40).
- Reading the code supports each claim: fill_release.sh:13, 51-57 and rel_checks.sh:250-255, 301-313.
- This is round 1's F2 again: the evidence lives only in scratch space.
- Ordinary work: yes, because a reboot, or `/tmp` being cleared before the post-fill review, is ordinary.
- Consequence: other (the evidence is lost).
- What would reverse this: kept logs of those runs under `log/`.

**F4 (row): `fill_release.sh` checks the files against BUNDLE.sha256, but not BUNDLE.sha256 itself against the reviewed value. An edit followed by a rehash passes the fill.**
- fill_release.sh:13 trusts whatever list is in the folder. Rehashing after an edit is the builder's routine step, done in this very round.
- This is what F6 asked for. The post-fill review (README:4) remains the backstop.
- Ordinary work: yes.
- Consequence: other. The post-fill review catches it.
- What would reverse this: a hand-over step or post-fill review that compares BUNDLE.sha256's own sha256 with the last review's `reviewed_sha256`.

**F5 (row): a signal in the single step between starting the refresh in the background and recording its pid leaves the refresh running, not stopped.**
- The window is template:231-233. The trap would find no pid, STOP, and the refresh could flip the store link afterwards.
- Ordinary work: no, because the window is one shell step.
- Consequence: other. The flip goes only to a half fully built at the run-time head, so nothing fails open and no work is lost.
- What would reverse this: evidence that bash cannot run the trap between those two steps.

**F6 (row): three trap branches and the move-aside are shown by reading the code, not by a rehearsal.**
- Not rehearsed:
  - a real Ctrl-C, which sends INT to the whole foreground group. rehearse_rel.sh:33-35 sends TERM to the script only.
  - the branch that puts the store link back when the refresh moved it before the loop saw the move (template:113). In neg-int the link never moved.
  - a signal after the switch, which should roll back.
  - the move-aside of an earlier folder. Each mode gets a fresh folder (rehearse_rel.sh:186).
- By reading, each is sound: the links only ever change by an atomic rename, and both `stop` and `rollback` are safe to run twice.
- Ordinary work: yes.
- Consequence: other.
- What would reverse this: logs that exercise each branch.

**F7 (row): the FIX-3 comparison does not refuse a pytest error under the new pin. FIX-4 and g14 now do.**
- rel_checks.sh:290 checks only for " passed". FIX-4 at :247 and g14 at :270 also refuse errors.
- A case that errors is not in the FAILED list, so it would be neither compared nor counted.
- Ordinary work: no, because only a setup failure on some of the parametrised cases produces it. If the whole suite errors, " passed" is absent and the check fails.
- Consequence: fails open (an unverified case passes).
- What would reverse this: showing that test_guard_fix_3.py's cases cannot error one by one.

## What I probed and found sound

1. **The hash list holds.** `sha256sum -c BUNDLE.sha256` and `--strict` both show all 7 files OK. BUNDLE.sha256's own sha256 is 5dae7e86c51f5bd524e42c71a30f5533433dfb9973744c17f728c6e94728b36e.
2. **The links cannot be left half-switched.**
   - The gov link (template:88, 275), the store link (:67) and the refresh's flip (refresh_integration_store.sh:32) all change by a link to a temporary name followed by `mv -T`. A signal at any point leaves the old or the new target, never a mix; at worst a stray `.tmp` or `.new` name.
   - PHASE becomes `switched` (:274) before the gov link changes, so a signal there rolls back, and rollback does no harm if nothing had switched yet.
   - After `live` (:312), the trap reports and does not roll back. That is correct: pin-C has passed its live checks.
   - `stop` and `rollback` are safe to run twice, which covers a second Ctrl-C landing inside a STOP.
   - The refresh decides "fresh" from the half the link names (refresh_integration_store.sh:25) and flips only when the rebuild exits 0 (:32). A refresh stopped part-way therefore leaves an unfinished spare half that nothing names.
3. **A STOP still puts the store link back.** neg-check-f7:84-85: "STOP: a check before the switch failed", then "the store link is back on W2-00-store-a". `stop` is unchanged (template:80-85).
4. **The 18-file list is written atomically.** It is written to `.tmp` and then moved into place (fill_release.sh:51-57). If any file cannot be read, both the filled script and the `.tmp` list are removed. Any partial state fails the operator's `sha256sum -c` (a missing file or a different hash), so it fails closed. The filled script is written the same way (:42-44).
5. **`tee -ai`** appears in the operator's line (README:56) and in the script's header (template:12). The `&&` binds the check to the whole pipeline.
6. **The logs support the claims.**
   - All 8 modes (run, neg-check, neg-int, neg-tag, neg-manifest, neg-sha, neg-src, neg-uncommitted) end with REHEARSAL OK or NEGATIVE RUN OK.
   - Every log reports the live fixed paths UNCHANGED. In run-f7 and neg-int, the live store moved with the CTO's landing 28acb676c, as the logs show (run-f7:133-144).
   - Every figure in the run-f7 row of NOTES.md:50 matches the log: 2,142 s; S 1,786 s; guard4 453; FIX-4 2, by name; live hook 267; g14 151 and 4 red; FIX-3 49/48 and the 2 differing cases named.
   - neg-int:58-65 shows the refresh stopped, STOP, and 20 s later the link on store-a with the group gone.
   - Both neg-tag-f7:38 and neg-manifest-f7:40 show fill_release.sh refusing.
   - neg-sha-h18:30 and :39-40 show the 18-file list failing only on the edited script.
7. **The trap stops the right processes.** `setsid` from a non-interactive script's background job makes the refresh's pid its session and group leader, so the group kill and the `ps -g` session check both name it. The services that gov starts in their own sessions (the reranker, ollama) are long-lived by design and never move the store link.

```verdict
verdict: PASS
blocking: 0
reviewed_sha256: 5dae7e86c51f5bd524e42c71a30f5533433dfb9973744c17f728c6e94728b36e
```

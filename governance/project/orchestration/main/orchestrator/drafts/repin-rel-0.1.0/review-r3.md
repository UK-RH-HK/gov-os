# Review r3: ACT-REPIN-REL-0.1.0, narrow check of the fold after review r2

task: ACT-REPIN-REL-0.1.0
decisions: DEC-1178, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-820

**Scope.** I checked only what changed since BUNDLE 5dae7e86: review r2's F1, F5 and F7, NOTES F2 and the hand logs (F3). I read nothing held out and no secret. The guard refused nothing.

**Classification.** 0 blocking, 8 rows. None of them is all three of: in scope, reachable in ordinary work, and fails open or loses work.

## Q1: are the folded findings fixed?

To see what changed, I compared run f7's filled script with the current template. Ignoring the four filled values, they differ only in the header comment (template:14-16), :61, :102-118, :129, :239 and :251. So parts 0, R, A, B, C, D, H and E are unchanged since f7, as NOTES.md:51 says.

| r2 row | fixed? | evidence |
|---|---|---|
| F1 (the watchdog could not be cancelled, about 60 s of silence) | **Yes** | The watchdog subshell is gone (template:105, "No watchdog process"). The handler now sends TERM to the group (:113), polls a live non-zombie member every 0.5 s and resends TERM each time, up to 120 polls (:106, :114-115). It sends KILL only if the group is still alive after that (:116), then waits and reports the seconds (:117-118). In neg-int-r2 the script ended 1 s after the TERM ("stopped, 0 s after the signal"), the store link was on store-a 20 s later and the group was gone. rehearse_rel.sh:260 now fails the rehearsal unless STOP comes within 30 s. In the hand-signal log, the "dies" case ended in 1.03 s wall. |
| F5 (a signal between the fork and `rp=$!`) | **Yes** | RP_STARTING is cleared at :61, set just before the fork at :239 and cleared at :251. At :111 the handler takes `$!` when `rp` is still empty. :114-115 cover a signal that lands before the child's setsid, because TERM is resent at each poll. Nothing earlier in the script starts a background job, so `$!` cannot be stale (hand-signal: "before any background job: ${!:-} = []"). The hand-signal "early" case stopped the group in 0 s. |
| F7 (FIX-3 ignored pytest errors; fails open) | **Yes** | rel_checks.sh:290-295 now stops part B unless each pin's run ends with passes and no error, the same test FIX-4 (:247) and g14 (:270) use. hand-checks-dry ran blocks cut from rel_checks.sh as it stands (sha b6418de1ccf4, the same bytes as BUNDLE). An error under the new pin and an error under the old pin each gave CHECK FAILED. The positive and the earlier four negatives behaved as before. I read checks_dry.sh: it cuts lines 243-257 and 290-320 by their marker lines, leaving out only the pytest call at :245. Skipped cases depend only on files existing (test_guard_fix_3.py:520), not on the pin, so a skip cannot hide a difference between the pins. |
| NOTES F2 (provenance wording) | **Yes** | NOTES.md:16 now reads "9 of these 10 … 12 of its 13 lines". NOTES.md:44-53 names the 17:25 changes to fill_release.sh and README.md, and the post-r2 changes to the template, rel_checks.sh, rehearse_rel.sh and README. The file times agree: template 17:39:17, rel_checks 17:39:28, rehearse_rel and README 17:39:45, fill_release 17:25:32, rel_registry 14:14:24. The claim at NOTES.md:51 is confirmed by the diff above. There is one new count slip; see N3. |
| F3 (hand checks had no kept log) | **Yes** | All five checks r2 listed now have a log under log/: hand-f6-refusal, hand-fill-positive (18 OK), hand-changed-byte, hand-unreadable and hand-checks-dry. hand-signal was added. Each log names the bytes it tested: BUNDLE d58ae15b48ad, rel_checks b6418de1ccf4 or template fc587c627717. Each was written after the last edit to the file it tests. neg-int-r2 started at 17:39:54, after the template (17:39:17) and rehearse_rel.sh (17:39:45). There is a residual; see N8. |

## Q2: did the fold add anything that fails open?

No.
- **Checks.** The new FIX-3 check only adds a refusal. The handler only adds stopping. Every path that leads to a STOP still runs `restore_store` first. :120 sets PREV from PREV_CUR when the refresh has already flipped the link.
- **Swallowed errors.** The handler's `set +e` and its ignored signals are confined to stopping the refresh, putting the link back and exiting.
- **Group check.** If `ps` fails, `grp_alive` reads the group as dead. The handler then waits on the refresh and puts the link back, so it fails closed.
- **Hash lists.** BUNDLE.sha256 lists all 7 shipped files. The only other files in the folder are review.md and review-r2.md, which are records, not shipped files. fill_release.sh is unchanged since r2, and the fold's new code runs no new file. N4 is older than the fold.
- **Slots.** The template still has exactly four slots (:32-35). The template refuses itself at :38 if one is left. fill_release.sh refuses at :43 if a slot remains after the fill.

## Q3: does `sha256sum -c BUNDLE.sha256` pass?

Yes. All 7 files print OK with exit 0, and `--strict` also passes. BUNDLE.sha256 hashes to d58ae15b48ad155c25a7e5f64faeac9106ada9a953e43901f6cd8c942adedecd.

## Q4: do they still refuse before any write?

Yes.
- **Template:**
  - An unfilled slot is refused at :38 and a C that is not a commit at :39. Both come before the move-aside at :63 and the mkdir at :64.
  - A wrong C, RECORD, SHA or EPOCH is refused in part R (:170, :178, :188-192, :193). This comes after writes in /tmp only and before part A builds or installs anything (:214-218).
- **fill_release.sh:**
  - The BUNDLE check comes first (:13). A missing C is refused at :14 and a wrong C at :19 and :23.
  - All of these come before mktemp at :26 and the `.tmp` writes at :42.
- **rel_checks.sh:** missing arguments are refused at :15-18, before the mkdir at :22. A wrong store commit fails at :136, after writes only to its scratch folder.
- **rehearse_rel.sh:**
  - An unknown mode or an existing folder is refused at :45-46, before any write.
  - A failing hash list stops it before the filled script runs (:182-184). The one exception is neg-sha, by design.
  - A refused fill stops it under `set -e` (:100).

## Findings

| id | file:line | what | consequence | scope | ordinary work | fails open |
|---|---|---|---|---|---|---|
| N1 | README.md:59; template:15, :118 | The text promises STOP "within seconds (60 s at most)". With a refresh that ignores TERM, it took 69.86 s wall, and the message still said "60 s" (hand-signal "ignores"). The extra time is the 120 `ps` polls. | other (wording) | in | yes | no |
| N2 | README.md:59-61; template:12-13 | "Closing the terminal is safe": the script still stops or rolls back. But `tee -ai` ignores only INT. On a hang-up, tee dies, so the log does not record the STOP or ROLLED BACK line the operator is told to report. HUP is not rehearsed. | other (evidence) | in | yes | no |
| N3 | NOTES.md:76 | "these 14 files": the files that are in the 18-file list but not in BUNDLE.sha256 number 15 (the smoke test, 9 tools and 5 files), or 16 counting the filled script. | other (wording) | in | yes | no |
| N4 | fill_release.sh:51-55; tools/rebuild_slot.sh:30 | Part S's rebuild runs tools/rebuild_semantic_check.py, which turns "ok with the semantic store not recreated" into a failure (exit 75). That file is not in the 18-file list, so an edit between fill and run would get past the operator's check. rel_checks section 4 (embed_headers true, the semantic facet available) is the backstop. This predates the fold. | fails open (narrow, with a backstop) | out (not from the fold) | no | yes |
| N5 | README.md:5, :42, :66 | The README's `{C}` slots appear only in prose, and nothing fills them: fill_release.sh writes only the script and the hash list. The operator's command line (:56) and the rollback line (:76) contain no slot, so nothing runs with an unfilled value. | other | out | yes | no |
| N6 | template:108, :91 | The handler ignores INT, TERM, HUP and PIPE. A reranker restarted by a rollback inside the handler inherits those settings, so it would ignore TERM, and `proc.sh stop` would have to escalate. Before the fold this held for TERM; the fold adds HUP. | other | out | no | no |
| N7 | (process) | This audit ran as a subagent sharing the builder's session scratchpad (session 6ff2ee7c…). The context was fresh and it wrote none of the audited files. Recorded for the MR-4 trail. | other | out | yes | no |
| N8 | log/repin-rel-hand-*.txt | The harnesses that produced the hand logs (checks_dry.sh, sig_harness.sh, hand_fill.sh) and their inputs live in the session scratchpad under /tmp. The logs are kept, but the checks cannot be re-run after a reboot. | other (evidence) | in | yes | no |

**Two lines per finding, and what would reverse it:**
- **N1.**
  - Ordinary work: yes, because a Ctrl-C while the refresh is running is ordinary.
  - Consequence: other.
  - Reversed by: a run where a refresh that ignores TERM ends in 60 s wall or less, or wording that says "about 70 s".
- **N2.**
  - Ordinary work: yes, because closing a terminal is ordinary.
  - Consequence: other.
  - Reversed by: a HUP rehearsal whose log shows the STOP line.
- **N3.**
  - Ordinary work: yes.
  - Consequence: other.
  - Reversed by: a count of the files in the list that are not in BUNDLE coming to 14.
- **N4.**
  - Ordinary work: no, because it needs an edit to that tool between the fill and the run while the CTO's hold is on; the file last changed on Nov 1.
  - Consequence: fails open, with section 4 as the backstop.
  - Reversed by: showing that rebuild_slot.sh does not run that file in part S, or the file appearing in the list.
- **N5.**
  - Ordinary work: yes.
  - Consequence: other.
  - Reversed by: a step that fills the README.
- **N6.**
  - Ordinary work: no, because it needs a signal after the switch, when the reranker was restarted.
  - Consequence: other.
  - Reversed by: the service installing its own TERM handler.
- **N7.**
  - Ordinary work: yes.
  - Consequence: other.
  - Reversed by: evidence that this was a separate session.
- **N8.**
  - Ordinary work: yes, because a reboot is ordinary.
  - Consequence: other.
  - Reversed by: the harnesses copied under log/ or drafts/.

## What I probed and found sound
- The fold changed only the trap in the template; the operator's path through parts 0 to E is unchanged since run f7.
- The new handler cannot leave a half-switched link. Every link change is still a temporary link followed by `mv -T`.
- A signal after `rp` is cleared, or after the refresh has finished, is harmless: the kill finds no process, and the link goes back if the refresh flipped it.
- The F7 check catches a pytest error whether the summary says "error" or "errors", and with a warnings count in the line. An interrupted collection has no " passed" and also fails.
- `ps -g` with a number selects by session in procps-ng 4.0.4. The refresh is its own session's leader through setsid.
- rehearse_rel.sh's new 30 s limit in neg-int is read from a value that defaults to 0 if bc prints nothing; bc is present, since the template itself uses it.

```verdict
{"kpis": [
 {"kpi": "Q1 folded findings fixed", "verdict": "pass", "findings": [{"id": "N1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "N3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "N8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "Q2 nothing new fails open", "verdict": "pass", "findings": [{"id": "N2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "N4", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}, {"id": "N5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "N6", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "N7", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "Q3 sha256sum -c BUNDLE.sha256 passes", "verdict": "pass", "findings": []},
 {"kpi": "Q4 refusal before any write", "verdict": "pass", "findings": []}
]}
```

```verdict
verdict: PASS
reviewed_bundle_sha256: d58ae15b48ad155c25a7e5f64faeac9106ada9a953e43901f6cd8c942adedecd
blocking: 0
```
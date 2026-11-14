# The re-pin from release 0.1.0: the preparer's notes (2026-11-14; DEC-1178 (3), P-RELEASE-1 §6)

For the CTO and the reviewer. The operator's page is `README.md` beside this file. Modelled on window 5's bundle
(`pin/REPIN-COMMANDS-W5.sh`, `repin7_checks.sh`, `repin7_registry.py`, `rehearse_repin7.sh`, its review
`reviews/ACT-REPIN-W5-review.md` READY, and the `log/repin-w5-rehearsal-*` logs).

## 1. The files
| file | what | from |
|---|---|---|
| `REPIN-COMMANDS-REL.template.sh` | the operator's script with four slots: `C`, `EPOCH`, `SHA` (the record's wheel sha256), `RECORD` (manifest.json's sha256); VERSION `0.1.0`, TAG `v0.1.0`, OLD `797495bdfc70` fixed | window 5's script, plus part R; built-from-C check now against the record's sha256; §5's two lines and P-2's line after the switch; the registry commit cites DEC-1178 |
| `fill_release.sh` | the CTO's step at "released": `bash fill_release.sh <C>` reads the tag and the record, refuses unless they agree with C, writes `REPIN-COMMANDS-REL-0.1.0.sh` and the hash list `REPIN-REL-0.1.0.sha256` (13 files, absolute paths) | new (RL-1: nothing copied by hand) |
| `rel_checks.sh` | part B's checks | `repin7_checks.sh` unchanged but: the old pin `797495bdfc70`; section 3d (the builds since window 5: `gov adapters`, `wait`, `dispatch`, `impact`, `session-watch`, `skilleval`, `release` answer `--help`; `gov.release` build/verify and `gov.wait.liveness` import) |
| `rel_registry.py` | part E's registry edit | `repin7_registry.py`: replaces window 5's entry (`797495bdfc70`, `04b094fb…7c3`); six arguments (adds version, tag, record sha256); the note names the release and the record; `approved_by: DEC-1178` (see 4, R-1) |
| `rehearse_rel.sh` | the rehearsal: the scratch mirror plus a scratch release in a scratch clone | `rehearse_repin7.sh` plus the scratch release, fill and three new negative modes |
| `README.md` | the operator's page (draft) | `ACT-REPIN-W5.md`'s form |
| `pin/smoke_repin5.sh` and the 9 CTO tools | used unchanged, by path | window 5's |

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

## 3. The rehearsal (stand-in C = `w2/integrate` head `494d5c9335fa` at 14:16)
REHEARSAL-OUTCOMES

## 4. Open points for the review and the owner
- **R-1, `approved_by` in the registry entry.** Every window's gov entry so far cites DEC-1037 (the re-pin windows).
  This one cites DEC-1178 (the owner's decision of the release and the re-pin from it). Within the CTO's purpose; the
  reviewer may ask for DEC-1037 kept. No owner question.
- **R-2, the registry commit's trailers:** `Task: decision-record`, `Implements: DEC-1178`, `Role: owner`, as window 5's
  (`Implements: DEC-1125`). The record commit of §4 step 5 takes `Task: DAEO-sdxk` (P-RELEASE-1's proposal); this commit
  changes a governance record (the tool registry), so `decision-record` is window 5's form.
- **R-3, the restart of the reranker** stays unrehearsed (the live service is never restarted in a rehearsal), as in
  windows 4 and 5.
- **R-4, the epoch:** the release's own build (`gov.release._wheel`, setuptools' `build_wheel` on `git archive C
  pyproject.toml src`) and the re-pin's (`pip wheel --no-build-isolation` on `git archive C`) gave the same bytes in the
  rehearsal (part A against the scratch record). This is P-RELEASE-1 §5's claim, now shown on one commit; the rehearsal
  at the real C shows it again.

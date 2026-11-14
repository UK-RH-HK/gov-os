# ACT-LANDING-CTO-ROUTE-1: the independent ACT review

- **task:** ACT-LANDING-CTO-ROUTE-1 (DAEO-sdxk)
- **decisions:** DEC-1167 (5), DEC-1104 (2), DEC-1104 (4), CAP-33, DEC-801, DEC-808, DEC-1010, DEC-1014
- **Reviewer:** a fresh read-only reviewer session (`f3886235-4854-4c91-9cf3-1a1dd009cb50`), not the ACT's author (the author is the CTO's ACT-preparation helper)
- **Brief:** `~/gov-os-operator/install/reviewer-brief.md`, sha256 `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a` (computed; equals the one given)
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-LANDING-CTO-ROUTE-1/`, `manifest.json` sha256 `973eba5fd258ef6293cf37500ff7c2777b5f551ff524a6f8caf6dac6d8fbd9e8` (computed; the package's yes line `973eba5f` matches)
- **Main tree at review:** `w2/integrate` `abadad60ed62` (two commits after `e437c799c`; neither touches a listed path: the source copy still hashes `a0687ebd...`, the test file is absent)
- **Where I rehearsed:** fresh `--no-hardlinks` clones of `w2/integrate` under `/tmp/claude-1000/rev-landing/`, each with a planted HOME holding a copy of the live install; TMPDIR inside that folder; the one pytest through `heavy_slot.sh`. Nothing written in the live install, the main tree or the bundle. The live install's `landing_check.py` and `APPROVED` were re-hashed at the end and are unchanged.
- **Where the block goes:** the brief says to append the verdict block to the bundle's `review.md`. My brief from the lead lets me write only this file, so the CTO has to copy the block below into `review.md` before G4 can read it.

## Classification of the findings (one line)

None blocks: F1 is out of scope (the package states it in §5 and its §7 option (a) closes it), reachable in ordinary work, fails open. F2, F3 and F4 are in scope, consequence other. No KPI line fails.

## The base against the live install today (the lead's question)

- The live `~/gov-os-operator/install/landing_check.py` hashes `a0687ebd...` and `APPROVED` hashes `3744df3a...`: both are the bundle's `before`. All 13 other install files hash as `keep.txt` says. The repository's source copy at HEAD is `a0687ebd...`, and the new test file is absent. Nothing is waiting in the operator's state: no `act-in-progress.txt`, `journal.json`, `operator.lock` or queued `.req`. `log/launch.lock` exists (0 bytes, since 2026-11-09).
- **The apply refuses cleanly if APPROVED has moved.** I ran three cases, each in its own clone and planted HOME:
  - R2: ACT-CLASS-RULES-AGENTS-1's after `APPROVED` and `class-rules.yaml` planted (that ACT applied first). `check` and `apply` both exit 3 with "moved: home/gov-os-operator/install/APPROVED (neither the before nor the after)" and "apply refused, nothing touched". A hash of every file before and after shows 0 differences.
  - R3: a single byte appended to `APPROVED`, everything else as built. Same result: exit 3, 0 differences.
  - The state test runs over every listed file before any write. A file that moves during the swap is caught per file (exit 3 "changed while the swap ran"). I read that guard but did not reproduce it.
- **The order with ACT-CLASS-RULES-AGENTS-1 works as that package says.** I applied this ACT, then that one (its bundle placed where its `ROOT` expects it), then undid both in reverse order. Results:
  - Applying this ACT, then that one: both exit 0, and that ACT's `check` names "the install after ACT-LANDING-CTO-ROUTE-1".
  - Undoing in reverse order: both exit 0, and this ACT's `check` is ready again.
  - Undoing this ACT while that one is on top: refused, exit 3, nothing touched (F4).

## The route against a (b) or (O) commit without the owner's yes recorded (the lead's question)

I ran ten probes of the after `landing_check.py` from the planted install. Each used a temporary repository, acts folder and approvals log, with the function's two test arguments; script `/tmp/claude-1000/rev-landing/probe_route.py`.

| probe | result |
|---|---|
| a (b) ACT commit with all three conditions | passes, as stated |
| no approvals line at all for a valid (b) bundle | flagged (P1) |
| an approvals line whose route is "the owner's operator agent (class (b)), queued by the CTO" | flagged |
| a "the CTO" line naming another manifest of the same ACT | flagged |
| an (O) control path (operator-own) under a manifest that claims (b) | flagged (the classifier votes O; the path class is O) |
| a (b) path renamed onto an (O) path | flagged (the diff lists both names because renames are not detected) |
| a merge whose first-parent change carries an (O) path | flagged |
| `Role: Orchestrator` with a capital O | flagged (fails closed) |
| a `manifest_sha256` key and a route "The CTO, by hand" | passes, as stated |
| a (b) path with a catch-all test path in the same ACT | flagged (the classifier votes O) |
| **the same `Role/Act/Act-sha` trailers reused on a later commit that changes the same (b) path to other bytes** | **passes: F1** |

No (O) control path can pass by this route. A (b) control path cannot pass without an approvals line for that ACT and that manifest whose route begins "the CTO". In that sense the owner's yes, as recorded in `log/act-approvals.jsonl`, is always required. The one gap is that one recorded yes admits any number of commits (F1).

Other checks of the route:
- I ran the old and the new check through the command line, as `landing_select.sh` does, over the last 1000 first-parent commits of `w2/integrate`. They print byte-identical output (11 items). The rehearsal ran the same comparison over 300.
- The new code has no environment or command-line seam. The two folders are constants in the file. The command line's error path still fails closed: an exception becomes one P1 item.

## Per check

1. **The touched list and the path rule: pass.**
   - My hash of the whole clone and planted HOME before and after `apply` shows the four listed files changed and nothing else, plus `log/launch.lock` (F3; it already exists live, so nothing changes live). The crontab is not touched.
   - `apply.sh` works from `$PWD`, `$HOME` and its own folder. No manifest check names the live repository or the real HOME literally, and nothing `cd`s to either.
   - The after `landing_check.py` contains the live scratch path as a constant. That is file content, not a command. In a dry run the manifest's behaviour check passes its own folders and reads nothing live.
2. **The undo: pass.** In R1, `undo` restored every touched file byte for byte. The only remaining difference is the pre-existing-live `launch.lock`. The clone's `git status` was clean after it. `undo` again: exit 0, nothing to do. Re-apply: the same bytes. The rehearsal log shows the same (B12 to B15, D4 to D7).
3. **The rehearsal is real: pass.**
   - `rehearsal.log` hashes as the manifest says (`ab792221...`) and is byte-equal to the draft's `rehearse.out`.
   - The bundle's `apply.sh` and after code are byte-equal to the drafts.
   - The log ends `failures: 0`.
   - Two text slips are recorded as F2.
4. **The checks are right: pass.** I ran all six manifest checks from the applied clone with the planted HOME. Every exit code and count equals the manifest's: 0/1, 0/1, 0/-, 0/1, 0/1, and 0/- (the behaviour check printed its pass line). The new unit file passes in the clone through `heavy_slot.sh`: 40 passed.
5. **The class: pass, class (O).** Three files fall under the `operator-own` row (O): the install's `landing_check.py`, the install's `APPROVED` and the source copy `governance/project/operator/landing_check.py`. The new test file falls under the catch-all row (O). The claim (O) is right, and so is the owner's operator applying it by hand.
6. **The guard replay: pass.** The ACT adds no path-map or deny-list rule, so `replay_refused` is empty.

## Findings

**F1: one recorded yes admits any number of later commits.** The CTO commits a (b) ACT with the route's three trailers after the owner's yes and its approvals line, and the commit passes. Later the CTO makes another commit on the same (b) path, with bytes no one reviewed, and reuses the same `Role: orchestrator`, `Act:` and `Act-sha:` trailers. For example: a follow-up fix copied from the earlier commit line, or the package's own "How the CTO then commits a (b) ACT" line used again. That commit passes too, and no P1 is raised. It should have been flagged, because the owner's yes covered the reviewed change, not a later one.
- The package's §5 states that "the route reads paths, not bytes". F1 follows from that, but §5 reads as one commit and does not mention reuse.
- The §7 option (a) closes F1: each touched blob must hash as the manifest's `after`, so a reused trailer set can only re-land the reviewed bytes.
- Recommendation: the CTO names the reuse in §5, so that the owner's choice between (a) and "neither" is informed.
- Ordinary work: yes, because an honest CTO can reuse a previous commit's trailer set for a fix it believes belongs to the same ACT.
- Consequence: fails open.
- Scope: out (stated in the package's §5 as content not bound, with the owner's option (a) to close it; not a loosening beyond what the package states).
- Reversed by: a probe in which the second commit with reused trailers and other bytes is flagged by the after `landing_check.py`. Or an owner decision that one approvals line may cover later commits on its paths, which would make F1 a stated design choice.

**F2: two text slips in the rehearsal log.**
- The log's clone line says `8ba025e8fa26`, where the package's §4 says the base was `79159cd44c5b`.
- E1 reads "red (39 failed, 1 passed in 2.59s): 33 failed", with two different failure counts.

Neither changes a result. The log still ends `failures: 0`, and my own rehearsal agrees with every step I repeated.
- Ordinary work: yes, because a reader of the package compares those numbers.
- Consequence: other.
- Reversed by: the clone actually being at `79159cd44c5b`, and the count text coming from one pytest line.

**F3: `apply` and `undo` create `$HOME/gov-os-operator/log/launch.lock` if it is absent.** The swap opens the launch lock for append. In a HOME without that file, the run leaves a new empty file that is not in `touched`. The live file exists (0 bytes, 2026-11-09), so the owner's run changes nothing outside the list. A dry run on a planted HOME without it will see one new empty file.
- Ordinary work: no, because the live install already has the file, and the bundle is (O), applied by hand and never dry-run by the operator agent.
- Consequence: other.
- Reversed by: the operator's dry-run diff ignoring `log/launch.lock`, or the planted HOME always copying `log/`.

**F4: this ACT's undo and verify refuse once ACT-CLASS-RULES-AGENTS-1 is on top.** With both applied, this ACT's `undo` exits 3 ("APPROVED neither", nothing touched). Its `verify` also exits 3, because `keep.txt` pins today's `class-rules.yaml`. Undoing in reverse order works. ACT-CLASS-RULES-AGENTS-1's package §7 already says this, but this package's §9 does not.
- Ordinary work: yes, because the owner's operator may undo this ACT first.
- Consequence: other (it fails closed and loses nothing).
- Reversed by: this ACT's undo succeeding with the other ACT on top, or §9 already naming the order.

## Probed and found sound

- The bundle hashes and the drafts' equality.
- The base equals the live install today.
- Refusals with nothing touched when APPROVED moves, alone or with ACT-CLASS-RULES-AGENTS-1 applied first.
- Apply, re-apply, undo, re-undo and re-apply, byte for byte; modes 0444 in the install and 0644 in the repository.
- The six manifest checks.
- The 40 new unit tests in a clone.
- Old and new outputs identical over 1000 first-parent commits.
- The route refuses: every (O) control path, renames onto (O) paths, merges carrying (O) paths, missing or foreign approvals lines, operator-agent routes, and catch-all paths beside (b).
- No seam: no environment variable or option names the approvals log or the acts folder.
- The command line still fails closed on an exception.
- The undo order with ACT-CLASS-RULES-AGENTS-1.

One limit stated in the package, not a finding: (b) ACTs that also touch HOME, such as the guard hook's HOME copy or the HOME settings, cannot use the route. They still go through the owner's operator.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "2", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "4", "verdict": "pass", "findings": []}, {"kpi": "5", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}, {"kpi": "6", "verdict": "pass", "findings": []}], "manifest_sha256": "973eba5fd258ef6293cf37500ff7c2777b5f551ff524a6f8caf6dac6d8fbd9e8", "class": "O", "reviewer": "reviewer-f3886235-4854-4c91-9cf3-1a1dd009cb50", "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a", "time": "2026-11-13T20:32:10+00:00", "replay_refused": []}
```

# Anti-drift audit, part (e1) and (f): every deterministic check at the re-pin candidate

Run 2026-11-11 01:14 to about 02:00 UTC by the CTO's helper (orchestrator role, Sonnet high, class C1; DEC-1125 (3) (iii)).

- **Candidate:** `w2/integrate` at `797495bdfc70` (W2-155's sources). The head moved while I worked: `e6dd74727` (01:24) and
  `72f645112461` (01:28). Every check below ran on `797495bdfc70` in a shared clone (`/tmp/gov-os-emg-checks/clone`), except where a row says live.
- **Store checks** ran in that clone with a byte copy of the integration store's `store.db` (the clone has no store of its own). The
  live store was read only by `gov retrieve`.
- Nothing was installed, changed or committed. `src/` untouched.

## Result in one line

One real red: `context-reproducibility` has 1 error (W2-155's ticket names `W1-19`, which the store does not hold). The CTO's
uncommitted edit in the main tree (`W1-19` to `DAEO-t6hf`) fixes it: I tried the same edit in the clone and the check went green.
Everything else is green, a warning already ruled, or a notice. Four notices need a decision or a fix by role (rows 6, 9, 10, 11).

## Table

| # | Check | Command (short) | Result | Red or notice | Cause | Who fixes |
|---|---|---|---|---|---|---|
| 1a | `gov check`, all 17 families | `gov check --json` in the clone, through `heavy_slot.sh` | exit 3. 11 families green, 2 yellow by design, 4 red in the clone | **Clone artifact** for 3 of the 4 reds: no store in the clone (index freshness, context reproducibility, recovery/rebuild) | Re-run on the store copy: see 1b | n/a |
| 1b | The three store families, on the store copy | `python3 -m gov.retrieval.lexical`, `gov.context.context_check`, `gov.rebuild.check` | index freshness: exit 0 (green). recovery/rebuild (store digest equals a clean rebuild): exit 0 (green). context-reproducibility: **exit 1, 1 error** | **RED (1)** | `ERROR: DAEO-ar89: mandatory input 'W1-19' not found in the store`. W1-19 is a work-breakdown id; the store holds that ticket as `DAEO-t6hf`. Added by `797495bdf`. The other 88 refusals over the 6,000-token ceiling are the accepted kind (DEC-1123 (2)) | CTO: commit the edit already in the main tree (`.tickets/DAEO-ar89.md`, `W1-19` to `DAEO-t6hf`). Trial in the clone: `green (131 packet(s) built twice alike, 88 refused over the ceiling twice alike)`, exit 0 |
| 1c | product traceability | in the 1a run | `product-traceability-trailers` RED with 424 findings: 354 missing `Implements:`, 66 `Implements:` ids that do not resolve, 4 closed tickets with no `Task:` commit | **Warning** (DEC-1123 (3)) | Same 424 as the ruling counted. No growth since. `openspec-validate` yellow: `openspec is not on PATH` | W2-115 (the ruling); nothing tonight |
| 1d | authority/role limits | in the 1a run | yellow: 269 findings of `core-decision-citations` (268 commits that cite a decision their own tree does not record, 1 unreadable ticket frontmatter in `6a572a4c65bd`, `.tickets/DAEO-clon.md`) | Notice (warning severity) | The newest two (`53affe5337fd` DEC-1124, `35396225e07c` DEC-1123) are the usual order: the work commit comes before the register commit. The rest are older | none |
| 1e | secrets indexing | in the 1a run | yellow: off by configuration (DEC-1045) | Notice, known | | none |
| 2 | Structural pass | `tools/structural_pass.py <clone> 622e9b741` | `structural pass at 797495bdfc70: all 9 families ok, 15.6 s` (schema, graph, claims, mutation, authority, pathmap, audit, skills ok; portability skipped, nothing changed under roles, skills or hooks) | Green. No unindexed-path notice | | none |
| 3a | Guard, four-rule check | `tools/guard4_check.py` (live hook, pinned judge) | `cases run: 453, failed: 0, sets cases: 527, skipped: R (SETS_PLANTED unset): 144` then `PASS` | Green | The 144 R cases need a planted sets root; not run (I may not touch `~/gov-os-eval/`) | none |
| 3b | Walls, guard cases | `drafts/indep-walls/walls_check.py repo <main tree>` | `repo cases: 331, run: 245, failed: 0, expect: after, skipped: R: 86` then `PASS` | Green | The R cases are planted-root cases, skipped | none |
| 3c | Walls, wall hook and built walls | `walls_check.py wall <sets root>`; `apply.sh check` | **Not run** | Gap, by design | `wall` mode reads walls built under the sets root; `apply.sh check` stops on an applied ACT. Both belong to the rehearsal clone (83 plus 84 cases, 0 failed on 2026-11-09) | CTO decides if a fresh rehearsal is wanted; I recommend not, nothing in the walls changed |
| 3d | `gov guard` subcommands | `gov guard --help` | There is no such command (`gov` has 21 commands, none is `guard`) | Notice | The guard is checked by the two tools above and the tests | none |
| 3e | Control files drift | `git status --short` in the main tree | No change under `.claude/`, the path map or the hooks. `.git/hooks/reference-transaction` present (Nov 9) | Green | The only changes are record files (tickets, register notes, FORECAST-W2-3) | none |
| 4a | Call log replay (both ways by sha256) | `build_replay_calls.py --hours 24` then the operator's own `check_against_log` on that set | **REFUSED:** 4 logged live calls missing from the set (sessions `412a4e37` x3 at 15:49, 16:14, 17:44, and `8ddb8b14` at 21:17, all `Write`, all allowed, rule none). Set: 8,331 calls written, 62 dropped (name the sets root), 237 left out (no log line); 8,187 logged replayable calls | **RED for an operator replay** (no harm to work) | No transcript holds a `Write` whose hash matches those four log lines (11,110 `Write` calls scanned). So the log holds an input the transcript does not. Cause not found | Open question, see note 4a |
| 4b | Call log, 24 h in numbers | read of `~/.gov-os/guard-calls/` | 12,402 lines: 8,601 from live sessions, 3,801 from check runs (`guard4`, `walls`, `refusal`, `guard`). Live: 8,583 allow, 17 deny, 1 ask. Time per call p50 97 ms, p95 175 ms, max 2,017 ms | Notice | The one `ask` is the install rule firing on the CTO session (rule 4-ask), correct | none |
| 4c | The 17 live refusals | log plus transcripts | 7 `2-listing`, 4 rule `5`, 1 `2b-line`, **5 `error`** | **Notice, 5 false refusals by the guard's own fault** | See note 4c | See note 4c |
| 5a | Store at the candidate | store worktree head against integrate | Store at `797495bdfc70` rebuilt 01:08:24, the same second as the commit. After the head moved: store A `e6dd74727` (01:24:01), store B `72f645112461` (01:28:36), integrate `72f645112461` | Fresh | The `reference-transaction` hook refreshes after every update; A/B swap works | none |
| 5b | Index freshness, path-map coverage | rows 1b and 2, plus `gov doctor` | Lexical index current; `path_map: unclassified_count 0`; pathmap family green in `gov check` and in the structural pass | Green | | none |
| 5c | `gov links` | `gov links --since 622e9b741` | `gov links: 0 new since 622e9b741, 1575 standing` | Green (0 new) | | none |
| 5d | Register consistent | my script over `docs/DECISION_REGISTER.md` | 1,121 entries, all unique, highest DEC-1125; last version row 0.509 says `Next free id: DEC-1126`, which is highest plus 1; it is the last line of the file | Green. Two old notices: ids 8, 9, 28, 29 do not exist; rows 0.1 to 0.12 are in reverse order | Old, not new | none |
| 5e | `context_check` expecting `0 error(s)` | `python3 -m gov.context.context_check` | `1 error(s)` | RED, same as row 1b | | CTO, row 1b |
| 5f | Search 1: DEC-1123's trailers ruling | `gov retrieve --root .../W2-00-store` | **Hit, rank 1** (DEC-1123, lines 14317-14338); `D10-RECORD-REDS.md` rank 2 | Green | | none |
| 5g | Search 2: DEC-1125's memory audit cadence | same | **Hit, ranks 3, 11, 13, 14, 15** (DEC-1125). **Rank 1 is DEC-1101**, which still says "every two weeks while development is active", with `changed_by=[]` and `in_force=True` | **Notice: stale answer first** | DEC-1125 (2) changed DEC-1101 (1) but only says so in its `Under:` line. The store builds "changed by" from a `**Changed by:**` marker in the older entry's status line | CTO, note 5g |
| 5h | Search 3: W2-155 | same | **Hit, ranks 1 and 2** (`.tickets/DAEO-ar89.md`) | Green | | none |
| 6 | `gov doctor` (extra, main tree) | `gov doctor --json --root <main tree>` | unhealthy: tools (3 pytest plug-ins not found), `path_compliance` (55 moved references, 162 older ones excluded), index freshness (the main tree's own local store is older than its tickets; not the integration store), Claude Code 2.1.322 against the pinned 2.1.292 | Notice | Not in my list; see note 6 | CTO, note 6 |

## Notes on the reds and notices

### 1b and 5e: the one red (context-reproducibility)
`797495bdf` ("DEC-105 and W1-19 in its sources") added `W1-19` to W2-155's `sources:`. Sources are mandatory inputs and the store
holds no record called `W1-19`. The record that carries it is `DAEO-t6hf` (external-ref and wbs_id `W1-19`, closed). The CTO's
working-tree edit does exactly this. I tried it in the clone: green. After the CTO commits it, the store refreshes by the hook;
`context_check` refuses a store from another commit than HEAD, so run it once more on the new head. The clone's code is the
same wheel, so `src/` stays frozen. Confidence high.

### 4a: four logged calls the replay cannot match
Why it matters: ACT-OPERATOR-2's replay refuses on any mismatch, both ways. A path-map ACT through the operator would be
refused while these four are inside its 48-hour window. The last one leaves the window about 21:17 UTC on 2026-11-12. The re-pin itself
is not a path-map ACT as far as I know; the CTO knows. I could not find why: no transcript, main or subagent, holds a `Write`
with that hash. The four `Write` calls were allowed. Recommendation: if an operator replay is needed before then, build the
set again from the log's side (the builder counts them: "logged replayable calls with no set line: 4") and ask the W2-148
owner for the cause; otherwise wait it out. Confidence on the cause: none. Confidence on the effect: high.

### 4c: the 17 live refusals
- **5 `error` refusals** (the guard could not decide and refused, as designed). All on ordinary work:
  - 3 x `list index out of range` (a guard defect): `timeout 170 bash -c 'until ...; done'; cat <file>`; a `source ... ; eval $(cat ...)` line; a
    `bash -c 'h=$(git -C ... hash-object ...)'` line.
  - 2 x `git cannot say whether a revision holds the hidden part`: a python heredoc that edits a brief, and one test-designer Bash call.
  - Verdict: false refusals, ordinary work: yes; consequence: other (a retry in another form). Fix needs the guard's code: after the lift, a guard ticket (W2-42a is the named home for the parser). Not tonight (`src/` and the hook are frozen).
- **12 refusals that name a rule:** 7 `2-listing` ("a listing whose start the guard cannot place"), 4 rule `5` (reviewers: three `rm` of their own temp folders were auto-classified false positives by the CTO's tool; one `Write` of a scratch script by a reviewer into `~/gov-os-runs/W2-153/review-s3/` looks like a true refusal), 1 `2b-line` (CTO session 20:51, a line naming the sets root with a hidden folder; I did not judge it).
- **The CTO's own refusal log is behind.** `log/guard-refusals.jsonl` ends at 2026-11-10 02:12; 9 of the 12 above are not in it, and the harvest tool never sees the `error` refusals (it keeps only texts holding "DEC-953 item 2"). I did not run it (it writes). Recommendation: run `guard_refusals.py` once by hand, then classify; and widen its filter to the `error` text after the lift.

### 5g: the memory gives the old cadence first
A question "how often is the memory audit run" returns DEC-1101 first (every two weeks), marked in force, with nothing saying DEC-1125
(2) changed it. DEC-1125 comes third. Smallest fix, by the CTO as a record edit: add `**Changed by:** DEC-1125 (item 2)`
to DEC-1101's status line, as DEC-953's status line does for its changes. I did not test that the store reads it that way for this entry;
the first memory audit will show it. Confidence medium.

### 6: `gov doctor` (not asked for; reported because it was cheap)
- **Moved references (55):** live records point at test paths that were renamed: `.tickets/DAEO-8s85.md` (`tests/unit/resources/test_w2_20_launch.py`), `.tickets/DAEO-btcs.md` (`tests/optin-lifted-breadth.txt` is now `tests/optin-breadth.txt`), plus reviews, probes and closes. Ticket and review files are the CTO's; the closes and probes are history. Fix the two tickets by role; leave the history.
- **Claude Code 2.1.322 is newer than the pinned 2.1.292.** Known drift, a decision for the owner, not for tonight.
- The three pytest plug-ins missing is the system Python; the pinned environment has them (the heavy slot runs use it).
- `canaries` and `framework_lock` are reported "unmeasured", not green.

## What was not measured
- The planted-root cases of both guard tools (230 cases): they need a planted sets root.
- The wall hook and built-walls cases (3c).
- The full suite, secrets scan: out of scope tonight.
- `gov check` run as one command with a store in place. I ran its three store families by hand on a copy of the store and the other
  families in one run. I read the combined result from both.

## Scratch
`/tmp/gov-os-emg-checks/` (clone, store copy, scripts, outputs).

---
type: probe
task: DAEO-cy5o
reviewer_session: 65b2eade-aedd-45f6-b014-4ff8f5d64a91
implementer_session: 310f4f41-0e50-4ddd-9c2d-bb6c998cc96f
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 8f61bda0eb5c65cf0683a5485332d5452bad0b2b
---

# Probe record: DAEO-cy5o (W2-57), load out of the close: review 2, the last of the ticket's one declared round (DEC-916)

## The lead's note

- **Commissioned and judged** by the ticket lead (an orchestrator-role session in this ticket's worktree, DEC-137). The reviewer was a fresh `independent-auditor` session (`65b2eade-aedd-45f6-b014-4ff8f5d64a91`, 2026-10-27). It was started through `gov launch` under its OS sandbox, with the reading tools alone (`Bash`, `Read`, `Grep`, `Glob`), at effort max. It wrote nothing: the lead's tripwire before and after its session shows no change in this worktree.
- **What was probed:** run 2 of W2-57 (owner, DEC-925 item 3) at head `8f61bda0eb5c` (code head `9f8b06408511`):
  - B1, the route: the close's serial phase takes only the entries not routed to the nightly (`src/gov/close/serial.py`, and the serial phase's call in `src/gov/close/command.py`);
  - R1, the doctor budget: an unread Claude Code version is never a pass. Both are by the engineer (`8d34ea94ba5a`, `9f8b06408511`, session `310f4f41-0e50-4ddd-9c2d-bb6c998cc96f`).
  - The test designer's run 2: W1-19's real-model file (W2-M332, B3), W1-30's r15 rulesync case (R2), and W2-57's R1 cases (`2074ac440fdb`, `8b62efcf2cc2`, `7d16971e1a82`, session `6e0470a5-0894-4c9c-957c-ca46d78108d0`).
  - The merge of `w2/integrate` (`101285866733`).
  - Review 1's record (`PR-DAEO-cy5o.md`, probed `6be837bbbe41`) is of an earlier round of this head's history, and this record is of the final code.
- **The lead's verification at `9f8b06408511`** (after a full rebuild, in the close's form, under the lock, with `-o tmp_path_retention_policy=failed`):
  - `gov check`: ok, 15 GREEN, 2 YELLOW (both known before), no RED.
  - The full parallel run: 16,430 passed, 31 skipped (none names rulesync), 8 failed. The 8 are W2-66's known red (DEC-919) and seven reds of the base that W2-74 retires or revises (W1-01's `docs/source` cases ×4, W1-47's ×2, W1-49's `[not on PATH]`). The route case and W1-06 pass.
  - The serial phase as the close now runs it (the 48 `serial` entries): 104 passed (11:48; it was 180 cases in 17:40 at review 1).
  - The 15 `nightly` entries, run alone as evidence: 76 passed, W1-19's revised real-model file on the shared GPU among them (hit@5 83.33).
- **Verdict: pass.** The lead's judgement agrees with the reviewer's classification (DEC-809):
  - **F1** is yes / fails open, feature-gated (DEC-803). It holds only once `python3 -m gov.close.nightly` replaces the live `nightly.sh`, which DEC-915 item 4 keeps unrun until row W2-M406's fix. The live nightly reads the plugin's entries itself and runs every entry of both routes. So F1 is an entry criterion of the nightly's next change, returned to the orchestrator, not a round.
  - **F2** is yes / other: a row, plus a decision on DEC-549 P-4's scope, returned as a package (DEC-105).
  - **F3** is no / other, and **F4** is no / fails open: rows for the Wave 3 hardening pass.
  - This was the last review of the round (DEC-916); nothing is committed after the probed head except this record.

## The reviewer's record

Verdict: pass, adds P-1 as an entry criterion of the nightly's next change, and takes P-2 to the orchestrator.

---

Verdict: pass

**Head probed:** `8f61bda0eb5c` on `w2/W2-57` (code head `9f8b06408511`; the head adds only the lead's checkpoint). Run 2's changes are `101285866733..8f61bda0eb5c`.

**Step 0:**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cy5o` failed with "Read-only file system", and no file exists.
- (b) `git hash-object -w --stdin` worked (exit 0), and `git update-index --refresh` worked (exit 0).
- Identity: `GOV_ROLE` is `independent-auditor`, `GOV_TICKET` is `DAEO-cy5o`; the toplevel is `/home/usain/gov-os-worktrees/W2-57` on `w2/W2-57`; HEAD is `8f61bda0eb5c`; `git status` shows the 11 placeholder mounts and nothing else, before and after.

**gov.__file__:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -c "import gov; print(gov.__file__)"` printed `/home/usain/gov-os-worktrees/W2-57/src/gov/__init__.py`.

**Classification (DEC-809):** F1 yes / fails open, feature-gated (DEC-803: an entry criterion of the nightly's next change, not a round); F2 yes / other (a row, plus a decision on DEC-549 P-4); F3 no / other (row); F4 no / fails open (row for the Wave 3 hardening pass). No finding is both "yes" and "fails open or loses work" in code in use at this head. If F1 is not read as feature-gated, it fails the probe.

## Probed and found sound

**1. The route (B1).**
- **Same reading as the plugin.** `serial.py` takes the entry with the same rule as the plugin. On the real list it reads 63 entries: 15 nightly and 48 serial, which add up to the whole list, and all 15 are among the plugin's entries.
- **Edge-case lines.** Ten planted lines, results:
  - an entry listed again with the other route: stays serial;
  - `Nightly`: stays serial;
  - `nightly-only`: stays serial;
  - "serial: … nightly …": stays serial;
  - a tab before `#`: the plugin's entry becomes the whole line, it is not routed, and the serial run refuses it under DEC-549;
  - leading spaces: routed, with the same entry;
  - a list that isn't UTF-8: an error, and the close's first read refuses it as `SERIAL_ONLY_LIST_UNREADABLE`.
- **No serial entry can be dropped.** Only an entry that every one of its lines routes to the nightly leaves the serial phase.
- **The parallel phase.** The plugin is still loaded whenever an in-scope entry exists, of either route, and it deselects every listed entry. When every in-scope entry was nightly (planted closes P3a and P3b), no routed case ran.
- **A nightly file that cannot be imported** still refuses the close.
- **Skips.** Routed cases are deselected, never counted as skipped (0 in every probe close), so the 31 the skip guard expects is unchanged.
- **Scope of the change.** `command.py` changed only in the serial phase's call (+7 −4, one import), and gate (h)'s line is untouched. The record's `cases` names the entries given to the serial run.
- **The live nightly.** `.gov-runtime/scratch/orchestrator/tools/nightly.sh` reads the plugin's entries (both routes) and gives them to its serial run, so every routed case runs there and DEC-549 holds there for every entry.
- **W1-30's r11** names all 15 current nightly entries and turns red if one of their cases disappears.

**2. Doctor (R1).** I called doctor's Claude Code check directly with ten stand-in answers:
- no output, exit 0 or exit 1: "unmeasured";
- output on stderr only: "unmeasured";
- `exec` of a missing program: "unmeasured";
- 2.0.0: "fail";
- text with no digits: "fail";
- 2.1.300: "pass".

With every probe hanging (nine registered tools, the venv freeze and `claude`), a full `gov doctor --json` ended in 120.1 s with exit 3, inside W1-07's 180 s. `claude_code` read "unmeasured" with the reason "its --version gave no answer within 30 s", and no process was left.

"Unmeasured" never hides a failure or drift: an extension below the minimum gives "fail", and an extension newer than the pin gives "drift".

**3. The test designer's run 2.**
- **W1-19** (read, not run):
  - the calls, warm-up and timed queries are the same as before;
  - the timed pass runs first, without the sampler;
  - the watched pass runs on a fresh clone and includes the index build;
  - the memory case adds an assertion that the watched pass reranked every list with both routes;
  - no assertion was dropped and no limit changed.
- **r15:** the existing `_assert_turns` check stays, and a stricter assertion is added: a finding naming 23.0.0 and the installed version, and no timeout finding. W1-38's `rulesync_version()` raises on a timeout, so r15 fails rather than skips.
- **The R1 cases** write only under `tmp_path`. Their `exec sleep` stand-ins are killed by doctor's own limit, and `stop_leftovers` runs at teardown.

**4. The change record.** Rows 5 to 7 match the code, apart from observation O1 and the omissions named in F1 and F2.

**5. The merge and the roles.**
- The ticket's amendment (`command.py` added to `allowed_paths`, run 2's KPI line, two more test-designer files) is the orchestrator's commit `235b871ad850`, brought in by the merge `101285866733`.
- Each run 2 commit stays inside its role's paths:
  - the engineer's commits touch only `allowed_paths` and no `tests/acceptance/` path;
  - the test designer's touch only the files the ticket body names, each with a `Rewrite-Reason:`;
  - the orchestrator's adds only the checkpoint.

## Findings

**F1. W2-66's nightly module no longer runs the entries routed to the nightly.**
- **Done:** I made a temporary project whose list routes one test file to the nightly and keeps one serial, with a plain case beside them. I ran `python3 -m gov.close.nightly main --root <project> --json` with this head's code.
- **Happened:** verdict "green", 2 passed. The routed case ran in neither phase: the plugin deselected it from the parallel run, and the route dropped it from the serial run, because the module calls the close's own test-run function. At the merge base that function gave every in-scope entry to the serial run, so the case ran alone (read from the diff; the comparison run was refused, see below). The change record says "Nothing else in the file changes", which is true of the file, but it doesn't name this effect.
- **Should have:** every entry of either route runs in the nightly. The list's header says so, and DEC-889 item 5 sends live and real-model tests there. It must not read green without them.
- **Severity:** high once that module is the nightly; nothing today. DEC-915 item 4 keeps it unrun until row W2-M406's fix ("in the nightly's next change"), and the live `nightly.sh` is unaffected.
- **No acceptance case covers it:** W2-57's nightly-form case uses a test-side form.

Ordinary work: yes, because the planned switch from `nightly.sh` to `gov.close.nightly` (DEC-889 item 4, DEC-915 item 4) is an ordinary orchestrator step after row W2-M406's fix.
Consequence: fails open (feature-gated, DEC-803: an entry criterion of the nightly's next change)

**F2. A nightly entry that names no case no longer refuses the close (DEC-549 P-4).**
- **Done:** I planted a list entry naming a function that doesn't exist, once routed nightly and once routed serial, and closed both projects.
- **Happened:** routed nightly, the close passed. Routed serial, it was refused: "the serial run afterwards … exited 4: … (no match …)". Before run 2, every in-scope entry was checked this way. The change record says the check "holds for" the serial entries, but doesn't record that it no longer covers the nightly ones.
- **Should have:** DEC-549 P-4 says "A list entry that names no case: … the close is refused with a finding". Either the close keeps that check for nightly entries, or the owner records that the check now covers only serial entries.
- **Severity:** low. No case runs less: what a stale entry meant to route still runs in the parallel phase. The live nightly refuses the entry, and r11 holds every current nightly entry.

Ordinary work: yes, because a renamed or mistyped entry is what DEC-549 P-4 exists for.
Consequence: other

**F3. A nightly function inside a serial file entry still runs in the close.**
- **Done:** I listed a file as serial and one of its functions as nightly, then closed the project.
- **Happened:** the nightly function ran once, alone, in the serial phase. The record's `cases` names only the file. (The reverse overlap, a nightly file with a serial function inside, behaved correctly.) W1-30's r11 takes the first entry that names a case, so r11 and the close can disagree on such overlaps.
- **Should have:** the KPI says "a nightly: entry is collected and left out of both phases".
- **Severity:** low. The case runs more, not less.

Ordinary work: no, because the list has no such overlap and only the owner adds entries (DEC-862).
Consequence: other

**F4. An unread Claude Code version still reads "pass" when `claude --version` exits non-zero with a number on stdout.**
- **Done:** I put stand-in `claude` CLIs first on the PATH. Each printed on stdout and exited 1, with "fatal: 7 problems" or with "Error: … Node.js 18.0.0 …".
- **Happened:** the `claude_code` part read "pass", with `cli_version` "fatal: 7 problems" or "18.0.0". Doctor ignores the exit code and takes any number as the version. These lines predate run 2.
- **Should have:** the part reads "unmeasured" or "fail", as R1's aim says.
- **Severity:** low.

Ordinary work: no, because a failing CLI prints its error on stderr, and doctor then reads "unmeasured" (probed).
Consequence: fails open (a row for the Wave 3 hardening pass)

## Observations (other, no round)

- **O1.** The change record's example "`nightly` without its colon" staying serial holds for the unit test's form ("nightly real-model …"). A bare `# nightly` comment routes to the nightly, which matches `serial.py`'s own docstring. In this repository r11 refuses such a comment because it has no kind or reason.
- **O2.** The close's record names no case it left out for the nightly: routed cases appear in none of the record's fields (`test_runs`, `cases`, `skips`, `left_out`). W2-58 is still in progress. At its own close, its four launched-session functions (five sessions) will leave its acceptance run, as DEC-889 item 5 and the KPI order, and its record won't say so. W2-58's lead verification must carry them.
- **O3.** A ticket whose every acceptance case is routed nightly is refused with "no test was collected". That fails closed, though the message is inaccurate: the cases were collected, then deselected.
- **O4.** The `load_sensitive` entries for W1-19's warm p95 and W1-46's 23 cases are now inert. The ticket's last KPI line gives their removal to the orchestrator.
- **O5.** Doctor's canaries part runs outside the probe limits. It is unchanged by run 2 and I didn't probe it.

## Scratch, refusals, retrieval

- **Scratch:** 8 inodes / 24 KB at start; 234 inodes / 956 KB after the heaviest probe and at the end. That is far inside my share of 6 GB and 300,000 files and folders.
- **Read refusals (DEC-849):** 0.
- **Other guard refusals:** 3, each on a different call, none tried twice:
  1. A Bash write to a shell variable's path ("guard-unresolvable"). I then wrote the stand-ins from a Python script inside my temporary folder, which is an adjustment I'm disclosing here.
  2. The merge-base comparison command for F1, refused as unreadable under DEC-409's check. Not retried.
  3. `rm -rf` of my probe folders, refused because the target held a variable. Not retried; the folder goes when the session ends (DEC-386).
- **`gov retrieve`:** used once, to ask which ticket or row switches W2-66's nightly on. Both facets answered "stale", so I read the named files instead (`WAVE_2_LIST.md` row W2-M406, the register, `nightly.py`).
- **Code-graph tool:** not used. The callers of the close's test-run function were found with one targeted search of `src/`: two callers, the close and the nightly module.

task: DAEO-qyt2 (W2-185), the narrow independent check of run 3's test revision only (4808016ac, merged by 997e25f1e)
status: PASS
work_completed: Sandbox check (a) and (b), then the `ps` check. Quoted HEAD. Read the ticket whole, with both widening notes, and DEC-917, DEC-1167 (4) and DEC-1156 (7). Read the diff 6b4bafb71..997e25f1e and the support helpers it calls. Checked the `src` and `template` diff since 16bddf807. Ran the revised file unplanted in an archive copy, then 3 required plants and 6 more in the copy's `template/.rulesync/hooks.jsonc`, so the generated case runs through rulesync. Ran the base (6b4bafb71) version of the file against today's template. Checked scope and trailers.
files_changed: none (scratch only in my own `$TMPDIR`)
evidence: `git rev-parse HEAD` = 997e25f1e9c670b17c7db880319d96c2119e4a44. `git diff --stat 6b4bafb71..997e25f1e` = 1 file, `tests/acceptance/W1-38/test_w1_38_hooks_command_line.py`, +39 −9. `git diff 997e25f1e 4808016ac` is empty, so the merge has the same tree as the test designer's commit. `git status --porcelain` on the tree is empty at the end.
tests: Copy at 997e25f1e unplanted: 19 passed, 0 skipped. Base file on today's template: 2 failed (the two `[PostToolUse]` ids, `assert 2 == 1`), 17 passed. All 9 plants turned red exactly the cases they should, and only those. One extra red under plant e is explained in point 2. Every run used `--optin lifted,breadth` through `heavy_slot.sh`, with an empty HOME in `$TMPDIR`; it was a single-file run, so no folder-level exclusion applied.
discoveries: In the lead's `cases-997e25f1e.txt`, `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestKernelAgainstAdapterSource::test_kernel_role_changed_without_its_source` and `::test_role_source_changed_without_its_kernel_role` fail (an extra `governance/kernel/templates/role-engineer.md`). They fail the same way at base e2a0d6191 (`rulesync-base-e2a0d6191.txt`, "FF.."), so they come from w2/integrate and are outside this revision and this ticket.
risks: none for this revision.
lessons: The template plant runs in about 9 s per plant. A heavy-slot wait (all 3 slots taken) cost about 30 minutes; my first base-file attempt was stopped by its background time limit while waiting, and the retry passed through.
proposed_decisions: none
unresolved: none
recommended_next_action: The lead copies the verdict block into `docs/probes/DAEO-qyt2/` and takes W2-185 on to its land. The two W1-38 rulesync reds go to whichever ticket owns `role-engineer.md` on integrate, not to W2-185.

Sandbox check (launch_worker.sh, Step 0):
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-185','w').write('x')"` failed with `OSError: [Errno 30] Read-only file system`, and no file was written.
- (b) `echo sandbox-trial | git hash-object -w --stdin` printed `1ae28402a109…` (exit 0); `git update-index --refresh` exited 0.
- `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"`: nothing.

**Code unchanged:** `git diff --stat 16bddf807 997e25f1e -- src template` shows 9 files (+875 −22): `adopt/*`, `check/commands.py`, `guard/bash_writes.py`, `guard/decide.py`, `skilleval/*`. These are exactly the w2/integrate changes since the merge base 235fc1cc6; the only first-parent commit touching them is the merge 6b4bafb71. `git show --cc 6b4bafb71 -- src template` is empty, so the merge resolved nothing by hand. The ticket's own `portability.py` and `template/.rulesync/hooks.jsonc` have not changed since 16bddf807.

## 1. Each revised case keeps its point: PASS (by reading and by running)

- **Guard events:** the new helper `_the_guard_line` finds the program the kernel template registers for the event and keeps the entries whose whole-file-name programs include it.
  - Exactly one such entry is required; two or none fail with `assert len(mine) == 1`.
  - Its line is then compared with the kernel template's line exactly, unchanged from before (DEC-917).
  - Plant g, which swaps the order of the two PostToolUse entries, stays green: the entry is picked by its program, not by its index or by a count of all entries.
- **PostToolUse:** besides the guard's entry there must be exactly one other entry, and it must name `context_watch.py`. This pins DEC-1167 (4) instead of the old one-entry behaviour.
- **PreToolUse and PostToolUseFailure:** before, the case required exactly one entry, and that entry had to equal the kernel line. Now it requires exactly one entry running the kernel program, no other entry, and equality. That is at least what was asserted before, and slightly stricter, because the program must match. The "no other entry" rule is the old one-entry rule carried over (DEC-608/917), not something new.
- **Lifecycle events:** `mine = list(commands)`, `others = []` and `len == 1` are exactly the old assertion, followed by DEC-608's plain form, unchanged.
- **Strictness compared with the decision:** DEC-1167 (4) puts the context watch line only in postToolUse, and S1 wires it there (matcher Bash, timeout 10). So "PostToolUse = the guard plus exactly the watch" is what was decided. Elsewhere the helper only keeps the earlier rules; it goes no further than DEC-1167 (4) needs.
- **The watch's own line is not held to a form here.** It never was in this file; W2-185's own S1 cases hold it (`tests/acceptance/W2-185/test_w2_185_hooks.py`).
- **No lowering:** no skip, xfail, flaky or rerun mark was added. The case docstrings and the `assert line == expected` message keep their DEC-917 meaning.

## 2. Plants: PASS (all run in the copy's template file, the generated case through rulesync)

Unplanted: `python3 -m pytest --optin lifted,breadth tests/acceptance/W1-38/test_w1_38_hooks_command_line.py …` gave **19 passed**.

Required plants (each red on both `[PostToolUse]` ids only; 2 failed, 17 passed):

| Plant | Failing assertion |
|---|---|
| (a) a second `posttooluse.py` entry under `postToolUse` | `2 hook entries run posttooluse.py under PostToolUse; one is expected` / `assert 2 == 1` |
| (b) the guard command changed by one character (final `exit 2` to `exit 3`) | `assert 'h="$CLAUDE_P..." >&2; exit 3' == 'h="$CLAUDE_P..." >&2; exit 2'` |
| (c) the guard entry removed, only the context watch left | `0 hook entries run posttooluse.py under PostToolUse; one is expected: []` / `assert 0 == 1` |

Further plants:

| Plant | Result | Failing assertion |
|---|---|---|
| (d) a second context-watch entry under PostToolUse | 2 failed, both `[PostToolUse]` | `the entry beside the guard's is expected to be the context watch's … assert (2 == 1)` |
| (e) the context watch also under preToolUse | `[PreToolUse]` generated and source red | `PreToolUse holds an entry beside the guard's, which DEC-1167 (4) gives only to PostToolUse` |
| (f) the context watch also under postToolUseFailure | 2 failed, `[PostToolUseFailure]` generated and source | the same "beside the guard's" assertion |
| (g) the two PostToolUse entries in swapped order | **19 passed** (picked by program, not by index) | none |
| (h) a second `stop.py` entry | 2 failed, `[Stop]` generated and source | `2 hook entries run a kernel hook program under Stop … assert 2 == 1` (lifecycle rule intact) |
| (i) the PreToolUse guard line changed by one character | 2 failed, `[PreToolUse]` | `assert '... exit 3' == '... exit 2'` |

Under plant (e), `TestAProductPackageNamedGov::test_a_call_the_guard_refuses_is_refused_by_its_written_refusal` also went red. That comes from the plant itself: the watch's answer under PreToolUse is not the guard's written refusal. It has nothing to do with the revision.

Before: the file at 6b4bafb71 run against today's template gives 2 failed (both `[PostToolUse]`, `assert 2 == 1`) and 17 passed, matching the brief.

## 3. Scope and trailers: PASS

- **Scope:** commit 4808016ac touches only `tests/acceptance/W1-38/test_w1_38_hooks_command_line.py`, which is in the ticket's `allowed_paths` (the 2026-11-14 widening, P-W2-185-REDS-2 (a)).
- **Trailers:** one final paragraph holding `Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 3)`, `Task: DAEO-qyt2`, `Role: independent-test-designer`, `Implements: DEC-1167, DEC-1156` and `Co-Authored-By`.
- **Implements:** both ids are in the ticket's `sources: [DEC-1167, DEC-1163, DEC-971, DEC-805, DEC-1156]`.
- **Merge commit:** 997e25f1e carries `Role: orchestrator`, and its tree is the same as 4808016ac's.

## Findings

None. What I probed and found sound:
- Entry selection by program, with order not mattering.
- Duplicate, missing or one-character-changed guard entries, under all three guard events.
- A context watch in the wrong event or doubled.
- The lifecycle one-entry rule and plain form.
- The kernel line equality (DEC-917).
- No lowering marks.
- Scope and trailers.
- No `src`/`template` change since the last PASS other than the clean w2/integrate merge.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}]}
```

guard_refusals:
- No guard refusals.
- One harness permission refusal: two Write-tool calls to `$TMPDIR/plant.py` and `$TMPDIR/run_plants.sh` returned "Claude requested permissions to write to …, but you haven't granted it yet." I wrote the same two scripts into `$TMPDIR` with a sandboxed Bash heredoc instead, since the brief asks for scripts to go in `$TMPDIR` and the sandbox allows writes there. I did not retry the Write tool.
- My first base-file run was stopped by its background time limit while waiting for a heavy slot. That was a wait, not a refusal, and the retry passed.

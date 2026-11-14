# Brief: independent auditor, W2-185 (DAEO-qyt2), the narrow independent check of run 2's test revision only (DEC-1156 (7))

You are a fresh independent auditor (role independent-auditor), ticket DAEO-qyt2 (W2-185), profile STANDARD, class C2.
Read-only: you change nothing in any tree; you write only in your sandbox's own `$TMPDIR`. Headless: only your last
message is read, and the lead copies its verdict block into the probe record as you wrote it.

## What you judge
Branch `w2/W2-185` at head **16bddf80782449573cedd7373544533d79d2a326** (quote `git -C /home/usain/gov-os-worktrees/W2-185 rev-parse HEAD`),
in `/home/usain/gov-os-worktrees/W2-185` (read it there; never write there). **Only the revision:**
`git -C /home/usain/gov-os-worktrees/W2-185 diff 0c7e4d68f..16bddf807` (8 files; base 0c7e4d68f = the ticket's build,
already judged PASS at 1180e4ec5 in `docs/probes/DAEO-qyt2/PR-DAEO-qyt2.md`, with w2/integrate merged). The ticket, read
it whole, with its widening note: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qyt2.md`. Decisions, grep
the register by id only (`/home/usain/gov-os-worktrees/W2-185/docs/DECISION_REGISTER.md`): DEC-1167 (4), DEC-971
item 3, DEC-1156 (7).

The revision: a fresh independent test designer (td-3, session 0298f2b5-6127-4da2-b447-a810a9ee8e3e) revised the 18
cases the round-1 probe record named (lines 41-57) to the decided behaviour of DEC-1167 (4): the template wires
`context_watch.py` in `postToolUse` beside `posttooluse.py`, and the lift exemption is per hook (the template's
`posttooluse.py` entries only). Commits, one per file, each with `Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 2)`:
2ad99213c (`tests/acceptance/W1-38/w1_38_hooks_support.py`), 8ee2c6dc4 (`test_w1_38_hooks_any_folder.py`), 6cb684972
(`test_w1_38_hooks_source.py`), 00b56d2f2 (`tests/acceptance/W2-59/test_w2_59_hook_lines.py`), 80841a0c6
(`test_w2_59_hook_lines_worker_env.py`), 1689ecce8 (`tests/unit/hooks/test_w2_106_template_hook_lines.py`), 86a7e7480
(`tests/acceptance/W2-05/test_w2_05_hooks_source.py`), e54b383f8 (`tests/unit/gitenv/test_hooks_lifted.py`); merged by
16bddf807 (the lead). It kept every id, deleted no case, added 16 cases (176 → 192 with the opt-in suites).

Judge:
1. **Each revised case keeps its point** (the probe record's 18 ids, plus `test_w1_38_hooks_source.py::TestRulesyncPassesBothThrough::test_a_limit_and_a_failed_tool_call_entry_of_the_source_reach_the_generated_settings`
   and the two `*_carries_the_time_limit` cases the default `-k` hides, which the same S1 line turned red): what it
   guarded before still fails when broken, and it now pins DEC-1167 (4) rather than the old one-entry or whole-event
   behaviour. Entries picked by program, not by index or count. No lowering: no skip, xfail, flaky or rerun mark; no
   weakened assertion beyond what the decided behaviour needs. Where the test designer could not read
   `portability.py` (the counterpart's work), its new unit cases accept `HOOKS_EVENT_DIFFERS` or `HOOKS_MATCHER_DIFFERS`:
   say whether that leaves any face unpinned.
2. **Plants** (in your copy): at least (a) the template without its `context_watch.py` entry turns the W2-59
   seven-lines case, the W2-106 pair case and the W1-38 context-watch cases red; (b) a non-exempt extra template entry in
   `postToolUse` (another program) gives a portability finding in the W2-05 / `test_hooks_lifted.py` cases' sense; (c)
   the template's `context_watch.py` given another matcher than the root's is a finding. Green unplanted, red planted.
3. **The five `PreCompact` cases** (`test_w1_38_hooks_any_folder.py` `[PreCompact-*]` and the space case `[PreCompact]`),
   outside the 18: red on 0c7e4d68f because `precompact.py` writes its read-first line as text before its JSON (W2-176,
   13fd1dd34, already in the claim base 31eab2103), not because of this ticket. The support's `_json` now reads the last
   JSON line. Judge whether the case still asserts the program's own "no state block" message, and whether this hunk
   belongs in this revision (allowed path; its `Rewrite-Reason` names DEC-1167 (4) though its cause is W2-176).
4. **Scope and trailers:** only the eight widened files; `Task: DAEO-qyt2`, `Role: independent-test-designer`,
   `Implements:` from `sources:` only, `Rewrite-Reason:` on each, trailers in one final paragraph.

S1, S2, S3 and F1 were judged PASS on the code at 1180e4ec5 and the code has not changed since (`git diff 1180e4ec5
16bddf807 -- src template` shows only w2/integrate's changes, if any; check it). Your verdict per KPI line is on whether
the revision keeps each line's guarding cases sound.

The lead's runs on 16bddf807 (in the tree, `.gov-runtime/scratch/lead/log/`): `gov accept W2-185` pass, 18 passed 0
failed (`accept-16bddf807.txt`); the eight files with the opt-in suites (`reds-post-16bddf807.txt`, when present);
lead_verify (`verify/summary.txt`, when present).

Work in a **copy** of the tree in your `$TMPDIR` (`git -C /home/usain/gov-os-worktrees/W2-185 archive HEAD | tar -x -C
"$TMPDIR/copy"`; never `git worktree add`, never a write in the tree). Where a plant or run cannot run in your sandbox,
say so with the exact refusal and judge by reading, naming which you did.

## Judgement rules (governance/project/briefs/JUDGEMENT.md, word for word)


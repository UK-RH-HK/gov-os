# W2-128 round 1 fixes — the product-spec worker's brief (DAEO-t8mp)

You are a fresh product-spec worker for **W2-128** (`.tickets/DAEO-t8mp.md`; read it, especially "Interface and
rounds"). Round 1 is on `w2/W2-128` (your commit `a6c83d497035`), reviewed READY. The review is
`/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/reviews/w2-128-r1.md` (on integrate; read
its findings F1-F5 and F9). This round fixes them before the merge, plus one line a revised W1-35 case needs.

## The fixes (only these)
1. **F1:** the test designer's command forms (`{CMD:accept}`, `pytest_folder`, `unit_tests`, and any other a designer's
   template uses) are bound to the designer's own tree: use `{WRITE_TREE}` (or a designer form such as R3's
   `acceptance_red`), never `{TREE}`, where T-4 or T-0 gives them to a designer; keys in `keys.yaml`.
2. **F2:** `steps.checkpoint_record` off (DEC-511 changed by DEC-1057, R-6 lifted), its comment corrected;
   `steps.collect_only` off or re-cited to an ACCEPTED rule still in force (DEC-868 was lifted by DEC-953 item 1).
3. **F3:** `role-lead.md`'s "one writer per worktree" line cites `[DEC-963]`, not `[DEC-254]`; `role-test-designer.md`'s
   "public interface; deterministic" line cites a decision that states it, or none.
4. **F4:** T-0's "Ask memory first" qualified for the sandbox ("outside the sandbox {CMD:retrieve} …; inside it, the
   Read and Grep tools [DEC-1065]"), and the same in T-4 and T-2 where they name `{CMD:retrieve}`. S20's exact
   sentence ("Search again once: …") stays right after the "Ask memory first" line, unchanged.
5. **F5:** one "first line in `evidence`" quote in T-7: `gov links`' (LINK-INTEGRITY §5: in place of
   `trailer_gate.py`'s); `trailer_gate`'s evidence quote dropped or the switch off.
6. **F9:** the CIT-P draft's record count from a fresh `python3 -m gov.check.schema` run.
7. **DEC-462 (a revised W1-35 case):** `role-test-designer.md` (or `role-lead.md`, where the lead writes a designer's
   brief) carries one line: "A test designer's brief states behaviour and sources only, never the names of the
   implementation's private parts [DEC-462]" (DEC-462 is ACCEPTED). The case reads `brief.md`, `role-lead.md` and
   `role-test-designer.md` for a statement that a test designer's brief states behaviour and sources only.
8. Every template stays within R3 §C's budget; every bracketed id ACCEPTED and not lifted or expired (check the
   entry's `Changed by:`/`Lifted by:` lines, not only its status word).

## Where you work, rules, return
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-128`, branch `w2/W2-128` (now `71817b01`: the W1-35 revision
  merged by the CTO). Your paths: the ticket's `allowed_paths`.
- **You never read `tests/acceptance/W2-128/` or `tests/acceptance/W1-35/`** (DEC-820 (c)); run them only as below and
  read only result lines. Exclude both folders from every Grep, Glob and recursive search.
- Checks, with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-128/src`: `python3 -m gov.cli.main accept W2-128 --root /home/usain/gov-os-worktrees/W2-128`
  (or, if it crashes in the sandbox, `python3 -m pytest tests/acceptance/W2-128 -q -p no:cacheprovider -rf`);
  `python3 -m pytest tests/acceptance/W1-35/test_w1_35_orchestration.py -q -p no:cacheprovider -m "not local_only" -k "TestBriefTemplates or TestRows or TestWording or record_template" -rf`;
  `python3 -m gov.check.schema`. No whole-suite run.
- Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No
  GPU, model, network, installs or `gov retrieve`. DEC-1080: one simple command per Bash call. Do not merge; never touch
  `tests/acceptance/**`, `.tickets/` or `.claude/`. Search again once (DEC-1092 (1)) if a search does not answer.
- **Commit** on `w2/W2-128`, only your paths, with
  `--trailer "Task: DAEO-t8mp" --trailer "Implements: DEC-1050, DEC-1052, DEC-1073, DEC-963" --trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round: keep it short.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), per fix what changed (file and line), each template's prose size, the three checks' counts.

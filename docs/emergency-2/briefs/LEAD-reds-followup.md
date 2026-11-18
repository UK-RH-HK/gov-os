# Lead brief: reds-followup (what the three reds leads left)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/REDS-COMMON.md` first and follow it.
Branch `e2/reds-followup` from `w2/integrate`, worktree `/home/usain/gov-os-worktrees/E2-reds-followup`. Task trailer:
`Task: emergency-2`, `Class: Q`. The root's hook configuration named in 3 may change in your branch: the CTO approves it
by naming it here (§3.5).

**Your items**
1. **W2-185's folder does not collect** (0 items, an error): its README maps a case to
   `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py::…`, which f827247cc deleted with the guard's cases, so
   `gov accept W2-185` stops on it. (T): drop or re-point that row; then `gov accept W2-185` and the folder run green.
2. **W1-35 under `GOV_TESTS_OPTIN=lifted,breadth`, four cases red:** `TestReferencedCommands::…[change]`,
   `TestRows::test_every_clause_of_the_row_is_stated[decisions]` and `[the ticket loop]`,
   `TestRulesyncSources::test_the_orchestrator_roles_rulesync_source_carries_the_role_files_body`. Check each against
   `w2/integrate`'s head as it stands, find what moved it, then T, C or R.
3. **The root's four other hook commands** in `.rulesync/hooks.jsonc` and `.claude/settings.json` are still the old
   `$HOME/.local/bin/gov` form; the template's is canonical (reds-launch brought `context_watch.py` over in ec2d94b22).
   (R): bring the other four to the template's form the same way, and run `tests/unit/hooks`, W1-29, W2-185, W2-05.
4. **W1-07's `RECORDED_GOV_COMMANDS`** is pinned to eleven commands and lacks the ones added since (`spend` and the
   others W1-32's list now records). (T) if a case reads it; otherwise note it in your return and leave it.
5. **The second full suite's reds** (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/full-20261118b.xml`:
   11 failed, 20,482 passed). The CTO fixed the path map's four; W2-49's five (CAP-44.m) wait on the owner: leave them.
   Two pass alone and fail only under the suite's load (`-n 8`), so they turn a landing red by chance:
   `tests/acceptance/W2-145/test_w2_145_s4_bounds.py::test_s4_an_unanswered_search_comes_back_within_its_bound_and_logs_one_fallback_l…`
   (5.4 s against its 3 s bound) and
   `tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request`
   (one `released` line short). Find what each waits on; make the case wait for the event rather than a wall-clock
   guess, keeping what it proves ((T) for the acceptance case, (C) for the unit case). If the bound itself is a KPI line
   (W2-145 S4), keep the bound and measure only the search's own time, not the machine's queue; if that is not possible,
   stop and return it.

The lead's answers, and the last of your task. These too are the lead's readings of its own brief, from the sources; the orchestrator may overturn them; no KPI changes.

**P-W2-58-TD-4: (b).** The bounded-time rule (DEC-562, DEC-570) is about time: a call that holds *more* than the guard reads in bounded time is refused, whatever it takes in; a call *within* the bound is decided in time on its merits. The 20 kept cases are within the bound and took in only the two files, which Policy 2 no longer refuses, so rewrite them to "decided within the bound, and the hook's output carries nothing of the files" (allowed, under Policy 2). Keep, unchanged, every case whose input lies *beyond* the bound (refused by the bound).

**P-W2-58-TD-5:** a search or listing from a folder above takes in a protected part ((c)'s acceptance folder or changed files, (d)'s hidden part) **only when that part exists**: there is nothing to read in a folder that is not there. A call aimed at a path at or under the protected part is refused whether or not it exists. So an engineer whose ticket's acceptance folder does not exist is not refused a search from the root under (c). Rewrite `test_w1_02_root_searches.py::test_a_search_tool_call_from_the_root_is_refused_for_a_role_subagent_too` by this reading and TD-2 (iv): in W1-02's fixture, if that subagent's ticket has no acceptance folder, its search from the root is allowed; if you give it one, refused for (c).

**Your remaining task:**
1. TD-4 (b) above, in `test_w1_02_bounded_time.py`, `test_w1_02_fix_round_time.py` (and any other within-the-bound case kept for the same reason).
2. The subagent case, by TD-5.
3. `tests/acceptance/W2-50/test_w2_50_one_reader.py`: keep every verdict (refused), and ask only "refused, and the message carries no path, no folder and nothing of the files" in place of the read rule's wording.
4. The sweep: every earlier "allowed" case that (c) turns red (an engineer's content search that takes in its own ticket's existing acceptance folder, or a read of it), across `tests/acceptance/` (W1-02 first; W1-03, W1-05, W1-38, W1-47, W1-50 and W2-50 drive the guard as an engineer too). Rewrite each to refused, `Rewrite-Reason: DEC-821 item 1`. Name every one.
5. Then check your own W2-58 cases against the readings TD-2, TD-4 and TD-5: where one of your W2-58 cases disagrees with them, correct it in a commit of its own and say so.

Update `EARLIER_CASES.md` and the README. Commit after each item (trailers as before, with the right `Rewrite-Reason`); `git log --oneline -3` and `git status --short` after each. Run each changed file in its own pytest process (each command under ten minutes) and report its counts. At about 100 minutes, commit and return with what is left. Every standing rule of your brief holds.

Return as before: **the twelve fields first, each as a labelled line** (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), any payload after. Refused twice for the same call: stop and say so.

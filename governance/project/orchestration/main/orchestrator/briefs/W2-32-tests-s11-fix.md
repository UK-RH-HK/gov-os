# W2-32's independent test designer: one fix in S11's per-file cases (DEC-1074 (5))

You are W2-32's independent test designer (`DAEO-0pyc`), launched by `gov launch` under that ticket's id. Same rules,
worktree and commit form as your last brief (`briefs/W2-32-tests-s11.md`, and `EMG-d4b-launched.md`); read both first.

**What the CTO found:** `gov accept W2-32` on the merged build gives 32 of S11's 35 cases passing. The three that fail
fail inside the test, before any assertion is judged:
- `test_w2_32_s11_pool.py::test_per_file_first10_holds_at_most_n_of_a_file_in_the_first_10_and_loses_none[1]`, `[2]`
- `test_w2_32_s11_pool.py::test_v456_per_file_first10_holds_with_the_others_on`

The failure, at `test_w2_32_s11_pool.py:280`: `p.items(p.capped(today["evidence"], n))`. `capped` returns a list of
evidence items, and `items` reads `bundle["evidence"]`, so it raises
`TypeError: list indices must be integers or slices, not str` (`w2_32_pool.py:170`). On integrate these cases were red
earlier, at the unknown setting, so this line was never reached.

**Your task:** fix the cases so they compare what S11 states (the first 10 hold at most n chunks of one file, filled in
today's order, the rest following in today's order, none lost), with no change to what they assert. Show the fix on
today's integrated code (still red for the setting) and in a stand-in, as you see fit; you do not read the build.
Commit with `Task: DAEO-0pyc`, `Implements: DEC-1074`, `Role: independent-test-designer`, `Rewrite-Reason: a helper
called with a list where it takes a bundle (the cases never reached it on integrate)`, `Co-Authored-By: Claude Opus
5.5 <noreply@anthropic.com>`. **Return:** the sandbox and `ps` checks, then the twelve labelled fields. Est.: 20 minutes.

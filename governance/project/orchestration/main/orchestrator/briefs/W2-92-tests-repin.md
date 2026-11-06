# W2-92's independent test designer: re-pin the 15 stale baseline cases (DEC-1074 (5))

You are W2-92's independent test designer (`DAEO-n0wb`), launched by `gov launch` under that ticket's id. Same rules,
worktree and commit form as your last brief (`briefs/W2-92-tests-w4.md`, and `EMG-d4b-launched.md`); read both first.

**What the CTO found:** run outside the sandbox through the heavy slot on today's integrated code (`436a7520`'s
`src/`), 15 of the folder's older cases are red, all with the same cause. They are the five
`test_w2_92_unchanged.py::test_u1_a_question_naming_no_record_or_symbol_gets_todays_bundle[*]` and the ten
`test_w2_92_speed.py::test_s6c_the_record_route_answers_as_the_integrated_code_does[*]`. The pinned "today's bundle"
predates a field the integrated code's bundle now carries (`repeats`, from W2-32's work on spans sent twice), so they
fail with "the bundle changed outside its evidence: {"repeats": ...}". Nothing W2-92 builds caused it.

**Your task:**
1. Re-pin those cases' baseline to the integrated code as it is now, as `507df49a` and `d71df8f8` did before: the
   `repeats` field becomes part of today's bundle, and any other change still makes them red. Change nothing else
   about what they assert.
2. Show them green on today's integrated code, and show each still red on a planted change to what it guards (as the
   earlier re-pins did).
3. Check whether the same stale pin affects the folders the README names for "nothing else changes" (`W2-87`,
   `W1-21`, `W1-19`, `W1-42`): run them outside the real-model cases. List any red with its cause in your return; do
   not change other tickets' cases.
4. Commit with `Task: DAEO-n0wb`, `Implements: DEC-1074`, `Role: independent-test-designer`,
   `Rewrite-Reason: the integrated bundle gained W2-32's repeats field after these cases were pinned`.

**Runs:** through the heavy slot, as before. **Return:** the sandbox and `ps` checks, then the twelve labelled fields.
Est.: 1 hour.

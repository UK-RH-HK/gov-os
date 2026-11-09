# W2-128 — the W1-35 revision, the independent test designer's brief (DAEO-t8mp)

You are a fresh independent test designer working under **W2-128** (`.tickets/DAEO-t8mp.md`). W2-128's TPL-1 S4
(its 4th success line) retires `template/governance/kernel/templates/brief-engineer.md`, `brief-test-designer.md`,
`brief-reviewer.md`, `brief-product-spec.md` and `brief-lead.md`: each becomes **a one-line pointer** to the template
that replaces it (the ticket body's "Interface and rounds": `brief-engineer.md` → `role-engineer.md` (T-5),
`brief-test-designer.md` → `role-test-designer.md` (T-4), `brief-reviewer.md` → `role-reviewer.md` (T-6),
`brief-product-spec.md` → `role-product-spec.md` (T-3), `brief-lead.md` → `role-lead.md` (T-7), with T-0 `brief.md` the
envelope). Four cases of the closed ticket **W1-35** (`DAEO-0i6h`) read the old brief texts word for word and go red
when that lands (confirmed by the CTO on `w2/W2-128`):
- `tests/acceptance/W1-35/test_w1_35_orchestration.py::TestRows::test_every_clause_of_the_row_is_stated[briefs]`
- `...::TestBriefTemplates::test_the_brief_has_a_placeholder_for_each_thing_it_is_filled_in_with[engineer]`
- `...::TestBriefTemplates::test_the_brief_carries_the_standing_sentences_word_for_word[engineer]`
- `...::TestBriefTemplates::test_the_test_designers_brief_states_behaviour_and_sources_only`

## The change (DEC-866: a revision of another ticket's case carries `Rewrite-Reason:`; D5 row 1: `Task:` is W2-128's)
For each of the four: decide, from W1-35's KPI line it covers (`tests/acceptance/W1-35/README.md`, the ticket) and
W2-128's KPI lines and interface, whether the case (a) follows its content to the replacing template, checked by the
**substance W1-35's line requires** (written from the specs, never from W2-128's implementation), or (b) accepts the
pointer form for the retired file and moves the substance check to the replacement, or (c) is retired as superseded by
TPL-1 S4 (DEC-1050, DEC-1052), with the reason in the README. Prefer (a) or (b) where W1-35's line still governs
something W2-128 keeps; (c) only where DEC-1050/1052's templates replace the rule itself. Each case must pass on today's
integrate **and** on a tree where the five files are one-line pointers and the role templates carry the substance:
write it so it does both (e.g. read the pointer's target when the file is a pointer).
Nothing else in W1-35 changes. Update W1-35's README map rows for the four.

## Where you work
- Your worktree `/home/usain/gov-os-worktrees/W2-128-tests`, branch `w2/W2-128-tests`. You write only
  `tests/acceptance/W1-35/`. If the guard refuses that path, stop and report it (do not route round it).
- **Never read W2-128's implementation (G-14; DEC-820 (c)):** never open `/home/usain/gov-os-worktrees/W2-128` or the
  branch `w2/W2-128`; keep every search inside your worktree (DEC-1093 (2)). You may read integrate's code and texts
  (DEC-963) and W2-128's own acceptance cases in your tree.
- Run only W1-35's cases: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-128-tests/src python3 -m pytest tests/acceptance/W1-35 -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit"`
  with an empty `HOME` (no whole-suite run); W1-35 and W1-30 have colliding `conftest` modules, so never run them in
  one pytest call.
- Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No
  GPU, model, network or installs. DEC-1080: one simple command per Bash call. No merge inside the sandbox. Search
  again once (DEC-1092 (1)) if a search does not answer.
- **Commit** on `w2/W2-128-tests`, only `tests/acceptance/W1-35/`, with
  `--trailer "Task: DAEO-t8mp" --trailer "Implements: DEC-1050, DEC-1052" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: W2-128 TPL-1 S4 retires brief-*.md to one-line pointers (DEC-1050, DEC-1052; DEC-866)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round: keep it short.

## Return
Your final message, in full: the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), per case
the choice (a), (b) or (c) and why, the run's counts on your tree, the commit and `TESTS-READY <hash12>`.

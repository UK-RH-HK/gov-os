# W2-105 (DAEO-zpdj): fix the six reds the merge of integrate revealed (independent test designer)

You are a fresh **independent test designer** (Opus 5.5, effort high, class C2; RUBRIC-2, DEC-1120), launched by the CTO
(orchestrator DAEO-sdxk, session b40cba91, 2026-11-11) under W2-105's ticket `DAEO-zpdj` in its own worktree
`/home/usain/gov-os-worktrees/W2-105`, branch `w2/W2-105`, head `f95b82431ec5` (the merge of `w2/integrate` into it, DEC-999).
No other worker is in that worktree. Read first, whole: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-common.md`
and `EMG-d4b-launched.md` beside it, then `LIFT-common.md` and `NIGHT-common.md`; where they differ from this brief,
this brief holds: the lift's closes are done; the main tree must stay clean (you never write in it); the next free
decision id is DEC-1137 (yours to propose, never to write). Your temporary folder is the sandbox's own `TMPDIR`
(never a new `/tmp/gov-os-emg-*` folder).

## What happened

The CTO merged `w2/integrate` into `w2/W2-105`. The one conflict (`template/.rulesync/permissions.jsonc`) was resolved
as both sides' intent: integrate's new allow line `"gov launch:*": "allow"` (W2-56 round 2, commit `dca333e7a55d`) stays,
W2-105's two removed deny lines (`npm install*`, `pip install*`) stay removed. The merged file is correct. Six test
cases are red only because their expected rule sets predate the allow line. The facts are in
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-105/RESOLUTION.md`, sections 5 (what goes red, and the probe fix) and
1 (the answer, short); read those two sections now. (If your sandbox cannot read that path, the launcher has copied
this brief with the facts below; they are enough.)

## The task: two fixes, nothing else

**Fix 1: W2-105's own folder, `tests/acceptance/W2-105/`, 4 cases.**
- `tests/acceptance/W2-105/w2_105_support.py` line 43: `BASE_COMMIT = "74d83913a86b"` predates W2-56's allow line, so the
  line reads as "added". Move it to `"dca333e7a55d"` (keep the 12-digit form the file uses). The base is meant to be "the last commit to change the file on `w2/integrate` before
  W2-105": that commit is now W2-56's, not DEC-664's. Make the text that says so true: the module docstring (line 16,
  "the commit of DEC-664's round"), the comment on line 43, and the README's line "The base ("before") is ... at
  `74d83913a86b`, the commit of DEC-664's round" (`tests/acceptance/W2-105/README.md`, near line 36), naming W2-56's round
  2 commit and what it added (`"gov launch:*": "allow"`). These three texts are W2-105's own; no other text changes.
- The four cases (from RESOLUTION.md section 5):
  `test_the_templates_source_is_its_base_less_the_two_install_rules`,
  `test_no_other_rule_of_the_templates_source_is_added_removed_or_changed`,
  `test_the_generated_rules_are_the_base_rules_less_the_two_install_rules`,
  `test_no_other_generated_rule_is_added_removed_or_changed`.
  Show each red on today's branch head first, then green after the change. Do not weaken any case: after the change each
  must still fail if one install rule were put back, or a rule other than the two were added, removed or changed
  (reason it through, or show it with a planted change in a copy under your `TMPDIR`, never in the tree).

**Fix 2: W1-38's file `tests/acceptance/W1-38/test_w1_38_test_folder_rule.py`, 2 opt-in cases.**
This file belongs to another ticket (W1-38). **You edit only the two expected-set constants named here, nothing else in it
and nothing else in W1-38's folder** (not its README, not its other files, not the cases' messages or docstrings), and you
say so in the commit message:
- `OTHER_SOURCE_RULES` (around line 66): add the member `("bash", "gov launch:*", "allow"),`.
- `OTHER_GENERATED_RULES` (around line 70): add the key/value `"allow": ["Bash(gov launch:*)"],`.
- The two cases they fix (opt-in, left out of the default run): `TestEveryOtherRuleStays::test_the_templates_source_gives_the_four_other_rules_and_nothing_else`
  and `TestEveryOtherRuleStays::test_the_four_other_deny_rules_are_still_generated_and_nothing_else`. The source case is
  already red on integrate today (W2-56 added the line without revising the constant); this fixes it on this branch.
- Their names and messages say "four" and "deny rules": leave them; the CTO routes that wording to the ticket that owns
  the file. Name it in your return as a discovery, with the line numbers.

Do **not** touch `template/**`, `src/**`, `.tickets/**`, any file outside the two folders above, or any other case.
If you find another red, re-run it alone, name it in your return, and do not fix it (a red you did not cause).

## Checks (scoped; through the heavy-job gate, DEC-1038 (4))

Run every pytest through the gate, with this tree's own code, the node that rulesync needs, and your `TMPDIR`
(`PYTHONUSERBASE=/home/usain/.local` as well if a planted `HOME` hides pytest or copier):

```
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src TMPDIR=<your TMPDIR> python3 -m pytest tests/acceptance/W2-105 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env GOV_TESTS_OPTIN=lifted,breadth PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src TMPDIR=<your TMPDIR> python3 -m pytest tests/acceptance/W1-38/test_w1_38_test_folder_rule.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs
```

- **Before the edit:** W2-105's folder 24 passed, 4 failed; W1-38's file with the opt-in 17 passed, 2 failed (the
  numbers RESOLUTION.md measured on an extracted copy; yours may differ, report what you see).
- **After:** W2-105's **28 cases green**; W1-38's file with `GOV_TESTS_OPTIN=lifted,breadth` **19 green**.
- Also run, once, the whole `tests/acceptance/W1-38/` folder with the opt-in on, to show nothing else there moved: no other
  folder, never the full suite (DEC-968). If the gate or the sandbox does not let you run a case, say which and why; never run it outside
  the gate. Run long commands in the background and wait by pid only (`tools/proc.sh`), never the Monitor tool, never a
  process-name match.
- Before you return: `git -C /home/usain/gov-os-worktrees/W2-105 status --porcelain` empty after your commit, and
  `git diff --stat HEAD~1 HEAD` showing exactly: `w2_105_support.py`, W2-105's `README.md`, and
  `test_w1_38_test_folder_rule.py` (two constants, a few lines).

## Commit (one commit, on `w2/W2-105` only; never merge, push, amend or rebase)

```
git commit -m "W2-105: the base commit of the install cases is W2-56's gov launch allow line (dca333e7a55d); W1-38's two opt-in expected sets hold it too" -m "<body: the six cases, why, the before and after counts; and the sentence: W1-38's file belongs to another ticket; only the two expected-set constants OTHER_SOURCE_RULES and OTHER_GENERATED_RULES changed, nothing else in it.>" \
  --trailer "Task: DAEO-zpdj" --trailer "Implements: DEC-966" --trailer "Role: independent-test-designer" \
  --trailer "Rewrite-Reason: W2-56 gov launch allow line (dca333e7a55d)" \
  --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" \
  -- tests/acceptance/W2-105/w2_105_support.py tests/acceptance/W2-105/README.md tests/acceptance/W1-38/test_w1_38_test_folder_rule.py
```

## Rules

- The guard's rules hold: no reads of secrets or of held-out material; never open `~/gov-os-eval` or a folder named
  `hidden` or `memory-verdict`; no installs; a refusal is taken, never routed round (a false one is worked round by an
  equivalent form, named in your return). Refused twice for the same call: stop and say so.
- Under `.gov-runtime/` write commit hashes as 12 digits; write none of the keywords `tools/keyword_warn.py` looks for
  (row W2-L423). Waits and stops by pid only.
- Scratch budget 30 GB and 2,000,000 files and folders outside the tracked tree; report `du -sh` and `du -s --inodes` of
  your `TMPDIR` in `evidence`; clean it.
- Estimate: 15 minutes, a few dollars. Past about 200k tokens, hand over and return PARTIAL.

## Return

The twelve fields first, as labelled lines at the start of their own lines (task, status, work_completed, files_changed,
evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action): step 0 and the
head commit of your commit first in `evidence`, the before and after counts in `tests`, the stale wording of W1-38's case
names in `discoveries`. Then a line `TESTS-READY` only if all of W2-105's 28 cases and W1-38's file are green; the CTO
writes the marker.

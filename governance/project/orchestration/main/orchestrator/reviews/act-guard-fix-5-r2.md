---
task: ACT-GUARD-FIX-5
type: review (ACT, round 2 of 2, DEC-1010)
reviewer: independent-auditor (fresh read-only session, round 2; not the ACT's author, not round 1's reviewer)
commit: f7b9ff50cbd4e2a6d7c54e6687b80b40d3215132   # main tree HEAD, w2/integrate, at review time
pack_sha256: none given; reviewer brief sha256 e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a
inputs_sha256:
  manifest.json: ef9078eb4ae59abd01a19e22feb1f8c2e9ddd25d60d13ab1d2e00ef44b1380fd
  before/repo/.claude/hooks/bash_writes.py: bb246a21735e70ad0b3a8213102a942bfcf1688838977aae618052c2f1f54732
  after/repo/.claude/hooks/bash_writes.py: e55c48a3bec603c44329e85b87d13f817e4af830c6ef6bab47f6758f20c5bfd7
  apply.sh: 4449e17ad7e49101dc6e9fc634b47e94d968e3df34e8052519ab7607e531cf12
  rehearsal.log: ec894ae7d077ec1aabf8cde7d1accee26ebbba02439d49d3e1ac1f9399be1226
decisions: [DEC-953, DEC-958, DEC-1050, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-820, DEC-1137, DEC-137]
status: STOPPED under AR-6 / DEC-1137. The live guard refused my probe call twice, so my own through-the-hook runs did not happen. This record holds what I verified, plus one blocking finding that rests on a code trace and has not been run.
---

# ACT-GUARD-FIX-5, review round 2

**Classification:** 1 blocking finding (F1: in scope, ordinary work yes, fails open). It rests on a code trace I could
not run (see "The refusal"). 4 recorded rows: F2 and F3 (out of scope, fail open), F4 and F5 (other).
**Recommendation:** NOT READY as submitted. This is round 2 of 2, so it goes to the owner once, with options (end of
this record). The cheapest step is to run the four reversal cases under F1: if they are refused after the apply, F1
is reversed and the other checks stand.

## The refusal (AR-6, DEC-1137)
The live hook refused my probe call twice (rule "reads files whose names another command gives at run time, from a
listing whose start the guard cannot place", DEC-820 (c), (d)). The call wrote a case-generator file and ran it in the
same call. My second try dropped the one listing the cases did not need, and it was refused the same way. I stopped
there. I did not respell the call or move it to another tool, and I ran no further hook probes. Everything below on
behaviour comes from reading the code and the rehearsal log, apart from the apply/verify/undo run I made before the
refusal. My bed (`/tmp/claude-1000/rv-gf5r2-wxxw96`) has been removed. The main tree's status is as I found it: one
untracked file, `governance/project/orchestration/packages/P1-W2-88-NC-1.md`, which is not mine.

## What I verified and found sound
- **Bundle integrity (check 1).** The manifest's sha256 is `ef9078eb…`, as expected. The bundle holds exactly
  `apply.sh`, `list.txt`, `manifest.json`, `rehearsal.log`, `followup-tests.diff`, `before/…/bash_writes.py` and
  `after/…/bash_writes.py`. It has no `__pycache__` and no bytecode (round 1's F2 is closed). Every file hashes as
  listed. The before copy equals HEAD's blob and the live file (`bb246a21…`). The after copy equals the draft. `touched`
  names the one file. `apply.sh` changes nothing in HOME or crontab. Path rule: no absolute path and no
  `~`/`$HOME`. Its one `cd` is the subshell that finds its own folder. The checks work from the current folder and
  write their temp folder under TMPDIR.
- **Apply, verify, undo in a fresh clone (checks 1 and 2).** I cloned `w2/integrate` at f7b9ff50c. `check` gave "state
  before" (exit 0). `verify` before the apply exited 3. `apply` exited 0, the mode stayed 644 and the sha256 became
  `e55c48a3bec6`. `verify` then exited 0. `git status` showed only `.claude/hooks/bash_writes.py`. `undo` exited 0, the
  file was byte-identical to the before copy, and the clone's status was clean.
- **The rehearsal (check 3).** The log is the output of `drafts/act-guard-fix-5/rehearse.sh`: step for step, its
  labels and messages are that script's and `apply.sh`'s. It ends `52 ok, 0 failed` / `failures: 0`, and its sha256
  matches the manifest. It covers undo byte for byte, the refusals of a changed file and of a link (E1-E7), and the
  follow-up tests: 31 red before and 67 green after, then the hook's suites at 561 passed and 1 skipped.
- **The checks (check 4).** All four use `python3 -B -I` (round 1's F5 is closed). Check 4 runs 20 commands through
  `pretooluse.py` itself as an engineer (round 1's F3 is closed). Rehearsal B2/B9 prints the expected exits:
  `0,1,1,1` before and `0,0,0,0` after. I did not re-run them.
- **The class (check 5).** It is a `.claude/hooks/**` guard-code change that alters a control: **b**, as claimed.
- **The `_kind` change.** By reading `_shell_kind`, it never reads as data a heredoc the old rule read as shell. A
  program is read only from a `-…c…` cluster, which the old rule also took for data. The floor keeps "`-s` present" and
  "every word starts with `-`". Option values, the stdin words and unknown options are read as shell, which is
  stricter. This agrees with round 1's 10.5 M-list run and with check 3's 2,000 seeded lists.
- **Round 1's F1 cases and W2-42a (KPI 2).** The `body()` change judges a quoted or expansion-free shell body as
  commands, and judges the command substitutions of a shell body that has expansions. The held-body loop now
  registers a body that a shell reader writes to a file. Together these cover the forms of round 1's F1. Rehearsal C
  shows all 13 such cases refused after, and H shows W2-42a's 15 shell spellings refused after with the 4 data controls
  allowed. The W2-42a ref has moved since the rehearsal (now `5d58123b1`; the package says `a4afc4166136`), but the
  fixture is byte-identical (`git diff` is empty; sha256 `44c4afe1…`). See F5.
- **Fails closed on an exception (KPI 3).** The new code raises nothing of its own. Any exception other than the scan's
  own "cannot read" signal reaches `pretooluse.py`'s top-level handler, which logs `deny/error` and exits 2. The
  "cannot read" signal is the exception to this, and it is F1.
- **Round 1's F6** (stale head) is closed: head f7b9ff50c.

## Findings

### F1 (check 6, blocking): a comment with an apostrophe in a shell's heredoc body lets the whole call's writes through
**What was done:** as an engineer, one Bash call runs `bash -euo pipefail <<'EOF'`. Its body holds an ordinary comment
line with an apostrophe (`# don't overwrite the fixture`) and harmless commands. After the heredoc, the same call
writes into `tests/acceptance/` (`echo x > tests/acceptance/X/zz.py`, a `cp` there, or a `python3 -c` that opens a file
there).
**What happens (by code trace, not run):**
- **Before the ACT**, a shell with options read its body as data, so the body was never tokenised. The scan read the
  rest of the call, found the write and refused it (rule 1).
- **After the ACT**, the body is read as a shell's commands. The scan keeps comment text when it tokenises, so the
  lone apostrophe is an unclosed quote. The scan signals "cannot read" for the **whole call**. The hook then falls back
  to the product's parser, which tokenises the whole call the same way, finds the same unclosed quote and returns
  "unresolvable". Under G-1 (DEC-1050 (12)), rule 1 drops an unresolvable target, so the call is **allowed**.
- The same holds for an auditor's write outside its records (rule 5) and for the 2b-write and 2d rules. It holds for
  every options spelling (`-o`, `-O`, `+o`, `--rcfile`, `-`, `/dev/stdin`) and for plain `bash <<EOF` with an unquoted
  body that has no expansion (before, that body was only an unresolvable note and the rest of the call was judged).
**What should happen:** a call refused before stays refused (the ACT's "stricter only" claim and the CTO's check
(1)). A body the new reading cannot tokenise should leave the call judged as it was before the ACT, not unjudged.
None of the rehearsal's 45 cases, 1,280-call matrix, 720 replayed calls, 20 check-4 commands or 67 follow-up tests has
a body with an unbalanced quote character in a comment, so none could see this.
**Reversal evidence:** run these four calls through `before/` and `after/` copies of the hook, as an engineer on
DAEO-03ub with the pinned interpreter. If each is **refused after the apply**, F1 is wrong.
(a) `bash -euo pipefail <<'EOF'` / `# don't overwrite` / `echo hi` / `EOF` / `echo x > tests/acceptance/X/zz.py`
(b) the same with `bash -o pipefail <<EOF` (unquoted)
(c) the same with plain `bash <<EOF` (unquoted)
(d) (a) with the last line replaced by `python3 -c "open('tests/acceptance/X/zz.py','w').write('x')"`
My trace predicts deny before and allow after for all four.
- Ordinary work: yes, because `bash -euo pipefail <<'EOF'` is the usual way agents write multi-line shell, comments
  with contractions ("don't", "it's", "the CTO's") are common in those bodies, and a call that also copies or writes
  into the tests (an engineer) or outside the records (an auditor) is the honest mistake rules 1 and 5 exist for.
- Consequence: fails open

### F2 (row, out of scope, existed before the ACT): an apostrophe in a top-level comment leaves any Bash call unjudged
**What was done:** any Bash call whose own text (not a heredoc body) holds a comment with a lone apostrophe, such as
`echo x > tests/acceptance/X/zz.py  # don't`. **What happens (trace):** the same chain as F1, before and after the ACT
alike: the scan cannot read the call, the parser returns unresolvable and rule 1 lets the write through. The same is
true of a quoted body read by plain `bash` before this ACT. **What should happen:** a comment's text is not tokenised.
The ACT does not change this, so it is not a round. It is a defect for the CTO's list (fixing it would also remove
F1's trigger). **Reversal:** the live hook refuses that call as an engineer.
- Ordinary work: yes, because trailing comments with contractions are common in agents' commands.
- Consequence: fails open

### F3 (row, out of scope): the P1 defect stays open for a body with such a comment
**What was done:** `bash -euo pipefail <<'EOF'` with a comment holding an apostrophe, and a write into the tests
inside the body. **What happens (trace):** it was allowed before, and after the apply it is still allowed, now for
F1's reason. It is not one of W2-42a's 15 spellings, so KPI 2 passes. **Reversal:** the after hook refuses it.
- Ordinary work: yes, for F1's reason.
- Consequence: fails open

### F4 (row, check 4): the checks do not test the interpreter the hook runs, and leave a folder behind
Check 4 runs the hook with `python3` from PATH and the tree's `src/` parser, not the pinned interpreter that
`.claude/settings.json` runs. Each run also leaves a temp folder that it never removes. No check or follow-up test
carries an unbalanced quote in a body (see F1). **Reversal:** the operator's G3 runs the checks with the pinned
interpreter.
- Ordinary work: yes, because every check run does this.
- Consequence: other

### F5 (row, check 3): the package names a stale W2-42a ref
The package says `refs/heads/w2/W2-42a` is at `a4afc4166136`. It is now `5d58123b1`. The fixture is byte-identical,
so D1b still holds. **Reversal:** a fixture diff between the two refs is non-empty.
- Ordinary work: yes, because refs move during review.
- Consequence: other

## Options for the owner (round 2 was the last, DEC-1010)
1. **Check F1 first (minutes).** The CTO runs the four reversal cases through the two hook copies. If all four are
   refused after the apply, F1 is reversed. A narrow independent check of that run then passes the review, and F2 to F5
   remain rows.
2. **Fix and rebuild (about an hour, plus a narrow check).** Make the new body reading additive. When a shell body
   cannot be tokenised, record it as unresolvable, as before, and keep judging the rest of the call; do not give up on
   the call. Add F1's four cases to the case file and to check 4, then rebuild the bundle (new manifest digits).
3. **Apply as is and accept F1 as a row.** The landing check backstops a commit to the tests without
   `Role: independent-test-designer` (G-1). The cost is that the ACT's "stricter only" claim is false for the F1
   calls.

```verdict
{"kpis": [{"kpi": "check 1", "verdict": "pass", "findings": []}, {"kpi": "check 2", "verdict": "pass", "findings": []}, {"kpi": "check 3", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 4", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 5", "verdict": "pass", "findings": []}, {"kpi": "check 6", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}],
 "manifest_sha256": "ef9078eb4ae59abd01a19e22feb1f8c2e9ddd25d60d13ab1d2e00ef44b1380fd",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session (round 2); not the author, not round 1's reviewer",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T17:27:29+00:00",
 "replay_refused": []}
```

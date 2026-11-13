---
type: probe
task: DAEO-03ub
reviewer_session: a84974e0-ecb1-4669-9d8d-39ecfbbd78cd
implementer_session: 5e9978c7-b620-45ea-8c22-c2ad2d95acc4
reviewer_wrote_nothing: true
commissioned_by: orchestrator (W2-42a ticket lead)
judged_by: orchestrator (W2-42a ticket lead)
judgement: fail
probed_commit: c1ee147bd61383cd29fcfd1998d2d2d514caceb8
decisions_applied: [DEC-1174, DEC-1164, DEC-409, DEC-1010, DEC-958, DEC-1028]
---

# Probe record: W2-42a (DAEO-03ub), the narrow independent check of the apostrophe fix (DEC-1164 (18), DEC-1174 (1))

## The lead's judgement

- **Who probed.** A fresh read-only independent auditor (Opus, high), launched by the ticket lead with
  `launch_worker.sh`; brief `.gov-runtime/scratch/lead/briefs/a4.md` (JUDGEMENT.md word for word); log
  `.gov-runtime/scratch/lead/log/a4.json`. It judged only the change bb464f2ca..c1ee147bd (the engineer's
  f16075e43, 669d87c91, c1ee147bd) against the cases' brief (a) to (d), the CTO's scope P-03ub-APOS-1 (A) and
  DEC-409. Its tripwire shows no change in W2-42a's trees; `git status` empty.
- **At this head:** `gov accept W2-42a` 803 passed, 0 failed, 2 skipped (the strict xfails); the scoped set
  (tests/unit/guard, tests/acceptance/W2-42a, tests/unit/hooks, DEC-409's cases in tests/unit/pause,
  tests/unit/containment/test_w1_50_freeze_flag.py, tests/acceptance/W1-50, W1-28, W2-16) 1809 passed, 2 xfailed,
  0 failed; with the opt-in tiers collected (GOV_TESTS_OPTIN=lifted,breadth) 3633 passed, 2 xfailed, 6 failed, the
  6 being W2-33's fixture copy (`tests/acceptance/W2-33/w2_33_support.py:376`, FileNotFoundError on the copied
  source's `template/governance/kernel/roles`), outside the guard and this change.
- **Not READY, by code.** The verdict block passes A, B, C, D, SCOPE and DEC409, and fails FC on F1: a `#` after a
  blank inside an unquoted `${…}` is taken for a comment and the write after it is dropped
  (`v='a # b'; echo ${v%% #*} > tests/acceptance/X/zz.py`: the base denies, the head allows, real bash writes);
  in scope, ordinary work yes, fails open. F2 (fails open, ordinary work no), F3, F4 and F5 (refuse work) are rows
  for triage; F6 (`bash <<< "…"`, pre-existing on the base) is out of scope.
- **Judgement: fail.** Returned to the CTO as a package (the triage and the options are in the lead's return).

## The reviewer's record (as returned)

The narrow check fails on fail-closed (FC): the change lets through a write that the base refuses. Everything else holds.

The sandbox check passed: (a) the write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-03ub` failed with "Read-only file system", and (b) `git hash-object -w --stdin` and `git update-index --refresh` both worked. The `ps` check found no ollama or llama-server process. The head is c1ee147bd61383cd29fcfd1998d2d2d514caceb8, and `git status --porcelain` was empty when I finished.

task: DAEO-03ub
decisions: DEC-1174, DEC-1164, DEC-409, DEC-1028, DEC-958, DEC-801, DEC-808, DEC-1010, DEC-1014
status: done. A, B, C, D, SCOPE and DEC409 pass; FC fails on F1.
work_completed: Read the change bb464f2ca..c1ee147bd (three engineer commits) and the code around it. Read the lead's logs instead of re-running them. Ran about 230 commands through `decide()`, `_extract_bash_write_targets()` and `lift_refusal()` on the head and on the base (exported with `git archive bb464f2ca src`), in a stand-in project under $TMPDIR. Ran every form that changed toward allowed in real bash, in $TMPDIR, to see whether it really writes T.
files_changed: none
evidence: All probe scripts and outputs are under $TMPDIR/aud: `probe.py`, `cmp.py`, `cases1-6.py` with results in `r1.txt`–`r3.txt`, and real-bash runs in `realbash.sh` / `realbash2.sh`. Lead logs: `apos-accept.log` (803 passed, 0 failed), `apos-scoped.log` (1809 passed, 2 xfailed, 0 failed).
tests: No pytest run; I took the lead's runs at this head. The opt-in run `apos-scoped-optin.log` has 6 failures, all in W1-50/W1-28 fixture-copy tests (FileNotFoundError on `source/template/governance/kernel/roles` in `w2_33_support.copy_folder`). They do not touch the guard; see discoveries.
discoveries: (1) A pre-existing gap, the same on base and head: `bash <<< "echo x > T"` is allowed, and real bash writes T. The scan reads the second and third `<` of `<<<` as a heredoc operator, which makes the command unreadable, and the line parser does not read a here-string as commands. Out of the narrow scope (F6). (2) In the product, a write made by a `python3 - <<'EOF'` body is not a write target on base or head; after departure 1, the same write made by `python3 -c` is. (3) The 6 opt-in failures are an environment or fixture problem outside this change.
risks: The live hook is to copy this parser (DEC-1174 (1)), so F1 would carry into the hook too.
lessons: The engineer's 211,200-command comparison only generated comment, quote and write lines after shell heads. It never put a `#` after a blank inside `${…}`, so it could not find F1.
proposed_decisions: The CTO accepts or rejects departure 1 by name: `python3 -c` writes become write targets in every adopted repository. Plain read-only one-liners stay free, but one that writes to /tmp, or uses `exec(open(...).read())` or `runpy`, is now refused.
unresolved: none
recommended_next_action: Classification: 1 finding in scope, ordinary work yes, fails open (F1); 5 recorded rows (F2–F6), none blocking. Recommendation: the CTO routes F1 to the engineer as a narrow fix (a `#` inside `${…}` never starts a comment), with F1's forms added as cases, then a narrow check of that fix only. The CTO may count this as beyond DEC-1010's two-round limit. In that case it goes to the owner once, with three options: fix F1 now; land the fix without the comment drop on the write side; or land as is and record F1 as a known fail-open.

**F1 (FC): a `#` after a blank inside `${…}` loses the write**
- **What:** A `#` after a blank inside an unquoted `${…}` expansion is taken for a comment. The head then drops the rest of the line, including a write that comes after it. Bash does not treat that `#` as a comment and runs the write. The base kept that text and refused the call.
  - `v='a # b'; echo ${v%% #*} > tests/acceptance/X/zz.py`: base denies (write to T), head allows, real bash writes T.
  - The same holds for `echo ${x:- #a}; echo x > T`, `v='a #b'; echo ${v/ #/} > T`, `while read -r l; do echo ${l%% #*}; done < f > T`, and `while read -r l; do k=${l%% #*}; echo $k >> T; done < f`.
  - It also holds inside a `bash <<'EOF'` body, inside a `bash -c '…'` string, and for a write placed before the `${…}`: `echo ${X:- #} > src/ok.py; cp x.py T`.
  - The forms the brief names, `${#v}`, `${v#a}` and `$#`, are refused correctly.
  - The lift check is not affected, because it always reads the command as before first.
- **Where:** `src/gov/guard/bash_writes.py:206-214`. The comment test has no `${…}` context, and the comment text is now dropped where the base kept it.
- **How found:** `python3 $TMPDIR/aud/cmp.py cases3.json` and `cases4.json` (cases pe1–pe3, pe6-body, loop, while, while2, patsub, default-src, bc-pe), then `bash $TMPDIR/aud/realbash.sh` and `realbash2.sh` (WROTE on each).
- **What would reverse it:** the head refusing those commands for T, or real bash not writing T for them.
- Ordinary work: yes, because `${line%% #*}` is the usual way to strip a trailing ` #` comment, and an honest agent can leave it unquoted ahead of a redirect on the same line, for example in a `while read` loop that writes a file.
- Consequence: fails open
- Scope: in. This is the change's own fail-closed requirement and the ticket's failure line 1: a write the base catches is missed.

**F2 (FC): a comment inside backticks can hide a write**
- **What:** A comment inside backticks runs to the end of the line, past the closing backtick. On one line this makes the command unreadable, so it is refused. But a later backtick substitution that spans a newline balances the count, and then a write on the first line is lost. Example: `` echo `date #x` > T; echo `pwd<newline>` ``: base denies, head allows, real bash writes T.
- **Where:** `src/gov/guard/bash_writes.py:206`, in the backtick context.
- **How found:** cases bt3 and bt4 in `cases2.json`, then `realbash.sh`.
- **What would reverse it:** the head refusing bt3 and bt4.
- Ordinary work: no, because it needs a backtick substitution that spans a newline, placed after a commented backtick on the write's line. That is a deliberate construction, so it is a Wave 3 row.
- Consequence: fails open
- Scope: in

**F3 (SCOPE): departure 1 refuses some ordinary Python one-liners**
- **What:** `python3 -c` writes are now write targets. Case (b) needs this, since without it the reversal call would become free. But beyond (A)'s two named fixes, it refuses one-liners the base allowed:
  - `python3 -c "open('/tmp/x.txt','w').write('x')"` and the same into $TMPDIR, now refused like the matching shell redirect;
  - `python3 -c "exec(open('x.py').read())"` and `runpy.run_path('x.py')`, now unresolvable;
  - code with a syntax error, now unresolvable.

  The 13 read-only one-liners I tried stay free (json, subprocess, yaml, pathlib, listdir, os.system('ls'), sqlite and others).
- **Where:** `src/gov/guard/bash_writes.py:1499-1506`
- **How found:** cases py-ok1 to py-ok16, py-w-*, py-tmpdir in `cases3.json` and `cases5.json`.
- **What would reverse it:** the CTO deciding that the product enforces `python3 -c` writes as it does shell writes.
- Ordinary work: yes, because agents often write a scratch file to /tmp with `python3 -c`.
- Consequence: other (refuses work; fails closed)
- Scope: in

**F4 (FC): any `#…quote` on a line now refuses commands the scan cannot read**
- **What:** When the scan cannot read a command, the head now refuses it in both the write reading and the lift check if any line has a `#` after a blank followed later by a quote. That includes a `#` inside a quoted string. Here-strings always fall into this case, because of the `<<<` misreading in discoveries (1). So these were allowed on base and are refused on head with "the command cannot be read":
  - `grep -c b <<< "a # b"`
  - `wc -w <<< "one # two"`
  - `jq -r '.x' <<< '{"x": "a # b"}'`
- **Where:** `src/gov/guard/bash_writes.py:86` (the comment-with-quote pattern), and where decide.py uses it at `src/gov/guard/decide.py:413` and `:1006`.
- **How found:** hs-ok1 to hs-ok3 in `cases3.json`.
- **What would reverse it:** the head allowing hs-ok1 to hs-ok3.
- Ordinary work: yes, because a here-string holding ` #` is plausible.
- Consequence: other (refuses work)
- Scope: in

**F5 (FC): a one-line comment inside backticks is now refused**
- **What:** `` x=`git rev-parse HEAD #comment`; echo $x `` was allowed on base and is refused on head as "cannot be read". The lift check now runs the scan even when its first reading is clean, and the scan finds the backtick still open.
- **Where:** `src/gov/guard/decide.py:1001-1004`
- **How found:** case bt-ok in `cases2.json`. Real bash runs it with no write.
- **What would reverse it:** the head allowing bt-ok.
- Ordinary work: no, because comments inside backticks are rare.
- Consequence: other
- Scope: in

**F6 (out of scope): here-string fed to `bash` is not read (pre-existing)**
- **What:** `bash <<< "echo x > T"` is allowed on both base and head, and real bash writes T.
- **Where:** `src/gov/guard/bash_writes.py:215`
- **How found:** hs-plain in `cases3.json`, then `realbash.sh`.
- **What would reverse it:** the base refusing it.
- Ordinary work: yes, because feeding a short script to `bash` through `<<<` is plausible.
- Consequence: fails open
- Scope: out. Pre-existing; not caused by this change and outside the narrow check. It belongs in a Wave 3 row or a ticket the owner decides.

**What I probed and found sound**
- **A:** all 8 shell forms from the brief, quoted and unquoted delimiter, are allowed through `decide()` on the head.
- **B and C:** every form is refused, for T or as unreadable: writes after the heredoc (redirect, `cp`, `python3 -c`), writes inside the body, and the edges `a#b`, `${#v}`, `$#`, `"a # b"`, `'it # s'`, `\#` and `\ #`.
- **D:** an unclosed quote is refused, with or without a comment, where the base allowed the commented form.
- **DEC-409:** the first reading is the base reading unchanged, so no form the base found can be lost. The probes agree: a lift form after, inside, or in the body of a comment, and in `$( )`, `bash -c`, nested heredocs, pipes, CRLF and backslash-newline cases, is refused on the head. Base let `lift-two` through; the head refuses it.
- **Departures 2–4:** keeping the comment's words is sound (a comment holding the form is refused). Departure 3 (data body with an odd apostrophe plus a top-level apostrophe comment) and departure 4 (a shell heredoc inside `$( )`) only add refusals; both fail closed.
- **SCOPE:** Python and data bodies are read as before: apostrophes in them stay refused, and no data body became commands or a write (data1, data2, nest1, py1, py2, tk, data-commit).

```verdict
{"kpis": [{"kpi": "A", "verdict": "pass", "findings": []}, {"kpi": "B", "verdict": "pass", "findings": []}, {"kpi": "C", "verdict": "pass", "findings": []}, {"kpi": "D", "verdict": "pass", "findings": []}, {"kpi": "SCOPE", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "DEC409", "verdict": "pass", "findings": []}, {"kpi": "FC", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F6", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```

Session id: a84974e0-ecb1-4669-9d8d-39ecfbbd78cd. Head probed: w2/W2-42a at c1ee147bd61383cd29fcfd1998d2d2d514caceb8.

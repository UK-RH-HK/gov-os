---
type: probe
task: DAEO-03ub
reviewer_session: 1e12d42f-b828-4265-8523-b54c8113f99b
implementer_session: d10c1d58-56f7-49d8-8bd5-d20929c6488f
test_designer_session: 8bfdec80-6a0b-4683-822f-07ef2fe3fec6
reviewer_wrote_nothing: true
commissioned_by: "orchestrator (W2-42a ticket lead)"
judged_by: "orchestrator (W2-42a ticket lead)"
judgement: pass
probed_commit: a62cd8c11439f35c3cb885087823d257d564fbda
base_commit: 692bc41bd177
decisions_applied: [DEC-1174, DEC-1164, DEC-1154, DEC-409, DEC-1010, DEC-958, DEC-1028, DEC-801, DEC-802, DEC-808]
---

# Probe record: W2-42a (DAEO-03ub), the narrow independent check of the F1/F4 fix (DEC-1164 (18), DEC-1174 (1), APOS-3/APOS-4)

## The lead's judgement

- **What was checked.** Only the change 692bc41bd..a62cd8c11: the test designer's merge c461d79de
  (tests/acceptance/W2-42a/test_w2_42a_apostrophe_2.py, 80 cases, red 28 on 692bc41bd: 21 F1 fail-opens, 7 F4
  refusals) and the engineer's fa77bb331, 1388fcec6, 07fb14799, a62cd8c11 (src/gov/guard/bash_writes.py,
  tests/unit/guard/test_w2_42a_apos2.py, docs/changes/W2-42a-evidence.md; decide.py untouched), against the CTO's
  decisions P-03ub-APOS-3 (1) (F1: a `#` inside `${…}` never starts a comment) and P-03ub-APOS-4 (a) (F4: a
  here-string holding ` #` is read; departure 1 accepted by name), DEC-409, and fail-closed. This is the CTO's own P2
  round (DEC-1164 (18)) landed on a narrow independent check (DEC-1154); it is not a review round under DEC-1010.
- **Who probed.** A fresh read-only independent auditor (Opus, high), launched by the ticket lead with
  `launch_worker.sh`; brief `.gov-runtime/scratch/lead/r4/a5.md` (JUDGEMENT.md word for word); log
  `.gov-runtime/scratch/lead/log/a5.json`. Its tripwire shows no change in W2-42a's tree; `git status` empty.
- **At this head:** `gov accept W2-42a` 883 passed, 0 failed, 2 skipped (the strict xfails); the scoped set with the
  opt-in tiers collected (GOV_TESTS_OPTIN=lifted,breadth: tests/unit/guard, tests/acceptance/W2-42a, tests/unit/hooks,
  DEC-409's cases in tests/unit/pause, tests/unit/containment/test_w1_50_freeze_flag.py, tests/acceptance/W1-50,
  W1-28, W2-16) 3751 passed, 2 xfailed, 6 failed, the 6 being W2-33's fixture copy
  (`tests/acceptance/W2-33/w2_33_support.py:376`, FileNotFoundError on the copied source's
  `template/governance/kernel/roles`), the same 6 as on 692bc41bd, outside the guard and this change.
- **READY, by code.** The verdict block passes HASH, HSTR, DEP1, DEC409 and FC. No finding is in scope, ordinary work
  yes and fails open or loses work.
- **Rows (recorded, not a round):**
  - R1 (FC, in scope, ordinary work no, fails open): `$${` opens a `${` at the second `$`, so two apostrophe comments
    can pair over a write until a later bare `}`.
  - R2 (DEC409, in scope, ordinary work no, fails open): the same `$${` misread hides the lift form.
  - R4 (out of scope, older than this change, ordinary work no, fails open): a backslash-newline between `$` and `{`.
  - R5 (out of scope, older than this change, ordinary work no, fails open): `<<` inside `${…}` on a prefix
    assignment.
  - R3 (out of scope, older than this change, ordinary work yes, fails open): the line parser splits a command at
    `<<`/`<<<` (decide.py:583), so a write argument after a here-string (`tee <<< "…" file`) is missed. It does not
    block this change; it goes to the CTO to decide (ride along under DEC-802 or a Wave 3 row).
  - Carried from the previous check (ordinary work no): F2 (a commented backtick plus a multi-line backtick hides a
    write; fails open) and F5 (a one-line backtick comment refused).
- **Judgement: pass.**

## The reviewer's record (as returned)

**Sandbox check (step 0):** passed.
- (a) The `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-03ub','w')…"` write failed with `OSError: [Errno 30] Read-only file system`, and no file exists.
- (b) `git hash-object -w --stdin` worked (1ae28402a…) and so did `git update-index --refresh` (both exit 0).
- **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.

task: DAEO-03ub (W2-42a): the narrow independent check of the F1/F4 fix, 692bc41bd..a62cd8c11 (DEC-1164 (18), DEC-1174 (1), APOS-3/APOS-4)

status: done. HASH, HSTR, DEP1, DEC409 and FC pass. Nothing blocks. There are 5 recorded rows: 2 are in scope with ordinary work no, 3 are out of scope because the defect predates this change.

work_completed:
- Identity: `git -C /home/usain/gov-os-worktrees/W2-42a rev-parse HEAD` = a62cd8c11439f35c3cb885087823d257d564fbda.
- Read the diff of `src/gov/guard/bash_writes.py` (`heredocs` with `${` tracking and `legacy`, `<<<` as a here-string, `_check_here_strings`, `comment_spans`, `Judgement.loose`, `body()` for unquoted shell bodies, `judge()`'s second readings). Read how decide.py consumes them: `_extract_bash_write_targets` at decide.py:406 uses only `targets()`; `_lift_in`/`lift_refusal` at decide.py:988–1056.
- Compared `decide()` on the base (`git archive 692bc41bd src`) and the head, one command at a time:
  - about 100 hand-written forms;
  - two generated sets of 115,200 and 64,512 commands (fragments: `${…}`, comments, here-strings, heredocs, writes, `gov pause --off`, `.env` reads, under 6 wrappers each).
- Ran in real bash 5.2.21 under $TMPDIR, with a stand-in `gov`, every command that moved toward allow (5,108 + 1,544) and every command whose lift-form finding was lost (1,159).

files_changed: none (`git status --porcelain` is empty; scripts and outputs are only under $TMPDIR/aud)

evidence:
- Scripts in $TMPDIR/aud: `probe.py`, `cmp.py`, `diff.py`, `realbash.py`, case files `c1.py`–`c6.py`, generators `gen.py`/`gen2.py`.
- Results: `r1.json`, `r2.json`, `rb_tow.json`, `rb_tow2.json`, `rb_lift.json`, `rb_c3.json`, `rb_c5.json`, `rb_c6.json`.
- Generated set 1 (115,200 commands): 5,108 moved toward allow. 28 of them write T or run the lift form in real bash. All 28 fall in rows R1, R2 and R5.
- Generated set 2 (64,512 commands): 1,544 moved toward allow. 15 write T, all in row R3. No lift form was lost to free.

tests: I ran no pytest, because the role re-runs nothing the lead ran. I relied on the lead's logs:
- `apos2-accept.log`: outcome pass, 883 passed, 0 failed, 2 skipped.
- `apos2-scoped.log`: 3751 passed, 2 xfailed, 6 failed. The 6 are all W2-33's `copy_folder` FileNotFoundError in the W1-50/W1-28 fixture tests, and do not touch the guard.
- The DEC-409 suites (tests/unit/pause, tests/unit/containment/test_w1_50_freeze_flag.py, tests/unit/guard, W1-50, W1-28) are inside that scoped set.
- No exclusion applied, since I ran no pytest.

discoveries:
- **Claim 1 is wrong for `$${`.** Bash reads `$$` and then a literal `{`; real bash closes `${v:-$${}` at its first `}`. The head opens a `${` there (rows R1 and R2).
- **Claim 5 does not hold over the change in general.** Commands that moved toward allow and do write T in real bash exist (R1, R3, R5). In R3 and R5 the head allows exactly what the base already allowed without the comment.
- **Claim 4 is sound.** `bash <<EOF` / `# note $(touch T)` / `EOF` is allowed on the base and denied at the head, and real bash writes T.
- **Bash 5.2 also treats `'` as a quote inside `"${v:-…}"`.** `echo "${msg:-it's done}"` is a syntax error in bash, so the head refusing it loses no work.
- **The engineer's 136,925-command comparison** never combined `$${` with a later bare `}`, nor a write argument placed after a here-string.

risks:
- R3 (`tee <<< "…" file`, and the same shape as `tee -a`, `cp`, …) is a fail-open that predates this change, and an honest agent can hit it. This change routes more here-string commands to the line parser that has it.
- The live hook is to copy this parser (DEC-1174 (1)).

lessons: I generated the counterexamples to cover two things the engineer's corpus lacked: a `}` that closes a misread `${` much later, and arguments placed after a redirect. All three fail-open classes came from these two.

proposed_decisions: none from me. For the CTO: whether R3 (the line parser splitting a command at `<<`/`<<<`, decide.py:583) rides along in this resume under DEC-802 or lands as a row.

unresolved: none

recommended_next_action: Classification: 0 findings in scope that are reachable in ordinary work and fail open or lose work. There are 5 recorded rows:
- R1 and R2 are in scope, ordinary work no, fails open.
- R3 is out of scope, ordinary work yes, fails open (it predates this change).
- R4 and R5 are out of scope, ordinary work no, fails open (they predate this change).

Recommendation: land the change. Record R1, R2, R4 and R5 as Wave 3 rows. The CTO decides on R3, a one-token fix in `_line_write_targets`: treat `<<`/`<<<` like `<` and skip its word.

---

**R1 (FC): `$${` hides a write between two comment apostrophes.** In scope.
- What happened: `echo $${v # it's` / `touch tests/acceptance/X/zz.py # don't` / `find . -name x -exec ls {} +`. The base denies it (target T). The head allows it with no target. Real bash writes T.
- It should be denied, as on the base.
- Same at the head: `{ echo $${v` / `# it's` / `touch T # it's` / `}`, and `echo ${v:-$${}` / `# it's` / `touch T # it's` / `}`.
- Where: bash_writes.py:196 and :137 open `${` at the second `$` of `$$`. The comments up to the next bare `}` are then not dropped, and the tokenizer pairs their apostrophes over the write.
- How found: generated set 1 (`diff.py g1.json r1.json`, then `realbash.py r1.json rb_tow.json toward`); narrowed in `c3.py`.
- Would reverse it: an ordinary command shape with `$$` directly followed by `{` and no `}` in that word.
- Ordinary work: no, because it needs `$$` directly before an unclosed `{`, an apostrophe comment before the write and another on the write's line so that they pair, and a bare `}` later. That is a deliberate construction.
- Consequence: fails open
- scope: in

**R2 (DEC409): the same `$${` misread hides the lift form.** In scope.
- What happened: `{ echo $${v` / `# it's` / `gov pause --off # it's` / `}`. The base refuses it with the lift form. The head allows it. Real bash runs `gov pause --off` (the stand-in recorded it).
- The other 23 commands that lost their lift-form finding are unclosed brace groups, and real bash runs nothing of them.
- Where: bash_writes.py:196. `comment_spans` returns no spans, so `_lift_in` at decide.py:1009 returns False.
- How found: `realbash.py r1.json rb_lift.json lift`.
- Would reverse it: as for R1.
- Ordinary work: no, because, as in R1, it needs a deliberate construction around the lift form.
- Consequence: fails open
- scope: in

**R3 (HSTR): a write argument placed after a here-string is not seen.** Out of scope: this change did not cause it.
- What happened: `tee <<< x tests/acceptance/X/zz.py` and `tee -a <<< x T` are allowed on the base and at the head, and real bash writes T.
- What this change moved: the F4 variants `tee <<< "a # b" T` and `tee /dev/null <<< "a # it's" T` went from refused (unreadable) to allowed. Likewise `tee /dev/null <<< "a # it's" cat $HOME/.ssh/id_rsa` is now allowed, and tee would overwrite that key.
- It should be denied.
- `sort <<< x -o T` and `dd <<< x of=T` became denied at the head (better).
- Where: decide.py:583. The line parser splits a command at the `<<<` token, so the words after `<<< word` become a new command. parser_text at bash_writes.py:440 passes `<<<` through unchanged.
- How found: generated set 2 (`realbash.py r2.json rb_tow2.json toward`); `c4.py`.
- Would reverse it: showing that the line parser reads words after `<<<` as arguments of the same command.
- Ordinary work: yes, because bash takes a redirect anywhere in a command, and `tee -a <<< "$line" file` is a plausible way to append a line.
- Consequence: fails open
- scope: out

**R4 (HASH): a line continuation between `$` and `{`.** Out of scope: this change did not cause it.
- What happened: `echo $\` (newline) `{v%% #*} > T` is allowed on the base and at the head, and real bash writes T.
- Where: bash_writes.py:196 looks for `${` before the backslash-newline is removed.
- How found: `c6.py`.
- Would reverse it: none needed; it is the same on the base.
- Ordinary work: no, because nobody splits `$` from `{`.
- Consequence: fails open
- scope: out

**R5 (FC): `<<` inside `${…}` on a prefix assignment.** Out of scope: this change did not cause it.
- What happened: `x=${v:-<<EOF} touch T` is allowed on the base and at the head, and real bash writes T.
- What this change moved: the variant `… touch T # it's` was refused on the base only through the comment-quote fallback, and is now allowed.
- Where: decide.py:583, the same split at a `<<` token.
- How found: generated set 1; `c3.py`.
- Would reverse it: none needed; it is the same on the base without the comment.
- Ordinary work: no, because a `<<` inside a parameter default is not written in ordinary work.
- Consequence: fails open
- scope: out

**What I probed and found sound:**
- **HASH:** each F1 form is now denied for T and allowed for an allowed path at the head. This covers top level, `${x:-…}`, `${x/…/…}`, `${x%%…}`, nested `${`, inside `bash -c`, a `bash <<'EOF'` body, `$( )`, backticks, `eval` and a `while read` loop. The base allowed most of them. `${#v}`, `${v#a}` and `$#` are unchanged, and real comments stay comments.
  - The allowed path used is `tests/unit/guard/test_w2_42a_zz.py`. The brief's `src/ok.py` is outside this ticket's `allowed_paths`, so `decide()` refuses it.
- **HSTR:** `grep -c b <<< "a # b"`, `wc -l <<< "a # b"` and `grep x <<< y # it's` are allowed, and their redirect and pipe writes are judged. `while read …; done <<< "T"` went from allowed on the base to denied.
- **Runners of a here-string are not freer:** `bash <<< 'touch T'`, `xargs touch <<< T`, `cat <<< 'touch T' | sh`, `python3 <<< "open('T','w')"` and `python3 -c "open('T','w')"; cat <<EOF` give the same answer on the base and the head.
- **DEP1:** `python3 -c` writes are denied for T and allowed for the allowed path; `print(1)` stays free. This is identical on the base and the head.
- **DEC409:** across 179,712 generated commands, the only lift form lost to free that bash runs is R2.
- **Claim 3:** `judge()`'s fail-closed result covers everything decide's base fallback gave (the line parser, plus the unresolvable target under the same condition). It re-raises when no second reading finds a target. Nothing downstream reads `findings`: the live hook calls only `_extract_bash_write_targets`.

```verdict
{"kpis": [{"kpi": "HASH", "verdict": "pass", "findings": [{"id": "R4", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "HSTR", "verdict": "pass", "findings": [{"id": "R3", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}, {"kpi": "DEP1", "verdict": "pass", "findings": []}, {"kpi": "DEC409", "verdict": "pass", "findings": [{"id": "R2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "FC", "verdict": "pass", "findings": [{"id": "R1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "R5", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]}]}
```

decisions: DEC-1174, DEC-1164, DEC-409, DEC-801, DEC-808, DEC-1010, DEC-1154

Session id: not known to me. Head probed: w2/W2-42a at a62cd8c11439f35c3cb885087823d257d564fbda.

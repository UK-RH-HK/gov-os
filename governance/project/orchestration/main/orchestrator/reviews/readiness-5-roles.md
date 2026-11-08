# Readiness review 5 of 7 before the fresh 80: role filtering and the hidden-set protection

- **For:** the Wave 2 CTO (DEC-1097 (3); FRESH-80-READINESS §5 item 5). **By:** readiness reviewer 5, read-only, 2026-11-08.
- **Tree:** `w2/integrate` at `232efc47d8a1`; pin `pin-bcea09060ebc`; ACT-GUARD-SETS-1 as rebuilt 2026-11-08.
- **Never opened:** anything under `~/gov-os-eval/`, the writer's or checker's folders or transcripts, any hidden
  or spent question file. Only names were judged: the hook was given paths that do not exist, or paths under a planted root.
- **Method:** I read the pin's code and the ACT's files. `apply.sh check` on the main tree gave exit 0 ("ready to
  apply"). Then I made a `--no-hardlinks` clone at `232efc47d8a1` in my scratchpad, ran `apply.sh apply` there, and
  pointed the block's root at a planted dummy root next to the clone. I ran the candidate hook on chosen events
  (`readiness-5/probe*.py`). After that the clone was removed. The live hook (`e406653ef6c9`) and the live map
  (`6d79946fdbbd`) are unchanged.
- **gov retrieve:** not used. Every question was a code or record read of a named file. Guard refusals: 0.
- **Scratch:** the peak was 166M and 7,847 inodes in `readiness-5/`. At the end it was 20K and 5 inodes.

## (a) `gov retrieve` by role, and the hidden halves never indexed: holds
- **Role filter:** every route's hits pass through `role_filter` before fusion (`retrieve.py:265-291`, `385-386`;
  `retrieve/command.py:121-133`; `supplementary.py:124-135`). It reads the main tree's `role_paths:`. A role map
  that cannot be read stops the search (ROLE_PATHS_UNREADABLE).
  - `role_paths` names only engineer (`{ticket_tests}`) and test designer (`{ticket_impl}`). This filter keeps a
    ticket's tests and its implementation apart. It is not the hidden-set mechanism.
  - The orchestrator has no entry. The fresh-80 measure and reader run with `GOV_ROLE=orchestrator` and no ticket,
    as E0 and E2 did (`e0_run.sh:14,39`; `f80lib.search`). So the bundles match E0's.
- **The hidden halves never enter search (DEC-1052 G-3, M-4):**
  - The lexical corpus is `git ls-files`, tracked files only (`lexical.py:6`, `138-145`). The hidden halves live
    outside every tree, under the sets root.
  - The namespace for `fixtures/evaluation/**` also says `lexical_policy: not indexed` and
    `embedding_policy: not embedded` (`path-map.yaml:256-264`; `lexical.kept_out`; `semantic._wanted`).
  - `.gov-runtime/` is ignored (`.gitignore:18`).
  - The `evaluation_sets` hidden globs in the repository match no tracked file. The only tracked folders under
    `fixtures/evaluation/` are `memory-retrieval/visible` and `memory-retrieval/retired`.
- **No query text kept by search:**
  - The vector caches are keyed by sha256 (`vector_cache.py:63`; `semantic.py:303-310`).
  - The rerank logs hold kinds and devices, not queries (`rerank.py:66-71`; `rerank_service.py:73-168`).
  - The continuation token is stateless.
  - A miss on a hidden question is recorded by its id only (`learning.py:141-160`).

## (b) ACT-GUARD-SETS-1 as rebuilt: the design is right, with one gap (F1)
- **What holds:**
  - Six refused roles. The block's five globs.
  - Other `runs/` folders stay open. In the clone, `cat <root>/runs/e0/counts.txt` was allowed.
  - A line that names only the root is allowed (F16–F18).
  - The orchestrator is kept out of `measures.roles`, so the measure is not refused for the CTO.
  - The block is read from the main tree only.
  - A malformed block fails closed.
  - `apply.sh check` gives exit 0, and both patches give their hashes.
- **The named gap (GOV_KEEP):** it is a row (R1). The wider form of the same cause is F1.

## (c) Other routes to the 80: one open route (F2), the rest rows
- **Checked and closed:**
  - The fresh-80 scripts' standard output carries ids and counts only (`f80lib.say`, `run_measure.sh` `say`).
  - The measure's helper stderr goes to `runs/fresh-80/` (hidden).
  - Kept outputs, rows and data all go under `runs/fresh-80/`.
  - The reader calls `claude -p` with `--no-session-persistence`, so it leaves no transcript.
  - `preflight.py` names load faults by id only.
  - The `.out` files in `~/gov-os-runs/fresh-80/` hold filtered lines only.
  - The CTO's session and every main-tree session get `GOV_ROLE=orchestrator` from `settings.local.json`.
    Subagents take the session's role.
  - The replay tool reads only the main tree's and the worktrees' transcript folders (`replay_sets.py:58-61`).

## (d) W2-84's deletion: clean
- In the applied clone, `git grep` for the seven names finds them, outside docs, tickets and orchestration records,
  only in `tests/acceptance/W2-84/README.md`, a leftover (R4).
- The ticket (DAEO-m1u3) is closed.
- `tests/unit/optin/test_optin_lifted.py`: 16 passed.
- Collection of `tests/acceptance/W2-84` and `tests/unit/guard` with `--optin=lifted`: 1,085, no error, as the
  rehearsal found.
- `gov doctor`'s stale-reference check follows renames only and skips `tests/acceptance/`
  (`doctor/command.py:71-76`, `565-572`).

## Findings

### F1: a path carried by a shell variable reads the 80's rows: FIX BEFORE THE 80
- **Evidence:** the applied candidate hook, with the planted root `<R>`.
  - **Allowed:**
    - `D=<R>; cat $D/runs/fresh-80/rows/q01.json` (engineer)
    - `D=<R>/runs/fresh-80; cat "$D/rows/q01.json"`
    - `R=<R>; cat $R/runs/fresh-80/USED` (orchestrator)
    - `R=<R>; ls $R/runs/fresh-80`
    - `R=<R>; grep -r x $R/runs`
    - `D=…; cd "$D" && cat rows/q01.json`
    - `R=<R>; find $R -name '*.json' -exec cat {} +`
    - `python3 -c` with `os.path.join(...)`, the class of B14.
  - **Refused (controls):** a direct `cat` or Read, a `for` loop over a glob, `grep -rn` on the named folder, and
    `export D=…; head $D/…`.
- **Cause:** the pin's `_expand_token` (`gov/guard/decide.py:225-250`) expands only the hook's own environment. A
  variable set on the command line stays literal and names no path.
- **Not introduced by the ACT:** the in-repo hidden rule has the same limit. In the clone,
  `D=<repo>/fixtures/evaluation/memory-retrieval/hidden; cat $D/h01.yaml` was allowed, and the direct form refused.
  The ACT names only the GOV_KEEP write form (F22, F23). The read form is not in the record.
- **Scope:** in (aspect (b); the 80's rows hold question, gold answer and answer, FRESH-80-1 §2 items 7 and 20).
- Ordinary work: yes, because the CTO is the one measured role that works with the sets root, and its usual shell
  form is `D=…; … $D/…`. Examples: `ACT-G14.md:285-292`, `ACT-GUARD-FIX-4.md:86-96`, and `F=…; PY=…` in
  `drafts/fresh80/README.md`. It will look into faults during the 80 (§3.5), and a first try written that way gets
  no refusal.
- Consequence: fails open
- **Effect on the verdict:** the store and the clone are frozen, so the computed figure would not change. The
  counts-only rule for the CTO would be broken without anyone being told.
- **Options:**
  - **(A) Narrow text check in the candidate hook, refused roles only.** Refuse a Bash command that names the sets
    root in any spelling (`~`, `$HOME` or absolute, including inside an assignment's value) and also names one of
    the globs' folders (`runs/fresh-80`, `fresh-80`, `memory-verdict-2`, `memory-verdict`,
    `memory-retrieval/hidden`, `transcripts`) as a whole path segment. Also refuse one where an assignment's value
    resolves into a hidden glob.
    - F16–F18 stay allowed. F22 and F23 become refused.
    - Watch for README step 4: `--sets-root ~/gov-os-eval > ~/gov-os-runs/fresh-80/measure.out` names `fresh-80`
      under another root. Exclude segments under another absolute prefix, or rename the out folder.
    - Cost: about 1–2 h for the build, the F cases and a re-run of the rehearsal. The hash table and `apply.sh` are
      redone.
  - **(B) An exception the owner records for the 80's window,** with a written CTO rule: no variable, loop, `find`
    or inline code that names the sets root; only the README's lines. Cost: none. The gap stays open.

### F2: the 80's writer and checker transcripts are open to every measured role: FIX BEFORE THE 80
- **Evidence:**
  - `~/.claude/projects/-home-usain-gov-os-writer/` and `~/.claude/projects/-home-usain-gov-os-checker/` exist. I
    saw their names only and never opened them.
  - The 80 were written by the writer session in `~/gov-os-writer`, whose conversation was kept and resumed with
    `claude --continue` (ACT-MSET-3 lines 1-9, §9). The checker read them (ACT-MSET-4). So the transcripts hold
    the 80's text and gold answers by construction.
  - The ACT's block has one root, `~/gov-os-eval`. The candidate hook allowed a Read and a `cat` of
    `~/.claude/projects/-home-usain-gov-os-writer/<name>` (orchestrator) and `…-checker/<name>` (engineer).
  - `settings.local.json` denies only Read of the three fixtures folders under `~/gov-os-eval`.
  - ACT-D8 §2.3 moved W2-61h's writer transcript into `~/gov-os-eval/transcripts/` for this reason. No such move was
    made for the 80's writer or checker.
  - The checker's staleness pass (READINESS §2) will add another transcript holding the gold answers.
- **Scope:** in (aspect (c): transcripts).
- Ordinary work: yes, because reading transcripts is ordinary CTO work. The standing tool
  `tools/guard_refusals.py:46` scans `~/.claude/projects/**/*.jsonl`. Other examples are `R2-BRIEFS` `extract.py`
  and INVESTIGATION-1. A plain `grep -rn <id> ~/.claude/projects/` prints matching lines of the writer's Write calls.
- Consequence: fails open
- **Fix (owner, about 2 minutes, no code):**
  - After the checker's pass and before the pre-flight, move both transcript folders, and the new checker's, into
    `~/gov-os-eval/transcripts/` (mode 700), in ACT-D8 §2.3's form. The ACT's `transcripts/**` then covers them.
  - Have the owner's operator check `~/gov-os-writer` and `~/gov-os-checker` for drafts or copies of the 80, by
    names only, and move them the same way.
  - To resume the writer, move its folder back.
  - The other way is extra roots in the block, which is a code change.

### Rows (DEC-1010)
- **R1: GOV_KEEP set on the command line (F22, F23).** It is set only inside `run_measure.sh`'s own code, which the
  hook never sees. It is a write and shows nothing. A stray kept file makes a `--kept` re-score refuse, so it fails
  closed. Option (A) of F1 closes it too.
  Ordinary work: no, because no measured role has a reason to point GOV_KEEP at the 80's folder.
  Consequence: other
- **R2: an unmerged worktree has no sets-root rule at all.** There are 35 entries under `~/gov-os-worktrees/`, and
  each runs its own copy of the hook. The ACT's step (6) merges the live ones. Proposed: put the list of merged
  worktrees in the operator's check.
  Ordinary work: no, because an engineer or lead has no work under `~/gov-os-eval/`.
  Consequence: fails open
- **R3: earlier runs' outputs for the 138 lie in open folders.** These are `~/gov-os-eval/runs/w4-e0/` and
  `w4-e5/` (kept retrieve outputs), and `~/gov-os-runs/D4B/{search-again/e2,e3,e5,glossary}/` (reader rows).
  They may hold the 138's hidden question text. Not the 80, and not opened, so not verified.
  Ordinary work: no, because no measured role has a reason to read them.
  Consequence: fails open
- **R4: W2-84's leftovers** (`README.md`, which names the deleted files; `conftest.py`; `w2_84_support.py`). This is
  the rebuilder's point 5.
  Ordinary work: no, because they are history files of a closed ticket.
  Consequence: other
- **R5: the code index takes untracked files.** It runs `ls-files --others --exclude-standard`
  (`codeintel/__init__.py:186`), while the lexical corpus is tracked files only.
  Ordinary work: no, because a hidden file would first have to be copied into a tree.
  Consequence: other
- **R6: the reader's own traceback lands in an open file.** `fresh80_reader.py` stderr goes to
  `~/gov-os-runs/fresh-80/reader.out` (`2>&1`, an open folder). As far as I read, the messages carry key names,
  not text. For reviewer 7.
  Ordinary work: no, because it needs an unexpected exception that carries data.
  Consequence: other

```verdict
{"kpis": [
 {"kpi": "5a-retrieve-role-filter-and-no-hidden-index", "verdict": "pass", "findings": [
   {"id": "R5", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "5b-act-guard-sets-1-design", "verdict": "fail", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "R1", "scope": "in", "ordinary_work": "no", "consequence": "other"},
   {"id": "R2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "5c-no-other-path-to-the-80", "verdict": "fail", "findings": [
   {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "R3", "scope": "out", "ordinary_work": "no", "consequence": "fails open"},
   {"id": "R6", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "5d-w2-84-deletion", "verdict": "pass", "findings": [
   {"id": "R4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}
]}
```

**NOT READY for the 80.** Two findings must be fixed before the 80 (F1, F2); six rows.

## Round 2 (the last): F1 after the line rule (the CTO's option A), 2026-11-08 07:16–07:40 GMT

- **The files checked:**
  - `pretooluse.candidate.py` `bd545af83198`, with `sets_line_refusal` (DESIGN.md §F).
  - `guard4_check.candidate.py` `ff5321041613`.
  - `apply.sh` `472bc1c1d226`. `apply.sh check` on the main tree: exit 0, "ready to apply".
  - The rehearsal record (`REHEARSAL.md`, `rehearsal.log` 07:04–07:13, 0 failures). Its 8 override-off FAIL
    lines are the expected X1, X2 and A7 cases.
- **My check:** a new `--no-hardlinks` clone at `232efc47d8a1`, `apply.sh apply` run there, and a planted root next
  to the clone (`runs/` and `transcripts/` dummies only). I ran three modes: the root absolute; `~/gov-os-eval` with
  HOME set to the planted home; and the `$HOME/…` spelling (`readiness-5/probe_r2.py`).
- **Result: 87 of 87 as wanted.**
  - **Refused, in all three spellings:** all ten F1 forms of round 1, including the `export` control and GOV_KEEP.
    Also seven more: a variable at `runs` (`D=<R>/runs; cat $D/fresh-80/…`), a `python3 -` heredoc with
    `os.path.join(…,'fresh-80',…)`, a `for` loop over a variable, `sed` through a variable, `jq` on the direct path,
    a two-line script and `transcripts` through a variable.
  - **Allowed, in all three spellings:**
    - every README command: set once, the pre-flight, step 4 with its restart, the wait, steps 5, 7 and 8 (e3,
      E5 live, the E4 dry run, the E4 window, the replays) and the hold line;
    - `tail` of `~/gov-os-runs/fresh-80/*.out`;
    - `ls <root>/runs` and `cat <root>/runs/e0/counts.txt`;
    - the measure's line;
    - unrelated variables and loops.
- **Regressions:** none found.
  - The candidate check's L cases in my clone: 368 of 370 ok. The two misses come from my setup, not the hook.
    W8 expects the reviewer's write rule to refuse, and my planted root lies under `/tmp`, which reviewers may write.
    T3's default tree, the live W2-13 worktree, is not a worktree of my clone.
  - The rehearsal's suites are the same before and after: 467 passed; 151 passed and 1 skipped; 16 passed.
- **The README's `proc.sh wait --max 3600 $(cat ~/gov-os-runs/fresh-80/measure.pid)` (A7): safe.**
  - The override lifts the listing refusal only when the listing starts outside the sets root and no word names the
    root or a folder above it.
  - `proc.sh wait` reads no file. Its argument is the CTO's own pid file in an open folder.
  - The general form is a row (R8).
- **The replay's 24 new refusals: acceptable** (`~/gov-os-runs/SETS-rehearsal/replay.json`, read in full; 0 deny→allow).
  - 6 are meant: `stat` and `repin_gold.py` on hidden folders, and a product-spec `find` of `memory-verdict-2`.
  - 6 false refusals come from the hidden rule, each a names-only probe of this ACT. One is my own
    `git check-ignore … transcripts runs`.
  - 12 come from the line rule on open `runs/` outputs. None read a hidden file. These refusals cost a retry with
    the direct path, which stays allowed, or a script file. They lose no work, so they are rows.
- **The known gaps:**
  - **A root spelled in pieces** (`A=~; $A/gov-os-eval`): allowed in my check.
  - **A positional parameter:** my form, which named a hidden folder in its inline code, was refused. The form with
    no hidden name stays open, as the rebuilder states.
  - **The in-repo hidden folders keep the old variable gap:** no hidden file is in any tree (G-3).
  - **One more spelling:** `D="$HOME"/gov-os-eval; cat $D/runs/fresh-80/…`, with HOME quoted on its own, is allowed.
    It is not among the rule's spellings. That form appears 0 times next to `gov-os-eval` in the CTO's records and
    tools, against 381 for `~/gov-os-eval` and 8 quoted-HOME forms in all. A cheap fix is to add `"$HOME"/` and
    `"${HOME}"/` to `sets_root_spellings`, at the next rebuild.
- **F2:** handed to the owner's operator (the coordinator). It stays open until the move is done.

### Rows added in round 2
- **R7: spellings the line rule does not know.** These are a root spelled in pieces, a positional parameter with
  no hidden name, and `"$HOME"/gov-os-eval`.
  Ordinary work: no, because the CTO's records spell the root `~/gov-os-eval`, `$HOME/gov-os-eval` or absolute; the
  quoted-HOME form next to it appears 0 times.
  Consequence: fails open
- **R8: the override follows a list file's contents.** `cat $(cat L)` and `xargs cat < L` read hidden paths written
  only inside a list file L (allowed in my check, for the engineer and the CTO).
  Ordinary work: no, because under the guard no ordinary command can produce such a list. `ls`, `find` or a glob
  over the 80's folder that names the root is refused by the line rule or the judge, and the fresh-80 scripts print
  no paths.
  Consequence: fails open
- **R9: the line rule's false refusals on open `runs/` outputs** (12 in the replay). Retry with the direct path or a
  script file.
  Ordinary work: yes, because the CTO and its engineer subagents read open `runs/` outputs this way.
  Consequence: other

```verdict
{"round": 2, "kpis": [
 {"kpi": "5b-act-guard-sets-1-design", "verdict": "pass", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "R7", "scope": "in", "ordinary_work": "no", "consequence": "fails open"},
   {"id": "R8", "scope": "in", "ordinary_work": "no", "consequence": "fails open"},
   {"id": "R9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "5c-no-other-path-to-the-80", "verdict": "fail", "findings": [
   {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}
]}
```

**Round 2 verdict: F1 is closed (now `consequence: other`).** The record stays **NOT READY** only for F2, which is
with the owner's operator. Once the writer's, checker's and new checker's transcripts are in
`~/gov-os-eval/transcripts/`, it is READY.

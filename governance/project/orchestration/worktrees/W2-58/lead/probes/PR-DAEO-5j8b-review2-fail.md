---
type: probe
task: DAEO-5j8b
reviewer_session: 8d1db0d3-45d5-473b-a206-cce2816f4f94
implementer_session: 1bdab8bd-9d97-44d7-805f-c508a8b32e72
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: bbbe20fa5c98fc606c888e59a620273b958f3e09
---

# Probe record: W2-58 (DAEO-5j8b), the (c)/(d) read rules fail open on a leading-`~` path through the file tools

- **What was probed.** The head `bbbe20fa`, for behaviour the acceptance tests miss that could lose work,
  widen a write, change the acceptance tests, or make the guard/launcher fail open. Driven against the real
  guard hook in fixtures built from scratch (the suite's own `w2_58_support`), plus `gov launch` with the
  suite's stand-in CLI; stand-in secrets throughout, no real secret or held-out path named. Covered: every
  read route of (a) secrets, (b) held-out, (c) the engineer's acceptance tests and the test designer's
  changed code, (d) the hidden eval part (measured by role and by ticket) — by Read, Grep, Glob and the Bash
  forms an honest agent uses (direct paths, relative, absolute, `~`, `$HOME`, `cd`, pipes into `xargs`,
  `$(…)`/backticks, `while read`, `for` loops, git history); the five review-round fixes (run-time names,
  subagent union, WBS-id tickets, credential names, no-write-widening); the launcher's hand-off; and the
  fail-closed paths (malformed `evaluation_sets`, unparseable ticket, git failure).

- **What was found.**

  **Finding 1 — the counterpart's work (c) and the hidden eval part (d) are readable through Read/Grep/Glob
  by a leading-`~` path (fails open). Severity: high.**
  - *What was done.* I asked the guard to read protected content by its `~`-home spelling through the file
    tools, and by the same spelling through Bash, and compared with the absolute and relative spellings.
  - *What happened.* For an engineer on T, `Read ~/gov-os-worktrees/W2-95/tests/acceptance/W2-95/test_feature.py`
    is **allowed**, and so are `Grep path=~/…/W2-95` and `Glob path=~/…/W2-95`; the absolute and relative
    spellings of the same file are refused. For a test designer on T, `Read ~/…/src/app/main.py` (a changed
    file) is **allowed**; absolute is refused. For a measured session (research by role, and an engineer on a
    ticket the set measures), `Read ~/…/eval/memory/hidden/answers.yaml`, `Grep` and `Glob` over that `~`-path
    are **allowed**; absolute is refused. The Bash equivalents (`cat ~/…`, `cat $HOME/…`, `grep -rn ~/…`) are
    all correctly refused.
  - *What should have happened.* Every route — the file tools included — must refuse (c) and (d). The cause is
    that the new rule resolves a file-tool path with `abspath`/`realpath` but never expands `~`, so a `~`-path
    is treated as a non-existent relative path and matches no protected part; the Bash branch of the same rule
    expands `~`/`$HOME`, and the held-out (b) rule and the oracle rule both expand `~`, so the omission is
    isolated to the file-tool resolver. The same omission would pass the home-prefixed (a) secrets
    (`~/.ssh/…`, the CLI key file) through the file tools, since those are matched by home-prefix, not by name.
  - *Reproduction.* Deterministic at the guard (the code under test), many times. That the Read/Grep/Glob
    tools open a `~`-path end-to-end is the project's own model (W1-47's `tilde-Read` sits in the set the guard
    must deny; `heldout.py` expands `~` for the file tools), not run live here (no network to the CLI in the
    sandbox).
  - Ordinary work: yes, because `~/gov-os-worktrees/<id>/…` is the canonical way the project's own prompts name
    a worktree and `~` is the ordinary home shorthand; an honest engineer, test designer or measured session
    using the Read or Grep tool with such a path — a measured session reads the visible eval part legitimately
    and the hidden part sits beside it under the same `~/…/eval/` tree — hits it, with no planted link, git
    environment variable or opaque interpreter (so not a Wave-3 construction under DEC-801).
  - Consequence: fails open — a route that must refuse (c)/(d) returns allow, and the tool then reads the
    protected content.

  **Finding 2 — the engineer's own test run is refused when the interpreter carries a flag, or under coverage
  (over-refusal). Severity: medium.**
  - *What was done / happened.* `python3 -m pytest tests/acceptance/W2-95` and `pytest …` are allowed, but
    `python3 -I|-B|-u|-W error|-X importtime|-E|-O -m pytest …` and `python3 -m coverage run -m pytest …` are
    refused under (c): the test-folder operand is read as a counterpart read because the pytest allow-list only
    recognizes the bare `pytest`/`python… -m pytest` forms.
  - *What should have happened.* KPI 1 — the engineer "can still run those tests with pytest." Ordinary flags
    (isolated/no-bytecode/warnings) and a coverage run should still count as a test run.
  - Ordinary work: yes, because `-B`/`-W error`/coverage are common ways to run a suite.
  - Consequence: other (blocks the engineer's own test run; does not fail open and does not lose work).

  **Probed and found sound.** (c) by every aimed and search route but `~`: Read/`cat`/`head`/`sed`/`awk`/
  `git show HEAD:<file>`/`cp`, Grep/Glob/`ls`/`find` aimed inside, searches from above (`grep -rn .`, `rg`,
  `git grep`, `-g`/`--include`/type filters), history (`git show HEAD`, `git log -p`, `git diff` with no
  pathspec, `git-grep`, `git cat-file`), and the run-time-name forms (`git ls-files|xargs`, `find|xargs`,
  `$(…)`, backticks, `while read`, `git status|…|xargs`) — all refused; narrowed-to-`src` forms and
  `pytest | tail` allowed. The subagent union (session role ∪ subagent type) refuses correctly; an
  untyped/`general-purpose`/`Explore` subagent of the ticket lead reads T's tests (as intended). WBS-id
  tickets (`GOV_TICKET=W2-95`) resolve and refuse; `gov launch … W2-95` hands on the id. Secrets by name
  (`*.env`, `.env.*`, `*.pem`, `*.key`, `config/secrets*`, `.secrets/…` at any depth, `~/.ssh` and the CLI key
  by absolute path) refused; neighbours readable. Held-out (b) refused by every route including `~`; its list
  names readable. No write rule widens: `dd of=`, `truncate`, `sort -o`, `rsync`, `patch`, `git checkout --`,
  `git restore` naming the two files are refused to the engineer and test designer; reading them is allowed.
  Launcher adds no `Read` rule and no sandbox read-deny for (c)/(d); keeps the held-out `Read` rule for every
  role; a malformed/unparseable `evaluation_sets` refuses the launch and refuses the guard calls of every
  session it could concern (fail closed); a git failure (orphan, no merge base) refuses the test designer fail
  closed; no base branch refuses nothing under (c). Bounded-time budgets hold (typical call 1–8 ms). The
  acceptance suite (749 passed) and guard/launch unit tests (1162 passed) are green and my runs changed no
  tracked file.

  **Residual class (Ordinary work: no → Wave-3 rows, not this round).** A `cd` whose target is a glob
  (`cd tests/acceptance/W2-9* && cat test_feature.py`) or an unresolvable shell variable
  (`D=…/W2-95; cd $D && cat …`; `cat $F` where `$F` holds the path) lets a read through — the recorded
  residual class of DEC-562/DEC-570 (shell spellings the token expansion gives up on; a `cd` the guard cannot
  place). `cat $(git rev-parse --show-toplevel)/<own file>` is over-refused to a session with a protected part
  (the change record's §7 residual 2). These need an unusual construction, not ordinary work.

- **Judgement.** **fail.** Finding 1 is "Ordinary work: yes" and "Consequence: fails open": the guarantees of
  (c) and (d) — and the home-prefixed part of (a) — are defeated through the primary read tools by a plain
  `~`-path spelling, because the file-tool path resolver omits the `~` expansion that the Bash branch, the
  held-out rule and the oracle rule all perform. The fix is one line and small tests; it rides the resume
  (DEC-802), alongside broadening the pytest allowance (Finding 2, Consequence: other). I repaired nothing
  (MR-4).

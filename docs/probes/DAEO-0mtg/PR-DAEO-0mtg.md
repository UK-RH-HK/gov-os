---
type: probe
task: DAEO-0mtg
reviewer_session: d80ccaed-381d-45a9-9d6e-474ede3887ed
implementer_session: unknown (the engineer's log was lost at the tool's time limit)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: c2c99e6c084feb004ef04dbb3f6768eec7ca23e6
---

# Probe record: W2-106 (DAEO-0mtg)

(`CLAUDE_SESSION_ID` is unset; the reviewer session id is this session's own, from its scratchpad path.)

- **What was probed:** head `c2c99e6c084f` of `w2/W2-106`, run, not only read.
  - **Setup** (nothing written in the repository; everything under the session's `TMPDIR`):
    - a stand-in pin, built as the acceptance support builds it: this worktree's wheel, built with no network, installed non-editable in a `--system-site-packages` venv, instrumented, and reached through a link at a temporary `HOME/.local/bin/gov`;
    - a project generated from the template (Copier from a file-by-file source, then `rulesync generate`), with an edited `gov` planted in its `src/`.
  - **Probed:**
    - the generated project's three guard lines, through `sh -c` with the event's JSON, as an engineer: an out-of-scope Write, an allowed Read, and the two post-tool events;
    - the same with a planted `PYTHONPATH` naming the edited gov, and `PYTHONHOME` naming a missing folder;
    - gov installed by pip into an environment whose path holds a space, and into one whose interpreter path is 155 characters long;
    - the same with a stand-in program named `import` on `PATH`, once returning at once and once waiting 61 s on its first run;
    - the kernel's programs run directly by dash and by bash in POSIX mode;
    - a dangling home link, with and without another gov on `PATH`;
    - a first line ending in a carriage return, a first line with a space after `#!`, and a project path holding a space;
    - an edited gov in the home's user site folder, directly and through an editable install's path file;
    - KPI 4, by a run of the reviewer's own;
    - the commits: paths per role, trailers, the merge.
  - No suite was re-run (DEC-959 item 1).

- **What it found:**

  **F1 (low; widens a known residual): when gov's launcher is in pip's long-path form, the guard lines hand the hook program to `/bin/sh`.**
  - **What was done:** this worktree's wheel was installed by pip (24.0) into a venv whose path holds a space, and into one whose interpreter path is 155 characters long. `HOME/.local/bin/gov` was linked to that launcher, and the generated lines were run.
  - **What happened:**
    - In both cases pip wrote the launcher in its long-path form: a first line `#!/bin/sh`, then a line that execs the real interpreter. `gov --version` works through it, so the install looks sound.
    - The lines take `/bin/sh` as the interpreter, because it is an executable file, and start it with `-E` on the Python program. dash reads the program as a shell script: it runs `from` and `import` as commands found on `PATH`, then stops at a syntax error with exit 2. Bash in POSIX mode, run directly, does the same.
    - Every call is refused, the allowed Read included. The post-tool lines end 2 without the containment check running. The agent sees the shell's errors, never the line's own message. The project's files were unchanged.
    - A stand-in `import` on `PATH` was run 7 times by the pre-tool line and 5 times by the post-tool line.
    - When that stand-in waited 61 s on its first run, the pre-tool line ended only after 67.6 s, past the entries' 60 s limit. DEC-580's own text says the harness ends a hook at that limit and lets the call through. The program's 20 s deadline never starts, because Python never runs.
  - **What should have happened:** a first line that names no Python interpreter is refused by the line's own check, with its message, as the `env` form is. Alternatively the interpreter is read from the launcher's exec line. Either way the program is never handed to a shell. This falls outside KPI 2's words, because a shell is "an interpreter that runs".
  - **Known and new:**
    - Known: W2-59's CIT-P §9 names this form as a risk, judged by reading. Its residual "checks only that the named interpreter is an executable file, not that it is a Python" is a Wave 3 row (DEC-877 item 5).
    - New: the template ships the form to every adopted product, and a product's install path is its owner's choice, so the owner pin's 50-character mitigation no longer covers every product.
    - New: the refusal is the shell's, and it comes only after the shell has run programs from `PATH`. A waiting one turns the refusal into a pass at the time limit.
    - A fix has to change this repository's form too: KPI 1 and its acceptance case hold the template to that form exactly, and this repository's lines are an owner change (DEC-822 item 2, CAP-33).
  - Ordinary work: yes for the refusal, because pip writes this launcher for any environment whose interpreter path holds a space or passes 127 characters, an ordinary install folder; no for the pass at the time limit, because it also needs a program named `import` or `from` on `PATH` that waits past 60 s, a machine state no agent sets up and in which every call takes a minute.
  - Consequence: other. As measured, it fails closed: an adopted product with such an install cannot work, because every call is refused with the shell's errors. It fails open only in the case marked "no".

  **F2 (info): a dangling link at `HOME/.local/bin/gov` counts as no gov there, and the gov next on `PATH` decides.**
  - **What was done:** the home gov was a link into a removed folder, as a re-pin that deletes the old pin's folder would leave it. A second gov on `PATH` named an interpreter of its own. The run was repeated with no gov on `PATH`.
  - **What happened:** with the second gov present, its interpreter started and decided. With none, the line refused with exit 2 and a message naming both places it looked.
  - **What should have happened:** the behaviour follows KPI 1's lookup order; it is recorded so the reading is on file. Whatever decides is another installed release, run under `-E`, never a gov that `PYTHONPATH` chose.
  - Ordinary work: yes, because a re-pin that removes the old folder before relinking, with a project environment's gov on `PATH`, leaves exactly this.
  - Consequence: other. Another installed gov's guard decides; nothing fails open by itself.

  **F3 (info; known from the acceptance README): once the lines are pinned, the suites that run the template's guard line from a stand-in home with only a user-site path file judge the gov on the runner's `PATH`, not this worktree, until W2-90's next round.**
  - **What was done:** the README's account was read and its mechanism measured. Under `-E`, the pin's import path is the standard library, then its own site-packages, then the user site folder and path-file entries. A user-site gov, placed directly or through an editable install's path file, was never imported, and the pin's guard denied the out-of-scope Write.
  - **What happened:** a stand-in home with only a path file gets the gov on the runner's `PATH`, here the owner's pin, whose guard code decides those suites' guard-line cases.
  - **What should have happened:** for an adopted product nothing changes: the line finds the product's own installed gov, as intended. For this repository's verification (DEC-732), the harnesses named for W2-90's next round (W1-05, W1-46, W1-28, W1-47, W1-50) need the editable install's gov script in their stand-in home, as W1-38's revision has.
  - Ordinary work: yes, because any later ticket that changes the guard runs those suites, which would then pass or fail on the pin's code.
  - Consequence: other. It is a verification gap in this repository's tests, not product behaviour.

- **What was sound:**
  - **Pinning:** in the generated project the pin's guard denied an engineer's out-of-scope Write, also with a planted `PYTHONPATH` naming an edited gov and with `PYTHONHOME` naming a missing folder. The edited gov and its `sitecustomize` never ran, and the decoy `python3` first on `PATH` never started. An allowed Read passed.
  - **Fail closed:** refused with exit 2 and the line's own message: a dangling home link with no gov on `PATH`; a first line ending in a carriage return; a first line with a space after `#!`.
  - **Paths with spaces:** a project path holding a space ran the program under the pin's interpreter with `-E`.
  - **KPI 4:** after Copier and `rulesync generate`, each generated guard line equals both template files' lines, character for character. The four lifecycle lines keep their plain form (DEC-917). The template diff is six lines, with no change under `src/`. The guard's child processes are git only, so `-E` drops nothing the hook-reached code uses.
  - **Roles:** `fd700209e354` (engineer) touches only its three allowed paths; `cd96b8d4d60d` and `091a07a70042` (test designer; the second with `Rewrite-Reason: DEC-966 item 2`) touch only `tests/acceptance/`; no engineer commit touches an acceptance test; `d56ed3fe7e71` is git's own merge of its parents.
  - **Not probed:** zsh or fish as the hook's shell (not installed); ImageMagick's own `import` (a stand-in was used); launchers written by uv (an install command refused to this role); a pin re-installed mid-session (reasoned about only: each run resolves the pin anew, and the measured analogues end 2).

- **Judgement (the lead, for the orchestrator, by JUDGEMENT.md's two questions):** pass. No finding is "yes" to ordinary work together with "fails open" or "loses work".
  - F1's ordinary path fails closed, and loudly: every call is refused, so a product owner sees it at once. Its pass needs a program named `import` or `from` on `PATH` that blocks past 60 s as well as a long-path install, which no agent sets up in ordinary work. It is a row for the Wave 3 hardening pass, joined to DEC-877 item 5's residual (a first line that names no Python is refused by the line's own check, or the launcher's exec line is read), with W2-59's CIT-P §9 corrected. Any change to the form is an owner change to this repository's lines too (DEC-822 item 2).
  - F2 and F3 are information. F3 is the test designer's P2 for W2-90's next round.

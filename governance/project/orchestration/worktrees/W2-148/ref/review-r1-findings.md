**Findings**

- **F1 (S6), scope: in.** The script scan (`act_class.py:233-279`, `segments` and `strip_wrappers`) treats a shell reserved word as the command name. A `sudo`, `git push`, `git tag`, install, network call or `rm` outside the project after `then`, `do`, `else`, `elif`, `{` or `!` raises nothing. Confirmed by the probe.
  Ordinary work: yes, because one-line `for …; do …; done` and `if …; then …; fi` are an everyday shell form that past ACTs use (ACT-QUERY-CPUS-1:24, ACT-QUERY-GPU-2:43), and the code's vote exists to catch the CTO's misclassification.
  Consequence: fails open.

- **F2 (S12), scope: in.** G8 runs `apply.sh` with the clone as cwd and a planted HOME (`operator_run.py:491-507`), but nothing refuses or detects a script that reaches the live repository or the real HOME by absolute path. Such a script applies the ACT live during the "dry run". The changed-set check then refuses as "missing" (`:504-507`), and the live change stays with no undo, journal, commit or after-check. The P1 does not say live files changed.
  Ordinary work: yes, because 50 of the 57 past ACT files name `/home/usain/…` and several begin with `cd /home/usain/Dynamic-Agentic-Engineering-OS`, while neither brief tells the author or the reviewer that `apply.sh` must stay relative.
  Consequence: fails open.

- **F3 (S15), scope: in.** The guard replay reads `calls`, by default the operator's own dry-run commands (`opcommon.py:77`, `operator_run.py:530-536`). No guard-wide log of the last 48 hours of calls exists. A path-map or deny-list addition in (a) that refuses agents' ordinary calls is therefore never caught.
  Ordinary work: yes, because it applies to every path-map or deny-list (a) ACT.
  Consequence: other (agents get refused; nothing loosens).

- **F4 (S21), scope: in.** The default push goes through `deadman.py --test`. It reaches the phone as "TEST DEADMAN | {json…" cut at 190 characters, so only about 60 characters of the notice text survive. Each notice also writes a TEST note into `deadman.log`. A P1 "lock held" can read like a test.
  Ordinary work: yes, because it applies to every notice.
  Consequence: other.

- **F5 (S13, S14), scope: in.**
  - The operator writes its commit freeze at `<operator root>/log/act-in-progress.txt`, which no CTO rule or tool reads; the prompt's freeze is the scratch's `log/act-in-progress.txt` (`w2-orchestrator.md:174`). So the CTO's commits are not frozen during an apply.
  - G9 and the launcher hold on the scratch file, which the prompt tells the CTO to write at hand-over and keep until the ACT is done. Queueing with that habit holds the launch indefinitely.
  Ordinary work: yes, because it is the CTO's standing rule.
  Consequence: other (the launch stalls, or a commit races the apply and the staged-list check refuses and undoes).

- **F6 (S17, S19), scope: in.** The session runs `operator_run.py` through Claude Code's Bash tool. Its timeout is 2 minutes by default and 10 at most; neither the brief nor the wall settings raise it. G8's clone and checks, plus each push (up to 300 s), exceed it, so the program is stopped mid-gate or mid-apply. The journal then undoes at the next launch, or the model reruns the command. Not exercised live; confirm in the rehearsal. A setting sized to `session_timeout_s` (for example `BASH_DEFAULT_TIMEOUT_MS` / `BASH_MAX_TIMEOUT_MS` in the wall's `env`) or a timeout named in the brief would fix it.
  Ordinary work: yes, because it is likely on every real run.
  Consequence: other.

- **F7 (S19), scope: in.** The wall hook and settings allow the session itself to run `bash <frozen>/apply.sh apply|undo` and `git add`/`commit` (`operator_wall_hook.py:98-133`, `settings.json.tmpl:7-10`), as §1 lists them. A session that leaves its brief could apply a frozen ACT after the program refused, for example at G6 for a missing yes. Nothing in the program ever asks it to run them (the "unless the program's output asks" in `brief.md:23` never occurs).
  Ordinary work: no, because the brief forbids it twice.
  Consequence: fails open. A Wave 3 row, and a DEC-105 note.

- **F8 (S1, S22), scope: in.** G1 removes and replaces an existing `acts/<id>-<sha12>/` before G5 runs (`operator_run.py:211-213`). If the bundle is edited and the request re-queued with the old sha (§6 row 1, "a fix it forgot to re-review"), the frozen copy of an already applied ACT is overwritten. That ACT's undo then refuses with "the frozen copy changed".
  Ordinary work: yes, because §6 itself names the stale re-queue.
  Consequence: other (the agent's undo is lost; a hand revert remains).

- **F9 (S4), scope: in.** The reviewer-is-not-the-author check is skipped when the manifest has no `author` (`operator_run.py:331-333`); `validate_manifest` does not require the field.
  Ordinary work: no, because it needs both the field missing and the CTO reviewing its own ACT.
  Consequence: fails open.

- **F10 (S21), scope: in.** An exception after G7 is refused as gate "error" (`operator_run.py:1419-1422`). It is neither pushed nor counted as a missing notice in the digest.
  Ordinary work: no, because it needs an unexpected exception.
  Consequence: other.

- **F11 (S12, S15), scope: in.** `.git/config` and the rest of `.git/` outside `hooks/` lie outside G8's changed set, the live unlisted-file check and the control snapshot. An unlisted `git config core.hooksPath …` in an (a) ACT would get past the git-hooks control.
  Ordinary work: no, because both the CTO and the reviewer would have to miss an unlisted command.
  Consequence: fails open.

- **F12 (S13), scope: in.** The nightly hold is by window only (`03:50-08:00`); the `NIGHTLY-RUNNING` flag, which other tools read, is not consulted. A nightly that runs past 08:00 does not hold an ACT.
  Ordinary work: yes, because overruns happen.
  Consequence: other.

- **F13 (S10), scope: in.** `owner_text` does not exclude `isCompactSummary` lines. If a future format marked such a line human, a yes quoted in it would carry a fresh timestamp after the review.
  Ordinary work: no, because it depends on a format not seen today.
  Consequence: fails open.

- **F14 (S6), scope: in.** An empty touched list with commands classifies as (a) (`act_class.py:478`). A commands-only effect with no file trace, such as a model pull through the local server, reaches the apply as (a) rather than (b). Recommend: an empty touched list with any command is at least (b).
  Ordinary work: no, because every one of the 57 past ACTs lists its files.
  Consequence: fails open.

**S23, re-read on a sample.**
- No row is lower than a pinned table row.
- Unpinned rows cannot come out lower: they are (a) or "none".
- The six (a) rows are the servers' ACTs, (a) by Q3. Their only network calls are to 127.0.0.1 (checked against their ACT files).
- The listed rises are right, for example D4-RESTORE-1 (opt-in lines added: (b)) and QUERY-GPU-2 (`~/.local/bin/ollama`: install).
- F1 does not change the trial: the only past hits behind `do` are local `curl` calls.

**S16.** "Outside a ticket" matches `landing_select.sh:72-83` word for word: `Role: owner`, or no `Task: DAEO-*` other than `DAEO-sdxk`; a merge is judged by its own trailers.

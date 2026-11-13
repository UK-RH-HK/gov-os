---
type: probe
task: DAEO-03ub
reviewer_session: 77822768-7673-4779-bf81-08afc3516d2f
implementer_session: c5aadf5f-6f83-4f5a-83ba-533bce8d7b41 (the F1 fix, a4afc4166 and 31201f0ad); the earlier engineer of 94c85f361 to ce03bb8b3 not recorded (before the emergency's stop of 2026-11-02)
reviewer_wrote_nothing: true
commissioned_by: orchestrator (W2-42a ticket lead, session w2-42a-f7)
judged_by: orchestrator (W2-42a ticket lead)
judgement: pass
probed_commit: bb2caf31789a359fe4ba48134bc8e816473fce94
---

# Probe record: W2-42a (DAEO-03ub), FULL review, round 2 of 2 (the last; DEC-1010)

## The lead's judgement

- **Who probed.** A fresh read-only independent auditor (Opus, high), not round 1's, launched by the ticket lead
  with `launch_worker.sh` once the resource gate opened (the first launch was refused by the gate, a wait under
  DEC-1146); brief `.gov-runtime/scratch/lead/briefs/a3-2.md` (JUDGEMENT.md word for word); log
  `.gov-runtime/scratch/lead/log/a3-2-2.json`. Its tripwire shows no change in W2-42a's trees; `git status` empty.
- **Round 1** (`PR-DAEO-03ub-round-1.md`, head e9e4f7bac) failed on F1 (a shell given an option with a value read
  its heredoc body as data; in scope, ordinary work yes, fails open). The fix round: an independent test designer's
  F1 cases (00e0b93e2; `fixtures/f1_shell_options.json`, the list the CTO reuses for the live hook's ACT-GUARD-FIX-5),
  a fresh engineer's fix (a4afc4166, 31201f0ad), and the two hook-fixture cases made strict xfails at the CTO's
  request (77cdf5993).
- **At this head:** acceptance 491 passed, 2 xfailed (strict); `gov accept W2-42a` 491 passed, 0 failed, 2 skipped;
  the scoped set GREEN (6385 tests, 0 failed, 8 skipped; serial 5 passed).
- **READY, by code.** The verdict block marks all 13 lines pass, with no finding. Round 1's rows F2, F3, F5, F7, F8
  and F6 stand as recorded Wave 3 rows; F4 is narrowed by the fix (`/dev/stdin`, `/dev/fd/0`, `/proc/self/fd/0` now
  read as a shell; `bash -c 'bash' <<EOF` remains, ordinary work no).
- **Outside this ticket:** the live hook's copy of F1 (`.claude/hooks/bash_writes.py`) is the CTO's ACT-GUARD-FIX-5;
  the two strict xfails turn red when it lands, and its companion removes them.
- **Judgement: pass.**

## The reviewer's record (as returned)

**Sandbox check (Step 0):** both parts passed.
- (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-03ub` was refused (`OSError: [Errno 30] Read-only file system`).
- (b) `git hash-object -w --stdin` gave `1ae28402…` (exit 0), and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing, at the start and at the end.

**Head probed:** bb2caf31789a359fe4ba48134bc8e816473fce94 (`git rev-parse HEAD` matches) in /home/usain/gov-os-worktrees/W2-42a. **Session id:** probably 77822768-7673-4779-bf81-08afc3516d2f (taken from this session's sandbox task path, not confirmed).

task: DAEO-03ub (W2-42a), independent audit, FULL profile, review round 2 of 2 (the last; DEC-1010)

status: done. All 13 lines pass and round 1's F1 is closed, so the ticket is READY. Classification: 0 blocking findings, 0 new rows. Round 1's rows F2–F8 stand as recorded; the fix narrowed F4 and left the others unchanged.

work_completed:
- **Read:** round 1's record, the diff since round 1 (e9e4f7bac..bb2caf317), the new `_kind` / `_shell_script` / `_script_words` and the places that use them (write walk, `script()`, `_may_run`, `read_view`, and `reads.py` through `read_view`), the F1 acceptance file and its fixture, and the evidence paragraph.
- **Three-way comparison:** I took the base (7c6a7427), round 1's head (e9e4f7bac) and this head from git history into $TMPDIR. I ran 4,201 commands through each tree's `_extract_bash_write_targets` and `read_view`.
- **F1 spellings, write side and read side:** 47 shell heads, each in 5 forms: quoted delimiter, unquoted delimiter, `cat <<EOF | <head>`, `<head> <<EOF | tee`, and `<<-`.
  - The heads include `-euo pipefail`, `-e -u -o pipefail`, `-o errexit` (sh, dash, zsh, ksh), `-O extglob`, `+o posix` and `+O`, `--rcfile f`, `--init-file f`, `--noprofile --norc -eo pipefail`, `-euxo`, `-eEuo`, `-o errexit -o nounset -o pipefail`, `-s -- a b`, `-`, `--`, `/dev/stdin` and `/proc/self/fd/0`, and the prefixes timeout, env, nice, command and nohup.
  - **Write side:** all 235 forms give both body targets at the head; round 1's head gave none for most of them.
  - **Read side:** `read_view` now keeps the body as commands in 230 forms. The other 5 are `/usr/bin/env bash …`, which is read as code at both heads (round 1's row F5, unchanged).
- **Fail-closed check of `_kind`:** I compared round 1's `_kind` with the head's on every option list of up to 4 words, from 26 words, for bash and sh: about 1.2M lists. None went from shell to data; 279,740 went from data to shell.
- **Real-shell check of the remaining data readings:** for each list the head still reads as data, I ran real `bash` and `sh` with a marker on standard input. That was every two-word list plus a random sample of 4,000 three-word lists per shell. The shell never ran its standard input in any of them. The marker check was first confirmed on known shell readers.
- **Broader comparison:** 3,900 generated heredoc commands, mixing 39 readers, 10 write bodies, pipes in front and after, `cd`, redirects, and a script written then run.
  - Against round 1's head, no command lost all its targets and no read-side body was dropped.
  - 9 commands lost one target: the `bash -euo s2.sh` form, covered under discoveries.
  - Every command that gained a target has a reader that really reads its input or really runs the script.
- **Failure line F2 inside shell-with-options bodies:** 44 unparseable or unknown forms (unbalanced quote, `eval "$X"`, `sh -c "$X"`, unterminated inner heredoc, loop over a substitution, nested heredocs). Each gives a target or the unresolvable target, and the read side keeps every body.
- **Scope of the round's commits:** the engineer's two commits touch only `src/gov/guard/bash_writes.py`, `tests/unit/guard/test_w2_42a_*` and `docs/changes/W2-42a-evidence.md`. The designer's two touch only `tests/acceptance/W2-42a/**`. The trailers are `Role: engineer` / `Role: independent-test-designer` / `Role: orchestrator`, with no `Decided-by`.

files_changed: none. `git status --porcelain` is empty at the end.

evidence: my scripts are under $TMPDIR/a2 (run.py, cmp.py, gen1.py, gen2.py, gen3.py, kinds.py, oracle.py), with outputs c1.out, c2.out, c2.json.res and newdata.json. The three source trees are in $TMPDIR/a2/{base,r1,new}.

tests:
- The brief's command through the heavy slot (`tests/acceptance/W2-42a tests/unit/guard`, `-m "not local_only" -k "not real and not green_here and not time_limit"`): **1060 passed, 2 xfailed** in 24.6 s. The 2 xfails are the strict hook-fixture cases that name ACT-GUARD-FIX-5.
- **What was left out:** 961 cases were deselected. All of them come from `tests/conftest.py`'s opt-in lists (`tests/optin-lifted-guard*.txt`: the lifted test_decide classes, test_protected, test_runs, test_tools, test_records and the breadth rows), not from my filter. No acceptance case was deselected (493 collected).
- **Opt-in run:** `tests/unit/guard` with `--optin=lifted,breadth`, same filter, through the heavy slot: **1530 passed**.

discoveries:
- **The F1 fix also closed a script-run gap.** Round 1's head also missed the body of a script written then run as `bash -euo pipefail run.sh`: it took `pipefail` for the script name, so it gave only `run.sh` and the read view cut the body. The `_script_words` change closes this; the head gives the body's targets and keeps the body.
- **`bash -euo s2.sh` loses its body targets, correctly.** At the head, `cat > s2.sh <<EOF … EOF; bash -euo s2.sh` no longer gives the body's targets; `s2.sh` itself is still a target. Real bash takes `s2.sh` as the value of `-o` and exits 2 ("invalid option name") without running it; dash does the same. So this is a correct reading, not a fail-open.
- **Round 1's F4 is narrower.** `/dev/stdin`, `/dev/fd/0` and `/proc/self/fd/0` now read as shell. `bash -c 'bash' <<EOF` still reads as data; that part of the row is unchanged and still ordinary work no.

risks:
- **The live hook still has the F1 gap.** `.claude/hooks/bash_writes.py` and the copy in the fixture still allow an engineer's `bash -euo pipefail <<EOF` that writes the acceptance folder; the strict xfails show it. This is outside W2-42a's paths and is the CTO's ACT-GUARD-FIX-5, so it is not a finding against this ticket.
- **Over-reads, which fail closed:** a shell given an option the guard doesn't know, or an unterminated inner heredoc in a shell body, is read as commands. This can refuse a harmless command. It never lets a write through.

lessons: none new.

proposed_decisions: none.

unresolved:
- The Write tool asked for a permission this session could not grant for `$TMPDIR` (once for each of two files). I wrote the probe files with Bash heredocs under `$TMPDIR`, each with a unique delimiter, as the brief directs. No guard refused any call.
- zsh and ksh were not covered by the real-shell check.

recommended_next_action: land W2-42a on this verdict (READY: no blocking finding at the head). Keep F2, F3, F5, F7 and F8, and F4 as narrowed, as Wave 3 rows. Drop the two strict xfails when ACT-GUARD-FIX-5's companion lands.

**Findings**

None this round. I re-raise none of round 1's rows F2–F8: the fix changed only F4, and only by narrowing it.

**What I probed and found sound**
- **F1 is closed for every spelling**, directly and through a pipe, on both the write side and the read side.
- **The floor holds:** every shell reading round 1's head gave is still a shell reading.
- **No new data readings let a stdin-run shell through:** none of the data readings left at the head is a shell that real bash or sh runs from its input.
- **No target or body lost against round 1's head** in 4,201 commands, beyond the correct `bash -euo s2.sh` reading.
- **Unknown forms still fail closed** inside option-bearing shell bodies.
- **The other lines S2–S5 and S7–S11 still hold:** their acceptance cases pass at the head, as do the 155 planted cases and the 53 `base_caught` writes.
- **Roles stayed in their paths:** the engineer did not touch the acceptance tests.

```verdict
{"kpis": [
{"kpi": "S1", "verdict": "pass", "findings": []},
{"kpi": "S2", "verdict": "pass", "findings": []},
{"kpi": "S3", "verdict": "pass", "findings": []},
{"kpi": "S4", "verdict": "pass", "findings": []},
{"kpi": "S5", "verdict": "pass", "findings": []},
{"kpi": "S6", "verdict": "pass", "findings": []},
{"kpi": "S7", "verdict": "pass", "findings": []},
{"kpi": "S8", "verdict": "pass", "findings": []},
{"kpi": "S9", "verdict": "pass", "findings": []},
{"kpi": "S10", "verdict": "pass", "findings": []},
{"kpi": "S11", "verdict": "pass", "findings": []},
{"kpi": "F1", "verdict": "pass", "findings": []},
{"kpi": "F2", "verdict": "pass", "findings": []}
]}
```

**What would reverse this verdict:**
- A shell option list the head reads as data where real bash or sh runs its standard input. None turned up among all two-word lists and 8,000 sampled three-word lists.
- An ordinary command for which round 1's head or the base gave a target the head now drops, other than a script name that bash itself takes as an option value.

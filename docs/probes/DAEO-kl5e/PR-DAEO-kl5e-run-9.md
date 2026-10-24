---
type: probe
task: DAEO-kl5e
reviewer_session: a167d26a-1658-4a40-8a41-f9c2f0792b16
implementer_session: d5d425fa-5790-4340-8e17-9e72c616f73c
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 6a3d3bfd1af5f18dc81f7a71b73eb983c77619de
---

# Probe record: W2-50, run 9's fresh FULL probe on the integrated head, after W2-58 changed the same files (DEC-894)

## What was probed
- Head `6a3d3bfd` on `w2/W2-50`: the merge `95fb5070` of `w2/integrate` at `c4f2b303` (parents `b9a5e5cd` and `c4f2b303`, tree equal to git's own merge), then the lead's checkpoint record CP-DAEO-kl5e-0051. W2-50's code was not changed in this round (DEC-894 item 2). The question: do W2-50's durable scratch root in the guard and the launcher's sandbox (DEC-728) and its secrets scan (DEC-853) still hold as the KPIs say, now that W2-58 (Policy 2, DEC-820, DEC-821, DEC-873, DEC-880) has rewritten `src/gov/guard/decide.py`, `src/gov/guard/protected.py` and `src/gov/launch/launcher.py`?
- The reviewer was a fresh read-only session (independent-auditor, session a167d26a-1658-4a40-8a41-f9c2f0792b16, 2026-10-22, `--effort max`), launched sandboxed. The code under test was this worktree's `src/` (DEC-732). The ticket's last implementer was session d5d425fa-5790-4340-8e17-9e72c616f73c.
- **The guard.** 129 decisions through the project's own hook, with a temporary HOME and own folders opened by `gov launch` with a stand-in CLI.
  - Own-folder writes by Write, Edit, MultiEdit, NotebookEdit and Bash. Paths given absolute, with a leading `~`, with `$HOME` and `${HOME}`, relative after a `cd`, and with the hook's working folder inside the own folder.
  - Every KPI refusal, in the same spellings.
  - Policy 2's read routes against W2-50's writes: pipes, `tee`, `rg` fed by a pipe, interpreter in-place edits, shell globs, symbolic-linking copies, prefix commands, and reads that also write.
- **`protected.py` after W2-58's rewrite.** All 91 cases of the one-reader rule (DEC-778), with the rule that refused each. W2-58's changes to `test_protected.py`, `test_protected_one_reader.py` and `tests/acceptance/W2-50/test_w2_50_one_reader.py` (`bfc290f3`, with its Rewrite-Reason).
- **The launcher's sandbox.** Eight `gov launch` runs with the stand-in CLI, for every role, a ticket with no W2 id, and a path map with an `evaluation_sets` block. Each checked the write list, the deny list, the own folder made on first use, and survival across launches.
- **The secrets scan.** Its code is unchanged since the last probe (`git diff 56240ffb HEAD` is empty on `src/gov/secrets/__init__.py`, `src/gov/guard/runs.py` and the check's declaration). Six runs of the declared check in a temporary project, each with a canary made at run time.
- **The merge and the probe gate.** `95fb5070` against git's own merge; the merge back onto `w2/integrate`; `eb0f1454`'s conflict; the gate's own readers, run read-only.
- **Suites, in the reviewer's sandbox:**
  - W2-50: 636 passed (its 3 large scan cases run alone);
  - `tests/unit/guard`: 1054 passed;
  - `tests/unit/launch`: 138 passed;
  - `tests/unit/secrets`: 26 passed;
  - `tests/acceptance/W2-58`: 803 passed. Its 5 live-session cases did not pass: the sandbox has no route to the model API.
- **Suites, the lead's own run at this code, outside the sandbox:**
  - the same W2-50 and unit counts;
  - the close's parallel run of `tests/`: 15,465 passed; red only W1-42's two accepted reds, plus two W1-38 rulesync timeouts under load that passed alone;
  - the serial-only cases: their reds passed alone; they came from load and from the file system running out of inodes for a while;
  - `gov check`: exit 0, with secrets-indexing GREEN.

## What it found
- **F1 (medium as a route; older than W2-58).** For an unsandboxed session, Bash writes in shapes the write reader does not read reach another ticket's folder under `~/gov-os-runs`. These shapes are prefix commands (`env`, `command`, `timeout`), runners (`find -exec`, `bash -c`, `xargs`), reads that also write (`sort -o`, `dd of=`, `rsync`, `tar -x -C`, `git -C … init`) and interpreters. Every plain write form is refused in every spelling. The Bash write reader is byte-identical to the one at `56240ffb`. A launched worker's sandbox write list holds only its temp folder and its own folder. Existing rows: W2-H057, W2-M023, W2-H055. Under DEC-779, a row.
  Ordinary work: no, because reaching another ticket's folder needs a wrong destination and a write shape the reader does not read at once; every ordinary write shape is judged in every spelling.
  Consequence: fails open (for unsandboxed sessions only).
- **F2 (low; older than W2-58).** A symbolic-linking copy (`cp -s`) of another ticket's file into the own folder, followed in the same command by a write through the new name, is allowed. For `ln -s` the guard also judges what the link names, and refuses. Unsandboxed sessions only. Rows: W2-H013, W2-H057.
  Ordinary work: no, because it needs a link to another ticket's file and a write through it in one command.
  Consequence: fails open (for unsandboxed sessions only).
- **F3 (low; accepted rows).** `perl -pi` and `sort -o` can rewrite the own folder's marker. Every form the reader sees is refused. The folder is then not opened by later launches, and its files stay on disk. Rows: W2-M363, W2-L349, W2-L354 (W2-M362 for the silent launch).
  Ordinary work: no, because an honest agent does not edit the marker, and a bulk edit would have to match its text.
  Consequence: other (fails closed; nothing is lost).
- **F4 (medium as a route; W2-58's semantics, not specific to W2-50).** Policy 2 (c) refuses the engineer's reads of its own acceptance tests in the project. It does not reach a clone of the project in the own folder or the temp folder: a launched worker could clone there and read them. This is the class of W2-58's own probe finding 3 (tool copies of the protected tests outside their folder). The temp folder gives the same route, so W2-50 adds no new class.
  Ordinary work: no, because the clones DEC-723 puts under the root are of product repositories, and an honest engineer has no reason to clone this repository to read tests it is refused.
  Consequence: fails open (for Policy 2 (c)).
- **F5 (low; process; decided behaviour).** `eb0f1454`'s only conflict was `governance/project/path-map.yaml`; its combined diff on W2-50's paths is empty. The gate measures each merge after the probed commit against git's own merge of its parents (DEC-754). It fell back to "the probed code" only because the path map conflicted. Without that conflict, run 8's probe would have passed the close although W2-58 rewrote the files it judged. The same holds for a later clean merge, for example W2-69's work (FULL, open, `src/gov/secrets/**`), if it merged before W2-50's close. Covered by DEC-895 item 2 (a fresh probe ordered at merge time) and row W2-M403 (DEC-790).
  Ordinary work: yes, because two tickets changing the same file and merging cleanly is ordinary.
  Consequence: other (the gate works as decided; no write is let through and no work is lost).
- **DEC-866 note.** In W2-58's rewrite of `tests/acceptance/W2-50/test_w2_50_one_reader.py` (`bfc290f3`), the test names (`…_are_refused_as_reads`, `…_is_refused_as_a_read_…`) and the helper `assert_refused_as_a_read` still carry the framing of DEC-508 and DEC-525. DEC-820 and DEC-821 item 3 superseded that framing. The assertions no longer enforce it. At this head all 91 cases are refused by the second-name rule (DEC-821 item 4), so no KPI or decision in force loses a check.

## Found sound
- **Own folder, every role** (engineer, test designer, orchestrator, product-spec, auditor, research, a ticket with no W2 id, a suffixed W2 id): writes are allowed in every spelling. From the own folder as working folder, ordinary reads and tools are allowed: W2-58's read rules refuse no ordinary own-folder work.
- **Every KPI refusal, with the guard's reason, in every spelling:**
  - another ticket's folder;
  - the root: a file in it, `rmdir`, `rm -rf` (also after `cd ~`), `mv`;
  - `..`, symbolic links, folder links and hard links;
  - the marker;
  - no, empty or unknown ticket;
  - outside the repository: HOME, elsewhere, `~` alone, `~user`;
  - `~/gov-os-workbench` and other worktrees;
  - a ticket's folder used by another ticket's session.
- **`~` expansion (W2-58's `841f8479`):** a `~` that cannot be expanded (no HOME) is refused. Globs over `~/gov-os-runs` are expanded and refused.
- **`reads.py`** returns only refusals, so it never skips the write judgement. Its own write check applies only to the held-out list and the settings file.
- **The one-reader rule (DEC-778)** holds: 91 of 91 cases are refused; plain copies stay allowed.
- **The launcher:**
  - The write list is exactly the session's temp folder and its own folder, for every role. It never holds the root, another ticket's folder, the workbench, the worktrees or HOME.
  - The own folder and its marker are made on first use, and the folder's contents survive a later launch. A folder made by hand gets no marker and is not opened.
  - The evaluation-set block adds no Read rule (DEC-873). The deny list is otherwise unchanged.
- **The secrets scan:**
  - the canary is named and never printed;
  - a clean result is reused by its hash;
  - a one-byte change is scanned again;
  - a link into `~/gov-os-runs` is not followed;
  - nothing under a temporary root is scanned or indexed.
- **The merge:**
  - `95fb5070` equals git's own merge, and nothing of either side was dropped.
  - The merge onto `w2/integrate` is clean and leaves W2-50's paths as at this head. The reviewer checked this at `89f043e2`, the lead at `efa2e4b0`.
  - The newer commits on `w2/integrate` touch none of W2-50's paths.
- **The probe gate:**
  - With this record, the records probed `fc9e6a2a…` and `56240ffb…` become earlier rounds.
  - `eb0f1454` and `4845b9b8` lie before the probed head.
  - The checkpoint and probe record paths are not the ticket's work.
  - Nothing was found that would refuse a passing record committed by the orchestrator role alone.

## The lead's notes (judged by the orchestrator role, from the reviewer's return)
- Judged under the judgement rules (`governance/project/briefs/JUDGEMENT.md`), DEC-779, DEC-790 and DEC-801.
  - F1 to F4 are "Ordinary work: no", so they are rows. F1 and F2 are reachable only by unsandboxed sessions; F3 matches accepted rows; F4 is in the class of W2-58's probe finding 3.
  - F5 is "Ordinary work: yes" with "Consequence: other", the gate as decided, covered by DEC-895 item 2 and row W2-M403.
  - No finding is both reachable in ordinary work and failing open or losing work.
- The tripwire around the reviewer showed changes only in other trees: two orchestrator commits, `17515bba` and `efa2e4b0` on `w2/integrate` in the main tree, and `70e41fff` in the record worktree. Nothing changed in this worktree; `git status --short` was empty before and after.

## Judgement
- **pass.** W2-50's durable scratch root in the guard and the launcher's sandbox (DEC-728), and its secrets scan (DEC-853), hold at `6a3d3bfd1af5f18dc81f7a71b73eb983c77619de` as the KPIs say, W2-58's changes included. F1 to F5 are rows or decided behaviour, returned to the orchestrator.

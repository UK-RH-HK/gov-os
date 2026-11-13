# ACT-CONTEXT-WATCH-1: register the context watch (W2-176's PostToolUse hook) so it runs live for every session (DEC-1140 (1)(b))

- **For:** the owner's yes, then the owner's operator **by hand** tonight (the operator agent does not run 01:00-08:00); class (b)
  by the rule table. About two minutes in the main tree, **after W2-176 has merged** (section 3).
- **By:** an ACT-preparation helper of the CTO (Sonnet, high; RUBRIC-2, class C1). **Nothing live was changed or started:** no commit,
  no stage, no live settings, no `~/.claude`. Built and rehearsed in clones (section 6). **Not yet independently reviewed** (section 7).
- **Under:** DEC-1140 (1)(b) (the owner's order of 11-11: a session that hands over before compaction, live for the CTO's, the leads'
  and the workers' sessions); DEC-1118 (A) (leads and workers hand over by 200,000 tokens); DEC-315 (class (b): `.claude/` and
  `.rulesync/`); CAP-33 (W2-176's CIT-P, section 5: this registration is the ACT that follows the owner's approval). The manifest's
  `dec` names them.
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/context-watch-1/` (the bundle is `acts/ACT-CONTEXT-WATCH-1/`; the tools in
  `tools/`, the rehearsal `tools/rehearse.sh`).

## 0. Class: (b) by the table; by your operator's hand tonight. Your yes first
**The yes line: `yes ACT-CONTEXT-WATCH-1 487c93c1`** (the first 8 digits of the manifest's sha256 in section 3).

I read `governance/project/operator/class-rules.yaml` first and ran the operator's own `act_class.py` (read only) on the bundle:

| File | Row | Class | Control path |
|---|---|---|---|
| `.claude/settings.json` | `settings` (a hooks block alters a control) | b | yes |
| `.rulesync/hooks.jsonc` | `rulesync-other` (`.rulesync/**`) | b | yes |

The vote is **(b)**. Since the operator agent does not run tonight, the steps are yours by hand (section 5); the bundle is still in the
operator's form (manifest, `apply.sh` deciding by sha256, a rehearsal log, checks run with `bash -c`), so the agent could take it in the
morning from the same bytes.

## 1. What changes, and why
W2-176 (merged first) adds `template/governance/kernel/hooks/context_watch.py`: a PostToolUse hook that, once per context window at 85 %
of the session's window (the CTO's session: its model's window; every lead and worker: at most 200,000), injects a note telling the
session to write its checkpoint, update its files and begin its compaction summary with the read-first line. It stops nothing and sets no
threshold. Without a registration it never runs. This ACT is the registration, and nothing else:

| File | Change |
|---|---|
| `.claude/settings.json` | one new `PostToolUse` block (12 lines added, none removed): matcher `Bash`, one command hook, `timeout` 10. The command is the PreCompact entry's command word for word with `precompact.py` replaced by `context_watch.py` (the pinned `gov` interpreter with `-E`, the script by its template path under `$CLAUDE_PROJECT_DIR`) |
| `.rulesync/hooks.jsonc` | the same entry as `postToolUse` (8 lines added, none removed): `settings.json` is generated from this source, so both change together; adapter-portability (a `hard-block` check) compares them byte for byte |

Nothing else moves: the other five events, the permissions, the deny list, every other file. `template/.rulesync/hooks.jsonc` and
`template/governance/kernel/settings.json` (adopted projects) are **not** touched. **It touches none of the other files of tonight's four
ACTs** (`launch_now.sh`, `dispatcher.py`, `balancer.py`, the two orchestration test files, `stop_idle_check.py` and its test,
`.claude/templates/role-*.md`, `.rulesync/subagents/*.md`, `.claude/agents/*.md`, `.claude/skills/**`): rehearsal J1. It reads no file of
theirs either, so it can go before or after them.

### The one decision for you: the matcher is `Bash`, not every tool
You asked for a matcher covering all tools. I built it and the repository's own check refused it (rehearsal F2): the template's hooks
source (`template/.rulesync/hooks.jsonc`) has `postToolUse` with matcher `Bash` (the lifted `posttooluse.py` line), and
`python3 -m gov.adapters.portability` compares the two sources' matchers per event (DEC-805; an event only the template has is excused,
DEC-971 item 3, but one both have is compared). A matcher of `*` gives `HOOKS_MATCHER_DIFFERS` (and `GENERATED_DIFFERS` if the sources
are not regenerated); that check is `hard-block`, tier G1, so it would turn `gov check` red for every ticket. With matcher `Bash` the
two sources have equal matcher lists and the check stays green (F1, I4, I8). Three costed options (DEC-105):

- **(a) Apply now with `Bash` (built; recommended).** Cost: the reminder is evaluated after each Bash call only, not after a Read, Edit
  or Grep. Every session of every role runs Bash all the time (tests, git, `gov`), and a reminder at 85 % only needs one call in the
  last 15 % of the window (30,000 tokens of a 200,000 window; 150,000 of the CTO's 1,000,000); a long run of Read and Edit calls with no
  Bash call delays it to the next Bash call. The hook itself is unchanged.
- **(b) Defer for all tools.** All tools needs one change to `src/gov/adapters/portability.py` (excuse a matcher superset for a lifted
  event, or make the template's source carry the same list), a ticket with its own tests (`tests/unit/gitenv/test_hooks_lifted.py` pins
  today's rule) and CIT-P if it touches the kernel; it ends by itself when W2-08 returns `postToolUse` to both sources. Not tonight.
- **(c) Apply with `*` and the check red.** Refused: a red hard-block check blocks every close.

If you want (b) later, the follow-up is a second ACT that changes the matcher in the same two files, on this ACT's after bytes.

## 2. Plain-language summary for the owner
After this, in every session of the repository (the CTO's, a lead's, a worker's), when the session has used 85 % of its context window,
the next Bash call carries one extra note: write your checkpoint now, update every file that needs it, and open your compaction summary
with "READ FIRST: <your checkpoint>". It appears once per window (again after a compaction, once usage has fallen below 50 %), it is
worded as a handover aid and not a stop, and the session carries on. Subagents' calls are skipped. If the hook cannot read the
transcript or anything else goes wrong, it says nothing and the tool call goes on. The cost is a hook process on every Bash call
(18 ms median on this machine for the registered command, wrapper included).

## 3. The bundle and the order
**The order (the entry criterion).** This ACT applies **after W2-176 has merged into `w2/integrate`**, because the hook file must exist
at its template path. Registered while it is absent, every Bash call would run a missing script: the pinned interpreter exits 2 with
`can't open file '.../context_watch.py'`, a blocking error shown on each call (rehearsal B6). So `apply.sh check` **and** `apply`
refuse (exit 6, nothing touched) unless `template/governance/kernel/hooks/context_watch.py` exists and its sha256 is the one the owner
approves in W2-176's CIT-P (section 2): **`c6dabb5eed394c89c31aae40a9466185355cfb3d161c44284c863c636559607c`** (rehearsal B1, B2, C5,
C6). `undo` and `verify` need no such file. W2-176's own merge is the CTO's and the queue's; the operator checks it in section 5's first
step (the hook file's sha256) and stops if it is not there.

`manifest.json` sha256: **`487c93c13e1b6ee2f223c5386fbb5cc38101737be200e94e4583aeb52350e58f`** (sha8 `487c93c1`).

| File | sha256 (first 16) |
|---|---|
| `before/repo/.claude/settings.json` | `8f1a3ef183f2953f` (the live file at the build; also `w2/integrate`'s) |
| `after/repo/.claude/settings.json` | `2a319ea4284a9184` |
| `before/repo/.rulesync/hooks.jsonc` | `43b51cd7c5794401` (the live file at the build) |
| `after/repo/.rulesync/hooks.jsonc` | `fbd5ddff1a4d1b0f` |
| `apply.sh`, `list.txt`, `rehearsal.log` | `620fbbe0dd08b95c`, `dc0c123e3cce8035`, `7818755bc72449d8`; in the manifest's `files` |

The after copy of `settings.json` is what `rulesync generate` writes from the after source (with the held-out step), not a hand edit:
adapter-portability reads it as drift-free.

`apply.sh check | apply | undo | verify`, by `list.txt` (`root|path|before|after`): each file's state is decided by its sha256 alone
(before, applied, other). **Every file is read first; if one is neither the before nor the after, nothing is written** (exit 3). Each
frozen copy is hashed against `list.txt` before it is used (exit 4). Writes go to a `mktemp` file beside the target, the mode kept,
then a rename; no temp file is left. A link or a missing file is refused. `check` is exit 0 only on the before and with the hook file in
place; `verify` only on the after.

**Checks** (the manifest's five, each run with `bash -c` from the repository root; none needs pytest, which the operator's planted HOME
hides; none writes byte-code; each leaves at most a small `mktemp` folder in the temp directory): 0 both files parse (JSON; the source
with its comment lines stripped); 1 the registration (the events in order; `PostToolUse` one block, matcher `Bash`, one hook, timeout
10, its command equal to the PreCompact command with the script swapped; the same entry in the source; the other events one block
each), count 6; 2 the hook file is there as the approved bytes; 3 the hook's behaviour as the registration runs it (the interpreter with
`-E`, planted project and transcript, a worker: 50 % and 84 % silent; 85 % one `additionalContext` with `READ FIRST:` and "not a stop",
no decision key; the next call none; a fall to 40 % re-arms; a subagent's event, a missing transcript, a cut assistant line and an empty
event all silent, exit 0), count 7; 4 the two files are tracked. **Check 1 is red on the old files** (rehearsal C).

**Undo:** `bash $A/apply.sh undo` puts both files back byte for byte (section 5), then a commit with the same trailers. Sessions that
loaded the new hooks keep running the hook until they restart (section 8); it is harmless without effect on the file.

## 4. The tests (no new cases: W2-176's carry the behaviour)
This ACT adds no test file. It reruns W2-176's 65 unit cases and the suites that read the repository's settings, hooks source and
portability, on the applied state (section 6, H).

## 5. The operator's steps: the message
> **ACT-CONTEXT-WATCH-1 (DEC-1140 (1)(b)): register W2-176's context watch as a PostToolUse hook (matcher Bash).**
> Class (b), by hand, **after W2-176 has merged**: your yes first: **`yes ACT-CONTEXT-WATCH-1 487c93c1`**. In the main tree, about two minutes:
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> test -z "$(git status --porcelain)" && test ! -e .git/MERGE_HEAD && echo clean     # expect: clean
> sha256sum template/governance/kernel/hooks/context_watch.py   # expect c6dabb5eed394c89c31aae40a9466185355cfb3d161c44284c863c636559607c (W2-176 merged)
> A=.gov-runtime/scratch/orchestrator/acts/ACT-CONTEXT-WATCH-1
> sha256sum $A/manifest.json     # expect 487c93c13e1b6ee2f223c5386fbb5cc38101737be200e94e4583aeb52350e58f
> bash $A/apply.sh check         # exit 0: "state before; template/governance/kernel/hooks/context_watch.py in place as approved"
> bash $A/apply.sh apply         # exit 0
> bash $A/apply.sh verify        # exit 0
> git diff --name-status         # expect exactly two M: .claude/settings.json and .rulesync/hooks.jsonc
> git commit -m "ACT-CONTEXT-WATCH-1: register context_watch.py as a PostToolUse hook, matcher Bash, so every session hands over before compaction (DEC-1140 (1)(b))" --trailer "Task: DAEO-ktiw" --trailer "Implements: DEC-1140" --trailer "Role: owner" -- .claude/settings.json .rulesync/hooks.jsonc
> ```
> - **If the first `sha256sum` shows no file or another hash,** W2-176 has not merged (or not as approved): stop, apply nothing, tell the CTO.
>   (`apply.sh` refuses by itself with exit 6.)
> - **If `check` stops** ("moved: <path>"), send its line to the CTO and apply nothing (`apply.sh` writes nothing).
> - **If `git diff --name-status` lists anything besides the two,** commit anyway: the `--` paths limit the commit.
> - **Undo:** `bash $A/apply.sh undo`, then the same `git commit` with the subject `ACT-CONTEXT-WATCH-1 undone`.
> - No restart of anything is needed for the files; running sessions pick up the new hook at their next start (section 8).

**Then the CTO:** after the commit, run `python3 -m gov.adapters.portability` from the repository root (expect `"findings": []`), and
watch the first session that passes 85 % for one `Context watch:` note.

## 6. The rehearsal (`rehearsal.log`; 97 ok lines, `failures: 0`)
As the operator will run it (`tools/rehearse.sh`): a `--no-hardlinks` clone of `w2/integrate` (the main tree's head at the build), then
`git merge --no-ff --no-edit 3a580a4b4d42` (W2-176) **in the clone only**, a planted HOME, the clean environment of the operator's dry
run, each manifest check run exactly as written with `bash -c`, the plain `apply.sh apply` with no option. The pytest runs go **one
folder per run** through the heavy-slot gate (`heavy_slot.sh env TMPDIR=<outside the repository> PYTHONUSERBASE=... PYTHONPATH=<clone>/src
python3 -m pytest <folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`), each parsed from pytest's own summary line
(exit 0, passed above 0, no failed). In order:

- **A** the bundle is not stale: the clone's and the main tree's two files are the frozen before; the hook file is absent before the merge.
- **B** the order: `check` and `apply` refuse with exit 6 and write nothing; `verify` refused, `undo` a no-op; **the registered command on
  a tree without the file exits 2 with `can't open file`** (B6).
- **C** W2-176 merged in the clone: the hook file is the approved sha256; the merge left both files as the frozen before; a hook file
  with one extra line: `check` and `apply` refuse (6); then `check` exit 0; check 1 red on the old files.
- **D** baseline on the merged clone, before the apply: adapter-portability no findings; `tests/unit/hooks` 166 passed, 1 skipped.
- **E** the plain apply: both files the frozen after byte for byte, modes kept (644), `git status` exactly the two (12 and 8 lines added,
  none removed), no temp file left, `verify` 0, `check` refused after, a second `apply` changes nothing.
- **F** the five checks as written (counts 6 and 7); adapter-portability after the apply: **no findings**; the same with matcher `*` in the
  source: **`HOOKS_MATCHER_DIFFERS`** (F2, the reason for section 1's decision).
- **G** the registered command run on planted PostToolUse events (a worker, `GOV_ROLE` engineer, a transcript at 90 % of a 200,000
  window): **one `additionalContext`** (exit 0, no stderr; it holds `READ FIRST:` and the not-a-stop sentence), **none on the second call**,
  one more after a fall to 40 %, none for a subagent's event; the hook wrote one file, the session's marker under
  `.gov-runtime/scratch/context_watch/`.
- **H** the tests on the applied state: W2-176's two unit files **65 passed**; `tests/unit/hooks` **166 passed, 1 skipped**;
  `tests/acceptance/W1-29` **42 passed**; `W1-49` **71 passed, 1 skipped**; `W2-62` **43 passed**; and the suites that read settings,
  hooks sources and portability: `tests/unit/adapters` 94, `tests/unit/gitenv` 61, `tests/acceptance/W2-05` 30, `W2-59` 48, `W2-65` 14,
  `W2-106` 26 passed; the tests left exactly the two applied files modified.
- **I** undo byte for byte and the clone clean; portability clean after the undo and the re-apply; one file moved: `check`, `apply` refuse
  (3); a half-applied state finished by `apply` and taken back by `undo`; a tampered frozen copy: exit 4, nothing written; a missing file
  and a link refused.
- **J** none of the other ACTs' files; the live files unchanged; the planted HOME empty; the classifier votes (b).

**The log has no head, pid, date or duration** (the pytest counts only; the pinned interpreter's path is shown as `PINNED`).

**Differences from the real run:**
- It is a clone of the head at the build; the files are checked by sha256, so a later head that leaves the two files alone changes
  nothing; one that edits either makes `apply.sh check` refuse and the bundle is rebuilt. **If other ACTs tonight commit first, nothing
  changes here** (disjoint files, J1).
- In the real run W2-176 has merged by the queue (a merge commit with its own trailers), not by `git merge` in a clone; the hook file's
  sha256 is the same bytes either way (C2), and `apply.sh` checks it.
- No operator gates G1-G9 ran (by hand tonight).
- The registered command ran against a planted project folder (the clone's `template/` linked in), never the live repository, so no marker
  was written under the live `.gov-runtime`.
- The pytest runs used the user's own HOME (the planted one hides the user-site pytest); no manifest check needs pytest.
- Not rehearsed: a live Claude Code session loading the hook (no session was started). The event and output shapes follow W2-176's CIT-P
  section 1 (the documentation as read there).

## 7. The review, residuals
- **Not independently reviewed.** The CTO may start the independent auditor (a fresh read-only session; it should run section 5's `check`
  and the five checks in its own clone, and read section 1's matcher decision first).
- **R8 of W2-176** (the window's marker is made before the reminder text is built; a failure building it, only possible with a partial copy
  of the hooks folder, spends that window's reminder silently) is a recorded row of W2-176, not an entry criterion here: `apply.sh`
  requires the approved bytes of the hook file, and the hooks folder is whole in a merged tree.
- `template/.rulesync/hooks.jsonc` and the template's `settings.json` do not carry the registration: adopted projects get the hook file
  from the kernel but no registration until W2-08 or the follow-up of option (b).

## 8. Risks, honestly
- **The reminder is evaluated after Bash calls only** (section 1). A session with no Bash call between 85 % and the window's end gets no
  note; the PreCompact line (W2-176 S1, already live) still tells the summary to open with the read-first line.
- **Sessions already running keep the hooks they loaded** (to my knowledge Claude Code reads the settings' hooks at a session's start, and
  may ask to review a changed hook in `/hooks`); the CTO's and the leads' current sessions get the watch at their next start or resume.
  I did not test this: it is the documentation as I know it, not a rehearsal result.
- **A hook process on every Bash call.** 18 ms median for the registered command here; the hook reads the transcript's last 256 KiB only
  (W2-176 S3: median 24 ms on a 50 MB transcript). `timeout` is 10 seconds; a hang is cut there and is non-blocking.
- **If the hook file is later removed or renamed** (a rename, a bad merge), every Bash call runs a missing script and gets exit 2 (B6).
  The ACT cannot guard against a later change; W2-176's file is in the kernel template, which is class (b) to change.
- **The pinned interpreter form.** The command is the PreCompact line's form, so a session without `gov` pinned gets exit 1 with a one-line
  message on each Bash call (non-blocking), as the Stop and PreCompact hooks do today. A plain `python3` line would avoid that and run on an
  unpinned interpreter; I kept the repository's own form so the three hooks behave alike.
- **The 1M-window models:** a lead or worker is reminded against 200,000 (DEC-1118 (A)), the CTO against its model's window (DEC-1140 (4)).
  A CTO session on a 1M model is reminded at 850,000 tokens.
- **The marker files** live under `.gov-runtime/scratch/context_watch/` (ignored by git); they are removed when usage falls below 50 %.

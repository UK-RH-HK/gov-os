---
type: probe
task: DAEO-wnnz
reviewer_session: "independent-auditor subagent of the CTO session b2f0511f-891b-4874-8930-6d34ca5972ea (close review, 2026-11-13)"
implementer_session: "8709adbe-df11-4c35-b700-999b41c3bb9c"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 94132594a02ab39adad785b5f4b46612b5f00560
decisions_applied: [DEC-794, DEC-799, DEC-801, DEC-803, DEC-808, DEC-1010, DEC-1083, DEC-1084, DEC-1098, DEC-1112, DEC-1114, DEC-1073]
---

# Probe record: W2-56 (DAEO-wnnz) `gov launch` usable for every worker: the close review of the merged code at w2/integrate 94132594a02a

## Who probed, and on what

- **Who probed.** A fresh, read-only independent auditor, a subagent of the CTO's session. It wrote none of W2-56's
  code or tests. The implementer sessions were the engineer's round 1 (`7084d6cc-3667-43e1-b860-da3c14e5c614`), round 2
  (`8709adbe-df11-4c35-b700-999b41c3bb9c`, named above) and the follow-ups R3/R5 (`69a3698a-5c4f-459b-b63e-9e0de0c18dc5`).
  The earlier reviewers were `6cbd7c46-4ecb-44a6-823f-589a263cd512` (round 1, `reviews/w2-56.md`) and the follow-ups'
  reviewer (`reviews/w2-56-f.md`).
- **What was probed.** `w2/integrate` at `94132594a02ab39adad785b5f4b46612b5f00560`, W2-56's whole merged result: the
  first build, the follow-ups R3/R5 (`4bc040898`), and what other tickets changed in W2-56's files after that (W2-153's
  template flag, W2-177's signal set-up in the supports, W2-52's/W2-92's/D-10's additions to `_CBM_SUITES`).
- **This is the close review** asked by DECIDED-NOT-DONE rows 30 and 81. It takes R2, R4 (round 1) and F2, F3 (the
  follow-ups' review) explicitly, re-runs the real-sandbox cases and S7's real case alone, and judges DEC-794's gate (a)
  as D9-FATES re-homes it.

## What I ran

Everything ran in a clean clone of `w2/integrate` at the probed commit under `/tmp/claude-1000/w256close-*/`, removed at
the end. `PYTHONPATH` was the clone's `src`, an absolute path. `TMPDIR` was outside the repository and outside
`~/gov-os-runs`. Every run went through `heavy_slot.sh`.

| Run | Result |
|---|---|
| `tests/acceptance/W2-56/` whole, without the opt-in | **292 passed, 4 skipped** (174 s). The 4 skips are the real cases. |
| The 4 real cases with `GOV_W2_56_REAL=1` (S2, S9, S7, S13), together, gate open | **4 passed** (18.7 s, 07:23 UTC) |
| S7's real case alone, run 1 | red: inside a running session, a command's sandbox failed with `bwrap: Can't find source path …/.git/config.lock`. This is the CLI's own per-command placeholder fault that S7 names as a Wave 3 row (W3-P29), not a start failure. |
| S7's real case alone, runs 2 and 3 | **passed**, **passed** |

- **Earlier attempts.** The same cases were tried earlier, between 06:38 and 07:20, while the CTO's W2-111 bench held the
  load at 20 and then 50. Each attempt was refused by the resource gate (`LAUNCH_REFUSED: the resource gate is shut`,
  cpu 20.03/20, then load 52.74/20). These are gate waits, not results. S2 passed in the one session the gate let
  through at 06:38. I re-ran after the bench ended (pid wait).
- **Seen live (read-only).** At 06:40 I read the running W2-88 engineer session (pid 2779791, started through `gov launch`).
  Its `--settings` sandbox block was enabled, `failIfUnavailable` true and `allowUnsandboxedCommands` false. The write
  list held exactly its temp folder, its run folder and `~/.cache/gov-os/rerank.log`. One socket was allowed (the
  reranker's) and no domain. The env keys were exactly `PATH`, `HOME`, `LANG`, `LOGNAME`, `TMPDIR`,
  `CLAUDE_CODE_TMPDIR`, `GOV_ROLE`, `GOV_TICKET` and `GOV_STORE`.
- **One direct probe.** I called the launcher's argument check in the clone on the context arguments (see A2).

## Probed and found sound

1. **S1.** The daemon folder is chosen in this order: the variable, then the launched session's folder (`<tmp>/cbm`, found
   from `CLAUDE_CODE_TMPDIR`), then the mark, then the default. The conftest makes one folder per run and removes it at
   the end. R3's owner record is a `flock` held for the run's life, so a killed run's folders are removed by the next
   run. Today's S13 real case showed it working inside a real sandboxed session: the suite's daemon folders lay under the
   session's temp folder, and `gov check --list` and the suite ended 0. Rows: A1, F2, F3.
2. **S2, S3, F1.** Seen live and in the code, the write list is today's three entries and nothing else.
   `/tmp/gov-cbm-<uid>` is never on it, and no entry comes from `allowed_paths`. Today's S2 real case passed: the
   operating system refused a script's write into a sibling worktree and into `tests/acceptance/`. The script-write gap
   inside the worktree is named in CIT-E §2. CIT-E §1 states how each allowed-path form is held.
3. **S4, F3.** The common exclude file holds the placeholder names, each with its folder exception, and the literal deny
   names that do not exist at launch. A repository whose exclude file cannot be written is not launched into. Row: R2.
4. **S5, F3.** The environment passes by a list of names, not a filter. The sign-in variables reach the CLI process only,
   never `--settings`. Seen live: none of the parent's `CLAUDE*`, `GOV_DEV_TIERS` or `PYTHONPATH` reached the engineer's
   settings. R5 holds: a lead gets the launcher's own `GOV_STORE`, never the parent's.
5. **S6.** The probe confirmed that `--restricted`, `--safe-mode`, `--agents`, `--plugin-dir`, `--plugin-url`,
   `--mcp-config` and `--system-prompt` are refused in the bare, spaced and `=` forms, in any position. CIT-E §3 weighs an
   accepted-arguments list against this refusal list. Row: A2.
6. **S7.** The launcher's short start lock serializes the starts. Three sessions started at once all started and
   committed in 3 of 4 runs today. The fourth failed on the CLI's per-command `config.lock` placeholder inside a running
   session, which S7 itself assigns to Wave 3 (W3-P29, DEC-1112 (3)). It was not a start failure.
7. **S8, S9, F4.** The one socket path comes from the service's own setting. Any link on the way to it gives nothing.
   `faults` refuses unknown keys, `allowAllUnixSockets`, a second socket, another socket and a pattern. Today's S9 real
   case passed: a second Unix socket was refused and the listener saw no connection. S8's reach on Linux is deferred
   (DEC-1114 (1), W3-P28). Row: R4.
8. **S10.** Deferred to Wave 3 by the owner (DEC-1114 (1), W3-P28). Nothing of W2-56's is left to judge here, so it is
   marked pass as "deferred by decision".
9. **S11, F5.** The log is made with `O_EXCL` and `O_NOFOLLOW`. A link, or a file that is not regular, is left off the
   list. Live, W2-145's evidence (11-13) counts 223 FALLBACK lines since 11-12, and `gov status` reports the unranked
   count. Every fallback traces to the sandbox making `~/.cache/gov-os` read-only, which is W3-P28's reach, not S11's
   count.
10. **S12, S15.** The session leads its own process group, and each ending signals the whole group. The temp folder is
    removed in `finally` on every path, without following links. After today's real sessions, no `gov-launch-*` folder of
    theirs was left under `/tmp`. The only two left belong to a live W2-88 engineer and an older auditor.
11. **S13.** The real case passed today (see S1). `gov rebuild` inside the sandbox stays a Wave 3 row (P-1 (b)), and it
    fails closed.
12. **S14, F6.** The template's `permissions.allow` is exactly `["Bash(gov launch:*)"]`, and the rulesync source carries
    it. There is no raw `claude` allow.
13. **F2.** Every earlier refusal is kept. The new ones fail closed: the second `sandbox_faults` after the filesystem
    block, the exclude-write failure and `SubprocessError`.
14. **MR-3, DEC-430.** All nine commits that touch `tests/acceptance/W2-56/` carry `Role: independent-test-designer`. The
    engineer's commits stay inside the ticket's `allowed_paths`.

## R2, R4, F2, F3 taken explicitly

None of the four is met by a code change; each stays a row, unchanged at the probed commit, with an owner proposed for
the CTO.

- **R2** (S4): the exclude lines are permanent and repository-wide: no leading slash, so any depth. In the probed
  sandbox code they are as R2 describes. Still ordinary work no: nothing in this repository tracks or generates those
  names, and a sandboxed command cannot write them.
  - Proposed owner: a Wave 3 parking row. One line goes to W2-27's brief, because EXAMIN's copy gets the same exclude
    lines at its first launch (DEC-803: the risk exists only once a launch runs in another repository).
  - Reversed by: a ticket that legitimately creates and commits a new file at one of those names.
- **R4** (S9, F4): `faults` does not check the contents of `allowWrite` or `allowedDomains`; it is unchanged.
  - Proposed owner: an entry criterion of set-up B's Wave 3 row (DEC-803, DEC-1112 (1)). Once write entries come from
    the path map, a check of their contents matters. Today only the launcher's own code builds the lists.
  - Reversed by: a path where a caller-supplied value reaches those lists today.
- **F2** (S1): a killed run's `gov-path-*` folder under a one-off `TMPDIR` stays until a run with the same temp root starts.
  The conftest sweeps `tempfile.gettempdir()` only; it is unchanged.
  - Proposed owner: a row for DEC-902's weekly sweep (a Wave 3 parking line, the CTO's).
  - Reversed by: such a leftover being followed by a run, or filling the disk.
- **F3** (S1, out of scope): killed runs' `gov-rebuild-<pid>-*.lock` files are not swept. Six are in `/tmp` now. They are
  W2-76's lock files, not R3's folders.
  - Proposed owner: the same weekly-sweep row (the CTO's).
  - Reversed by: a leftover lock blocking a later rebuild. That cannot happen, because each process makes a new name.

## Findings

Classification: no finding is in scope, reachable in ordinary work, and fails open or loses work; every finding below is
a row. The earlier reviews' rows R2, R4, F2 and F3 are above.

- **A1 (S1). S1's words "the real code-graph daemon runs only in W1-16 and W1-20" no longer describe the code.** The
  conftest now keeps the tool on `PATH` for seven suites: W1-16, W1-20, W1-41, W2-52, W2-69, W2-92 and W1-06's digests
  file. Three of them came from D-10 run 1 group C (`843777f66`), briefed by the CTO under DEC-1122 (3). W2-92
  (`5fc7681a1`) and W2-52 (`d9028de12`) were added by their own designers. The per-run daemon folder and the cleanup
  still hold for all of them; only the list of suites drifted from the KPI line. `843777f66` was a test designer's edit
  of `tests/conftest.py`, an engineer path of this ticket. It was briefed by the CTO, so it was not a role straying on
  its own.
  - scope: in
  - Ordinary work: yes, because every full run executes those suites with the tool on PATH.
  - Consequence: other (more real-daemon runs, each in its run's own folder; nothing fails open or is lost).
  - Proposed owner: the CTO marks S1 `[changed]` and names the seven suites, citing the D-10 brief and DEC-1122 (3), or
    narrows the list.
  - Reversed by: a decision or a ticket annotation already in force that names these suites under S1.
- **A2 (S6). A caller's `--system-prompt-file` is accepted after `--`, and so are `--append-system-prompt` and its file
  form.** The probe called the launcher's argument check. CIT-E §3 names these "to be weighed with W2-60a". W2-60a's
  KPI now refuses `--append-system-prompt` and its file form, but `--system-prompt-file` is in neither ticket. The CLI's
  help lists it beside `--system-prompt`, which S6 refuses.
  - scope: in (the spirit of S6; the letter of S6 is met)
  - Ordinary work: no, because no launch tool passes it, and a worker would have to choose to add a system prompt file.
  - Consequence: other (context replaced or added; the guard hook, the sandbox and `--settings` stay).
  - Proposed owner: W2-60a adds `--system-prompt-file` to the arguments it refuses, or a Wave 3 row.
  - Reversed by: a decision that admits `--system-prompt-file` for workers.
- **A3 (S7, out of scope). S7's real case stays intermittent.** It went red in 1 of 4 runs today on the CLI's
  per-command `config.lock` placeholder. This is P-S7/R6, already W3-P29. The record states it only so that the close
  does not read a red as W2-56's.
  - scope: out
  - Ordinary work: yes, when sandboxed workers in one repository run at once.
  - Consequence: other (a loud failure of one command, then a retry).
  - Reversed by: a failure at the start of a session, which the start lock should prevent.

## DEC-794's gate (a), as D9-FATES re-homes it

**GREEN.** Gate (a) is section (a) of the quality-control check: "workers sandboxed through `gov launch`". DEC-794 states
it; DEC-799 item 4 and D9-FATES §3 (DEC-1083, DEC-1084) re-home it to W2-56's close. Evidence:

1. `launch_worker.sh` starts every worker through `gov launch`. Before the launch it dry-runs the launcher's refusals and
   `sandbox_faults` on the built settings and refuses on any fault (exit 4). After the session ends it checks the
   `.sandbox-trial-<ticket>` file and the tripwire.
2. The live W2-88 engineer runs sandboxed with today's exact block (seen 06:40, above).
3. The real cases passed today: the OS refused a script's writes outside the session (S2) and a second Unix socket (S9).
   A code-graph suite and `gov check` ran inside the sandbox (S13). So DEC-799 item 3's fallback, the old launch form
   for workers whose suites need the code graph, is no longer needed.

What gate (a) does not cover, by its own words: leads (orchestrator sessions) are still started outside `gov launch` with
no sandbox (`launch_when_gate_opens.sh`, a raw `claude -p` with `--settings` holding the identity only). This is the
decided state: DEC-1098 (4) and DEC-1112 (1), set-up B in Wave 3. It is not a worker.

Register note: DEC-794's own status is DONE ("a one-off act, finished": DEC-1098 (3), W2-130's sitting), while DEC-1083
(D9-FATES) and DEC-799 item 4 still make its section (a) W2-27's gate. Both ids are named here (DEC-1073 rule). DONE is
neither superseded nor PROPOSED, so the gate is judged as DEC-799 item 4 and D9-FATES state it. This is a register
hygiene row for the CTO (ordinary work yes, consequence other): DEC-794's entry could point to the re-home.

## For the close (not a finding on W2-56)

`gov close` in this project is the scoped close (`governance/project/close.yaml`: `close: scoped`). It computes READY from
this record's verdict block and accepts the block only if the commit that last wrote it carries `Role:
independent-auditor` alone (W2-115 S11, `review_verdict`). A commit with `Role: orchestrator` is refused as
`VERDICT_NOT_REVIEWER`; the unit case "a lead writing over the reviewer's verdict is refused" pins this. Without a record,
the scoped close refuses `VERDICT_MALFORMED`, not `PROBE_MISSING`; `PROBE_MISSING` is the strict close's code. The strict
close's probe gate wants the opposite role, `Role: orchestrator`, on every commit of the record. No FULL ticket has closed
through the scoped `gov close` so far: every FULL close since W2-115 went through the merge queue or a recorded close. The
frontmatter above also satisfies the strict gate.

```
task: W2-56 (DAEO-wnnz), the close review: a FULL read-only probe of the merged code at w2/integrate 94132594a02a, judged on S1-S15 and F1-F6, with R2, R4, F2, F3, the real cases and DEC-794's gate (a)
status: DONE; 21 lines pass; no finding is in scope, ordinary work yes and fails open or loses work
work_completed: read the ticket whole, both earlier reviews, D-10's effects review, the CIT-E, sandbox.py, environ.py, launcher.py's launch path, codeintel's daemon base, the conftest's R3 code, the template; ran W2-56's acceptance suite and the real cases in a clean clone; read the live engineer's settings; probed the argument check
files_changed: none in any tree; this record's draft only (in scratch, see the return)
evidence: clone at 94132594a02a under /tmp/claude-1000, removed at the end; main tree git status clean at the start and the end; read refusals 0; write refusals 1 (the draft folder under drafts/, see the return)
tests: tests/acceptance/W2-56 292 passed, 4 skipped; the 4 real cases 4 passed; S7's real case alone 2 passed, 1 red (W3-P29's per-command config.lock); earlier attempts refused by the resource gate during the W2-111 bench (waits, not results)
discoveries: A1 (S1's list of suites drifted to seven); A2 (--system-prompt-file unrefused by W2-56 and W2-60a); the scoped gov close's reviewer-role rule for the verdict block; DEC-794 DONE while its gate (a) is in force via DEC-799 item 4 and DEC-1083
risks: S7's real case stays intermittent until W3-P29; leads stay unsandboxed until set-up B
lessons: a KPI line that names suites goes stale when other tickets widen the list; mark it changed when they do
proposed_decisions: none needed; owners proposed for R2, R4, F2, F3, A1, A2
unresolved: who commits this record with Role: independent-auditor so that the scoped close reads READY
recommended_next_action: commit this record under docs/probes/DAEO-wnnz/ in a commit whose Role is independent-auditor alone; file the rows; close W2-56; W2-27's gate (a) green
```

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "A1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "R2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": [{"id": "A2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S7", "verdict": "pass", "findings": [{"id": "A3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S8", "verdict": "pass", "findings": []}, {"kpi": "S9", "verdict": "pass", "findings": [{"id": "R4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S10", "verdict": "pass", "findings": []}, {"kpi": "S11", "verdict": "pass", "findings": []}, {"kpi": "S12", "verdict": "pass", "findings": []}, {"kpi": "S13", "verdict": "pass", "findings": []}, {"kpi": "S14", "verdict": "pass", "findings": []}, {"kpi": "S15", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": [{"id": "R2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F4", "verdict": "pass", "findings": [{"id": "R4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F5", "verdict": "pass", "findings": []}, {"kpi": "F6", "verdict": "pass", "findings": []}]}
```

---

task: DAEO-wnnz
decisions: DEC-794, DEC-799, DEC-801, DEC-803, DEC-808, DEC-1010, DEC-1073, DEC-1083, DEC-1084, DEC-1098, DEC-1112, DEC-1114, DEC-1122
probed_commit: 94132594a02a

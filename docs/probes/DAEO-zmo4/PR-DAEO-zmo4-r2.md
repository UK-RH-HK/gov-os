---
type: probe
task: DAEO-zmo4
status: final
reviewer_session: ba5def67-a55d-420e-bd7c-6924c378002a
implementer_session: 2f1c9b8c-8ee4-4687-9748-cd1e9fb3d24d
first_implementer_session: 02c77f05-209f-4519-afe5-9e9e4afeb1da
test_designer_session: 10c9d616-60e2-44af-897c-dcb89aaedaf8
test_designer_batch_sessions: [4337e067-051e-4699-8c09-8fb336b1af86, 92a3afeb-a643-4948-9e7b-e71feb056134]
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 66026a90391c8746d52319ea7478e41fd158d5a4
round_base_commit: aa717e110cfd
decisions_applied: [DEC-1188, DEC-1130, DEC-1083, DEC-1050, DEC-1121, DEC-1122, DEC-801, DEC-802, DEC-803, DEC-808, DEC-809, DEC-1010, DEC-820, DEC-1154]
scope: "W2-174 FULL reopen (DEC-1188), review round: the launch fields S6, S7, F4 of the Verify pass, and S1-S5, F1-F3 still holding"
---

# Probe record: W2-174 (DAEO-zmo4), the FULL reopen's review round at 66026a90391c

## Summary

- **What was probed.** Head `66026a90391c8746d52319ea7478e41fd158d5a4` of `w2/W2-174`, from the reopen's base
  `aa717e110`: the engineer's `f3daf80ee` (the six launch fields in `src/gov/adopt/verify_pass.py` and `command.py`,
  unit tests `tests/unit/adopt/test_w2_174*`; session `2f1c9b8c`, continuing `02c77f05`'s uncommitted unit tests), and
  the independent test designer's `24c37a68b`, `5d9ae4661` (128 new cases in `tests/acceptance/W2-174/`, session
  `10c9d616`) and `9edcca3b0` (the README map read whole, session `4337e067`), merged by the lead at `e005850eb` and
  `66026a903`.
- **Who probed.** A fresh read-only independent auditor (`claude-opus-5-5`, effort high, class C2), session
  `ba5def67-a55d-420e-bd7c-6924c378002a`, started through `launch_worker.sh` (`gov launch`, its OS sandbox, Bash, Read,
  Grep and Glob only), with `governance/project/briefs/JUDGEMENT.md` word for word in its brief and the interface the
  lead stated to both workers (L10 to L17). It wrote nothing (`git status --short` empty; launcher tripwire clean).
- **The lead's evidence.** `gov accept W2-174` at `66026a90391c` (with `W2_174_BASE=aa717e110`): 222 passed, 0
  failed, every line reported (S1 9, S2 15, S3 2, S4 36, S5 12, S6 11, S7 96, F1 15, F2 2, F3 6, F4 20), none unmapped.
  `lead_verify` at the same head: 7,425 tests, 2 failed, 8 skipped (1,913 s):
  `tests/acceptance/W2-174/test_w2_174_scope.py::test_f2_the_adoption_stages_and_w2_152s_acceptance_folder_are_unchanged`
  (the auditor's F5: a stale built-in base; fixed after this review by the test designer's `ffd6d8b03`, merged at
  `c7000431f`, under a narrow re-check, DEC-1154) and
  `tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request`
  (load-sensitive: alone, 1 passed in 0.33 s; not this ticket's).
- **Verdict.** Pass on all eleven lines; READY by the verdict block (no finding in scope with ordinary work yes and
  fails open or loses work). Six findings, all rows, no round (DEC-1010 item 1).

## The lead's triage (the auditor's verdict stands as written)

- **F1** (in scope, ordinary work yes, other: fails closed). In a wheel install of gov the ticket schema cannot be
  read (`pyproject.toml` ships no `_shipped/template/governance/kernel/schemas/`, and `jsonschema` is not a declared
  dependency), so every apply is refused `VERIFY_PASS_SCHEMA`, label-only applies included. The fix lies outside this
  ticket's paths (`pyproject.toml`, package data): an entry criterion of release 0.1.1's packaging (DEC-803), for the
  CTO. Until then the pass runs from a source checkout.
- **F2** (in scope, ordinary work no, fails open). An answered `role` is not checked against `allowed_paths` the
  ticket already has; reaching it needs a hand-edited ticket holding `allowed_paths` without `role`. A Wave 3 row;
  rides along if the ticket resumes (DEC-802).
- **F3** (out of scope: L16). tk writes no `state_class`, so a ticket made by `tk create` is refused
  `VERIFY_PASS_SCHEMA`. For the owner or the next ticket on the pass (adding `state_class` to the fields written).
- **F4** (in scope, other). `**` is refused for an orchestrator ticket, as S7 reads; EXAMIN's answers file names
  narrower paths for `exa-dt1z`. A row.
- **F5** (out of scope, other). The F2 stages case's stale base: fixed after this review (`ffd6d8b03`), checked by
  the narrow re-check.
- **F6** (in scope, ordinary work no, other: fails closed). A front matter ending in a `|+` block scalar is refused
  `VERIFY_PASS_EDIT_FAILED`. A row.

## The auditor's return, word for word

**Pass.** 0 blocking findings and 6 recorded rows: F1, F4: in scope, ordinary work yes, other. F2: in scope, ordinary work no, fails open. F6: in scope, ordinary work no, other. F3, F5: out of scope, other.

Sandbox check (Step 0, `EMG-d4b-launched.md`): (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zmo4` failed with `OSError: [Errno 30] Read-only file system`, and no file exists. (b) `git hash-object -w --stdin` worked (1ae28402…) and `git update-index --refresh` exited 0. The `ps` check for ollama or llama-server showed nothing, at the start and at the end.

Identity: `git rev-parse HEAD` = `66026a90391c8746d52319ea7478e41fd158d5a4`. Engineer and test-designer commits are separate by their `Role:` trailers. The engineer's commit (f3daf80ee) touches only `src/gov/adopt/{verify_pass,command}.py` and `tests/unit/adopt/test_w2_174*`. Nothing under `tests/acceptance/` was written by the engineer.

## Findings

**F1: the schema check refuses every apply when gov is installed from a wheel, label-only applies included.**
- **What:** `_validator` looks for `ticket.schema.json` and `common.schema.json` in two places. One is a parent folder of the module that holds `template/governance/kernel/schemas/`, which only a source checkout has. The other is `gov/_shipped/template/governance/kernel/schemas/`, which `pyproject.toml` does not package; `_shipped/` holds only `governance/project/…`. Also, `jsonschema` is not a declared dependency (only `PyYAML>=6`). The pinned `gov` on PATH (`~/.local/share/gov-os/pin-076cded14882`) is a wheel install, and it gets `jsonschema` only through `include-system-site-packages = true`.
- **How I reached it:** I copied `src/gov` alone to `$TMPDIR/probe/inst/gov`, which is what an installed wheel looks like, and ran `apply` on fixture repos. A label-only apply (S1 on a ticket with all six fields) and a six-field apply were both refused `VERIFY_PASS_SCHEMA: the kernel's ticket schema cannot be read (looked in: …/no-source-tree/…; …/_shipped/template/governance/kernel/schemas)`. Nothing was written. From the source tree, both succeed.
- **Why it matters:** the checks fail closed, as intended. But the release DEC-1188 ships in (0.1.1), installed as a wheel, can apply nothing, and that includes the S2 label pass that worked before the reopen. So W2-27 would still stop.
- **KPI lines:** S6 (and S2/S3 in an installed gov).
- `Ordinary work: yes, because the EXAMIN CTO runs the installed gov, not the source tree`
- `Consequence: other (fails closed: every apply refused, nothing written)`
- **Scope:** in. **Disposition:** an entry criterion of the 0.1.1 packaging (DEC-803): package the two schema files under `_shipped/template/governance/kernel/schemas/` and declare `jsonschema`. Then repeat this probe on a built wheel.
- **What would reverse it:** a 0.1.1 wheel that carries both schema files and declares `jsonschema`, where a label-only apply succeeds.

**F2: an answered `role` is not checked against `allowed_paths` the ticket already has.**
- **What:** the acceptance-path check only looks at *answered* `allowed_paths`. A ticket that already has `allowed_paths: [tests/acceptance/**]` and lacks `role` can be answered `role: engineer`. The apply writes the role, the schema passes, and the ticket is marked `verify_pass`. The result is an engineer ticket whose paths reach `tests/acceptance/`, made by a permission field the apply wrote. L13's "the answered role, else the ticket's own" covers the reverse case only.
- **How I reached it:** fixture `existing_paths` in `$TMPDIR/probe/p1.py`. The result was `OK ['abc-a001']`, with the role lines inserted after the existing paths.
- **KPI line:** S7.
- `Ordinary work: no, because nothing in an adopted repository writes allowed_paths without role: tk writes neither, the apply writes all six at once (UNANSWERED otherwise), the operator's script writes both; it needs a hand-edited ticket`
- `Consequence: fails open (the pass's own check; the kernel guard's gov.guard.decide still drops tests/acceptance/** patterns from a non-test-designer's scope)`
- **Scope:** in. A row for the Wave 3 hardening pass. If the ticket resumes anyway, the fix rides along (DEC-802): when `role` is answered, check every pattern the ticket will hold.
- **What would reverse it:** a refusal (`VERIFY_PASS_ACCEPTANCE_PATH`) on this fixture.

**F3: a ticket created by tk can never be passed.**
- **What:** tk writes no `state_class`, and the schema requires it. The six fields don't include it, so any tk-created ticket is refused `VERIFY_PASS_SCHEMA` (fixtures `no_state_class`, `aon_schema`, `label_only_nostate`). The A5 review ticket in the operator's script needed `state_class: AUTHORITATIVE` inserted by hand.
- **Why it stands:** this is L16's stated design, so it holds as specified. But in an adopted repository the apply only serves tickets like A0's coordination ticket, not new tickets made with `tk create`.
- **KPI line:** S6.
- `Ordinary work: yes, because every new ticket in an adopted repository comes from tk create`
- `Consequence: other (refused, nothing written)`
- **Scope:** out (L16; state_class is not one of the six fields). A row for the owner or the next ticket that touches the pass.
- **What would reverse it:** tk writing `state_class`, or a decision adding it to the fields the pass writes.

**F4: the operator's `allowed_paths: ['**']` for the coordination ticket cannot be reproduced with the apply.**
- **What:** under the lead's decision, `**` is refused for `orchestrator` (`VERIFY_PASS_ACCEPTANCE_PATH`). That matches S7's text ("unless the role is independent-test-designer"). It is not a loss: nothing is written, and narrower paths work. `gov.guard.decide` already gives an orchestrator *session* `**` whatever its ticket says.
- **KPI line:** S7.
- `Ordinary work: yes, because the worked example writes exactly this`
- `Consequence: other (a refusal with a named code)`
- **Scope:** in. A row; the answers file for exa-dt1z must name narrower paths.
- **What would reverse it:** an owner reading that the orchestrator is exempt from S7.

**F5: the acceptance case for F2 has a stale built-in base.**
- **What:** `test_f2_the_adoption_stages_and_w2_152s_acceptance_folder_are_unchanged` uses the built-in base `f2b1d38af`. It fails on `src/gov/adopt/stages.py` unless `W2_174_BASE=aa717e110` is set.
- **How I reached it:** my run of the briefed command gave 497 passed, 1 failed. Re-run with `W2_174_BASE=aa717e110`, that file gives 7 passed. The `stages.py` change is W2-88's `fcfbd87f9`, integrated before the reopen. `git diff aa717e110..HEAD` names nothing under `src/gov/brief/`, the kernel templates or schemas, `stages.py`, `tests/acceptance/W2-152/` or the adopt skill.
- **KPI line:** F2.
- `Ordinary work: yes, because any runner without the variable sees it red`
- `Consequence: other (a false red, no false green)`
- **Scope:** out (test harness; the test designer's to fix).
- **What would reverse it:** a W2-174 diff naming `stages.py`.

**F6: a front matter ending in a `|+` block scalar is refused.**
- **What:** inserting the field lines changes the scalar's value, so the re-read refuses `VERIFY_PASS_EDIT_FAILED`. Nothing is written (fixture `blockkeep`).
- **KPI lines:** S2, S6.
- `Ordinary work: no, because ticket front matter rarely ends in a keep-chomped block`
- `Consequence: other (fails closed)`
- **Scope:** in. A row.
- **What would reverse it:** the apply writing such a ticket with a value that changed.

## Probed and sound
- **The acceptance-path rule** (on fixtures, engineer role). Refused: `**`, `tests/**`, `t*`, `tests/acceptance/**`, `tests/acceptance/W2-1/x.py`, `./tests/acceptance/x`, `tests//acceptance/x`, `tests/./acceptance/x`, `TESTS/Acceptance/x` (casefolded), `tests/acceptance`, `tests`, `tests/accept*`, `**/acceptance/**`, `*.md`, and a pattern with spaces around it. A `..` segment or a leading `/` is `BAD_FIELD`. Allowed: `src/**`, `tests/unit/**`, `tests/acceptance-old/**`. A role taken from the ticket (`engineer`, `[engineer]`, null, wrong case) is refused. The test designer, answered or already on the ticket, is allowed. The guard's matcher (`gov.util.patterns`) treats only `*` as a wildcard, so the pass's literal-prefix rule is never looser than the guard.
- **Field checks:** unknown role, non-string role, empty, string or blank-item `allowed_paths`, null `reads`, a bad `waits_on` item, `kpis` without `failure` or with an extra key, a missing verify, empty/`TBD.`/`n/a` verifies, `FIELD_SET`, `UNANSWERED`, a `state_class` key (`UNKNOWN_LABEL`), and a closed ticket. Each was refused with its code and the tree byte-identical.
- **All-or-nothing:** with three tickets where the last is bad, either by path or by schema, nothing was written.
- **Byte preservation** (difflib on lines): comments, CRLF, no trailing newline, an existing marker mid-way or last, an indented sequence, a flow continuation, trailing spaces on the closing `---`, and a `---` in the body. The only differences are the appended clauses, the inserted field lines in L10 order and the marker. The re-read refuses any other change.
- **CLI:** `--verify-list --json` text is `abc-c001 role allowed_paths kpis reads needs waits_on`. A refusal gives the API-0002 envelope and exit 1.
- **The lead's four decisions:** none of them fails open or loses work. The schema check on label-only applies is the right call under F4, but with F1 it disables the whole tool in a wheel install.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S7", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": [{"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}]}
```

- task: DAEO-zmo4 (W2-174), review round of the FULL reopen (S6, S7, F4), head 66026a90391c
- status: done; pass, no blocking finding
- work_completed: sandbox and `ps` checks; read the ticket, DEC-1188, L10 to L17, the operator's `operator_tickets.py`, `verify_pass.py`, `command.py`, the round's diff and commit trailers, the kernel guard's acceptance filter and pattern matcher, and the ticket schema. Ran fixture probes p1 to p4 under `$TMPDIR/probe`, plus an installed-copy simulation; ran the briefed test line.
- files_changed: none
- evidence: `$TMPDIR/probe/p1.py` to `p4.py`; `pyproject.toml` package-data; `src/gov/guard/decide.py` lines 101 to 118; `src/gov/util/patterns.py`; `git diff --stat aa717e110..HEAD`
- tests: briefed command gave 497 passed, 1 failed (F5), 120 deselected. The deselection (`-m "not local_only" -k "not real and not green_here and not time_limit"`) left out the real-model and time-limit cases. `test_w2_174_scope.py` with `W2_174_BASE=aa717e110` gave 7 passed. The lead's full suite was not run by me.
- discoveries: F1 (the schema files and `jsonschema` are not shipped); F3 (tk tickets lack `state_class`); a ticket file starting with a UTF-8 BOM is invisible to the pass (`UNKNOWN_TICKET`; this predates the reopen)
- risks: release 0.1.1 shipped as it stands cannot apply (F1)
- lessons: probe a fail-closed dependency (schema, library) from an installed copy, not only the source tree
- proposed_decisions: make F1 an entry criterion of the 0.1.1 packaging; the owner reads F3 (tk tickets and `state_class`)
- unresolved: whether the exa-dt1z answers file should name narrower paths than `**` (F4)
- recommended_next_action: lead commits this record and closes on the verdict. Rows F2, F3, F5 and F6 go to the Wave 3 hardening list; F1 goes to the 0.1.1 release ticket.

`git status --short` (worktree, at end): empty

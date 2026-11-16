---
type: probe
task: DAEO-wnnz
status: final
reviewer_session: a537d537-0cb2-48c4-98b3-13eee38b18a1
implementer_session: defbb518-771b-494a-816f-4cd9081192e6
test_designer_session: defbb518-771b-494a-816f-4cd9081192e6
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: b635c50ed42adae3827a276a4a067a75a4f956de
reviewed_commit: 99769aa51bf7
decisions_applied: [DEC-1154, DEC-1156, DEC-820, DEC-1052, DEC-801, DEC-802, DEC-808, DEC-809, DEC-1010, DEC-1073]
scope: "W2-56 narrow independent check (DEC-1154) of the 11-16 reopen (DEC-1156 (7)): S1's session-daemon case set-up revision since 99769aa51bf7 (the test designer's f31fba661, merged as b635c50ed42a); the assertion and S1's meaning unchanged"
---

# Probe record: W2-56 (DAEO-wnnz), the narrow check of S1's session-daemon set-up revision at b635c50ed42a

## Who probed, and on what

- **Who probed.** A fresh, read-only independent auditor (`gov launch independent-auditor`, Opus, effort high,
  session `a537d537-0cb2-48c4-98b3-13eee38b18a1`), brief `au-1` carrying JUDGEMENT.md word for word. It wrote no file
  (`git status --porcelain` empty at its end; its sandbox step 0 wrote one loose git object, as the step requires).
- **Whose work.** The independent test designer's revision (session `defbb518-771b-494a-816f-4cd9081192e6`, commit
  `f31fba6619d0871a4c04bee140f0ef4398b3ad64`), merged by the lead as `b635c50ed42adae3827a276a4a067a75a4f956de`. No
  engineer and no product change this round.
- **What changed.** One file, `tests/acceptance/W2-56/test_w2_56_session_daemon.py` (31 added, 8 removed): a
  `short_root` fixture makes the launcher's temp root `/tmp/w<8>` with `w2_56_sandbox_support.short_base("w")` and
  removes it in a `finally`; `_daemons` swaps the box's `tmpdir` for it; the module docstring states the new set-up.
- **Why.** The 11-16 nightly reddened `..._the_daemon_folder_is_under_the_sessions_temp_folder[*]` for all five worker
  roles: W2-88's 4ea9bc194 moves the code-index folder to `/tmp/gov-cbm-<uid>` when a socket under the session temp
  folder would pass 107 bytes (DEC-338), and the case built its stand-in session under pytest's long `tmp_path`.

## The two questions and the auditor's answers

1. **The set-up now matches a real launch: yes, closely enough, and only in the safe direction.** A real launch's
   folder is `/tmp/gov-launch-<8>` (`src/gov/launch/launcher.py:109` `TEMP_PREFIX`, `:1045` `mkdtemp`), 24 bytes; the
   stand-in's is `/tmp/w<8>/gov-launch-<8>`, 34 bytes. With `daemon_dir`/`socket_length` on fabricated environments:
   real root socket 95 bytes, stand-in 105 bytes (both under 107, folder not moved), fallback under a long `$TMPDIR`
   moved to `/tmp/gov-cbm-1000/…`. A longer stand-in can only make the "under" assertion falsely red, never falsely
   green. The fixture removes the root on every ending (nothing left after a 5-fail/5-pass run); no short root at all
   fails the case with a reason (`pytest.fail`), and a long fallback makes it red, never a pass.
2. **The assertion and S1's meaning are unchanged: yes.** Both tests change only their signature and the `_daemons`
   call; lines 74-77 and 83-90 are textually identical to the base; no skip, xfail or new mark; names unchanged. The
   sibling socket-room case now measures an unmoved folder (45 + 50 = 95 bytes) where at the base it measured the
   moved `/tmp/gov-cbm-…` and passed trivially: stricter, not looser. With `daemon_dir` placing the folder outside
   the session temp folder the case is red (shown by the auditor's own sandboxed run). No other W2-56 case touched.

## What was run

| Run | Where | Result |
|---|---|---|
| `test_w2_56_session_daemon.py` | lead, outside the sandbox, at b635c50ed42a | 10 passed (7.5 s); no `/tmp/w<8>` left |
| `gov accept W2-56` | lead, at b635c50ed42a | 19 of 20 lines pass; 292 passed, 0 failed, 4 skipped; S13's one case is the opt-in real case (`GOV_W2_56_REAL=1`), skipped here as README line 139 records |
| `lead_verify` (the scoped run, DEC-968) | lead, at b635c50ed42a | GREEN: 7200 tests, 0 failed, 0 errors, 10 skipped (915 s) |
| `test_w2_56_session_daemon.py` | the test designer, in its sandbox | 5 failed, 5 passed: `/tmp` read-only there, the root falls back to the long `$TMPDIR` and the folder moves (expected) |
| `test_w2_56_session_daemon.py` | the auditor, in its sandbox | 5 failed, 5 passed, the same reason; shows the case goes red when the folder lies outside |
| `tests/acceptance/W2-56/` whole | the test designer, in its sandbox | 5 failed, 278 passed, 1 skipped, 12 deselected; the same 5 only |

## Findings (rows; none blocks)

**N1.** The stand-in session's temp folder (34 bytes) is longer than a real launch's (24); its socket is 105 of 107
bytes, a 2-byte margin. A uid of 7 or more digits, or a `/tmp` reached through a link, would push it over and the case
would go falsely red. The docstring's "as short as a real launch's" is not literal.
(`tests/acceptance/W2-56/test_w2_56_session_daemon.py:16,51,63`; `src/gov/codeintel/__init__.py:60`)
- Ordinary work: yes, because a CI runner or directory-service account can have a long uid (not on this machine, uid 1000).
- Consequence: other (a false red, never fail-open)

**N2.** Where `/tmp` cannot be written the long fallback makes the "under" case red with a message that names the
moved folder but not the fallback; diagnosability only, the case fails closed.
(`test_w2_56_session_daemon.py:51-54,77`; `w2_56_sandbox_support.py:237`)
- Ordinary work: yes, because sandboxed sessions have a read-only `/tmp`.
- Consequence: other

**N3.** Clean-up is `rmtree(ignore_errors=True)`: a SIGKILLed run, or a folder that cannot be removed, leaves
`/tmp/w<8>` behind silently; on every ending observed nothing was left. (`w2_56_sandbox_support.py:245-247`)
- Ordinary work: yes, because killed test runs happen.
- Consequence: other (a small leftover in `/tmp`, no work lost)

Classification: 3 findings, all in scope, ordinary work yes, consequence other; 0 blocking (DEC-1010 item 1). They
ride along if the ticket resumes for another reason (DEC-802); no round.

The lead's judgement: pass. The block below is the auditor's, copied verbatim from its return
(`.gov-runtime/scratch/lead/log/au-1.result.md`); the lead writes no verdict over it.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "N1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "N2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "N3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```

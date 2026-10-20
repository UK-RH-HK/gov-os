---
type: probe
task: DAEO-6mk8
reviewer_session: d8062593-f33e-47cc-b645-a1cc45a52186
implementer_session: 95af66a4-44c2-410f-bed3-aef6f631ef81
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 065f9b83f011fb510563443ebf52de6c7f6013ab
---

# Probe record: W1-31 round, the session-log reader accepts any Claude Code version it can parse (DEC-655)

- **What was probed.** The round's code at `065f9b83` on `w1/W1-31b` (one session of a lead since
  `02b12017`): the reader of the harness session log without its exact-version pin, the version read
  returned in `agent.version`, four new types passed over by name, every other unseen form still
  "not measured" by name. The branch is merged directly at the probed head.
- **Who.** A fresh reviewer session started by the orchestrator through `gov launch independent-auditor`,
  read-only, other than the implementer. It wrote nothing to the repository; the worktree was at
  `065f9b83` and clean when it left.
- **What held.** On stand-in logs built from scratch (about 95 runs of `gov telemetry`):
  - logs in the first three specimens' forms give the reader's output of the code before the round,
    apart from the version;
  - eight forms that were "not measured" before the round are still "not measured" by name, with the
    same exit code and reason, at 2.1.288, 2.1.292 and 2.1.296, and no measured or total share is a
    number in a log that holds one;
  - the pass-over is by exact type name only; near names and other shapes are refused or "not
    measured";
  - a version that is not two to four dotted numbers is refused; a log that names no version is
    refused; another program's transcript gets no figure;
  - only the two files under `src/gov/telemetry/` changed; nothing of the close or of another command.
- **Findings and their judgement.** None for the merge. Lesser, named residuals for
  `governance/project/bootstrap.md` and the Wave 2 list: the four passed-over types are passed over by
  name and their real content is not shown by the reduced specimen; sessions of more than one version
  give a share with the version "not measured" and the versions read recorded nowhere (the lead's
  package G); `agent.version` can be null where the README says never; the close record does not
  carry the version; the version pattern takes non-ASCII digits; a type that is a list gives a
  traceback (as before the round); one misleading refusal reason; the harness's identity rests on form
  and on ccusage only.
- **Not probed, by the brief.** A real session log; a real 2.1.296 log; `gov close` end to end. The
  lead measured one real exit-run session (ORION-sp01, 2.1.292) through the command without a refusal.
- **Judgement.** Pass: no fail-open hole that ordinary work produces (no share reported as measured
  that was not), nothing that breaks a Wave 1 exit criterion (DEC-584).

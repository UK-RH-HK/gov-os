
## W1-31 round: the session-log reader accepts any Claude Code version it can parse (2026-10-13; DEC-655, DEC-663)

Probed head `065f9b83`, merged directly at `9495bf3a`. Built: the reader of the harness session log has no exact-version pin; it accepts a version of two to four dotted numbers and returns the version read in `agent.version`. The line type `file-history-delta` and the attachment types `instructions`, `sandbox_instructions` and `silent_turn_reminder` are passed over by name and count nothing. Every other form no specimen shows is "not measured" by name, at any version. 30 acceptance cases added, 1 rewritten (the refusal of another version became its measurement; reason DEC-655). Source lines: `src/gov/telemetry` +31 −20 against an estimate of 150. Probe: pass (`docs/probes/DAEO-6mk8/PR-DAEO-6mk8-round-DEC-655.md`). Residuals, all on the Wave 2 list:

- **Sessions of more than one version** give a share with `agent.version` "not measured", without a reason beside it, and the versions read are recorded nowhere (package G, DEC-663).
- **After a CLI update every log is "not measured"** until a fresh specimen is read and the new forms are given rules (package H, DEC-663). Four patch versions brought three new attachment types and one new line type.
- **`instructions` and `sandbox_instructions` lines count nothing**; whether they replace the estimate is open (package I, DEC-663).
- **The four passed-over types are passed over by name**; the reduced specimen shows their type and length only, not their real content.
- **`agent.version` can be null** where the suite's README says never; the close record does not carry the version.
- **The version pattern takes non-ASCII digits.**
- **A line whose type is a list gives a traceback** (as before the round).
- **An attachment of an unseen type that carries no version** is refused with "names no version", not named as an unseen type: the safe side, with a misleading reason.
- **The harness's identity rests on the log's form and on ccusage only.**
- **Not probed:** a real session log, a real 2.1.296 log, `gov close` end to end. The lead measured one real exit-run session (ORION-sp01, 2.1.292) through the command without a refusal.
- **The round's first checkpoint record is numbered `CP-DAEO-6mk8-0002`** in the round's worktree; no `0001` was written there.

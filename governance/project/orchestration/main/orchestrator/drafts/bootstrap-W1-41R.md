
## DAEO-cdoi (W1-41): the round of DEC-694, residuals for the Wave 2 list (2026-10-14; DEC-694, DEC-700, DEC-702)

Merged at `945643ec` after a probe PASS (`docs/probes/DAEO-cdoi/PR-DAEO-cdoi-round-DEC-694.md`). Adoption's stage A3 refuses (`ADOPT_EMBEDDING_POLICY`, nothing written) a project path map whose namespaces state another `embedding_policy` than `embedded` or `not embedded`, or none, or in which no namespace is embedded; `gov rebuild` and `gov doctor` say "no namespace is embedded". The two rulesync sources of the adopt skill were brought to the kernel skill (`a8cf8867`); the generated copy under `.claude/skills/` is applied by the operator (DEC-616).

- **A3 checks what namespaces state, not what retrieval embeds** (medium). A map whose embedded namespace is overlapped by a not-embedded catch-all, matches no tracked file, or (template-style) has no `paths` passes A3 with no file embedded, and rebuild and doctor stay silent. Fix: count the files the retrieval's per-file rule would embed, in A3 and in `none_embedded()`.
- **A3 does not pin the project path map's hash** (low): A6 and A8 go on after a later edit that embeds nothing; the rebuild's words in A6 and A8 say it.
- **The doctor's words sit only under its semantic canary's answer** (low): absent when the canary raises or gives no semantic entry.
- **A3's embedding check answers before its `--map` check** (info).
- **Sandbox placeholders seen during a sandboxed session** (info; DEC-693, DEC-697): eleven root dot-files as character devices `1,3` owned by `nobody`, and `docs/source`, in the worktree's status while the reviewer's session ran; gone after it; no containment finding.
- **Containment attribution during test design** (info; DEC-253, DEC-254): two `flagged` entries on the designer's two new files against the lead's waiting commands.
- **Learning metrics of the round:** KPI disputes 0; 119 W1-41 cases rewritten before implementation ("planned: behaviour ordered", one support default); 36 cases added, 12 of them controls that pass on the old code; 0 rewritten after implementation; source lines +50 against 80.

## DAEO-gjjf (W1-42) run 7: residuals for the Wave 2 list (2026-10-14; DEC-695, DEC-699)

- **`gov close`'s own trailer gate does not read `trailers_base`** (`src/gov/close/command.py`, `_check_trailers`; only `src/gov/close/traceability.py` reads it): the base clears `gov check` but not `gov close`. ORION-im01's second close (count 2 of 3) refused with `TRAILER_MISSING` on `540004a` alone, before a-dev's base `bb1852e`; DEC-690's close of DAEO-emkd refused on three commits all before this repository's base `1c33dd28`. With the owner as a package.
- **The repair ticket `ade-ke2y`** that the second close wrote in a-dev is open and incomplete; it turns a-dev's claims and schema checks red.
- **Context reproducibility with a live semantic index** (run 6, measured again in run 7): the context of a ticket differs between the first and later computations in one process (a-dev: ORION-gp01, ade-5rcs); `gov ci` is red on it.
- **The restart of 2026-10-14 (DEC-699):** live clones under `/tmp` are lost on a reboot; the operator backs them up after every run that changes one (DEC-698).

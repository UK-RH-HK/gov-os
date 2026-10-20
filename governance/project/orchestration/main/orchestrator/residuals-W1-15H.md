
## W1-15 round: the secrets-indexing scan in parallel, a check's own time limit, the template's hooks source (2026-10-10; DEC-595, DEC-596, DEC-601)

Merged at `bcce3d4f` (probed head `cddf5ee3`). Residuals, none a fail-open hole of ordinary work (Wave 2 list unless stated):

- **One gitleaks run can pass the module's own 60-second limit** on a slow or loaded machine with a large store. Fails closed. The figure on this repository's real store is the orchestrator's measurement.
- **A stated limit above about 2,147,483 seconds** is accepted by the declaration reader and then ends `gov check` with a traceback and no envelope. Fails closed; a deliberate shape. Fix: an upper bound in the reader.
- **YAML spellings of the limit:** `0x10`, `010`, `1_0` and `1:30` (read as 90) are accepted as whole numbers; a key written twice, the last wins; a misspelt key is ignored and the check keeps 60.
- **`gov check --list`** entries carry a sixth key when the limit is stated.
- **The commit hook waits for the whole scan** in a project with a large store (137 to 369 s on the lead's stand-in; before the round the same commit was refused at 60 s). Whether an agent's commit through Bash outlives its own tool limit there is not measured. Result caching is on the Wave 2 list (DEC-595).
- **A file deleted between the walk and its read, or a dangling link under the runtime folder,** makes the check red. Fails closed; a concurrent session's snapshots can produce it; the parallel form shortens the window.
- **The `PYTHONPATH` prefix of the hooks source's command lines** puts the product's `src` ahead of the installed package: a product package named `gov` there can silence containment. A deliberate or unusual shape, older than the round.
- **The relative command lines of the hooks source** (all seven entries, older than the round): from a subfolder each exits 2. With the owner as package P-38; measured on an adopted dev-tier clone.
- A check killed at its limit may leave child processes; no worker count is set for the scan; both large stores are held in memory at once; the figure 60 for a declaration without the key is held by no case; `5.0` as a limit is held neither way; the adapter-portability check does not read the template's hooks source.
- **For the exit auditor:** the test designer's commits `ac979053` and `7112564a` of this round carry no `Implements:` trailer (under later commits; no branch is rewritten, DEC-558). The orchestrator's commit `abcb3095` cites DEC-594 one commit before the register recorded it (a citation warning).

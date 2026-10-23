# Lens H's raw trial results, archived (owner, DEC-899 item 9, 2026-10-23)

These are lens H's completed trials as its own runner wrote them, on 2026-10-21 and 2026-10-22, in `/tmp/gov-os-assessment-H/logs/`. That folder does not survive a reboot, so the files are kept here and synced to `record/w2` (`main/evidence/lens-H/`). They are copied byte for byte. The summary that cites them is `governance/project/orchestration/packages/TOOL-TRIALS-2026-10-22.md`, under "Lens H's remaining trials".

| File | sha256 | What it is |
|---|---|---|
| `rest.log` | `8fa0655d5d7a7f55f9a3e4c86ceebb49c92aa3ca182d0a6831a87521f44d4a5e` | Lens H's rest run: the 32 planted faults and the 65 mutation items, as run by `run_rest.sh` |
| `analysis_a6.json` | `6754eaaf2fb3afbf2aa490b438ce532f4f2dddb9b04343c7568d260ac8277acd` | The planted-fault results: each selector's detection and recall |
| `analysis_b2.json` | `b3a231428722121d5fa2059ee46d2ca8ed6cb3c71d83ac29870fa5ff359ba454` | The mutation results |

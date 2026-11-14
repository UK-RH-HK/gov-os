Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-88b/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Independent auditor brief: W2-88b (DAEO-aks1), gov adopt's stage A5 on the copy of redis

You are a fresh **independent-auditor** session. You ran no stage of this adoption. Your one job is the verdict that `gov adopt --lite --stage A5` needs on **one copy's path map**: the independent review of the path map before any move (DEC-090; DEC-1176 (3) (a), the owner's choice). It is part of running gov adopt in the W2-88b smoke run. It is not a validation of the smoke run's result and **it judges the path map only, never memory** (no index, embedding, store or retrieval question is yours).

## The ground
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-aks1.md` (S4 is your line). The decision: DEC-1176 item (3) in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (grep by id only).
- The copy: `/home/usain/gov-os-runs/W2-88b/redis` (a clone of https://github.com/redis/redis at its pinned commit ee8e7f70152404649ac947157fd662d11b4a00d5). It lies under the ticket's runs folder; it is never this repository and never pushed.
- What the lead's session ran there, each committed by gov itself under `governance/adoption/` with `session: lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1`: the adopter's path map `governance/project/path-map.yaml` (committed before A0), then A0 (safety baseline), A1 (inventory), A2 (classification), A3 (target path map, from the adopter's proposal `/home/usain/gov-os-runs/W2-88b/redis-out/proposal.yaml`, which names no action, so every artefact is kept), A4 (batched plan). The copy's HEAD now: `4583708a93bcf9f33bcb2e1ddd359d604bc7ddf5`.
- The gate that reads your verdict: `/home/usain/gov-os-worktrees/W2-88b/src/gov/adopt/stages.py` lines 432-478 (`_verdict`, `a5`, `guard`); A3 and A4 are lines 207-425; the shared parts are `src/gov/adopt/project.py`. Read them first.

## What you judge
Whether the path map, as A3 recorded it and A4 planned it, lets the migration (A6) and the legacy retirement (A8) go ahead safely and as the product's rules say. At least:
1. every tracked artefact of A1's inventory is held by a namespace of the path map (A2's `unknown` list) — an unknown artefact blocks A6/A8 (CAP-06.c);
2. every namespace states `embedding_policy` as `embedded` or `not embedded`, and at least one says `embedded` (stages.py 326-345);
3. A3's `artefacts` are A1's inventory, each with an action the proposal gave or KEEP, no move into or out of a native package layout without its grounds (CAP-44.j), nothing under `governance/adoption/`;
4. A4's plan is exactly the plan A3's map yields (batches, dependents, retirements), and nothing in it moves, retires or deletes what it should not;
5. anything else in the path map or these records that would make A6 or A8 unsafe or wrong.
The map is the smoke run's adopter input, minimal by design (one namespace). Judge whether it is correct and safe for A6 and A8, not whether it is the best taxonomy. Say what you checked and how (commands, counts).

## What you write and commit (the only write you make)
Your session id: the value of `$CLAUDE_CODE_SESSION_ID` (`printenv CLAUDE_CODE_SESSION_ID`). The path map's hash: `sha256sum /home/usain/gov-os-runs/W2-88b/redis/governance/adoption/A3-target-path-map.md` (it must equal `6f9a287a72ac1062f1103651205e35d56ff74a810cdef715640a52e991f94d5a`, the hash of the A3 record as it stands; if it does not, stop and say so).
One file, `/home/usain/gov-os-runs/W2-88b/redis/docs/audit/A5-path-map-verdict.md`, written with one Bash call (`mkdir -p <copy>/docs/audit && cat > <copy>/docs/audit/A5-path-map-verdict.md <<'EOF' ... EOF`), then committed in the copy. `docs/audit/` is one of the independent auditor's own record folders the guard lets it write, inside the copy (a run clone under ~/gov-os-runs is a tree of the project); the folder `governance/reviews/` was refused by the guard on the first attempt and is not to be tried. Its front matter, exactly these keys:
```
---
id: AV-A5-redis
type: adoption-verdict
status: ACTIVE
state_class: EVIDENCE
stage: A5
verdict: pass            # or fail; only pass passes
path_map: governance/adoption/A3-target-path-map.md
path_map_hash: <the sha256 above, 64 hex>
auditor_session: <your session id>
checked:
- {record: governance/project/path-map.yaml, sha256: <its sha256 at HEAD>}
- {record: governance/adoption/A1-inventory.md, sha256: <...>}
- {record: governance/adoption/A2-classification.md, sha256: <...>}
- {record: governance/adoption/A3-target-path-map.md, sha256: <...>}
- {record: governance/adoption/A4-batched-plan.md, sha256: <...>}
---
```
then a body: `# AV-A5-redis`, what you checked and found, each finding with its file and line or record key, and the verdict's reason. No repository content beyond paths and counts; never a secret's value.
Commit it alone, with `Role: independent-auditor` as its only Role trailer and nothing else under `governance/adoption/`:
```
git -C /home/usain/gov-os-runs/W2-88b/redis add -- docs/audit/A5-path-map-verdict.md
git -C /home/usain/gov-os-runs/W2-88b/redis -c user.name="independent-auditor (W2-88b A5)" -c user.email="auditor@example.invalid" commit -q -m "A5: the independent auditor's verdict on the path map (W2-88b smoke run)" --trailer "Role: independent-auditor"
git -C /home/usain/gov-os-runs/W2-88b/redis log -1 --format='%H %(trailers:key=Role,valueonly)'
```
Write nothing else anywhere: not in this repository, not in the copy beyond that one file, not in the other copy. Do not run `gov adopt`, `gov rebuild` or any stage; the lead runs A5 with your verdict.

## Rules
- Reads are open except: secrets (never printed), the held-out qualification material's contents, the counterpart's work, the hidden half of an evaluation set; never read or list `~/gov-os-workbench/`, `~/workspace` or `~/EXAMIN APP`, and nothing of the other copy.
- No `gov retrieve` and no `gov context` in the sandbox; search with Read and Grep, and search again once in different words before you say "not found".
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so in your return; never work around a refusal. If you cannot write or commit the verdict file, say exactly what refused it; the lead records A5 as failed (`NO_VERDICT`), never writes a verdict for you.

## Return (your last message; only it is read)
The twelve fields, each a labelled line ("none" where nothing):
`task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:`
In `evidence`: the verdict (pass or fail), the verdict file's path, its commit hash in the copy and the Role trailer as `git log` prints it, your session id, the path map hash, and each check with its result. End with a fenced verdict block:
```
verdict: pass | fail
copy: redis
verdict_file: docs/audit/A5-path-map-verdict.md
verdict_commit: <40 hex>
auditor_session: <id>
path_map_hash: <64 hex>
```


## How you run tests
Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR` (outside the repository and outside ~/gov-os-runs):
```
env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder in $TMPDIR> PYTHONPATH=<the copy>/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest --optin lifted,breadth <node id or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Run each case from the copy's root. A resource gate's refusal is a wait: wait and retry; it does not count as a refusal.

## Searching and forms
No `gov retrieve` and no `gov context` in the sandbox: Read and Grep; search again once in different words if needed.
Never open the evaluation sets' root, held-out material or any hidden or memory-verdict folder. Scripts longer than one
line go in `$TMPDIR`. Refused twice for the same call: stop and say so; never work around a refusal. No commit, merge or push.

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line ("none" where nothing):
task: / status: (PASS or FAIL) / work_completed: / files_changed: none / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then, for each of the four points: the verdict, the commands you ran and their result lines (each plant: green unplanted, red planted, the failing assertion).
Then each finding, with `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
Then the fenced verdict block, one entry per KPI line of the ticket, ids S1, S2, S3, F1, in this exact form:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": []}, ...]}
```
Then: guard_refusals: none or a line each.

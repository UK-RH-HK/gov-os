# ACT under DEC-886 (only if the trigger fires): W1-07's `doctor` envelope case onto `load_sensitive`

## Before the ping (orchestrator)
1. Confirm the trigger:
   - the close's JSON names `tests/acceptance/W1-07/test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]` as `RED_NOT_ACCEPTED`;
   - no other red that is not accepted (any other red is a package, not this ACT).
2. Run the case alone, three times, at a low load. Record the passes and the time:
   `env -u PYTEST_ADDOPTS PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src python3 -m pytest -q -p no:cacheprovider "tests/acceptance/W1-07/test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]"`
   (three separate runs; give the load at each).
3. Move the repair ticket to `log/repair-tickets/`.
4. Commit DEC-886's register entry first (`Task: decision-record`, `Role: orchestrator`, `Decided-by: owner (chat, 2026-10-21)`), after `tools/record_checks.sh`.
5. Write the entry into `governance/project/path-map.yaml` at the end of `load_sensitive` (after W1-38's two entries), uncommitted, for the owner's commit:

```yaml
  - test: "tests/acceptance/W1-07/test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]"
    decision: DEC-886
    reason: "<fails in the close's parallel regression at load <L> and passes alone, <n> of <n> in <s> s (W2-02's closes, 2026-10-21 15:36 and <time>)>"
    fixed_by: W2-57
```

6. Check the path map with `tools/record_checks.sh` (core-pathmap), and gate (f)'s suites.

## The owner's commit (plain terminal, operator)

```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git diff -- governance/project/path-map.yaml
git commit -m "Owner decision DEC-886: W1-07's doctor envelope case load-sensitive until W2-57 (row W2-L409)" --trailer "Task: decision-record" --trailer "Role: owner" -- governance/project/path-map.yaml
```

## After the commit
- Re-run that close, and the rest of the queue after it, with `tools/close_queue.sh <the tickets left>`. This is a re-run after a change (the owner's entry), not a retry.
- Row W2-L409's "closes when": W2-57 fixes the case; then the orchestrator commits the entry's removal.

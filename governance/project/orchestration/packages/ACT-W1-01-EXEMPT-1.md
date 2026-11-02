# ACT-W1-01-EXEMPT-1: the exemption entry for merge 0568d91baf56 (DEC-1031 item 3)

For the owner's operator, in the main tree: your own `Role: owner` commit, as DEC-906's entry was (only an owner's
commit adds to `acceptance_exemptions`).

## Why
P1-NIGHTLY-2026-11-02 (a), decided in DEC-1031 item 3: merge `0568d91baf56` (2026-10-31, `w2/integrate` into
`w2/W2-67`) resolved a conflict in an acceptance file in the merge commit itself; the resolution was a test
designer's (td-9), but the merge carries `Role: orchestrator`. W1-01b (`DAEO-vhad`, queued) lets a merge listed in
`acceptance_exemptions` be exempt for its own changes; this entry lists it. The order does not matter: the entry is
inert until W1-01b lands, and W1-01b's live-history case is green once both are in.

## Checked
- The patch applies cleanly to today's `governance/project/path-map.yaml` (`git apply --check`).
- The pinned judge's validator (`~/.local/share/gov-os/pin-5c401220/bin/python -E
  .gov-runtime/scratch/orchestrator/tools/validate_entry.py`): `PASS`, 1 entry judged, 0 failed; the placeholder scan
  clean.
- W1-01's own reader (`acceptance_exemptions` in `tests/acceptance/W1-01/w1_01_support.py`) reads the patched list as
  `{c9a08678…: DEC-900, 0568d91baf56…: DEC-1031}`.

## The commands
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git status --short -- governance/project/path-map.yaml
python3 - <<'EOF'
p = 'governance/project/path-map.yaml'
s = open(p).read()
a = '''acceptance_exemptions:
  - commit: "c9a08678644485a7528bc875164e110881b63d93"
    decision: DEC-900
'''
b = a + '''  - commit: "0568d91baf566b4d8f3ccb448e51af41cbb46d03"
    decision: DEC-1031
'''
assert s.count(a) == 1
open(p, 'w').write(s.replace(a, b))
EOF
git diff --stat -- governance/project/path-map.yaml
git add governance/project/path-map.yaml
git commit -m "Owner decision DEC-1031 item 3: acceptance_exemptions lists 0568d91baf56 (W1-01's merge rule)" --trailer "Task: decision-record" --trailer "Role: owner"
```
- The first line must show nothing (no change pending in the path map).
- The diff must show `1 file changed, 2 insertions(+)`.
- Undo: `git revert <the commit>`.

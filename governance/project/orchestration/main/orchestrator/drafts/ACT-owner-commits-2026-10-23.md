# The owner's two Role: owner commits of 2026-10-23 (DEC-899 item 3, DEC-900), prepared and validated

Both are prepared as patches against `w2/integrate` at `b930ed41`. **Apply A, then B, in that order:** B's path-map hunk sits next to A's.

**Validation (DEC-895), with the pinned judge's own code** (`pin-fecb870c`, its python `-E`), on a fresh clone of `b930ed41` with A then B applied:
- the pin's config loader reads the patched path map;
- the pin's ratchet counts all 30 remaining `load_sensitive` entries with 0 findings;
- `accepted_reds` is empty (0 entries, 0 findings);
- none of the four removed entries is still listed;
- the placeholder scan finds nothing in either patch.

**Run in that clone, with its own code:**
- W1-42, W2-53 and the unit ratchet tests: 85 passed;
- W1-08, W1-30's r11 file and `tests/unit/close`: all green (649 passed). The one red there came from my own W2-13 ticket edit, since fixed in `120f6c72`; W1-08's ticket test then passed, 16 of 16;
- the collection: 15,760 tests, exactly the 2 retired fewer.

The scripts: the scratchpad's `make_owner_patches.py` and `validate_removals.py`.

## Commit A: W1-02's and W1-05's p95 entries removed (DEC-899 item 3)

`drafts/OWNER-A-p95-removal.patch` (sha256 starts `2ee7d2a0d472daa4`): 8 lines removed from `governance/project/path-map.yaml`.

```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git status --short
git apply --check .gov-runtime/scratch/orchestrator/drafts/OWNER-A-p95-removal.patch
git apply .gov-runtime/scratch/orchestrator/drafts/OWNER-A-p95-removal.patch
git diff --stat
git commit -m "Owner decision DEC-899 item 3: W1-02's and W1-05's p95 load_sensitive entries removed" --trailer "Task: decision-record" --trailer "Role: owner" -- governance/project/path-map.yaml
```

## Commit B: W1-42's two accepted reds retired with their entries (DEC-900)

`drafts/OWNER-B-W1-42-retirement.patch` (sha256 starts `5be104a5bcb4bb87`):
- `governance/project/path-map.yaml`: `accepted_reds: []`;
- `tests/acceptance/W1-42/test_w1_42_exit_report.py`: RETR-X-02's parameter dropped, RETR-A-04 kept; the governance-share function removed;
- `tests/acceptance/W1-42/README.md`: its rows updated.

```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git apply --check .gov-runtime/scratch/orchestrator/drafts/OWNER-B-W1-42-retirement.patch
git apply .gov-runtime/scratch/orchestrator/drafts/OWNER-B-W1-42-retirement.patch
git diff --stat
git commit -m "Owner decision DEC-900: W1-42's RETR-X-02 case and governance-share case retired with both accepted_reds entries (AR-9 ruled: the stated gap)" --trailer "Task: decision-record" --trailer "Role: owner" -- governance/project/path-map.yaml tests/acceptance/W1-42/README.md tests/acceptance/W1-42/test_w1_42_exit_report.py
```

## The install for W2-66: pytest-timeout 2.4.0 (DEC-892 b, DEC-889 item 13)

W2-66's per-test limit uses pytest-timeout with the signal method, which the tool trials measured.
- **Wheel:** sha256 `c42667e5cdadb151aeb5b26d114aff6bdf5a907f176a007a30b940d3d865b5c2`, as in the trial install.
- **Where:** the user site of `/usr/bin/python3`, where pytest and pytest-xdist live, so the leads' and workers' runs load it.
- **Behaviour:** installed, it changes no run that does not pass `--timeout`.
- **Requirement file:** `drafts/pytest-timeout-requirements.txt`, one line, with the hash.

```
/usr/bin/python3 -m pip install --user --break-system-packages --require-hashes -r /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/pytest-timeout-requirements.txt
/usr/bin/python3 -c "import pytest_timeout; print(pytest_timeout.__file__)"
```

**After it:**
- I record it in `governance/project/tool-registry.yaml` (approved by DEC-892), in the form of pytest-xdist's entry.
- The close runs from the pin's own environment, so the first re-pin's environment gets the same wheel. I add that to the re-pin plan's acts.

After both commits: `git status --short` shows nothing. The orchestrator then runs its record checks and sees the next close's ratchet read the shorter lists.

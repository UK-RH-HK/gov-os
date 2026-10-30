# P-W2-54 — W2-48's install: pytest-testmon and coverage, one DEC-083 package (ACT; gates W2-48's engineer)

**From:** the W2 orchestrator, 2026-10-20. **Decided already:** DEC-843 item 3 (Q-13): pytest-testmon and coverage come as one DEC-083 install package when W2-48 starts. This is that package; the act is the owner's (DEC-083, ADR-0001's install rule).

## What and where
- `pytest-testmon==2.2.0` and `coverage==7.16.2`, the latest on PyPI on 2026-10-20 (`pip index versions`).
- For `/usr/bin/python3` (3.12.3), user site, the way pytest 9.0.3 and pytest-xdist 3.8.0 are installed (`tool-registry.yaml`, DEC-514).
- `--no-deps`: pytest-testmon needs pytest and coverage, both pinned here; nothing else is pulled.
- W2-48's lead verifies that testmon 2.2.0 works with pytest 9.0.3 and xdist 3.8.0 in its choice record (`docs/research/W2-48-cache-choice.md`); if it does not, the uninstall line below is the way back.

## Operator commands (a plain terminal)
```bash
mkdir -p /tmp/w2-48-wheels
/usr/bin/python3 -m pip download --no-deps -d /tmp/w2-48-wheels pytest-testmon==2.2.0 coverage==7.16.2
sha256sum /tmp/w2-48-wheels/*.whl
/usr/bin/python3 -m pip install --user --break-system-packages --no-deps /tmp/w2-48-wheels/*.whl
/usr/bin/python3 -c "import testmon, coverage; print(testmon.__file__, coverage.__version__)"
```
Uninstall (the way back): `/usr/bin/python3 -m pip uninstall --break-system-packages pytest-testmon coverage`

## The record
Once installed, the orchestrator records both in `governance/project/tool-registry.yaml` (name, version, the wheel's sha256 from `/tmp/w2-48-wheels`, install and uninstall commands, date, `approved_by: DEC-843`), committed under DEC-861.

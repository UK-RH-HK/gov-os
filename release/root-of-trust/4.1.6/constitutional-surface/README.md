# Constitutional Surface Inventory and coverage checker (RoT-1 revision 4)

**Status:** PROPOSED architecture artefacts. Not signed, not active, not approved, not the Governance OS implementation.
Specification: `../23-CONSTITUTIONAL-SURFACE.md`.

| File | What it is |
|---|---|
| `CONSTITUTIONAL_SURFACE_INVENTORY.yaml` | Draft **surface section of Trust Policy v1** (schema version 2, `floor_schema_version` 3). It classifies every file and leaf of the current kernel (`framework/`, plus `migrations/` and `tools/` for release payloads) with one floor semantics each. Floors, registered digests, member ids, **required presence**, the **exact precedence registration**, the **Overlay Surface** (directions and migration-writable targets) and **owner-domain slots**. Schema: `../schemas/constitutional-surface-inventory.schema.json`. |
| `csi_lib.py` | Reference semantics for `floor_schema_version: 3`. Inventory-driven leaf enumeration; default deny; presence; the single YAML profile; operators and joins. The two-directional precedence order (admitted strengthening and weakening sets); registered-only effective precedence with the held registration; the directed project join. Strength requirements over effective policy; the migration whitelist; E7 evaluation; computed reductions; owner-domain evaluation. |
| `csi_derive.py` | Producer tooling. Drafts an inventory from a kernel using the classification rules in the file. The root ceremony reviews the draft; the binary never derives classification at run time. |
| `csi_check.py` | `check` (coverage and E7 against the inventory), `check-owner` (owner constitutional domain), `reductions` (computed reductions between two inventories) and `selftest`. |

## Running

```sh
E="env -i PATH=/usr/bin:/bin HOME=<scratch>/home PYTHONDONTWRITEBYTECODE=1"
$E python3 csi_check.py check --json ../../../../framework                          # exit 0
$E python3 csi_check.py check --json ../../../../release/releases/4.1.5/kernel      # exit 3 (historical set_lock_field migrations)
$E python3 csi_check.py check --json ../../../../release/releases/4.1.2/kernel      # exit 2
$E python3 csi_check.py reductions --old <inventory v1> --new <inventory v2> [--lowering-history <file>] --json   # exit 6 when undeclared
$E python3 csi_check.py check-owner --registrations <file> --json <repo root>
$E python3 csi_check.py selftest --scratch <scratch dir>                              # exit 0 when all 56 cases behave as expected
$E python3 csi_derive.py ../../../../framework > <file>                               # regenerate the draft (review the diff)
```

**Exit codes:**
- 0 — pass;
- 2 — coverage failure: an unclassified or ambiguous file or leaf, a **required file or leaf missing**, or a structure or
  **YAML profile** violation;
- 3 — a floor, pin, membership, **precedence registration** or **migration operation** violation, or a value stronger
  than registered;
- 4 — inventory consistency failure: a class weaker than the registered precedence, a catch-all rule, `project_tunable` on
  a non-overridable key, or an inconsistent Overlay Surface or owner-domain entry;
- 5 — inventory malformed;
- 6 — computed reductions not declared in `lowering_history` (`reductions`).

Requires Python 3 with PyYAML only. The self-test writes only under `--scratch`. Always run with
`PYTHONDONTWRITEBYTECODE=1` so no `__pycache__` is written into the repository.

**Recorded results:**
- `../evidence/CSI-check-*.json`: framework exit 0; 4.1.5 exit 3; 4.1.5 with lock operations removed exit 0; 4.1.2, 4.1.3
  and 4.1.4 exit 2;
- `../evidence/CSI-selftest.json`: 56 of 56.

The self-test is a conformance oracle for the implementation's evaluator, not an expected count (`../12-ACCEPTANCE-TEST-PLAN.md` §8).

# Constitutional Surface Inventory and coverage checker (RoT-1 revision 3)

**Status:** PROPOSED architecture artefacts. Not signed, not active, not approved, not the Governance OS implementation.
Specification: `../23-CONSTITUTIONAL-SURFACE.md`.

| File | What it is |
|---|---|
| `CONSTITUTIONAL_SURFACE_INVENTORY.yaml` | Draft **surface section of Trust Policy v1**. It classifies every file and leaf of the current kernel (`framework/`, plus `migrations/` and `tools/` for release payloads) with one floor semantics each: floor values, registered digests, registered member ids, and registered precedence rules. Schema: `../schemas/constitutional-surface-inventory.schema.json`. |
| `csi_lib.py` | Reference semantics for `floor_schema_version: 2`: inventory-driven leaf enumeration, default deny, operators and joins, precedence lattice per concrete key, evaluation (E7 surface check and effective values), exception relaxation rule. |
| `csi_derive.py` | Producer tooling. Drafts an inventory from a kernel using the classification rules in the file. The root ceremony reviews the draft; the binary never derives classification at run time. |
| `csi_check.py` | Coverage checker (`check`) and self-test (`selftest`). |

## Running

```sh
python3 csi_check.py check ../../../../framework                       # exit 0
python3 csi_check.py check ../../../../release/releases/4.1.5/kernel   # exit 0
python3 csi_check.py check ../../../../release/releases/4.1.2/kernel   # exit 2 (legacy kernel: unclassified key)
python3 csi_check.py selftest --scratch <scratch dir>                  # exit 0 when all 26 cases behave as expected
python3 csi_derive.py ../../../../framework > <file>                   # regenerate the draft (review the diff)
```

**Exit codes:**
- 0 — pass;
- 2 — coverage failure: an unclassified, ambiguous or structurally invalid file or leaf;
- 3 — a floor, pin, membership or precedence violation, or a value stronger than registered;
- 4 — inventory consistency failure: a class weaker than POLICY_PRECEDENCE, a catch-all rule, or `project_tunable` on a
  non-overridable key;
- 5 — inventory malformed.

Requires Python 3 with PyYAML only. The self-test writes only under `--scratch`.

**Recorded results:** `../evidence/CSI-check-*.json`, `../evidence/CSI-selftest.json`.

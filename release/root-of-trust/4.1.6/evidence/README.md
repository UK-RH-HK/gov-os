# Evidence index (RoT-1 revision 2)

| File | Revision | What it is |
|---|---|---|
| `ESCALATION_PROBES.md`, `probe.sh`, `regen.py`, `probe-output.txt` | 1 (unchanged) | escalation probes E1–E5 against the 4.1.5 binary |
| `F1-format-boundary-probe.py`, `F1-format-boundary-probe.json` | 2 | feasibility probe for the trust-format boundary (`13` §3): the real 4.1.5 binary run against a scratch project written in the proposed format (lock sentinels, tombstone `KERNEL_MANIFEST.json`, `governance/trust/FORMAT`) |

## F1 summary

Run in a scratch directory against `target/release/gov` 4.1.5 (runtime unchanged since `da9c851`):

| 4.1.5 command | Result |
|---|---|
| `kernel trust` | `verified: false`, embedded baseline substituted, problems contain the sentinel |
| `kernel verify` | `ok: false` |
| `doctor` | `UNHEALTHY`, critical D003, D004, D029 |
| `task create` | `KERNEL_TAMPERED`, message contains the sentinel |
| `rebuild-memory` | `KERNEL_TAMPERED` |
| `status`, `capabilities plugins` | run (read-only) |
| `kernel reinstall` | `KERNEL_MISMATCH` after overwriting the kernel directory (residual LC-1) |

The probe writes its consumers next to the script (`tempfile.mkdtemp(dir=<script dir>)`). Run a copy from a scratch
directory to keep the repository clean.

## Evidence produced by the independent review (not copied here)

`../4.1.6-review/evidence/`:
- `E1-E5-reproduction-output.txt`
- `continuity-check-4.1.2-4.1.5.txt`
- `legacy-kernel-security-diffs.txt`
- `R1-legacy-kernel-floors.{py,json}` — executed RV-H1
- `R2b-use-time-toctou.{py,json}` — executed RV-H3

Revision 2 cites them and requires them to flip in acceptance (`12` RT-32, RT-42, RT-72).

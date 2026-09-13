# Review evidence index

All probes ran in the reviewer's scratch directory against `target/release/gov` (4.1.5). The runtime, CLI, framework,
migrations, tools and Cargo files are unchanged between the rejected candidate `da9c851` and HEAD (`git diff --stat` is
empty for those paths). No repository file outside this review directory was written. Absolute scratch paths in outputs
are kept verbatim.

| File | What it is | Result |
|---|---|---|
| `E1-E5-reproduction-probe.sh` | The architect's `probe.sh`, with only the scratch path changed | — |
| `E1-E5-reproduction-output.txt` | Verbatim output | Identical to the architect's `probe-output.txt` apart from paths: E1b ok with regenerated `aa8fb66a…`; E2 `human_gate_required:false`, applied without `--approve`; E3a/E3b poisoned cache installed and used as baseline; E4 `verified:true`, D003/D004/D029 ok; E5 rollback `kernel_ok:true`; restricted floor removed in each |
| `continuity-check-4.1.2-4.1.5.txt` | The architect's `make_example.py`, run from a scratch copy for each legacy version | tree digest = published `release_hash` and manifest digest = `KERNEL_MANIFEST.json` hash for all four; schema-valid; DSSE verify and tamper rejection; 4.1.5 example payload byte-identical |
| `legacy-kernel-security-diffs.txt` | `diff` of security-relevant kernel files between consecutive legacy releases | 4.1.2→4.1.3 AUTHORITY_POLICY (+35 operation classes including `update_apply: L4`, `resume_control: L4`), ROLES groups; 4.1.3→4.1.4 TOOL_POLICY `plugins` block + `EXEC_PLUGIN`; 4.1.4→4.1.5 TOOL_POLICY and three POLICY_PRECEDENCE plugin rules; no POLICY_PRECEDENCE.yaml before 4.1.4 |
| `R1-legacy-kernel-floors.py` / `.json` | Two consumers, one initialised from `release/releases/4.1.2`, one from `4.1.5`; L3 `change-controller` runs `update --apply` and `resume` | 4.1.2: `verified:true`, update passes authority (`HUMAN_GATE_REQUIRED`), resume ok. 4.1.5: `verified:true`, both `AUTHORITY_DENIED` → **RV-H1** |
| `R2-preliminary-probes.py` | First TOCTOU run, restricted material under `customer/**` (outside the contract's index scope) | The swapped floor was consumed in 5/5 trials (restricted exclusion disappeared); nothing indexed because of scope |
| `R2b-use-time-toctou.py` / `.json` | TOCTOU with in-scope restricted material (`spec/decisions/D-9001.yaml`, `product/restricted-plan.md`); inotify racer swaps `SECURITY_POLICY.yaml` after kernel_trust's read and restores it on exit | Control: both excluded. Trial 1: swap 0.11 ms after the read; both indexed (`sensitivity = restricted`); unraced `memory query` returns both; `kernel trust verified:true`; D003/D004/D029 ok; policy bytes restored → **RV-H3** |

Reproduce, from the repository root with a built `target/release/gov`:

```bash
python3 release/root-of-trust/4.1.6-review/evidence/R1-legacy-kernel-floors.py
python3 release/root-of-trust/4.1.6-review/evidence/R2b-use-time-toctou.py   # Linux (inotify via ctypes)
```

Both scripts create their temporary consumers next to the script (`tempfile.mkdtemp(dir=<script dir>)`). Run copies from
a scratch directory to keep the repository clean, as this review did.

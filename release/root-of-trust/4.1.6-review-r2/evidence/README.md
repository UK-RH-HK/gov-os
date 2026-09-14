# Evidence — independent review of RoT-1 revision 2

All probes are scratch-only:
- consumer repositories are created under `$GOV_REVIEW_SCRATCH`, or the system temp directory when unset;
- the canonical repository is never written;
- environment variables starting with `GOV_` are removed from the child environment;
- `GOV_KERNEL_CACHE` points into scratch.

The probes are review instruments, not Governance OS implementation.

| File | Kind | What it establishes | Result |
|---|---|---|---|
| `REVIEWED-CONTENT-DIGESTS.txt` | record | SHA-256 of every reviewed file in commit `d37b05c`, plus an aggregate | — |
| `P1-floor-coverage.{py,json}` | executed (4.1.5) + static + reference evaluation | TPS v1 floors derived exactly as `examples/make_example.py`; coverage of AS-1 leaves; all 145 floors hold on a kernel changing only unfloored leaves; the 4.1.5 binary consumes those leaves for authority, secrets and gate answering | 145 floors; 64 of 125 AS-1 leaves unfloored; (a) L1 `resume` ok vs `AUTHORITY_DENIED`; (b) AWS credential file indexed and retrievable vs excluded; (c) agent answers R5 gate vs denied → **R2-H1** |
| `P2-gate-record-forgery.{py,json}` | executed (4.1.5) | an A2 commit editing `spec/decisions/HDG-0001.yaml` authorises `update --apply --approve` without `gate present` or `decide` | control `applied: false`; forged `applied: true`, 4.1.4 → 4.1.5 → **R2-M1** (and the R2-H2 bound) |
| `P3-pre-rot-binary-matrix.{py,json}` | executed (4.1.5 and 4.1.2) | 3 layouts × 2 binaries × 8 commands on a RoT-1 project with a legacy update snapshot and a project restricted-classification | V0 (pack layout): legacy `update --rollback` and `init --force` rewrite kernel, lock and overlay, delete the classification, report verified, serve the restricted file. V1 insufficient. V3: every command refused with no write → **R2-H4** |
| `P3b-attribution-control.{py,json}` | executed | the 4.1.2 binary also serves restricted material on a plain 4.1.5 project | attributes that exposure to 4.1.2 itself |
| `P4-trust-state-model.{py,json}` | reference model of `17` S2–S9, §6 and `19` §5–§6, §10 as written | six scenarios B1–B6, each compared with the pack's claim | all `agrees: false` → **R2-M2** (B1, B4), **R2-M3** (B2), **R2-M4** (B3), **R2-H2** (B5), **R2-M5** (B6) |

## Running

```sh
export GOV_REVIEW_SCRATCH=<scratch dir>
python3 P1-floor-coverage.py > P1-floor-coverage.json         # GOV=<4.1.5 binary> optional
python3 P2-gate-record-forgery.py > P2-gate-record-forgery.json
GOV415=<4.1.5 binary> GOV412=<4.1.2 binary> python3 P3-pre-rot-binary-matrix.py > P3-pre-rot-binary-matrix.json
python3 P3b-attribution-control.py > P3b-attribution-control.json
python3 P4-trust-state-model.py > P4-trust-state-model.json    # no binary needed
```

**Requirements:**
- Python 3 with PyYAML;
- `git`;
- the 4.1.5 binary (`cargo build --release` at a commit whose runtime equals `da9c851`);
- the 4.1.2 binary (`git worktree add --detach <dir> 8ad06be`, then `cargo build --release`).

P3 takes a few minutes; the others take under a minute each.

## Notes

- **P1 part 3** installs the tampered kernel through the 4.1.5 V-H3 path only to obtain a verified policy root carrying
  that content. The finding concerns what revision 2 would accept as a policy root once such content is authentic and
  eligible, not V-H3.
- **P3** uses the 4.1.5 payload as the stand-in RoT-1 kernel, as the architect's F1 did. The "RoT-1 view" column applies
  the `18` §9 rules by reading, since no RoT-1 binary exists.
- **P4** assumes all signatures verify. It tests decision logic only, and its rules are quoted from the pack in the code
  comments so each can be checked against the text.

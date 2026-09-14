# Evidence index (RoT-1 revision 3)

All probes are scratch-only:
- consumers are created under a scratch directory given by the operator;
- the repository and the canonical checkout are never written;
- `GOV_*` variables are removed from child environments;
- `GOV_KERNEL_CACHE` and `HOME` point into scratch.

The probes are architecture instruments, not Governance OS implementation. Absolute scratch paths in outputs are replaced
by `<scratch>`, `<repo>` and `<legacy-bin>`.

## Revision 3 evidence

| File | Kind | What it establishes | Result |
|---|---|---|---|
| `CSI-check-framework.json`, `CSI-check-release-4.1.5.json` | coverage checker (`../constitutional-surface/csi_check.py check`) | every file and leaf of the current kernel and the 4.1.5 payload has floor semantics and satisfies the draft TPS v1 inventory | exit 0 for both (113 and 121 files; 0 unclassified) |
| `CSI-check-legacy-4.1.2.json`, `-4.1.3.json`, `-4.1.4.json` | coverage checker | legacy kernels fail the surface | exit 2 (4.1.2: 1 unclassified key, 64 violations); exit 3 (4.1.3: 64; 4.1.4: 62) |
| `CSI-selftest.json` | checker self-test (26 cases) | HO-0001 §3.1 test list; unknown key and file fail; data-only forward compatibility passes; inventory lint | **26 of 26 as expected** |
| `P1r3-floor-coverage.{py,json,stderr}` | static + reference evaluation + executed consumption on the real **4.1.5** binary | Revision-3 floor semantics over the whole surface. The review r2 P1 tamper and the §3.1 cases are ineligible, with effective policy equal to genuine. The materialised effective kernel flips every harm. A newer TPS raises floors over an older kernel. | coverage 0 unclassified; 308 of 308 review-listed leaves classified; §3.1 cases all effective = genuine; harm verdicts (a) authority, (b) secret, (c) R5 gate flipped; (d) raised role floor and (e) raised confidence floor enforced |
| `P3r3-pre-rot-register-matrix.{py,json,stderr}` | executed with the real **4.1.2, 4.1.3, 4.1.4, 4.1.5** binaries | Commands derived from each binary's own `--help` (104/109/115/119 leaves), with synthesized arguments, flag variants, destructive combinations and 10 stateful chains. Run on the revision-3 layout (L3) with a legacy update snapshot and a restricted classification; positive control on an ordinary legacy project (L0); ablation without the no-install occupations and with adoption residue (L3A). | **L3: 695 invocations and 40 chains, 0 tree changes, 0 Git changes, classification intact.** L0: 36/42/46/47 changing invocations. L3A: 4 changing invocations per binary. |
| `P4r3-trust-state-model.{py,json,stderr}` | reference model of `17`, `19` §10, `24`, `25` §5, `05` §3 | review r2 B1–B6; machine list M1–M7 (with OP-7 options); replay, witness replay, repository gate records, hints, pin mismatch, VTS deletion; forks; whitelist; `verify-artifact` | **34 of 34 scenarios agree**; B1–B6 all flipped |
| `G1-git-occupation-behaviour.{sh,txt}` | executed Git behaviour | a tracked occupation file at `.governance-runtime/migration` removes ignored residue on pull, aborts checkout for unignored residue, and is present in fresh clones | as stated |

## Running (from this directory)

```sh
export SCRATCH=<fresh scratch dir>
GOV_REVIEW_SCRATCH=$SCRATCH GOV=<gov 4.1.5 binary> python3 P1r3-floor-coverage.py > P1r3-floor-coverage.json
P3_REPO=<repo root> P3_LEGACY_BIN=<dir with gov-4.1.2 … gov-4.1.5> python3 P3r3-pre-rot-register-matrix.py $SCRATCH/p3 --workers 16 > P3r3.json
python3 P4r3-trust-state-model.py > P4r3-trust-state-model.json
./G1-git-occupation-behaviour.sh $SCRATCH/g1 > G1-git-occupation-behaviour.txt
python3 ../constitutional-surface/csi_check.py selftest --scratch $SCRATCH/csi > CSI-selftest.json
```

- The committed `P3r3-pre-rot-register-matrix.json` is a compacted form of the harness output. Per-row changed paths are
  kept only for rows that changed.
- The legacy binaries used were `gov 4.1.2`, `4.1.3`, `4.1.4` and `4.1.5`; their SHA-256 digests are recorded in the JSON.
- P3r3 takes about two minutes with 16 workers. P1r3 takes about a minute. The others take seconds.

**Attribution.** P1r3 part 3 and P3r3 adapt the method of review r2 `evidence/P1-floor-coverage.py` and
`evidence/P3-pre-rot-binary-matrix.py`. P4r3 takes the scenario shapes B1–B6 from review r2
`evidence/P4-trust-state-model.py`. Rules and layouts are revision 3. The review directories were not edited.

## Earlier evidence (history)

| File | Revision | Status |
|---|---|---|
| `ESCALATION_PROBES.md`, `probe.sh`, `regen.py`, `probe-output.txt` | 1 | escalation probes E1–E5 against 4.1.5; still the reproduction target for RT-72 |
| `F1-format-boundary-probe.{py,json}` | 2 | **Superseded (R2-L3).** It wrote `FORMAT` as `rot-1\n` rather than JSON, omitted lock `kernel.*`, ran one destructive command, and used the withdrawn sentinel layout. It supports no revision-3 claim. |

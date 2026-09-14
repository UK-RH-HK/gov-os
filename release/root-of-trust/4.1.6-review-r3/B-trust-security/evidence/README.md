# Evidence — review r3 B (trust and security), run AR-0002

All probes run in scratch only.
- **Repository.** The reviewer worktree is read, never written, except this output directory.
- **Child environment.** `GOV_*` variables are removed; `GOV_KERNEL_CACHE` and `HOME` point into scratch.
- **Consumers.** Consumer repositories are created under `$GOV_REVIEW_SCRATCH`.
- **Binaries.** Legacy binaries are used read-only from the orchestrator's `legacy-bin/` directory. No RoT-1 binary exists; revision-3 behaviour is evaluated with the pack's own checker, the architect's reference scripts (re-run) and an independent reference model.

## Files

| File | Kind | What it establishes | Result |
|---|---|---|---|
| `REVIEWED-CONTENT-DIGESTS.txt` | record | SHA-256 of every reviewed file at `ca77a431418bd6b349f465aa2521ca43bccfd5a6`: pack, D-0007, D-0008, ARCH-0002, `docs/DECISIONS.md`. The pack is unchanged between `ca77a43` and the review base `83aa822`. | 107 files; aggregate recorded |
| `r2rerun-P1-floor-coverage.{py,json,stderr}` | executed, 4.1.5 | Review r2 P1, copied with attribution; only `REPO` and the default `GOV` changed | Reproduced: 145 floors, 0 violated by the tamper. Harms on 4.1.5: L1 `resume` ok; AWS file indexed and retrievable; agent answers the R5 gate. |
| `r2rerun-P2-gate-record-forgery.{py,json,stderr}` | executed, 4.1.5 | Review r2 P2, copied with attribution | Reproduced: control `applied: false`; forged record `applied: true` (4.1.4 → 4.1.5) |
| `r2rerun-P4-trust-state-model.{py,json,stderr}` | reference (revision 2 rules) | Review r2 P4, copied with attribution | Reproduced: B1–B6 all `agrees: false` under revision 2 rules |
| `arch-rerun-P1r3-floor-coverage.{json,stderr}` | executed, 4.1.5 | The architect's `evidence/P1r3-floor-coverage.py`, run unmodified from the pack path | Parts 1, 2, summary and part-3 verdicts identical to the committed JSON; the r2 harms flip on the effective kernel |
| `arch-rerun-P4r3-trust-state-model.json` | reference | The architect's `evidence/P4r3-trust-state-model.py`, run unmodified | 34/34; byte-identical to the committed JSON |
| `RV3-B-M-reference-model.{py,json,stderr}` | reference (independent) | This review's encoding of revision 3 (`17`, `24`, `25` §5, `05` §3, `27` §3), written from the text: B1–B6 re-executed, RV3-B-A02, A04–A13, 132-row machine × OP-7 × adversary matrix | B1, B2, B3, B4 and B6 claims hold, and the P2 flip holds. B5 fails with a stale pin. A02, A04–A12 contradict pack claims. R7 (revoked) is a C2 policy root in 90 of 132 rows. |
| `RV3-B-A01-precedence-immutable.{py,json,stderr}` | executed, 4.1.5 plus the pack checker | A kernel changing only precedence modes to `immutable` | Checker exit 0; join `immutable`; project strengthening discarded for authority, indexing and gates; overlay unchanged |
| `RV3-B-A03-A14-A16-probes.{py,json,stderr}` | executed, 4.1.5 plus the pack checker | A03: `gov verify product` runs an A2-committed command that writes pin files. A14: YAML 1.1 `on` differential. A16: `project_tunable` leaves with runtime consumers. | A03: both files written by uid 1000. A14: checker exit 0 for 10 leaves; runtime reads `"on"`. A16: checker exit 0. |
| `RV3-B-CSI-injections.{py,json,stderr}` | pack checker | Independent unknown key, file, directory, stray and structural injections | I01–I06 exit 2; I07 exit 3; I08 (new migration) exit 0; I09 (deleted floor leaf) exit 0 |

The architect's coverage checker was also run directly, with outputs kept in scratch: `framework/` exit 0; the 4.1.5 payload exit 0; 4.1.2 exit 2; 4.1.3 and 4.1.4 exit 3; `selftest` 26/26 as expected.

## Running

```sh
W=<reviewer worktree>; S=<scratch>
cd $W/release/root-of-trust/4.1.6-review-r3/B-trust-security/evidence
env -i PATH=/usr/bin:/bin HOME=$S/home GOV_REVIEW_SCRATCH=$S REVIEW_REPO=$W python3 r2rerun-P1-floor-coverage.py > r2rerun-P1-floor-coverage.json
env -i PATH=/usr/bin:/bin HOME=$S/home GOV_REVIEW_SCRATCH=$S REVIEW_REPO=$W python3 r2rerun-P2-gate-record-forgery.py > r2rerun-P2-gate-record-forgery.json
python3 r2rerun-P4-trust-state-model.py > r2rerun-P4-trust-state-model.json
env -i PATH=/usr/bin:/bin HOME=$S/home GOV_REVIEW_SCRATCH=$S GOV=<legacy-bin>/gov-4.1.5 python3 $W/release/root-of-trust/4.1.6/evidence/P1r3-floor-coverage.py > arch-rerun-P1r3-floor-coverage.json
python3 $W/release/root-of-trust/4.1.6/evidence/P4r3-trust-state-model.py > arch-rerun-P4r3-trust-state-model.json
python3 RV3-B-M-reference-model.py > RV3-B-M-reference-model.json
env -i PATH=/usr/bin:/bin HOME=$S/home GOV_REVIEW_SCRATCH=$S REVIEW_REPO=$W python3 RV3-B-A01-precedence-immutable.py > RV3-B-A01-precedence-immutable.json
env -i PATH=/usr/bin:/bin HOME=$S/home GOV_REVIEW_SCRATCH=$S REVIEW_REPO=$W python3 RV3-B-A03-A14-A16-probes.py > RV3-B-A03-A14-A16-probes.json
env -i PATH=/usr/bin:/bin HOME=$S/home GOV_REVIEW_SCRATCH=$S REVIEW_REPO=$W python3 RV3-B-CSI-injections.py > RV3-B-CSI-injections.json
```

**Requirements:** Python 3.12 with PyYAML, `git`, and the legacy `gov-4.1.5` binary (default path in the scripts; override with `GOV`). Each probe takes under a minute.

## Notes

- **4.1.5 as a consumption stand-in.** The 4.1.5 binary shows how kernel content is consumed. Revision 3 keeps that model: a project layer that may only strengthen, and precedence evaluated per override (`runtime/src/policy_precedence.rs`). A01 installs the tampered kernel through the 4.1.5 directory-source path, as review r2 P1 and the architect's P1r3 did, only to obtain a verified policy root carrying that content. The revision-3 effective kernel for A01 equals the tampered kernel, checked in part A.
- **Model independence.** The model is independent of `P4r3-trust-state-model.py`. Where the two agree on B1–B6, the agreement is a reproduction. Where they differ (A12), the difference is the anchor-satisfaction rule, quoted in the scenario.
- **Owner parameters.** The pack leaves two values to the owner: `max_anchor_age_days` and `witness_max_validity_days`. The model uses 180 and 7.
- **Not run by B.** P3r3 (legacy command matrix) and the G1 Git behaviour are reviewer C's scope, and were not re-executed.

# P2-AR-0052 evidence

Every file here was produced by the synthesis verifier on `cap2-candidate-1` in its own worktree
(`phase2/verify-1-synthesis`) and its own scratch area. Nothing was written into any other verifier's evidence
directory: where a family's `RUN-ALL` defaults to writing there (beta's `BETA_EVIDENCE`, delta's `EV`), the output
path was redirected, and delta's probes were run individually rather than through its `RUN-ALL` for that reason.

| File | What it is |
|---|---|
| `rerun-alpha-RUN-ALL.out` | P2-AR-0046's held-out suite, re-run by me: 387 PASS / 10 FAIL over its default set t01–t06 |
| `rerun-beta-RUN-ALL.out` | P2-AR-0047's suite: 185 PASS / 10 FAIL. Its nine recorded failures exactly; the tenth (`C1-transactions`) is a load artefact — an isolated re-run of `t-C1-deterministic-memory.sh` gave 17/0, and `cit propose` → `cit list` reproduces by hand. See 00-SYNTHESIS-REPORT.md §2.1 |
| `rerun-gamma-RUN-ALL.out` | P2-AR-0048's suite: 184 PASS / 17 FAIL, its totals exactly, including `V1-F4-01-executed-proof.sh` |
| `rerun-delta-RUN-ALL.out` | P2-AR-0049's nine probes run individually: 256 PASS / 9 FAIL, its recorded failures exactly |
| `rerun-epsilon-RUN-ALL.out` | P2-AR-0050's suite: 163 PASS / 4 FAIL, exactly its figures |
| `rerun-zeta-RUN-ALL.out` | P2-AR-0051's suite: 135 PASS / 2 FAIL, exactly its figures |
| `rerun-r1-preservation-RUN-ALL.out` | P2-AR-0044's suite and its four unedited prior R1 suites. Every per-binary figure reproduced: p1 13/0, p2 9/0, p3 10/1, p6 8/0; AR-0027 12/0+6/2+4/1+4/0; AR-0029 6/0+4/2+5/0+5/0+6/0; AR-0031 5/3+5/1+6/2+11/1; AR-0033 9/1+7/0+6/0+8/0; and the OWNER-DECISION-0006 §6 census at 123 files / 2392 functions with zero violations in all three splitter configurations. **The log ends mid-way through the suite's own trailing regression run**, which is not evidence I rely on — AC-15 is `AC-15-regression.out`, run by me in one pass each |
| `rerun-oracle-format.out` | P2-AR-0045's two load-bearing checks, re-run: the Gate V crosswalk against the owner-source bytes (35 bullets + 5 statements, 0 problems) and the 93-sample attack matrix (93 as expected, 0 unexpected); plus the `format_sha256` recomputed |
| `AC-15-regression.out` | `cargo test --lib` 276/0 and `cargo test --test certification` 207/0, run by me in this worktree, one pass each |
| `AC-13-independent-line-accounting.py` / `.out` | My own check of the compiled contract view against the owner source, **without using the product**: 1026 of 1026 lines carried verbatim exactly once, 0 missing, 0 extra, 0 without a verbatim carrier; 101 capabilities including Gate U; 713 + 9 = the source's own 722 checklist lines |
| `AC-9-AC-13-pinned-inputs-and-contract-verify.out` | `cmp` of the canonical import, every pinned SHA-256, `git rev-list`, `product_identity.py` at the tag and at `HEAD`, and the full `gov contract verify` output (`CONTRACT_SOURCE_BOUND`) |
| `AC-10-gov-contract-matrix-with-my-runs.yaml` | `gov contract matrix` fed with my own lib, certification, held-out and health/doctor logs: 101 capabilities, 798 owners, 0 with zero owners, 0 unresolved, 0 capabilities without an owner I observed running |
| `AC-5-health-catalogue.json`, `AC-5-health-run-G5.json`, `AC-5-health-run-G1.json`, `AC-5-doctor.json` | The tier gap re-established from scratch in my own probe project: 74 checks declared, 74 at G5 and 49 at G1; `--tier G5` evaluates 39 and records `complete: true, not_evaluated: 0`; `--tier G1` evaluates 18 of 49; D001–D035 appear only under `gov doctor` |
| `AC-16-end-to-end-chain.out` | My own chain across family boundaries: CIT impact simulation reaching the dependent task at hop 1 `via CONSUMES → REQ-0001` (R2); staleness propagated with both hashes and `propagated: true`; the delivered packet failing to verify; the green record obsolete naming five input classes; the G0 guard re-evaluating at the instant of the call |

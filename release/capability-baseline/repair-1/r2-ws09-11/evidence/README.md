# P2-AR-0030 evidence (repair iteration 1, round 2, WS-9/11)

Everything here is **builder regression evidence** (Contract v3 O3). Nothing in it claims acceptance.

Binaries:

- **Candidate:** `target/release/gov` built from work commit `23a76d2`, SHA-256 `8bd03daa…0e25`. The product code is identical at the final work commit (the later commits add only evidence and reports).
- **Base (negative control):** the base 843d79c (the integrated round-1 tree), SHA-256 `e09eb5dc…4880`. Its build log is `regression/base-843d79c-release-build.out`.
- **"Before" runs:** these run from a `git archive` of 843d79c with the base binary, so their probe files, fixtures and canonical root are the base ones too.

Scratch lived only under the session scratchpad (`…/scratchpad/p2ar0030/`). Outputs contain those absolute paths.

| Path | Content |
|---|---|
| `probes/R2-ws0911-named-checks.py` | **Named checks.** A discriminating reimplementation of every audit-of-record line this round's classes name. It covers BC-P2-34 (adoption side: alpha-r N1/N2/N7, T1c, epsilon-r O3 §C/§D, A10/A11 authorship, role consistency, the T2 record), the adoption-gate subject binding, the adopt tier calls (G0/G4/G5) and the BC-P2-10 export approval (epsilon-r Q1.6-8). It uses only the paths the product now requires: declared roles and sessions, reviewer/verifier-authored tests, and owner-signed answers from WS-3's published test-material signer. |
| `probes/R2-named-checks.base-843d79c.out` | Negative control on the base binary: **4 PASS (the [control] lines) / 33 FAIL** of the 37 lines the base can reach. The 4 export lines after Q1.6-8 need an export gate, which the base never raises. |
| `probes/R2-named-checks.candidate.out` | Candidate: **41 / 41 PASS**. |
| `probes/run-probe.sh` | Runner for the audit-of-record probes, **unedited**. It takes `before`/`after` × `direct` (the real binary) / `shim` (the round-1 integration's evidence adapter `gov-owner-channel-shim.py`, used unedited by path). The adapter adapts only three things: an undeclared role becomes orchestrator, a relayed human `decide` becomes an owner-signed answer, and missing gate-package fields are filled. |
| `probes/{before,after}-{direct,shim}/` | Unedited outputs: alpha-r `S4-T2-B2-negative`, `T1-roles`, `S4-adopt-end-to-end` (prepared, and `RAW_SQL_STORE=1`); epsilon-r `O3-independent-authorship`, `Q-learning-upstream`. `*.shimlog` records each adaptation. |
| `probes/derived/derived-S4-adopt-end-to-end.r2-roles.P2-AR-0030.py.txt` (+ `.diff`, `run-derived-s4.sh`, `after-shim/`) | **Derived, labelled copy** of alpha-r `S4-adopt-end-to-end.py`. Exactly 5 lines differ (see the diff): the designated roles for A5/A7/A10/A11, one reviewer-authored test, and verifier-authored held-out queries. Every negative check is kept. The candidate completes A0–A11 with the prepared fixture and with `RAW_SQL_STORE=1` (BC-P2-33 criterion preserved). |
| `probes/derived/derived-B-ws0911-regression-probes.owner-channel.reviewer-tests.P2-AR-0030.py.txt` (+ `.diff`, `run-derived-b.sh`, `before/`, `after/`) | **Second-generation derived copy** of P2-AR-0021's round-1 builder probe, made from P2-AR-0022's owner-channel copy. Its only further change is a reviewer-authored test before each approval. BC-P2-33/52/21/50 regression: **27/27 on both trees**. |
| `regression/cargo-test-lib.out` | `cargo test --lib` at `23a76d2`: **153 passed, 0 failed** (base 146). |
| `regression/cargo-test-certification.out` | `cargo test --test certification` at `23a76d2`: **102 passed, 0 failed** (base 100), including `section6::*`. |
| `r1-heldout/run-r1-heldout.sh`, `r1-heldout/r1-heldout-work-23a76d2.out` | **Every prior R1 held-out suite, unedited** (a `cmp` line for each copied file). They were built against **this worktree** through a private per-run scratch path (P2-HO-0020 item 7). Results: AR-0027 26/3, AR-0029 26/2 (`ho_f` does not compile), AR-0031 27/7 and AR-0033 30/1, all at their recorded baselines. The one AR-0033 failure is `hv_a::a1`: its pins are 84 files / 740 functions, against a measured **105 files / 1515 functions**. The unpinned copy, and AR-0033's own `derive.py`, find **0 violations in every §6 activity**. |

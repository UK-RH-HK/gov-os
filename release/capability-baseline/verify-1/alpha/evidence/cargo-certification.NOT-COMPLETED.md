# `cargo test --test certification` — not completed inside this run

`cargo test --lib` was reproduced in this worktree and is captured in `cargo-lib.out`:
**276 passed, 0 failed**.

`cargo test --test certification` was started in the same worktree (`CARGO_BUILD_JOBS=2`,
`~/.cargo/bin/cargo test --test certification`) and was still executing when this verification
finished writing its report. The host was running several Phase-2 verifiers at once at a load
average above 160, and the suite drives `gov` against many disposable projects, so it did not
complete inside this run's window.

What this does and does not mean:

* It does **not** affect any capability status in `../capability-audit.yaml`. Every status there
  rests on this verification's own held-out evidence (`../heldout/`), never on the product's suites;
  builder tests are cited as regression evidence only (Contract v3 O3).
* It **does** leave one input of **AC-15** ("`cargo test --lib` and `cargo test --test certification`,
  zero failures") unestablished by this run. The R1-preservation verifier and the synthesis verifier
  should read a completed certification run before AC-15 is called met.

Reproduce with:

```
cd <worktree>
export CARGO_BUILD_JOBS=2
~/.cargo/bin/cargo test --test certification
```

Recorded honestly rather than omitted: see §9 "What I could not establish" of
`../00-VERIFICATION-REPORT.md` and `unresolved` in the run report.

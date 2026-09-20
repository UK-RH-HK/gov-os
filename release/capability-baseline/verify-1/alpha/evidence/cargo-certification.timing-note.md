# `cargo test --test certification` — timing note

This file previously recorded that the certification suite had not completed inside this
verification's window. **It has since completed and its output is captured in
`cargo-certification.out`: 207 passed, 0 failed, 4910.33s.**

The note is kept rather than deleted so the record is honest about the order of events:

1. The suite was started in this worktree (`CARGO_BUILD_JOBS=2`,
   `~/.cargo/bin/cargo test --test certification`) alongside `cargo test --lib`.
2. `cargo test --lib` finished quickly — **276 passed, 0 failed** (`cargo-lib.out`).
3. The certification suite ran for about 82 minutes, because the host was running several Phase-2
   verifiers at once at a load average above 160. It had not finished when
   `00-VERIFICATION-REPORT.md` and the run report were first committed
   (evidence commit `2697acb`, report commit `cfa1a77`), and both said so.
4. It then finished green, and its output was added in a follow-up evidence commit. §2 and §9 of
   the verification report and the run report's `unresolved` list were corrected in the same pass.

No capability status in `../capability-audit.yaml` ever depended on it: every status rests on this
verification's own held-out evidence (`../heldout/`), and builder tests are regression evidence only
(Contract v3 O3). What it establishes is the **AC-15** input — `cargo test --lib` and
`cargo test --test certification`, zero failures — now reproduced by this verifier, independently of
the integrator's own claim of the same numbers.

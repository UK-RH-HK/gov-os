# P2-AR-0096 — orchestrator finding: the revised 5C positive control no longer exercises the production cross-process path

| Field | Value |
|---|---|
| Found by | the Phase-2 outer orchestrator, 2026-09-25, while AR96's third full suite was running |
| Status | **to be corrected before the tree is frozen for Review 8** — it is a gap against an explicit owner instruction, not a reviewer's judgement call |
| Not | a product defect. `runtime/` is unchanged by either of AR96's two flake fixes. |

## The owner's instruction (5C, approved Option B)

> The revised positive control must still prove that a genuine OS-created sandbox works **cross-process WHILE its
> creator remains alive**, while an unrecorded/substituted sandbox does not.

## What AR96 did, and why

`ar94_nc2` case A failed once in full-suite run 1 and again in run 2 — same test, same `NOT_INSTALLED` symptom,
different sandbox instance. The builder's second diagnosis is **correct as far as it goes**: the sandbox it was
probing is a `scheduler/mod.rs` per-family sandbox, whose `create` → checks → `Drop` all happen synchronously inside
one `gov verify governance` invocation. Probing that from outside races a lifecycle with **no lower bound on
survival**, and under 368-test contention a fork+exec+full-CLI round trip sometimes lost.

Its fix: case A stops spawning a `gov` subprocess and instead calls `gov_runtime::paths::adoption_floor_anchor_path_at`
**in-process from the test binary**.

## Why that is not sufficient

The builder's supporting claim is:

> *"Nothing in the product ever reads such a sandbox from a SEPARATE subprocess."*

That is **true for `scheduler/mod.rs`'s per-family sandboxes and false for the product as a whole.**
`skills.rs:528 execute_check` creates a sandbox and then calls `run_gov`, which is
(`skills.rs:489`, verified by the orchestrator at `92982ff`):

```rust
let mut child = std::process::Command::new(gov)
    .args(["--json", "--root"]).arg(root)          // root = sb.root, the sandbox
    .current_dir(root)
    .env(crate::scheduler::sandbox::SANDBOX_ENV, "1")
```

— the **real `gov` binary**, spawned as a child, rooted in the live sandbox. So production *does* read a sandbox
cross-process, and it is the one path where creator-liveness has to hold through a full CLI invocation.

After the fix, the CLI cross-process path is exercised **only by the negative cases** (B1/B2, on an
already-dead-creator sandbox). The positive side of the property is now proved in-process only. That is precisely the
asymmetry the Review-8 context pack warns about: *a guard that refuses everything passes every negative test.*

## The correction, which needs no product change

Probe a sandbox of the **`execute_check` shape** rather than a `scheduler` family sandbox. Its lifetime is bounded
below **by design** — `execute_check` holds `sb` in scope across its whole step loop, precisely so child `gov`
processes can run against it — so a full-CLI round trip is not racing an unbounded lifecycle. That restores the real
production shape and removes the flake's cause at the same time, instead of trading one for the other.

## Why this is being recorded rather than left for Review 8 to find

Review 8 is the convergence decision point (OD-P2-09 §5). Freezing a tree whose positive control does not prove what
the owner's own instruction required would either waste that review or, worse, pass it on evidence that does not
cover the production path. Verifying the builder's load-bearing claims is the orchestrator's job, and this one did
not hold.

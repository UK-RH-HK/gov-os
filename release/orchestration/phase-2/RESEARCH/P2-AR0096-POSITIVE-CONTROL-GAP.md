# P2-AR-0096 — orchestrator finding: **WITHDRAWN**

| Field | Value |
|---|---|
| Raised by | the Phase-2 outer orchestrator, 2026-09-25, while AR96's third full suite was running |
| **Status** | **WITHDRAWN 2026-09-25 — the finding was wrong.** Retained, not deleted: failed iterations are historical evidence (OD-P2-08 §10). |
| Withdrawn on | code read at `3c880d8`, below |

## What I claimed

That AR96's second flake fix — making `ar94_nc2` case A probe in-process instead of spawning `gov` — left the
owner's 5C positive control no longer exercising the production cross-process path, because `skills.rs:528
execute_check` spawns the real `gov` binary rooted in a live sandbox (`skills.rs:489`). I proposed "correcting" the
control to probe an `execute_check`-shaped sandbox instead.

## Why it was wrong

`execute_check` creates its sandbox with `SandboxOptions { runtime: true, git: true }`, and `git: true` runs a
**fresh `git init`** (`scheduler/sandbox.rs:113`). So the sandbox's `repository_lineage_id` never matches the
`bound_repository_lineage` in the floor document it copied.

And `read_project_adoption_floor` checks lineage **before** the identity path: at `paths.rs:1200` a mismatch
**returns early** with `rules: vec![]` and a finding — `FloorIdentity::reconcile`, and therefore
`is_health_sandbox_root`, are never reached.

**Consequence:** the sandbox exemption is never consulted for an `execute_check` sandbox. Its only live consumer is
`scheduler/mod.rs`'s `git: false` per-family sandbox, which is created, used and dropped **entirely in-process**.
The production shape for this mechanism therefore *is* in-process, the builder's fix matches it, and my proposed
correction would have tested a path where the exemption never decides anything.

The builder's disclosure (1) had already recorded the `git:true`/`git:false` distinction and its reason for
filtering. I read that disclosure and still argued past it from a partially-verified inference.

## What this cost, and the lesson for my own record

Nothing, because the check came before the freeze. But this is the **second** load-bearing claim I got wrong in this
phase by reasoning from a partial trace instead of reading to the decision point — the first was proposing the
T2-verified document as a rules authority, which the owner caught. Both times the error had the same shape: I
verified that a path *exists* and did not verify that the path *reaches the decision*. That is precisely the
enumeration-vs-authority confusion this phase keeps finding in the product, appearing in my own reasoning.

## The adjacent observation that IS real, and goes to Review 8

The verification above establishes something worth deciding rather than discarding:

> Inside a `skills::execute_check` scenario sandbox, the project adoption floor is **always** refused — on lineage,
> unconditionally, because `git: true` mints a fresh lineage by construction.

So scenario checks run with **no floor applied at all**. The builder correctly identified this as an AR84-C3-shaped
issue unrelated to the exemption, and correctly declined to fix it in a bounded delta. Whether "a scenario sandbox
never has a floor" is intended, harmless, or a gap is a judgement for Review 8 — it is stated here so the reviewer
inherits the fact rather than rediscovering it.

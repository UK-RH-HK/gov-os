# P2-HO-0059 — AR94 repair round (P2-AR-0095)

| Field | Value |
|---|---|
| Authorised by | **OD-P2-08 §8** — ordinary defects inside the accepted architecture: repair → invalidate evidence → fresh review, automatically |
| Base | `phase2/review-7` **`f2a9ab9`** (product source identical to `a376cc4`; the review adds only `ar94_floor.rs`, one `mod` line, and its probes) |
| Evidence class | **`BUILDER_DEVELOPMENT_EVIDENCE`** — nothing you write closes a finding |
| Review being answered | P2-AR-0094, `probes/P2-AR-0094/P2-AR-0094-REVIEW.md`. **Read it in full first.** |

## 0. What held, what failed

**Property A holds for the third consecutive round.** `exec_resolve.rs` is untouched and its closure re-ran 22/0.
**Do not touch it.** Any change there is out of scope.

**The AR92 repair you are building on was real** — all four of AR92's HIGH reproductions are genuinely closed
(`ar92_floor` 11/11, independently re-run), the liveness conjunct is gone with the whole C1 family, and the sandbox
exemption really is decided by an OS record that still works for a real sandbox (the reviewer built the positive
control the last round lacked: `ar94_nc2`, green in both directions).

**What failed is the seventh instance of one pattern.** The round added two places where **authority is determined
outside the representation being checked**: a capability written to disk that outlives the thing it describes, and a
remedy that reads the identity it moves **out of a file the attacker can write**.

## 1. Non-deferrable. Both HIGHs and the three MEDIUMs that compose with them

I verified each of the following in the code myself before writing this. Do not re-derive; fix.

### 1.1 AR94-C2 (HIGH) — `floor-reanchor` must take the identity from the store, never from the document

`reanchor_project_identity` (`paths.rs:1301`) reads `doc.get("bound_project_identity")` **from the floor document on
disk**, then scans the store for *that* identity and moves it to the current path. **It never asks whether this
checkout is entitled to that identity.** Its two other checks do not cover the gap: the T2 seal carries no path and
no identity (AR84-C3), and the git lineage is public and reproducible by cloning (AR86-C1).

Measured attack: **one project-scoped file copy** by the attacker; the owner relocates their own checkout — the case
the remedy exists for — and follows the advice the OS itself prints (`refusal_text_names_floor_reanchor=true`). The
owner's live checkout then carries the **attacker's** identity, `last_known_rules` becomes the attacker's weaker set,
`src/**` leaves the floor, `d027_ok=true`, and **nothing anywhere says the identity moved.**

This is exactly OD-P2-08 §2's forbidden shape: an ordinary edit plus an ordinary owner action silently removes an
authenticated obligation.

**The repair — take the identity from the store and make the human name it.** `gov floor-reanchor --from <previous
canonical path>`, looked up by `sha256(<previous path>)`, the key the store already uses. Refuse unless the
document's `bound_project_identity` equals **that entry's** identity. The planted document then names a different
identity than the entry at the path the owner named, and it refuses.

**Note what this is and is not.** You are adding an *argument*, not a mechanism — the decision moves to the operator,
who is the only party that knows which checkout this was. That is a narrowing, not another layer. **Do not add a
second mechanism to compensate for the first.**

### 1.2 AR94-C1 (HIGH) — the sandbox marker is a capability, and minting one is free

I verified: `remove_sandbox_record` has **exactly one caller**, `sandbox.rs:144` in `Drop`. There is **no GC of any
kind.** Rust installs no signal handler, so SIGKILL/SIGINT/OOM/power-loss all skip `Drop` and the marker persists.

And it is cheaper than the chain I derived. The adversary need not watch the victim or wait for the victim's process
to die: the marker's path comes from `p.runtime_dir()` of **whichever project the health run started in**, so an
adversary who can run `gov` against **their own** project mints a marker for a directory **they own** and kills
**their own** process. Measured: `markers_after_SIGKILL=[…]`, donor still live, victim moved into that path →
`effective_class="generated"`, `d027_ok=true`, `finding=None`.

**This re-classifies a LOW.** Unbounded `health-sandboxes/` growth is not storage hygiene — **every leaked entry is a
standing capability.** The previous builder's classification was wrong.

**The repair — delete the durable artefact.** `Sandbox::create` and the code that later reads the sandbox run in the
**same process**, so a **process-local registry** of live sandbox roots (insert on create, remove on drop) cannot
leak. That is a deletion, which is why it is the right shape.

**One warning, and take it seriously.** For a child `gov` process the reviewer offers binding the existing
`SANDBOX_ENV` handshake to a per-sandbox nonce. An environment variable is **ambient authority** — the exact class
Property A exists to refuse. If you need the child path at all, the nonce must be unguessable, single-use, and
verified against process-local state the parent holds; if you cannot make it that, use the pid+start-time fallback,
or report that the child path cannot be secured and say so plainly. **Do not quietly trust an env var.**

### 1.3 AR94-C3 (MEDIUM) — a command that destroys machine state and reports success

`FloorIdentity::write_full` (`paths.rs:788`) returns `Ok(())` **without writing** when `path(root)` is `None`, and
`reanchor` then runs `remove_dir_all(&old_dir)` unconditionally. Verified. Inside a root holding the sandbox
exemption: store goes 2 entries → 1, nothing is written, and the command reports `reanchored: true`. That destroys
`max_known_sequence` (AR86-C3 rollback protection) and `last_known_rules` (AR86-C6).

**Repair:** refuse when `FloorIdentity::path(root)` is `None`, and make `write_full` return a **typed error** rather
than `Ok(())` when it writes nothing. A function that reports success for work it did not do is a defect wherever it
appears — check whether `write_full` has other callers relying on the silent `Ok`.

### 1.4 AR94-C4 (MEDIUM) — the advice the OS prints is destructive for the second-checkout case

Measured: at a second working copy, following the printed remedy takes the **first** checkout's floor —
`first_AFTER=[finding=true, d027_ok=false]`. AR92 §8 specifically asked that the finding text name the
second-checkout case with the **re-onboarding** remedy; `advice_names_second_checkout_case=false` — it was not
implemented. Implement it. Once 1.1 lands, `--from` makes this an explicit decision rather than a silent transfer.

### 1.5 AR94-D1 (MEDIUM) — disclose the transfer

`bootstrap_disclosure`'s own doc claims it covers "a completed `reanchor_project_identity`". It does not: `reanchor`
carries the old entry's `bootstrap_adopted` forward, and a `gov init` entry has it `false`, so after a successful
re-anchor `disclosures=[]`. **This is what makes AR94-C2 invisible.** Mark the entry the re-anchor writes so the
transfer discloses on every later read.

The reviewer cleared two things here, so do not redo them: routing abuse is **not** possible (separate fields; every
refusal path returns `..Default::default()`), and the durable field has no consumption path. But its **reach** is one
surface — `gov policy overrides`'s `"disclosures"` key at `cli/src/main.rs:2321`, with no doctor check, no health
family, no telemetry. Widen the reach.

## 2. Second-order — take if clean, otherwise name precisely

* **AR94-D5.** `ADOPTION_FLOOR_REANCHOR_NO_PRIOR_CLAIM` is effectively **dead code** (any `gov` invocation's policy
  load reaches `reconcile` first). It fails closed. Label it defence in depth; do not present it as the guard.
  Rename `ar92_c4_a_bare_relocation_re_anchors_silently` — its name now contradicts its own assertion. **This is the
  one rename you are authorised to make**, because the reviewer named it as a defect.
* **AR94-D3.** The two parallel label tables. The reviewer independently confirmed my ruling that this is **not** an
  authority hole (`command_name`'s result is discarded at `main.rs:2365`; every `g0_label` string has a guard row;
  unmatched labels fail closed). LOW, real defect class.
* **AR94-D4.** A bare relocation now takes `gov doctor` **DEGRADED → UNHEALTHY**. Correct, but a larger blast radius
  than "a finding appears". State it as a cost in the docs rather than changing it.
* **AR92-D1/D2** unchanged, carried forward. **AR90-C7 is largely CLOSED** — do not reopen it.

## 3. The standing rule, seventh time

**Remove ambient authority. Do not extend lists, and do not add a mechanism to guard a mechanism.** The failure chain
is now: programs → shapes → list premises → class values → consumers → obligations → a liveness predicate → **a
capability that outlives its subject, and a trusted input read from a file the attacker can write.**

Both repairs above are a **deletion** (the durable marker) and a **narrowing** (the identity comes from the store,
named by the operator). If you find yourself adding a third thing to make the second thing safe, stop and report it.

Do not touch `t2::mac_message`. Do not build a hand-edit detector. Do not introduce Landlock/containers/microVMs. Do
not reopen Level 1 / R0 / R1.

## 4. Tests and evidence

`tests/certification/ar94_floor.rs` is **released** and is your regression target: currently **5 passed / 5 failed**
— the 5 failures are the findings, the 5 passes are controls that must stay green, including **`ar94_nc2`**, the
positive control proving a genuine OS-recorded sandbox still gets the exemption and a byte-identical copy at a
sibling path does not. **A guard that refuses everything passes every negative test; that control is what stops you.**

Also green, independently re-run by the reviewer and yours to keep: `ar92_probe ar90_probe ar88_` (22/0),
`ar90_floor ar83_governed_widening multi_machine::clone_rebuilds_identical_derived_state
brownfield::brownfield_adoption_end_to_end` (15/0), `ar92_floor` (11/0). All five OC-P2-04 cases reachable and
reportable; `floor_requires_product=false`; conforming pinned ELF ungated **and running**; foreign clone still
bootstraps healthy.

Your tests are development evidence only, **including property and generative tests**. **Name the cases your
generators cannot reach** — every builder in this phase has done it and it has been the most useful part of each
handover. The reviewer's own unprobed list: `reanchor` concurrency (constructed as `ar94_c5`, but the invocations
serialised, so **not ruled out**), glibc+musl, malformed-ELF fuzzing, the `verify`→`Command` TOCTOU window, bind
mounts, SIGINT specifically (SIGKILL measured; SIGINT reasoned same-class), `bound_cit` naming an unknown
transaction, hand-edited `cit_status`.

Product lines change, so **one full certification run is required** (~58 min at 363 tests, default threads). Never
`--test-threads=1`. Never pipe without `set -o pipefail`. Never bare `cargo fmt`. `. "$HOME/.cargo/env"` is refused
by the worktree sandbox guard — use `"$HOME/.cargo/bin/cargo"` directly. Record command/commit/count/threads/load/
duration for every figure.

You are pre-authorised to change what an existing test asserts where this repair makes its old claim false — every
changed assertion listed with old and new claim, never weakened to pass, **and only the one rename named in §2**.

## 5. Anti-stall

Never wait on me. Do not ask permission to start the full suite: proceed when no competing `cargo`/`gov` process runs
and load is below ~4; otherwise wait bounded and **proceed automatically**. Every wait needs a bounded iteration
count and a deterministic timeout action. If you match processes, prove the waiter cannot match itself. Checkpoint to
`telemetry/checkpoints/P2-AR-0095.checkpoint.md`.

## 6. Return

Verdict; **what you deleted**; each §1 item with the mechanism now enforcing it and the reproduction proving it; how
you handled the child-process path in 1.2 and whether an env var is trusted anywhere in it; each §2 item taken or
named; changed assertions with old and new claims; tests added by kind; **the cases your generators cannot reach**;
every check with full figures; anything left undone; your commit SHA.

An accurate `PARTIAL` naming a real weakness is worth far more than a confident `REPAIRED_CLAIMED`.

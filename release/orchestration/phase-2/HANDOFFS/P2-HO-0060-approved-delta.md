# P2-HO-0060 — the complete owner-approved delta (P2-AR-0096)

| Field | Value |
|---|---|
| Authorised by | the owner's decision approving fresh-identity re-onboarding, plus the accepted trust-source correction |
| Base | `phase2/remediation-ar94` **`92982ff`** (full suite 373/0) |
| Evidence class | **`BUILDER_DEVELOPMENT_EVIDENCE`** |
| Design records | `RESEARCH/P2-PROBE-OPTION-C.md`, `RESEARCH/P2-HISTORICAL-RULE-SOURCE.md`. **Read both first.** |
| Next | targeted → affected regression → required full certification → Review-8 context pack → Review 8 |

## 0. This round is mostly deletion. That is the point.

Seven reviews have failed by adding a mechanism to guard the previous mechanism. This delta **removes** a command,
a race, and five findings, and adds one condition plus one read. **If you find yourself adding a guard, stop and
report.**

## 1. Delete `gov floor-reanchor` entirely — non-deferrable

Remove the command, its `--from` argument, `reanchor_project_identity`, its error codes, its guard row, its
`g0_label`/`command_name` entries, and its tests. **AR94-C2, C3, C4, D1, D5 and the confirmed C5 race all go with
it** — the transfer primitive that produced all six stops existing. Do not leave a deprecated stub.

The owner's invariant, which this delta must hold **by construction, not by a check**:

> Relocation never transfers trusted identity between paths. A stale old binding may be invalidated or left inert. A
> new location receives authority only through the normal authenticated adoption/onboarding transaction.

**Do not build `floor-forget`.** The stale entry is inert once identities are fresh (proved: a fresh identity never
matches `other_live_claim`'s scan). Its unbounded growth stays the known LOW, AR90-C7.

## 2. Fresh-identity re-onboarding — non-deferrable

`init.rs:303` and `adopt.rs:1840` currently write the floor only `if !already_installed`. Extend that condition to
fire **also when this checkout holds no authenticated anchor for its current canonical path**, even though
`framework.lock` exists. Authority is unchanged: `init` and `adopt` already require `install_kernel` via G0.

`FloorIdentity::advance` (`paths.rs:728`) already mints `uuid::Uuid::new_v4()` when this checkout has no entry —
which is exactly the relocated state — so a **fresh identity falls out of the existing code**. Do not add an
identity-minting path. A second working copy follows the same rule and gets its own fresh identity, which fixes
AR92-C3 as a side effect.

**Measured, so you know the shape of the bug you are removing** (`RESEARCH/P2-PROBE-OPTION-C.md`): deleting the stale
entry alone makes the repository healthy again but re-establishes the **same identity at the new path, taken from
the document** — the system's own disclosure says *"never by this checkout's own onboarding"*. That is the state
this item must make unreachable.

## 3. Never-weaker rule preservation from a proof-grade source — non-deferrable

**Read `RESEARCH/P2-HISTORICAL-RULE-SOURCE.md` in full before writing this.** The orchestrator proposed inheriting
rules from the T2-verified document; the owner rejected it, correctly — **OD-P2-08 §2 makes the T2 seal detection,
never proof-grade.** The document must not be consulted for rules here.

The approved source is the **protected machine store** — `FloorIdentity::last_known_rules`, under
`srr::state::resolve_state_root()`, outside every project, unreachable by an ordinary actor (AR88).

The rule:

```
floor written at re-onboarding  =  native derivation  ∪  conservative union of last_known_rules across the store
```

**additive only**, exactly like the existing AR86-C6 union in `policy.rs` — add a historical rule **only for a
pattern the fresh derivation does not already cover**, so the fresh derivation always wins on conflict and no class
is ever displaced. Because the union is additive, you **never need to decide which historical entry owns this
checkout** — which is what would have required trusting a project-editable identity claim. Reuse the shape already
in `policy.rs`; do not invent a second one.

**Where it goes is load-bearing.** It must be in the derivation `init`/`adopt` hand to
`write_project_adoption_floor` — **not only** in `PolicySet::load`'s reconstruction fallback. Once re-onboarding
writes a floor, `adoption_floor.rules` is non-empty and reconstruction never fires, so a weak derived floor would be
promoted to *authenticated*: strictly worse than the case it replaces.

**Disclose it** (OC-P2-04 §4): the re-onboarding must report which patterns were restored and that they came from
protected machine state rather than this repository's current shape.

## 4. Sandbox exemption = creator liveness — non-deferrable (owner-approved 5C Option B)

Approved semantics:

```
live OS-created sandbox              → exemption may be valid
creating/owning process dies         → exemption is no longer authoritative → fail closed → cleanup/rebuild
```

**Delete the inode-binding and the GC** added in P2-AR-0095 if no production path still needs them. The orchestrator
verified none does: `skills.rs:528 execute_check` holds its `Sandbox` alive across every child `gov` call
(`run_gov`), so the creator is alive for **every** production read. Cross-process, yes; post-mortem, never.

**`ar94_nc2` must be revised**, on the owner's explicit instruction — it currently uses `spawn_and_kill_when` to
SIGKILL the creator, which encodes the old implementation rather than a product requirement. The revised control must
still prove **both**: a genuine OS-created sandbox works **cross-process while its creator is alive**, and an
unrecorded or substituted sandbox does **not**.

**No environment variable may carry authority.** P2-AR-0095 confirmed `SANDBOX_ENV` is not referenced in the
exemption decision; keep it that way. If creator liveness needs a cross-process signal, use pid plus process start
time — never a value a child can be handed.

## 5. Do not do

No new command. No new subsystem. No `floor-forget`. No hand-edit detector. No treating T2 as proof-grade. No
Landlock/bubblewrap/containers/microVMs. No reopening Level 1 / R0 / R1. Do not touch `t2::mac_message`. **Do not
touch `runtime/src/exec_resolve.rs`** — Property A has held three consecutive independent reviews and is out of
scope.

## 6. Tests

Expect to **delete** every `floor-reanchor` test and to rewrite `ar94_nc2`. You are pre-authorised to change what an
existing test asserts where this delta makes its old claim false, and to delete tests whose subject no longer
exists — every change listed with old and new claim, never weakened to pass.

Must stay green: `ar92_probe ar90_probe ar88_` (22/0), `ar90_floor ar83_governed_widening
multi_machine::clone_rebuilds_identical_derived_state brownfield::brownfield_adoption_end_to_end` (15/0). All five
OC-P2-04 cases reachable and reportable; `floor_requires_product=false`; conforming pinned ELF ungated **and
running**; a genuine foreign clone still bootstraps healthy.

**Add** end-to-end coverage for the new lifecycle: relocate → refused → re-onboard → **fresh** identity (assert it
differs from the original), freshly derived floor, D027 healthy, old entry inert, **and** the never-weaker union
proven by reshaping a directory under an `ALWAYS_EXCLUDED_DIRS` name before re-onboarding and showing the pattern is
still floored. Also: a second live checkout re-onboards to its own identity without disturbing the first.

Product lines change, so **one full certification run is required** (~60 min at 373 tests, default threads). Never
`--test-threads=1`. Never pipe without `set -o pipefail`. Never bare `cargo fmt`. Use `"$HOME/.cargo/bin/cargo"`
directly. Record command/commit/count/threads/load/duration for every figure.

## 7. Anti-stall

Never wait on the coordinator. Do not ask permission to start the full suite — evaluate the precondition yourself and
proceed automatically. Every wait needs a bounded iteration count and a deterministic timeout action. If you match
processes, prove the waiter cannot match itself. Checkpoint to `telemetry/checkpoints/P2-AR-0096.checkpoint.md`.

## 8. Return

Verdict; **what you deleted**, as the headline; each §1–§4 item with the mechanism and the reproduction proving it;
where the union is applied and why there; the disclosure added; the revised `ar94_nc2` and what it now proves;
changed and deleted tests with old and new claims; **the cases your generators cannot reach**; every check with full
figures; anything left undone; your commit SHA.

An accurate `PARTIAL` naming a real weakness is worth far more than a confident `REPAIRED_CLAIMED`. The previous
builder declared a deviation from its brief rather than burying it, and that disclosure is why this delta exists —
hold that standard.

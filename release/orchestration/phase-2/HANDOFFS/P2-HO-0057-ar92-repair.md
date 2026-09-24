# P2-HO-0057 — AR92 repair round (P2-AR-0093)

| Field | Value |
|---|---|
| Authorised by | **OD-P2-08 §8** — an ordinary implementation defect *within* the accepted architecture: repair → invalidate affected evidence → fresh review, **automatically, without returning to the owner** |
| Base | `phase2/review-6` **`4686e8d`** (product source identical to `a01f0c9`; the review adds only probes and its own two test files) |
| Evidence class | **`BUILDER_DEVELOPMENT_EVIDENCE`** — nothing you write closes a finding |
| Review being answered | P2-AR-0092, `probes/P2-AR-0092/P2-AR-0092-REVIEW.md`. **Read it in full first.** |
| Next | one full suite → freeze → seventh independent Opus adversarial review |

## 0. What the review found, and what it did not

**Property A HOLDS** for the second round running, and the reviewer re-proved AR88-F4 is not re-opened.
**Do not touch `exec_resolve.rs`.** Any change there is out of scope and will be treated as a regression risk with no
finding behind it.

**Property C FAILS.** `other_live_claim` — the first mechanism in six rounds to ask a question the attacker cannot
answer for the OS — then conditions its answer on `Path::exists()` of **a string the attacker chose**.

All seven OD-P2-08 §8 stop conditions were evaluated by the reviewer and answered NO, and I independently re-checked
the three that decide it (below). This is a repair round, not an escalation.

## 1. Non-deferrable. All four. None of these may be carried to a later round

Three previous rounds deferred a named item because my brief listed it among several. That was my defect, not the
builders'. So: **items 1.1–1.4 are each a blocking obligation. If you cannot complete one, you report `PARTIAL` and
name it — you do not silently carry it.**

### 1.1 Drop the liveness conjunct (closes AR92-C1, C1B, C1C — three HIGH)

`runtime/src/paths.rs:651`:

```rust
if minted_for != current_canon && Path::new(minted_for).exists() {
```

The `exists()` conjunct is a **liveness test on a path the adversary supplies**, so the guard refuses only the
careless adversary. Three proved ways past it, all silent, all in the review's own reproductions:

* **C1** — `mv` the donor aside, then `mv` the victim. Measured **permanent**: restoring the donor afterwards does
  not restore the refusal. One read during a momentary absence converts the checkout for good.
* **C1B** — the donor need not move at all. `Path::exists()` **fails open on `EACCES`**: `chmod 000` on the donor's
  parent makes an intact donor read as gone. Same class: dangling symlink, unmounted filesystem, removed component.
* **C1C — the cheapest, and the one that decides this round.** Mint the donor *inside* the victim (AR86-C2's
  subdirectory oracle, still open), plant the floor, and **the owner's own rename** removes the donor's mint path as
  a side effect. Every attacker write is inside the project root and **the attacker performs no move at all.** That
  is precisely the shape OD-P2-08 §2 forbids: an ordinary project-scoped write acquiring authority.

**The repair:** refuse the bootstrap whenever this machine's store holds **any** entry for the claimed identity, live
or stale. Delete the conjunct; do not replace it with a better liveness test, a staleness window, or a second
condition. The attacker cannot remove a store entry — reaching `<state_root>/adoption-floors/` is exactly the
privilege AR88 established they do not have.

**I verified the two claims this repair rests on, myself, rather than relaying them:**

* **Portability is untouched.** `other_live_claim` scans `resolve_state_root()`'s own `adoption-floors/`, and
  `srr/state.rs:95` refuses an environment variable relocating a provisioned machine's protected root. A genuine
  foreign clone's new machine has **no entry for that identity at all**, so it still bootstraps. P2-ADJ-0002 and
  `multi_machine::clone_rebuilds_identical_derived_state` are not at risk. **Prove it anyway — that test is a hard
  constraint and must be green.**
* **The repair opens no pre-poisoning denial channel.** `project_identity` is `uuid::Uuid::new_v4()`
  (`paths.rs:730`), never derived from repository content, so an attacker cannot pre-mint a store entry for an
  identity the victim will later generate. This is the check that would have made "any entry, live or stale"
  dangerous, and it comes out clean. Do not weaken the uuid derivation.

### 1.2 Grant the sandbox exemption from the OS's own record, not from a path's spelling (AR92-C2, HIGH)

`is_health_sandbox_root` (`paths.rs:556`) matches **four trailing path components** and consults nothing else. It is
the **only unconditional bypass** of the guard, and it is reachable: `mkdir -p …/.governance-runtime/health/
sandboxes/purpose-xxxx` **outside any governed project**, plus one `mv`, bypasses the check with the donor **still
live** (`donor_still_live=true anchor_path=None`). The previous round's justification — that `RUNTIME_DIR` is
`mutation: os-only` territory — is true and irrelevant: the shaped directory is not inside any governed project, so
no policy governs creating it. Canonicalisation closed the *symlinked* route (`ar90_c4` green) and does nothing
about a real directory of that shape.

`Sandbox::create` is OS code in the same process that later reads the sandbox. **Record the sandbox root in the
machine store the OS already owns, and require that record** — a path shape is not a capability. This introduces no
new authority: it is the same store, written by the same OS, at a moment the OS already controls.

### 1.3 A refused relocation must have a remedy that actually works — demonstrated, not cited

This is the obligation most likely to be skipped, and the only one that could turn this round into a genuine owner
decision. 1.1 makes two *legitimate* situations fail closed:

* a legitimate relocation of the owner's own checkout (today: silently adopted — AR92-C4);
* **AR92-C3**, already true at `a01f0c9`: an ordinary second working copy on the same machine (`git clone`,
  `git worktree add`) is refused its own committed floor, **permanently**, with D027 failing.

The review's proposed exit is an explicit re-anchor via the `gov init` / `gov adopt` re-derivation the current
finding text already names. **Demonstrate that end-to-end in a test:** relocate (or make a second checkout), observe
the refusal and the finding, run the named remedy, and show the floor honoured again with D027 healthy and the
authenticated obligations intact. Re-anchoring must **update** the identity's existing store entry, not append a
second one (see 2.3).

**If that remedy cannot be made to work without inventing a new trusted authority, stop and report it** — that is an
OD-P2-08 §8 stop condition and it is mine to escalate, not yours to work around.

### 1.4 The relocation must not be silent (AR92-C4, MEDIUM — but it is the enabling condition)

A bare relocation today mints a new anchor from the document's own claim with **no finding, no doctor change, D027
healthy**. Strictly, OC-P2-04 §4's five reportables do not list a relocation, so a narrow reading is satisfied. That
narrow reading is not available here: **this silence is what makes C1, C1B and C1C invisible.** From the OS's point
of view the attack and the legitimate move are indistinguishable, and it says nothing in either case. Report the
event — the same disclosure serves the honest owner and removes the attacker's cover.

## 2. Second-order. Fix if it is clean inside the existing construction; otherwise name it precisely

These are not blocking. **Naming one accurately is worth more than a rushed change**, and a rushed change here costs
a round.

* **2.1 `bound_cit` is detection, not binding (AR92-D1, LOW).** The gate reads `cit_status` via `RecordStore::load`,
  which verifies **no seal** although `cit` is in `t2::SEALED_RECORD_TYPES`, and matches on **id alone**, never
  `cit::binding::writes_sha256`. The reviewer confirmed `bound_cit` blocks no legitimate governed widening
  (`ar83_governed_widening` 2/2) and does refuse a floor naming a transaction this store never had (`ar90_c5`).
  Correctly labelled defence in depth — **so make the code and its documentation say that**, and do not describe it
  as binding authority.
* **2.2 The rollback residual.** A legitimately rolled-back floor reads as *stale* until one more governed
  reclassification. Fail-closed, disclosed, and it clears — the reviewer explicitly ruled it **not** a reason to
  withhold the candidate. The suggested shape is advancing the anchor on commit with a `pending_sequence` for the
  crash case: one more field in a file the OS already owns. Take it only if it is genuinely that small.
* **2.3 AR90-C7 now matters (elevated by this round's own design).** Stale entries are no longer inert — they are
  what `other_live_claim` reads, and after 1.1 every entry is a permanent claim. Every relocation mints an entry and
  removes none. Recreating a directory at a stale mint path is a cheap DoS on the owner's own project. At minimum,
  re-anchoring must update in place. Unbounded growth beyond that: name it with your reasoning.
* **2.4 `manifest_paths` is still hand-enumerated (AR92-D2, LOW).** `regenerate_views` names no path;
  `install_tool` pushes its registry only `if let Some(r)` where `register_plugin` has a default. Everything the
  reviewer could find escaping is a *derived* artefact, so this is consistency rather than authority — **but the
  next authoritative writer added to `apply_op` reproduces AR90-C6 exactly.** A structural fix at the existing
  construction point is welcome. A broader refactor is not.

## 3. The standing architectural rule

**OD-P2-08 §1: remove ambient authority. Do not extend lists.** Seven rounds have now failed by enumeration —
programs → shapes → list premises → class values → consumers → obligations → **and now a liveness predicate on an
attacker-chosen string.** The pattern is always the same: *the check reasons about a representation while the
authority is determined outside it.* `exists()` is that defect in one conjunct.

**If you find yourself adding a name, a shape, a window or a second condition to make a case pass, you are doing the
wrong thing.** Both repairs above are *deletions and substitutions*, and both are smaller than any predecessor's.

Do not build a hand-edit detector. Do not treat the T2 seal as proof-grade. Do not introduce Landlock, bubblewrap,
containers or microVMs. Do not reopen Level 1 / R0 / R1. Do not touch `t2::mac_message`.

## 4. Tests, evidence and the cases your generators cannot reach

The AR92 probes are **released** — the reviewer's verdict is committed, so `tests/certification/ar92_floor.rs` and
`ar92_probe.rs` are now regression evidence you must turn green (`ar92_floor` is currently 1 passed / 6 failed; the
1 is the reviewer's negative control **AR92-NC1**, which must stay green — it proves the mechanism works where its
precondition holds).

Green everything the review re-ran independently, and do not pass by gating more: `ar92_probe ar90_probe ar88_`
(22/0), `ar90_floor ar83_governed_widening multi_machine::clone_rebuilds_identical_derived_state
brownfield::brownfield_adoption_end_to_end` (15/0). **All five OC-P2-04 cases must stay reachable and reportable**,
`floor_requires_product=false` must stay false, and a conforming pinned ELF must stay ungated **and running**.

Your tests are development evidence only — **including property and generative tests. A generative test is not
independent merely because it generates many cases.** So: **name the cases your generators cannot reach.** The last
three builders did this unprompted and it was the most valuable part of all three handovers. The AR92 reviewer's
own "what I could not probe" list is the standard.

**Product lines change, so one full certification run is required.** It costs **~50–62 minutes** (measured: 350
tests, 3,380 s at load 0.63). Never `--test-threads=1`. Never pipe a test command without `set -o pipefail`. Never
run bare `cargo fmt`. Start commands with `. "$HOME/.cargo/env"`. Record with every suite figure: exact command,
commit, test count, thread setting, machine load, duration, outcome.

You are pre-authorised to change what an existing test asserts where this repair makes its old claim false — **no
renames**, every changed assertion listed with old and new claim, never weakened to pass. If a test cannot be
satisfied by a *correct* implementation, stop and report it.

## 5. Anti-stall — you must never wait on me

`worker_stall_protection` is ACTIVE. **Do not ask permission to start your full suite.** Evaluate the precondition
yourself: proceed when no competing `cargo`/`gov` process runs and load is below ~4; otherwise wait, re-check, and
**proceed automatically**.

Every wait needs a **bounded iteration count** and a **deterministic timeout action**. If you use process matching,
**prove the waiter cannot match itself** — a `pgrep -f <pattern>` inside a shell whose own command line contains that
pattern never exits, which cost this orchestration ten hours. Prefer waiting on file content, as the AR92 reviewer
did. If you genuinely need a decision, report `BLOCKED_ON_COORDINATOR` with the timeout and the default action you
will then take — **and take it**.

Checkpoint to `telemetry/checkpoints/P2-AR-0093.checkpoint.md` before the full suite and after each item in §1 lands.

## 6. Return

Verdict; **what you deleted**; each §1 item with the mechanism that now enforces it and the reproduction that proves
it; the demonstrated re-anchor remedy; the disclosure added for a relocation; each §2 item taken or named with
reasoning; changed test assertions with old and new claims; tests added with kinds; **the cases your generators
cannot reach**; every check with command/commit/count/threads/load/duration; anything left undone; your commit SHA.

An accurate `PARTIAL` naming a real weakness is worth far more than a confident `REPAIRED_CLAIMED`. The reviewer who
follows you is independent, adversarial, and has now broken this surface at argv, wrapper arguments, shebang, the
dynamic loader, and a liveness predicate.

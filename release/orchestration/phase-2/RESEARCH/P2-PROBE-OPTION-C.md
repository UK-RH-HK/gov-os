# P2-PROBE-OPTION-C — owner-ordered end-to-end proof of the proposed Option-C lifecycle

| Field | Value |
|---|---|
| Run by | the Phase-2 outer orchestrator, 2026-09-24 |
| Ordered by | the owner's pre-final sweep response: *"Before I approve C, prove those statements are compatible."* |
| Subject | `92982ff` (P2-AR-0095), probed in an isolated detached worktree |
| Method | read/probe/design. The delete-only operation is **simulated** by removing the machine-store entry directory. **Nothing named `floor-forget` was built** — per the owner, it must not be built merely to prove itself. |
| Probe source | `P2-PROBE-OPTION-C.rs` (beside this file). Not product code; not committed to the certification suite. |
| **Verdict** | **`OPTION_C_REQUIRES_ONBOARDING_CHANGE`** |

## The two statements under test

1. *(orchestrator)* `init`/`adopt` do not re-establish a floor after relocation — both gate on `!already_installed`.
2. *(Option C)* delete the stale entry and **the existing bootstrap/adoption path then succeeds**, with no onboarding
   change required.

**Both are literally true. They are not compatible with the owner's invariant**, and the probe shows exactly why.

## Probe 1 — the full lifecycle, measured

| Step | Measurement |
|---|---|
| **1. adopted** | `eff(src/**)="source"`, `finding=false`, `d027_ok=true`, store `[(6548006e…, 1, /tmp/gov-cert-oclife-…)]` |
| **2. relocated** | `finding=true`, `d027_ok=false`, **D027 absent** — refuses safely, as designed |
| **3. after simulated forget** | `finding=false`, `d027_ok=true`, `eff="source"` — **operationally healthy again** |
| | store `[(6548006e…, 1, **/tmp/oclife-relocated**)]` — **the same identity, now minted for the new path** |
| | `IDENTITY_AFTER_FORGET == identity_before` → **`identity_unchanged_from_document=true`** |
| **4. existing onboarding** | `gov init` → **`ALREADY_INSTALLED`**; `framework_lock_present_at_new_path=true` |

**The system's own disclosure text is the finding.** Step 3 emits `PROJECT_ADOPTION_FLOOR_BOOTSTRAPPED` whose reason
reads:

> *"…was established by adopting `governance/registry/project-adoption-floor.json`'s own claim (a portable clone, or a
> completed re-anchor), **never by this checkout's own onboarding**…"*

So deleting the stale entry does not route relocation through onboarding. It routes it through the **bootstrap-adopt
branch**, which takes the identity **from the document**. The identity is still transferred between paths — by a
different mechanism than `floor-reanchor`, with the same end state.

Measured against the owner's stated invariant:

```
relocation never transfers trusted identity between paths          → VIOLATED (identity unchanged, path changed)
a stale old binding may be invalidated/deleted                     → satisfied
a new location receives authority only through the normal
  authenticated adoption/onboarding transaction                    → VIOLATED (bootstrap-adopt, not onboarding)
```

## Probe 2 — second live checkout

| Step | First checkout | Second checkout (`git clone`) |
|---|---|---|
| both live | healthy, `d027_ok=true` | `finding=true`, `d027_ok=false` (the known AR92-C3 state) |
| after deleting the **first**'s entry | re-bootstraps, **takes its identity back**, disclosure fires | **unchanged — still refused** |

**No second live checkout is silently invalidated** by the delete-only operation. It is also not helped by it.

## The simpler operation the owner asked me to look for — it exists, and it is better

> *"Also check whether an even simpler operation exists: explicit governed 'forget old project binding' + existing
> `gov adopt`/re-onboard, without introducing a new long-lived recovery subsystem."*

**Neither a forget operation nor a recovery subsystem is needed.** The decisive fact is `FloorIdentity::advance`
(`paths.rs:728`): it mints `uuid::Uuid::new_v4()` whenever this checkout has no entry of its own — which is exactly
the state a relocated checkout is in. So if onboarding is allowed to run at the new path, it mints a **fresh**
identity:

* `other_live_claim` scans for the **new** identity, finds nothing, and never refuses;
* the stale old entry becomes **inert** — nothing needs to delete it (its unbounded growth stays the known LOW
  AR90-C7, unchanged);
* **no identity is transferred between paths** — the invariant holds by construction, not by a check;
* **AR92-C3 is fixed as a side effect**: a second working copy re-onboards to its own fresh identity instead of being
  permanently refused.

### The minimum change

1. **Delete `gov floor-reanchor` entirely** — with it go AR94-C2, C3, C4, D1, D5 and the confirmed C5 race, because
   the transfer primitive that produced all six stops existing.
2. **Relax one gate at two sites** — `init.rs:303` and `adopt.rs:1840` currently write the floor only
   `if !already_installed`. Extend that to *"or this checkout holds no anchor of its own for its current path"*, so a
   relocated repository re-runs the adoption decision under the **existing `install_kernel` authority** `init` and
   `adopt` already require. No new authority, no new command, no new subsystem.
3. **Nothing else.** No `floor-forget`.

### One risk I am naming rather than leaving for Review 8 to find

Re-derivation reads the repository's **current on-disk shape**. At a new path there is no entry, therefore no
`last_known_rules`, so AR86-C6's "a reconstruction is never weaker than what was last known good" protection does not
apply to the re-onboarding case. An attacker who reshaped the tree before the owner re-onboards could obtain a weaker
derived floor.

**Proposed mitigation, inside the existing design:** on re-onboarding, take the union of the freshly derived native
rules with the rules of the **T2-verified, lineage-bound floor document already present** — inheriting its *rules*
while minting a *fresh identity*. That separation is the whole point: a verified document is trustworthy about **what
this repository's layout obliges**, and must never be trusted about **which identity this checkout is**.

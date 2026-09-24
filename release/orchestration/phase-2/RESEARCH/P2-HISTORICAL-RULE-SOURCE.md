# P2 — proof-grade source for last-known-good floor rules

| Field | Value |
|---|---|
| Ordered by | the owner's decision approving fresh-identity re-onboarding, with a trust-source correction |
| **Verdict** | **`HISTORICAL_RULE_SOURCE_REUSES_EXISTING_PROOF_GRADE_PRIMITIVE`** |
| Method | read/probe/design at `92982ff`. No new command, no new subsystem, no new authority mechanism. |

## The owner's correction, accepted

I proposed inheriting rules from "the T2-verified, lineage-bound floor document". **That was wrong** and the owner
caught it: OD-P2-08 §2 establishes the T2 seal as **detection and defence in depth, never proof-grade**, because its
symmetric key is readable inside the local OS trust domain. My mitigation would have re-admitted the document as an
authority source through the back door — the exact shape this phase exists to remove. The document is dropped from
the design entirely.

## Exact source of last-known-good rules

`FloorIdentity::last_known_rules`, read through the existing `paths::last_known_adoption_floor_rules`, stored at

```
<srr::state::resolve_state_root()>/adoption-floors/<sha256(canonical_path)>/identity.json → last_known_rules
```

— the same protected machine state root `t2` already resolves its own machine binding key from, **outside every
project**.

## Why that source is authoritative

OD-P2-08 §2 names proof-grade authority as *"authenticated machine/kernel floor + authenticated project adoption
floor + owner-signed governed transition"*. This is the first of those. It is **not** the project document, **not**
derived from T2, and **not** reachable by an ordinary actor: AR88 established that writing under
`<state_root>/adoption-floors/` is precisely the privilege the threat model denies. `write_durable` is the only
writer and it runs as the OS.

## How it is associated with the repository — it is not, and that is the point

The store is keyed by **canonical path**, so a relocated checkout has no entry of its own. Associating the old entry
with the new path would require trusting some claim — and the only available claim is the project-editable
`bound_project_identity` in the document, which is exactly what we are removing.

**The owner's own suggestion dissolves the problem.** The existing AR86-C6 union in `policy.rs` is **pattern-additive
by construction**:

```rust
if !fresh_patterns.contains(p) { reconstructed.push(r); }
```

A historical rule is added **only for a pattern the fresh derivation does not already cover**. It can therefore only
**add** patterns, never displace a class the fresh derivation produced. So a **conservative union across every entry
in this machine's store** is safe, and removes any need to decide which historical identity "owns" the new checkout.

## Why a project edit cannot weaken it

The attacker's lever is reshaping the tree so `native_layout_rules`' `has_code` check misses a directory (moving code
under an `ALWAYS_EXCLUDED_DIRS` name). That weakens the **fresh derivation** — and the union is precisely what
repairs it. The attacker cannot delete a store entry or edit its `last_known_rules`; that is the privilege AR88
established they lack.

## Why relocation cannot turn an attacker-controlled document into authority

The document is **not consulted for rules at all** on this path. Identity is freshly minted by `FloorIdentity::
advance`; rules are `native derivation ∪ protected machine state`. A planted document contributes nothing to either.

## Why a wrong or missing historical source fails closed

| Case | Result |
|---|---|
| **Missing** (fresh machine, first project) | fresh derivation only — today's behaviour, never weaker than today |
| **Wrong** (a foreign project's rules) | can only **add** patterns → restrictive, never permissive |
| **Conflicting** (foreign rule for a pattern we derive) | fresh derivation wins; our own classifications are never displaced |

Every failure direction is toward *more* obligation, never less.

## New authority mechanism added

**None.** Same protected store, same read helper, same `init::native_layout_rules`, same additive-union shape already
present in `policy.rs`. What is new is one enumeration over entries the store already holds — a read, not an
authority.

## Where the union must happen — the load-bearing detail

**At re-onboarding derivation time, not only in the reconstruction fallback.** Once re-onboarding writes a floor,
`adoption_floor.rules` is non-empty, so `PolicySet::load`'s reconstruction (which already performs the AR86-C6 union)
**never fires**. A weak derived floor would therefore be promoted to *authenticated* — strictly worse than the
reconstruction case it replaces. The union belongs in the derivation that `init`/`adopt` hand to
`write_project_adoption_floor`.

## Cost to name

On a machine with many unrelated projects, the conservative union imports their patterns into every re-onboarding.
In practice these are common layout names (`src/**`, `tests/**`, `app/**`) and a pattern is only imported when the
fresh derivation did not produce it — the AR86-C6 case. The effect is restrictive and bounded, but it must be
**disclosed** (OC-P2-04 §4): the re-onboarding report must name which patterns were restored and that they came from
protected machine state rather than from this repository's current shape.

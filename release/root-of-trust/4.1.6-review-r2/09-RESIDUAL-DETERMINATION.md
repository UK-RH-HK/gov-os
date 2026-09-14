# Residual determination

A documented residual is accepted only if one of these holds:
- **(1)** its trigger requires a capability the production trust model explicitly excludes;
- **(2)** it is unavoidable under the chosen assumptions, **and** its bound is stated correctly, **and** the verdict
  surface does not present the residual state as a stronger one, **and** no reasonable design removes it.

## 1. The architect's three named residuals

### R-1 — "a machine that never receives newer trust metadata cannot know that newer metadata exists"

- **Unavoidable core: agreed.** Under G5 (offline verification), with no clock (mode A), a verifier cannot learn what it
  was never given.
- **Stated bounds:**
  - `17` RS-1: it "cannot produce a relaxation (mode A), remove a known negative fact, lower floors below the compiled
    TPS, or certify";
  - `20` RR-2: "Floors and install authority are unaffected";
  - `19` §10: floors "at least as strong as the newest registered ones";
  - `22` §8: none "can produce … a floor below the compiled Trust Policy, or a relaxation under OP-3 mode A".
- **Tested** (P4-B5, P2):
  - *"no relaxation (mode A)"* — against A2 the gate is not a bound. Git-delivered installs are evaluated at use with no
    gate. Ingress gates are repository records that A2 writes (P2 applied an update this way).
  - *"floors unaffected" (RR-2)* — **false** whenever the binary predates the newest TPS. Floor = compiled TPS ⊔ the
    kernel chosen by the attacker (P4-B5: 5 → 4).
  - *"not below the compiled TPS"* — true. But nothing bounds the compiled TPS's age: the lever that retires old
    binaries (`min_binary_version`) is delivered through the channel A2 strips.
  - *verdict surface* — `CURRENT_KNOWN(n)` and `verified: true`, with no doctor warning on a fresh VTS.
- **Determination: not bounded as claimed, and not compatible with G11 and D-0008 rules (6), (7) and (18) as written.**
  - The unavoidable core is accepted.
  - The architecture must give stateless verifiers a bound before governed mutations: retained or pinned state from
    outside the repository, or an explicit time-bounded mode.
  - It must correct RS-1, RR-2 and `19` §10, and show `FRESHNESS_UNPROVEN`.
  - Finding **R2-H2**; correction **CD2-2**.

### R-2 — "a same-user process may alter on-disk files after one process built its snapshot; another or new process must detect it"

- **Trigger:** A3, same user, inside the account boundary. The model accepts that A3 can act as the user; what it must
  guarantee is byte binding within a process and detection afterwards.
- **Short-lived CLI processes: bounded.** The snapshot enforces verified bytes and the next process detects PPS changes.
  Accepted.
- **Not bounded for:**
  - long-lived processes: no next process, and no re-check of identity, trust state or revocation (**R2-M7**);
  - agent consumption of kernel content from disk: never checked (**R2-M8**);
  - non-PPS authorisation records and the overlay: the next process does not detect changes to them (**R2-M1**,
    **R2-M9**).
- **Determination: acceptable for short-lived CLI processes only; the general claim is not guaranteed as written.**
  Acceptable overall once CD2-5, CD2-11 and CD2-12 are applied.

### R-3 — "old pre-RoT binaries retain their historical flaws, including destructive operations before refusing a new-format project"

- **Trigger:** routine commands by operators who have not upgraded (A14). This is expected during migration and needs no
  attacker.
- **Stated bounds:**
  - LC-1: "availability impact only";
  - LC-2: "RoT-1 cannot change their behaviour through data".
- **Tested (P3, P3b):**
  - project-owned strengthening is deleted;
  - the old binary reports `verified: true` or `kernel verify` ok;
  - restricted material is served;
  - by specification, no RoT-1 remedy restores or reports the overlay;
  - layout V3 blocks every tested command of 4.1.5 and 4.1.2 **before any write**.
- **Determination: not bounded, and not inherent.** Finding **R2-H4**; correction **CD2-4**.

## 2. Every other declared residual

| ID | Determination | Condition or note |
|---|---|---|
| RS-2 (mode B trusts the clock) | accepted as an owner option | only with TA-7 stated at the decision and RT-56; not the default |
| RS-3 (A3 deletes its VTS) | accepted for A3 | the machine then becomes stateless, so R-1 applies |
| VR-1 | see R-2 | — |
| VR-2 (advisory locks ignored) | accepted | produces refusals only |
| VR-3 (non-`gov` subprocess writes) | accepted for PPS content, which is detected | **not** for gate, decision and exception records or the overlay (R2-M1, R2-M9) |
| VR-4 (profile runtimes by path) | accepted | host verification brackets every persistent write |
| RR-1 (ineligible state after automatic rollback) | accepted | fails closed; separately, the exchange drops PTR statements (R2-M9) |
| RR-2 | **not accepted as stated** | R2-H2 |
| RR-3 (A3 deletes the per-project record) | accepted for A3 | as RS-3 |
| LC-1, LC-2 | **not accepted** | R2-H4 |
| LC-3 (4.1.5 read-only commands use its cache baseline) | accepted | superseded by CD2-4 |

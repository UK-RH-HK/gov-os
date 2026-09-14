# 03 — Residuals judged against explicit criteria (AR-0021)

Each residual the architect declares within compatibility/transaction scope is judged **ACCEPTED**, **ACCEPTED WITH
CONDITION** (a named carried requirement) or **NOT ACCEPTED**, against this criterion: a residual is acceptable only if it is
(1) stated exactly, (2) fails closed or is provably inert, (3) needs a capability the trust model already treats as
out of reach (a repository writer A2, a same-account attacker A3, or an unavoidable core the owner accepted), and (4) does
not, as written, let an ordinary or legacy operation produce a state a RoT-1 binary later treats as valid, and does not
deviate from a binding owner resolution.

| Residual | Where | Determination |
|---|---|---|
| **RS-1 / RS-1b** running-machine currency on a stale anchored/media state | `24` §10; `32` §12 | **NOT ACCEPTED as stated.** RS-1b claims a C3 decision "can be stale by up to 24 hours"; executed staleness is 882 h (bounded by the 90-day anchor validity, not 24 h). OT-1 forbids C1–C3 on stale media state. **RV7-C-H1.** |
| **CUR-R1** a revocation issued within the 24 h before admission, not yet in the published state | `32` §8 | **ACCEPTED.** Bounded to the 24-hour admission window (`{win}`); a machine whose store holds the newer state refuses; conforms to OT-1's identity/freshness split for the **admission** path (M1/M2 in `cur7x` confirm FC-9 refuses stale admission). The **running-mode** extension of this window to 90 days is RV7-C-H1, not CUR-R1. |
| **RS-2 / RS-2b** a machine without a store, stored codes and a clock set back / a restored backup | `24` §10; `32` §12 | **ACCEPTED.** A machine **with** a store fails closed below the high-water (R-CLK-1, `adm7x` CLK reproduced). The pure no-store case rests on the local clock (TA-7), an unavoidable core. But see RV7-C-M1: a first admission after protected-store loss discards a surviving account-store high-water — a distinct gap, not this residual. |
| **RS-3 / VR-3 / TG-2** A3 rewrites its own account store / writes the overlay, records, PPS between units of work | `24` §10; `18` §11 | **ACCEPTED WITH CONDITION RV7-C-M1** for the store: A3 rewriting its own account store is a request; but a **legitimate** account-store high-water being discarded by a first-admission move-aside after protected-store loss is not A3 and is not covered by RS-3. |
| **AD-2′** same-account code before the first admission | `31` §9 | **ACCEPTED for the attack direction** (a planted account store is moved aside, ADM7 A07 reproduced); **NOT the whole story** — the same move-aside discards a legitimate high-water (RV7-C-M1). |
| **LR-1** legacy binaries on a pre-migration working copy | `26` §8 | **ACCEPTED.** `txn7`/`gitops7`: a pre-migration checkout, worktree or restore is `LEGACY`/`KERNEL_TAMPERED`; a RoT-1 binary is read-only on it. |
| **LR-2** occupation removed or pre-migration paths restored | `26` §8 | **ACCEPTED.** Every removal/restore/sparse/`cp`-without-dotfiles tree is `PARTIAL(occupation)` or `LEGACY` (never `COMPLETE`) under every reading (`gitops7`, `txn7`, matrix6 reproduced). |
| **LR-3** explicit operator output paths / nested legacy install | `26` §8 | **ACCEPTED.** R7V nested sub-project is reported `NESTED_LEGACY_PROJECT`; writes stay inside `vendor/` (matrix7 P-VEND). |
| **LR-4 / RR-2′** a fresh clone / a machine without a per-project record accepts the repository overlay; the local gate selects | `26` §8; `20` §10; `29` DR-25 | **ACCEPTED**, **with the caveat** that the "per-project record" whose absence triggers LR-4 has the unrealizable identity of RV7-C-M2, so a **relocated** checkout of a machine that **did** record the vector also degrades to LR-4 (loss of E10/strength detection), widening LR-4 beyond "a fresh clone". Carried as RV7-C-M2. |
| **RS-1c** a valid pin provisioned before a revocation admits the stale descendant for C1–C2 | `24` §10 | **ACCEPTED for C1–C2 within pin validity**, but the pin/confirmation path also reaches **C3** on the stale state (RV7-C-H1), which RS-1c does not state. |
| **layout durability** through clone/checkout/pull/stash/clean/sparse/archives/line-ending/case | `13`; `26` | **ACCEPTED.** `gitops7` (45 operations, real Git) and matrix6 (reproduced) show every full clone/archive/bundle/worktree/submodule/clean-on-machine is `COMPLETE`, every occupation-losing operation is `PARTIAL(occupation)`, every conversion attempt is defeated by the member or fails closed. |
| **cross-device transaction area (C-2)** | `18` §3 | **ACCEPTED WITH CONDITION** (carried, specification only): `TRUST_PLATFORM_UNSUPPORTED(cross_device_tx)` before any write; not executable before implementation (RT-123). |
| **`20` §6 uninstall "leaves the result `ABSENT`"** | `20` §6 | **ACCEPTED WITH CONDITION** (carried): the uninstall moves only `governance/trust` and the occupation, leaving `governance/overlay`/`views`, so `state_r7` computes `PARTIAL`, not `ABSENT` (R-INIT-9 refuses). Fail closed; the `20` §6 wording must be aligned with the `18` §9 `ABSENT` row, or uninstall must also move the overlay/views (`txn7` uninstall). (`04` CR7-C-6.) |
| **C-4** entry types by `st_mode`; `st_nlink == 1` at use | `18` §3, §9.1 | **ACCEPTED WITH CONDITION** (carried): a hard-linked **occupation** file stays `COMPLETE` at the layout level (`struct7`); VU-12 is the use-time guard, specification only. |
| **RS-4** a pin the repository writer controls / a CI job as a writer of the pin location | `24` §10 | **ACCEPTED** (outside TA-9); GB-6 effective-uid-0 rule reproduced in spirit (`ADM7` X7 user-writable rows). |
| **CUR-R1 / RS-2 computed sets** | `32` §8, §12; `35` §7 | **ACCEPTED as computed** (CUR7 reproduced byte-identical); the residual **bounds** are correct for admission, but the running-mode extension is RV7-C-H1. |

**Residuals outside compatibility/transaction scope** (deferred to reviewer B / synthesis): FC-R1′, FC-R5 (the
first-contact root and key theft), TB-4′, TB-S2″, TA-12″ (source, environment and toolchain compromise), A8 (root
threshold). I did not re-adjudicate these beyond confirming, at the compatibility surface, that an uncertified target is
refused (`TARGET_NOT_CERTIFIED`) and that the excluded modes are refused when offered (see `00-REPORT.md` §exclusions).

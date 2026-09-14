# G — Quality of RT-01 … RT-72

Counting scenarios is not the question. The question is whether a correct execution of the plan would detect this
review's findings. It would detect **none of the four HIGH findings**.

## 1. Coverage by trust class

| Trust class | Scenarios | Adequate? | What is missing |
|---|---|---|---|
| Authenticity and tree rules | RT-01…06, 09, 10, 23, 39 | **yes** | — |
| Integrity at use | RT-07, 07b, 51 | **yes** | — |
| Currency, eligibility and floors | RT-11, 29, 31–34, 49, 57, 70 | **no** | No scenario changes an **unfloored** constitutional value (R2-H1; P1 would pass every current scenario). RT-31 never states the binary's compiled TPS, so it passes trivially whenever the binary compiles v2. No stateless verifier with an older binary and a stripped PTR (R2-H2). RT-49 lowers *required* levels only, never *actor* levels (ROLES). RT-57 tests only a declared `lowers[]` (R2-M5). |
| Freshness and lifecycle | RT-20, 35–38, 56, 60–62 | **partial** | RT-35(d), 37(c) and 38(c) have no pass/fail criterion ("the report must record"). No equivocation (M4), no inflated reference (M2), no certification-key un-withdraw (M3), no trust-state reference inflation (M2). |
| Authorisation and gates | RT-11, 30, 33, 54, 63 | **no** | Every gate scenario assumes an authentic gate record. None tests an answered record committed by A2, written by A3 or a plugin, or answered by an agent (R2-M1; P2, P1c). |
| Byte binding | RT-16, 22, 40–43, 59, 71 | **mostly** | no long-lived process (M7); no agent or adapter consumption (M8); no hard-link variant (L2); RT-42 races only files that are already floored |
| Purpose separation | RT-04, 21, 25, 46, 47, 55, 62 | **partial** | no artifact or TCB forgery (H3); no trust-state ∩ certification grant (M6) |
| Protected writes | RT-17, 27, 45, 48, 58 | **mostly** | The [FS] rule depends on "the test-build interception layer" that the builder supplies (rule 6), so the evidence is not independent. No plugin or tool subprocess writing gate records or overlay. No `.tx/` delivered by Git. No PTR loss on exchange (M9). |
| Pre-RoT format boundary | RT-50 | **no** | Expected results are copied from the architect's F1, so the scenario is self-referential. Only 4.1.5 read commands and `kernel reinstall`. No assertion that destructive commands leave `governance/` and `spec/` unchanged. The overlay is never checked after a legacy rollback or `init --force` (H4; P3). |
| Bootstrap and TCB | RT-65, 66, 68, 69 | **partial** | no forged `artifact-final`; no binary whose compiled T0 is older than the VTS high-water (H3) |
| Availability of security updates | — | **no** | no scenario for a global no-override freeze (M2) |

## 2. Independence and self-reference

| Issue | Scenarios | Required change |
|---|---|---|
| Expected result defined by the architect's evidence | RT-50 ("as `evidence/F1`"), RT-72 ("expectations of `13` §8") | property assertions: no byte of `governance/` or `spec/` changes for any command of any pre-RoT binary; no pre-RoT binary reports `verified` after any command |
| Documented-residual variants without a pass criterion | RT-35(d), RT-37(c), RT-38(c) | bounded assertions, for example "a verifier without retained state refuses governed mutations or reports `FRESHNESS_UNPROVEN`" (after CD2-2) |
| Builder-supplied instrumentation | every [FS] scenario (rule 6) | the verifier observes with OS-level tracing (`strace -f -e trace=%file`, fanotify or eBPF), not with a layer compiled into the product |
| Positive-only multi-machine case | RT-26 | add the stateless-verifier attack variants RV2-A09…A12 |
| Gate authenticity assumed | RT-11, 30, 33, 54 | add forged-record variants RV2-A13, A14 |
| Harm assertion limited to floored policy | rule 3 (restricted material) | add authority and gate harm assertions for unfloored inputs (RV2-A01…A08) |

## 3. Testability

Every scenario of `12` and every held-out attack of `08` can be run black-box through `gov --json`. Two exceptions:
- [FS] as written;
- RT-68, which is a build-pipeline check.

The reference model in `evidence/P4` shows that the trust-state rules can also be tested below the CLI with synthetic
signed statements from the test profile. The plan should require that.

## 4. Additional negative tests

`08-HELDOUT-ATTACK-REGISTER.md` lists 36 held-out architecture attacks with expected secure outcomes. The revised plan
must add scenarios for each, with the independence rules of §2.

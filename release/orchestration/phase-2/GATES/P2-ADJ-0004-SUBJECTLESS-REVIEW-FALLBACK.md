# P2-ADJ-0004 — Orchestrator adjudication: the subjectless-review fallback is retired, and two test constructions change with it

| Field | Value |
|---|---|
| Record | Orchestrator adjudication (**not** an owner decision; the owner may override) |
| Date | 2026-09-21 |
| Raised by | P2-AR-0070, which correctly declined to act without authorisation, after P2-AR-0068 (independent adversarial review) rated the underlying defect HIGH as finding AR68-F2 |
| Classes touched | BC-P2-41 (review bound to the installation it authorises) |

## The question

Under **OD-P2-05** (bind the bytes, not the meaning) and **OD-P2-03 requirement 3**, a review must be bound to the exact
installation it authorises. The implementation kept a **single-use fallback**: a review naming no subject may still
authorise one installation. The adversarial reviewer showed the practical consequence — a subjectless review evidences an
installation no reviewer ever saw, and, because the report schema never described the review block and no command computed
the binding, *the weak path was the default for every review the governed route produced*.

P2-AR-0070 closed the schema and computation halves, so the strong form is now the default and is always reported. It did
**not** retire the fallback, because doing so breaks two currently-passing tests it had no authorisation to touch:

- `tests/certification/r2_wsa.rs::an_unbound_review_is_still_held_to_a_single_installation` — a test written in this same
  iteration specifically to assert the fallback's single-use behaviour.
- `tests/certification/ws07.rs::a_governed_security_review_by_another_role_lets_the_installation_proceed` — the flagship
  test OD-P2-03 itself cites as proof that round-3 behaviour is restored, whose control descriptor installs on a
  subjectless review.

Declining to force that was the right call: a repair worker must not quietly change what a test proves.

## Ruling

**Retire the fallback.** A review that does not name the installation subject authorises nothing.

- *Source:* OD-P2-05 clause 4 — the governed review carries the judgement the OS cannot make, and the OS binds identity and
  integrity; a review that names no subject binds nothing, so it cannot carry anything. OD-P2-03 requirement 3 — what
  cannot be evaluated gates. Contract v3:431 — a security review cannot be self-attested; a review that could authorise
  any first installation is self-attestation by the installer's choice rather than the reviewer's.
- This is **not** an owner decision: it implements decisions already in force rather than trading anything the sources
  leave open. The owner chose byte binding minutes ago precisely because the weak default was indefensible.

## The two tests, and why changing them is not weakening

1. **`r2_wsa::an_unbound_review_is_still_held_to_a_single_installation`.** Its assertion changes, because the behaviour it
   asserts is the defect. It must now assert that an unbound review is **refused outright**, and keep its name or gain a
   name that says so. This makes the test *stricter*, not weaker. The change and this reasoning are recorded here so no
   later reader mistakes it for a repair convenience.
2. **`ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed`.** Only its **construction** changes:
   the review it writes must now name the installation subject. The property it proves — an independent governed review
   lets a conforming installation proceed **ungated** — is preserved exactly, and that property is what OD-P2-03
   requirement 6 needs. If that test cannot be made to pass with a bound review, the repair is wrong and the run must stop
   and say so rather than relax the test.

No other test may be edited. Any test that turns out to depend on a subjectless review authorising something is a finding
to report, not a file to adjust.

## Residual risk recorded for the verifier

Retiring the fallback removes the attack the reviewer demonstrated. What remains is the ordinary risk the architecture
accepts: a bound review attests content the OS cannot interpret, and the pin guarantees only that what runs is what was
reviewed. That is OD-P2-05's stated division of labour, not a gap.

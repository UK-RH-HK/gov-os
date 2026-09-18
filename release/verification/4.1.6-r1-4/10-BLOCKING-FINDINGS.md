# AR-0033 — blocking findings on `srr1-r1-candidate-4`

## None.

**This file is intentionally and explicitly empty of findings.** Verdict: `ROT_PHASE1_CANDIDATE_ACCEPTED_R1`.
`GATE-R1-CANDIDATE-ACCEPT` is satisfied.

* Blocking findings: **0**
* Materially new blocker classes: **0** — the owner escalation rule of `OWNER-DECISION-0008` is **not** triggered
* `REQUIRES_R0_OR_OWNER_ADJUDICATION`: **none**
* `NEW_OWNER_DECISION_REQUIRED`: **none**
* `R0_OWNER_READJUDICATION_REQUIRED`: **not triggered**

---

## What I found that did not block, and why

I am recording the near misses here rather than only in `20-LATER-LIFECYCLE-CONDITIONS.md`, because a verifier who
says "nothing" should show what they weighed. Full reasoning is in `00-VERIFICATION-REPORT.md` §12.

**1. The signatures miss 9 of 9 plausible future primitives (`AR33-N1`).** Including, notably, the repair's own
worked example of the latent bullet-6 primitive. Not blocking because: the normative source
(`OWNER-DECISION-0006` §6) forbids the product from *permitting* an effect, not from having an incomplete static
detector; no §6-forbidden effect is reachable below floor at this commit, which I established behaviourally per
bullet and by an independent re-derivation of the census showing 0 violations; and every gap falls inside a limit
the candidate states in `evidence/DERIVATION.md` §4 and ranks in §5, where it explicitly makes no universal
claim. A finding cannot falsify a claim that was never made.

**2. An acceptance marker accepts an unenforced implementation (`AR33-N2`).** Demonstrated by construction, and
demonstrated live in the product at the base commit (`cit::apply_op` was accepted purely by the `save_record(`
marker while its `write_file` branch wrote a governed record path by hand). Not blocking because the one instance
is closed at this commit, no other bullet-2 writer has that shape, and the weakness is disclosed as limit 6 and
defeat condition 3 with an accurate statement that no cheap fix was found. This is nevertheless the mechanism's
weakest joint and the condition I would prioritise.

**3. A stdout path bypasses the command-result envelope (`AR33-N3`, `AR33-N4`).** `gov capabilities serve-embed`
prints and calls `std::process::exit(0)` from inside `run()`, so the presentation is never attached. Two claims
are false as written — that `run()`'s value reaches stdout *only* through one envelope, and that "the derivation
finds" the two non-result print sites (it does not; both live in `cli/src/main.rs::run`, which matches no
bullet-7 signature marker). Not blocking because the bypassing path reports a **provider protocol version, not
the installed release**, and makes no currency claim, so §6 bullet 7's MUST NOT is not breached; and because the
substance — both print sites, and precisely this reason — is disclosed in `DERIVATION.md` §4 limit 10. What is
wrong is a sub-clause about the mechanism's reach, not the safety argument. This is materially unlike `AR31-B1`,
where the forbidden presentation genuinely occurred on four surfaces.

**4. The tree is not rustfmt-canonical, so limit 5's stated mitigation is absent (`AR33-N5`).**
`cargo fmt --check` fails with 57 hunks across 8 files. Not blocking because I measured the consequence: my
brace-counting splitter and the candidate's indentation splitter disagree on exactly one function body in the
whole tree (`runtime/src/util.rs::glob_to_regex`) and **no §6 verdict changes**.

---

## Why none of this is a materially new class

The only candidate for a fourth class is *"the coverage mechanism's own coverage is unmeasured"*. I judge it a
**residual of `BC-R1-2` (guard coverage)**, not a new class:

* it is the same failure mechanism — an effect reaching no enforcement point — observed one level up, at the
  detector rather than at the guard. Viewing a known class at meta-level does not create a new one;
* it yields no reachable counterexample at this commit: 0 violations independently derived, and every bullet's
  sink refuses when driven;
* it is disclosed, bounded and correctly ranked by the candidate itself, which declines the universal claim that
  would have to exist for this to falsify anything;
* unlike the three prior classes, it needs no rethinking of the control's shape and no owner decision. "No
  syntactic mechanism is a decision procedure" is not something an owner can decide differently.

I have deliberately not shaded this either way. If the product owner reads `AR33-N1`+`AR33-N2` together as
evidence that derivation-from-source has reached the limit of what it can assure, that is a legitimate reading and
a reason to invest in `AR33-N2` — but it is a strengthening decision, not a defect in this candidate.

# P2-AR-0052 — owner decisions required

# none

No item in this verification needs a choice the accepted sources do not already make. Every blocking finding is a
capability the contract, the governing documents or an owner decision in force already requires, so each is an
ordinary repair requirement; they are stated as requirements in `repair-delta.md`.

A capability the contract already requires is not an owner decision. I applied that rule in both directions:
I did not manufacture an owner gate to soften a rejection, and I did not suppress one to let the phase move.

---

## The one candidate I was asked to adjudicate

**`A1-W8-01` — cross-language and cross-repository relationships (W8.5), raised by P2-AR-0051 with
`owner_decision_required: true`.** *Adjudicated: **not an owner decision at this gate.***

Contract v3:1152 conditions the bullet on **"where in scope"**. Nothing in the owner source, the three governing
documents, the active decisions and architecture (`spec/decisions/`, `spec/architecture/`, `spec/interfaces/`,
ARCH-0003), the Phase-1 owner records, the Phase-2 owner decisions (OD-P2-01, OD-P2-02, OD-P2-03) or the frozen gate
contract places a cross-language or cross-repository relationship in scope at Phase 2, and the Gate-W
advanced-qualification challenge (Contract v3:1194) names no such fault. The repository contract declares no
convention for either.

So there is no unmet Phase-2 obligation here, and therefore nothing the owner must decide **in order to close this
gate**. P2-AR-0051 recorded the bullet as not-established rather than unmet and argued W8 `CANNOT_UNDERMINE`, which
I confirm: the single-language, single-repository relationships the contract does place in scope are captured and
walkable in both directions (W8.1–W8.4, independently evidenced, and reproduced in my re-run).

Placing such a relationship in scope would be a **new product requirement**, not the resolution of an ambiguity —
which is precisely why it is not an owner decision *for this gate*. It becomes a real question when Phase 3 and
Phase 4 design the qualification repositories and decide whether Repo A or Repo B spans languages or repositories.
It is recorded in `later-lifecycle-notes.md` so the owner meets it at the point where it decides something.

## Owner-decision flags in the iteration-1 findings, adjudicated

| Finding | Flag | Adjudication |
|---|---|---|
| `A1-W8-01` (zeta, W8) | `owner_decision_required: true` | **Not an owner decision at this gate** — above. Phase-3/4 scoping question. |
| `V1-A3-01` (alpha, A3, LOW, non-blocking) | `owner_decision_required: true` — personal/customer data the project has not classified is indexed and returned by retrieval | **Not an owner decision at this gate.** A3's bullets are met: paths, datasets, tools and namespaces carry classification, secret and restricted content is excluded according to policy, and a project override cannot weaken a restricted namespace. What P2-AR-0046 raises is whether the OS should refuse to index data the *project* never classified — a default-posture question the contract does not answer and that no acceptance criterion turns on. It is an operations/adoption posture question, recorded in `later-lifecycle-notes.md`; raising it as a gate would be manufacturing an owner decision out of a non-blocking observation. |

No other iteration-1 finding carries `owner_decision_required: true`.

## What is *not* an owner decision, stated explicitly

Each of these could look like one and is not; the sources already decide them, so each is a repair requirement:

- **Whether an unreadable install command should gate** — OD-P2-03 requirement 3 already says an unevaluable
  condition gates and the installation does not proceed (BC-P2-53).
- **Whether the security review must bind to the installation** — OD-P2-03 requirement 3 names BC-P2-41 by its own
  class id and says an unbound review gates (BC-P2-41).
- **Which overlay documents belong inside POLICY_PRECEDENCE** — OD-P2-03 requirement 2 names the envelope sources,
  and Contract v3:134/:137 state the property (BC-P2-45).
- **Whether the owner's "gate only elevated installs" decision was right** — OD-P2-03 is in force and I did not
  re-open it. Every finding here is against its *implementation*, which the decision's own closing paragraph
  anticipates: *"A verifier may still find the implementation of this decision insufficient against a Contract v3
  requirement; that is a finding against the implementation, not a re-opening of the decision."*
- **Whether adoption may stall on a secret-bearing tree** — Contract v3:929 requires A6 to be executable and the
  availability rule (L4, O5:807) forbids a block that refuses its own remedy (BC-P2-33).
- **Whether the four failure classes are required** — Contract v3:276–283 lists all seven (BC-P2-32).
- **Whether a tier must run its declared membership** — frozen gate contract AC-5 (BC-P2-07).

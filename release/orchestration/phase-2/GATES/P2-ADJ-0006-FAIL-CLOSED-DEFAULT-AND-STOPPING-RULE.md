# P2-ADJ-0006 — Orchestrator adjudication: the classifier's default must fail closed, and one structural repair round only

| Field | Value |
|---|---|
| Record | Orchestrator adjudication (**not** an owner decision; the owner may override) |
| Date | 2026-09-22 |
| Raised by | P2-AR-0073, the second independent adversarial pre-mint review: 3 HIGH, 1 MEDIUM, 2 LOW, after P2-AR-0068's six were all closed |

## 1. Inverting the classifier's default implements OD-P2-05; it is not a new decision

AR73-F1 is not a gap in an enumeration. `unreadable_command_shape`'s last statement is `None` — **the default for an
unrecognised program is "readable"** — so it fails closed only for what policy happens to name. Fourteen shapes therefore
install ungated and write outside the project root.

**OD-P2-05 clause 3 already forbids this, in its own words:**

> Classification is conservative and fails closed. A command is admitted to the ungated path only when the OS can
> confidently classify every argument … Anything it cannot classify with confidence is `undetermined` and gates. **A missed
> classification must fail towards the gate, never away from it.**

The implementation inverted that default. Repairing it is therefore **implementing the owner's decision as written**, not
trading anything the sources leave open, so it needs no fresh owner decision. The owner's earlier choice between "bind the
bytes" and "deny by default" was about whether projects must *enumerate their installs*; this is narrower — an
unrecognised **program** yields `undetermined`, and the conforming path the reviewer's own NC1 exercises is unaffected.

The same clause disposes of AR73-F4: a guard that skips re-verification when a field is absent, `null` or a number fails
away from the gate. And clause 1 disposes of AR73-F2: a pin that hashes `a/b.sh` while the shell executes `a\b.sh` does
not bind what will run.

## 2. AR73-F3 is the same class as AR68-F3 and is repaired, not re-adjudicated

The overlap procedure is sound for the vocabulary it models. The defect is that `decide`'s real matcher has a **second
rule** — any `/`-free pattern also matches as `**/<pattern>` — which the procedure never models, so it misses exactly the
shortest patterns. That this widens indexing, retrieval and export is the consumer breadth P2-AR-0069 itself recorded as
unaudited. It is a residual of the same class, with a concrete fix.

## 3. The loop's own method was part of the failure — and it changes now

The reviewer's most valuable sentence is about **us**, not the product:

> In both iterations the new tests encode the last reviewer's attack list, so each round closes the previous round's
> reproductions and leaves the class open.

That is accurate, and it is the orchestrator's fault: each repair packet carried the previous reviewer's shapes as its
acceptance evidence, so the tests that resulted proved the last attack was dead rather than that the **property** holds.
Recurrence was therefore structural, not bad luck.

From now on, on this surface:

- The acceptance evidence for a classification repair is a **property test over the default**: an *arbitrary, unnamed*
  program, wrapper, flag form and interpreter must yield `undetermined` and gate — asserted generatively, not by
  enumerating the reviewer's list.
- The reviewer's shapes remain as **regression** guards only, never as the definition of done.
- A repair that adds a name to a list, without changing the default, is not a repair of this class.

## 4. Stopping rule for this surface

This is the **third** consecutive iteration in which the command derivation has been defeated. One structural repair round
follows this adjudication, and exactly one:

- If the next independent adversarial review still breaks the command classifier **after the default is inverted**, the
  orchestrator stops, produces a decision package and escalates to the owner rather than iterating again. Repeating a
  method that has failed three times, having been told why, would be indefensible.
- AR73-F5 and AR73-F6 are LOW and latent with no proven effect; they travel to the formal verifier as disclosed residual
  risk rather than blocking the candidate.
- If the round lands and the review is sound, the candidate is minted and the formal independent verification proceeds
  with every one of these findings, and this adjudication, in its inputs.

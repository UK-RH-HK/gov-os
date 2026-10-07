---
name: discovery
version: "1.0.0"
description: Method for discovery, research, experiments and decision packages during specification work.
---
# Discovery

This skill describes how to conduct discovery and research as part of the specification lifecycle. It follows the Contract and the decision register; it does not grant permissions or set rules on its own authority.

## Order of specification work

Per DEC-103 (CAP-30.f), specification work proceeds in this order:

1. Discovery and research: identify unknowns, gather evidence, run experiments (DEC-103).
2. Scenarios: write scenario descriptions that cover the feature's expected behaviour (DEC-103).
3. Representative data: assemble data samples that exercise each scenario (DEC-103, CAP-30.f).
4. UX for a feature with a user interface: the owner reviews scenarios and UX designs, not test code (DEC-103).
5. Acceptance tests: derive testable assertions from the scenarios and data (DEC-103).
6. Implementation: build the feature to pass its acceptance tests (DEC-103, CAP-30.f).

The owner is asked to review scenarios and UX designs; test code is reviewed by the independent test designer (DEC-103).

## Experiments

Per DEC-102 (CAP-32.c), experiments — spikes, tool-compatibility trials and performance trials — are a normal step that runs at any point during discovery.

Each experiment follows this method:

1. Run in a sandbox outside production paths (DEC-102, CAP-32.c).
2. Leave an evidence record describing what was tested, how it was tested, the results and the verdict (DEC-102).
3. Code from an experiment is promoted through the normal cycle, not copied directly into production paths (DEC-102, CAP-32.c).
4. Results that change a closed specification are proposed through CIT-P; the change skill handles that workflow (DEC-102, CAP-32.c).

Use `gov retrieve` to pull the retrieval bundle — context and prior evidence — before starting a new experiment.

## Decision packages

Per DEC-093 (CAP-34.c, MR-6), discovery produces decision packages for the owner.

### Routing

A decision package is routed to the owner when discovery identifies a question that the retrieval bundle and existing specifications do not answer (DEC-093, CAP-34.c). The package carries the question, the evidence gathered so far and a recommended answer.

### Batching

Decision packages are ranked P1 (blocking), P2 (important) or P3 (nice-to-have) (DEC-093). At most five packages are open at a time; a P1 package may bypass that cap when it blocks progress (DEC-093, CAP-34.c).

### State

Each package moves through these states: draft → submitted → decided → recorded (DEC-093, CAP-34.c). A decided package is recorded in the decision register. An undecided package stays open until the owner responds or the cap forces deferral (DEC-093).

## Retrieval bundle

Before formulating a decision package, the practitioner gathers context through `gov retrieve` (CAP-34.c). The retrieval bundle surfaces related specifications, decisions and evidence so that packages present questions the existing record does not already answer.

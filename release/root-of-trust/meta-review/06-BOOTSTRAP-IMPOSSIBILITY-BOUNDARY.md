# Bootstrap impossibility boundary

## Hard boundary

An unauthenticated machine cannot derive an authentic new trust root solely from files delivered through an attacker-controlled channel. Matching files, hashes, manifests, locks and signatures whose verification key arrives in the same untrusted bundle prove self-consistency, not authenticity.

At least one trust input must pre-exist or arrive through an independently trusted act, for example:

- a root public key/fingerprint embedded in a previously trusted installer or binary;
- an operating-system/package-signing trust path the owner explicitly accepts;
- a hardware/firmware root;
- an administrator-installed root file from trusted media;
- an operator who verifies a fingerprint through an independent channel.

The architecture must name this assumption. It must not claim to eliminate it.

## Other impossible or conditional guarantees

### Offline currentness

Offline verification can prove that an envelope was validly signed and unexpired according to available time. It cannot prove that no newer revocation or security minimum exists if the machine has not received current metadata. Honest states are:

- authentic and current within a defined signed-expiry/refresh policy;
- authentic but freshness unknown/stale;
- unauthenticated.

“Offline and definitely current indefinitely” is unsatisfiable.

### Organizational independence

Two signatures or key IDs do not prove two independent people, teams, infrastructures or reasoning processes. Independence requires operational evidence and audit. Cryptography can enforce threshold use, not organizational reality.

### Compiler correctness

Reproducible builds prove the same inputs/process produced the same bytes. They do not prove the compiler is benign. Diverse double compilation or independently bootstrapped chains reduce trusting-trust risk but still depend on bootstrap, source, hardware and process assumptions. “Prove no toolchain compromise” is not an absolute Phase-1 guarantee.

### Availability under strict freshness

A 24-hour freshness rule plus no witness/online path deliberately sacrifices privileged availability. An offline or partitioned machine must degrade. A design cannot simultaneously promise strict currentness, no fresh channel and uninterrupted privileged operation.

### Local compromise

If the same attacker controls the privileged installer, trust store, runtime memory and execution environment, ordinary application-level signatures cannot guarantee correct execution. The support envelope must state OS/admin/hardware assumptions.

## Acceptable Phase-1 statement

The release authenticity guarantee should be conditional and testable:

> Given an authentic installed Governance OS root key set and uncompromised local verification/installation boundary, the system accepts only release metadata authorized under that root, verifies payload bytes before staging, installs and executes the verified bytes, enforces version/expiry/revocation policy using the newest signed metadata it has validly acquired, and reports stale/unknown currency without claiming knowledge it does not possess.

This is strong, honest and implementable. It does not promise magic first trust, omniscient offline revocation or proof of every build participant's integrity.

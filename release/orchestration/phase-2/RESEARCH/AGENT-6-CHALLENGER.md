# Agent 6 — Cross-Domain Prior-Art Challenger

Scope per dispatch: find what the other five researchers' seed lists will miss, challenge "we must build this
ourselves," and challenge the framing itself. This report does not repeat the seed-list-shaped searches (TUF/Sigstore
release trust, OPA/Rego-style policy engines, Nix/Bazel hermetic execution, gVisor/Firecracker/seccomp isolation,
DevOps tooling) that the other five agents own. Read against `COMMON-BRIEF.md`.

**Headline finding**: the diagnosis in the brief is not just plausible, it is a named, 38-year-old, extensively
formalized problem with a known solution family, and there is also a live 2026 security-research literature applying
that exact solution family to LLM-agent systems — a search space none of the other five agents' seed lists would
surface. Where I disagree with the brief, it is only on emphasis: the three-level frame is fine for scoping, but the
2A/2B/2C subdivision of Level 2 is very likely reproducing, in the *research* org chart, the same fragmentation that
produced five failed repairs.

---

## Part A — The framing challenge

### A.1 Is "the check reasons about a representation, but the effect comes from elsewhere" the right diagnosis?

Yes, and it has a canonical name and a 1988 solution proposal: the **confused deputy problem**. Norm Hardy, "The
Confused Deputy: (or why capabilities might have been invented)," *ACM SIGOPS Operating Systems Review* 22(4),
October 1988, pp. 36–38 (https://dl.acm.org/doi/10.1145/54289.871709; primary text mirror:
http://web.cs.wpi.edu/~cs557/f14/papers/confused_deputy-hardy.pdf). Hardy's compiler holds the authority to write the
billing log; a client supplies a *filename* the compiler treats as data but which the runtime resolves against a
namespace the client also controls, so the client redirects the compiler's real authority onto the billing file
itself. That is P79-F11 and P79-F1 to the letter — `install.sh` is the compiler's billing-log write, `argv`/`PATH`/
`cwd` is the attacker-controlled filename, and the kernel is the deputy.

The formal explanation of *why* this happens, and the two properties that prevent it, come from Mark S. Miller's PhD
thesis, "Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control," Johns Hopkins
University, 2006 (http://erights.org/talks/thesis/markm-thesis.pdf), and Miller, Yee, Shapiro, "Capability Myths
Demolished," Johns Hopkins tech report SRL2003-02
(https://srl.cs.jhu.edu/pubs/SRL2003-02.pdf; commentary: https://blog.acolyer.org/2016/02/16/capability-myths-demolished/):

- **Property A — No Designation Without Authority.** A system must not let a party *name* (designate) an object it
  does not already hold authority over. Governance OS's defects invert this: `argv[0]`, `PATH`, `cwd`, and the
  `class` field in `REPOSITORY_CONTRACT.yaml` are all **designations supplied by a lower-trust party**, and the
  kernel/checker treats designation as if it implied authority.
- **Property D — No Ambient Authority.** Authority must be *exercised*, not *ambient* (implicitly available to
  anyone who asks). `PATH`, `LD_PRELOAD`, `BASH_ENV`, and friends (P79-F1's "26 of 26 loader-variable shapes") are
  textbook ambient authority: the environment, not an explicit grant, decides what code runs.

This is precisely on point, not a loose analogy. **Recommendation: adopt "confused deputy" / "ambient authority
violation" as the standing vocabulary for this defect class in owner-facing material** — it is more precise than
"the check reasons about a representation" and it comes with 38 years of established counter-architecture (§B.1)
rather than needing Governance OS to invent one.

A second, much more recent and much more precisely on-point term exists for the configuration-side defects
(P79-F8, AR77-F3): **"authority laundering,"** coined in Igor Santos-Grueiro, "Context-to-Execution Integrity for
LLM Agents," arXiv:2607.06000 (July 2026) (https://arxiv.org/abs/2607.06000): *"A value that should be evidence
gains authority to select, authorize, trigger, or parameterize a privileged side effect."* That is P79-F8 exactly —
the `class` field is meant to be descriptive evidence about a repository entry, and it silently gained the authority
to cancel `MATERIAL_CHANGE_REQUIRES_CIT`. I treat this citation and its architecture in detail in §B.2; flagging
here because it directly answers "is there a better-established name."

**Caveat on maturity**: "confused deputy" and "ambient authority" are established, decades-old, heavily cited terms.
"Authority laundering" is a single-author 2026 arXiv preprint with no confirmed peer-review venue I could establish
(§G) — treat it as a well-argued and unusually precise *framing*, not as settled literature the way Hardy 1988 is.

**Note on the brief's 2026-09-23 correction**: the brief was updated after I began this research to clarify that only
SRR-1/ARCH-0003 is accepted at Level 1; the RoT-1 hardening lineage was rejected across all seven revisions and is
frozen pending meta-architecture review, with D-0008/ARCH-0002 proposed but not active. Nothing in this report relies
on or assumes RoT-1's correctness — every concrete recommendation I make (git signed commits, extending
`cit::binding`, CUE-style merge semantics, the CXI-style action manifest) is a Level-2 mechanism (governed
state/authority provenance, execution binding, policy/config integrity), not a Level-1 runtime-authenticity claim.
Where I mention "Level 1" below it is only to name the axis, not to assert a status for it.

### A.2 Is the three-level frame (trust the OS / trust its decisions / hostile execution) the right decomposition?

As a **scoping** tool — what's in bounds for this phase — it is reasonable and I would not discard it. As an
**explanatory** tool for why five repairs have failed, it is misleading in one specific way worth stating plainly:

The three levels split by **what you are trusting** (identity, decisions, execution environment). The five failed
repairs split by **which subsystem the enumeration lived in** (programs → command shapes → list-entry premises →
class values → consumers of a class field → obligations of a field). Those are different axes. Level 2 is then
further split into 2A (state/authority provenance), 2B (execution binding), 2C (policy/config integrity) — which
re-introduces the subsystem axis *inside* Level 2, and this research exercise itself assigns one agent to "governed
configuration," one to "exact and hermetic execution," and so on — the research org chart mirrors the repair org
chart. If the actual defect is a single mechanism (confused-deputy / ambient-authority, per §A.1) that merely
*surfaces* in three subsystems, then organizing the fix search by subsystem again risks a sixth repair that closes
2A, 2B, or 2C individually and leaves the mechanism intact in whichever subsystem nobody was looking at (e.g., a
future 2D). I don't think this means the six-researcher structure was a mistake — parallel breadth is efficient for
*research* — but the **owner-facing synthesis should explicitly re-test whether one mechanism-level fix closes 2A,
2B and 2C simultaneously** before accepting three separate subsystem fixes, because that is exactly the outcome this
report's evidence (§B.2, the CXI "action manifest") suggests is achievable and is the strongest form of "several
defects, one defect" available (§A.4).

### A.3 P79-F10 — is "detection" the wrong verb?

Yes, and Governance OS's own codebase already contains the right verb applied to a *different* record type, which is
the most concrete evidence I found for this claim. `runtime/src/cit/binding.rs` (module docs, lines 1–29) describes
exactly the pattern mature systems use instead of detection:

> "A Change-Impact Transaction is T2 state... The CIT record is a plain repository file, so this module binds those
> facts... every `gov cit` operation that changes CIT state writes an `os_state` block into the record and seals it
> with the machine binding key... Consumers never trust the record's top-level fields for an authority decision:
> approve and execute recompute the digests from the record as it stands and compare them with the sealed block...
> a hand-edited manifest, impact, approval, gate reference or status is therefore refused, typed, at approve and at
> execute."

This is **authentication, not detection**: a CIT record's authority is not inferred by comparing its shape to
known-good shapes after the fact; it is a property of *how the record came to exist* — sealed digests
(`content_sha256`, `impact_sha256`, `binding_sha256`) bound to a signed Human Decision Gate answer. A hand edit to a
sealed CIT field doesn't need to be *detected*; it is structurally incapable of carrying a valid seal, so "was this
governed" is decidable by construction. **`REPOSITORY_CONTRACT.yaml`'s `class` field sits outside this mechanism** —
it is a plain project-editable YAML value with no seal, no binding to any governed event, which is precisely why
P79-F8/AR77-F3 could not be caught: nothing was ever minted, so there was nothing to check for.

This generalizes past Governance OS's own code. Every mature "was this authorized" system I found in this study
answers the question the same way — as a **provenance/authentication** question, never a **classification/anomaly**
question:

- **Git's object model.** Content is addressed by the hash of its bytes (a Merkle DAG of blob/tree/commit/tag
  objects); a commit can additionally be GPG/SSH-signed, and `git verify-commit` validates that signature
  (https://git-scm.com/docs/git-verify-commit; overview: Scott Chacon & Ben Straub, *Pro Git*, 2nd ed., Apress 2014,
  free at https://git-scm.com/book/en/v2, ch. 10 "Git Internals"). "Was this a governed change" reduces to "is this
  tree reachable from a signed commit on an approved ref" — a decidable graph-reachability question, not a
  heuristic comparison of file shapes.
- **Perkeep's claims over permanodes.** "A permanode is really just a signed random number... A claim is any signed
  JSON schema blob... referenc[ing] a permanode and say[ing] things like 'set the field foo to value bar'... The
  state of a permanode is the result of combining all attribute-modifying claims which reference it, in order"
  (https://perkeep.org/doc/schema/permanode, https://perkeep.org/doc/terms). A field value that was never set by a
  signed claim simply isn't part of the object's state, by definition — there is no "hand edit vs. governed edit"
  distinction to detect because an unsigned mutation is not a mutation at all.
- **Dhall's semantic integrity hashes.** `dhall freeze` pins an import to the hash of its normal form; "an import
  frozen in this way can never successfully return a different expression... If the URL tried to serve a new
  expression then the integrity check would fail and the interpreter would reject the configuration file"
  (https://docs.dhall-lang.org/discussions/Safety-guarantees.html,
  https://github.com/dhall-lang/dhall-haskell/pull/637). Authenticity is a hash comparison against a value fixed at
  authoring time, not a heuristic over the value's current shape.

**"Detect a hand edit" is the wrong question because it asks the system to distinguish two things after they already
have equal standing in the data model.** The right question is "did this value ever have a signed/sealed/hashed
authorization event in its causal history," which only works if the governed pathway *is* the only pathway that can
produce a valid artifact — i.e., authority is established at write-time by construction, not inferred at read-time
by comparison. P79-F10's finding ("no mechanism anywhere... blocks the obvious fix") is actually evidence *for* this
reframe: the obvious fix is blocked because detection was the wrong tool for the job, not because the right tool is
hard to build — Governance OS already built it once, for CIT records.

### A.4 Is there a formulation in which several defects are one defect?

Yes. Restated at the mechanism level (not the subsystem level):

> **Governance OS repeatedly lets a lower-trust party supply a value it calls "data" or "evidence," and then lets
> some other, unbound part of the system treat that value as if it were, or could mint, a capability.**

- P79-F11/P79-F1/AR77 family (execution): `argv`, `PATH`, `cwd`, embedded tokens, hard links are all *data* the
  classifier reasons about. The kernel's `execve` resolves them as if they *were* the bound reference to what should
  run, instead of the classifier handing the kernel an already-resolved, already-verified reference (a file
  descriptor / content hash) that cannot be redirected after the check.
- P79-F8/AR77-F3 (configuration): the `class` field is *data* in a project-editable file. Two separate consumers
  treat it as if it carries the authority to remove an obligation, without either consumer being handed anything a
  trusted issuer minted.
- P79-F10 (meta-level): there is no capability-issuing step at all for "this edit is governed," so the absence
  described in A.3 is the same defect viewed from one level up — nothing was ever minted, so nothing can be checked.

The most concrete evidence that this unification is achievable, not just rhetorically appealing, is the "action
manifest" mechanism in the CXI paper cited above (arXiv:2607.06000, §3.1–3.6), aimed at exactly this problem for
LLM-agent tool execution: a single **deterministic gate** admits a call only after **field authority** (is this
specific field's value backed by a trusted or authorized-derivation atom), **exact-effect authorization** (does the
effect the sink will actually apply match the effect a validator authorized, computed under the same trusted
snapshot/policy epoch/adapter revision), and **invocation authority** (a manifest-bound capability, consumed once,
authorizes this exact call) **all bind to the same canonical action manifest** — one object, one nonce, one digest
set, checked once, immediately before and structurally inseparable from execution. The paper states the property
Governance OS needs directly: *"CXI runs only the exact effect the validator authorized and only the exact manifest
the capability admitted"* (§3.6). That is one mechanism that would, if it held, foreclose 2A (state/authority
provenance — field authority), 2B (execution binding — exact-effect authorization bound to the actual sink call),
and 2C (policy/config integrity — invocation authority over the whole action) *simultaneously*, because they are the
same check performed once instead of three checks performed by three components that can drift out of sync (which is
literally how P79-F8/AR77-F3 happened: two consumers of the same field, one check).

I want to be careful not to oversell a single-author, unreviewed-venue preprint (§G). What I am confident asserting,
because it rests on the 1988–2006 capability literature rather than the 2026 preprint alone: **the "one defect"
formulation is Property A / Property D violation, occurring at three sites; a fix that establishes designation-bound,
non-ambient authority once, at the point where verification and use are the same event, is structurally capable of
closing all three sites with one mechanism.** The CXI paper is the most concrete worked example of that mechanism I
found, applied to the nearest available real-world analogue (LLM tool-calling agents), but its status as engineering
guidance should be weighted as "one credible independent design sketch," not as proven prior art.

---

## Part B — Prior art outside the DevOps/cloud-native search space

Format follows brief §5/§6 per candidate: what it provides, what it explicitly does not, trust assumptions,
maturity/maintenance, licence, offline/WSL2 fit, classification.

### B.1 Capability-security systems and the confused-deputy literature

| Candidate | Provides | Does NOT provide | Maturity/maintenance | Licence | Offline/WSL2 |
|---|---|---|---|---|---|
| **Hardy 1988, confused deputy** | The name and root-cause analysis for the entire defect class. Not software. | No implementation. | N/A (paper) | N/A | N/A |
| **Miller 2006 thesis + Capability Myths Demolished** | Formal properties (A, D, ...) that characterize capability-safe designs; a vocabulary for auditing whether a fix actually closes the hole or just re-enumerates it. | Not a library; the E language/Caja it discusses are not production targets for Rust. | Thesis is 2006, still the standard reference (https://en.wikipedia.org/wiki/Object-capability_model cites it as foundational). | N/A | N/A |
| **Capsicum** (FreeBSD 9+; also a Linux prototype existed) | Kernel-enforced capability mode: `cap_enter()` puts a process into a mode where it **cannot** perform any operation that names a global namespace object (no absolute `open()`, no `PATH` search, no arbitrary `connect()`) — only operations on capabilities (fds) it already holds, `openat`-relative to those fds. Watson, Anderson, Laurie, Kennaway, "Capsicum: Practical Capabilities for UNIX," USENIX Security 2010 (https://www.usenix.org/legacy/event/sec10/tech/full_papers/Watson.pdf); overview: https://en.wikipedia.org/wiki/Capsicum_(Unix). | Does not itself verify file contents (still need hashing); FreeBSD-native — mainstream Linux support is partial/prototype-only, not something Governance OS could adopt wholesale on WSL2/Linux today. | Shipped in FreeBSD since 9.0 (2012); actively part of base system. BSD-licensed. | BSD | Not directly usable on this deployment's Linux/WSL2 kernel without a port; the **pattern** (no ambient namespace access) is portable, the **implementation** is not. |
| **seL4** | A microkernel where all authority is capability-typed and the *entire* kernel is machine-checked against its spec, including — in later work — information-flow non-interference. Klein et al., "seL4: Formal Verification of an OS Kernel," SOSP 2009 (https://www.sigops.org/s/conferences/sosp/2009/papers/klein-sosp09.pdf); Murray et al., "seL4: from General Purpose to a Proof of Information Flow Enforcement," IEEE S&P 2013. | Not a userspace framework Governance OS could bolt on to an existing Linux/WSL2 process model; adopting it means adopting a different OS/hypervisor layer, which is a Level-3 (hostile execution) move the brief explicitly says not to import into Level 1–2 work. | Extremely mature for what it proves; seL4 Foundation actively maintained. | GPL v2 / BSD dual | seL4 itself: yes for the kernel; but re-platforming Governance OS onto it is out of scope per brief §3. |
| **EROS / KeyKOS** | Historical proof that capability discipline is practical at OS scale with acceptable performance via persistent single-level store; KeyKOS ran production VISA transaction processing from 1983. Shapiro, Smith, Farber, "EROS: a fast capability system," SOSP 1999 (https://flint.cs.yale.edu/cs428/doc/eros.pdf). | Neither is a maintained, deployable target today. | Historical/dormant. | N/A | N/A |
| **WASI Preview 2 / WebAssembly Component Model** | A *modern, actively maintained* embodiment of Property D: "a WebAssembly module or component starts with no access to the outside world and can only perform operations that the host explicitly grants... Each capability (filesystem access, networking, environment, clocks, randomness) is a separate import... statically inspectable in the component binary itself" (https://wasi.dev/security, https://component-model.bytecodealliance.org/). | Requires Governance OS's tool/plugin surface to actually compile to Wasm components to get the guarantee — does not retroactively secure the existing native-process command classifier without a rewrite of the execution boundary. | Active, Bytecode Alliance-governed, shipping 2024–2025 as stable (per search results). | Apache-2.0 | Works locally/offline; runs fine on Linux/WSL2 (any Wasm runtime, e.g. Wasmtime). No root required. |

**Classification**: **ADAPT THE PATTERN** for Capsicum/seL4/EROS (the architecture — "resolve once, hand down an
unforgeable reference, forbid ambient namespace lookups thereafter" — is exactly what P79-F11/F1/AR77-F4 need, but
none of these specific implementations fit this deployment without a much larger re-platforming than Phase 2 scope).
**WRAP/INTEGRATE — USEFUL LATER** for WASI/component model if Governance OS ever moves plugin/tool execution to Wasm
(a natural fit for "sandboxing and isolation," which is agent 4's territory — flagging the overlap rather than
duplicating it). **Defect mapping**: P79-F11, P79-F1, AR77-F1/F2/F4, AR68/AR73 family.

### B.2 Contemporary security literature on LLM-agent execution (a search space the seed lists would not surface)

This is the most important finding of this report per the dispatch's own framing ("finding it is worth more than
everything else in this study combined" if a canonical prior treatment exists). It is not DevOps-shaped; it is
2026 cs.CR arXiv literature specifically about agentic tool execution — the exact product category Governance OS is.

- **Igor Santos-Grueiro, "Context-to-Execution Integrity for LLM Agents," arXiv:2607.06000 (July 2026)**
  (https://arxiv.org/abs/2607.06000, full text https://arxiv.org/html/2607.06000). Names the failure mode
  **"authority laundering"** and proposes a single **deterministic gate** binding **field authority**,
  **exact-effect authorization**, and **invocation authority** to one **action manifest**, explicitly in "the
  confused-deputy and capability tradition" (its §7 cites Hardy and related capability literature by its own
  numbering). Directly addresses "verified bytes ≠ executed bytes" (§A.4 above quotes the exact sentence). **This is
  the closest thing to a canonical treatment of Governance OS's precise problem that I found.**
- **Derek Lilienthal & Sanghyun Hong (Oregon State University), "Mind the Gap: Time-of-Check to Time-of-Use
  Vulnerabilities in LLM-Enabled Agents," arXiv:2508.17155 (August 2025)** (https://arxiv.org/abs/2508.17155,
  full text https://arxiv.org/html/2508.17155v1). States the class precisely: *"TOCTOU arises when an agent
  validates external state (e.g., a file or API response) that is later modified before use, enabling practical
  attacks such as malicious configuration swaps or payload injection."* P79-F11 (`env --chdir=decoy sh install.sh`)
  **is** a "malicious configuration swap" in this paper's exact taxonomy. Introduces TOCTOU-Bench (66 tasks) and
  evaluates three mitigations — prompt rewriting, **state-integrity monitoring** (verify immediately before use, not
  earlier), and **tool-fusing** (collapse check-and-use into one atomic tool call, shrinking the window to zero) —
  reporting state-integrity monitoring alone cut the attack window ~95%. "Tool-fusing" is architecturally identical
  to what P79-F11 needs: don't hash-verify a path and separately let the kernel resolve a different path; make
  "verify" and "execute" the same atomic operation over the same already-open reference.
- **Rania Bousdid Kaddour et al. or similarly framed, "ConfusedPilot: Confused Deputy Risks in RAG-based LLMs,"
  arXiv:2408.04870 (2024)** (https://arxiv.org/abs/2408.04870). Explicitly maps Hardy's 1988 problem onto a
  2024-era production system (Copilot for Microsoft 365 / RAG), showing the confused-deputy pattern recurring in
  a totally different, also-LLM-adjacent deployment shape — corroborating evidence that this is not a Governance-OS
  idiosyncrasy but a recurring instance of the same 38-year-old class whenever an LLM-adjacent system lets low-trust
  content steer high-trust action.
- **"SoK: Trust-Authorization Mismatch in LLM Agent Interactions," arXiv:2512.06914 (Dec 2025)**, a 200+ paper
  survey proposing a Belief-Intention-Permission (B-I-P) unifying lens for LLM-agent security failures. Less
  directly applicable — its axis is *dynamic trust in a probabilistic agent* rather than *static designation vs.
  authority*, and Governance OS's execution-binding defects (P79-F11/F1) don't require any LLM/probabilistic
  component to reproduce (they're plain shell/env attacks) — but it corroborates, from an independent 200-paper
  survey, that "diverse threats... share a common root cause" is a live, well-evidenced finding in this exact
  product category, supporting §A.4's "several defects, one defect" claim from a second independent angle.

**Classification**: **ADAPT THE PATTERN.** None of these are shippable libraries; all are architecture sketches (CXI
most concretely) applicable to Governance OS's execution boundary and its authority-bearing config fields.
**Maturity/citation caveat** (brief §5, "state what evidence is thin"): all four are arXiv preprints from 2024–2026;
I could not establish peer-reviewed publication venue for any of them (§G). Weight CXI and the TOCTOU-Bench paper as
"credible, well-specified, directly on point, unconfirmed peer review" — worth the owner's attention on the merits
of the argument and the precision of the fit to the defect ids, not on venue authority. **Defect mapping**: P79-F11
(CXI + Mind-the-Gap directly), P79-F1 (CXI), P79-F8/AR77-F3 (CXI's "authority laundering" is a near-exact redescription).

### B.3 Complete mediation, TOCTOU, and ambient authority in classical OS-security literature

- Saltzer & Schroeder, "The Protection of Information in Computer Systems," *Proc. IEEE* 63(9), 1975
  (https://www.cs.virginia.edu/~evans/cs551/saltzer/). The **complete mediation** principle: *"every access to
  every object must be checked for authority"* and a system must be built on "arguments why objects should be
  accessible, rather than why they should not." P79-F11's bug is a complete-mediation violation: the OS checked
  authority for `<root>/install.sh` and then mediated a *different* access (`<root>/decoy/install.sh`) without
  re-checking. This is the oldest and most authoritative citation available for "checking a representation once is
  not the same as mediating the actual access."
- Bishop & Dilger, "Checking for Race Conditions in File Accesses," *Computing Systems* 9(2), 1996
  (https://nob.cs.ucdavis.edu/bishop/papers/1996-compsys/racecond.pdf). The formal TOCTOU (time-of-check to
  time-of-use) treatment: *"flaws due to race conditions in which the binding of a name to an object changes between
  repeated references."* Directly names the **temporal** mechanism behind P79-F11/F1 (the binding of `argv`/`install.sh`
  to a filesystem object changes, or is made to differ, between the hash-check and the `execve`). Confused deputy
  (§A.1) explains *why* this is exploitable (ambient, redirectable naming); TOCTOU explains *when* (a gap the
  attacker's own input controls, between check and use). Both are correct descriptions of the same bug from
  different angles — this is worth stating in owner-facing material so the fix is understood to need to close both:
  eliminate the ambient redirect (capability discipline) *and* eliminate the temporal gap (bind check to use, e.g.
  CXI's "same action manifest," or Bazel/Nix-style resolve-once-then-hash — but that overlaps agent 3/5's scope).
- Chen, Wagner, Dean, "Setuid Demystified," USENIX Security 2002
  (https://people.eecs.berkeley.edu/~daw/papers/setuid-usenix02.pdf). Directly on point for P79-F1's 26/26
  loader-variable result: the paper's guidance for secure privileged programs is that *the entire environment must
  be erased and only a short, explicitly safe allowlist reconstructed* before exec — not enumerated and blocklisted
  variable-by-variable, which is exactly the enumeration pattern the brief says has failed five times (`LD_PRELOAD`,
  `LD_AUDIT`, `PYTHONPATH`, `BASH_ENV`, `GIT_SSH_COMMAND`, ...). The paper's own conclusion after cataloguing Unix
  uid-setting pitfalls is structural (allowlist-and-erase), not enumerative (blocklist-and-patch).
- Linux `openat2(2)`, flags `RESOLVE_BENEATH` / `RESOLVE_NO_SYMLINKS` (https://man.archlinux.org/man/openat2.2.en).
  A modern (Linux 5.6+) kernel primitive built specifically to close TOCTOU path-resolution races that plagued
  `openat()`+manual-canonicalization approaches; notably its `RESOLVE_BENEATH` design was deliberately changed from
  FreeBSD's `O_BENEATH` "to avoid a well-known correctness bug in FreeBSD's implementation that rendered it
  effectively insecure" — i.e., even the capability-adjacent primitive has a documented history of a first attempt
  that looked right and wasn't, which is a useful data point for how hard this defect class is to get right by
  ad hoc reasoning even *with* kernel support. **Important limit**: this addresses symlink/`..`-escape races, not
  the hard-link case (AR77-F4) — a hard link is a second, fully valid directory entry for the same inode from
  outside any boundary the kernel is asked to enforce; no amount of `..`-escape prevention touches it, because
  there is nothing to canonicalize (the brief's own diagnosis is correct here and is confirmed by the mechanism of
  `openat2`'s flags, which only ever talk about symlinks and `..` components, never alternate hard-linked names).
  The structural fix for the hard-link case is identity-by-content-hash-or-inode/fd, not identity-by-path, which is
  the same conclusion content-addressing (§B.4) reaches independently.

**Classification**: **BUILD CUSTOM is not defensible for the general pattern** — Saltzer/Schroeder's complete
mediation and Chen/Wagner/Dean's allowlist-and-erase are 20–50-year-old, unambiguous, freely available design
guidance that the five repairs' enumerate-and-patch approach contradicts directly. `openat2` flags are
**USE DIRECTLY** where the specific defect is a symlink/`..` race (not AR77-F4). **Defect mapping**: P79-F11, P79-F1,
AR77-F1, AR77-F4 (negative result — cite as evidence path-boundary fixes cannot close this one), AR68/AR73 family.

### B.4 Database systems: constraint enforcement at commit, not diff-based grant tracking

The brief's own diagnosis of P79-F8 is: *"The integrity check models authority **granted**, not obligations
**lost**."* This is precisely the distinction between two different ways to validate a state transition, and
databases picked the right one decades ago:

- A system that checks **"what did this transaction grant"** is diffing the transition against an enumerated list of
  known-dangerous grants — it must enumerate every way authority could be gained, which is exactly the pattern the
  brief says has failed five times (programs → command shapes → premises → class values → consumers → obligations).
- A system that checks **"does the resulting state satisfy every constraint"** at commit doesn't care how the state
  got there; it re-validates the *whole* invariant set against the *whole* resulting state, every time. This is
  ordinary relational-database constraint enforcement (`CHECK`, `NOT NULL`, foreign keys, triggers) plus
  write-ahead logging for durability of the check having happened.

For the specific case of **evidence currency** (is a previously-recorded fact still valid against present state) —
which the R0/R1-era memory notes as "stateless currency," and which `runtime/src/verification/currency.rs`
implements as a bespoke `Currency::evaluate(project, snapshot)` recomputation — the directly relevant database
literature is **serializable snapshot isolation**: Cahill, Röhm, Fekete, "Serializable Isolation for Snapshot
Databases," SIGMOD 2008 (https://people.eecs.berkeley.edu/~kubitron/courses/cs262a-F13/handouts/papers/p729-cahill.pdf),
which is precisely about the class of bug where a decision made against a *snapshot* of state silently becomes
invalid because the real state moved before the decision was acted on — and formalizes exactly when that's safe
(no anomalies) versus when it silently corrupts invariants. PostgreSQL's production implementation of this
(the first production SSI implementation, per the search results) is a mature, freely available reference
architecture for "how do you make a currency claim about a point-in-time snapshot into something that is either
provably still valid or automatically aborted," rather than the ad hoc recomputation Governance OS currently hand-rolls.

**Grounding in the codebase**: `runtime/src/cit/binding.rs` already implements the *correct* half of this pattern
for CIT records (seal at commit, re-derive and compare rather than trust top-level fields — see §A.3). The gap is
that `REPOSITORY_CONTRACT.yaml`'s `class` field, and evidence-currency claims generally, are validated by
special-purpose Rust logic re-implementing (piecemeal) what a transactional engine's constraint system gives for
free: full-state invariant re-checking at every commit point, not incremental "what changed" diffing.

**Classification**: **ADAPT THE PATTERN**, not literal database adoption — Governance OS does not need to embed
Postgres. What it needs is the **discipline**: express Property C ("cannot weaken a floor") and the "obligations
cannot be silently lost" rule as **constraints checked against full resulting state at every commit**, not as
special-cased diffs of what a particular change *granted*. This is a genuine simplification opportunity (§F):
replacing N enumerated "does this value/consumer/field grant something bad" checks with one "does the resulting
state satisfy every current invariant" check removes an entire class of "we forgot a consumer" bugs (which is
literally what AR77-F3 was — a second consumer the integrity check didn't know about).
**Defect mapping**: P79-F8, AR77-F3, R0/R1-era currency issues, the RoT review findings on "stateless currency" per
project memory (I did not re-derive those findings myself — flagged in §G).

### B.5 Content-addressing and Merkle DAGs beyond git

- **Git's own object model** (already covered in §A.3 for the provenance argument; repeating the citation here for
  the "authority substrate" framing the dispatch specifically asked about). Chacon & Straub, *Pro Git*, ch. 10
  (https://git-scm.com/book/en/v2). Governance OS already runs inside git repositories for every deployment in its
  profile (§ deployment profile: private repositories, owner-controlled). **Using git's own signed-commit/tag
  mechanism and object graph as the authority substrate for "was this a governed change" is close to free** — the
  infrastructure is already present in every target environment, requires no new dependency, works fully offline,
  and needs no root. This is the single cheapest "use directly" opportunity in this entire report.
- **IPFS.** Benet, "IPFS - Content Addressed, Versioned, P2P File System," arXiv:1407.3561 (2014)
  (https://arxiv.org/pdf/1407.3561). Generalizes the Merkle-DAG-as-identity idea beyond git specifically. Not a
  good fit for this deployment profile directly (it's a P2P network protocol; the brief's profile is single-owner,
  offline, no cloud dependency) but useful as the canonical citation that "identity by content hash, not by path or
  name" is an established, cross-system pattern, not a git idiosyncrasy — relevant to AR77-F4 (hard links) and
  AR77-F1/F2 (path-based identity failing to catch alternate representations of the same target).
- **Perkeep** (formerly Camlistore) — already detailed in §A.3: signed claims over permanodes, i.e., a small,
  readable, directly-relevant worked example of "authority-bearing field mutation, expressed as an explicit signed
  transaction over content-addressed storage" (https://perkeep.org/doc/schema/permanode). This is the closest
  external analogue I found to what `REPOSITORY_CONTRACT.yaml`'s `class` field *should* be: not a plain YAML value
  any project-level edit can set, but a claim, signed by whatever already-governed event (a CIT approval, per
  §A.3's evidence that Governance OS has the mechanism) is supposed to authorize it.

**Classification**: **USE DIRECTLY** for git's own object model and commit signing (already present, already
trusted per the deployment profile's "trusted: the OS, the hardware, the owner" — an owner-signed commit is
squarely inside that trust boundary). **ADAPT THE PATTERN** for Perkeep's claim/permanode split as the conceptual
model for authority-bearing contract fields. IPFS: informative citation only, not a fit for this deployment.
**Defect mapping**: P79-F10 (primary), P79-F8, AR77-F3, AR77-F4.

### B.6 Configuration languages with guarantees as a *language* property, not a *checked* property

The brief flags this as possibly the highest-leverage area ("our Property C problem might be a type-system problem
rather than a verification problem") and the codebase confirms it concretely.

`runtime/src/policy_precedence.rs` (module docs, lines 1–22) hand-implements precedence/overlay merge logic in Rust:
per-key `Rule`s with a `mode`, an `order`, and hand-written reasoning about what happens when a rule set "declares no
rule at all" for a key. Its own doc comment records a **real historical bug** from exactly this hand-reasoning:

> "Reading their silence as 'deny every key' refused purely descriptive keys (`project.name`, `providers`, …), made
> doctor D027 CRITICAL and rolled back an update to shipped 4.1.5."

This is a bug class — *silence in a merge is ambiguous between "no opinion" and "deny everything"* — that a
lattice-based configuration language makes structurally unrepresentable, because "no opinion" has a canonical
algebraic identity element and merge is defined as an operator with known algebraic properties, not as prose:

- **CUE.** "All possible values are ordered in a lattice... The unification of values a and b is defined as the
  greatest lower bound of a and b... Since CUE values form a lattice, the unification of two CUE values is always
  unique" (CUE Language Specification, https://cuelang.org/docs/reference/spec/; conceptual overview,
  "The Logic of CUE," https://cuelang.org/docs/concept/the-logic-of-cue/). Unification (`⊓`, meet) is commutative,
  associative, and idempotent by construction, meaning: (a) merging two config layers can only ever *narrow*
  (make more specific / equal), never widen a constraint — Property C ("cannot weaken a floor") becomes a
  mathematical consequence of using `⊓` for every merge, not a rule a Rust function must remember to enforce
  correctly on every code path; and (b) "no rule for this key" is simply the top element (⊤, unconstrained), which
  unifies with anything to produce that other thing — exactly correct behavior for the 4.1.5 D027 bug, achieved for
  free rather than by careful prose reasoning about which rule sets "declare" a label.
  **Caveat**: I could not find an official CUE source using the literal phrase "cannot subtract information" (the
  brief's suggested phrasing) — I'm reporting the underlying mathematical property (monotonic lattice meet) which
  supports the same conclusion, sourced to the spec and design docs above, not to that exact phrase (flagged per
  brief §5's instruction to say when evidence is thin).
- **Dhall.** Non-Turing-complete, total (every program terminates, no exceptions), with LangSec as an explicit
  design goal: "Dhall's is best-in-class when it comes to language security (LangSec). The language aims to support
  safely importing and evaluating untrusted Dhall code, even code authored by malicious users"
  (https://github.com/dhall-lang/dhall-lang, https://www.haskellforall.com/2020/01/why-dhall-advertises-absence-of-turing.html).
  Plus semantic-hash import pinning (`dhall freeze`, §A.3) for supply-chain integrity of config fragments. Directly
  relevant to `REPOSITORY_CONTRACT.yaml`/overlay-template files: if these were Dhall instead of plain YAML, an
  import of a policy fragment could be pinned by semantic hash the same way P79-F11 pins `install.sh` — except
  Dhall's import resolution has no analogue of `PATH`/`cwd` redirection, because imports are total, typed
  expressions resolved by the interpreter itself, not names resolved by an OS-level namespace search.
- **Starlark.** Deliberately non-Turing-complete (no unbounded recursion; fixed-width ints), deterministic and
  hermetic by design ("user code cannot interact with the environment... execution cannot access the file system,
  network, or system clock" — https://github.com/bazelbuild/starlark/blob/master/spec.md, https://bazel.build/rules/language).
  Less directly relevant to Property C specifically (Starlark doesn't have CUE's lattice-meet guarantee), but a
  second, independently-arrived-at example of "make the dangerous behavior *inexpressible in the language*" rather
  than "check for it after the fact" — the same design philosophy the brief's §7 asks for.

**Classification**: **ADAPT THE PATTERN — this is a genuinely strong "delete custom code" opportunity per brief §7.**
Migrating `policy_precedence.rs`'s merge semantics onto a CUE-style lattice-meet (even reimplemented natively in
Rust rather than depending on the CUE toolchain, if integration cost is a concern) would remove the entire class of
bug the 4.1.5/D027 incident represents, by making "silence ≠ deny" and "merge cannot widen a floor" properties of
the merge *operator's algebra* rather than properties every call site must get right. I would flag this as one of
the two or three highest-value findings in this report. Full adoption of CUE-the-language (not just the pattern) is
**USE DIRECTLY** if Governance OS is willing to take a new toolchain dependency — the license is Apache-2.0, it's
Go-based (single static binary, works offline, no root, no cloud, runs fine under WSL2) — but that's an integration
decision for the owner given brief §6's "be conservative about BUILD CUSTOM" burden-of-proof, not a security
verdict either way. **Defect mapping**: primarily the Property-C class implied by P79-F8/AR77-F3 and directly
evidenced by the 4.1.5/D027 policy-precedence incident found in the codebase itself.

### B.7 Package managers with strong local, offline trust models

Requested explicitly in the dispatch as a possible reinvention target for "trust metadata." I want to flag directly:
this overlaps agent 1's (secure update/release trust) territory, which likely goes deep on TUF/Sigstore-style
release roots already accepted at R0/R1 per project memory. My angle here is narrower and different: these systems'
**local, offline verification chain** as a possible simplification of Governance OS's ad hoc "trust metadata" +
"policy precedence" combination, not as a replacement for the release-root work.

- **Debian/APT.** Signed `InRelease` (or detached `Release.gpg`) → lists SHA256 of every `Packages` file → each
  `Packages` entry lists the hash of the actual `.deb`. *"apt-secure is the last step in this chain; trusting an
  archive does not mean that you trust its packages not to contain malicious code, but means that you trust the
  archive maintainer"* (`apt-secure(8)`, https://manpages.debian.org/unstable/apt/apt-secure.8.en.html; mechanism
  detail: https://debian-handbook.info/browse/stable/sect.package-authentication.html). One signature, one hash
  chain, no synchronized enumerations — a useful contrast to "trust metadata," "policy precedence," and the
  "class"-field consumer problem, which are effectively three unsynchronized places authority can be asserted.
- **Fedora/RPM+DNF.** Two independent layers: `rpm --checksig` for individual package signatures, and
  `repo_gpgcheck`/signed `repomd.xml` for repository metadata — explicitly closing a gap Debian's simpler model
  doesn't have a name for: *"the metadata index that lists packages is otherwise trusted based only on TLS and
  checksums. Without a signature on the index, a compromised mirror... could serve modified metadata that hides or
  blocks security updates"* (https://docs.aws.amazon.com/linux/al2023/ug/repo-metadata-signing.html;
  https://blog.packagecloud.io/how-to-gpg-sign-and-verify-rpm-packages-and-yum-repositories/). Worth flagging to
  agent 1 even though it's their territory: this "index/metadata needs its own signature, separate from
  per-artifact signatures" pattern is exactly the kind of thing a single unified "trust metadata" blob can miss if
  it conflates "is this artifact authentic" with "is this the complete, current, unmodified *list* of artifacts."
- **Alpine/apk.** Simplest of the three: `/etc/apk/keys` holds trusted public keys by filename; each package's
  control segment is signed directly, no separate repository-metadata signature layer
  (https://wiki.alpinelinux.org/wiki/Apk_spec, https://wiki.alpinelinux.org/wiki/Include:Abuild-sign). Useful as
  the *minimal viable version* of this pattern — relevant given the deployment profile's "one owner, owner-controlled
  machine" (i.e., Governance OS doesn't need a multi-maintainer keyring or a mirror-integrity story; it needs "is
  this the owner's key, yes or no").

**Classification**: **ADAPT THE PATTERN — USEFUL LATER**, primarily as a design contrast rather than a component to
adopt (Governance OS is not distributing packages to third parties; it's securing its own contract/overlay/plugin
files for a single owner). The transferable lesson: **collapse "trust metadata" + "policy precedence" + "class-field
consumers" into one signed index with one hash chain**, the way all three of these ecosystems do, rather than three
independently-reasoned-about mechanisms whose consistency currently depends on remembering to update every
consumer (which is exactly what AR77-F3 says did not happen). **Defect mapping**: P79-F8, AR77-F3 (structural
contrast), general "trust metadata" reinvention question in §C.

---

## Part C — "We must build this ourselves": reinvention audit

Per dispatch: for each of the six named custom mechanisms, is it reinventing an existing primitive?

| Custom mechanism (as named in dispatch) | What it's reinventing | Evidence | Verdict |
|---|---|---|---|
| **Command classifier** | Ambient-authority-free execution (Capsicum's `cap_enter()`, seL4/EROS capability handles) and allowlist-and-erase environment handling (Chen/Wagner/Dean 2002) — both of which treat "what will execute" as something you *construct* from an already-bound reference, not something you *classify* from a string and hope stays bound. | §B.1, §B.3. AR68/AR73's ~40 command shapes and P79-F1's 26/26 loader variables are direct evidence the classify-and-enumerate strategy cannot converge: every fix adds coverage for shapes found so far, and the underlying mechanism (ambient environment resolution happening after classification) is untouched. | **Reinventing, and losing.** The blocklist-of-shapes approach is precisely what Setuid Demystified's authors concluded doesn't work at OS-privilege scale either. |
| **Trust metadata** | Signed-index + hash-chain package-manager trust models (Debian/RPM/Alpine, §B.7) and, more directly in scope, TUF-style release roots (agent 1's territory — noted, not duplicated). | §B.7. | **Likely reinventing**, but I defer the primary verdict to agent 1 since this is squarely their seed area; my only addition is the RPM lesson that metadata-list integrity and per-artifact integrity are two different guarantees that can silently diverge if not designed as one signed structure. |
| **Policy precedence and overlay logic** | CUE's lattice-meet unification (§B.6) — monotonic narrowing and unambiguous "no rule" handling as algebraic properties. | §B.6, with a **live, named, in-repository bug** (the 4.1.5/D027 rollback, documented in `policy_precedence.rs`'s own comments) caused by exactly the kind of hand-reasoning a lattice-meet operator makes unnecessary. | **Reinventing, and it already produced a real incident** doing so. This is my strongest single reinvention finding — I have direct code evidence, not just an analogy. |
| **Authority-exemption predicate** | Object-capability discipline (Property A, §A.1): an exemption should be an unforgeable capability minted by a trusted issuer, not a predicate computed over a project-editable field's content. | §A.1, §A.4. P79-F8's `class: test` is a plain string in a file the project can edit; nothing mints it, nothing seals it. | **Reinventing, badly** — it inverts Property A (designation used as if it were authority) rather than implementing any known capability pattern. |
| **Review-to-installation binding** | Git's own signed-commit/tag provenance (§B.5) is available for free in every deployment target per the profile (already-git, already-offline, already owner-trusted); Perkeep's signed-claim-over-permanode model (§B.5) if a field-level (not whole-file) granularity is needed. | §B.5. Notably, `cit/binding.rs` shows Governance OS *has already built* essentially this pattern (sealed digests bound to a signed gate decision) for CIT records — so this is also **internal** reinvention, not just external: the "review-to-installation binding" problem for `REPOSITORY_CONTRACT.yaml` is arguably already solved elsewhere in the same codebase and not yet applied here. | **Partially reinventing an external primitive (git) and partially failing to reuse an internal primitive (`cit::binding`) that already does the right thing for a sibling record type.** |
| **Evidence currency mechanisms** | Serializable snapshot isolation / commit-time constraint re-validation (§B.4) — the database literature's answer to "does a decision made against a snapshot remain valid." | §B.4, grounded in `verification/currency.rs`'s bespoke `Currency::evaluate(project, snapshot)`. | **Reinventing** a narrower, hand-rolled version of a well-studied database concurrency-control problem, without the formal guarantees (serializability / anomaly-freedom proofs) the database literature provides. |

**Overall pattern across all six**: every one of them is, at root, an attempt to answer "is this value trustworthy"
by *inspecting the value itself or its immediate context* (classify the command string; check the metadata blob;
evaluate the precedence rule; evaluate the exemption predicate; check the binding record's fields; recompute
currency from a snapshot) rather than by asking "does this value carry an unforgeable proof that a trusted issuer
authorized it, checked at the moment of use." That is the single sentence I would put in front of the owner if only
one sentence were allowed.

---

## Part D — Defect-id cross-map

| Defect id | Root-cause literature | Concrete prior-art fix pattern | My classification |
|---|---|---|---|
| P79-F11 | Hardy 1988 (confused deputy); Bishop & Dilger 1996 (TOCTOU); Saltzer & Schroeder 1975 (complete mediation); CXI arXiv:2607.06000; Mind-the-Gap arXiv:2508.17155 | Bind verification and execution to the same already-resolved reference ("tool-fusing" / "action manifest"); Capsicum-style no-ambient-namespace execution | ADAPT THE PATTERN |
| P79-F1 | Same as above + Chen/Wagner/Dean 2002 (Setuid Demystified) | Allowlist-and-erase environment, not enumerate-and-blocklist | ADAPT THE PATTERN |
| AR77-F1 | Saltzer & Schroeder (complete mediation over the *actual* resolved endpoint, not the string) | Same as P79-F11 | ADAPT THE PATTERN |
| AR77-F2 | Same | Same | ADAPT THE PATTERN |
| AR77-F4 (hard link) | Content-addressing literature (§B.5); `openat2` flags explicitly do **not** cover this case | Identity by content hash / fd / inode, not by path-string | ADAPT THE PATTERN (path-boundary tooling alone: negative result) |
| AR68/AR73 family | Setuid Demystified; confused deputy | Same structural fix as P79-F1/F11 — this family is evidence the enumeration approach cannot converge, not a separate defect | ADAPT THE PATTERN |
| P79-F8 | Miller 2006 (Property A); CXI's "authority laundering" | Capability-minted exemptions (only a trusted issuer can grant); DB-style commit-time full-invariant check (§B.4) instead of grant-diffing | ADAPT THE PATTERN + BUILD CUSTOM is defensible only for the Governance-OS-specific invariant *content*, not the *mechanism* |
| AR77-F3 | Same as P79-F8 | Same + "one signed index, not N consumers" (§B.7) | Same |
| P79-F10 | Git object model; Perkeep; Dhall semantic hashes (§B.5, §A.3) | Authenticate provenance structurally (signed transitions over content-addressed state), don't detect anomalies after the fact; Governance OS's own `cit/binding.rs` is a working internal example | USE DIRECTLY (git) + ADAPT THE PATTERN (Perkeep-style claims) |
| R0/R1-era (unauthenticated source, currency claims) | Serializable snapshot isolation (§B.4); TUF (agent 1's territory, not duplicated) | Commit-time full-state re-validation instead of point-in-time snapshot trust | ADAPT THE PATTERN |

---

## Part E — REQUIRED NOW / USEFUL LATER / HIGH-ASSURANCE ONLY

**REQUIRED NOW** (private/local integrity, fits the single-owner offline WSL2 profile with no new heavyweight
dependency):
- Adopt "confused deputy" / Property A / Property D vocabulary and audit method for every future fix proposal
  (§A.1, §A.4) — costs nothing, prevents re-enumerating.
- Apply the `cit::binding` sealing pattern (already in the codebase) to `REPOSITORY_CONTRACT.yaml`'s authority-bearing
  fields, closing P79-F8/AR77-F3/P79-F10 together (§A.3, §B.5, §C).
- Use git's own signed-commit/tag mechanism as (at least one input to) the review-to-installation binding, since the
  infrastructure is already present, offline, and inside the stated trust boundary (§B.5).
- Re-derive `policy_precedence.rs`'s merge semantics as a lattice-meet operator (CUE-pattern, need not take the CUE
  dependency) so Property C is an algebraic invariant of the merge function, not a property every call site must
  get right by hand (§B.6) — directly motivated by a real incident already in the codebase's own history.

**USEFUL LATER** (R2 release, larger integration cost or dependency not yet justified):
- Full CUE or Dhall adoption for overlay-template/config files, if the team is willing to take a new toolchain
  dependency (§B.6).
- WASI Preview 2 / component-model capabilities for plugin/tool execution, if that execution surface moves to Wasm
  (overlaps agent 4's sandboxing scope — flag, don't duplicate) (§B.1).
- Formal commit-time constraint re-validation modeled on serializable snapshot isolation for evidence currency more
  broadly, beyond the immediate P79-F8 fix (§B.4).

**HIGH-ASSURANCE ONLY** (R3/hostile/enterprise — explicitly out of Phase 1–2 scope per brief §3):
- seL4/EROS-style re-platforming of the execution kernel.
- Capsicum-style kernel-level capability mode (FreeBSD-native; a genuine Linux port would itself be an R3-scale
  undertaking, not a Phase 2 fix).
- IPFS-style distributed content addressing (the deployment profile is explicitly single-owner/offline; IPFS's
  P2P trust model solves a problem Governance OS doesn't have).

---

## Part F — Simplification opportunities (trusted computing base reduction)

Per brief §7 ("actively look for places where an established primitive lets Governance OS delete custom code"):

1. **One authority substrate, not two.** Git's object model + signed commits already gives Governance OS an
   authenticated, content-addressed history for everything living in the repository. `cit/binding.rs`'s
   sealed-digest mechanism is a second, independently-built authority substrate for CIT records specifically. If
   `REPOSITORY_CONTRACT.yaml` and overlay-template authority-bearing fields moved onto the *same* substrate as CIT
   records (rather than remaining plain project-editable YAML), Governance OS would have **one** provenance
   mechanism instead of two, and P79-F8/AR77-F3/P79-F10 close as one fix rather than three.
2. **One merge operator, not N hand-reasoned precedence rules.** §B.6/§C: replacing `policy_precedence.rs`'s
   per-key `Rule`/`mode`/`order` reasoning with a lattice-meet operator removes the entire "does silence mean deny
   or no-opinion" class of bug (the 4.1.5/D027 incident) as a matter of algebra, and would very likely shrink that
   ~805-line module substantially, since much of it is bookkeeping to manually reconstruct a property (monotonic
   narrowing) a meet operator has automatically.
3. **One check, not three, for execution.** If a CXI-style "action manifest" binding field authority + exact-effect
   authorization + invocation authority is adopted for the execution boundary (§A.4), 2A/2B/2C's execution-adjacent
   checks (command classifier, trust metadata for what's executable, review-to-installation binding for what was
   approved to run) become one gate evaluated once, immediately before and atomically with execution, rather than
   three independently-maintained enumerations that must be kept in sync by hand (which is exactly how AR77-F3, a
   second unknown consumer, happened).
4. **Fewer enumerations overall.** Every "BUILD CUSTOM, badly" finding in §C shares one symptom: an enumerated list
   (of command shapes, of loader variables, of class-field consumers, of precedence rules) that must be manually
   kept complete. Every prior-art fix pattern in Part B replaces an enumeration with either an algebraic guarantee
   (CUE meet, Dhall totality) or a structural guarantee (capability discipline, content addressing) that doesn't
   need to be "complete" because the excluded case is inexpressible rather than unlisted.

---

## Part G — What I could not determine

- **Peer-review status of the four 2024–2026 LLM-agent security papers** (CXI arXiv:2607.06000, Mind-the-Gap
  arXiv:2508.17155, ConfusedPilot arXiv:2408.04870, SoK arXiv:2512.06914). I found arXiv listings and abstract-page
  metadata for each; I could not confirm any of them at a named peer-reviewed venue (conference/journal) via the
  searches available to me. Treat their specific mechanisms (especially CXI's "action manifest," which is the paper
  doing the most work in this report) as well-argued, precisely-fitting engineering proposals from credible but
  unconfirmed-review sources, not as established literature on the level of Hardy 1988 or Saltzer & Schroeder 1975.
- **Whether "cannot subtract information" is CUE's own phrasing** (brief's suggested wording) — I could not find
  this exact phrase in official CUE documentation. I'm confident in the underlying claim (lattice-meet is
  monotonic/narrowing by construction) from the CUE language spec directly, but flagging the phrase mismatch per
  the brief's own instruction to be precise about sourcing.
- **Current mainline-Linux support status for Capsicum.** Sources describe it as FreeBSD-native with historical
  Linux prototype work; I could not establish whether any Linux capability-mode equivalent is production-ready
  enough to recommend for this WSL2 deployment today. I'm treating Capsicum as pattern-only evidence for this
  deployment, not as an installable component, and I'd flag this as something worth a narrower follow-up if the
  owner wants to pursue kernel-level capability mode specifically.
- **Whether Governance OS's `cit/binding.rs` mechanism, if extended to `REPOSITORY_CONTRACT.yaml`, would itself
  need a Human Decision Gate wired to every contract edit, and what the UX/workflow cost of that is** — this is an
  implementation question outside read-only research scope, but the owner should know the "USE DIRECTLY" verdict in
  §E for this item is about the *mechanism's applicability*, not a claim that applying it is free.
- I did not independently re-derive the RoT-1 review findings referenced in project memory ("stateless currency,"
  "floor coverage," CD-1..CD-13, CD2-1..CD2-14) — I cite them only as corroborating context for §B.4's currency
  argument, sourced to the orchestrator's own memory record, not to a document I read myself in this session.
- I did not deeply investigate Fedora/RPM or Alpine/apk beyond their signing model (no deep dive into their
  dependency-resolution or conffile-precedence handling), since that risked duplicating agent 1's scope without
  adding new insight; flagged in §B.7 as intentionally narrow.

---

## Sources

**Capability security / confused deputy**
- Hardy, N. "The Confused Deputy (or why capabilities might have been invented)." *ACM SIGOPS Operating Systems
  Review* 22(4), 1988. https://dl.acm.org/doi/10.1145/54289.871709 / http://web.cs.wpi.edu/~cs557/f14/papers/confused_deputy-hardy.pdf
- Miller, M. S. "Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control." PhD
  thesis, Johns Hopkins University, 2006. http://erights.org/talks/thesis/markm-thesis.pdf
- Miller, M. S., Yee, K.-P., Shapiro, J. "Capability Myths Demolished." Johns Hopkins SRL2003-02.
  https://srl.cs.jhu.edu/pubs/SRL2003-02.pdf
- Watson, R. N. M., Anderson, J., Laurie, B., Kennaway, K. "Capsicum: Practical Capabilities for UNIX." USENIX
  Security 2010. https://www.usenix.org/legacy/event/sec10/tech/full_papers/Watson.pdf
- Klein, G. et al. "seL4: Formal Verification of an OS Kernel." SOSP 2009. https://www.sigops.org/s/conferences/sosp/2009/papers/klein-sosp09.pdf
- Shapiro, J., Smith, J., Farber, D. "EROS: a fast capability system." SOSP 1999. https://flint.cs.yale.edu/cs428/doc/eros.pdf
- WASI security model and component model: https://wasi.dev/security, https://component-model.bytecodealliance.org/

**Contemporary LLM-agent security (arXiv, review status unconfirmed — see §G)**
- Santos-Grueiro, I. "Context-to-Execution Integrity for LLM Agents." arXiv:2607.06000 (2026). https://arxiv.org/abs/2607.06000
- Lilienthal, D., Hong, S. "Mind the Gap: Time-of-Check to Time-of-Use Vulnerabilities in LLM-Enabled Agents."
  arXiv:2508.17155 (2025). https://arxiv.org/abs/2508.17155
- "ConfusedPilot: Confused Deputy Risks in RAG-based LLMs." arXiv:2408.04870 (2024). https://arxiv.org/abs/2408.04870
- "SoK: Trust-Authorization Mismatch in LLM Agent Interactions." arXiv:2512.06914 (2025). https://arxiv.org/abs/2512.06914

**Classical OS security**
- Saltzer, J. H., Schroeder, M. D. "The Protection of Information in Computer Systems." *Proc. IEEE* 63(9), 1975.
  https://www.cs.virginia.edu/~evans/cs551/saltzer/
- Bishop, M., Dilger, M. "Checking for Race Conditions in File Accesses." *Computing Systems* 9(2), 1996.
  https://nob.cs.ucdavis.edu/bishop/papers/1996-compsys/racecond.pdf
- Chen, H., Wagner, D., Dean, D. "Setuid Demystified." USENIX Security 2002.
  https://people.eecs.berkeley.edu/~daw/papers/setuid-usenix02.pdf
- Linux `openat2(2)`: https://man.archlinux.org/man/openat2.2.en

**Databases / transactions**
- Cahill, M., Röhm, U., Fekete, A. "Serializable Isolation for Snapshot Databases." SIGMOD 2008.
  https://people.eecs.berkeley.edu/~kubitron/courses/cs262a-F13/handouts/papers/p729-cahill.pdf

**Content addressing**
- Chacon, S., Straub, B. *Pro Git*, 2nd ed. Apress, 2014. https://git-scm.com/book/en/v2 (ch. 10, Git Internals)
- `git-verify-commit(1)`: https://git-scm.com/docs/git-verify-commit
- Benet, J. "IPFS - Content Addressed, Versioned, P2P File System." arXiv:1407.3561 (2014). https://arxiv.org/pdf/1407.3561
- Perkeep permanode/claim schema: https://perkeep.org/doc/schema/permanode, https://perkeep.org/doc/terms

**Configuration languages**
- CUE Language Specification: https://cuelang.org/docs/reference/spec/; "The Logic of CUE": https://cuelang.org/docs/concept/the-logic-of-cue/
- Dhall safety guarantees: https://docs.dhall-lang.org/discussions/Safety-guarantees.html; dhall-lang README:
  https://github.com/dhall-lang/dhall-lang; `dhall freeze` PR discussion: https://github.com/dhall-lang/dhall-haskell/pull/637
- Starlark spec: https://github.com/bazelbuild/starlark/blob/master/spec.md; Bazel docs: https://bazel.build/rules/language

**Package managers**
- Debian `apt-secure(8)`: https://manpages.debian.org/unstable/apt/apt-secure.8.en.html; Debian Handbook §6.6:
  https://debian-handbook.info/browse/stable/sect.package-authentication.html
- RPM/DNF repository metadata signing: https://docs.aws.amazon.com/linux/al2023/ug/repo-metadata-signing.html;
  https://blog.packagecloud.io/how-to-gpg-sign-and-verify-rpm-packages-and-yum-repositories/
- Alpine apk keys/signing: https://wiki.alpinelinux.org/wiki/Apk_spec, https://wiki.alpinelinux.org/wiki/Include:Abuild-sign

**Governance OS source (read for grounding, not modified)**
- `runtime/src/cit/binding.rs` (lines 1–29) — sealed-digest CIT record binding, the internal precedent cited in §A.3
- `runtime/src/policy_precedence.rs` (lines 1–22 and `Rule`/`Precedence` structs) — hand-reasoned merge logic and
  its documented 4.1.5/D027 incident, cited in §B.6/§C
- `runtime/src/verification/currency.rs` (`Currency::evaluate`, `close_currency`) — bespoke snapshot-recomputation
  logic, cited in §B.4
- `runtime/src/cit/materiality.rs` (module docs) — the eight material-change classes and the "proposer's trigger
  label is a claim" framing, background for §B.4/§C

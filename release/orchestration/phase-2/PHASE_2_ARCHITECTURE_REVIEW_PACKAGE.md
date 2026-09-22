# Phase 2 — architecture / meta-review package: the install-trust surface after four rounds

| Field | Value |
|---|---|
| Date | 2026-09-22 |
| For | the product owner |
| From | the Phase-2 outer orchestrator |
| Trigger | **OA-P2-06's stop condition, triggered on both limbs** by P2-AR-0077 |
| Status | **STOPPED.** `cap2-candidate-2` **not** minted. No fifth repair round started. No formal verification dispatched. |
| Evidence | `AGENT_RUNS/P2-AR-0077.run.yaml`; probes and raw results at `probes/P2-AR-0077/`; review commit `b96109d`; repair under review `e25ca70` |

## 1. Why I stopped

You set two conditions. Both fired:

> STOP and return to me for an architecture/meta-review if that fourth adversarial review: finds another materially new
> HIGH blocker on the install-trust surface; **or** leaves AR75-F1 or AR75-F2 materially open.

P2-AR-0077 (fresh Opus 5, independent of every repair and all three prior reviews) returned **`RESIDUAL_DEFECTS` — 3 HIGH,
1 MEDIUM, 1 LOW**, with all three HIGHs materially new, and both AR75 findings materially open as *classes*.

## 2. First, what the repair did achieve — this is not a failed round

The reviewer is emphatic and I agree: **the repair is competent, correctly scoped, and does exactly what P2-HO-0052
asked.** Specifically, and each proven by the reviewer's own reproduction against a **differential control** (the parent
commit `c34c439` extracted and built separately, so "closed" and "new" are measured, not asserted):

- **Both AR75 witnesses are dead.** `cp` through a symlink and `curl -K` both fired at `c34c439` — writing outside the
  project root — and both now gate. The `class: derived` overlay witness was accepted at `c34c439` and is now refused.
- **All three of the builder's self-declared gaps hold.** The untested dangling-symlink path gates. `--config`,
  `--config=<file>`, `-sK`, `-Ks` and `--CONFIG` all gate. The case-fold collision is exactly as disclosed, and the
  builder's test asserts precisely what its name claims.
- **All twelve prior findings remain closed**, re-verified by the reviewer's own probes across 26 and 14 shapes.
- **Every negative control passes. There is no over-gating.** A conforming install proceeds with **zero** gate records;
  `gov init` on a brownfield repository refuses nothing; legitimate declarations are honoured; ~14 edge cases of the new
  boundary check are inert with no false findings. **OD-P2-03 requirement 6 holds.**
- **Two of the three new HIGHs are pre-existing, not regressions.** AR77-F1 and AR77-F2 fire identically at `c34c439`.
  The repair did not break them; it revealed that the surface was never closed.

The boundary-resolution machinery itself is sound. In the reviewer's words: *"its problem is what it is handed, not what
it does."*

## 3. What is still open

**AR77-F1 (HIGH, new)** — `endpoint_host` ends with `(!host.is_empty()).then(…)`, so a `file://` URL with an **empty
authority** returns `None` and is never routed to the network branch. It then falls through to boundary resolution,
where the token begins with `f` and contains no whole `..` segment, so it is joined *under* the root as
`<root>/file:/etc/hostname` — judged inside. Four shapes install `not_gated`, `expands_authority: false`, no triggers,
nothing `undetermined`, **zero gate records**, while writing a file outside the project root or copying `/etc/hostname`
into it. The `health_check` variant **recreates its marker on every later `gov tools health`** — the exact recurrence
class OD-P2-05 clause 5 exists to close. *Verified by me at `runtime/src/tools.rs:1408`.*

**AR77-F2 (HIGH, new)** — `token_values` yields the token plus the RHS of the **first `=`** only, and `leaves_project`
tests the token's *prefix*. An absolute path embedded behind any other prefix character is invisible. `curl --write-out`
supports `%output{<path>}` (curl ≥ 8.3; this host has 8.5.0), redirecting its own output into an arbitrary file. Installs
ungated with zero gate records; marker written outside the root.

**AR77-F3 (HIGH, new)** — **`class` has a second authority-bearing consumer.** `orchestration::tasks::is_production_path`
exempts **six** values — `evidence | narrative | historical | generated | derived | runtime-data` — and gates three
controls. The repair's check names **two** of the six. One hand edit appending `{pattern: "product/*.yaml", class:
evidence}` to the project-editable `REPOSITORY_CONTRACT.yaml` is **not refused, not reported, invisible to `gov doctor`**,
and turns a refused `EXPERIMENT_OUTPUT_IN_PRODUCTION` into an accepted experiment naming a production path as an output.
*Verified by me: `tasks.rs:1865–1868` matches six; `policy_precedence.rs:586–587` matches two.*

The reviewer states the counter-argument fairly rather than burying it: `is_production_path`'s own doc comment describes
classifying a tree as `evidence` to sandbox experiments as an **intended capability**, via *"a governed change to the
repository contract"*. The capability is by design. **The defect is that a hand edit obtains it silently** — OC-P2-04
clause 3, and clause 4 is verbatim on the point: *"Silence is failure. An increase that takes effect without being
refused and reported is a defect even if some other control would later catch it."*

**AR77-F4 (MEDIUM, new)** — a **hard link** defeats the boundary model entirely: there is nothing to canonicalise. The
file outside the root was rewritten, verified by content comparison. MEDIUM because git does not preserve hard links, so
this cannot arrive through version control or a governed clone.

**AR77-F5 (LOW)** — the argument-indirection refusal tells an auditor that `curl -k` "reads further arguments from a
file"; `-k` is `--insecure` and reads nothing. The policy file discloses the collision honestly; the runtime message does
not. Same class as the AR75-F3 wrong justification corrected in this very round.

## 4. The meta-finding: every failure on this surface has been an enumeration failure

This is what I think you most need, and it is why I am not asking for a fifth round.

| Round | Mechanism | How it was defeated |
|---|---|---|
| 1 | per-token scan | wrapping |
| 2 | positive allowlist of *readable shapes* | 25 shapes |
| 3 | **invert the default** (P2-ADJ-0006) | the inversion **held** — but two list entries' premises were false |
| 4 | fix those two entries | the premise is still false for `curl`, twice more; and `class` comparison covered 2 of 6 values, 1 of 2 consumers |

**The inversion was right and it is still holding.** An unrecognised program gates. Unnamed wrappers gate. A project
cannot touch the policy lists. That is not the problem.

The problem is that **every exception to a fail-closed default is an enumeration, and each enumeration is a hole.** The
system's security currently depends on the completeness of sets that nobody can prove complete:

- the set of programs whose argv can be read in full (`plain_argument_programs`);
- the set of flags by which a program acquires arguments the OS never saw (`argument_indirection_flags`);
- the set of `class` values that confer an exemption;
- **the set of consumers of `class`** — the one that just failed.

Each repair correctly fixed the enumeration it was handed and left the *enumerating pattern* intact. Four rounds is
enough evidence: the pattern, not any particular list, is the defect.

Note the sharpest instance. `curl` is on `plain_argument_programs` **because the certification suite needs it**, on the
stated ground that its arguments carry no file-execution meaning. That ground was false when P2-AR-0075 found `-K`, and
it is false twice more now. The reviewer stopped enumerating deliberately and put the real question to you: *not "which
curl flag next", but whether `curl` can be on that list at all.*

## 5. The meta-finding about our own method: P2-ADJ-0006 failed one level up

I required (P2-ADJ-0006 §3) that acceptance evidence be **a property over the default**, not the last reviewer's shape
list, because tests encoding the previous attack guaranteed recurrence. The builder complied faithfully. It did not help,
and the reason is instructive:

```rust
for cand_class in ["generated", "derived"]   // repair4.rs:616
```

in a test named `a_candidate_conferring_the_generated_exemption_is_refused_for_any_class_value_…`. **The test says "for
any class value" and quantifies over exactly the two values the fix implements.** The AR75-F1 property test has the same
shape: every case it generates is a token that *is* a path — it never produces a URL, a path embedded in a larger token,
or any `curl` argv at all, which is precisely where AR77-F1 and AR77-F2 live.

The builder wrote both the mechanism and the generator that tests it, so **the generator's domain is the implementation's
domain, and the property proved is "the fix does what it does."** The old failure was a test encoding *the last
reviewer's shape list*; the new one is a test encoding *the implementation's own value set*. Same structure, one level up.

**This directly answers the test-author independence question you raised while the tests were running, and vindicates it.**
Builder-authored property tests are not a substitute for independent attack — not because the builder was careless (this
one was unusually careful and disclosed its own gaps unprompted) but because no author can generate the case they failed
to imagine. The frozen gate contract already says this at line 57: *"builder tests are regression evidence, not
independent certification."* What we learned is that it applies to **property** tests too, which I had implicitly assumed
were immune.

## 6. Options

**A — Empty the exception list: installs must execute pinned artefacts, not raw commands.** Remove `curl` and `cp` from
`plain_argument_programs`. Any install that is not a hash-pinned file gates. This follows directly from OD-P2-05's own
logic — *bind the bytes* — since a raw command has no artefact to bind, while an `install.sh` does. It kills AR77-F1, F2
and F4 and the entire class at once, because there is no longer a path that reaches the per-token scan on trust.
*Cost:* a real, comprehensible usability cost — projects must wrap installs in pinned scripts, and the certification
suite's own `curl` fixtures must change. *This is the minimal coherent answer and my recommendation for the command half.*

**B — Constrain effects instead of predicting them.** Execute install commands under an isolation boundary that cannot
write outside the project root, making classification advisory rather than load-bearing. This is the only option that
stops depending on completeness at all. `Isolation::Sandbox` already exists in the scheduler (3 of 41 checks), so there
is a foothold. *Cost:* genuine engineering, platform-specific behaviour, and almost certainly beyond Phase 2. **The right
long-term answer; I do not think it can be done inside this phase.**

**C — For AR77-F3 specifically: make the exemption set derived, not enumerated.** One authoritative predicate — *"does
this class confer any exemption from any governed control?"* — that both `is_production_path`, `contract_generated` and
the overlay comparison call. Adding a consumer then cannot silently widen authority, because the comparison already
covers the whole exemption vocabulary. *Cost:* small and local. **I regard this as correct regardless of what you choose
elsewhere, and it is the structural version of the fix rather than a fourth enumeration.**

**D — Re-scope.** Declare the tool-installation trust surface out of the Phase-2 capability baseline, with the residuals
recorded and compensating controls named, and gate it at R2 certification instead. The other 51 blocker classes are
closed. *This is yours alone — it changes what must hold now rather than what is true.*

**E — Accept and disclose**: mint with three HIGHs documented and let formal verification judge. I do not recommend it —
AC-3 and AC-4 would almost certainly fail on defects we have already characterised, spending a nine-role verification to
learn what this package says.

## 7. What I have not done, deliberately

No fifth repair round. No mint. No formal verification. No change to any accepted boundary. The repair branch
(`e25ca70`), the review branch (`b96109d`), all probes and every run record are committed and reproducible. `cap2-candidate-2`
does not exist.

If it helps: **options A and C together are a bounded round** — one list change plus one predicate, with independent
attack afterwards. B is a phase of work. D is a decision only you can make.

# Independent challenge of the architecture synthesis

| Field | Value |
|---|---|
| Run id | **P2-SYN-0002** (independent challenger) |
| Date | 2026-09-23 |
| Target | `release/orchestration/phase-2/RESEARCH/SYNTHESIS.md` (P2-SYN-0001) |
| Nature | **READ-ONLY.** One document written. No product, runtime, kernel, policy, schema or test file touched. Nothing implemented. |
| Stake | None. I did not write the synthesis, conduct the research, or contribute to the escalation package. |
| Trees read | frozen reviewed tree `35461c9` (`phase2/remediation-ac-review`) and the working tree at `b99a50d` (`release/4.1.6-rc1`). |
| Evidence produced | two probes run on this machine (Appendix, probes 1 and 2), both writing only into the session scratchpad; plus source re-derivation at `35461c9`. |

---

## 0. Headline

**The synthesis is substantially sound, and its two corrections to the owner (P79-F10 is false; the recommended
Property-A fix does not work) both survive independent verification. Its ranking — Option 1 › 2 › 3 — survives.**

**But its own proposed fix is defeated, by execution, on this machine.** The property §9 promises —
*"the interpreter that runs is the one intended, on the bytes reviewed"* — is **false as specified**. I ran the
synthesis's own prescription (`O_PATH|O_NOFOLLOW` descriptor acquisition → `execveat(fd,"",AT_EMPTY_PATH)` with an
OS-constructed `envp` and an OS-pinned cwd) against a reviewed, hash-pinned artefact and made it execute an
**unpinned, unreviewed project-local file** twice, by two different routes, both of which act **before a single
reviewed byte runs**.

The cause is the synthesis's own diagnosis, one level further down than it looked:

> `env` is a program whose *arguments* act after `gov` loses control — and a **`#!` line is a program invocation
> `gov` does not construct at all.** `execveat` hands the kernel an object; the kernel then performs a *second*
> resolution, from bytes inside the artefact, against a namespace the OS pinned for it.

The synthesis found this pattern, named it as the study's thesis, applied it to the escalation package's
recommendation — and did not apply it to its own. **That is the fourth instance of the study's thesis in this
study, and the first inside the recommended architecture.**

This **qualifies and extends** Option 1; it does not displace it. The remedy is small and in the same spirit.
But the sentence "*both problems reduce to the same three changes*" is no longer true: it is four.

---

# PART I — THE OWNER'S SEVEN QUESTIONS, ANSWERED DIRECTLY

## Q1. Did the synthesis overlook a mature existing primitive?

**Yes — one, and it is in-repo, which makes it the same shape as the synthesis's own best finding.**

`runtime/src/memory/profile.rs:378` already implements `fn shebang(file) -> Option<String>` — reading a script's
`#!` line to determine *which interpreter actually runs* — and that module's own header states the interpreter so
found is **content-hashed**:

> *"| inference runtime | in-process | the interpreter or executable the command runs (**shebang** or `PATH`
> resolution), **content-hashed** |"* — `memory/profile.rs:19` **[verified at 35461c9]**

So the product already knows, in one subsystem, that a shebang decides which executable runs and must be hashed.
**`runtime/src/tools.rs` — the installation classifier that carries OD-P2-05 clause 1 — never reads a shebang.**
`git grep '#!'` over `runtime/src/` at `35461c9` returns `memory/profile.rs` and nothing else. This is precisely
the synthesis's §1.1 move (`t2::verify_file` exists and was never pointed at the path map) recurring at the
execution boundary, and the synthesis did not make it.

**Caveat, measured:** the in-repo primitive is itself incomplete against this adversary. Its `env` special case
(`parts.find(|a| !a.starts_with('-'))`) returns **`"PATH=."`** as the interpreter for
`#!/usr/bin/env -S PATH=. sh`. Reusing it is right; reusing it unchanged is not.

Everything else I looked for, the synthesis had. I found no missed *external* primitive. `AT_EXECVE_CHECK`,
`openat2`, `memfd_create`+`F_SEAL_WRITE`, `fexecve`, Landlock, seccomp, bubblewrap, `tough`, in-toto, CUE, OPA,
Sigstore are all present and correctly classified. Its `NOT APPLICABLE` reasons (kernel ≥6.14 for
`AT_EXECVE_CHECK` against 6.6.87; no guest TPM; no fleet for Uptane) are correct.

## Q2. Is any custom mechanism proposed unnecessarily?

**No.** Exactly one `BUILD CUSTOM` survives its own filter (floor-composed `decide()`), and I agree it is
justified: no external primitive expresses "this project's path map, floored by this kernel's template," and the
kernel-template floor it composes against is **already authenticated** (below). The ~40-line estimate is
optimistic but the order of magnitude is right — see F-7.

I checked the inverse too: is any *external* mechanism proposed where in-repo material would do? No. The
synthesis consistently prefers the in-repo primitive (`t2`, `human_channel`, `cit::binding`) and its stated reason
— *a shipping in-repo implementation outranks an unreviewed preprint as evidence* — is the right rule here.

## Q3. Is any recommended dependency solving a stronger or different problem than ours?

**No, and its declines are well-judged.** The three declines I tested hardest all hold:

- **bubblewrap**: the synthesis declines it on the ground that *"its own docs say the security is entirely the flag
  list you write"* — i.e. it replaces one bespoke enumeration with another. Correct, and it is the brief's §7 test
  applied honestly against a mechanism the orchestrator's own measurement had just made *more* feasible. Declining
  something you just learned is available is the harder call and the right one.
- **OPA/Rego, CUE toolchain**: a whole policy runtime to obtain an `AND`. Correct to decline.
- **git signed commits** (Agent 2's and Agent 5's shared instinct): the synthesis's three grounds are all real —
  it misses uncommitted working-tree edits (P79-F8's actual vehicle), it promotes git to a runtime authority
  dependency, and it creates a **second** owner-key custody story beside `human_channel`. I verified the third:
  `human_channel.rs:15-16` states *"Ed25519 keys of the `human-gate` role, held by the product owner **outside the
  machine the agents run on** (the `gov` binary contains no signing code and no key)"* **[verified]**, and
  `srr::crypto::verify_strict` is the only crypto call on that path. Agent 2's own §10 goal ("one root of trust
  instead of two") does indeed condemn its own recommendation. The adjudication is correct.

**One dependency is solving a *different* problem and the synthesis says so**: Landlock closes effects
(AR77-F1/F2/F4), not identity (the open HIGHs). See Q6 and F-11.

## Q4. Are trust assumptions explicit?

**Yes — §15 is the best part of the document, and it is honest to the point of self-harm.** Three specific credits:

1. **The T2 symmetric-key limit is stated, quoted from the module, and correctly weighted.** Verified verbatim at
   `runtime/src/t2.rs:79-85`. **The synthesis's quote is accurate but truncated one sentence early, and the
   omitted sentence makes the exposure worse, not better**: *"what such a process forges on one of the owner's
   machines is **honoured on the others** holding the same key."* The seal is not merely detection-grade against a
   same-account agent; a forgery propagates across every provisioned machine. The synthesis's conclusion is
   unchanged and its recommendation (do not let the seal carry weight it cannot bear) is if anything
   under-stated. **Credit, with the quote to be completed.**
2. **Assumption 3** ("`argv` handed to a pinned artefact is still attacker-influenced… a project that pins
   `/usr/bin/env` as its artefact reconstructs P79-F1 inside a 'conforming' install") **predicts, in prose, an
   attack I then executed** (§P-2 case C). That is a genuine act of intellectual honesty and it should be
   credited as such rather than re-reported by me as a finding. My only correction is to its adjective — see F-6.
3. **§10.4 and §9.4** each state a limit before a challenger could find it. Both are real limits, both correctly
   described; §10.4 is materially larger than its placement implies (F-9).

**What is missing from §15 is the assumption my probes broke**: *the artefact's own first line does not choose
the interpreter.* That assumption is nowhere stated because it was not noticed. Adding it as assumption 8 is not
sufficient — it is the assumption the architecture must **enforce**, not disclose (F-1, F-2).

## Q5. Has Level 3 contaminated Level 1/2?

**No. I looked specifically and found nothing.** §14's test is the right one — *name the Level-3 component §9 or
§10 introduces* — and I cannot name one. `execveat` is a plain syscall, not a boundary; `O_PATH`/`O_NOFOLLOW` is
descriptor hygiene; floor-composition, the T2 seal and the `human_channel` route are all in-repo Level-2
mechanisms. Nothing in the §11 minimum adds a namespace, an LSM, a privilege or a daemon.

**The synthesis also correctly resists the contamination that would have been easiest to commit**: Agent 1's
`tough` WRAP is deferred to the frozen meta-review rather than actioned, with the right reason (ARCH-0003 is
owner-adopted and R0/R1-accepted; the RoT-1 lineage is frozen; D-0008/ARCH-0002 are PROPOSED, not active). That
matches the memory record and the brief's correction. **Clean.**

The one place contamination *could* have entered — Landlock — the synthesis pushes to R2 and labels explicitly as
"contaminating if placed in REQUIRED NOW." I agree with the placement (F-11).

## Q6. Would the recommendation actually have prevented the concrete R0/R1/P79 attacks?

**Mostly yes, with one correction and one restatement.**

| Defect | Synthesis says | I find |
|---|---|---|
| P79-F11 `env --chdir=decoy sh install.sh` | YES | **YES.** Confirmed: with `wrapper_programs` deleted, `env` reaches the classifier's fail-closed default (`UnrecognisedProgram`) and gates — I read that default at `tools.rs:1338-1348` and it needs no new list. Change 2 then execs `/bin/sh <abs>/install.sh`, which my control T3/E confirms runs the verified bytes. |
| P79-F12 | YES | **YES**, same path. |
| P79-F1 `env PATH=. true` | YES, for a corrected reason | **YES**, and the corrected reason is right. `true` also ceases to be ungated once `plain_argument_programs` goes. |
| P79-F8 / P79-F9 | YES | **YES for this repository. NO for a project onboarded by `gov adopt` with a native layout** — see F-9. This is not a footnote. |
| AR77-F3 | YES, structurally | **YES, and more strongly than argued** — see F-8. |
| AR68/AR73 family | YES as a class | **YES**, with the residual in F-5/F-6. |
| AR77-F1/F2/F4 | NO | **NO**, correctly and plainly stated. |
| R0/R1 unauthenticated-source | NO, and must not claim to | **NO.** Correct; nothing in §9/§10 touches Level 1. |
| **Direct-artefact shape (`install_command: ["install.sh"]`)** | *not considered* | **NO — the recommendation does not close it.** F-1, F-2. |

**The correction.** The synthesis's defect table is built from the *declared-interpreter* shape (`["sh",
"install.sh"]`), which is what every certification fixture uses (`r2_failclosed.rs:643`, `r2_toolbind.rs:463`,
`repair4.rs:676` — all `["sh", "<file>"]`) **[verified]**. The classifier also admits the **direct-artefact**
shape: `looks_like_a_file(argv[0])` → `classify_file_candidate` → readable-and-ungated when the bytes match the
pin **[verified, `tools.rs:1334-1336` and `classify_file_candidate`]**. For that shape, §9's guarantee is broken
(F-1, F-2) and §11's minimum does not reach it.

## Q7. Does it simplify the system or merely relocate complexity?

**It genuinely simplifies — more than one of its own metrics claims, and less than another.**

**Genuine simplification, verified:**
- The 45 deleted envelope entries do not reappear anywhere. Deleting `wrapper_programs` does not require a
  "wrapper detection" replacement: the classifier's **existing** inverted default already gates an unrecognised
  program. That is deletion without relocation, and it is the strongest structural claim in the document.
- The chokepoint claim is not merely true, it is **structurally** true (F-8): `PathDecision` — the only type with
  a `.class()` method — is constructed at exactly **one** site in the entire runtime, inside `decide()`
  (`paths.rs:710`). The synthesis argued this by enumeration; it can be argued by construction, which is
  unfalsifiable-proof-surface → single-proposition, exactly what the brief asked for.
- Change surface for the minimum is genuinely tiny: `wrapper_programs` appears in one policy file and `tools.rs`;
  `skip_wrappers` in `tools.rs` and one certification test **[verified by `git grep -c` at `35461c9`]**.

**Relocation I did find, and it is small but real:**
- §15 assumption 3's residual — *"is this artefact an exec vector"* — is described as *"smaller and bounded."*
  **It is smaller. It is not bounded.** F-6 shows a byte-identical *copy* of `/usr/bin/env` under an arbitrary
  project path satisfies the pin and is the exec vector. No name list reaches a copy; only a content denylist
  would, and that is unbounded. The honest statement is that this residual is **co-extensive with the concession
  §9.4 already makes** ("what the interpreter does next") and therefore belongs to OD-P2-05 clause 4's governed
  review, not to a bounded enumeration.
- The property "the OS executes an object, not a name" is presented as architecture but scoped to *"`util::run_cmd`'s
  two install call sites."* `run_cmd` has **four** call sites at `35461c9`; the other two —
  `adopt.rs:622` (a detected native test command) and `verification/product.rs:255` (`pl.command`, a
  project-declared verification plan) — execute **project-influenced** command vectors through the same
  program-by-string, no-`env_clear` path **[verified]**. Neither is an open HIGH, so this qualifies scope, not
  correctness; but "two call sites" should read "two now, four for the property."

---

# PART II — FINDINGS

## What I proved

### F-1 **[MEASURED — concrete defeat of the proposed fix]** A relative `#!` line inside pinned, reviewed bytes executes an unpinned project file

I implemented §9.2 exactly as specified — `open(O_PATH|O_NOFOLLOW)`, OS-constructed
`envp = {PATH=/usr/bin:/bin, HOME=/nonexistent}`, cwd pinned to the project root, then
`execveat(fd, "", argv, envp, AT_EMPTY_PATH)` — and ran it against a hash-pinned artefact whose only unusual
property is its first line.

```
artefact  a.sh   (sha256 42913c68…ac81 — this is what pinned_files would hold)
contents  #!./w
          echo "(never reached)"

OS resolves to absolute path, clears env, fixes PATH, pins cwd, execs the OBJECT:
  → PWNED: unpinned ./w ran (shebang-named interpreter)      rc=0
```

`./w` is an ordinary project file. It is **not** in `pinned_files`, is **not** hashed, is **not** reviewed, and
can be rewritten after review without changing `a.sh`'s hash. The kernel resolved `./w` against the cwd — **the
cwd the OS itself pinned.** Pinning the working directory does not merely fail to help here; it is the mechanism's
enabling condition. (Control A2: with cwd elsewhere, `execveat` fails `ENOENT` — the attack *needs* the OS's own
pin.)

**This violates OD-P2-05 clause 1 directly** ("every executed file hash-pinned and re-verified at every
execution"), and it violates §9.1's stated property ("the OS executes a kernel object it holds, never a name it
was handed") — the OS held the object; the object handed the kernel a name.

It is **not** an instance of §9.4's disclosed limit ("what the interpreter does next"). It happens *before* the
interpreter runs, and it decides *which* interpreter runs.

### F-2 **[MEASURED — concrete defeat]** `env -S` in a `#!` line discards the environment the OS constructed

```
artefact  b.sh   (sha256 881dcbf2…f515)
contents  #!/usr/bin/env -S PATH=. sh
          echo "(never reached)"

same OS-constructed envp (PATH=/usr/bin:/bin), same pinned cwd, same execveat:
  → PWNED: unpinned ./sh ran (PATH=. via env -S in shebang)   rc=0
```

§9.2(3) — *"Construct the environment; do not filter it"* — is defeated in one exec hop by four bytes inside the
reviewed artefact. The OS built `PATH=/usr/bin:/bin`; the shebang named `/usr/bin/env` absolutely (so nothing the
OS does to `PATH` matters), and `env -S` rebuilt the environment inside the child. **This is P79-F1 reconstructed
inside a conforming, pinned, byte-verified installation under a fully constructed environment.**

Measured: GNU coreutils 9.4, kernel 6.6.87.2-microsoft-standard-WSL2, unprivileged.

### F-3 **[VERIFIED, source]** Nothing in the installation path reads a shebang

`git grep -n '#!' runtime/src/` at `35461c9` finds `memory/profile.rs` only. `classify_file_candidate`
**[verified in full]** checks: token does not leave the project; the path is named in `pinned_files`; the file
reads; `canonicalize()` stays under the root (AR73-F6); sha256 matches. **It does not look at the first line.**
So F-1 and F-2 reach the *ungated* branch — `Option<Unreadable>` is `None`, `change_class.branch` is
`not_gated` — for the direct-artefact shape the classifier admits.

### F-4 **[VERIFIED]** The remedy exists in-repo and is itself incomplete

`memory/profile.rs::shebang` resolves `#!` and even special-cases `env`. Against `#!/usr/bin/env -S PATH=. sh`
its `parts.find(|a| !a.starts_with('-'))` returns **`"PATH=."`**. Reuse it, do not reuse it unchanged.

### F-5 **[VERIFIED]** `O_PATH|O_NOFOLLOW` does what the synthesis says, and a naive hash does not

A pinned artefact that is a **symlink** to `/usr/bin/env` is refused by the prescribed descriptor acquisition
(`ELOOP`, measured) — the synthesis's §6 classification of `O_PATH + O_NOFOLLOW` as the correct acquisition is
right and load-bearing. Note the contrast: `sha256sum` on that same path happily reports `/usr/bin/env`'s digest
(measured). Hash-through-descriptor is not a nicety.

### F-6 **[MEASURED]** §15 assumption 3 is real, is reachable without naming `env`, and is not "bounded"

```
cp /usr/bin/env proj/tools/setup
sha256(proj/tools/setup) == sha256(/usr/bin/env) == 886e5fa8…a050
declared command: ["tools/setup", "PATH=.", "true"]
  → PWNED: project-local ./true ran                          rc=0
```

The pin is satisfied, the bytes are verified, the artefact never leaves the project root, and the result is
P79-F1. The synthesis **predicted this in prose** and deserves credit for it. My correction is one word: it calls
the residual *"smaller and bounded."* A copy defeats every name-based list, so the residual is not bounded — it
is the same set as §9.4's already-conceded "what the interpreter does next," and should be assigned to the same
place (OD-P2-05 clause 4's governed review), not presented as a small enumeration.

### F-7 **[VERIFIED]** The floor is not reachable from `decide()`; change 3 is not "inside an existing function"

- `Project::contract()` builds `RepositoryContract::new(self.overlay().get("REPOSITORY_CONTRACT.yaml"))`
  (`project.rs:176`). `RepositoryContract` carries `data`, `roots`, `rules`, `sensitivity` — **no kernel
  template** (`paths.rs:555-560`).
- The kernel template is read as a **local variable** inside `PolicySet::load`
  (`repository_contract_baseline`, `policy.rs:410-414`) and is not retained on `PolicySet`.
- Therefore floor-composition requires: retain the template (or its `paths`) on `PolicySet`, add a field to
  `RepositoryContract`, and set it at its **one production construction site**. That is a new field and a new
  retention, plus the ~40 lines. Still small; still the right shape; **but "≈40 lines inside an existing
  function" and "one function plus one string in a three-member const" (the reversibility claim) both understate
  it.** Call it one function, one struct field, one retention, one construction site.

**Two things I verified that make this *better* than the synthesis argued, and it should say so:**

1. **The floor is authenticated.** `PolicySet::load` takes `kernel_dir = trust.policy_root`
   (`policy.rs:117`) — `kernel_trust`'s verified root, which authenticates the payload against
   `KERNEL_MANIFEST.json`, the manifest against `framework.lock.kernel_manifest_hash`, and the whole against this
   machine's protected SRR installation record, substituting the binary's embedded payload otherwise. **So
   floor-composition rests on authenticated kernel content, not on a project-editable file** — which is exactly
   why it "needs no key" and why it is genuinely stronger than the seal. The synthesis asserts this; it does not
   show it, and it is the single most reassuring fact in the Property-C story.
2. **`contract()` already reads the *effective* overlay**, not the raw file: `Overlay::get` returns
   `set_effective`'s value when present, and `contract()` calls `policies()` (which sets it) first
   (`policy.rs:46-58`, `project.rs:148-176`) **[verified]**. The precedence layer's refusals therefore already
   reach every `decide()`. That is the rail floor-composition rides on, and it exists.

### F-8 **[VERIFIED]** The single-chokepoint claim is TRUE — and provable by construction, not enumeration

I enumerated all 41 `.class()` sites at `35461c9` independently. Excluding `#[cfg(test)]` and the comparison
machinery (`policy_precedence.rs:606`, `rule_effective_attrs`), **every production read derives from
`RepositoryContract::decide()`**. I traced each receiver: `memory/manifest.rs:234` (`let d = contract.decide(&rel)`),
`orchestration/tasks.rs:954,1882` (`decide(path)`), `memory/indexer.rs` — all six sites flow from
`contract.decide(rel)` at `indexer.rs:1395` and `:1472`, and `indexer.rs:210` takes `d: &PathDecision` as a
parameter; `paths.rs:445` is `PathDecision::is_secret` calling its own `class()`.

**Stronger than the synthesis argued:** `PathDecision` is the only type carrying `.class()`, and it is constructed
at exactly **one** place in the entire runtime — `paths.rs:710`, the tail of `decide()`. The only other
`PathDecision`-typed function is `rule_effective_attrs`, which obtains one *by calling `decide()`*. So "no consumer
enumeration is needed" is a **type-level** fact, not a search result. OD-P2-07 C's "search for ALL consumers" is
discharged by construction. The synthesis should make this argument; it is the difference between "I looked and
found one" and "there cannot be another."

**Two small errors in its list**, neither weakening the claim: `migrations/executor.rs:714` is inside
`#[cfg(test)] mod tests` (which begins at line 665) — a test, not a production consumer; and its parenthetical
"~19 production consumers" over-counts slightly for the same reason.

### F-9 **[VERIFIED]** The floor-coverage limit is a hole, not a footnote — for adopted projects

`framework/overlay-templates/REPOSITORY_CONTRACT.yaml` floors `governance/**`, `spec/**`, `product/**`,
`archive/**`, `**/.env*`, `**/secrets/**`, `.governance-runtime/**` **[verified, 28 rules]**.

`runtime/src/adopt.rs:1579` and `:1585` **[verified]** generate, for any repository whose source or tests are not
under `product/`:

```rust
extra.push(json!({"pattern": format!("{d}/**"), "class": "test",   "owner_role": "independent-test-designer", …}));
extra.push(json!({"pattern": format!("{d}/**"), "class": "source", "owner_role": "backend-engineer",          …}));
```

with `d` excluded only when it is one of `spec|governance|archive|product|docs`. So `src/**`, `app/**`, `lib/**`,
`cmd/**` are **project-declared patterns with no kernel counterpart, hence no floor**.

**Consequence, stated plainly:** for a project onboarded by `gov adopt` with any layout other than the kernel's
own, floor-composition closes **zero** of P79-F8 and P79-F9's shape. `{pattern: src/*.py, class: test}` still
cancels `MATERIAL_CHANGE_REQUIRES_CIT` at `cit/materiality.rs:870`, and still drops the file out of
`lineage.rs:981`'s `CODE_CLASSES` filter. The *instance* is closed because this repository uses `product/`; the
*capability* is untouched for the population `gov adopt` exists to serve.

The synthesis states this limit accurately in §10.4 and asks the right question in §16 Q3 — **credit** — but its
§5 verdict table says "P79-F8 — YES" without qualification, and its Option 1 row claims "Closes all 4 open HIGHs."
Those two should read "closes them for kernel-layout projects; for adopted layouts the shape remains open until
the floor is extended to declared project roots." **Q3 is not an open question to file; it is a precondition of
the claim.**

### F-10 **[VERIFIED]** Deletion arithmetic: the envelope count is exact; two line counts are wrong

**Exact, checked entry by entry at `35461c9`:** `installation_envelope` holds **106** entries; the seven deleted
lists hold **45** (`opaque_recipe_programs` 14, `inline_code_flags` 9, `wrapper_programs` 8, `script_interpreters`
6, `flagless_code_programs` 4, `argument_indirection_flags` 2, `plain_argument_programs` 2); the retained eight hold
**61** (`host_authority_tokens` 28, `credential_patterns` 9, `privilege_tokens` 9, `host_authority_classes` 4,
`host_scope_flags` 4, `policy_paths` 4, `network_classes` 2, `credential_classes` 1).  Every figure in §8's execution table matches mine exactly. **The synthesis's refusal to claim "106 deleted" is correct and creditable.**

**Two corrections:**

| Claim | Measured at `35461c9` |
|---|---|
| `LOADER_ENV_VARS`, **32 entries** | **30 entries** (32 *lines* including `pub const … = &[` and `];`). The list was counted by its representation rather than its contents — a small, ironic instance of the study's own thesis. |
| `CLASS_EXEMPTIONS` table, **30 lines** | **20 lines** (`const` through `];`); 22 with its doc comment. |

Consequently the comparison-machinery total is **≈447**, not 457, and the net deletion ≈**−250**, not −260. Every
other span I re-measured matches exactly: `evaluate_path_rules_overlay` 131, `path_rule_narrowing` 90,
`overlap_is_no_less_restrictive` 83, `evaluate_path_rules` 71, `rule_effective_attrs` 16, `describe_exemptions` 13,
`Exemption` enum 10, `class_exemptions` 7, `class_confers` + `patterns_may_overlap` 6.

**The `LOADER_ENV_VARS` observation itself is correct and is the best small point in §8**: the list contains no
`PATH`, no `IFS`, no `GIT_SSH_COMMAND` **[verified — full list re-derived]**. The product's best existing
environment defence omits the variable P79-F1 uses.

### F-11 **[VERIFIED]** The `class`-is-a-label finding holds; the Landlock placement holds

- `cit/materiality.rs:870` reads exactly as quoted **[verified]**; `paths::Exemption` has exactly two variants,
  `TaskMutationObservation` and `ProductionTreeMembership` **[verified, `paths.rs:371-380`]**; `CLASS_EXEMPTIONS`
  maps six classes onto those two. A `source → test` edit confers neither exemption, so
  `overlap_is_no_less_restrictive` passes it while `materiality`'s **positive** `class == "source"` match silently
  stops firing. **`class` is a label, not a level; a bidirectional predicate over it is meaningless. Sound, and
  correctly kills the escalation package's option (i) on evidence.**
- **Landlock at R2:** the synthesis makes a call Agent 4 explicitly declined to make, using a reason Agent 4 itself
  supplied ("a legitimate reason to defer this to R2 rather than pull it into a stopped Phase 2, and it's the
  owner's call"). That is adjudication, not overruling, and it is well-founded: a Level-3 LSM closing two
  already-disclosed MEDIUMs while HIGHs are open is priority inversion. **One precision correction:** the
  synthesis says Landlock "closes neither open HIGH." Agent 4 notes that a blanket
  *no `LANDLOCK_ACCESS_FS_EXECUTE` under the project root* ruleset **would** stop P79-F1's specific shape — as a
  containment side-effect, not a fix, and one that must be carved out the moment any build step legitimately
  executes a project file. The conclusion is unaffected; the sentence should be "closes no open HIGH's underlying
  defect."

### F-12 **[VERIFIED]** The one-mechanism rejection is correct — and my probes strengthen it

The synthesis rejects Agent 6's unification on the ground that the two deputies differ: the kernel's `execve` for
2B versus `decide()` for 2A/2C; Governance OS controls only the second. Agent 6 argued the decomposition was
itself the failure.

**I adjudicate for the synthesis, on evidence I produced.** F-1 and F-2 show the kernel performing a *second*,
independent resolution from bytes inside the artefact — after the OS has handed it a descriptor. A CXI-style
action manifest binding `{interpreter: sh, artefact: install.sh, argv, envp}` describes that invocation perfectly
and stops **neither** attack, because nothing consumes the manifest at the moment the kernel reads `#!`. Agent 6's
mechanism is a *description*; the defeat happens below descriptions. **"A manifest can describe both. It can
enforce neither" is now measured, not asserted.**

Agent 6's *framing* contribution stands and the synthesis adopts it correctly: Hardy 1988 / Miller 2006, and
`cit::binding`'s `os_state` block as an already-shipping instance of the manifest shape. Agent 6's warning about
the research org chart mirroring the repair org chart is fair and partly upheld by the synthesis itself (§7.4's
seed-list audit). It does not carry the conclusion.

## What I suspect but did not prove

1. **The direct-artefact install shape may be rare in practice but is not forbidden.** Every certification fixture
   I read uses `["sh", "<file>"]`. I did not build a project descriptor and run `gov tools install --execute`
   end-to-end for `["install.sh"]`; I derived its admissibility from `looks_like_a_file` + `classify_file_candidate`
   in source. **If the owner wants F-1/F-2 graded as an exploitable finding rather than an architecture defect,
   that end-to-end run is the missing step and it is cheap.** As an architecture finding it stands regardless:
   §9 prescribes `execveat` on the artefact descriptor, and that prescription is what my probes defeat.
2. **The `#!` route probably also survives §11 change 2 for the declared-interpreter shape in one sub-case** —
   where the pinned "script" is itself handed to an interpreter that re-execs (`sh -c` inside pinned bytes). I did
   not separate this from §9.4's conceded limit because I believe it *is* that limit, honestly disclosed.
3. **Reverting a kernel-policy deletion is not purely a `git revert`.** Removing `wrapper_programs` from
   `framework/policies/TOOL_POLICY.yaml` changes the kernel payload, hence `KERNEL_MANIFEST.json`,
   `framework.lock.kernel_manifest_hash`, the binary's embedded payload and this machine's SRR installation
   record. I did not attempt it. "Reversible in an afternoon" is right about *code*; it is a claim about the
   release transaction that I could not check, and `ENFORCEMENT_MAP.yaml` coverage (`policy_coverage.rs` treats
   "declared but does nothing" as a finding) is a second small edit the synthesis does not mention.

## What I could not rule out

1. **Whether any *other* second resolution exists between descriptor and first instruction.** I found two (`#!`
   interpreter path; `env -S` rebuilding `envp`). I did not enumerate dynamic-loader routes (`ld.so` config,
   `DT_RUNPATH`/`$ORIGIN` in a pinned ELF artefact, `LD_*` — note `LOADER_ENV_VARS` is stripped only on the
   *plugin* path, not at `run_cmd`). **I specifically could not rule out that a pinned dynamically-linked ELF
   artefact resolves a library from a project-controlled path.** This is the same shape as F-1 and deserves the
   same probe before implementation.
2. **Whether the floor-composition field-wise AND is well-defined for every attribute.** §10.2 gives orders for
   `indexing`, `mutation`, `agent_read`, `export`, `sensitivity`. `decide()` merges `class_defaults(cls)` then the
   rule's explicit fields over `base_defaults()`, and applies secret-locking, sensitivity ranking, `never_index`
   and `never_export` **after** the rule loop (`paths.rs:608-712`). I did not verify that a floor/local AND
   composes correctly with that post-processing. It looks composable; I did not prove it.
3. **Whether `execveat`'s degradation path is safe.** The synthesis says the design "must degrade to change 2's
   absolute-path exec, not fail open." I agree, and note F-1/F-2 apply to *both* limbs, so the degradation is not
   the weak point — the missing shebang check is.

---

# PART III — VERDICT

## Is the synthesis fit to go to the owner?

**Yes, after one substantive amendment and three corrections. Its two headline findings, its ranking, its
adjudications and its honesty are all sound; the flaw is in the specification of its own fix, and the flaw is
fixable in the same idiom.**

What is right and should not be softened:

- **The falsification is real.** I reproduced T1/T2/T3 exactly (`env -i PATH=/usr/bin:/bin`, cwd pinned; both
  attacks succeed; wrapper-free control runs the verified bytes). The escalation package's §6 recommendation must
  be marked superseded, as the orchestrator already recorded.
- **P79-F10 is false.** `t2::verify_file`, `t2::classify_path` and `cit::binding` all exist, all public, all
  general; `SEALED_RECORD_TYPES` has three members and the path map is not one **[all verified]**.
- **The single-chokepoint claim is true and is provable more strongly than it was argued** (F-8).
- **The floor is authenticated kernel content, not a project file** (F-7) — the best fact in the Property-C story,
  and currently asserted rather than shown.
- **Option 1 › 2 › 3 stands.** Nothing I found favours Option 2 or 3. Option 3 in particular remains a superset of
  Option 1's need, and F-1/F-2 would survive inside a bubblewrap jail unchanged (`./w` is a declared input).

## What must change first

**1. Substantive — the architecture must close the shebang. (Blocking.)**

§9.2(1)'s reduction must read the artefact's first line. Concretely, the reduction fails (→ `undetermined` → gate)
unless:
- the artefact has no `#!`, **or**
- the `#!` names an **absolute** interpreter path that the OS itself resolves, opens and hashes as part of the
  same `ResolvedExecution`, and that interpreter is not itself a re-exec vector (no `env`, no `-S`).

A relative `#!` path, an `env`-fronted `#!`, or any `#!` naming an unpinned program is a reduction failure.
`memory/profile.rs::shebang` is the starting point (F-4), amended for `-S`. **§15 gains a new assumption only
after the architecture enforces it — disclosure is not sufficient here, because OD-P2-05 clause 1 is normative.**

**2. Substantive — §11's minimum is four changes, not three.** Change 4: for the direct-artefact shape, either
apply the shebang rule or refuse the shape (require a declared interpreter). The headline sentence — *"both
problems reduce to the same three changes"* — must be re-counted before it reaches the owner, because the owner
will quote it.

**3. Correction — Q3 is a precondition, not an open question.** §5 and the Option 1 row must say that P79-F8/F9
are closed for kernel-layout projects and remain open for `gov adopt`'s native layouts until the floor extends to
declared project roots (F-9).

**4. Corrections — arithmetic and attribution.** `LOADER_ENV_VARS` is 30 entries, not 32;
`CLASS_EXEMPTIONS` is 20 lines, not 30; the comparison total is ≈447 and the net deletion ≈−250;
`migrations/executor.rs:714` is a test; "two `run_cmd` call sites" is two of four; complete the `t2.rs` quote
(forgery propagates across the owner's machines); soften "closes neither open HIGH" to "closes no open HIGH's
underlying defect"; change "≈40 lines inside an existing function" to "one function, one struct field, one
retention, one construction site."

**5. Before implementation, not before the owner — one more probe.** A pinned dynamically-linked ELF artefact and
a project-controlled `RUNPATH`/`$ORIGIN`/`LD_*`. Same shape as F-1; `LOADER_ENV_VARS` is stripped on the plugin
path only. Three lines of test, per this study's own standing instruction.

## Where I agree, explicitly

I found no manufactured objection worth making about: the level separation (clean); the dependency declines
(correct, including the hard one — bubblewrap, declined right after a measurement made it easier); the
`class`-is-a-label finding (verified in the code); the Landlock placement (adjudicated, not overruled); the refusal
to reopen the frozen RoT-1 lineage (correct and important); the honesty of §9.4, §10.4, §13 and §15; the refusal to
claim "106 entries deleted"; and the preference for in-repo shipping mechanisms over 2026 preprints. **On the
question the brief said would be most valuable — whether the synthesis relocates complexity — my answer is that it
genuinely removes it, in one place (§15 assumption 3) describes a residual as bounded when it is not, and in one
place (§9) is missing a check that, once added, removes complexity rather than adding it.**

---

## Appendix — evidence I produced

**Probe 1** (`scratchpad/chal/probe1.sh`) — reproduction of the synthesis's §1.2 falsification.
`env -i PATH=/usr/bin:/bin` with cwd pinned to the project root: `env PATH=. true` → project-local `./true` ran;
`env --chdir=decoy sh install.sh` → decoy ran; `/bin/sh <abs>/install.sh` → verified bytes ran. GNU coreutils 9.4,
kernel 6.6.87.2-microsoft-standard-WSL2, unprivileged. **Matches P2-SYN-0001 and the orchestrator exactly.**

**Probe 2** (`scratchpad/chal/fdexec.c`, `probe2.sh`) — §9.2 implemented as specified
(`open(O_PATH|O_NOFOLLOW)`, OS-built `envp`, pinned cwd, `execveat(fd,"",…,AT_EMPTY_PATH)`), attacked five ways:
A `#!./w` → unpinned `./w` ran; A2 same with cwd elsewhere → `ENOENT` (attack requires the OS's own pin);
B `#!/usr/bin/env -S PATH=. sh` → unpinned `./sh` ran; C pinned byte-identical copy of `/usr/bin/env` →
project-local `./true` ran; D symlinked artefact → `ELOOP`, refused (correct); E honest artefact with absolute
`#!` → reviewed bytes ran under the intended interpreter.

Both probes ran unprivileged and wrote only inside the session scratchpad
(`/tmp/claude-1000/…/scratchpad/chal/`). **No repository file was created, modified or deleted by this challenge
other than this document.** Residue disclosed: `chal/{probe1.sh,probe2.sh,fdexec.c,fdexec,t/,proj/,pp.rs,paths.rs,idx.rs}`,
all outside the repository.

**Source claims re-derived independently at `35461c9`, not inherited:** all 41 `.class()` call sites and each
receiver's origin; `PathDecision`'s sole construction site (`paths.rs:710`); `RepositoryContract`'s fields and its
one production construction site (`project.rs:176`); `PolicySet::load`'s `kernel_dir = trust.policy_root`
(`policy.rs:117`) and its `repository_contract_baseline` local (`policy.rs:410`); `Overlay::get`/`set_effective`;
`kernel_trust`'s stated loading boundary; `unreadable_command_shape`, `skip_wrappers`, `classify_file_candidate`,
`looks_like_a_file` in full; the `installation_envelope` entry counts list by list; `LOADER_ENV_VARS` in full;
the ten comparison-machinery function spans; `t2.rs` (`SEALED_RECORD_TYPES`, `verify_file`, `classify_path`, the
symmetric-key paragraph in full); `human_channel.rs:11-16`; `cit/materiality.rs:860-880`; `paths::Exemption` and
`CLASS_EXEMPTIONS`; `framework/overlay-templates/REPOSITORY_CONTRACT.yaml`'s 28 rules; `adopt.rs:1555-1590`;
`repository-contract.schema.json` and `tool.schema.json` (`additionalProperties`, `pinned_files`);
`run_cmd` and its four call sites; `memory/profile.rs::shebang`; the certification fixtures' install-command shapes.

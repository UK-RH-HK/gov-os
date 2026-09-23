# Measured environment facts — orchestrator, 2026-09-23

**Why this file exists.** Several researchers correctly flagged environment-dependent prerequisites as "could not
determine" and asked for direct verification on the target machine. The orchestrator measured them. **These are
measurements, not inferences** — every line below was produced by a command run on the actual deployment machine, and
each is stated with the command that produced it so the synthesiser and challenger can re-run it.

This matters because one of these results **contradicts a researcher's reasoned inference**, and it changes a
recommendation's feasibility.

## The headline correction

**AGENT-5-TOOLING flagged, as its main "could not determine":** whether WSL2 enforces Ubuntu 24.04's AppArmor
restriction on unprivileged user namespaces, which would break bubblewrap- and Nix-sandbox-style tools unless a profile
or sysctl override were applied. It judged there was "strong indirect evidence it does, since the restriction is distro
AppArmor policy not WSL2-specific code", and labelled bubblewrap **contingent** on resolving it.

**Measured: the restriction does not apply on this machine, and unprivileged namespaces work.**

The reasoning was sound but the conclusion was wrong, for a reason the inference could not reach: the restriction is
indeed distro AppArmor policy — and **this kernel does not load AppArmor at all.** WSL2 runs a Microsoft kernel, not
Ubuntu's, so the userland is Ubuntu 24.04 while the kernel is not.

## The measurements

| Fact | Result | Command |
|---|---|---|
| Distro userland | **Ubuntu 24.04.1 LTS (Noble Numbat)** | `grep -E "^(NAME\|VERSION)=" /etc/os-release` |
| Kernel | **6.6.87.2-microsoft-standard-WSL2** | `uname -r` |
| `kernel.apparmor_restrict_unprivileged_userns` | **key absent** | `sysctl kernel.apparmor_restrict_unprivileged_userns` → `No such file or directory` |
| `kernel.unprivileged_userns_clone` | **key absent** | `cat /proc/sys/kernel/unprivileged_userns_clone` |
| AppArmor securityfs | **not present** | `ls /sys/kernel/security/apparmor` |
| `user.max_user_namespaces` | **63589** | `cat /proc/sys/user/max_user_namespaces` |
| **Unprivileged user + mount namespace creation** | **SUCCEEDS** — `uid=0` inside the namespace, mount namespace created | `unshare -Urm --propagation private /bin/sh -c 'id -u'` |
| Landlock kernel symbols | **present** | `grep -q landlock /proc/kallsyms` |
| bubblewrap installed | **no** — `bwrap` not on `PATH` | `command -v bwrap` |
| Physical topology | 8 P-cores + 4 E-cores = **12 physical, 20 threads**; guest presents a synthetic uniform 10×2 | `lscpu`, `/proc/cpuinfo` |

## What follows, and what does not

**Follows:** namespace-based sandboxing (bubblewrap, Bazel-style hermetic actions, Nix's sandbox) is **not blocked by
the prerequisite Agent 5 identified** on this machine. bubblewrap would need installing (`apt install bubblewrap`), but
that is a package, not an obstacle. Landlock is present in the kernel.

**Does not follow — do not over-read this:**

- ~~**Landlock's ABI level is not established here.**~~ **RESOLVED — see below.** AGENT-4-ISOLATION subsequently ran a
  live unprivileged syscall probe on this exact kernel and established the ABI empirically.
- **Namespace creation succeeding is not the same as bubblewrap working.** It is the prerequisite Agent 5 named, and it
  is satisfied; the tool itself is untested here because it is not installed.
- **This is one machine at one moment.** WSL2 kernels update. A recommendation that depends on this should say so and
  should degrade safely if the capability disappears, rather than assuming it persists.
- **Nothing here says sandboxing is the right answer.** It says one specific objection to it does not apply. Agent 4
  owns whether it is warranted at all, and was explicitly told that "none of this yet" is a valid finding.

## Landlock, measured live on this kernel (AGENT-4-ISOLATION, empirical)

Agent 4 compiled and ran an unprivileged C probe against this machine's kernel rather than reasoning from
documentation. Results, which supersede the caveat above:

- **Landlock ABI 3 is supported**, compiled in, and in the kernel's **default-enabled LSM list**. A full
  `create_ruleset → add_rule → restrict_self` cycle succeeded **with no root and no capabilities**, and enforcement is
  real: a denied write returned `EACCES`, as did a denied read outside the granted rule.
- **A genuine trap, found by probing rather than reading**: `LANDLOCK_ACCESS_FS_WRITE_FILE` governs opening an
  *existing* file for write. **It does not cover creating a new file** — that is `MAKE_REG` and siblings. A ruleset
  handling only `WRITE_FILE`/`READ_FILE` therefore leaves **file creation unrestricted everywhere**, which the agent
  confirmed by watching a file get created despite the "denied" write. Any design that reaches implementation must
  enumerate the `MAKE_*` access rights explicitly. **This is precisely the shape of defect that has beaten this project
  five times** — a mechanism whose advertised property is not the property needed — so it is recorded prominently.
- `/dev/kvm` exists but the working user is not in the `kvm` group, so Firecracker and KVM-backed gVisor have an unmet
  precondition. Docker is installed as a conventional **root-owned daemon**; rootless prerequisites are only partial
  (`subuid`/`subgid` present, `newuidmap`/`newgidmap` absent). seccomp, unprivileged user namespaces and cgroup v2 all
  work. **AppArmor is compiled in but runtime-disabled** — consistent with, and explaining, the measurement above.
- bubblewrap, gVisor, Firecracker, wasmtime/wasmer, Nix and Bazel are **none of them installed**; all would be new
  dependencies.
- Still undetermined and flagged rather than guessed: exact kernel versions for Landlock ABI 5+ (sources disagreed);
  whether nested KVM works reliably under this WSL2 configuration; whether AppArmor's disabled state is WSL2-general or
  specific to this machine.

**Residue disclosed:** the probe left one inert 0-byte file, `/tmp/landlock_probe_writetest.txt`, which the agent's own
`rm` restriction prevented it from removing. Harmless, outside the repository, recorded for honesty.

## Verified repository fact — the product already concedes the confinement gap

**AGENT-4-ISOLATION identified `runtime/src/tools.rs` as already admitting the exact gap.** Verified by the
orchestrator; the doc comment reads, verbatim:

> The token and pattern lists in `TOOL_POLICY.installation_envelope` are a **kernel floor, never a safety proof**: the
> OS **cannot confine a spawned process**, so what it cannot observe is carried by the independent governed security
> review the non-gated branch also requires.

**This is the single most important sentence surfaced by the study so far.** The architecture has always known it
cannot confine execution, and compensated by trying to *observe* more — which is exactly what five rounds of
enumeration were. Landlock would change the premise rather than extend the observation: confine the process, instead of
predicting it.

It also means a confinement mechanism would be filling a gap the design *already documents*, not adding an unplanned
capability — which materially lowers the architectural risk of adopting one.

**One category error to avoid**, also flagged by Agent 4 and worth stating for the synthesiser: the existing
`Isolation::Sandbox` (`runtime/src/scheduler/sandbox.rs`) is a **disposable filesystem copy for reproducibility between
concurrent checks — it is not a security boundary.** Nothing prevents a process "inside" it from reading or writing
outside it. Any recommendation that reuses that name must say which of the two things it means.

## Verified repository fact — the floor/local axis already exists

**AGENT-2-GOVERNED-STATE claimed**, from reading the repository, that `REPOSITORY_CONTRACT.yaml`'s schema already
carries the `owner_role`/`mutation` axis needed for a release-sealed floor versus a project-editable local layer, and
that the gap is only that `class`-driven obligations for `product/**` do not respect that existing distinction.

**Verified by the orchestrator.** `framework/overlay-templates/REPOSITORY_CONTRACT.yaml`, lines 13–28, verbatim:

```yaml
  - pattern: "governance/kernel/**"
    class: authoritative
    owner_role: release-agent        # release-owned
    mutation: prohibited             # the floor
  - pattern: "governance/project/**"
    class: authoritative
    owner_role: change-controller    # project-owned
    mutation: restricted             # the local layer
```

**Why this matters more than it looks.** The study's central question for Property C is whether "only authenticated
state has authority" can be implemented at single-owner scale. This shows the **distinction it needs is already
modelled in the product's own schema** — a release-owned prohibited tier and a project-owned restricted tier, already
declared, already enforced for those paths.

So the candidate fix is not "invent a floor/local split". It is "**apply the split the schema already makes to the
authority-bearing `class` axis, which currently ignores it**". That is a substantially smaller and more reversible
change than anything the five repair rounds attempted, and it is the difference between adopting a pattern and
extending one the codebase already commits to.

**The synthesiser should treat this as a load-bearing constraint**, and should say explicitly whether its recommended
architecture builds on this existing axis or replaces it — and if it replaces it, why that is worth the larger change.

## Answering AGENT-3's open repo question — and a new finding it led to

**AGENT-3-EXECUTION listed as "could not determine"**: whether Governance OS has any existing declared-dependency
mechanism to hang a Bazel-style environment allowlist off.

**Answer: yes.** The tool descriptor schema (`framework/schemas/tool.schema.json`) already declares
`permissions`, `required_permission_classes`, `capabilities`, `credential_scope`, `package`, `source`,
`version_pin` and `installation_sha256`. A declared environment allowlist has a natural home in that existing
surface — an installation would declare the variables it needs exactly as it already declares permission classes, and
anything undeclared would be cleared. **This removes AGENT-3's main open obstacle to the Bazel
`--incompatible_strict_action_env` pattern**, which it recommended as ADAPT / REQUIRED NOW.

### The finding that came out of checking

Verified on the reviewed tree `35461c9`:

| | Result |
|---|---|
| `pinned_files` occurrences in `runtime/src/tools.rs` | **7** |
| `pinned_files` occurrences in `framework/schemas/tool.schema.json` | **0** |
| Top-level `additionalProperties` in that schema | **absent** (so undeclared fields are permitted) |

**`pinned_files` is the field that carries the entire "bind the bytes" guarantee of OD-P2-05 — and the schema does not
describe it at all.** Nothing validates its presence, its shape or its types; the schema does not even forbid unknown
fields.

This is the same defect class one field over from **AR73-F4**, where `installation_sha256` being absent, `null` or a
*number* each had to be caught by hand-written runtime checks precisely because the schema does not constrain it. It is
also another instance of the study's central pattern: **the check reasons about a representation that is itself
unvalidated.**

Recorded as a new observation for the synthesiser and for the formal verifier. It is **not** in scope for this
read-only study to fix, and it does not by itself constitute a proven exploit — but any recommendation that leans on
descriptor-declared data (which every Property A option does) should say whether it also requires that data to be
schema-constrained.

## ★ The most consequential finding — P79-F10 is WRONG, and the mechanism already exists

**AGENT-6-CHALLENGER claimed** that `runtime/src/cit/binding.rs` already implements the exact pattern P79-F10 says the
product lacks, and that it has simply never been applied to `REPOSITORY_CONTRACT.yaml`. **Verified by the orchestrator
on the reviewed tree `35461c9`.** This is a direct correction to a finding the escalation package treated as an
architectural blocker.

**P79-F10 stated** — and the orchestrator repeated it to the owner — that *"the product has no mechanism anywhere to
distinguish a governed contract change from a hand edit"*, and that Property C therefore could not be completed without
first building one. The reviewer was careful to say its search was **"targeted, not exhaustive"**. It missed this.

### What already exists, from the module's own documentation

`runtime/src/cit/binding.rs` seals an `os_state` block with the machine binding key, carrying digests rather than
copies — including `binding_sha256`, described as *"what a Human Decision Gate raised for this CIT carries as
`subject.sha256`, so the owner signs exactly this transaction and impact."* And then, decisively:

> **Consumers never trust the record's top-level fields for an authority decision**: approve and execute recompute the
> digests from the record as it stands and compare them with the sealed block; **a hand-edited manifest, impact,
> approval, gate reference or status is therefore refused, typed**, at approve and at execute.

> [`seal`] also T2-seals the **whole record** … **A hand edit of any field breaks the whole-record seal**, and no CIT
> operation blesses it.

That is, precisely: *only authenticated state has authority; a hand edit is inert and refused.* It is the pattern
AGENT-2 independently identified as the mature answer, already implemented, already shipping, already carrying an
owner signature through a Human Decision Gate.

### And the primitive is general, not CIT-specific

| Fact | Evidence (`35461c9`) |
|---|---|
| `t2::seal_value` / `t2::seal_record` / `t2::verify_record` | **public, general-purpose** functions in `runtime/src/t2.rs` |
| Record types sealed **today** | `SEALED_RECORD_TYPES = ["human-gate", "cit", "task"]` |
| Is the path map among them? | **No.** |

**So extending this to `REPOSITORY_CONTRACT.yaml` is adding a fourth member to an existing closed list, not inventing a
mechanism.**

### Why this changes the owner's decision materially

The Option B escalation package put to the owner that Property C faced a prerequisite — build a way to tell a governed
change from a hand edit — and that everything else about C depended on settling it. **That prerequisite appears already
satisfied by existing, shipped, owner-signed machinery.** Combined with the separately verified fact that the schema
already carries the `owner_role`/`mutation` floor/local axis, Property C now looks like **two mechanisms the product
already has, applied to one more file** — rather than new architecture, a new dependency, or a deferred decision.

**The synthesiser must treat this as load-bearing**, must verify it independently rather than inherit it, and must say
explicitly whether its Property C recommendation builds on `t2`/`cit::binding` or proposes something else — and if
something else, why that is worth more than extending a mechanism already carrying owner signatures in production.

**And the orchestrator must correct the owner**, since it relayed P79-F10's framing as a blocker. That correction is
owed regardless of what the synthesis concludes.

## ★★ The orchestrator's own recommendation to the owner was wrong — reproduced by hand

`PHASE_2_OPTION_B_ESCALATION_PACKAGE.md` §6 recommended, and the orchestrator told the owner, that:

> Clearing the environment to a controlled allowlist, pinning the working directory so it cannot be overridden, and
> executing the verified artefact by resolved absolute path, would close both [P79-F1 and P79-F11].

**P2-SYN-0001 falsified this by measurement. The orchestrator then reproduced it independently.** Run on this machine,
with a **fully cleared** environment (`env -i PATH=/usr/bin:/bin` — strictly stronger than an allowlist) and the
working directory pinned to the project root:

| Attack, under a cleared environment and pinned cwd | Result |
|---|---|
| `env --chdir=decoy sh install.sh` (P79-F11) | **`DECOY-SCRIPT-RAN`** — still succeeds |
| `env PATH=. true` (P79-F1) | **`PROJECT-LOCAL-TRUE-RAN`** — still succeeds |
| *control:* `/bin/sh <abs>/install.sh` | `REAL-VERIFIED-SCRIPT` — correct |

**Two of the three limbs do nothing.** The reason is embarrassing once seen: **`env` is not an environment variable, it
is a program the OS chooses to execute**, and `PATH=.` and `--chdir=` are *arguments to that program*, applied by it
inside the child **after `gov` has already lost control**. No environment `gov` constructs survives a program whose
entire job is to construct a different one. Pinning the cwd is defeated the same way.

**Only the third limb works** — and it is the one the package stated least precisely. The correct property is not
"control the environment" but:

> **Do not execute the wrapper chain at all. Resolve to the artefact and execute the object.**

### Why this belongs in the permanent record, not just the report

This is **the study's own thesis recurring inside the study**. Six researchers, the escalation package, and the
orchestrator all inherited the common brief's framing of P79-F1 as an *environment* defect. It is a *wrapper-execution*
defect. The check — here, a recommendation — reasoned about a representation (the environment) while the effect came
from somewhere the representation did not cover (an argument to a program).

The orchestrator relayed this to the owner as its own recommendation, with confidence, **without running the two
commands that disprove it** — a three-line test. That is the same failure this session has now recorded three times in
others and twice in itself, and it is the strongest available argument for the standing instruction below.

**Consequence for the owner-facing report:** the escalation package's §6 recommendation must be marked **superseded**,
and the correction must be stated plainly rather than folded silently into a new recommendation. The owner made a
decision partly on that recommendation's strength.

## Standing instruction for the synthesis

Where a researcher marked something "could not determine" **about this machine**, prefer measuring it over reasoning
about it. Where a measurement contradicts an inference, the measurement wins and the inference should be recorded as
corrected rather than quietly dropped — this session has already had two cases where a confident, well-reasoned
inference was falsified by a direct measurement that had been argued unnecessary.

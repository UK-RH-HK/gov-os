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

## Standing instruction for the synthesis

Where a researcher marked something "could not determine" **about this machine**, prefer measuring it over reasoning
about it. Where a measurement contradicts an inference, the measurement wins and the inference should be recorded as
corrected rather than quietly dropped — this session has already had two cases where a confident, well-reasoned
inference was falsified by a direct measurement that had been argued unnecessary.

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

- **Landlock's ABI level is not established here.** Symbols being present says the feature is compiled in, not which
  ABI version. Landlock's capabilities differ materially by version (filesystem scope, truncation, and network
  restrictions arrived in different ABIs), and kernel 6.6 does not have the newest. **The synthesiser must not assume a
  specific Landlock ABI without checking it**, and no recommendation should depend on an unverified ABI level.
- **Namespace creation succeeding is not the same as bubblewrap working.** It is the prerequisite Agent 5 named, and it
  is satisfied; the tool itself is untested here because it is not installed.
- **This is one machine at one moment.** WSL2 kernels update. A recommendation that depends on this should say so and
  should degrade safely if the capability disappears, rather than assuming it persists.
- **Nothing here says sandboxing is the right answer.** It says one specific objection to it does not apply. Agent 4
  owns whether it is warranted at all, and was explicitly told that "none of this yet" is a valid finding.

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

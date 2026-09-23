# Research Agent 4 — Sandboxing and Isolation (Level 3 prior art)

Scope per dispatch: process sandboxing, filesystem isolation, network isolation, syscall restriction, Linux
capabilities, namespaces, seccomp-bpf, Landlock, containers/rootless containers, bubblewrap, gVisor, Firecracker/
microVMs, WASI/WebAssembly, VM isolation, hermetic/reproducible builds, remote execution sandboxes.

**Read-only research. No product code touched.** One empirical departure from pure literature review: because the
brief demands "check this specifically, do not assume" for Landlock-under-WSL2, I compiled and ran a small,
self-contained C probe against this exact machine's kernel (unprivileged, no product code, files written only to
the session scratchpad and to `/tmp` — none left behind). That evidence is marked **[EMPIRICAL, this machine]**
throughout and is stronger than anything I could cite second-hand. Everything else is cited from primary sources.

---

## 0. Headline answer

For the stated deployment profile (one owner, WSL2, offline, no cluster, no daemon wanted), almost everything in
this study's catalogue is oversized. **Exactly one candidate clears the bar as more than "useful later": Landlock,
used narrowly as an unprivileged filesystem-write backstop around the small number of call sites that already spawn
external processes.** Everything else — containers, gVisor, Firecracker, WASM/WASI, VM isolation, remote execution
— is real, well-documented technology solving a real problem, but not *this* problem, at *this* trust level, on
*this* machine. Detail and evidence follow.

Also, and this matters more than any single tool verdict: **isolation does not touch either of the two problem
classes in the brief.** It can shrink the blast radius of *where* an effect lands. It cannot establish *which
artifact ran* (2B) or *whether authority was legitimately granted* (2A/2C). Section 6 works this through against the
actual defect ids, because the discipline the owner asked for — not letting Level 3 quietly answer a Level 2
question — is easiest to violate exactly at the point where isolation looks like it would have helped.

---

## 1. What's already in the repository — the existing seam

Two things already exist and matter for "does this fit a seam we have" (owner's question 3):

**`Isolation::Sandbox` (`runtime/src/scheduler/catalogue.rs:55-63`, `runtime/src/scheduler/sandbox.rs`).** This is
*not* a security sandbox. It is a **disposable filesystem copy**: `Sandbox::create` copies every file
`iter_repo_files` would read into a fresh directory under the project's runtime dir, optionally copies the derived
DB/claims stores, optionally `git init`s it, and the check then runs against that copy instead of the live tree
(`runtime/src/scheduler/mod.rs:538-556`). Its purpose, per its own doc comment, is Contract v3:804 reproducibility
— "isolated worktrees/processes where required" — so that a check which writes derived state doesn't race or
corrupt the live repository. Nothing about it is kernel-enforced: a check running "inside" this sandbox can still
read or write anywhere the OS-level process can, including outside the sandbox directory. It is a convention, not a
boundary. That is an accurate and sufficient design for its stated purpose (reproducibility isolation between
concurrent checks) and a **materially different problem** from confining a lower-trust process (adversarial
isolation). Conflating the two would be a category error worth naming explicitly if anyone proposes "we already
have sandboxing."

**`runtime/src/capabilities/host.rs::invoke()`** is the actual external-execution call site: it builds a
`std::process::Command`, applies a loader-variable allowlist (`apply_plugin_env`, `binding::LOADER_ENV_VARS`,
BC-P2-40) so no caller-controlled `LD_PRELOAD`-shaped variable substitutes code, sets `process_group(0)` for clean
teardown, and spawns. This is the "controlled `execve`" the dispatch prompt gestures at — curated argv, curated env,
curated cwd. It is also, by the codebase's own admission, incomplete on exactly the axis this research covers.
`runtime/src/tools.rs:892-897` states it directly:

> "The token and pattern lists in `TOOL_POLICY.installation_envelope` are a **kernel floor, never a safety proof**:
> **the OS cannot confine a spawned process**, so what it cannot observe is carried by the independent governed
> security review the non-gated branch also requires."

That sentence is the precise gap this study was commissioned to look at. It is also precisely scoped: it says the
OS cannot confine a spawned process's *effects*. It does not say (and Landlock would not fix) the separate problem
that the OS may be wrong about *which bytes* that spawned process runs (P79-F11) — see §6.

---

## 2. Empirical findings on the actual deployment machine

Run directly on this machine (`uname -r`: `6.6.87.2-microsoft-standard-WSL2`), unprivileged, uid=1000, no sudo, no
product code changed:

| Check | Result |
|---|---|
| `CONFIG_SECURITY_LANDLOCK` (`/proc/config.gz`) | `y` — compiled in |
| `CONFIG_LSM` boot list (`/proc/config.gz`) | `landlock,lockdown,yama,loadpin,safesetid,integrity,selinux,apparmor,tomoyo` — Landlock is in the **default-enabled** LSM stack, not something that has to be turned on |
| Live ABI query (`landlock_create_ruleset(NULL,0,LANDLOCK_CREATE_RULESET_VERSION)`, syscall 444) | **ABI 3 supported**, unprivileged |
| Ruleset create → add rule (`READ_FILE` under `/tmp` only) → `landlock_restrict_self` | **All three syscalls succeeded, unprivileged, no `CAP_SYS_ADMIN`** |
| Post-restrict: open `/tmp/x` for write (right not granted) | **Denied, `EACCES`** — enforcement is real, not advisory |
| Post-restrict: read `/etc/hostname` (outside the one granted rule, but `READ_FILE` is a *handled* right globally) | **Denied, `EACCES`** — confirms Landlock's deny-by-default-within-handled-rights model |
| `/sys/kernel/security/lsm`, `/sys/kernel/security` (securityfs) | Not mounted in this WSL2 session. **Irrelevant to Landlock** — the three Landlock syscalls need no securityfs mount; they worked regardless. (Tools that *introspect* LSM state via securityfs, e.g. some AppArmor tooling, would not work here.) |
| `unshare --user --map-root-user` | Succeeds unprivileged — user namespaces work under this WSL2 kernel |
| `CONFIG_SECCOMP`, `CONFIG_SECCOMP_FILTER` | Both `y` — seccomp-bpf fully available |
| `/sys/module/apparmor/parameters/enabled` | `N` — AppArmor is compiled into the LSM list but **disabled at runtime** on this machine |
| `/dev/kvm` | Present, group `kvm`, but the working user is **not a member** — `open()` returns `EACCES`. KVM-backed tooling (Firecracker, gVisor's KVM platform) would need a privileged one-time `usermod -aG kvm` step this profile doesn't currently have |
| `cgroup2` | Mounted at `/sys/fs/cgroup`, unified hierarchy — modern container tooling's prerequisite is met |
| `newuidmap`/`newgidmap` | **Not installed** (would need the `uidmap` package), even though `/etc/subuid` and `/etc/subgid` already have a range for the user. Rootless Podman/Docker is not ready out of the box |
| `docker` | **Already installed and running** as a conventional root-owned daemon (`dockerd` PID owned by `root`, socket `root:docker 0660`). Default runtime is plain `runc` — no gVisor runtime registered. Membership in the `docker` group (already present for this user) is a well-documented root-equivalence, not a sandboxing improvement |
| `podman`, `bwrap`, `runsc` (gVisor), `firecracker`, `wasmtime`/`wasmer`, `nix`, `bazel` | **None installed.** All would be new dependencies, not tools already on the machine |

Two conclusions follow directly from the table, not from any vendor claim:

1. **Landlock works fully, unprivileged, offline, under this exact WSL2 kernel.** This was the one point the
   dispatch explicitly said not to assume, and it checks out empirically rather than by inference from "WSL2 is a
   real kernel."
2. **A container/VM daemon is not free on this machine — it is either already a root-owned liability (Docker) or
   an unmet prerequisite (rootless Podman needs a package install; KVM-backed tooling needs a group membership
   change).** None of that is disqualifying in principle, but none of it is "just use what's there" either.

One empirically-discovered subtlety belongs here because it is a genuine trap for anyone implementing this later,
not a general Landlock fact I could have gotten from documentation alone: **`LANDLOCK_ACCESS_FS_WRITE_FILE` governs
opening an *existing* file for writing. It does not govern *creating* a new file — that is the separate
`LANDLOCK_ACCESS_FS_MAKE_REG` right (and its siblings `MAKE_DIR`, `MAKE_SYM`, `MAKE_FIFO`, …).** In my first probe
run, a ruleset that handled only `WRITE_FILE | READ_FILE` did not stop file *creation* outside the allowed
subtree — the kernel allowed `open(O_CREAT|O_WRONLY)` to create the file (because `MAKE_REG` was not in
`handled_access_fs`, so that right was simply un-restricted, not denied) and only then denied the subsequent write.
A naive "confine writes to the project root" ruleset that omits the `MAKE_*` family, `REMOVE_*`, and `REFER`
rights would leave file creation everywhere on the filesystem completely open — silently. This is exactly the kind
of enumeration trap the brief warns about, just relocated one layer down: Landlock's rights are individually
opt-in, and getting the *set* right is the part that needs care, not the mechanism itself. (Kernel docs, §3.1
below, confirm this is documented behavior, not a bug I tripped over; I only confirmed it holds here.)

---

## 3. Per-candidate record

For each: property provided / not provided, trust assumptions, maturity, licence, platform, offline, root?,
WSL2?, complexity, TCB delta, fit.

### 3.1 Landlock

- **What it provides**: An unprivileged Linux Security Module letting a process restrict its own and its
  descendants' filesystem (and, at higher ABI, network) rights, enforced by the kernel, deny-by-default *within
  the set of rights the ruleset declares it handles*. "Landlock's goal is to enable to restrict ambient rights...
  for a set of processes" and it "empowers any process, including unprivileged ones, to securely restrict
  themselves" (kernel docs). [docs.kernel.org/userspace-api/landlock.html]
- **What it does not provide**: It is scoped to filesystem and (ABI ≥4) TCP network actions. The kernel's own
  manual page lists syscalls it currently cannot restrict: `chdir(2)`, `stat(2)`, `flock(2)`, `chmod(2)`,
  `chown(2)`, `setxattr(2)`, `utime(2)`, `fcntl(2)`, `access(2)` [man7.org/linux/man-pages/man7/landlock.7.html].
  It does not mediate file descriptors already open before the ruleset is applied. It does not restrict mount
  operations or `pivot_root`. It does not propagate through OverlayFS layers (each layer and the merge are
  independent) [man7.org/linux/man-pages/man7/landlock.7.html]. It has **no opinion on which bytes execute for a
  given path** — it can allow or deny *execute* on a path, but cannot verify a path's content against a hash;
  that is not its job and it does not claim it.
- **ABI history** (corroborated across kernel docs and the Rust crate's own ABI enum; only V1–V4 are
  cross-confirmed by two independent sources plus my own probe, so treat V5+ kernel-version numbers as
  **not fully verified** — the two sources I fetched disagreed on them):
  - **V1 — Linux 5.13**: initial filesystem rights (execute/read/write/create/remove/…).
  - **V2 — Linux 5.19**: `LANDLOCK_ACCESS_FS_REFER` (link/rename across directories).
  - **V3 — Linux 6.2**: `LANDLOCK_ACCESS_FS_TRUNCATE`.
  - **V4 — Linux 6.7**: network rights, `LANDLOCK_ACCESS_NET_BIND_TCP` / `CONNECT_TCP`.
  - V5+ (ioctl-on-device restriction, scoped signals/abstract sockets, multi-thread sync, UDP, logging
    controls) exist in more recent kernels per the crate's ABI enum, but I could not pin exact kernel-version
    numbers to a primary source I trust; **I could not determine this precisely** and flag it rather than guess.
  - **This machine's kernel (6.6.87.2) reports ABI 3 live**, which is internally consistent with the V3=6.2 /
    V4=6.7 mapping (6.6 is ≥6.2 and <6.7) — the empirical result cross-validates the cited table for the range
    that matters here. **Network-layer Landlock (ABI 4) is not available on this exact kernel.**
- **Trust assumptions**: trusts the kernel (already in the profile's trust boundary) and nothing else. No
  daemon, no setuid binary, no additional process. A restricted process cannot un-restrict itself (Landlock
  domains only ever narrow, and `no_new_privs` plus the kernel's own enforcement prevent a `setuid` execve from
  escaping — this is the LSM's whole design point).
- **Maturity / maintenance**: Upstream Linux kernel LSM since 5.13 (2021), authored by Mickaël Salaün (ANSSI),
  still gaining ABI versions in recent kernels — active, first-party, not a third-party add-on.
- **Rust crate**: `landlock` (crates.io / `docs.rs/landlock`), hosted under the official `landlock-lsm` GitHub
  org, maintained by the same author as the kernel feature (`l0kod`) — about as close to "the reference binding"
  as a crate gets. Dual MIT/Apache-2.0. MSRV 1.71. Provides a `Ruleset`/`Compatible` builder API that degrades
  gracefully on older kernels (ask for what you want; the crate tells you what the running kernel actually
  granted) rather than requiring the caller to branch on ABI numbers by hand. [docs.rs/landlock,
  landlock.io/rust-landlock]
- **Licence**: kernel feature is GPL-2.0 (irrelevant to a userspace caller); crate is MIT/Apache-2.0.
- **Platform**: Linux only, kernel ≥5.13 for any version, ABI negotiated up from there. **Confirmed working on
  WSL2 6.6.87.2, empirically, unprivileged, this session** (§2). Does not exist on WSL1 (no real Linux kernel to
  host an LSM).
- **Offline**: yes — no network access of any kind is involved; it is pure syscalls.
- **Root required**: **no** — this is the entire point of the feature, and I verified it directly (uid=1000,
  no capabilities).
- **Operational complexity**: very low. No daemon, no service to keep running, no config file format to design —
  a ruleset is built and applied in-process, once, typically right before `exec`.
- **Integration complexity**: low-to-moderate. The natural integration point is a `pre_exec` closure on the
  `std::process::Command` already built in `host.rs::invoke()` (via `CommandExt::pre_exec`, itself an existing,
  well-understood Rust std API — `command.process_group(0)` in that same function already uses the `unix`
  extension trait), calling `landlock_restrict_self` in the child after fork, before exec. Getting the *rights
  enumeration* right (§2's `MAKE_REG` trap) is the actual work, not the plumbing.
- **Performance impact**: negligible — a handful of syscalls at process start; per-syscall enforcement overhead
  is a kernel-internal rule lookup, not something a single-owner workload would notice.
- **Fit for this profile**: strong. It is the only mechanism in this catalogue whose cost (one small,
  officially-maintained crate, no daemon, no privilege) is proportionate to the specific defect class
  (AR77-F1/F2/F4, P79-F1's write/execute surface) it would close.

### 3.2 Linux namespaces (mount, PID, network, UTS, IPC, user, cgroup, time)

- **What they provide**: Per-resource *views* — a mount namespace gives a process its own filesystem mount
  table, a network namespace its own interfaces/routes, a PID namespace its own process-ID space, a user
  namespace its own UID/GID mapping (the one that makes all the "unprivileged" tooling below possible at all).
  [man7.org/linux/man-pages/man7/namespaces.7.html; man7.org/linux/man-pages/man7/user_namespaces.7.html]
- **What they don't provide**: A namespace changes what a process *can see*, not what it's *allowed to do* within
  what it sees — namespaces are not a permission system by themselves. An unshared mount namespace with nothing
  bind-mounted into it is not a filesystem restriction; it's an empty view that then needs mounts populated
  correctly, which is exactly the composition work bubblewrap does (§3.4).
- **Trust assumptions / root**: **unprivileged user namespaces confirmed working on this machine** (`unshare
  --user --map-root-user` succeeded as uid 1000, §2). This is the load-bearing primitive under bubblewrap,
  rootless Docker/Podman, and (partly) gVisor.
- **Maturity**: core kernel feature since ~2013 (user namespaces stabilized), extremely mature, no maintenance
  burden of its own — it's kernel ABI, not a library.
- **Fit**: not something Governance OS would call directly; it's the foundation other tools in this list are
  built on. Calling `unshare(2)`/`clone(2)` flags directly to hand-roll a sandbox is exactly the "BUILD CUSTOM
  when a mature primitive exists" anti-pattern the brief warns against — bubblewrap already is that composition,
  maintained, fuzzed, and used by Flatpak in production for years.

### 3.3 seccomp-bpf

- **What it provides**: A BPF program evaluated against every syscall a process makes (number + architecture +
  arguments), returning allow/deny/trap/kill/log per call. `CONFIG_SECCOMP_FILTER` confirmed present and enabled
  on this kernel (§2).
- **What it doesn't provide**: It restricts *which syscalls* run, not *what those syscalls do* — `openat()`
  allowed with no path filtering still opens anything. Argument filtering exists but is brittle for path-shaped
  arguments (seccomp inspects raw pointers/integers, not resolved strings, so it cannot safely say "only allow
  `openat` under `/project`" the way Landlock can). This is precisely why Landlock exists as a *separate* LSM
  layered on top of, not instead of, seccomp — they answer different questions ("which syscall" vs "which
  path/resource").
- **Trust assumptions**: kernel only, unprivileged with `no_new_privs` set (same precondition as Landlock).
- **Maturity**: mainline since Linux 3.5 (2012), used by every major container runtime (`runc`'s default
  profile), Chrome, Firefox — extremely mature.
- **Fit**: valuable as defense-in-depth (block whole syscall *families* Governance OS never needs — e.g.
  `ptrace`, module loading, raw sockets) but the specific defect class in this brief (writes/execs landing
  outside the project root) is a *path* question, which is Landlock's job, not seccomp's. Building and
  maintaining a bespoke seccomp-bpf policy (an allowlist of ~300 possible syscalls, arch-dependent, ABI-fragile
  across kernel versions) is real ongoing maintenance burden for a benefit narrower than Landlock's for this
  specific problem.

### 3.4 bubblewrap (`bwrap`)

- **What it provides**: A userspace tool that *composes* mount namespaces, user namespaces, PID/IPC/UTS/network
  namespaces and (optionally) seccomp into a working sandbox, unprivileged. "Historically, bubblewrap also
  supported a setuid mode... this has been removed" — current versions are pure unprivileged-userns.
  [github.com/containers/bubblewrap]
- **What it doesn't provide**: bubblewrap's own documentation is explicit that it is a *construction kit*, not a
  policy: "the level of protection between the sandboxed processes and the host system is entirely determined by
  the arguments passed to bubblewrap." It ships no default policy at all — a misconfigured invocation (e.g.
  bind-mounting `/` read-write "to be safe") provides zero isolation. That burden lands entirely on whoever
  writes the flag list, which is real, ongoing, security-relevant maintenance.
- **Maturity**: mature, actively maintained, 8.8k GitHub stars, the isolation layer under Flatpak and
  rpm-ostree — real production track record. [github.com/containers/bubblewrap]
- **Offline / root / WSL2**: offline yes; **not installed on this machine** (§2) — would be a new binary
  dependency (small, ~1 static-ish binary, C, no daemon) but still something to fetch, verify, and pin, which
  the brief's offline/no-new-trusted-binary bar should weigh; unprivileged-userns is confirmed working here so
  it would function once installed.
- **Fit**: this is the right *shape* of tool if Governance OS ever needs to run an entire untrusted subprocess
  tree (not just confine one exec's filesystem effects) with process/PID/network isolation as well as
  filesystem. For the specific defect class in §6 (filesystem effect confinement around one `Command::spawn`),
  it is more machinery than the problem needs: a whole new external binary dependency, a hand-written flag
  policy to get right and keep right, versus one small Rust crate calling three syscalls already available in
  the kernel. It is the right answer for a *broader* isolation need than currently exists in the codebase.

### 3.5 Linux capabilities (`capabilities(7)`)

- **What they provide**: Decomposition of root's monolithic privilege into ~41 independent bits (`CAP_NET_ADMIN`,
  `CAP_SYS_ADMIN`, `CAP_DAC_OVERRIDE`, …), settable per-process or per-file, droppable so a process that starts
  privileged can shed exactly the bits it no longer needs. [man7.org/linux/man-pages/man7/capabilities.7.html]
- **What they don't provide**: relevance only to processes that *have* elevated privilege in the first place. I
  confirmed by grep that Governance OS never elevates (`sudo`, `setuid`) itself — the one reference in the
  codebase (`runtime/src/tools.rs:892`) is about *detecting* a plugin installer that invokes `sudo`, not about
  Governance OS doing so. For an owner-run, always-unprivileged process, the *ambient* capability set is already
  empty; there is nothing to drop that matters.
- **Fit**: essentially N/A to the current architecture. Would become relevant only if Governance OS ever spawned
  something that legitimately needs one narrow elevated right (rare, and arguably a smell if it happens) — at
  which point capability-dropping on that one spawn (again via `pre_exec`) would be the correct minimal response,
  not a general capabilities program. **HIGH-ASSURANCE ONLY, and only conditionally even there.**

### 3.6 Containers / rootless containers (Docker, Podman)

- **What they provide**: namespace + cgroup + (usually) seccomp + capability-drop composition, packaged with
  image management, orchestrated by a runtime (`runc`/`crun`) and usually a daemon.
- **What they don't provide, here specifically**: the deployment profile explicitly wants daemonless. Standard
  Docker is a **root-owned daemon** — confirmed running as such on this exact machine (`dockerd` PID owned by
  `root`, socket group `docker`). Membership in the `docker` group (already granted to this user, incidentally)
  is documented as root-equivalent, since a container can bind-mount the host filesystem. Using Docker as a
  Governance OS isolation primitive would mean *depending on* a pre-existing root-owned service whose access
  control (`docker` group) is coarser than the guarantee being sought.
- **Rootless mode exists** (Docker rootless, Podman) — daemon (or daemonless, for Podman) runs entirely as the
  unprivileged user, using user namespaces + `newuidmap`/`newgidmap` to map a wider UID range. Requirement:
  kernel ≥5.11 (or ≥4.18 with userns enabled) [docs.docker.com/engine/security/rootless] — met here. **But**:
  `newuidmap`/`newgidmap` are **not installed** on this machine even though `/etc/subuid`/`/etc/subgid` ranges
  already exist for the user (§2) — an extra package install (`uidmap`) is a precondition not currently met.
  Podman is not installed at all.
- **Maturity**: both extremely mature, industry-standard, large communities. Not a maintenance risk in
  themselves; the risk is architectural (daemon dependency, image-management surface, a much larger TCB than
  the problem needs) not a quality risk.
- **Fit**: wrong shape for a single always-local, offline, single-owner tool. Even rootless mode brings image
  layering, a container runtime, and (for Docker) systemd `--user` service management — solving problems
  (multi-tenant isolation, distribution, orchestration) Governance OS does not have, at a TCB and operational
  cost the defect list does not justify. **HIGH-ASSURANCE ONLY** (and even then, Podman rootless would be the
  candidate to revisit, not Docker with an already-root daemon sitting on this machine).

### 3.7 gVisor

- **What it provides**: A userspace "application kernel" (Sentry) written in Go that intercepts and services
  syscalls itself rather than passing them to the host kernel, with a separate Gofer process mediating
  filesystem access over 9P; ships as the OCI-compatible `runsc` runtime for Docker/Kubernetes. Positioned as "a
  distinct third approach" between full VMs and syscall filtering, aiming for "many of the security benefits of
  VMs" with lower overhead than a VM. [gvisor.dev/docs]
- **What it doesn't provide (here)**: it is a **container runtime**, not a library Governance OS could call —
  adopting it means adopting a container runtime first (§3.6's cost), *then* swapping its execution engine, for
  workloads (arbitrary install scripts) it was not designed to make faster or simpler. Not installed on this
  machine; not on the default runtime list of the Docker install that *is* here (`runc` only, §2).
  Ptrace-platform gVisor is markedly slower per-syscall than native; KVM-platform gVisor needs `/dev/kvm`, which
  exists on this machine but **the working user cannot access it** (§2) without a privileged group-membership
  change.
- **Maturity**: Google-maintained, open source, real production use (GKE Sandbox) — mature and well-documented,
  not a risk in itself.
- **Fit**: solves *hostile multi-tenant* isolation (mutually distrusting workloads on shared infrastructure).
  Governance OS's stated threat model is "lower-trust input on an owner-controlled machine," not hostile
  co-tenants. This is squarely **HIGH-ASSURANCE ONLY**, and even there it is a heavier answer than the
  microVM alternative for a single-owner box.

### 3.8 Firecracker / microVMs

- **What it provides**: A minimal VMM (Rust) built on KVM, purpose-built for fast-booting, low-overhead
  microVMs — "boot in <125ms," "<5 MiB overhead per VM," designed for dense multi-tenant serverless (AWS Lambda
  is the canonical deployer). [firecracker-microvm.github.io]
- **What it doesn't provide (here)**: **hard requirement on `/dev/kvm` and hardware virtualization.** Confirmed
  present as a device node on this WSL2 machine, but **not accessible to the working user** (no `kvm` group
  membership) — meaning even the prerequisite is not currently met without a privileged setup step. More
  fundamentally, WSL2 itself already runs inside a lightweight Hyper-V VM; whether nested KVM-in-Hyper-V is
  reliable and supported here is a real open question I could not resolve — the official docs I fetched say
  nothing about nested/non-bare-metal hosts, and I would not assert either way without a source. **I could not
  determine whether Firecracker is reliably usable inside this specific WSL2 configuration even after the group
  membership gap is closed.**
- **Fit**: purpose-built for a threat model (many mutually-distrusting tenants sharing a fleet, needing
  sub-second cold starts) that is the opposite of one owner's single always-on machine. Clearly
  **HIGH-ASSURANCE ONLY**, and likely not even the first HIGH-ASSURANCE choice for this profile given the
  KVM-access uncertainty just noted.

### 3.9 WASI / WebAssembly isolation

- **What it provides**: A capability-based sandbox at the *language-runtime* level — a Wasm module has no
  ambient authority at all; the host must explicitly grant filesystem preopens, socket capabilities, etc. "A Wasm
  module or component starts with no ambient authority and can only do what the host explicitly grants."
  [wasi.dev] As of this research (per multiple 2026 secondary sources, not independently verified against a
  W3C/Bytecode Alliance primary source): WASI 0.2 stable, 0.3 released with native async, 1.0 expected
  late 2026/2027.
- **What it doesn't provide (here)**: this is an isolation model for code *compiled to WebAssembly*. Governance
  OS's actual execution problem (§6) is running arbitrary project-supplied shell scripts, installers, and
  interpreters — `install.sh`, `curl`, Python, `sh` — none of which are Wasm binaries and none of which anyone
  is proposing to recompile to Wasm. Using WASI here would mean either (a) restricting Governance OS to only
  execute pre-vetted Wasm-compiled tools, which is a different and much larger product decision than anything in
  this defect list, or (b) running a general-purpose Wasm engine (wasmtime/wasmer — **neither installed on this
  machine**, both meaningful new dependencies with their own CVE surface) as a compatibility shim, which adds
  TCB without removing the actual attack surface (the interpreter still runs native, off to the side). Not
  applicable to the concrete defects. **HIGH-ASSURANCE ONLY, and only for a hypothetical future where the
  executed artifacts are Wasm-native — not a fit for the current execution model at all.**

### 3.10 VM isolation (general — full VMs, not microVMs)

- **What it provides**: hardware-mediated isolation via a hypervisor; the strongest boundary in this catalogue.
- **What it doesn't provide (here)**: heavyweight — full guest OS, minutes not milliseconds to provision by
  comparison to the above, meaningful disk/memory footprint, and (per the deployment profile) "no
  hardware-security assumptions established" for this WSL2 host, which already *is* a VM (Hyper-V) — nesting
  another one is exactly the KVM-access question raised in §3.8, unresolved here.
- **Fit**: **HIGH-ASSURANCE ONLY**, and arguably subsumed by Firecracker/gVisor as better-fitted implementations
  of the same idea if this level is ever needed.

### 3.11 Hermetic / reproducible build environments (Nix, Bazel sandboxed actions)

- **What it provides**: A different property than adversarial isolation — *reproducibility*: "a build is
  hermetic if it is not affected by details of the environment where it is performed... a prerequisite for
  remote caching and remote execution." [bazel.build/basics/hermeticity] Bazel enforces this partly via
  sandboxing (each action runs in an execroot containing only its declared inputs, so a compiler "cannot
  accidentally read random files on the host or reach out to the network by accident") — filesystem confinement
  in service of *correctness*, not adversarial defense. Nix achieves the same property differently: pinned,
  content-addressed dependency closures rather than per-action sandboxing.
- **What it doesn't provide**: neither is designed to contain a *hostile* input; Bazel's sandbox exists so a
  well-behaved build doesn't accidentally depend on ambient machine state, not to stop a malicious build target.
  A determined adversarial build action inside Bazel's sandbox is bounded by the same underlying namespace/mount
  mechanics as everything else in this document, not by anything Bazel adds on top.
- **Relevance to this brief**: interesting mainly as a **pattern**, not a component to adopt: it's a second,
  independent confirmation that "confine an action to its declared inputs/working directory via
  namespaces/bind-mounts" is a well-established idea outside the security literature too — the same idea Landlock
  would deliver more cheaply and more precisely here. Neither Nix nor Bazel is installed on this machine (§2);
  adopting either as infrastructure would be a large, unrelated build-system decision, not a security fix.
  **ADAPT THE PATTERN, not USE DIRECTLY — and not relevant to Phase 2's defect list at all.**

### 3.12 Remote execution sandboxes (Bazel Remote Execution API and similar)

- **What it provides**: running build/test actions on a remote worker fleet, with the sandboxing question
  delegated to whatever isolates workers from each other (typically containers or gVisor) on that fleet.
- **What it doesn't provide (here)**: the deployment profile is explicitly single-machine, offline, no cloud
  dependency. A remote execution service is definitionally the opposite of this profile.
- **Fit**: **not applicable.** Listed for completeness per the assigned scope, not because it has any purchase
  on a one-owner offline machine. If Governance OS ever became a multi-user service, this pattern (delegate
  isolation to the execution backend) would be the natural place to revisit gVisor/Firecracker — that is a
  fully different product, not Phase 2 or even Level 3 for the current one.

---

## 4. Classification matrix

| Mechanism | USE DIRECTLY / WRAP / ADAPT / BUILD CUSTOM | REQUIRED NOW / USEFUL LATER / HIGH-ASSURANCE ONLY |
|---|---|---|
| Landlock (via `landlock` crate) | **WRAP** — Governance OS supplies the ruleset (what subtree, which rights); the kernel supplies the guarantee | **The one candidate I'd argue belongs in REQUIRED NOW** — see §5 for the explicit argument, not asserted lightly |
| Linux namespaces (raw) | n/a — foundation other tools compose, not a direct integration point | n/a (not a standalone decision) |
| seccomp-bpf | **WRAP**, if adopted — via a maintained crate (e.g. a seccomp-filter builder), never hand-rolled BPF | USEFUL LATER — real defense-in-depth, but answers a different question than the defect list asks; worth a narrow syscall-family denylist (`ptrace`, raw sockets, module ops) only after Landlock, not instead of it |
| Linux capabilities | n/a — currently no elevated process to restrict | HIGH-ASSURANCE ONLY, and conditional on Governance OS ever elevating at all |
| bubblewrap | **WRAP**, if/when a *whole subprocess tree* (not just one exec's filesystem effect) needs confinement | USEFUL LATER — right shape, more machinery (new binary, hand-written policy) than the current defect list needs |
| Rootless containers (Podman/Docker rootless) | **WRAP**, only if isolation needs grow to "run an entire untrusted toolchain," not for one exec | HIGH-ASSURANCE ONLY — daemon dependency (or missing prerequisites) contradicts current profile |
| Docker (as installed here) | n/a — already root-owned; not a candidate to build on as-is | Explicitly **not** a candidate — using it would *regress* the trust boundary, not strengthen it |
| gVisor | **WRAP**, only inside a container runtime already adopted for other reasons | HIGH-ASSURANCE ONLY — hostile-multi-tenant tool for a non-multi-tenant profile |
| Firecracker / microVMs | **WRAP**, only at true multi-tenant/hostile scale | HIGH-ASSURANCE ONLY — KVM-access precondition itself unmet here (§3.8) |
| VM isolation (general) | **WRAP** | HIGH-ASSURANCE ONLY |
| WASI / WebAssembly | **BUILD CUSTOM** if ever pursued (Governance OS's own tool ecosystem isn't Wasm-native; adopting WASI is a platform bet, not a wrap) | HIGH-ASSURANCE ONLY, and only for a hypothetically Wasm-native future |
| Hermetic build sandboxing (Nix/Bazel) | **ADAPT THE PATTERN** | USEFUL LATER, and only as a *reproducibility* concern, not a security one — orthogonal to this brief |
| Remote execution sandboxes | n/a | Not applicable to this deployment profile at all |

---

## 5. The explicit argument for Landlock as REQUIRED NOW (and why I'm not making that call myself)

The brief asks me to make this argument explicitly if I believe it, rather than let "most things land in the
last two buckets" default me out of saying it. Here it is, stated so the owner can accept or reject it on its
merits, not on my say-so:

1. **The codebase already says, in its own words, that this gap is open** (`runtime/src/tools.rs:892-897`, quoted
   in §1) — "the OS cannot confine a spawned process." That's not a Level-3 hypothetical; it's a documented,
   accepted limitation of the *current, shipped* execution path, sitting directly under two of the concrete
   defects this study is about (AR77-F1, AR77-F2, AR77-F4, P79-F1 all end in "writes ungated," and the write
   lands via a spawned process).
2. **The cost is genuinely small and does not scale with the problem's difficulty.** No daemon (checked: none
   needed). No privilege (checked: works at uid 1000). No new binary — one small, first-party-adjacent crate
   calling three syscalls already compiled into this exact kernel (checked). This is a categorically different
   cost profile from every other mechanism in this document, all of which require either a new external
   dependency, a daemon, elevated setup, or a threat model Governance OS doesn't have.
3. **It maps onto an existing call site, not a new architecture**: `capabilities/host.rs::invoke()` already
   constructs the `Command` and already uses a `pre_exec`-adjacent Unix extension (`process_group(0)`) at exactly
   the point a Landlock ruleset would attach. This is "delete-a-future-defect-class," not "add a subsystem."
4. **Against it**: this is still a Level-3-shaped mechanism (kernel LSM, security boundary) being proposed for
   what the brief frames as Level-2 territory (execution binding / effect containment on a trusted machine, not
   hostile isolation). The brief's own discipline warns against exactly this move — reaching for isolation
   because the technology exists and is cheap, rather than because the deployment profile demands it. A
   reasonable owner could say: on a single owner's own machine, where the actual attacker model is "a
   project-editable script tricks the classifier," effect *containment* is a genuine mitigation but a
   compensating one — the real defect (§6) is representation-vs-reality mismatch in what the classifier reasoned
   about, and no confinement layer fixes that; it only limits how bad a still-successful trick can be. That is a
   legitimate reason to defer this to R2 rather than pull it into a stopped Phase 2, and it's the owner's call to
   weigh "small cost, partial mitigation, right now" against "not our current failure mode, stay stopped."

I am flagging both sides because the brief is explicit that this determination belongs to the owner. My read is
that Landlock is unusual in this catalogue for having a defensible REQUIRED-NOW case at all; I am not asserting
it should be built.

---

## 6. What isolation does not solve — checked against the actual defect ids

This is the part of the brief I take most seriously, because it's the failure mode most likely to recur: treating
"we could sandbox that" as an answer to "was the governance decision correct."

- **P79-F11** (`env --chdir=decoy sh install.sh`; verified `<root>/install.sh`, executed
  `<root>/decoy/install.sh`): **A Landlock ruleset confined to the project-root subtree would not have stopped
  this.** `decoy/` is *inside* the project root. The defect is that the OS hashed one path and the kernel resolved
  and ran a different one — both inside the allowed subtree. Confinement narrows *where* effects can land; it has
  no opinion on *which file, among the files it already permits touching, actually ran*. This is the cleanest
  demonstration in the whole defect list that isolation is orthogonal to binding correctness.
- **P79-F1** (`PATH=. true`; kernel executes `<root>/true`, a project file pinned by nothing): partial, narrow
  overlap only — a ruleset that denied `LANDLOCK_ACCESS_FS_EXECUTE` under the project root entirely would stop
  *this specific* shape (executing a project-tree file as a command), **but** that is a containment side-effect
  of a blanket "nothing in the project tree may be executed" policy, not a fix for the underlying defect (`PATH`
  rebinding the resolved program after classification). The same underlying defect would resurface the moment
  anything in the project legitimately needs to execute (a build step, a test runner) — at which point the
  ruleset must carve out an exception, and the exception is exactly as easy to place wrongly as the original
  classifier was. Isolation shrinks the attack surface of this one variant; it does not generalize to the
  "verified bytes ≠ executed bytes" pattern the brief identifies as the actual defect.
- **AR77-F1/F2/F4** (empty-authority `file://`, path hidden inside a larger token, hard link defeating
  boundary resolution): these are the cases isolation is legitimately good at. A write that Landlock's
  `handled_access_fs` denies outside the project subtree is denied **regardless of how cleverly the path
  reached the kernel** — an empty-authority URL, a token-embedded path, or a hard link all eventually resolve
  to a real inode via a real syscall, and Landlock mediates that syscall, not the string that produced it. This
  is the genuine, honest win: it collapses an entire *class* of path-obfuscation tricks (present and future
  variants neither AR77 nor any classifier enumerated) into "did the final resolved path fall inside the
  allowed subtree," decided once, by the kernel, instead of needing the userspace scanner to anticipate every
  spelling. That is also precisely why it does *not* help with P79-F11/F1 above — those aren't obfuscated paths,
  they're *correctly resolved* paths to the *wrong* file.
- **P79-F8 / AR77-F3 / P79-F10 (authority-bearing state — Property C)**: **isolation contributes nothing here,
  and I want to be unambiguous about that rather than hedge.** The defect is that a hand-edited
  `REPOSITORY_CONTRACT.yaml` is indistinguishable from a governed edit, and that indistinguishability lets an
  edit silently remove an obligation. No sandbox, namespace, or seccomp filter changes what bytes are *in* a
  file that a trusted, unconfined process (the OS itself, reading its own project's contract) is entitled to
  read. This is a provenance/authentication problem for *data*, not an execution-confinement problem for
  *processes*. Running the YAML parser inside a Landlock jail changes nothing about whether the YAML it parsed
  was legitimately authored. This defect class lives entirely in Level 2A (governed state/authority provenance)
  and Level 2C (policy/config integrity) — sealing or signing the contract, or deriving it rather than trusting
  a mutable file, are the right directions, and neither is an isolation architecture. (I understand Research
  Agents 2/3 are covering that territory directly; I flag it here only to be explicit that my scope has nothing
  to offer it, per the brief's instruction to say plainly when the answer is "nothing we currently need.")
- **R0/R1-era unauthenticated update/init source**: same reasoning as Property C — a supply-chain/identity
  problem (Level 1), not a process-confinement problem. Isolating the *installer process* after the fact doesn't
  establish that the thing it's installing is the authentic release.

**Summary of the boundary**: isolation is well-matched to defects where the vulnerability is "many ways to make a
syscall land somewhere unintended" (AR77 family) and poorly matched — arguably irrelevant — to defects where the
vulnerability is "the wrong artifact was trusted" (P79-F11, P79-F1's resolution half) or "the wrong data was
trusted" (P79-F8/F3/F10, R0/R1). Phase 2's five consecutive failures are mostly the second shape. That is the
single strongest reason to keep this research at arm's length from Phase 2, exactly as the brief instructs.

---

## 7. Trusted computing base accounting

| Option | Added to TCB | Ongoing maintenance burden |
|---|---|---|
| Landlock | The already-trusted kernel's Landlock LSM (no new trust — it's part of the kernel already in the profile's trust boundary) + one small crate (~few hundred lines, audit-once) | Low: track ABI additions if wanting to use new rights; the crate's `Compatible` degrade-gracefully API absorbs most of this automatically |
| seccomp-bpf | Already-trusted kernel feature + a filter-policy the project authors and must keep correct across syscall-table changes | Moderate: policy drifts as new syscalls are used; wrong-direction denials cause hard-to-diagnose failures, not security holes, but are an ongoing support cost |
| bubblewrap | One new external binary + a hand-written flag policy that *is* the whole security boundary per its own docs | Moderate-high: the policy is bespoke and its correctness is entirely on Governance OS, not on bubblewrap |
| Docker/Podman (rootless) | Container runtime, image format/registry-adjacent tooling, (Docker) a daemon, (either) `newuidmap`/`newgidmap` setuid helpers | High: an entire runtime ecosystem, version-skew surface, CVEs in a much larger codebase than the problem needs |
| gVisor | Everything containers bring, plus a Go-implemented syscall-compatible kernel (Sentry) — large, novel codebase in the trust path | High |
| Firecracker | A VMM + KVM as a hard dependency + (here) an unmet access precondition | High, and currently blocked on this exact machine |
| WASI/WASM runtime | An entire alternate execution runtime (wasmtime/wasmer) that the actual workloads (native shell/Python tools) don't run on anyway | High, for close to zero coverage of the actual attack surface here |
| Nix/Bazel | Build-system-scale adoption, unrelated to security | High, and orthogonal |

Landlock is the only option on this list whose TCB delta is close to zero, because the thing it trusts (the
kernel) is already fully trusted by the deployment profile, and the thing it adds (one crate) is small enough to
read in full.

---

## 8. Simplification opportunities

- If Landlock is adopted narrowly at `host.rs::invoke()`, it **replaces no existing custom enumeration** — there
  isn't one at that layer yet — but it **forecloses the need to ever build one** for "which paths can a spawned
  plugin/installer touch." That is a defect class that, per the brief's own history (five rounds of
  enumeration-based repair), would otherwise very likely be re-solved the same losing way a sixth time. A kernel
  boundary that says "outside this subtree, no," decided once, is strictly fewer authority sources than any
  userspace path-scanner trying to anticipate `file://` variants, token-embedded paths, and hard links one at a
  time (AR77-F1/F2/F4's actual history).
- No other candidate in this study offers a comparable reduction for this codebase; everything else (§3.6–3.10)
  would be **net additions** to trusted surface and operational complexity, not simplifications, because the
  problem they solve (hostile multi-tenancy, cross-platform WASM portability, build hermeticity) is not a problem
  Governance OS currently has.
- The existing `Isolation::Sandbox` (§1) should **not** be extended into a security boundary by informal
  convention (e.g. "checks that run in the sandbox are safe to run untrusted code because they're in the
  sandbox") — it provides no kernel enforcement today, and conflating it with a security boundary would be a
  false sense of safety worse than having neither.

---

## 9. What I could not determine

- **Exact kernel versions for Landlock ABI 5 and above.** Two independently fetched sources disagreed
  (one said ABI5=6.3/ABI6=6.5, the other ABI5=6.10/ABI6=6.12; a third figure, "ABI8=Linux 7.0/ABI9=Linux 7.1,"
  is very likely a summarization artifact rather than a real kernel version and I am explicitly not
  relying on it). ABI 1–4 are corroborated by two sources plus this machine's own live probe and I trust them;
  ABI 5+ I could not pin down and did not want to present with false confidence.
- **Whether Firecracker (or KVM-backed gVisor) is reliably usable inside this specific WSL2 configuration**, even
  after the `kvm`-group access gap is closed. `/dev/kvm` exists on this host, which is itself notable (not all
  WSL2 configurations expose it), but I found no primary-source statement from Firecracker's own docs about
  nested-virtualization/non-bare-metal support, and I did not attempt to actually launch a microVM (would have
  required a privileged group-membership change I'm not authorized to make in a read-only research task).
- **Whether AppArmor's runtime-disabled state on this machine (`/sys/module/apparmor/parameters/enabled` = `N`,
  despite being compiled into `CONFIG_LSM`) is a WSL2-general characteristic or specific to this machine's
  configuration.** I did not find an authoritative statement either way and did not want to generalize from one
  data point.
- **Whether Docker's rootless mode, once its `uidmap` prerequisite is installed, performs acceptably under
  WSL2's own virtualization layer (a VM inside a VM, in effect).** I did not test this; it was out of scope to
  install new packages for a read-only study, and I did not want to assert performance characteristics I hadn't
  measured.

---

## Sources

- Linux kernel documentation, *Landlock: unprivileged access control* — https://docs.kernel.org/userspace-api/landlock.html
- `landlock(7)` manual page — https://man7.org/linux/man-pages/man7/landlock.7.html
- Rust `landlock` crate documentation — https://docs.rs/landlock/latest/landlock/
- Rust `landlock` crate ABI enum (official binding, `landlock-lsm` org) — https://landlock.io/rust-landlock/landlock/enum.ABI.html
- `capabilities(7)` manual page — https://man7.org/linux/man-pages/man7/capabilities.7.html
- `namespaces(7)` manual page — https://man7.org/linux/man-pages/man7/namespaces.7.html
- `user_namespaces(7)` manual page — https://man7.org/linux/man-pages/man7/user_namespaces.7.html
- bubblewrap project (GitHub, `containers/bubblewrap`) — https://github.com/containers/bubblewrap
- gVisor documentation — https://gvisor.dev/docs/
- Firecracker microVM project site — https://firecracker-microvm.github.io/
- Docker Engine documentation, *Rootless mode* — https://docs.docker.com/engine/security/rootless/
- WASI project site — https://wasi.dev/
- Bazel documentation, *Hermeticity* — https://bazel.build/basics/hermeticity
- This repository: `runtime/src/scheduler/catalogue.rs` (`Isolation` enum), `runtime/src/scheduler/sandbox.rs`
  (`Sandbox`/`SandboxOptions`), `runtime/src/scheduler/mod.rs` (`execute_one`), `runtime/src/capabilities/host.rs`
  (`invoke`), `runtime/src/tools.rs` (`installation_authority`, the "OS cannot confine a spawned process" comment)
- Empirical probe of this exact machine (kernel `6.6.87.2-microsoft-standard-WSL2`): `/proc/config.gz`,
  `landlock_create_ruleset`/`landlock_add_rule`/`landlock_restrict_self` syscalls (444/445/446) invoked directly,
  `unshare(1)`, `docker version`/`docker info`, `/dev/kvm` permission check, `/etc/subuid`/`/etc/subgid`,
  `/sys/fs/cgroup` mount type, `/sys/module/apparmor/parameters/enabled` — all run in this session, unprivileged,
  no product files touched, probe artifacts confined to the session scratchpad and (one harmless empty file,
  a byproduct of the `MAKE_REG` finding in §2) system `/tmp`.

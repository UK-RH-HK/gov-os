# Agent 5 — Developer Tooling and Build Systems: Prior-Art Study

**Scope**: Nix, Guix, Bazel/Buck2/Pants, OCI content addressing, GitOps reconciliation (Flux/Argo CD/OpenGitOps), plus
two smaller primitives pulled in because the big systems turned out to reduce to them (bubblewrap; `fexecve`/git-native
content addressing). Read-only research per `COMMON-BRIEF.md`. No product code touched.

---

## 0. Headline finding

None of the five large systems studied is a good fit **as a whole system** for Governance OS's deployment profile
(one owner, one WSL2 machine, offline, no cluster, no daemon wanted). Every one of them was built to solve a
multi-user, multi-machine, or multi-tenant problem, and that shows up as real, non-optional operational cost
(daemons, package ecosystems, registries, control planes) that does not pay for itself at this scale.

But the **patterns** underneath three of them map almost exactly onto our three open questions, and in each case the
pattern can be extracted in a form small enough to run as a few hundred lines of Rust with no new runtime dependency:

| Our question | System studied | What actually transfers | What does not |
|---|---|---|---|
| Verified bytes ≠ executed bytes (P79-F11, P79-F1) | Nix content-addressed store | **Never resolve a program name through a mutable environment/cwd; bind to an absolute path at declaration time; verify the file you are about to exec, not a file you looked up earlier** | The Nix language, channels, `/nix/store`, the daemon, package ecosystem |
| No governed/hand-edit distinction (P79-F8, AR77-F3, P79-F10) | GitOps reconciliation | **Desired state lives in one place, is content-addressed (a git commit), and the runtime refuses to treat working-tree content as authoritative unless it matches that commit exactly — checked synchronously at use-time** | The continuously-running reconciler/controller, the cluster, self-heal, admission webhooks |
| Custom command classifier | Bazel hermetic actions | **Declare inputs/outputs and let the sandbox make unauthorized access physically impossible, instead of statically predicting intent from argv** | Bazel itself, BUILD files, the dependency graph, remote execution |

This is the study's actual result: **three cheap, sourced, well-understood primitives replace three enumerations**,
without adopting any of the five ecosystems. Details, evidence, and honest caveats follow.

---

## 1. Nix (and, briefly, Guix)

### 1.1 What Nix actually guarantees

Nix store paths are **not uniformly content-addressed today**. This is the single most important correction to make
before using Nix as evidence for anything:

- **Fixed-output derivations** (e.g. `fetchurl`, source tarballs) are addressed by the hash of their actual output
  content — these genuinely are "the path is the hash."
- **Ordinary build derivations** (the vast majority — anything built from source) are, by default, **input-addressed**:
  the store path is a hash of the *derivation* (its inputs and build recipe), not of the resulting output bytes. Two
  bit-for-bit-identical outputs built from differently-labelled inputs get different store paths.
- **Content-addressed derivations** (RFC 62, the `ca-derivations` feature) change build *outputs* to be addressed by
  their actual content too, enabling build cutoff. This has been landing incrementally since Nix 2.4 (2021) but
  **remains behind an experimental flag and is not the default** as of the current Nix 2.3x manuals.
  [Nix 2.31 manual — Content-addressing derivation outputs](https://releases.nixos.org/nix/nix-2.31.0/manual/store/derivation/outputs/content-address.html) ·
  [NixOS RFC 62](https://github.com/NixOS/rfcs/blob/master/rfcs/0062-content-addressed-paths.md) ·
  [nixos.wiki: Ca-derivations](https://nixos.wiki/wiki/Ca-derivations)

So: **"the path is the hash" is true and load-bearing for fetched/pinned inputs (exactly our use case: a hash-pinned
`install.sh`), and only conditionally true for build outputs.** For Governance OS's problem — verifying a
hash-pinned, already-fetched file — the fixed-output/content-addressed case is the relevant one, and Nix's guarantee
there is real and strong: the store path `/nix/store/<hash>-name` cannot contain anything other than the bytes that
hashed to `<hash>`, because the path *is* derived from a hash of those bytes, checked on import
([Nix manual — Building](https://nix.dev/manual/nix/2.34/store/building.html)).

### 1.2 Does this make "did the verified artefact execute?" unanswerable-in-the-negative — precisely

**No, not by itself, and being precise about why matters more than the headline claim.**

Content addressing answers a *different* question than the one P79-F11/F1 exploit. It answers: "does the content at
this path match this hash?" It does **not** by itself answer: "did the process that just ran actually load its
program from this path, as opposed to some other path?" That second question is about **name resolution at the
call site**, and it is orthogonal to how the target is addressed.

What actually closes P79-F11/F1 inside Nix is a *different*, less-advertised property: **Nix build inputs reference
each other exclusively by absolute, fully-resolved store paths baked in at construction time — never by a name
resolved through `$PATH`, a relative path, or the current working directory.** Concretely:

- The build sandbox sets `PATH=/path-not-set` and `HOME=/homeless-shelter` specifically so that any program which
  falls back to searching `$PATH` or `$HOME` fails loudly instead of silently resolving to something impure
  ([Nix Reference Manual — Common Environment Variables](https://nix.dev/manual/nix/2.33/command-ref/env-common.html); this exact mechanism is documented across the stdenv build process).
- Interpreters and shebang lines in built artefacts get their references rewritten to absolute `/nix/store/...`
  paths (this is why Nix "patches shebangs" as a standard build step) — so a later invocation of that artefact does
  not re-resolve anything via environment or cwd.
- On Linux, builds run inside private mount/PID/network/IPC/UTS namespaces and see **only** the store paths declared
  as their dependencies, plus the build directory
  ([Nix Reference Manual — sandbox, nix.conf](https://nix.dev/manual/nix/2.34/command-ref/conf-file.html?highlight=sandbox)).

So the honest formulation of the transferable lesson is: **Nix's real defence against P79-F1/F11's mechanism is not
content addressing — it is the elimination of *any* runtime name-resolution step for build-time references.**
Content addressing is what makes it *safe to cache and dedupe* those absolute paths across machines and builds; it is
not what prevents the substitution attack. A system that adopted content addressing but still let a caller invoke
programs by relative path, bare name, or anything subject to `$PATH`/cwd would remain exactly as vulnerable to
P79-F1/F11 as Governance OS is today. Conversely, a system that never adopted content addressing but *always*
resolved to an absolute path at declaration time and verified the bytes at that exact path immediately before
`exec` — ideally via `fexecve()` on an already-opened, already-hashed file descriptor rather than re-opening a
pathname, which is the standard TOCTOU-safe idiom
([`fexecve(3)` — Linux manual](https://man7.org/linux/man-pages/man3/fexecve.3.html); [CERT FIO45-C](https://wiki.sei.cmu.edu/confluence/x/RdUxBQ)) —
would close P79-F11/F1 without adopting any part of Nix.

**Verdict on the framing question**: "did the verified artefact execute?" does not become structurally unanswerable
in a content-addressed store — it becomes a **different, answerable question once resolution is pinned at
declaration time**: "was this exact fd/path, and no other, ever handed to exec?" That is a call-site discipline
question, not a storage-addressing question. Nix demonstrates the discipline; it does not require the store to get
it.

### 1.3 Smallest useful subset — can you take the store without the language/daemon?

Yes, with real caveats.

- **`nix-store --add` / content-addressed import without the Nix language**: `nix-store` can add a file to the store
  and get back its hash-addressed path without writing any Nix expressions, and `nix store` subcommands operate on
  paths directly. You do not need Nixpkgs, channels, or `.nix` files to get hash-addressed, immutable file storage.
- **Single-user, no-daemon install is real and documented**: `curl -L https://nixos.org/nix/install | sh -s --
  --no-daemon` installs Nix with `/nix` owned by the invoking user and no `nix-daemon`
  ([nix.dev — Installing a Binary Distribution](https://nix.dev/manual/nix/2.18/installation/installing-binary)). This is explicitly the lower-isolation,
  lower-sharing option: "this installation has less requirements than the multi-user install, however it cannot
  offer equivalent sharing, isolation, or security. This option is suitable for systems without systemd"
  (same source). For a single-owner machine this tradeoff is close to free — there is no second user to isolate from.
- **WSL2 fit**: Nix installs and runs on WSL2. If systemd is enabled (WSL ≥0.67.6 supports it), the multi-user
  daemon install is what upstream recommends; without systemd, `--no-daemon` (or `--init none`) is the documented
  path ([NixOS Wiki — Nix Installation Guide](https://wiki.nixos.org/wiki/Nix_Installation_Guide)).
- **The sandbox is the part that costs the most on WSL2, and single-user mode weakens it.** Build sandboxing (the
  namespace isolation that gives Nix its purity guarantees during a *build*) depends on unprivileged user namespaces
  being usable. This is exactly the mechanism that is now broken by default on modern Ubuntu: **Ubuntu 23.10+, and
  by default on 24.04 LTS, sets `kernel.apparmor_restrict_unprivileged_userns=1`, which blocks `unshare(CLONE_NEWUSER)`
  for any tool without a matching AppArmor profile — this is documented to break bubblewrap, Chromium's sandbox,
  Flatpak, and "anything built on raw `unshare(CLONE_NEWUSER)`"**
  ([Ubuntu Discourse — Understanding AppArmor User Namespace Restriction](https://discourse.ubuntu.com/t/understanding-apparmor-user-namespace-restriction/58007); [Launchpad bug #2046477](https://bugs.launchpad.net/ubuntu/+source/apparmor/+bug/2046477)). Since WSL2's default distro is
  Ubuntu, **this is a live, not hypothetical, risk for exactly this deployment profile**: the fix is a scoped
  AppArmor profile or `sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0`, both real operational steps
  the owner would have to take and maintain. I could not determine whether WSL2's own kernel/AppArmor stack applies
  this restriction identically to bare-metal Ubuntu 24.04 — the WSL2 kernel is a Microsoft-maintained fork and the
  restriction is enforced by AppArmor policy shipped with the *distro* (Ubuntu userspace), not by WSL2 itself, so it
  most likely does apply, but I did not find a source testing this specific combination and I am flagging that gap
  rather than asserting it.
- **What using just the store, without the language, costs you**: you lose the entire point of Nix as a *package
  manager* (dependency closures, reproducible builds of third-party tools, binary caches). What you would actually
  be building is a hand-rolled content-addressed blob store plus a hand-rolled absolute-path-pinning discipline —
  at which point you are not really "adopting Nix," you are reimplementing its two good ideas in ~a few hundred
  lines of Rust with no daemon, no `/nix` partition, and no exposure to the Nix ecosystem's governance turmoil (see
  §1.5). That reimplementation is what I recommend evaluating, not a `nix-store` dependency.

### 1.4 Guix

Guix is architecturally the same idea (functional, content-addressed-ish store, build daemon, Guile-based
expressions) with one materially different fact for this deployment profile: **Guix's unprivileged, no-daemon path
is less mature and slower than Nix's.** Guix "may be run in single or multi-user mode," but full isolated builds
depend on the daemon, which itself now (since ~2025) supports dropping root privileges via unprivileged user
namespaces when available
([Guix HPC blog — Build daemon drops its privileges (2025)](https://hpc.guix.info/blog/2025/03/build-daemon-drops-its-privileges/); [Guix HPC — Using Guix Without Being root](https://hpc.guix.info/blog/2017/10/using-guix-without-being-root/)). For users who cannot or do not want to run the
daemon at all, the documented fallback is **PRoot**, a `ptrace`-based namespace emulator that does not require
kernel namespace support or root, but is a **process-tracing** approach — meaningfully slower and with a different
(weaker, syscall-interposition-based) isolation model than real Linux namespaces
([Guix HPC — Using Guix Without Being root](https://hpc.guix.info/blog/2017/10/using-guix-without-being-root/)). I found no evidence of a documented, supported "no
daemon at all, no PRoot" mode analogous to Nix's `--no-daemon` single-user install. **Guix is a weaker fit than Nix
for "no daemon we want to run," not a better one.** I am not recommending further investment in Guix specifically
for this project; everything useful about it is also true of Nix, with Nix having the more mature no-daemon path.

### 1.5 Maturity, maintenance, licence — an honest caveat the owner needs

Nix is old and heavily used (Eelco Dolstra's 2006 PhD work; LGPL-2.1; steward is the NixOS Foundation). But **the
ecosystem underwent a real governance crisis starting late 2023**: banned contributors, mass resignations from the
Foundation board and moderation team, the founder's forced resignation, and the emergence of community forks —
notably **Lix**, backed by former core maintainers, explicitly positioned as a "transparent, community-managed
alternative" both to stock Nix and to Determinate Systems' proprietary fork
([LWN — Nix alternatives and spinoffs](https://lwn.net/Articles/981124/); [Lix FAQ](https://lix.systems/faq/)). This does not make Nix unusable, but it means
"pick a Nix" is now a real decision with an unstable governance backdrop, and any recommendation to depend on the
Nix *ecosystem* (rather than the narrow store/pinning idea in §1.3) should flag this explicitly. This is exactly the
kind of maintenance-status fact the brief asks to be stated plainly rather than assumed from popularity.

### 1.6 Classification

**ADAPT THE PATTERN, not WRAP/USE DIRECTLY.** The specific properties that solve P79-F11/F1 (absolute-path pinning
at declaration time, environment-cleared execution, exec-what-you-just-verified) do not require the Nix store, the
Nix language, or a daemon, and are cheap to build directly in Rust. Taking a dependency on `nix-store` buys you a
package manager's worth of surface area (and, on WSL2/Ubuntu, a live AppArmor/user-namespace operational cost) for a
guarantee you can get more directly. **BUILD CUSTOM is justified here** — narrowly, for the ~200-line primitive
described in §5, not for a command classifier.

---

## 2. Bazel (and Buck2, Pants)

### 2.1 What Bazel's action sandbox actually is

A Bazel **action** declares its inputs and outputs explicitly (as part of the build graph). At execution time,
Bazel's sandbox builds a directory containing **only** those declared inputs (as symlinks) as the process's working
directory/execroot, executes the command line there, and then only the declared outputs are allowed back out —
anything else the process wrote is discarded and anything it tried to read that wasn't declared simply is not
present to read
([Bazel docs — Sandboxing](https://bazel.build/docs/sandboxing); [Bazel — Hermeticity](https://docs.bazel.build/versions/5.0.0/hermeticity.html)). On Linux this is enforced with mount, PID,
network, IPC and UTS namespaces (the `linux-sandbox` helper), i.e. the same class of kernel primitive Nix's build
sandbox uses.

Critically for our purposes, **Bazel does not read the command line to guess what it will do.** It does not
classify `curl` vs `rm` vs a shell wrapper. It makes the question moot by construction: if a command tries to open
a path that was not declared as an input, the open fails — not because Bazel recognized the command as dangerous,
but because the path does not exist in that mount namespace. This is a structurally different strategy from a
classifier: **the classifier predicts intent from syntax; the sandbox makes unauthorized *effect* physically
impossible regardless of intent.**

Bazel also (since `--incompatible_strict_action_env`, on by default since Bazel 0.21) does **not** inherit the
invoking shell's `PATH`/`LD_LIBRARY_PATH` into actions by default — it fixes `PATH` to a constant
(`/bin:/usr/bin` on Linux) specifically because environment-dependent actions break caching and reproducibility
([bazel-discuss — action_env, use_default_shell_env, incompatible_strict_action_env](https://groups.google.com/g/bazel-discuss/c/jHaj11mm6sU); [GitHub issue #6648](https://github.com/bazelbuild/bazel/issues/6648)). This is
the same discipline as Nix's `PATH=/path-not-set`, arrived at independently, for a different reason (cache
correctness rather than security) — which is itself a useful data point: **two unrelated mature systems converged
on "never let ambient PATH/env influence what executes" as a load-bearing invariant.** That convergence is stronger
evidence for the pattern than either system alone.

### 2.2 Does this remove the need to read commands at all, and what does it cost?

**For the specific class of attacks in P79-F11/F1/AR77-F1/F2/F4, yes, largely** — if Governance OS wrapped its own
tool/script invocations in an equivalent sandbox (declared-input allowlist, cleared environment, no ambient PATH),
a decoy directory outside the declared inputs would not be *visible* to the sandboxed process, an `LD_PRELOAD`
pointing outside declared inputs would fail to load, a hard link to an undeclared file would still resolve to
content outside the sandboxed root (namespaces isolate the *view*, not links themselves, but combined with an
allowlisted, read-only bind-mount of only the verified paths, the hard-link problem (AR77-F4) is also closed:
the sandbox never exposes the target of the link in the first place).

**It does not remove the need to reason about commands entirely** — you still must decide, for each governed
operation, *which paths* are legitimate inputs and outputs. That is a much smaller and more tractable enumeration
than "what will this argv do" (Governance OS's current classifier), because it is expressed as **capabilities
(paths) rather than **syntax (command shapes)**, and capabilities compose/allowlist far better than syntax
recognition does — but it is still a declaration surface, not a free lunch. Bazel's own experience shows the
migration cost: "hermeticity" required years of ecosystem work (`--incompatible_strict_action_env` alone shipped as
a breaking, opt-in-then-default change specifically because many existing BUILD rules implicitly depended on
ambient `PATH`) ([bazel-discuss thread linked above](https://groups.google.com/g/bazel-discuss/c/_VmRfMyyHBk)). For Governance OS this translates to: every governed tool
invocation needs an explicit, maintained list of the paths it is allowed to touch — a real authoring burden, though
one that fails *safe* (undeclared access errors out) rather than *silent* (today's classifier misses fail open).

### 2.3 Smallest useful subset — declared-inputs sandboxing without Bazel

Yes, and this is the most directly actionable finding in this report. **Bazel's own Linux sandbox is, at the
mechanism level, the same primitive as `bubblewrap` (bwrap)**: an unprivileged mount/user/PID namespace jail that
exposes only an explicit allowlist of paths, built and torn down per invocation
([bazel/site/en/docs/sandboxing.md](https://github.com/bazelbuild/bazel/blob/master/site/en/docs/sandboxing.md)). Bubblewrap is a small (~few-thousand-line), independently
packaged, widely-deployed C tool — it is the sandboxing engine underneath Flatpak — that does exactly this:
"bubblewrap uses Linux kernel user namespaces... allowing any user to use the tool... creates a new mount namespace
where the root is on a tmpfs invisible to the host... the level of protection... is entirely determined by the
arguments passed to bubblewrap"
([GitHub — containers/bubblewrap](https://github.com/containers/bubblewrap); [ArchWiki — Bubblewrap](https://wiki.archlinux.org/title/Bubblewrap)). Concretely, Governance OS could shell out through
`bwrap --ro-bind <verified-path> <verified-path> --unshare-all -- <command>` (or link `libseccomp`/namespace syscalls
directly in Rust, which is not much more code) and get Bazel's structural guarantee — "the path either exists in the
jail or the syscall fails" — without taking any dependency on Bazel, BUILD files, or a dependency graph. **This is
adopting the pattern at essentially zero ecosystem cost.**

The one real cost, and it is the same one flagged for Nix in §1.3: **bubblewrap needs unprivileged user namespaces,
and Ubuntu (WSL2's default distro) restricts them by default since 23.10/24.04** via
`kernel.apparmor_restrict_unprivileged_userns`, which is documented to break bubblewrap specifically
([Ubuntu Discourse](https://discourse.ubuntu.com/t/understanding-apparmor-user-namespace-restriction/58007); [melange issue #1508](https://github.com/chainguard-dev/melange/issues/1508); [VS Code issue #316046](https://github.com/microsoft/vscode/issues/316046) — the last one specifically documents this failure
mode inside a dev-tool sandbox, which is close to our exact use case). The fix (a scoped AppArmor profile shipped
alongside Governance OS, or documenting the one-line sysctl override for the owner) is small but **is a real
prerequisite the owner has to accept and maintain**, not a zero-cost adoption.

### 2.4 Buck2 and Pants — where they differ meaningfully

- **Buck2** (Meta, Rust, Apache-2.0) uses the same industry-standard Remote Execution API as Bazel (content-addressed
  action/input digests, Merkle-tree input roots) — so the addressing model is identical
  ([Buck2 docs — Remote Execution](https://buck2.build/docs/users/remote_execution/)). The materially different fact: **Buck2 "does not provide any
  local-sandboxing implementations by default"** — hermeticity is a property of remote execution, and local runs are
  closer to a plain task runner (Make/Just) unless you opt into sandboxing separately
  ([Hermetiq — Bazel vs Buck2 vs Pants (2026)](https://www.hermetiq.com/blog/bazel-vs-buck2-vs-pants)). For a **single-machine, no-cluster** deployment — exactly our
  profile — this means Buck2's out-of-the-box guarantee is *weaker* than Bazel's for local execution, which is the
  only execution mode we would ever use. This is a genuine, sourced reason to prefer Bazel's model (or bubblewrap
  directly) over Buck2's for this specific use case.
- **Pants** sandboxes local execution via per-work-unit temp-directory chroots materialized by a component called
  the **Sandboxer**, coordinated through `pantsd` — Pants' own **persistent daemon**
  ([Pantsbuild — Introducing the Sandboxer](https://www.pantsbuild.org/blog/2025/06/29/introducing-the-sandboxer)). Pants also documents an explicit escape hatch, the
  `workspace` execution environment, for tools that must run un-sandboxed inside the repo, with the caveat that
  "Pants cannot reasonably guarantee that build processes are reproducible" in that mode
  ([Pantsbuild — In-Workspace Execution](https://www.pantsbuild.org/blog/2024/12/04/workspace-environments)). Two things follow: Pants' sandboxing is directory-based
  (chroot-like), not namespace-based, which is a materially weaker isolation primitive than Bazel/bubblewrap's
  approach (it stops accidental path leakage, not a determined program probing `/proc` or issuing raw syscalls); and
  Pants' architecture assumes a long-running daemon, which conflicts directly with the "no daemon we want to run"
  constraint.

**Net**: for this deployment profile, **Bazel's sandboxing model (or its bubblewrap-equivalent) is the one worth
extracting; Buck2's default local mode is weaker than what we need, and Pants bundles a daemon we don't want.**

### 2.5 Classification

**ADAPT THE PATTERN.** Declared-inputs/outputs sandboxing, implemented via bubblewrap or direct namespace syscalls,
is the right shape for replacing the command classifier's *intent-prediction* function with a *capability-boundary*
function. **BUILD CUSTOM** is justified for the thin wrapper (a few hundred lines: build an allowlist from the
existing verification step, invoke bwrap, tear down), same reasoning as §1.6 — the mature systems' value here is
entirely in the *mechanism* (Linux namespaces), which is already a stable public primitive, not in the systems
themselves.

---

## 3. OCI (container image content addressing)

### 3.1 What it guarantees, precisely, and the parallel to P79-F11/F1

An OCI image manifest, and the config blob it references (which carries `Env`, `Entrypoint`, `Cmd`, `WorkingDir`),
are content-addressed: each blob's digest is `hash_algorithm:hash_value` computed over its actual bytes, and the
manifest digest is computed over the manifest JSON, which embeds the config blob's digest — so **the entrypoint,
default command, and default environment are genuinely pinned by a `pull-by-digest` reference**, not just the
filesystem layers ([OCI image-spec — manifest.md](https://github.com/opencontainers/image-spec/blob/main/manifest.md); [OCI image-spec — config.md](https://github.com/opencontainers/image-spec/blob/v1.1.1/config.md)). "Blobs are immutable by
definition, and changing content changes the digest, which changes the parent reference"
([Stack Harbor — The OCI image spec](https://stackharbor.com/en/knowledge-base/containers-oci-image-spec-deep-dive/)).

But this is exactly where the P79-F11/F1 pattern re-appears, in a different system, confirming it is architectural
rather than Governance-OS-specific: **the image digest pins what the image *declares* as its entrypoint/env/cwd, but
`docker run --entrypoint ... --env ... -w ...` overrides those declared values at invocation time, and that override
is not content-addressed, not verified against anything, and not part of the pulled artefact's identity at all.**
The digest guarantees "this is the artefact you verified." It says nothing about "the command you actually ran was
the one the artefact declared" if the invoker chose to override it — which is structurally identical to `env
--chdir=decoy sh install.sh` overriding a verified script's resolution via cwd, or `env PATH=. true` overriding it
via `$PATH`. **Content addressing an artefact and controlling how that artefact is invoked are two separate
problems; OCI solves the first completely and leaves the second entirely to the caller's discipline** — the same
conclusion reached for Nix in §1.2, from an unrelated ecosystem.

### 3.2 Smallest useful subset

You do not need a registry or a container runtime to use the pattern: it is "compute a digest over the full
declaration (paths + env + cwd + argv), not just over one input file, and pin the whole tuple as the unit of
verification, checked immediately before exec." That is a data-modelling change to what gets hashed, not a
dependency on OCI tooling. **I am not recommending adopting `containerd`/OCI runtimes** for this deployment profile
— running actual containers on WSL2 for governance checks would mean either Docker Desktop (a real daemon, licence
and resource cost) or a raw OCI runtime plus manual namespace setup, which is strictly more machinery than the
bubblewrap-based approach in §2.3 for the same guarantee.

### 3.3 Classification

**ADAPT THE PATTERN only.** OCI is valuable here purely as *independent confirmation* that "content-addressed
artefact ≠ controls how it's invoked" is a general architectural fact, not a Governance OS bug pattern. **No
component of OCI tooling is recommended for adoption** at this scale — the guarantee it provides over layers is not
one Governance OS needs (we are not distributing filesystem layers), and the guarantee we do need (declaration ==
what executes) is not something OCI provides either, per §3.1.

---

## 4. GitOps reconciliation (Flux, Argo CD, OpenGitOps)

### 4.1 The model, precisely

OpenGitOps' four principles: desired state is **declarative**; it is **versioned and immutable** (not "latest" —
a specific commit); a software agent **pulls it automatically**; and the same agent **continuously reconciles** live
state toward it ([OpenGitOps — PRINCIPLES.md](https://github.com/open-gitops/documents/blob/main/PRINCIPLES.md)). Argo CD and Flux both implement this as a controller that
diffs live cluster state against the git-declared state on an interval (Argo CD ~120s by default, faster with
webhooks; Flux similar), and optionally **self-heals** — Argo CD's `selfHeal: true`, Flux's `prune: true` plus its
reconciliation interval — actively reverting manual changes back to the git-declared state
([OneUptime — Flux CD vs ArgoCD: Drift Detection](https://oneuptime.com/blog/post/2026-03-13-flux-cd-vs-argocd-drift-detection/view); [Akuity — What Is Argo CD?](https://akuity.io/blog/what-is-argo-cd-features-and-business-benefits)).

### 4.2 Does this genuinely transfer to a single machine, no cluster — the hard question

**Only partially, and the part that transfers is not the part that gives GitOps its teeth.**

GitOps' actual enforcement mechanism — the reason a hand edit "gains no exemption" in a real GitOps deployment — is
**an always-running controller with continuous or webhook-triggered reconciliation**, i.e. exactly the kind of
daemon the deployment profile says we don't want. Without that controller, "desired state lives in git" is just a
filing convention; nothing stops a hand edit from taking effect between reconciliation cycles, and nothing reverts
it if nothing is watching. **The self-heal property strictly requires a control plane that is running independently
of the thing being governed** — that is not a detail of Kubernetes, it's the load-bearing part of the architecture.
Both Flux and Argo CD are Kubernetes controllers; I found no evidence either project, or the OpenGitOps spec, claims
the model works without a continuously-running reconciling agent, because "continuously reconciled" is one of the
four defining principles, not an optional extra.

**What does transfer, without a daemon**, is a narrower and cheaper sub-pattern: GitOps' *first two* principles
(**declarative** and **versioned-and-immutable**) plus a **synchronous check performed by the consumer itself at
every use**, rather than an independent watcher. Concretely, for P79-F8/AR77-F3/P79-F10:

- Treat the authority-bearing file (`REPOSITORY_CONTRACT.yaml`) as authoritative **only when it is byte-identical
  to a specific, identified git commit** — verified by content hash (git's own object model is already
  content-addressed: a blob's object ID is the hash of its content) at the moment Governance OS is about to *use*
  it, not on a timer.
- If the working-tree copy differs from that commit's blob, Governance OS treats the file as **unauthoritative** —
  not "reverted" (no daemon needed to revert anything), but simply **not read for authority purposes** until it is
  re-committed through whatever process is designated as "governed" (e.g., a signed commit, or a commit satisfying
  some already-existing CIT gate).
- This closes P79-F10's stated blocker directly: **the distinguishing mechanism the product currently lacks is
  exactly "does this content match a known, identified commit" — which is a single hash comparison against git's
  already-content-addressed object store, not a new enumeration.** A hand edit to the working tree is, by
  construction, either (a) not yet committed — hash mismatch, correctly rejected — or (b) committed — at which point
  it *is* a governed change by definition, because it went through commit, and whatever gate the project puts on
  commits (signing, CIT, review) is the actual governance point. This reframes "detect a hand edit" (P79-F10's
  blocked question) into "verify content against a designated commit" (an already-solved primitive), which is the
  simplification the brief is looking for.

This is precisely a case of taking OpenGitOps' *declarative + versioned-immutable* principles while explicitly
**declining** its *pulled-automatically + continuously-reconciled* principles, because those two require exactly the
daemon the deployment profile rules out. **Be honest about what is lost**: this gives you detection-and-refusal at
use-time, not active self-healing between uses. If a hand edit is made and nothing invokes Governance OS afterward,
nothing reverts it — but nothing needs to, either, because nothing reads it as authoritative until it is committed
and re-verified. That is a materially different (weaker in one sense, adequate for this profile in another) property
than what Argo CD/Flux provide, and the report should not blur that distinction.

### 4.3 Classification

**ADAPT THE PATTERN**, specifically the OpenGitOps "declarative + versioned-immutable" half, **not** the
"pulled-automatically + continuously-reconciled" half. **BUILD CUSTOM** is justified for the verification check
itself (hash comparison against a designated commit, invoked synchronously) — this is a small, well-understood
primitive (git's own content addressing, already a dependency the project has), not a new enumeration, and directly
answers P79-F10's "no mechanism to distinguish a governed change from a hand edit."

---

## 5. Concrete "smallest useful subset" proposals

These are research findings, not implementation — offered because the brief asks explicitly what could be deleted.

1. **Verified-exec primitive** (answers P79-F11, P79-F1, AR77-F4): resolve every governed path to an absolute,
   canonical path once, at declaration/verification time; open it there (not by re-resolving the name later); hash
   the opened file descriptor's content; keep the fd; if it must be handed to a child process, use `fexecve()` on
   that fd (not `execve()` on a path string) so there is no window between "this is what I verified" and "this is
   what runs" ([`fexecve(3)`](https://man7.org/linux/man-pages/man3/fexecve.3.html)). Clear/allowlist the child's environment before exec (Nix's and Bazel's
   independently-converged practice, §1.2/§2.1) so `$PATH`, `LD_PRELOAD`, `PYTHONPATH`, etc. cannot rebind anything
   post-verification. This directly removes the "loader-variable shape" enumeration (26 of 26 in P79-F1) by making
   the enumeration irrelevant rather than more complete.
2. **Declared-capability sandbox** (answers the classifier question, AR77-F1/F2, AR68/AR73 family): wrap governed
   command execution in bubblewrap (or direct `unshare()`/mount-namespace calls) with an explicit allowlist of
   verified paths, cleared environment, and no network unless declared. Undeclared filesystem access fails
   structurally; the classifier's job shrinks from "predict what this argv does" to "list the paths this operation
   needs," which is both smaller and fails safe. **Prerequisite cost**: WSL2/Ubuntu's default AppArmor restriction
   on unprivileged user namespaces (§1.3/§2.3) must be addressed — a profile or sysctl change, owner-visible and
   owner-maintained.
3. **Commit-identity gate for authority state** (answers P79-F8, AR77-F3, P79-F10): before reading
   `REPOSITORY_CONTRACT.yaml` (or any authority-bearing file) for a decision, hash its current content and compare
   against the blob hash recorded for a designated commit; refuse to treat it as authoritative on mismatch. No
   daemon, no reconciler — the check runs synchronously inside the existing invocation path.

None of these requires adopting Nix, Guix, Bazel, Buck2, Pants, OCI tooling, Flux, or Argo CD as dependencies. All
three are extractions of a single well-evidenced idea each.

---

## 6. Per-candidate record (brief §5 format)

| Candidate | Security property provided | Property NOT provided | Trust assumptions | Maturity | Maintenance | Licence | Platform | Offline? | Root? | WSL2? | Op. complexity | Fit (1 owner, no cluster, no daemon) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Nix store (no-daemon)** | Content-addressed fixed outputs; absolute-path pinning; env-cleared builds | Uniform content-addressing of *all* build outputs (input-addressed by default); anything about caller-side exec discipline outside Nix-built artefacts | Trusts local disk, single-user perms | ~20 yrs, very mature | **Governance crisis 2023–24, community forks (Lix)** — flag to owner | LGPL-2.1 | Linux, macOS (multi-user only on macOS) | Yes | No (single-user) | Yes, with caveats (§1.3 AppArmor userns) | Low-medium | Weak — whole package ecosystem for one guarantee we can build directly |
| **Guix** | Same idea as Nix | No documented no-daemon-no-PRoot mode | Trusts daemon or PRoot's ptrace model | ~12 yrs, mature, smaller community | Active (GNU project) | GPLv3 | Linux only | Yes | Daemon: yes (root or userns); PRoot: no | Untested by me on WSL2 | Medium-high | Weaker than Nix for this profile |
| **Bazel sandbox (linux-sandbox)** | Structural input/output isolation via namespaces; env not inherited by default | Does not predict/classify intent; still requires declaring the allowlist | Trusts kernel namespace enforcement | ~10 yrs OSS, Google-backed, very mature | Active, large community | Apache-2.0 | Linux, macOS, Windows(partial) | Yes | No | Yes, with same AppArmor/userns caveat as bubblewrap | Medium (full Bazel) / Low (bubblewrap-only) | Strong *pattern* fit; full Bazel itself is too heavy |
| **Buck2** | Same addressing model as Bazel (REAPI) | **No local sandboxing by default** — weaker than Bazel for single-machine use | Trusts remote executor for hermeticity (we have none) | Newer (2023 OSS), Meta-backed | Active | Apache-2.0/MIT (Meta OSS) | Linux, macOS, Windows | Yes | No | Untested by me | Medium | Poor — its guarantee mode (remote execution) is the one we don't have |
| **Pants** | Directory/chroot-based sandboxing | Weaker isolation than namespaces (no syscall/proc isolation); "workspace" mode drops guarantees entirely | Trusts `pantsd` daemon | Mature (Python ecosystem) | Active | Apache-2.0 | Linux, macOS | Yes | No | Untested by me | Medium-high (daemon) | Poor — bundles a persistent daemon we don't want |
| **OCI content addressing** | Full-image (incl. Env/Entrypoint/Cmd) immutability by digest | **Invocation-time overrides are unaddressed** — same gap as P79-F11/F1 | Trusts registry or local blob store integrity | Very mature, CNCF/Linux Foundation spec | Active, industry-wide | Apache-2.0 | Cross-platform via runtimes | Yes (local registry/store) | Typically yes for runtimes (rootless variants exist) | Yes via rootless podman etc., not evaluated in depth | High (registry/runtime) for a guarantee we don't need | Poor — no component recommended; pattern only |
| **Flux / Argo CD / OpenGitOps** | Continuous drift detection + self-heal, given a running controller | **Nothing** without a continuously-running agent — this is definitional, not incidental | Trusts the controller's own security and the cluster's admission control | Both CNCF graduated, very mature | Active | Apache-2.0 | Kubernetes | N/A (built for clusters) | N/A | N/A — not a fit for single-machine at all | High (both need a cluster) | Poor as systems; **declarative+immutable half of the pattern is a strong fit, reconciliation half is not** |
| **bubblewrap** | Unprivileged namespace jail, explicit allowlist | Nothing beyond what's passed as arguments; "protection... entirely determined by the arguments" | Trusts kernel userns support | Mature, small, widely deployed (Flatpak) | Active | LGPL-2.1 | Linux | Yes | No | Yes, **but blocked by default on Ubuntu 23.10+/24.04 AppArmor policy** without a profile/sysctl fix | Low | **Strong — this is the recommended extraction point for §2** |
| **git object content-addressing** | Blob/commit identified by content hash; tamper-evident history | Nothing about *runtime* enforcement — only about whether content matches a known commit | Trusts local git object store integrity | Extremely mature | Active | GPL-2.0 | Cross-platform | Yes | No | Yes | Near zero (already a dependency) | **Strong — already-available primitive for §4's gate** |

---

## 7. Classification summary (brief §6)

| Candidate | Classification | Reasoning |
|---|---|---|
| Nix (whole system) | **BUILD CUSTOM** (reject WRAP/USE DIRECTLY) | The two guarantees we need (absolute-path pinning, verify-then-exec) don't require the store, language, or daemon; adopting Nix buys an entire package ecosystem, a live WSL2/AppArmor operational cost, and exposure to unresolved governance turmoil, for a property extractable in ~200 lines |
| Guix | **Not recommended** | Strictly weaker no-daemon story than Nix for the same idea |
| Bazel (whole system) | **BUILD CUSTOM** for the mechanism (bubblewrap-based) | Full Bazel (BUILD files, dependency graph, query language) is disproportionate; the sandbox mechanism is a public, extractable Linux-namespace primitive |
| Buck2 | **Not recommended** | Its hermeticity depends on remote execution, which this profile doesn't have; local mode is weaker than Bazel's |
| Pants | **Not recommended** | Bundles a persistent daemon (`pantsd`); weaker (chroot, not namespace) local isolation |
| OCI | **ADAPT THE PATTERN only** (no component adopted) | Confirms the "artefact ≠ invocation" gap generalizes; no registry/runtime needed to act on that confirmation |
| Flux / Argo CD / OpenGitOps | **ADAPT THE PATTERN** (declarative + versioned-immutable halves only) | Reconciliation half requires a daemon this profile excludes; the other half maps directly onto git's existing content-addressed object store |
| bubblewrap | **WRAP / INTEGRATE** | Small, mature, single-purpose; a real candidate to shell out to directly rather than reimplement namespace calls from scratch |
| git content-addressing | **USE DIRECTLY** | Already a project dependency; the "hash the blob, compare to a designated commit" check is a direct, no-new-dependency use of a primitive already trusted |

---

## 8. Defect mapping

| Defect | Root architectural fix identified | Source pattern | Classification |
|---|---|---|---|
| P79-F11 (verified ≠ executed, cwd rebind) | Absolute-path pinning at declaration time + `fexecve` on an already-verified fd | Nix (§1.2), Bazel strict-env (§2.1) | ADAPT + BUILD CUSTOM (narrow) |
| P79-F1 (PATH/env rebind, 26 loader vars) | Cleared/allowlisted environment before exec; no ambient PATH resolution | Nix build env (§1.2), Bazel `--incompatible_strict_action_env` (§2.1) | ADAPT + BUILD CUSTOM (narrow) |
| AR77-F1 (empty-authority `file://`) | Out of this study's direct scope (URL parsing correctness) — but a declared-capability sandbox (§2.3) would deny the resulting out-of-root write structurally, independent of the parsing bug | Bazel sandbox | ADAPT (defense in depth) |
| AR77-F2 (absolute path inside a token) | Same — sandbox denies the write regardless of whether the scanner saw the path | Bazel sandbox | ADAPT (defense in depth) |
| AR77-F4 (hard link defeats path resolution) | Sandbox exposes only bind-mounted verified paths; the hard-linked target is never visible inside the jail even though canonicalisation can't see it | Bazel/bubblewrap sandbox (§2.3) | ADAPT + WRAP (bubblewrap) |
| AR68/AR73 family (~40 command shapes) | Declared-capability sandboxing replaces syntax classification for the whole family at once — this is the "one derived source replacing several enumerations" the brief asks for | Bazel hermetic actions | ADAPT + WRAP (bubblewrap) |
| P79-F8 (hand edit gains unmodelled exemption) | Commit-identity gate: content unauthoritative unless it matches a designated commit's blob hash | OpenGitOps declarative+immutable half; git object model | ADAPT + USE DIRECTLY (git) |
| AR77-F3 (second unmodelled consumer of `class`) | Same gate, applied uniformly at every consumer rather than re-derived per-consumer — collapses "does this field grant authority" into one check instead of N | OpenGitOps pattern | ADAPT |
| P79-F10 (no governed/hand-edit distinguishing mechanism) | The commit-identity hash comparison **is** the missing mechanism; it was absent because the project was treating "authority in the file" as the question instead of "does the file match a known-good commit" | OpenGitOps + git content addressing | ADAPT + USE DIRECTLY |

---

## 9. REQUIRED NOW / USEFUL LATER / HIGH-ASSURANCE ONLY

- **REQUIRED NOW** (private/local integrity, matches current Phase-2 problem exactly):
  - Commit-identity gate for authority-bearing files (§4.2, §5.3) — directly answers P79-F8/AR77-F3/P79-F10, zero
    new dependencies.
  - Verified-exec discipline: absolute-path pinning + cleared environment + `fexecve` on a verified fd (§5.1) —
    directly answers P79-F11/P79-F1.
- **USEFUL LATER** (R2, once the above are proven):
  - Declared-capability sandboxing via bubblewrap (§5.2) for the broader AR68/AR73 command-shape family — higher
    payoff but real authoring cost (every governed operation needs a declared path allowlist) and a real WSL2
    prerequisite (AppArmor/userns fix) that should be scoped and tested before committing to it.
- **HIGH-ASSURANCE ONLY** (R3/hostile, explicitly not now):
  - Full Nix/Guix adoption as build systems, Bazel/Buck2/Pants as build systems, OCI runtimes, Flux/Argo CD as
    control planes. All five assume either a package ecosystem to manage, a cluster to reconcile against, or a
    remote execution fleet — none of which this deployment has or should acquire for this problem. Revisit only if
    Governance OS ever needs to govern a *fleet* of machines rather than one owner's WSL2 box, which would be a
    materially different problem than the one in the brief.

---

## 10. What this would let Governance OS delete

- The 26-entry loader-variable enumeration (P79-F1) — replaced by "environment is cleared/allowlisted before every
  governed exec," a single invariant instead of a list that must be kept complete.
- The growing AR68/AR73 command-shape enumeration (~40 shapes and counting) — replaced by a capability-boundary
  check whose completeness does not depend on anticipating every wrapper/flag/interpreter shape, because it denies
  undeclared *access* rather than recognizing dangerous *syntax*. This is the single largest test-surface reduction
  identified: the enumeration stops growing because the mechanism stopped depending on enumeration.
  - AR77-F1/F2/F4 collapse into the same sandbox boundary rather than needing three separate parsing fixes (empty
    authority, embedded absolute path, hard link) — one mechanism instead of three.
- The open question "how do we detect a hand edit" (P79-F10) — replaced by a single hash comparison against a
  designated commit, deleting the need to ever again special-case a "second consumer" of an authority field
  (AR77-F3's actual failure mode): every consumer checks the same gate, so there is only one authority source to
  keep synchronized, not N.
- Net effect across the "authority-bearing state" defect family (P79-F8, AR77-F3, P79-F10): **three defects, one
  primitive.** Across the "execution binding" family (P79-F11, P79-F1, AR77-F1/F2/F4, AR68/AR73): **an open-ended,
  still-growing enumeration replaced by a structural boundary that does not need to grow.**

---

## 11. What I could not determine

- Whether the WSL2 kernel/AppArmor stack enforces `apparmor_restrict_unprivileged_userns` identically to bare-metal
  Ubuntu 24.04 — I found strong evidence the restriction is real on Ubuntu 24.04 generally and is enforced by the
  distro's AppArmor policy (not WSL2-specific code), so it most likely applies, but I did not find a source that
  specifically tested bubblewrap or Nix sandboxing on WSL2 Ubuntu 24.04 post-restriction. This should be verified
  directly on the target machine (`sysctl kernel.apparmor_restrict_unprivileged_userns`) before relying on it in a
  design.
- Exact current stabilization date/status of Nix's `ca-derivations` feature beyond "still experimental in the
  2.3x manual line" — I could not find an official announcement of it becoming a non-experimental default.
- Performance/operational experience of Guix's PRoot fallback in practice — the sources describe the mechanism but
  I found no benchmarked comparison to real namespaces.
- Whether Buck2's or Pants' local-sandboxing gaps have shifted in the most recent releases (both projects are
  actively developed; the sources cited are from 2025–2026 but this is a fast-moving area and I would not treat
  these as permanently fixed facts about either project).
- I did not evaluate Podman/rootless-container tooling as a distinct candidate beyond noting it exists (§6 OCI row)
  — the brief's OCI question was specifically about content addressing, not about rootless container runtimes as a
  sandboxing mechanism, and §2's bubblewrap finding already covers the sandboxing need with less machinery.

---

## 12. Sources

Nix: [nix.dev manuals (2.18–2.35)](https://nix.dev/manual/nix/2.34/), [NixOS RFC 62](https://github.com/NixOS/rfcs/blob/master/rfcs/0062-content-addressed-paths.md), [nixos.wiki Ca-derivations](https://nixos.wiki/wiki/Ca-derivations), [NixOS Wiki Nix Installation Guide](https://wiki.nixos.org/wiki/Nix_Installation_Guide), [LWN — Nix alternatives and spinoffs](https://lwn.net/Articles/981124/), [Lix FAQ](https://lix.systems/faq/).
Guix: [Guix HPC — Build daemon drops its privileges (2025)](https://hpc.guix.info/blog/2025/03/build-daemon-drops-its-privileges/), [Guix HPC — Using Guix Without Being root](https://hpc.guix.info/blog/2017/10/using-guix-without-being-root/), [GNU Guix Reference Manual](https://guix.gnu.org/manual/devel/en/guix.html).
Bazel: [bazel.build/docs/sandboxing](https://bazel.build/docs/sandboxing), [Bazel Hermeticity (5.0.0 docs)](https://docs.bazel.build/versions/5.0.0/hermeticity.html), [bazel-discuss — strict action env](https://groups.google.com/g/bazel-discuss/c/jHaj11mm6sU), [GitHub bazelbuild/bazel #6648](https://github.com/bazelbuild/bazel/issues/6648), [bazelbuild/remote-apis remote_execution.proto](https://github.com/bazelbuild/remote-apis/blob/main/build/bazel/remote/execution/v2/remote_execution.proto).
Buck2: [buck2.build — Remote Execution](https://buck2.build/docs/users/remote_execution/), [buck2.build — Why Buck2](https://buck2.build/docs/about/why/), [Hermetiq — Bazel vs Buck2 vs Pants (2026)](https://www.hermetiq.com/blog/bazel-vs-buck2-vs-pants).
Pants: [Pantsbuild — Introducing the Sandboxer](https://www.pantsbuild.org/blog/2025/06/29/introducing-the-sandboxer), [Pantsbuild — In-Workspace Execution](https://www.pantsbuild.org/blog/2024/12/04/workspace-environments).
OCI: [opencontainers/image-spec manifest.md](https://github.com/opencontainers/image-spec/blob/main/manifest.md), [opencontainers/image-spec config.md](https://github.com/opencontainers/image-spec/blob/v1.1.1/config.md), [Stack Harbor — OCI image spec deep dive](https://stackharbor.com/en/knowledge-base/containers-oci-image-spec-deep-dive/).
GitOps: [OpenGitOps PRINCIPLES.md](https://github.com/open-gitops/documents/blob/main/PRINCIPLES.md), [OneUptime — Flux CD vs ArgoCD drift detection](https://oneuptime.com/blog/post/2026-03-13-flux-cd-vs-argocd-drift-detection/view), [Akuity — What Is Argo CD?](https://akuity.io/blog/what-is-argo-cd-features-and-business-benefits).
Sandboxing/exec primitives: [GitHub containers/bubblewrap](https://github.com/containers/bubblewrap), [ArchWiki Bubblewrap](https://wiki.archlinux.org/title/Bubblewrap), [Ubuntu Discourse — AppArmor userns restriction](https://discourse.ubuntu.com/t/understanding-apparmor-user-namespace-restriction/58007), [Launchpad bug #2046477](https://bugs.launchpad.net/ubuntu/+source/apparmor/+bug/2046477), [VS Code issue #316046](https://github.com/microsoft/vscode/issues/316046), [`fexecve(3)` man page](https://man7.org/linux/man-pages/man3/fexecve.3.html), [CERT FIO45-C](https://wiki.sei.cmu.edu/confluence/x/RdUxBQ).

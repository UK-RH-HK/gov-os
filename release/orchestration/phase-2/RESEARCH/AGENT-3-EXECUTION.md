# Research Agent 3 — execution binding (Level 2B)

Scope: `approved artefact = verified artefact = EXECUTED artefact`. Defects of record: **P79-F11** (verified
`<root>/install.sh`, executed `<root>/decoy/install.sh` via `env --chdir=decoy`) and **P79-F1** (`env PATH=.
true` executes an unpinned `<root>/true`; 26/26 loader-variable shapes classify as readable). Generalisation per
the brief: *the OS binds lexical argv while the kernel executes what argv resolves to, through an environment
and working directory that the same argv controls.*

This report is read-only research. Nothing here is implemented. Deployment profile assumed throughout: single
owner, WSL2, kernel **6.6.87.2-microsoft-standard-WSL2** (from this session's own environment banner — used
below as the concrete kernel-version baseline, not a guess), no hardware-security assumptions, must work
offline.

---

## 1. Root-cause framing, checked against the mechanisms

Both proven defects share one shape: **something other than the verified representation determines what bytes
actually run.** For P79-F11 it is the working directory; for P79-F1 it is `PATH` plus the inherited environment.
Both are properties of the *exec call site*, not of any enumeration the OS could extend. That matches the
brief's diagnosis exactly, and it is why "parse argv more carefully" has failed five times: argv is not the
thing that determines execution — `execve()`'s three independent inputs (pathname resolution, `envp`, and the
process's `cwd`) are, and the current architecture only inspects one of the three (the lexical command string)
while the kernel evaluates all three at exec time, none of which are pinned to what was inspected.

The fix has to move the guarantee onto the execution primitive itself: verify a specific, already-resolved
**thing** (a path with no further resolution possible, or better, an open file descriptor), and execute *that
same thing*, through a call that cannot be perturbed by cwd or by an environment the input controls.

---

## 2. Candidate mechanisms

### 2.1 `execve(2)` with an absolute path and a caller-constructed `envp`

**Property provided:** `execve()` takes the pathname literally — it does **not** search `PATH`. Per man7:
"[execve] uses [path] literally; it does not search PATH — that is a feature of libc wrapper functions (execvp,
execl, etc.), not execve itself." `envp` is entirely caller-supplied: "envp is an array of pointers to strings
... which are passed as the environment of the new program" — nothing is merged in from the caller's own
environment unless the caller explicitly copies it in. [man7 execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html)

**Property NOT provided:** `execve()` still performs ordinary filesystem pathname resolution on its `path`
argument at call time. If that path is relative, it resolves against the process's *current* `cwd` — "If the
pathname does not start with the `/` character, the starting lookup directory of the resolution process is the
current working directory" [man7 path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html)
— which is exactly the P79-F11 lever (`env --chdir=decoy`). `execve()` alone does not protect against symlink
swaps, renames, or hard links occurring between a separate verification step and the exec call: the man page
documents no TOCTOU mitigation for path-based exec at all.

**Verdict for our two defects:** using `execve()` directly, with an **absolute, canonicalised** path constructed
by Governance OS itself (never a relative path handed through from argv, and never re-resolved against a
`cwd` the command could set) and an explicit minimal `envp`, closes P79-F1 completely and closes the *lexical*
half of P79-F11 (chdir can no longer change what path is opened, because there is no relative component left for
it to act on). It does **not** close the TOCTOU gap between "we hashed this path" and "we exec this path" if
verification and execution are two separate opens of the same path string — see §2.2.

### 2.2 `fexecve(3)` / `execveat(2)` with `AT_EMPTY_PATH` — execution by verified descriptor

**Mechanism:** `execveat(dirfd, "", argv, envp, AT_EMPTY_PATH)` executes whatever `dirfd` already refers to,
where `dirfd` may be an `O_PATH` (or `O_RDONLY`) descriptor obtained earlier. `fexecve(fd, argv, envp)` is the
glibc-level convenience wrapper for the same operation. Added to Linux in **3.19**; glibc has used it since
**2.27** ("if the underlying kernel supports the execveat(2) system call, then fexecve() is implemented using
that system call, with the benefit that /proc does not need to be mounted" — [man7 fexecve(3)](https://man7.org/linux/man-pages/man3/fexecve.3.html)).
On the kernel this deployment runs (6.6.87), both are fully available.

**The rationale, stated by the kernel documentation itself, is our exact use case.** fexecve(3) exists to "allow
the caller to verify (checksum) the contents of an executable before executing it" — i.e. it was designed
precisely to close the verify→execute gap.

**Property provided — narrows the window, does not eliminate content races:** the man page is explicit and
should be quoted directly, because it is the single most load-bearing citation in this report:

> "fexecve() does not mitigate the problem that the contents of a file could be changed between the checksumming
> and the call to fexecve(). In this case, the solution is to use file permissions to prevent the file from being
> modified by unauthorized users, or, better, use fsuid or Linux capabilities [...]" — [man7 fexecve(3), NOTES](https://man7.org/linux/man-pages/man3/fexecve.3.html)

This directly answers Q2: **execution-by-descriptor eliminates the *identity*-rebinding TOCTOU (the one P79-F11
exploits — cwd, symlink swap, rename, or re-resolving a path a second time cannot change which inode is executed
once you hold an fd to it) but it does not, by itself, eliminate a *content*-mutation race on that same inode**
between when you hash it and when you exec it. Closing that residual gap requires one of: (a) the file living on
read-only/immutable storage for the interval, (b) exclusive/advisory locking held across hash-then-exec, or (c)
the strongest and cleanest option for anything Governance OS downloads or stages itself — `memfd_create()` plus
sealing (§2.3), where the content literally cannot be written again once sealed, so "hash it, then exec the same
fd" is airtight by construction rather than by external discipline.

**Sharp edges (both explicitly documented, both real for our conforming path `sh install.sh`):**

- **Scripts and `#!`, the known sharp edge the dispatch called out, is real and specific.** When `execveat`/
  `fexecve` is used on a script, the kernel's `#!` handling rewrites `argv[0]` for the interpreter to a
  `/dev/fd/N` (or `/dev/fd/N/P`) path, which requires `/dev/fd` (→ `/proc/self/fd` on Linux) to be mounted and
  requires the descriptor to still be accessible to the interpreter the kernel launches. If that descriptor was
  opened `O_CLOEXEC` — the ordinarily-*safer* default — the interpreter cannot see it: "the program identified
  by dirfd and path requires the use of an interpreter program (such as a script starting with "#!"), but the
  file descriptor dirfd was opened with the O_CLOEXEC flag, with the result that the program file is inaccessible
  to the launched interpreter." [man7 execveat(2)](https://man7.org/linux/man-pages/man2/execveat.2.html).
  `fexecve(3)`'s BUGS section states the resulting failure mode plainly: if `fd` is close-on-exec, "fexecve()
  fails with the error ENOENT" because by the time the interpreter runs, the fd is already gone. **Practical
  consequence:** a Rust implementation must deliberately clear `O_CLOEXEC` on the verified descriptor immediately
  before the `fexecve` call (safe, because the process is about to replace its image anyway), or the entire
  mechanism silently fails on exactly the conforming case (`sh install.sh`) that P79-F11 is about.
- **`/proc`/`/dev/fd` dependency for scripts specifically.** Binary execution by descriptor genuinely does not
  need `/proc`. Script execution by descriptor does, because argv[0] becomes a `/dev/fd/N` path the interpreter
  must open. WSL2 runs a real Linux kernel with `/proc` and `/dev/fd` present and functional; I found no WSL2-
  specific defect reports for `execveat`/`fexecve`/`memfd_create` in kernel or Microsoft/WSL issue trackers. This
  should be treated as "no evidence of a problem found" rather than "confirmed clean" — I did not run it.
- **`AT_EXECVE_CHECK` is the kernel's own, very recent, answer to the *interpreter* half of this problem, and it
  is not usable yet.** Linux added `AT_EXECVE_CHECK` (merged for **6.14**, with IPE integration following in
  **6.19**) specifically so that "direct file execution (e.g. `./script.sh`) and indirect file execution (e.g.
  `sh script.sh`) lead to the same result" — this is a verbatim, kernel-documentation statement of the exact
  P79-F11 problem. [Executability check — Linux kernel docs](https://docs.kernel.org/userspace-api/check_exec.html);
  [Phoronix: AT_EXECVE_CHECK for 6.14](https://www.phoronix.com/news/Linux-6.14-AT_EXECVE_CHECK). It requires the
  *interpreter itself* to call `execveat(fd, "", ..., AT_EMPTY_PATH|AT_EXECVE_CHECK)` before interpreting; I found
  no evidence of `bash`/`dash`/`sh`/`python3` upstream adoption as of this research. **And it requires kernel
  6.14+; this deployment's WSL2 kernel is 6.6.87 — AT_EXECVE_CHECK is not available here today, full stop.**
  Classification: **HIGH-ASSURANCE ONLY / USEFUL LATER**, not part of any near-term fix.

### 2.3 `memfd_create(2)` + sealing — closing the residual content-mutation race

`memfd_create()` creates an anonymous, in-memory file descriptor. `fcntl(fd, F_ADD_SEALS, F_SEAL_WRITE |
F_SEAL_SHRINK | F_SEAL_GROW)` makes its contents permanently immutable once sealed. [man7 memfd_create(2)](https://man7.org/linux/man-pages/man2/memfd_create.2.html)

**Why this matters here:** for anything Governance OS *downloads or stages itself* (as opposed to a file already
sitting in the project tree), the pattern "write bytes to a memfd → seal `F_SEAL_WRITE` → hash the sealed fd →
`fexecve()` the same sealed fd" closes the content-mutation gap that §2.2 shows plain `fexecve` leaves open —
because after sealing, no process, including a racing one with the same UID, can alter those bytes. Hash and exec
now provably observe the same, frozen content. This is the strongest available guarantee I found for "verified
bytes = executed bytes" on this platform, and it is native kernel functionality with no additional trust
assumptions. **It does not, by itself, extend to files that must remain on disk as ordinary project files** (the
common case for `install.sh` sitting in a repository) — there, sealing is not applicable, and the answer for the
residual content race is filesystem-level (read-only mount, or accept the same window every non-Nix, non-CAS
system accepts and document it rather than claim it is closed).

### 2.4 `O_PATH` and `AT_EMPTY_PATH` — cheap, race-avoiding descriptor references

`open(path, O_PATH)` yields "a file descriptor that can be used ... to indicate a location in the filesystem
tree and to perform operations that act purely at the file descriptor level," without actually opening the
file's content ("read(2), write(2) ... fail with the error EBADF"). [man7 open(2)](https://man7.org/linux/man-pages/man2/open.2.html)
Combined with `O_NOFOLLOW`, it lets code obtain a reference to exactly the inode a path currently names, without
following a symlink, and without the overhead or risk of a full open. Passed to `execveat(fd, "", ...,
AT_EMPTY_PATH)`, it becomes the execution target directly. This is the natural low-level primitive under §2.2;
it does not add a new property beyond what is already stated there, but it is the correct way to *obtain* the
descriptor cheaply (no read permission required, only execute-search on the path prefix).

### 2.5 Environment clearing and allowlisting

**What must be cleared, with citations, matching the brief's named list:**

| Variable | Mechanism | Citation |
|---|---|---|
| `PATH` | if present, determines search order for bare-name resolution in `execvp`/`posix_spawnp`/shell built-ins | [man7 exec(3)](https://man7.org/linux/man-pages/man3/exec.3.html) |
| `LD_PRELOAD` | loads arbitrary shared objects before all others (ignored only in secure-execution/setuid mode, which is irrelevant here) | [man7 ld.so(8)](https://man7.org/linux/man-pages/man8/ld.so.8.html) |
| `LD_AUDIT` | loads audit shared objects that observe/intercept dynamic linking; "ignored in secure-execution mode" only | [man7 ld.so(8)](https://man7.org/linux/man-pages/man8/ld.so.8.html) |
| `LD_LIBRARY_PATH` | adds search directories for shared libraries at load time; ignored only in secure-execution mode | [man7 ld.so(8)](https://man7.org/linux/man-pages/man8/ld.so.8.html) |
| `PYTHONPATH`, `BASH_ENV`, `ENV`, `PERL5OPT`, `NODE_OPTIONS`, `GIT_SSH_COMMAND` | each is a documented, legitimate, interpreter- or tool-level code/command injection vector when the interpreter runs non-interactively/non-setuid — this is precisely the "26 of 26 loader-variable shapes classify as readable" finding in P79-F1, and it is architecturally the *same* problem recursing one level down inside whatever interpreter runs next (§4 below) | `BASH_ENV`: "looks for the variable BASH_ENV ... and uses the expanded value as the name of a file to read and execute" — note PATH is *not* used to find it, so it accepts relative paths directly — [GNU Bash manual, Bash Startup Files](https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html); `PERL5OPT`: "switches in this variable are treated as if they were on every Perl command line," including `-M` (load and execute a module) — [perlrun](https://perldoc.perl.org/perlrun); `GIT_SSH_COMMAND`: "interpreted by the shell," directly command-injectable — [git-scm.com Environment Variables](https://git-scm.com/book/en/v2/Git-Internals-Environment-Variables) |

**Important, easily-missed nuance found while verifying the Rust implementation (§5): clearing the *target
process's* `envp` is not sufficient by itself if the exec call used to launch it does its own `PATH` search
against the *caller's* environment rather than the `envp` being handed to the child.** The relevant primary-
source statement: `execvpe()` "searches for the program using the value of PATH from the caller's environment,
not from the envp argument" — [man7 exec(3)](https://man7.org/linux/man-pages/man3/exec.3.html). The same trap
applies to `posix_spawnp()`. This is a real, documented footgun that "clear the envp, call an exec/spawn
function" does not automatically avoid — the *search*, not just the *result*, has to be pinned. §5 shows how
Rust's standard library specifically engineered around this; any Governance-OS-side implementation needs the
same care and should not assume `env_clear()`-and-forget is sufficient without checking exactly which syscall
variant executes underneath.

**What legitimate installers need, and how mature systems resolve the tension (Q3), evidenced rather than
asserted:**

- Real `install.sh` scripts routinely shell out to `tar`, `curl`, `mkdir`, `sed` etc. by bare name, and often
  read `$HOME` for caches/dotfiles. A fully empty `envp` and no `PATH` breaks most non-trivial installers
  immediately.
- **Nix's answer:** inside its build sandbox, "the environment is cleared and set to the derivation attributes,"
  and specifically "`PATH` is set to `/path-not-set` to prevent shells from initialising it to their built-in
  default value" — i.e. Nix does not give builders *any* ambient tool access; every tool the build needs must be
  an explicitly declared input, and `PATH` is then constructed *inside* the build from those declared, hash-
  addressed inputs. [Nix manual, derivations](https://nix.dev/manual/nix/2.24/language/derivations). This
  requires a fully declared dependency closure — a real lift, and not something an ad hoc `install.sh` model
  provides for free.
- **Nix's second answer for genuinely impure needs (network, unpredictable environment) is the fixed-output
  derivation:** these are the *one* exception given network access during the build, but the trust model shifts
  from "control the process" to "verify the outcome" — "Nix computes a cryptographic hash of its output and
  compares that to the hash declared with these attributes. If there is a mismatch, the derivation fails,"
  regardless of how the output was produced. [Nix manual, advanced attributes — fixed-output derivations](https://nix.dev/manual/nix/2.24/language/advanced-attributes).
  This is a materially different guarantee than "verified bytes = executed bytes": it says nothing about the
  process, only about the artefact it emits, and it does not obviously transfer to an installer whose "output"
  is mutation of a live system rather than a content-addressable artefact. Worth flagging as a structurally
  different, *complementary* idea rather than a substitute.
- **Bazel's answer is the closest fit to Governance OS's actual constraint (ad hoc scripts, not a full declared
  closure), and it is directly evidenced, production-proven, and cheap:** since `--incompatible_strict_action_env`
  became default (Bazel 0.21), "Bazel will no longer use the client's PATH and LD_LIBRARY_PATH environment
  variables in the default action environment" — instead "`--experimental_strict_action_env` sets PATH for
  actions to a **fixed value** (`/bin:/usr/bin` on Linux) and does not set LD_LIBRARY_PATH at all." Anything more
  is added back explicitly and individually via `--action_env=VAR` — an allowlist, not the inherited environment
  and not a blanket clear. [bazel-discuss: Action environments — action_env, use_default_shell_env, and
  incompatible_strict_action_env](https://groups.google.com/g/bazel-discuss/c/jHaj11mm6sU); corroborated by
  [bazelbuild/bazel#6648](https://github.com/bazelbuild/bazel/issues/6648). Note this was driven by *two*
  motivations, not just security: unreproducible caching, since environment differences change cache keys. That
  is independent, converging evidence for the same design, not merely a security opinion.
- **Applied to Governance OS's actual tension:** the evidence points away from a binary "clear everything" vs
  "inherit everything" choice, and toward **a fixed, Governance-OS-constructed minimal `PATH`** (e.g.
  `/usr/bin:/bin`, never the invoking shell's or the project's `PATH`) plus an explicit, named allowlist for
  anything else a given installer step declares it needs — mirroring Bazel's proven default. A disposable,
  Governance-OS-controlled `HOME` (rather than either the real owner `$HOME` or no `HOME` at all) resolves most
  of the remaining breakage for tools that insist on writing caches/dotfiles somewhere, without exposing the
  owner's actual home directory contents to the installer.

### 2.6 Controlled working directory

`chdir()` happens, and *then* any subsequent relative-path resolution (including a second `execve` of a relative
program name) resolves against it — this is the entire mechanism P79-F11 exploits, and it is confirmed in both
the kernel documentation (§2.1) and, independently, in Rust's own documentation for `Command::current_dir()`,
which explicitly warns: "If the program path is relative ... it's ambiguous whether it should be interpreted
relative to the parent's working directory or relative to current_dir. The behavior in this case is platform
specific and unstable, and it's recommended to use canonicalize to get an absolute program path instead." [Rust
std::process::Command docs](https://doc.rust-lang.org/std/process/struct.Command.html). Two independent, primary
sources landing on the identical warning is strong corroboration that this is a well-understood, real footgun,
not an edge case. **The fix is not "control the cwd carefully" — it is "never let a relative program path exist
at the point of exec."** Once the path handed to `execve`/`fexecve` is absolute (or is a descriptor), the cwd
becomes irrelevant to *which program runs*, even though it still affects the child's *own* relative-path
behaviour after it starts (a separate, and much smaller, concern — Governance OS can still set a controlled,
disposable cwd for the child for that reason, just not rely on it for exec-time identity).

### 2.7 `noexec` mounts, read-only bind mounts, immutable roots

`noexec`: "Do not permit direct execution of any binaries on the mounted filesystem" [man7 mount(8)](https://man7.org/linux/man-pages/man8/mount.8.html).
**This is a poor fit for the specific conforming path in P79-F11.** `noexec` blocks the kernel from directly
executing a binary that lives on that mount; it does nothing to stop an interpreter that lives elsewhere (e.g.
`/bin/sh`, not on the `noexec` mount) from *reading* `install.sh`'s bytes off that same mount and interpreting
them — which is exactly `sh install.sh`. `noexec` remains a useful, cheap, independent control for the
AR68/AR73-family defects (a downloaded or planted binary executed directly), but it does not address the
interpreter-script shape at the centre of P79-F11, and should not be sold to the owner as doing so.

Read-only bind mounts and immutable roots are the filesystem-level way to close the residual content-mutation
TOCTOU noted in §2.2/§2.3 for files that must stay on disk (as opposed to being staged into a sealed memfd).
These are squarely adjacent to Agent 4's isolation scope (mount namespaces, containers) and I have deliberately
not gone deeper than citing the primitive, per the brief's boundary.

### 2.8 Content-addressed execution (Nix / Guix) and hermetic execution (Bazel) as *architectures*, not just as environment-handling precedents

Covered substantively in §2.5 and §4. The one point not yet made: both systems replace "verify a name, then
trust whatever that name resolves to at run time" with "the name **is** the hash" (a Nix/Guix store path embeds
the input hash; there is no separate resolution step to attack, because resolution and identity are the same
operation). This is the deepest, most structural version of "verified = executed," and it is the correct
comparison class for the owner's framing question in §6. It is also the most expensive: it requires a fully
declared dependency closure, which nothing in Governance OS's current installer model provides.

---

## 3. The Rust ecosystem (Q5), verified against source, not just documentation

**`std::process::Command` on Unix — what it actually gives, checked against the standard library source
(`library/std/src/sys/process/unix/{common,unix}.rs` and `library/std/src/sys/process/common/mod.rs` in
rust-lang/rust, fetched directly, not paraphrased from docs alone):**

- **`env_clear()`**: "Clears all explicitly set environment variables and prevents inheriting any parent process
  environment variables." Confirmed against source: it empties the `BTreeMap<OsString, OsString>` that
  `Command` uses to build the child's `envp`; `spawn`'s default (no `env_clear()`) is full parent-environment
  inheritance. [Rust docs](https://doc.rust-lang.org/std/process/struct.Command.html)
- **How `envp` reaches the child, and a real internal mitigation for the `execvpe`/`posix_spawnp` "wrong
  environment's PATH" trap documented in §2.5:** in the fork+exec fallback path (`do_exec`, `process/unix/
  unix.rs`), Rust does **not** call `execvpe`. It temporarily overwrites the process-global `environ` pointer to
  point at the child's constructed `envp` immediately before calling libc's `execvp` (`*sys::env::environ() =
  envp.as_ptr(); libc::execvp(...)`), and restores the original `environ` on any non-exec error path via an RAII
  guard. Because `execvp`'s `PATH` search reads the process's live `environ`, and that pointer has just been
  swapped to the *child's* configured environment, `PATH` search correctly follows `Command::env()`/
  `env_clear()`, not the calling process's real environment — this closes the specific trap in §2.5 for the
  fork+exec path. Separately, for the fast-path `posix_spawnp()` optimisation (`posix_spawn`, same file), Rust's
  own source explicitly guards against exactly this class of bug: it refuses the fast path — falling back to the
  safe `execvp` path above — whenever `self.env_saw_path() && !self.program_is_path()`, i.e. whenever the caller
  set a custom `PATH` *and* the program still needs `PATH`-style lookup. This guard was added deliberately: see
  [rust-lang/rust#77455, "Use posix_spawn() on unix if program is a path"](https://github.com/rust-lang/rust/pull/77455),
  whose description states the earlier code "would fall back to the non-posix_spawn based implementation if the
  PATH environment variable was possibly changed," precisely because `posix_spawnp()` is documented to search
  "in the same way as for execvp(3)" [man7 posix_spawn(3)](https://man7.org/linux/man-pages/man3/posix_spawn.3.html)
  — i.e. against the wrong environment if naively used. **This is a genuinely well-engineered piece of standard
  library code for exactly the footgun this research flags**, and it is a reason to prefer `std::process::Command`
  over a hand-rolled `execvp` call, not merely a convenience.
- **`current_dir()`**: sets the child's cwd via `chdir()`, executed in `do_exec` *before* `pre_exec` closures and
  well before the exec call. The relative-program-path ambiguity is documented by Rust itself (quoted in §2.6)
  and is not hidden — the standard library's own guidance is to canonicalise the program path to absolute before
  ever constructing the `Command`, which is precisely the fix this report converges on independently from the
  kernel-level analysis.
- **`CommandExt::arg0`** (Unix-only): sets `argv[0]` independently of the resolved program path — useful for
  producing a specific process-visible name without changing what is actually resolved and executed; not itself
  a security control.
- **`CommandExt::pre_exec`**: runs a closure in the forked child, after `fork()`, after `chdir`/`chroot`/uid-gid
  changes, but before `envp` is swapped in and before the exec call — i.e. late enough to be useful for last-
  moment checks (e.g. re-verifying a descriptor) but the closure still runs with the *parent's* environment
  live at that point (the `environ` swap happens after `pre_exec` closures run, per source) — worth flagging as
  a subtlety for anyone using `pre_exec` to do a security-relevant check, since `getenv()` inside that closure
  will not yet see the child's intended, cleared environment.
- **Where it falls short for our exact problem:** `std::process::Command` has **no built-in support for
  `fexecve`/`execveat`-by-descriptor execution at all.** Everything above operates on a *path string*
  (`ProgramKind::{Absolute, Relative, PathLookup}`, itself computed lexically from the program string at
  `Command::new()` time — the same "classify the string" pattern the brief warns is structurally insufficient,
  though here it is only choosing an *exec strategy*, not making a trust decision). There is no descriptor-based
  exec anywhere in `std`. To get §2.2/§2.3's TOCTOU-closing property, Governance OS needs a crate or raw `libc`/
  `nix` call outside `std`.
- **A directly relevant, currently in-flight change to Rust itself, found while verifying the above (dated to
  this month):** [rust-lang/rust#157144](https://github.com/rust-lang/rust/pull/157144), open and in final
  comment period at time of writing, removes the global-`environ`-pointer-mutation trick from `CommandExt::exec`
  (the Unix "replace current process" variant, as distinct from `spawn()`) because it violates the function's own
  locking invariants under concurrent `exec` calls, and replaces it with **Rust performing its own `PATH` search
  in pure Rust code and then calling `execve()` directly with the fully resolved absolute path** — i.e. the
  standard library's own maintainers are independently converging, right now, on "resolve to an absolute path
  yourself, then use the non-searching primitive," which is the same conclusion this report reaches from the
  kernel-documentation side. This is corroborating engineering direction, not just an analogy.

**Crates that cover the `fexecve`/`execveat` gap:**

| Crate | Coverage | Maturity/licence | Notes |
|---|---:|---|---|
| [`nix`](https://docs.rs/nix/latest/nix/unistd/) | `nix::unistd::execve`, `execveat`, `fexecve` all present | v0.31.3 (May 2026), MIT, actively released | Confirmed directly against docs.rs: `fexecve(fd: Fd, args: &[SA], env: &[SE]) -> Result<Infallible>` — safe-ish wrapper (still requires `unsafe`-adjacent care around process replacement), well-typed, covers the exact primitive in §2.2. This is the crate I would point an implementation at. |
| `rustix` (bytecodealliance) | Requested in [bytecodealliance/rustix#490](https://github.com/bytecodealliance/rustix/issues/490) (opened Dec 2022) | — | **I could not confirm current status.** The issue thread I could retrieve did not show a clear resolution, and a direct docs.rs module fetch for a plausible `runtime::execveat` path 404'd. Treat as unconfirmed rather than either "available" or "unavailable" — verify directly against `docs.rs/rustix` before relying on it. |
| [`cap-std`](https://github.com/bytecodealliance/cap-std) (bytecodealliance) | Capability-oriented `std` replacement; `Dir` handles eliminate ambient-authority path traversal (protects against `..`, symlinks, absolute paths escaping a `Dir`) | Actively maintained, Apache-2.0/MIT dual, used inside Wasmtime | Architecturally the right *pattern* for "hold a verified handle, never re-derive it from a path string" — directly analogous to what §2.2/§2.4 ask for at the exec boundary, though `cap-std` itself is about filesystem access capabilities, not process exec. Does not appear to include an exec-by-descriptor primitive itself; would need pairing with `nix::unistd::fexecve`. |

---

## 4. Answering the five questions directly

**Q1 — smallest change, and what it does not close.** Two changes, applied together, close both proven defects:
(1) resolve the target to an **absolute, canonicalised path (or an open descriptor) before verification, and
execute that same resolved target** — never a relative path, never a second independent path lookup; (2) **exec
with a Governance-OS-constructed `envp`** (fixed minimal `PATH`, explicit allowlist, no inherited loader/
interpreter variables) **via a syscall path that honours that `envp` for its own internal `PATH` search** (Rust's
`std::process::Command` already gets this right for its `spawn()` fork+exec path, per §3 — a raw `execvpe`/
`posix_spawnp` call would not, per §2.5). What it does **not** close: the content-mutation TOCTOU window between
hash and exec unless paired with §2.2/§2.3/§2.7 (descriptor-exec + immutability); anything the *interpreter*
itself does once it starts running the verified script (§4 below, Q4); AR77-F1/F2/F4 (URL-authority parsing,
embedded absolute paths, hard links), which are different sub-mechanisms of the same family and need their own,
related fixes (notably: hard links have no symlink to canonicalise away — identity there has to be established
by device+inode of the opened descriptor, not by any path string, which is the same "verify the descriptor, not
the name" principle applied one level further); and it provides no protection at all against a correctly-and-
exactly-executed script that is simply malicious — exactness is not safety, and that boundary is intentionally
Level 3, not this report's problem to solve.

**Q2 — does descriptor-based exec eliminate TOCTOU, or narrow it?** **Narrows it, precisely and provably, but
does not eliminate it**, and the kernel's own documentation says so in as many words (fexecve(3) NOTES, quoted in
full in §2.2). It eliminates the *identity*-rebinding race (P79-F11's exact mechanism: nothing can make an
already-open descriptor refer to a different inode). It leaves open a *content*-mutation race on that same inode
unless combined with immutability (sealing, read-only mount, or exclusive locking held across the whole
hash-then-exec interval).

**Q3 — what breaks, and how do mature systems resolve it?** A fully cleared environment and no `PATH` breaks
almost any real installer that shells out to coreutils by bare name. Nix resolves this by never giving builders
ambient tools at all — every tool is a declared, hash-addressed input, and `PATH` is synthesised from those
inputs inside the build (a full-closure model Governance OS's ad hoc installer scripts do not have). Bazel
resolves the same tension more cheaply and closer to Governance OS's actual shape: a **fixed, non-inherited
default `PATH`** (`/bin:/usr/bin`), no `LD_LIBRARY_PATH`, and an explicit per-variable allowlist (`--action_env`)
for anything more — evidenced as the shipped default since Bazel 0.21, not a proposal. This is the directly
transferable precedent: replace "inherit everything" and "clear everything" with "a fixed, OS-owned minimal
baseline plus an explicit allowlist."

**Q4 — interpreters: what does hash-pinning `install.sh` actually guarantee?** Only that a specific set of bytes
existed at a specific, fully-resolved location at the moment they were hashed. It guarantees nothing about which
`sh` interprets them (a second, independent resolution, subject to the identical PATH/cwd problem one level up
— which is exactly how P79-F11 defeats it), nothing about whether the bytes handed to that `sh` are the same
bytes that were hashed (the TOCTOU gap in Q2, unless the same fd is used for both), and nothing about what those
bytes cause `sh` to run *next* — every command the script itself invokes by bare name is a fresh, unpinned
instance of the same resolution problem, recursively, inside the interpreter's own process. Content-addressing
(Nix/Guix) is categorically different because it does not hash-pin an entry point and hope the rest behaves — it
makes every name reachable from the process resolve only to other hash-addressed artefacts, so there is no
unpinned target *to* resolve to, at any recursion depth. Hash-pinning the top-level script is necessary but
structurally incapable of delivering that property by itself; closing it fully requires either a fully declared
closure (expensive, a Level-of-effort well beyond this defect fix) or accepting that "what a verified script then
does" is a review/policy question, not an execution-binding one, and belongs outside Level 2B's remit.

**Q5 — Rust reality.** Covered in full in §3. Summary: `std::process::Command`'s `env_clear()`/`current_dir()`
are sound and, per direct source inspection, specifically engineered against the `execvpe`/`posix_spawnp`
"wrong-PATH" footgun (`rust-lang/rust#77455`) — better than a naive libc call would be. It has no descriptor-exec
primitive at all; `nix::unistd::fexecve`/`execveat` (MIT, actively maintained, v0.31.3) is the natural, verified-
available fill for that specific gap. Rust's own maintainers are independently moving `CommandExt::exec` toward
"resolve to an absolute path in Rust code, then call `execve()` directly" (`rust-lang/rust#157144`, open, dated
to this research period) — the same architecture this report recommends, arrived at independently.

---

## 5. Classification

| Mechanism | Classification | Maps to defect(s) | REQUIRED NOW / USEFUL LATER / HIGH-ASSURANCE ONLY |
|---|---|---|---|
| Absolute-path resolution before verify; never exec a relative path | ADAPT THE PATTERN (no library — it's a discipline in the call site) | P79-F11 (lexical half), AR68/AR73 family | REQUIRED NOW |
| `execve()` with Governance-OS-constructed `envp`, fixed minimal `PATH`, explicit allowlist | ADAPT THE PATTERN, informed directly by Bazel's shipped default | P79-F1 (all 26 loader-variable shapes) | REQUIRED NOW |
| `fexecve`/`execveat(AT_EMPTY_PATH)` via `nix` crate, descriptor obtained via `O_PATH` | WRAP / INTEGRATE (`nix` crate) | P79-F11 (identity-rebinding half) | REQUIRED NOW, with the `O_CLOEXEC`-on-scripts caveat implemented deliberately |
| `memfd_create` + `F_SEAL_WRITE` for anything Governance OS downloads/stages itself | WRAP / INTEGRATE (kernel primitive, direct `libc`/`nix` binding) | Residual TOCTOU on P79-F11 for staged content | USEFUL LATER (only applies once Governance OS stages installers itself rather than reading them in place) |
| `AT_EXECVE_CHECK` | not usable — kernel 6.14+ required, no interpreter adoption found | P79-F11 (interpreter half), Q4 | HIGH-ASSURANCE ONLY / USEFUL LATER — re-evaluate once WSL2's kernel and mainstream shells catch up |
| `noexec` mounts / read-only bind mounts / immutable roots | WRAP / INTEGRATE, but scoped correctly | AR68/AR73 family (direct-binary defects) **only** — not P79-F11 | USEFUL LATER, coordinate with Agent 4 |
| Full Nix/Guix-style content-addressed closure for installer dependencies | ADAPT THE PATTERN — architecturally correct, expensive | Q4's recursive interpreter problem, structurally | HIGH-ASSURANCE ONLY / USEFUL LATER — too large a lift to be "the cheapest increment" (see §6) |
| `std::process::Command` (env_clear/current_dir/arg0) as the base | USE DIRECTLY | P79-F1, P79-F11 (partially) | REQUIRED NOW — but must be paired with the descriptor-exec crate above; `std` alone does not reach the TOCTOU-closing property |
| `cap-std` | ADAPT THE PATTERN (illustrative; not a drop-in exec primitive) | general reinforcement of "verify the handle, not the name" | USEFUL LATER |

---

## 6. Testing the owner's framing: is this "Option B's principle at its cheapest increment"?

**Largely yes, with one important qualification.** The evidence supports treating "own the execution boundary"
as cheap relative to full sandboxing: it requires no new isolation technology, no containers, no new trust
roots — just disciplined use of syscalls that have existed since Linux 3.19 (`execveat`) or are original POSIX
(`execve`), wrapped by a crate (`nix`) that is already MIT-licensed, maintained, and small. The REQUIRED NOW row
above is genuinely a small, well-understood, well-precedented change (Bazel ships the environment-handling half
of it as a *default*, not an experiment).

**The qualification:** "cheapest increment" is only true for the *P79-F1 shape* (environment/PATH rebinding) and
the *lexical half* of the *P79-F11 shape* (cwd rebinding a relative path). It is **not** true for the full
Q4 problem — making the interpreter's own, recursive, internal resolutions trustworthy — which genuinely does
require either the Nix/Guix-scale architecture (expensive, out of proportion to "cheapest increment") or an
explicit, honest decision that Level 2B's guarantee stops at "the interpreter that runs is the one intended, on
the bytes that were reviewed" and does not extend to "everything that interpreter subsequently does is also
verified." I think the second framing — own the boundary, and say plainly that ownership stops where the
interpreter's own behaviour begins — is the correct scope for this increment, and matches the brief's Level 2
vs Level 3 boundary instruction. Presenting the cheap fix as closing more than that would repeat the pattern the
brief says has failed five times: solving the enumeration you were handed while leaving the general shape open.
One further, concrete simplification this increment buys: **it deletes the need for the command-shape/argv
classifier that AR68/AR73's ~40 command shapes were built to enumerate**, for the specific sub-problem of "what
actually gets executed" — once execution is bound to a resolved descriptor/absolute-path plus a controlled
`envp`/cwd, wrapper chains, flag bundles, and backslash/forward-slash spelling divergence stop being relevant to
*this* question, because they can no longer change what the kernel executes, only what a human reads in a log.
That is a real reduction in enumeration surface, not just a new control layered on top of the old one.

---

## 7. What I could not determine

- Whether `rustix` currently exposes `execveat`/`fexecve` — the GitHub feature request (#490, opened Dec 2022)
  did not show a clear resolution in what I could retrieve, and a direct docs.rs fetch 404'd. Use `nix` (confirmed
  present, MIT, v0.31.3) instead, or verify `rustix` directly against `docs.rs/rustix` before choosing it.
- Whether any mainstream shell or interpreter (`bash`, `dash`, `sh`, `python3`) has adopted `AT_EXECVE_CHECK` —
  I found no adoption evidence, but absence of evidence in web search is weaker than a direct source check I did
  not have budget to perform against each project's own repository.
- Whether WSL2 has any undocumented divergence from mainline Linux for `execveat`/`fexecve`/`memfd_create`
  sealing specifically — I found no reported issues, which is not the same as a positive confirmation; I did not
  have an environment to execute a test in.
- The precise performance cost of the fork+exec fallback path (`do_exec`/`execvp` with the `environ` swap) versus
  the `posix_spawn` fast path, for Governance OS's actual workload shape — this is knowable but requires
  measurement I did not perform.
- Whether Governance OS's current installer model has *any* existing declared-dependency mechanism that a
  Bazel-style `--action_env` allowlist could hang off of, or whether that allowlist would need to be invented from
  scratch — this is a codebase question outside this report's read-only web/kernel-documentation research scope.

---

## 8. Sources

- man7.org: [execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html), [execveat(2)](https://man7.org/linux/man-pages/man2/execveat.2.html), [fexecve(3)](https://man7.org/linux/man-pages/man3/fexecve.3.html), [open(2)](https://man7.org/linux/man-pages/man2/open.2.html) (O_PATH), [exec(3)](https://man7.org/linux/man-pages/man3/exec.3.html), [path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html), [posix_spawn(3)](https://man7.org/linux/man-pages/man3/posix_spawn.3.html), [ld.so(8)](https://man7.org/linux/man-pages/man8/ld.so.8.html), [memfd_create(2)](https://man7.org/linux/man-pages/man2/memfd_create.2.html), [mount(8)](https://man7.org/linux/man-pages/man8/mount.8.html)
- Linux kernel documentation: [Executability check / AT_EXECVE_CHECK](https://docs.kernel.org/userspace-api/check_exec.html)
- LWN.net: [syscalls,x86: Add execveat() system call](https://lwn.net/Articles/619392/)
- Phoronix: [AT_EXECVE_CHECK submitted for Linux 6.14](https://www.phoronix.com/news/Linux-6.14-AT_EXECVE_CHECK)
- Nix manual: [derivations](https://nix.dev/manual/nix/2.24/language/derivations), [advanced attributes — fixed-output derivations](https://nix.dev/manual/nix/2.24/language/advanced-attributes)
- Bazel: [bazel-discuss — Action environments: action_env, use_default_shell_env, incompatible_strict_action_env](https://groups.google.com/g/bazel-discuss/c/jHaj11mm6sU); [bazelbuild/bazel#6648](https://github.com/bazelbuild/bazel/issues/6648)
- Rust: [std::process::Command docs](https://doc.rust-lang.org/std/process/struct.Command.html); source: `library/std/src/sys/process/{common.rs,unix/common.rs,unix/unix.rs}` at rust-lang/rust (fetched directly, main branch); [rust-lang/rust#77455](https://github.com/rust-lang/rust/pull/77455) (posix_spawn PATH fallback rationale); [rust-lang/rust#157144](https://github.com/rust-lang/rust/pull/157144) (in-flight: manual PATH resolution + execve to remove global-environ mutation)
- Crates: [nix::unistd (docs.rs)](https://docs.rs/nix/latest/nix/unistd/fn.fexecve.html) v0.31.3 MIT; [bytecodealliance/cap-std](https://github.com/bytecodealliance/cap-std); [bytecodealliance/rustix#490](https://github.com/bytecodealliance/rustix/issues/490) (status unconfirmed)
- GNU Bash manual: [Bash Startup Files (BASH_ENV)](https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html)
- Perl: [perlrun (PERL5OPT)](https://perldoc.perl.org/perlrun)
- Git: [git-scm.com — Environment Variables (GIT_SSH_COMMAND)](https://git-scm.com/book/en/v2/Git-Internals-Environment-Variables)
- Deployment fact used directly: this session's own environment banner, kernel `6.6.87.2-microsoft-standard-WSL2`, used to determine `AT_EXECVE_CHECK` (needs 6.14+) is not available on the target deployment today.

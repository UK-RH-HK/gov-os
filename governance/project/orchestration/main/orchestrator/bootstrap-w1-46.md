
## W1-46 residuals (worker session launcher, 2026-10-04)

Recorded at W1-46's close, from the three ticket-lead summaries and the two reviewer passes. `gov launch` is built;
leads and workers were still started unsandboxed during this ticket (DEC-183). Each item names who should settle it
where that is known; the rest go to EXP-002 and the mid-wave audit.

**What a launched session can still do**

- **A new name under `.gov-runtime/` outside `scratch/`, made at the OS level after launch, is not denied**
  (DEC-311): the sandbox skips glob deny paths on Linux, so only the names that exist at launch and the freeze flag
  carry literal rules. Inferred, not run: a project root whose path contains `*`, `?` or `[` would turn those literal
  rules into patterns the sandbox skips.
- **The shared git directory is writable from a launched session in a linked worktree.** It can commit (tested), and
  it can also create a new file directly in the main repository's `.git`, which includes other branches' refs;
  `.git/hooks` and `.git/config` are refused.
- **The held-out path travels in argv**: the built settings are an inline `--settings` argument, visible in the
  process list, the worker's own Bash included.
- **The per-session temp directory is left behind** after the session ends.
- **A research session starts in the repository root**, so a bare `uv add` is denied until it does `cd <folder>`. A
  new directory a research install creates inside the repository is stopped by neither the fence nor the guard, only
  reported by containment, and not at all if it is gitignored.

**What the launcher does not check**

- `~/.claude/settings.json` is not checked for bypass mode, added directories, `disableAllHooks` or a weak `sandbox`
  block (DEC-313 covers the command line and the project's settings).
- Option prefixes, another letter case and `--dangerously-skip-permissions=true` pass the launcher; the reviewer
  infers the real CLI rejects them, and nobody ran it.
- In force and stricter than some callers expect: `--setting-sources` is refused with any value, and a guard
  registered only in `.claude/settings.local.json` refuses the launch (DEC-314).
- `gov launch` ends with the session's exit code (DEC-332), so a session's own 1 to 4 reads like an API-0002 code;
  a refusal is told apart by its envelope.

**What the guard alone lets through** (left to the sandbox of a launched session)

- **Install spellings for non-research roles:** `env` and `command` prefixes (known from W1-04), `exec`, `nice`,
  `time`, `xargs`, `bash -c`, `python3 -mpip`, `uv pip sync`, `uv tool run`, `npm ci`, `npx`, `yarn add`, `pnpm add`,
  `pipx run`, `cargo add`, `go get`, a pipe into a shell. Stopped only by the empty allowlist and the write fence.
  For research: `uv --directory` or `--project`, `pip install --target` or `--user`, and `cd` behind an assignment,
  `builtin`, `command` or `eval`. An orchestrator subagent in a worker session gets "ask" for an install, not "deny".
- **`ln` behind a wrapper** (`env`, `command`, `nice`, `xargs`, `find -exec`, `bash -c`, backticks).
- **Links the guard does not see made:** a write through a hard link already on disk, or through a link made by an
  interpreter one-liner; replacing a symbolic link that already sits inside the acceptance tests and points into the
  role's paths; a link made by `cp -s` followed by a write in the same command.
- **Other programs that take options after operands** (`touch -d`, `tee`, `rsync`, `dd`) are not read the way `cp`
  and `install` now are.
- **An opaque Bash write is not judged**: an engineer changed a guard file inside its own paths with a Python script
  fed through a here-document, and the guard allowed it, while it refuses the orchestrator's here-documents. The
  holder exception follows a symbolic link: if `.claude/settings.json` were a link into scratch, any role could
  write the path there.
- **On a ticket whose `allowed_paths` name `.tickets/` or `.claude/`**, the guard alone allows writes there; only a
  launched session carries the deny rules. DEC-315 has no exception for such a ticket: in a launched session the
  deny rule stays (fail closed), which is why no headless session could write `.claude/agents/research.md` and the
  owner placed it (DEC-312).

**Where the guard is stricter than needed**

- `ln -t`, `ln --`, a destination that is exactly the top directory of an allowed pattern, `ln <own> <own> -S bak`,
  and a hard link whose source is outside the role's paths even when the source is harmless (a file under `docs/`).
- A link to a protected place plus any other write in the same command; `ln -s <relative name>` plus any other
  write; `cp -t <dir>` with a glob operand that matches nothing; `cp a b dir -p` judges the later sources as write
  targets too.

**The generic command line (DEC-317)**

- A stray command module that hard-exits at import makes `gov --help` and a misspelt command end with exit 0.
- A stray `src/gov/status/command.py` takes over `gov status`; `status` and `check` have no precedence guard.
- No acceptance test shows that a new module alone adds a command, its arguments and its act paths. W1-25 was the
  first user and needed no change to `main.py`.

**Carried to other tickets**

- **W1-08's `systems` snapshot** in the path map still shows the launcher and the research role as before this
  ticket; it is updated when W1-33 lands the remaining role definitions.
- **The experiments root is the fixed name `experiments/`** (DEC-333); a project key waits for a project that needs
  one.
- **Size.** 819 lines added outside tests against an estimate of 220, about 200 of them the DEC-317 change that
  W1-25's package moved here; 214 acceptance cases were added after implementation, almost all for owner and
  delegated decisions.

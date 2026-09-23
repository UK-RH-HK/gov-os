# Probe P2 — loader falsification probe: RESULT

| Field | Value |
|---|---|
| Run by | the Phase-2 outer orchestrator, 2026-09-23, on the deployment machine |
| Authorised by | the owner's Phase-2 completion decision, §3 — *"run the outstanding research probe P2 before implementing the selected execution architecture"* |
| Question | Can the proposed `ResolvedExecution` guarantee verify one object while the kernel/loader causes **unverified executable code to run before the first reviewed instruction**? |
| **Answer** | **YES. The attack succeeds.** |
| **Disposition** | **Does NOT falsify the authorised architecture.** It extends the closure. Incorporated; work continues automatically per §3. |

## Why this does not stop the phase

The owner's §3 sets the test precisely: stop only *"if the finding materially falsifies the authorised architecture
rather than requiring an ordinary implementation refinement."*

The authorised Property A is:

> The OS executes a kernel object it holds, never a name it was handed — **and nothing inside that object may silently
> name a second unverified executable object before the first reviewed instruction.**

An ELF's `DT_NEEDED` + `RUNPATH` is *exactly* "something inside the object naming a second executable object". The
probe therefore confirms the property's necessity and identifies one more member of the closure it must cover. **The
architecture is unchanged; its closure is extended.** Stopping would be wrong.

## The measurement

**Test object**: `tool`, a dynamically-linked ELF — the artefact the OS would pin, hash and verify.

```
$ readelf -d tool
 (NEEDED)   Shared library: [libhelper.so]
 (NEEDED)   Shared library: [libc.so.6]
 (RUNPATH)  Library runpath: [$ORIGIN]        ← recorded INSIDE the verified object
```

**Conditions** — the strongest the authorised architecture offers: environment **fully cleared** (`env -i
PATH=/usr/bin:/bin`), working directory pinned, execution by **resolved absolute path**.

| Run | Output |
|---|---|
| **Control** — benign `libhelper.so` | `FIRST-REVIEWED-INSTRUCTION-REACHED` → `benign helper` |
| **Attack** — only the *unpinned* `.so` swapped | **`UNVERIFIED-CODE-RAN-BEFORE-MAIN`** → `FIRST-REVIEWED-INSTRUCTION-REACHED` → `evil helper` |

**Effect measured, not inferred**: a file was written **outside the project root** by the `.so`'s
`__attribute__((constructor))`, containing `written by unverified .so constructor`.

**The pinned artefact was never touched:**

| | sha256 |
|---|---|
| `tool` **before** | `6bbc5518e234ffc1a08463aadf7a74ebbbb502fbf4a7eb511fbb3fd482acbc6a` |
| `tool` **after** | `6bbc5518e234ffc1a08463aadf7a74ebbbb502fbf4a7eb511fbb3fd482acbc6a` |

**Identical. Verification would pass.** Loader resolution confirmed via `LD_TRACE_LOADED_OBJECTS=1`:
`libhelper.so => <project>/libhelper.so`. The in-place library's digest matched `libhelper.so.evil`
(`34ddd21a…05ac1`), confirming the swap.

**The decisive property: `RUNPATH` lives inside the ELF, not in the environment.** Clearing the environment cannot
reach it. This is the shebang finding's exact shape, one layer lower — the loader performs a **second resolution from
data inside the verified object**.

## Structural mitigations, measured — no denylist required

| Variant | Result |
|---|---|
| **Static link** | `0` dynamic entries — **the closure is the file itself**. Structurally immune. |
| **No `RUNPATH`** | Loader **fails**: `cannot open shared object file`. Project-controlled resolution removed; the artefact simply does not run. |

Both outcomes are *structural*, which is why the fix is not another list.

## The required closure extension

Per the owner's §3 — *"DO NOT add that dependency to another denylist"* — the rule generalises without naming anything:

> **An ELF artefact's `ResolvedExecution` closure includes its dynamic-dependency closure.** Resolve `DT_NEEDED` the
> way the loader will (`RUNPATH`/`RPATH` with `$ORIGIN` expansion, then system paths); **open, verify and bind every
> resolved object**, or the execution is `UNDETERMINED` and takes the governed route.

Three consequences fall out, none of them an enumeration:

1. A **statically linked** artefact needs nothing extra — its closure is itself.
2. An artefact resolving **only** from authenticated system paths inherits the machine floor.
3. An artefact whose resolution can reach **project-controlled** paths carries those objects in its closure and they
   are verified like any other — or it gates.

`LD_PRELOAD`, `LD_LIBRARY_PATH` and `LD_AUDIT` are *separately* handled by the constructed environment (Property A
obligation 3) and are **not** what this probe demonstrates. The probe deliberately defeated environment control to show
that environment hygiene alone is insufficient.

## Scoring

**Six for six.** Every time this study has asked "does a second resolution happen below the level we just secured?",
the answer has been yes: argv → wrapper arguments → shebang → dynamic loader. Each was found by execution, never by
inspection.

**What this predicts, and what must therefore be stated as a limit rather than assumed closed:** the honest inference
is *not* that the loader is the bottom. Candidates below it, none probed: `LD_AUDIT`/`ld.so.preload` at machine scope
(outside the project's authority, but inside the machine's); interpreter-internal module resolution (`PYTHONPATH`,
`NODE_PATH`, `GEM_PATH`) for a pinned script whose interpreter is verified but whose *imports* are not; and setuid or
capability-bearing binaries. **These are recorded as known-unprobed, not as closed.** The implementation should state
its guarantee as *"every executable object the kernel and dynamic loader resolve before the first reviewed
instruction"* — and say plainly that what a verified interpreter subsequently imports is Level-3 territory, governed by
OD-P2-05 clause 4's independent review, not by this property.

## Reproduction

`scratchpad/p2probe/` — `tool.c`, `libhelper_benign.c`, `libhelper_evil.c`, build commands inline above. Nothing in the
repository was touched; the marker was written to a scratch directory outside the probe's project root, by design.

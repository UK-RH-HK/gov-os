
## W1-27 residuals (gov doctor and gov rebuild, 2026-10-07)

- **Built:** `gov doctor [--json]`, a read command with eleven sections (tools, hooks, path map, path
  compliance, index freshness, canaries, framework lock, isolation, Claude Code, held-out file, adoption
  level); exit 3 when unhealthy. `gov rebuild` recreates the derived stores through the code that owns each
  (the record store, the lexical index with its secrets filter, the semantic index and the code index when
  their tool answers) and names each outcome; it returns `digest`, `store` and `stores`. The check
  `gov.rebuild.check` is the recovery/rebuild family check. `gov` validates the path map against W1-08's
  schema; W1-07's provisional cases were revised in this ticket's test design (DEC-228).
- **Rules decided on the way (DEC-440, DEC-448, DEC-452):** an error in a measurement is a failure and an
  absent component is "unmeasured", never the top adoption level; doctor looks for a tool under its own
  registry entry's PATH prefix, then under every prefix the registry carries, then on PATH; a tool passes only
  by a version read and equal to the pin or, where no version can be read, by a hash computed and equal to the
  pin; historical records (the register, CIT records, this file, archived sources) are left out of the
  stale-path check, and the section says how many files it left out.
- **KPI line 6 against DEC-210:** the extension newer than the CLI, both above the minimum, is reported as
  drift and makes doctor exit 3. The owner called this drift harmless (DEC-448); it is re-recorded at the
  Wave 1 exit.
- **Doctor knows six registry entries by name** (`pyyaml`, `superpowers`, `sqlite-vec`, `qwen3-embedding`,
  `reranker-venv`, `reranker`): where each is and what its registered hash is the hash of is written in the
  code, not in the registry. A generic kernel command that knows this repository's tools: the registry needs
  a field for "what the hash is of and where", for the adoption tickets. It computes the vendored folder's
  digest with its own function.
- **A registry entry's PATH prefix is read out of its install command** (`PATH=…:$PATH`); the registry has no
  field for a tool's location. Node's own entry carries none and is found through the prefix of other
  entries.
- **`reranker-venv` passes by the versions in its package metadata,** not by its registered hash (the hash is
  of a package listing made with a tool; `sha256_match` is false for it). The local version suffix of torch
  (`+cu130`) is not compared. `pyyaml`, `ccusage`, `bubblewrap` and `socat` pass by version only: their
  registered hashes are of packages that are not on the machine.
- **Doctor takes about 7.5 s here:** it hashes the embedding model (610 MB) and the reranker model (1.14 GB)
  on every run.
- **Rebuild takes about 157 s on a project of about 955 tracked files** (the secrets filter runs on every
  file), 2.5 s on three files. The suite's rebuild cases run on a small project, and five of W1-07's cases
  that ran every command on a copy of this tree were revised to run rebuild on a two-file project.
- **Rebuild without a path map returns its envelope** with the lexical index named as not recreated and the
  reason; an owner of a store that raises gives the error `REBUILD_FAILED` with the store and the text. An
  optional index (semantic, code) whose tool errors is named `not_recreated` with the reason and exit 0.
- **The recovery check with no store exits 1** ("unmeasured"), so the recovery/rebuild family is not green in
  a project that was never loaded.
- **Earlier defects found by reading the code against the KPI clauses, each fixed test-first:** rebuild wrote
  the lexical index itself, past the secrets filter, and into another module's tables; a false reason "no code
  index module exists"; a tools case that asserted a key name; `socat` passing with no version read and no
  hash match; six entries reported as "hash matched" because a folder existed; three "healthy project" cases
  that depended on this machine's home; rebuild ending in a traceback on a project with no path map; three
  cases that imported the package into the test process and passed only where PYTHONPATH was set.
- **Records:** commit `2e6ec15b` (engineer) names "Claude Opus 4.6" as co-author. Temporary folders
  `/tmp/gov-launch-engineer-en6s9b8e` and `/tmp/gov-launch-engineer-4mcz3fb1` were left by launches. The
  containment check flagged `94bc7635` (a merge-back's own change to W1-07's support file).
- **Learning metrics:** three lead starts, then five designer-and-engineer rounds started by the orchestrator
  (rounds 4 to 10); two review rounds (the limit); 117 cases, of which about 30 were revised after
  implementation began and about 50 added after it; 943 lines of source against an estimate of 230. Every
  section of doctor maps to a KPI clause; the estimate was wrong, not the scope.
- **Regression at `MERGEID`:** REGLINE

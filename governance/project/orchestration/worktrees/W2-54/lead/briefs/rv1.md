You are a fresh reviewer. Ticket DAEO-0rfi (W2-54, "The context packet's dropped list in a stable order; the context check's declared time limit; the audit-report type"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-54` on branch `w2/W2-54`, at the head `7661402c041b048d637977ef4c3be5f11a729aa3`, and its acceptance tests pass. You probe that head for behaviour the tests miss, on the ticket's whole change since its base `b644d28a`. You write nothing in the repository. You were started through `gov launch` as `independent-auditor`, under its OS sandbox.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0rfi','w').write('x')"` must **fail**. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must **work**. If (a) wrote the file or (b) failed, stop there and return, naming what happened (never delete a file (a) made).

## The threat model you judge against (the owner's DEC-801, DEC-808)

Reviewers and probes judge against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round. Only a finding an honest agent can hit in ordinary work, and that fails open or loses work, justifies a round.

Ask of every finding these two questions: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"

Every finding in your return carries these two lines, under it:

    Ordinary work: yes|no, because …
    Consequence: fails open|loses work|other

A finding marked "no" is a row, never a round.

## Standing rules (read first)

- Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-0rfi`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-54` and `w2/W2-54`) and `git log --oneline -1` (expect `7661402c`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A foreground command is killed at 10 minutes: give long commands the Bash tool's `timeout: 600000`.
- You write nothing, so no commit of yours will exist: return when your findings are complete. Write no file of the repository and make no commit; keep every throwaway file in your session's temporary folder (`$TMPDIR`, as a literal path). No subagents. Install nothing. No push, merge, rebase or tag.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no stash in this worktree. Reading another commit with `git show <commit>:<path>` is allowed (W2-02's branch included: `git show 2a35fd7b:<path>`).
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one in your temporary folder; a throwaway stand-in imports the package from this worktree's `src/` or copies single named files, never `governance/project/`. No clone, copy or file of a programme under a `.gov-runtime/` folder (DEC-673).
- Never write the main tree (`/home/usain/Dynamic-Agentic-Engineering-OS/`) or another worktree, and never this worktree's `.gov-runtime/` store: a probe that needs a store builds one in a temporary project.
- **Inside your sandbox `gov` reaches no shared Ollama** (`127.0.0.1:11434`) and the GPU is hidden; an Ollama that `gov` starts inside the sandbox runs on the CPU. Probe with stand-in embedders (the suite's support module `tests/acceptance/W2-54/w2_54_support.py` has them) and say which findings you could not reproduce for that reason. Never stop, restart or reconfigure a server you did not start; never pull, remove or create a model.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. The sandbox may show placeholder files in the worktree (`.bashrc`, `.mcp.json`, `docs/source`, …): they are not the ticket's.
- Never run `gov rebuild` on this worktree, never `gov rebuild --no-embeddings` anywhere; never `gov close`, `gov adopt` or `gov pause`.
- Never edit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` (its sha256 must be `b14e17d6e71b2727c3cea123dec112fdccbeb27afc1f50b67f5e27294ecdac1d`).
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0rfi.md`: its KPI lines and its `allowed_paths`.
- The ticket's change: `git log --oneline b644d28a..7661402c` and `git diff b644d28a..7661402c -- src template tests/unit`; the change record `docs/changes/W2-54-CIT-E.md`; the acceptance suite `tests/acceptance/W2-54/` (README first) and the W1 fixture changes (`git diff b644d28a..7661402c -- tests/acceptance`).
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-768, DEC-773, DEC-595, DEC-626, DEC-441, DEC-565, DEC-260, DEC-261, DEC-379, DEC-413, DEC-414, DEC-462, DEC-136, DEC-732. And these, staged for the owner's commit and not yet in the register (apply them as written here):
  - DEC-782 (P-W2-32 (a)): a read command (`gov retrieve`, `gov context`) may write the query-vector cache and nothing else: one derived file under `.gov-runtime/`; keyed by model, model revision and a hash of the exact text; atomic writes, safe with several sessions at once; bounded in size (DEC-797: `GOV_QUERY_VECTOR_CACHE_MAX_BYTES`, default 64 MiB); rebuildable from nothing. A cold, full, deleted and unwritable cache all give the same vector for the same text.
  - DEC-798 (P-W2-40 (b)): a CPU-only embedder that `gov` starts on its own port (`GOV_QUERY_OLLAMA_HOST`, default `127.0.0.1:11435`, started with `CUDA_VISIBLE_DEVICES=-1`, DEC-811 item 5) answers query embeddings, and only those; the shared GPU runner (`OLLAMA_HOST`) keeps building the index; no request to the shared runner names `num_gpu: 0` or any runner option; the cache key names the device; `gov` starts both daemons on demand and stops neither (DEC-261 as amended).
  - DEC-811: three acceptance cases in `test_w2_54_cpu_embedder.py` were rewritten after the implementation (`75049714`, each with a `Rewrite-Reason:`): reads that expect lexical evidence ask a phrase a fixture note holds; steps 5 and 6 of the first case ask new texts; the hit@5 case reads W1-21's headline figure. The builder test fixture in `tests/unit/semantic/test_semantic.py` gained round 4's call shapes (`a0cb797e`).

## What you probe for

Behaviour the acceptance tests miss, above all a case that could lose work, let a role write outside its scope, let an implementer change the acceptance tests, or make the guard or a gate fail open. In particular:

1. **The dropped list and the hash:** a context whose items or hash differ between two computations, for any ticket, with ties in score, with an empty store or a missing index; a tie-break that is not total.
2. **The declared time limit:** the context-reproducibility check's declared limit set so high that it hides a hang, or not fitting the measured run; the measurement not recorded or not reproducible (the change record's §§ on it).
3. **The `audit-report` type:** differing from W2-02's (`git show 2a35fd7b:template/governance/kernel/schemas/audit-report.schema.json`, and W2-02's lines for that type in `git show 2a35fd7b:src/gov/check/schema.py`) in any byte of its schema file or in its lines of `src/gov/check/schema.py`, or bringing anything of W2-02's other types (`close`, `adoption-verdict`); a record outside `docs/audit/` without `type`, or an audit report without `milestone`, `commit` or `pack_sha256`, passing core-schema; any hard-block check weakened; the W1-43 audit report touched.
4. **The query vector and its cache:** a text that gets two query vectors in one store, whatever was embedded before it; a stored vector used for another model, another model revision, another device or a different text (case, spacing, Unicode form, a trailing newline); a stored vector that a failed or partial embedding call leaves behind; a read that writes anything but the cache file; a key that is not a hash of the exact text or misses the model, its revision or the device; a torn, lost or duplicate entry when several processes write at once; a cache that grows past its bound; a result that changes when the cache is deleted, full or unwritable; the cache written outside the repository's store or read across worktrees.
5. **The CPU-only embedder (this round's limits):** a query vector computed by the shared runner served as a CPU one; a request that moves the shared runner to the CPU (any runner option in a request to `OLLAMA_HOST`); a CPU embedder that answers anything but query embeddings (an index build, a rebuild, a refresh sent to it) or binds a port another session holds (a second daemon started while one serves, another port taken silently, a fall-back to the shared runner when the CPU address is held or nothing can be started); a cache key without the device.
6. **The acceptance tests:** a rewritten W1 or W2-54 case whose pass line, threshold or expectation moved (DEC-811's three rewrites and the W1 fixture changes: each with its `Rewrite-Reason:`); an implementer commit that changed `tests/acceptance/**` (check each commit's `Role:` trailer against the paths it changed).

Run the code; do not judge it by reading alone (the suite's support module builds temporary projects with stand-in embedders; `gov retrieve --json --root <project>` and `gov context --json --root <project>` are the read commands). A finding you could not reproduce is marked as such.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Nothing comes before the twelve fields. Refused twice for the same call, stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

After the twelve fields, the payload: **the probe record's body** (Markdown, no frontmatter; the lead adds it), beginning with your verdict on one line, `Verdict: pass` or `Verdict: fail`, then: the head you probed; step 0's result; the `gov.__file__` line; what you probed and found sound; and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`). Your verdict is `fail` only if a finding is marked both `Ordinary work: yes` and `Consequence: fails open` or `loses work`; otherwise `pass`, with the other findings as rows. You repair nothing (MR-4).

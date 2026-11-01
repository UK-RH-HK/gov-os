You are the ticket lead for ticket `DAEO-jsg1` (`W2-86`, "The kernel template is embedded as the path map means it: template/ except vendored code, the vendored parts a namespace of their own"). It is profile STANDARD, the first of the owner's memory quick wins, and you work only in the worktree `/home/usain/gov-os-worktrees/W2-86` on branch `w2/W2-86`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `8d513849fb0c`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-jsg1.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-86");
- DEC-952, DEC-388 (DP-8 above all: it names this value and this fix), DEC-381, DEC-694, DEC-941 (item 1), DEC-833 (item 3), DEC-860 and DEC-951 (item 5);
- lens B's F6, `docs/assessment/2026-10/B-memory-retrieval.md` (the finding at line 520, and the policy value at line 633);
- W2-61's baseline, on its branch: `git show a9a25960:docs/research/W2-61-baseline.md`, §4 to §6 for the figures and §8 for how the measure is repeated;
- `src/gov/retrieval/semantic.py`, `EMBEDDED` (line 44) and `_wanted` (lines 206 to 220): the indexer's selection;
- `governance/project/path-map.yaml`, its header (lines 1 to 3) and its `namespaces:` block (lines 6 to 133), above all `kernel-template` (lines 84 to 93);
- the vendored parts: the `superpowers` entry of `governance/project/tool-registry.yaml` and `template/governance/kernel/skills/superpowers/vendored.yaml`.

## Why you start now

- **The owner ordered quick wins first** (DEC-952), before the longer memory chain, each re-measured with W2-61's measure.
- **W2-61's baseline (visible half):**
  - hit@5 8 of 20 (40 %, against CAP-10's floor of 85);
  - full evidence 12 of 20 (60 %, against the owner's target of 99 %);
  - in the bundle 14 of 20.

- **Since then, W2-87's authority order (merged and closed 2026-10-31):** hit@5 11 of 20 (55 %), full evidence 11 of 20 (55 %), in the bundle 15 of 20 (W2-87's re-measure at `cffef92c8534`). Your control run at `8d513849fb0c` includes it.

  Q18 and Q19 miss because their governing sources have no vectors: `template/governance/kernel/hooks/precompact.py` and the role files.
- **The cause is the path map, not the indexer.** `path-map.yaml:91` says `embedded, except vendored code`. The indexer embeds only the exact value `embedded` (`semantic.py:216`), and DEC-388 reads any other value as not embedded (fail closed). DEC-388 named the fix: the vendored paths get their own namespace, so the rest of `template/**` can say `embedded`. Nothing in the code changes.

## The decisions for this run

- **The path map: these lines only (DEC-952).** The briefs have kept the path map as the orchestrator's and the owner's (DEC-757 and DEC-766, for the ratchet lists). DEC-952 lets this ticket edit its `namespaces:` block:
  - `kernel-template` changes its `paths` and its `embedding_policy`;
  - new namespaces go beside it.

  Nothing else in the file changes. Your check: `git diff 8d513849fb0c -- governance/project/path-map.yaml` touches only lines inside `namespaces:`. If DEC-952 is not in the register when you start, return PACKAGES.
- **What is embedded and what is not:**
  - **Embedded (`kernel-template`, `embedding_policy: embedded`):** every tracked file under `template/` but those below. Among them are the role files, the hooks, the kernel skills (`template/governance/kernel/skills/<name>/SKILL.md`) and `skills/superpowers/vendored.yaml`, which is the kernel's own record.
  - **Not embedded: vendored code,** in a new namespace:
    - `template/governance/kernel/vendor/**`;
    - the kernel's copies of the vendored skills, `template/governance/kernel/skills/superpowers/<skill>/**`;
    - the vendored tk, `template/governance/kernel/bin/**`.
  - **Not embedded: the generated adapter copies,** `template/.rulesync/**`, in a new namespace. The root's `.rulesync/**` and `.claude/**` are already not embedded, and the copies would put each kernel skill in the index twice.
  - **Every new namespace** carries every field `kernel-template` has, with `embedding_policy: not embedded` written exactly.
  - **Exactly one namespace for every tracked path under `template/`** (the header's rule). So `kernel-template`'s patterns are narrowed (`**` crosses folders, `*` stays inside one), never left overlapping.
- **Tests, minimal and in proportion** (DEC-951 item 5), **in parallel with the engineer** (the common brief's work order, DEC-963): a fresh independent test designer (launched sandboxed from the `W2-86-tests` worktree, `--effort high`; its brief must not set `TMPDIR`; its retrieval from the integration branch's store) writes `tests/acceptance/W2-86/`. Three cases and a short README, about 100 lines in all:
  1. Every tracked file under `template/` (by `git ls-files`) is in exactly one namespace. The indexer's selection takes the role files, the hooks, the kernel skills and every other file but the vendored set and `template/.rulesync/**`, and takes none of those. Drive the selection as the semantic route applies it, over a planted table of chunk paths in a temporary folder. No embedder and no rebuild.
  2. Every namespace's `embedding_policy` is `embedded` or `not embedded`, exactly.
  3. For every tracked path outside `template/`, the selection's verdict is the same under this worktree's path map as under the path map at `8d513849fb0c` (`git show`). The README names that base.

  Cases 1 and 2 must be red on today's map. Case 3 is a guard, green before and after; the README says so.
- **The engineer** (fresh, launched sandboxed, `--effort medium`) edits only the `namespaces:` block of `governance/project/path-map.yaml`. It may add a builder test as new `tests/unit/retrieval/test_w2_86*`, or none. In a later batch it writes `docs/research/W2-86-memory-measure.md` from your outputs.
- **Fail closed:**
  - no vendored file is embedded;
  - no path under `template/` is in no namespace, or in two;
  - no value but the two;
  - no change to the indexer's code.
- **Running beside you:**
  - **W2-87's** `retrieval_authority` block is merged; **W2-78** is parked. Other tickets edit other lines of the path map only by a merge back.
  - **W2-19** holds `path-map.schema.json`. **W2-23** holds `template/governance/project/path-map.yaml`.
  - **W2-76** (closing) and **W2-107** (running) hold `src/gov/rebuild/**`.
  - **W2-95** (running) holds `src/gov/check/pathmap.py`, the check that reads your namespaces: run it, never edit it.
  - **W2-32 and W2-13** hold `src/gov/retrieval/**` and `tests/unit/retrieval/**`. They are open; write only new `test_w2_86*` files there.
  - **W2-61** holds `src/gov/retrieval/measure.py`: you run it, never edit it.
  - **W2-84** (closing) holds `src/gov/guard/reads.py`.

  Do not touch their files. If your change needs one, return PACKAGES.
- **The re-measure, in your own session** (inside the sandbox gov embeds on the CPU, so a sandboxed worker's figures prove nothing):
  - **W2-61's measure is on `w2/integrate`** (merged and closed). Follow W2-61's §8, with these places:
  1. **Three clones by exact path,** each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>` and checked out detached:
     - `/home/usain/gov-os-runs/W2-86/head` at the engineer's path-map commit;
     - `/home/usain/gov-os-runs/W2-86/base` at `8d513849fb0c` (the control);
     - `/home/usain/gov-os-runs/W2-86/measure` at `w2/integrate`'s head (the measure's code and the visible set).

     Nothing goes under `.gov-runtime/` or in the main tree.
  2. **The stores, in `head` and `base`, built by the pinned gov:** `env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock gov rebuild --json`. Run it after the disk gate. Never `--no-embeddings`. The change is data, so the pinned gov is the code that reads it.
     - Record each rebuild's `digest`.
     - Record, from each store, the chunks with vectors under `template/governance/kernel/roles/`, `hooks/` and `skills/`, and under the vendored set and `template/.rulesync/`.
     - Record the paths whose vector set differs between `base` and `head`.

     The queries go in a script file under `.gov-runtime/scratch/lead/`, opening each store read-only (never `python3 -c` with braces, DEC-409).
  3. **The measure, visible half only, on each clone:** `env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-86/measure/src python3 -m gov.retrieval.measure memory-retrieval --root <clone> --sets-root /home/usain/gov-os-runs/W2-86/measure --part visible --gov /home/usain/.local/bin/gov --out /home/usain/gov-os-runs/W2-86/records --json`. Run `head` with `--compare` on `base`'s record. **Never `--part hidden`;** nobody here reads `fixtures/evaluation/**/hidden/**` in any tree.
  4. **The record** (a fresh engineer batch, from your outputs) goes in `docs/research/W2-86-memory-measure.md`, in W2-61's form. It holds:
     - the commits and the pinned gov's version;
     - both figures together, always: hit@5 against 85, full evidence against 99 %, and the in-the-bundle count;
     - for the head, the control, W2-87's figures (11, 11 and 15 of 20 at `cffef92c8534`) and W2-61's baseline (8, 12 and 14 of 20 at `23079f92a6fa`), side by side, in total and per question, with Q18 and Q19 named;
     - the vector counts and the vector diff.

     Leave the clones in place for the orchestrator. Give their paths, `du -sh` and `du -s --inodes` in your return.
- **Verification: scoped (DEC-968), in the close's form,** as the common brief's step 4 says: the selection tool's set (quote its scope and reasons); the full suite runs only in the nightly. The disk gate first; every rebuild under `flock /tmp/gov-os-rebuild.lock`.
  - **Look hardest at:**
    - `gov check --json` on this worktree's code: the path-map, config and schema families green;
    - `gov doctor`: no "no namespace is embedded";
    - W1-19's and W1-41's acceptance cases (embedding policy).
  - **Known:** W2-54's green-here cases may time out under load (row W2-L429), so re-run them alone. W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause.
- **No review (STANDARD).**

## This run's order

1. The test designer and the engineer in parallel (the common brief's work order); merge the tests branch; **check cases 1 and 2 red at `8d513849fb0c` and green on the engineer's commit yourself.**
2. The engineer's namespace block, judged against the spec and the ticket's KPIs, not the tests.
3. The re-measure (or its gate's skip), then the engineer's record batch.
4. Verify (scoped).
5. **Return** DONE or PACKAGES.
   - DONE means the branch is ready to merge. Give the figures beside the baseline and the control, or say that the re-measure is the orchestrator's.
   - Name as a row the residual this ticket leaves: an `embedding_policy` outside the two values is still read silently as not embedded outside adoption (a warning belongs to W2-76's or W2-22's files).

**Estimate:** about 25 lines of path map and about 100 of tests; about 6 hours:
- the tests and the engineer, about 1.5 hours;
- two rebuilds with embeddings and two measures, about 2.5 hours;
- the scoped run, about 60 to 90 minutes at today's load.

If your session nears its end first, write your checkpoint and return PACKAGES naming what is left; a fresh lead resumes from the checkpoint.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---

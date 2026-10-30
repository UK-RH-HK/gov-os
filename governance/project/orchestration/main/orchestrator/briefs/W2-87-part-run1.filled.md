**DEC-953 (owner, 2026-10-30), read with the common brief's DEC-953 block:** the Gov OS's features are lifted as gates on this repository's development; your ticket closes on the audit's 10 practices. Where this part names a lifted rule (the close queue, a ratchet list, re-probes after merges, the 90-minute budget), the common brief's DEC-953 block holds. W2-61's measure tool is merged (`758cd53f`). W2-03 is merged and closing in today's batch. The path map's `retrieval_authority` block is yours (DEC-952 item 1); nothing else in that file changes. Verify with `select_tests.py` as the common brief says.

You are the ticket lead for ticket `DAEO-s9qc` (`W2-87`, "Retrieval ranks by authority: for the same match, an accepted decision, the Contract, a specification or an ADR comes before a test or an assessment report, by an order the path map states"). It is profile STANDARD, the second of the owner's memory quick wins, and you work only in the worktree `/home/usain/gov-os-worktrees/W2-87` on branch `w2/W2-87`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `df0782fa4c4e`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**First, the register defect (owner, 2026-10-30): it is likely the largest cause of the 40 %.**
- **The defect:** `retrieve.py`'s `record_of` (line 52) maps every one of the register's 953 decisions to the register's single path. So every register chunk takes the newest entry's status, and the closure route (line 130) shares the fault.
- **The fix,** in its own test batch and engineer batch, before any authority order: a register chunk is ranked and filtered as the entry whose span holds it.
- **Then the re-measure** (W2-61's measure, visible half, both figures, beside the baseline). Then the authority order, then the re-measure again. Report both figures after each step in the return, so the owner sees what each part moved.

**Read first:**
- the ticket file (`.tickets/DAEO-s9qc.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-87"); W2-55's ticket (`.tickets/DAEO-arrl.md`), for the division below;
- DEC-952, DEC-866, DEC-423, DEC-424, DEC-791 (item 1), DEC-860, DEC-877, DEC-941 (item 1), DEC-833 (item 3) and DEC-951 (item 5);
- W2-61's baseline, on its branch: `git show a9a25960:docs/research/W2-61-baseline.md`, §5 (Q17 and Q20, and what took their first five) and §8;
- `src/gov/retrieval/retrieve.py` whole (262 lines), above all:
  - `_graph` (lines 43 to 60, and `record_of` at line 52);
  - the closure route (line 130);
  - `rrf` and the gathering cut (lines 135 to 151);
  - the drops (lines 181 to 200);
  - the rerank and DEC-424's order (lines 207 to 216);
- `src/gov/retrieval/fusion.py` (`rrf`, read only) and `src/gov/retrieval/rerank.py`;
- `src/gov/records/queries.py` (`records`, `edges`) and the register's records in `src/gov/store/loader.py` (lines 130 to 215: each entry's heading, span and status, W2-03);
- `src/gov/config/loader.py` (`load_config`, `_validate_path_map`) and `src/gov/config/path_map_schema.py`.

## Why you start now

- **The owner ordered quick wins first** (DEC-952), before the longer memory chain, each re-measured with W2-61's measure.
- **Tests and reports crowd out the governing sources.** In W2-61's baseline, Q17 and Q20 have their first gold at rank 21, outside the 20 items of the first call. Q20's first five are a W1-29 test, a W1-49 README and three assessment chunks. Lens B counted 37 of the 100 first-five places as tests.
- **Nothing in retrieval knows a source's authority.** The fused order (RRF) and one rerank decide everything. So the order goes in at the two places DEC-424's order already uses: before the cut and after the rerank.

## The decisions for this run

- **Design first, short.** The ticket's paths hold no note, so you write it in your scratch: `.gov-runtime/scratch/lead/design.md`, at most a page, in behaviour; it is a plan, not code. It says:
  - **the configuration:** one top-level block of the path map, `retrieval_authority`. It holds the tiers in order and the lift.
    - Each tier is matched by path pattern (`**` crosses folders, `*` stays inside one) and by the store's record type and status.
    - The first content:
      - governing: decisions whose status is ACCEPTED, the `capability` records and `docs/contract/**`, `docs/charter/**`, `docs/spec/**`, `docs/adr/**`, and the kernel's roles and skills;
      - reports and tests, below everything else: `tests/**`, `docs/assessment/**`, `docs/audit/**`, `docs/probes/**`;
      - the rest in the middle.
    - What a chunk in two tiers gets.
    - The note proposes the lift's value and says why.
  - **the lift:** how a tier changes the fused score before the cut, and the rerank's order after it. It is bounded: a lower-authority chunk whose match is better by more than the lift keeps its place. With the block absent, the bundle is today's, item for item;
  - **the register:** a chunk of `docs/DECISION_REGISTER.md` is ranked as the entry whose span holds it, found from the store's register records (W2-03), never as the register as a whole.
    - An entry that is SUPERSEDED (by status or by a SUPERSEDES edge), or whose status is not current (DEC-423), gets no lift.
    - The mapping is one function in `authority.py`, which W2-55 will reuse.
  - **what stays:**
    - what the bundle leaves out (W2-55's, below);
    - the budget, batches, continuation, stopping reasons and parent expansion;
    - DEC-424's records ahead of everything;
    - determinism, with ties in a stated order;
  - **fail closed:** a block that cannot be read, or that names an unknown tier, field or status, refuses with `CONFIG_INVALID`. It is never read as empty or as today's order.

  It goes into the test designer's and the engineer's briefs as text.
- **The path map: one new block only (DEC-952).** The briefs have kept the path map as the orchestrator's and the owner's (DEC-757 and DEC-766, for the ratchet lists). DEC-952 lets this ticket add its top-level `retrieval_authority` block; nothing else in the file changes. Your check: `git diff df0782fa4c4e -- governance/project/path-map.yaml` adds that block alone. If DEC-952 is not in the register when you start, return PACKAGES. The block needs no schema change: the schema sets no `additionalProperties`, and the loader refuses no unknown top-level key. If that turns out false, return PACKAGES (W2-19 holds the schema).
- **Tests first, minimal and in proportion** (DEC-951 item 5). A fresh independent test designer (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`) writes `tests/acceptance/W2-87/`: about six cases and a README, a few hundred lines at most.
  - **Everything planted** in a temporary repository built from scratch: a register with a superseding pair, a capability, a spec, an ADR, a test and an assessment report, all carrying the same matching text. The store is built there without embeddings, and the reranker is a stub passed in. Nothing reads this repository's store.
  - **The cases:**
    1. For the same match, every governing chunk ranks above every test and report chunk, without a reranker and with a stub that scores them alike.
    2. A governing chunk that the plain order leaves just past a small first call (a small `--batch-size`) enters it. A lower-authority chunk scored better by more than the lift keeps its place.
    3. Configuration decides: a planted path map that puts tests above decisions flips the order. With the block absent, the order is the plain fused one.
    4. An unreadable block, and a block naming an unknown tier, each refuse with `CONFIG_INVALID`.
    5. The superseded entry ranks below its successor. A register whose last entry by id is superseded keeps its other entries ranked as their own.
    6. Two runs on one store give the same bundle, and nothing kept or left out changes.

  Cases 1, 2, 3 and 5 must be red on today's code.
- **The engineer** (fresh, launched sandboxed, `--effort high`) works only in the allowed paths:
  - the new `src/gov/retrieval/authority.py`;
  - `src/gov/retrieval/retrieve.py`: the two calls, and nothing in what it drops;
  - the one block of `governance/project/path-map.yaml`;
  - new `tests/unit/retrieval/test_w2_87*`.

  In a later batch it writes `docs/research/W2-87-memory-measure.md` from your outputs.
- **Your own check against today's code:** with the block removed from a scratch copy of the planted repository, the bundle at `df0782fa4c4e`'s code and at the head's code is the same, item for item. Run each through a checkout's `src/` on `PYTHONPATH` (DEC-877), and keep the script under `.gov-runtime/scratch/lead/`.
- **Division with W2-55** (`DAEO-arrl`, open):
  - this ticket owns the order: the tiers, the entry mapping and no lift for a superseded entry;
  - W2-55 owns what is left out, superseded and done entries with their count (DEC-791 item 1), and the tags.

  So leave `_graph`, `record_of` and the drops as they stand, and name the `record_of` hazard (ticket body) in your return for W2-55.
- **Running beside you:**
  - **W2-13** (`DAEO-zqvn`) holds `fusion*`, `lexical*` and `src/gov/retrieve/**`: read only.
  - **W2-32** (`DAEO-0pyc`, open) holds `src/gov/retrieval/**` and `tests/unit/retrieval/**`. Take only `authority.py`, `retrieve.py` and new `test_w2_87*` files.
  - **W2-04** (`DAEO-u4oz`) holds `src/gov/context/**` and `supplementary*`. Its packets inherit your order, and must stay deterministic.
  - **W2-03** holds `src/gov/store/**` and `src/gov/records/**`: read only. **W2-61** holds `measure.py`: run, never edited. **W2-84** holds `src/gov/guard/reads.py`. **W2-76** holds `src/gov/rebuild/**`.
  - **W2-86 and W2-78** edit other lines of the path map. Whichever merges second merges back.
  - **W2-05** holds the git-environment lines across `src/gov/**/*.py`. If your code runs git, leave its environment as it stands.

  Do not touch their files. If your design needs a change there, return PACKAGES.
- **The re-measure, in your own session** (inside the sandbox gov embeds on the CPU, so a sandboxed worker's figures prove nothing):
  - **Gate: W2-61's measure must be on `w2/integrate`.** Check with `git -C /home/usain/Dynamic-Agentic-Engineering-OS log --oneline -1 w2/integrate -- src/gov/retrieval/measure.py`.
    - **If it names no commit, skip the re-measure.** Return DONE, and state that the re-measure is the orchestrator's after W2-61 merges.
    - **If it names a commit, measure as follows.** The change is code, so the retriever must be the code under test (DEC-877), and the stores are the same for both runs:
  1. **Three clones by exact path,** each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>` and checked out detached:
     - `/home/usain/gov-os-runs/W2-87/head` at the engineer's last code commit;
     - `/home/usain/gov-os-runs/W2-87/base` at `df0782fa4c4e` (only its `src/` is used);
     - `/home/usain/gov-os-runs/W2-87/measure` at `w2/integrate`'s head (the measure's code and the visible set).
  2. **The stores, in `head` only, built by the pinned gov:** `env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock gov rebuild --json`. Run it after the load and disk gates, and never while `CLOSE-RUNNING` or `NIGHTLY-RUNNING` exists. Never `--no-embeddings`. The store's code is not changed here. Record the `digest`.
  3. **Two launchers in `/home/usain/gov-os-runs/W2-87/bin/`,** written with the Write tool and made executable: `gov-base` and `gov-head`.
     - Each first line is `#!/usr/bin/env -S PYTHONPATH=<clone>/src <pinned python>`. `<pinned python>` is the interpreter on the first line of `/home/usain/.local/bin/gov`.
     - The body is the pinned launcher's: import `main` from `gov.cli.main` and exit with it.
     - **Before you trust a run,** its record's `retriever.gov_file` must name `<clone>/src/gov/__init__.py`. If it does not, stop the re-measure, and return DONE with the re-measure the orchestrator's.
  4. **The measure, visible half only, twice on `head`'s stores:** `env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-87/measure/src python3 -m gov.retrieval.measure memory-retrieval --root /home/usain/gov-os-runs/W2-87/head --sets-root /home/usain/gov-os-runs/W2-87/measure --part visible --gov <launcher> --out /home/usain/gov-os-runs/W2-87/records --json`.
     - Run it first with `gov-base` (the control), then with `gov-head`, using `--compare` on the control's record.
     - **Never `--part hidden`;** nobody here reads `fixtures/evaluation/**/hidden/**` in any tree.
  5. **The record** (a fresh engineer batch, from your outputs) goes in `docs/research/W2-87-memory-measure.md`, in W2-61's form. It holds:
     - the commits, the launchers' first lines and each run's `gov_file`;
     - both figures together, always: hit@5 against 85, full evidence against 99 %, and the in-the-bundle count;
     - for the head, the control and W2-61's baseline (8, 12 and 14 of 20 at `23079f92a6fa`), side by side, in total and per question, with Q17 and Q20 named;
     - every question whose first gold rank fell, with its rank before and after.

     Leave the clones in place for the orchestrator. Give their paths, `du -sh` and `du -s --inodes` in your return.
- **Verification:** in full, in the close's form (the path map is shared core), under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite, no full run and no rebuild. Wait, and go on the moment it is gone.
  - **Closes:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, start no worker, no suite and no rebuild.
  - **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00.
  - **Locks:** every full run goes under `flock /tmp/gov-os-verify.lock`, and every rebuild under `flock /tmp/gov-os-rebuild.lock` (DEC-939 item 2).
  - **Look hardest at:**
    - the retrieval suites: `tests/acceptance/W1-19/`, `W1-21/` (RETR-A-04's bundle among them) and W1-42's retrieval cases;
    - `tests/unit/retrieval/`, `tests/unit/semantic/` and `tests/unit/context/`;
    - `gov check --json` on this worktree's code. The retrieval-regression family says "unmeasured" without `GOV_DEV_TIERS`; say which it was.
  - **Known:** W2-54's green-here cases may time out under load (row W2-L429), so re-run them alone. W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause. A retrieval case that is red because the order changed is a finding: name the case, the old and new order and the decision it rests on, and return PACKAGES rather than edit it.
- **No review (STANDARD).**

## This run's order

1. The design note (yours, in scratch).
2. Tests first (the test designer), then **check red yourself.**
3. The engineer, then your own check against today's code.
4. The re-measure (or its gate's skip), then the engineer's record batch.
5. Verify in full.
6. **Return** DONE or PACKAGES.
   - DONE means the branch is ready to merge. Give the figures beside the baseline and the control, or say that the re-measure is the orchestrator's.
   - Name for W2-55 the `record_of` hazard and the entry mapping it should reuse.

**Estimate:** about 120 lines of code and about 300 of tests; about a lead-day:
- the design note and the tests, about 2 hours;
- the engineer, one 90-minute budget;
- one rebuild with embeddings and two measures, about 1.5 hours;
- the full run, about 95 minutes.

If your session nears its end first, write your checkpoint and return PACKAGES naming what is left; a fresh lead resumes from the checkpoint.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---

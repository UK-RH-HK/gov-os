"""DEC-953/954/957: writes briefs/<W2>-part-resume-dec954.md for the built tickets that still need a lead run (W2-51 is
close only). Each part = identity + state check + the ticket's own scope (pointing at its older, decided part where
one exists) + the common DEC-953 overrides, verification, installs, budget and return. @@HEAD@@ is filled by
brief_resume_dec954.py. Safe to re-run."""
from pathlib import Path

O = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
ACC = "tests/" + "acceptance"
CASES = str(O / "briefs/W2-90-cases.txt")

T = {
    "W2-05": dict(
        id="DAEO-0z8c", title="The git environment of every check, hook and helper; the settings re-sort",
        profile="FULL",
        status=f"one line only, `?? {ACC}/W2-05/test_zz_scratch_b1.py`. That file is expected: a stray (a docstring, no "
               "test) left by an earlier test designer. Your test designer removes it in its batch (or commits it, if "
               "it is real work); never you or the engineer",
        older="briefs/W2-05-part-run4.md",
        scope=f"""- **The answer in force:** DEC-951 item 2 (P-B1-1 (a)): a short test-designer revision of W1-02's deadline support, then W2-05 resumes.
- **What is left, from the run-4 part (its steps 3, 4, 6 and 7, with their texts):**
  1. **The W1-02 revision** by a fresh independent test designer, in `{ACC}/W1-02/` only, the behaviours exactly as the run-4 part's step 3 gives them, `Rewrite-Reason: DEC-951 (P-B1-1); DEC-783 item 2; W2-L160`. It also removes the stray file above.
  2. **Engineer batch 2:** `eng5-work-DRAFT.md` with the run-4 part's step-4 corrections (`@@B1@@` is `8b8a3baa347a`; `src/gov/guard/reads.py` is W2-84's: never changed, listed "after W2-84 merges"; W2-03's and W2-77's rows routed now).
  3. **Not yours, though `src/gov/**/*.py` is in your paths:** `src/gov/rebuild/**` (W2-76, running), `src/gov/retrieval/**` (W2-87, running), `src/gov/launch/launcher.py`, `role.py`, `record.py` (W2-60a), `src/gov/resources/**` (W2-20), `src/gov/impact/**` (W2-37), `src/gov/release/**` and `src/gov/lock/**` (W2-16): list their git calls in the sweep as "after <ticket> merges", change nothing there.
  4. **`gov checkpoint`,** committed before the review.
  5. **The FULL review** (none has passed for this work yet): the run-4 part's step 7, `--effort max`, read-only, sandboxed; commit the probe record only if it passes.""",
        hours="7 to 8"),
    "W2-84": dict(
        id="DAEO-m1u3", title="the hidden-set refusal in every tree", profile="FULL", status="nothing",
        older="briefs/W2-84-part-run1b.md",
        scope="""- **Why first:** memory's critical path. W2-61h, the hidden half of the measure, waits on your merge (DEC-950).
- **State:** the fix is in at code head `c0f35c87fd8a`; its own suites and the parallel phase were green before the merge. The orchestrator has now merged `w2/integrate` in (93 commits; check `git diff --stat c0f35c87fd8a HEAD -- src/gov/guard tests/unit/guard` and say what came in).
- **What is left:**
  1. **Verification** (below): `src/gov/guard` is shared core, so the selection will say `full`; run it once under `verify_lock.sh`. W1-05's latency cases under load: re-run alone, report both.
  2. **The FULL review** with your filled `briefs/rev-1.md` (JUDGEMENT.md word for word, `--effort max`, read-only, sandboxed), on the final head. It asks above all whether any route lets a measured session read a hidden part in any tree: an absolute path, another worktree, a run clone, a symlink, git's object store. It judges the product's guard (`src/gov/guard/`); this repository's own hook is now the five-rule hook (ACT 1), which is not under review.
  3. Commit the probe record only when it passes. A fail-open finding: one test batch, one engineer, the runs, review 2 (DEC-413).""",
        hours="2 to 3"),
    "W2-60a": dict(
        id="DAEO-cv58", title="The role, its skills and its model and effort loaded at launch; the launch record",
        profile="FULL", status="nothing", older="briefs/W2-60a-part-run2.md",
        scope="""- **The answer in force:** DEC-951 item 4, P-W2-60a-ROUND3 (a): round 3, the last under the owner's exception to DEC-413, scoped strictly to the items of the run-2 part's section "The five items, and nothing else", with its delegated items. If review 3 finds another fail-open case: PACKAGES, never a fourth round.
- **What is left, from the run-2 part (its steps 3 to 8):** one test batch (the minimum that shows each item: the owner on proportion, DEC-951 item 5), one engineer for items (i) and (ii), the verification below, `gov checkpoint` committed before the review, review 3 (`--effort max`, read-only, sandboxed), the probe record committed only if it passes.
- **DEC-957 (roles approved):** this ticket builds nothing beyond its listed items. The orchestrator merges W2-33's role default lines before your merge; that is not yours.""",
        hours="4 to 5"),
    "W2-67": dict(
        id="DAEO-9nys",
        title="Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions",
        profile="FULL",
        status=f"exactly one line, `?? {ACC}/W1-27/w2_67_td4_plant.py`. That file is expected: the inert plant DEC-920 "
               "item 5 keeps untracked; leave it. If it must go, your test designer removes it (or commits it, if it is "
               "real work), never you or an engineer",
        older="briefs/W2-67-part-resume.md",
        scope="""- **State:** all three declared rounds are built; round 1 is merged into `w2/integrate`; rounds 2 and 3 passed their review (`docs/probes/DAEO-9nys/PR-DAEO-9nys-run3.md`). The orchestrator has merged `w2/integrate` in (no conflict).
- **No fresh probe.** A passing review exists for every round, and DEC-953 dropped the staleness rule. A new review runs only if this run's repair changes code or tests, and then on that change only (`--effort max`).
- **What is left, from the older part (its steps 3, 4, 6 and 8; not its step 5 and not the `_check_probe` dry run, a lifted gate):**
  1. the verification below (`tests/conftest.py` is in your change, so expect `full`), with TD1C-A's case run outside the sandbox, as the run-3 probe record did, and KPI 4's count;
  2. at most one repair batch, in the files the older part's step 4 names;
  3. the open KPI parts named in the return, with no work on them: KPI 2's second half (worksteal re-measured in the nightly, which is frozen) and KPI 5's T-A3 rows;
  4. the list of later `w2/integrate` commits that touch your files (step 8).""",
        hours="2 to 3"),
    "W2-49": dict(
        id="DAEO-ha8z", title="Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P)", profile="STANDARD",
        status="nothing", older="briefs/W2-49-part-mergeback.md",
        scope="""- **Start check:** `git merge-base --is-ancestor w2/W2-51 HEAD` must succeed: W2-51's validator (`docs/plan/tools/validate_w2.py`) must be in your tree. W2-51 merged is enough; its close is not needed (DEC-953). If it fails, stop and return PACKAGES.
- **What is left, from the older part (its steps 2, 3, 5, 7 and 8; its step 1's merge is done, but run its two checks):**
  1. tests first by a fresh independent test designer (`--effort high`): KPI line 3 and the failure line against W2-51's validator, DEC-745 item 2's eight source-map rows, DEC-750 item 5's `CAP-45.a.md` and status lines; nothing that fixes DEC-841's nine items either way;
  2. a fresh product-spec worker: the eight `SOURCE_MAP.csv` rows, `CAP-45.a.md` regenerated and every capability record's `status:` ACCEPTED, one CIT-E line each; no Contract text changes;
  3. the verification below, plus W2-51's validator over the merged tree once, quoted;
  4. return PACKAGES with P-A (DEC-841: the CIT-P addendum the owner approves before the nine items move) and P-B (DEC-825 item 3), as the older part's step 8 gives them, and the branch state as DONE would give it.
- **Merge order (the orchestrator's):** W2-51, then W2-49, then W2-52, then W2-16 (stacked on you, DEC-752, DEC-786).""",
        hours="4 to 5"),
    "W2-52": dict(
        id="DAEO-siiz", title="The lite A7 and A10 stage records", profile="FULL", status="nothing",
        older="briefs/W2-52-part-mergeback.md",
        scope="""- **The answers in force:** DEC-814 (P-6: `.claude/skills/adopt/SKILL.md` regenerated by rulesync, nothing else); DEC-810 (P-7: F-1 and F-3 are rows W2-M378, W2-M379).
- **What is left, from the older part (its steps 2, 4, 5, 6 and 7; step 1's merge is done, but run its two checks):**
  1. a fresh engineer regenerates `.claude/skills/adopt/SKILL.md` with rulesync from `.rulesync/skills/adopt/SKILL.md` (Node 22: `PATH=~/.nvm/versions/node/v22.23.3/bin:$PATH`), and nothing else; any other file rulesync would change is named and returned as PACKAGES;
  2. the verification below; `gov check`'s adapter-portability line quoted;
  3. **a review of the new change only:** your probe at `643aeeef` passed (`docs/probes/DAEO-siiz/PR-DAEO-siiz.md`) and DEC-953 dropped the staleness rule, so the fresh reviewer (`--effort max`, read-only, sandboxed) judges the regenerated skill against its rulesync source and against the stage records it describes; commit `PR-DAEO-siiz-run3.md` only if it passes;
  4. before the reviewer starts, the older part's check on `w2/W2-49` (if W2-49's run 3 moved it with a change to `docs/contract/**`, `docs/changes/**` or its tests, merge `w2/W2-49` in and re-run W2-49's and W2-52's suites).
- **Merge order (the orchestrator's):** after W2-49.""",
        hours="3"),
    "W2-37": dict(
        id="DAEO-6n5k", title="gov impact", profile="FULL", status="nothing", older=None,
        scope=f"""- **Read:** your lead checkpoint's "For the resume lead" section; review 2's draft `.gov-runtime/scratch/lead/probes/PR-DAEO-6n5k-round-2.md`; DEC-812, DEC-815, DEC-816, DEC-859 and the ticket's card in `docs/plan/WAVE_2_WBS.md` ("#### W2-37"). W2-03 is merged into your tree (its close runs in the orchestrator's batch).
- **The answers in force:** DEC-812 (A and B fixed in this resume, C, E and F4 ride along, D, F5 and F7 are rows; P-7 (a): `src/gov/check/commands.py`'s line recording `impact`, and `impact` in W1-07's lists and W1-32's command-set assertion, by your test designer with a `Rewrite-Reason:`); DEC-815 (depths 1, 3, 8 hops; `depth_source` names DEC-815 in `readings.py`); DEC-816 (the change skill's impact-assessment section routes to `gov impact`, in the template and its three rulesync copies); DEC-859 (the code graph by targeted traversal and pages, `src/gov/codeintel/**`; its KPIs). The orchestrator adds these paths and DEC-859's KPI lines to your ticket file in the main tree before you start; you never edit `.tickets/`. If `.tickets/DAEO-6n5k.md` lacks them, stop and return PACKAGES.
- **What is left:**
  1. **tests first,** a fresh independent test designer (`--effort high`): A (`--compare` reads the proposal as the store holds it, or refuses `matches: true` while the CIT-P file differs from HEAD); B (a register the path map names, differing from HEAD, makes `graphs.record` `stale`, even with no entry at HEAD); C, E, F4 as behaviours; the depth source; the skill routing; DEC-859's KPIs (no query over the tool's row cap, on this repository and a synthetic one well over it; the callers of `rrf` and `indexable` answered); `impact` in W1-07's and W1-32's lists;
  2. **one engineer** (fresh, `--effort high`) for all of it, in the widened paths only;
  3. the verification below;
  4. `gov checkpoint`, then **a fresh FULL review** (none has passed: review 2 failed on A and B), `--effort max`, read-only, sandboxed, with JUDGEMENT.md word for word; commit the probe record only if it passes. If DEC-859's part alone grows past this run, return PACKAGES with its cost and the rest DONE.
- **Shared line:** `src/gov/check/commands.py` is also W2-20's and W2-16's (one line each); change only your `impact` line. Whichever merges second merges back.""",
        hours="8 to 10 (DEC-859's part about 4 of them)"),
    "W2-16": dict(
        id="DAEO-49o5", title="Immutable, hash-pinned releases (CAP-43.b lite)", profile="FULL", status="nothing",
        older=None,
        scope=f"""- **Read:** your lead checkpoint (RESUME HERE, "What the resume lead must do"); the probe `docs/probes/DAEO-49o5/PR-DAEO-49o5-last-round.md` (passed); DEC-767, DEC-771, DEC-772, DEC-752, DEC-753.
- **The answers in force:** P-R3-1, P-R3-4 and P-R3-5 are deferred to W2-17 and W2-18 (DEC-771): not yours. P-R3-2 (a) (DEC-767). P-R3-3 = DEC-772 item 1.
- **What is left, one round (DEC-772: "that round does only this"):**
  1. **tests first,** a fresh independent test designer (`--effort high`): DEC-772 item 1 as behaviours (`gov release` refuses with a Claude Code process among its ancestors, with `GOV_ROLE` or `GOV_TICKET` set, or without a terminal, and asks for a typed one-time code); P-R3-2's one-line rewrite of R3-F5 (the case copies into a fresh folder), `Rewrite-Reason: DEC-767`; and, only if W2-20's change to `src/gov/check/commands.py` is already in your tree, W1-07's `release` list entry (DEC-753), `Rewrite-Reason: DEC-753`;
  2. **one engineer** (fresh, `--effort high`): DEC-772 item 1 in `src/gov/release/**`; the `release` line in `src/gov/check/commands.py` under the same condition. If W2-20's change is not in your tree, leave the line, and name W1-07's and W1-26's "release unrecorded" cases as known reds with DEC-753 item 3 as their reason;
  3. the verification below;
  4. **one review of the round's change only** (DEC-772, DEC-767): `--effort max`, read-only, sandboxed; commit its probe record only if it passes.
- **Not this run:** the numbered, frozen release for W2-81 and EXAMIN's copy (DEC-954 Q8c) and any tag: the owner's acts, later.
- **Merge order (the orchestrator's):** after W2-49 and W2-52 (stacked, DEC-752).""",
        hours="5 to 6"),
    "W2-20": dict(
        id="DAEO-r30l", title="Machine-wide resource gate", profile="STANDARD", status="nothing",
        older="briefs/W2-20-part-run3.md",
        scope="""- **The answer in force:** DEC-950 item 2 (P-W2-20-SCOPE (a)): the gate re-scoped to DEC-942 and DEC-947 on this machine; machine-agnostic in Wave 3. DEC-953 lifted the memory arithmetic as a gate on this repository's work, not as W2-20's product feature: you build it as the ticket says.
- **You merge first.** The orchestrator could not merge `w2/integrate` in: it conflicts (the older part names `tests/acceptance/W1-07/README.md`; there may now be more). Do the older part's step 1: `git merge --no-ff w2/integrate`, trailers `Task: DAEO-r30l`, `Implements: DEC-950`, `Role: orchestrator`; a conflict in an acceptance file is resolved by a fresh independent test designer (both sides kept as written), never by you; any other conflict inside your own paths you resolve mechanically and say how; anything else: `git merge --abort` and PACKAGES. Then re-verify the merged head before new work.
- **What is left, from the older part (its steps 2 to 7, 9 and 11):** the design note, tests first (`--effort high`), the engineer, the verification below, at most one repair batch, `gov checkpoint`, the return. No review (STANDARD).
- **Shared line:** `src/gov/check/commands.py` is also W2-37's and W2-16's (one line each); keep your own lines only. Whichever merges second merges back.""",
        hours="12 to 16 (1.5 to 2 lead-days)"),
}

COMMON_OVERRIDES = """**What no longer applies (DEC-953; `governance/project/orchestration/LIFTED-BY-DEC953.md`), wherever the older part or your checkpoint says otherwise:** the merge step where the orchestrator has done it; the pre-close gate and `gov close` with its probe gate; fresh probes because a merge made a review stale (there is no staleness rule; a review is needed only where none has passed, or for new work); the trailer gate as a refusal (trailers are still written); the ratchet lists; the night window, the 01:00 cut-off, the `NIGHTLY-RUNNING` and `CLOSE-PENDING` holds and the 90-minute rule; the wait-based park. Test designers and engineers run at `--effort high`; only reviewers at `--effort max` (DEC-957). The guard is five rules now (ACT 1): command forms are no longer refused."""


def verify(w2, tid):
    return (f"""**Verify (DEC-953 item 4, the common brief's step):** your own acceptance suite and unit tests, then the selection, `PYTHONPATH=/home/usain/gov-os-worktrees/{w2}/src python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py /home/usain/gov-os-worktrees/{w2} {w2} {tid}`; the full suite only when its scope is `full`, and then once, under `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh <command>` (closes take the lock first). Rebuild once first, under `flock /tmp/gov-os-rebuild.lock`, never `--no-embeddings`. A red in your files that fails alone is yours; one that passes alone is a flaky candidate, named. **Known reds you do not own** (named, left): the 235 live-wiring cases ACT 1 turned red, until W2-90 lands (`{CASES}`); W1-42's accepted reds; latency cases under load (W1-02, W1-05), re-run alone; DEC-919's W2-66 case naming a new conftest.""")


def tail(w2, hours):
    return (f"""**Installs:** the guard refuses them for you and your workers; raise any as a P1 in your return. **Scratch:** 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-{w2}`; clean as you go, report `du -sh` and `du -s --inodes` in `evidence`, and name anything left for the orchestrator. **Repair:** at most one batch; a second, a fix outside your paths, or a red in another ticket's code: PACKAGES with its cost in lines and hours. **Finish what is listed and nothing new** (DEC-946 item 6).

**Estimate:** about {hours} hours.

**Return:** the twelve fields first, as labelled lines; status DONE (each step's counts, the selection's scope and reasons, the probe record where one is due; ready to merge) or PACKAGES (each in six parts, with your recommendation and confidence, saying what it blocks).
""")


for w2, t in T.items():
    lines = [f"You are the ticket lead for ticket `{t['id']}` (`{w2}`, \"{t['title']}\"), profile {t['profile']}, working "
             f"only in the worktree `/home/usain/gov-os-worktrees/{w2}` on branch `w2/{w2}`.", "",
             f"**This is a resume, under DEC-953, DEC-954 and DEC-957: read your lead checkpoint, `.gov-runtime/scratch/lead/"
             f"CHECKPOINT.md`, first.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`"
             + ("" if w2 == "W2-20" else " (the orchestrator merged `w2/integrate` in: ACT 1's five-rule guard, DEC-953 to "
                                         "DEC-957, W2-90 filed)")
             + f", and `git status --short` must show {t['status']}. Anything else: stop and return PACKAGES naming it.", ""]
    if t["older"]:
        lines += [f"**Your decided scope is in your older part,** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/"
                  f"scratch/orchestrator/{t['older']}`: read it whole for its texts (behaviours, checks, who runs beside "
                  "you). This part holds wherever the two differ.", ""]
    lines += ["## What is left", "", t["scope"], "", COMMON_OVERRIDES, "", verify(w2, t["id"]), "", tail(w2, t["hours"])]
    (O / "briefs" / f"{w2}-part-resume-dec954.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote", w2)

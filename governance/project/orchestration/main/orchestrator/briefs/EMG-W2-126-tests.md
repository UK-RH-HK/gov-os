# Emergency task: W2-54's sharing case revised to W2-126's machine-wide cache; W2-126's README map made readable (independent test designer)

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** independent test designer. **Worktree:** `/home/usain/gov-os-worktrees/W2-126-tests`, branch
`w2/W2-126-tests` (`w2/integrate` plus W2-126's acceptance suite, `2ddb12ff1452`; no W2-126 implementation). TMPDIR
`/tmp/gov-os-emg-w2126-tests`. Write only under `tests/acceptance/W2-54/` and `tests/acceptance/W2-126/`.

## Why (DEC-1042, delegated, under DEC-1033 item 3)
W2-126 (`DAEO-jpr0`) adds one vector cache shared on the machine, keyed by the model, its revision (the `/api/tags`
digest) and the sha256 of the exact text: the same text gets the same vector in every project. W2-54's
`test_two_projects_do_not_share_query_vectors` (`tests/acceptance/W2-54/test_w2_54_query_vector.py`) asserts the old
rule ("the second project never asked its embedder" is now the intended outcome, and the case reads it as a failure).
And `gov accept DAEO-jpr0` refuses W2-126's README with `ACCEPT_MAP_UNREADABLE`: it reads only tables whose column
header starts with "test" or "file".

## Independence
**Never read `~/gov-os-worktrees/W2-126`** nor any file its branch `w2/W2-126` changes against `w2/integrate` (the
implementation). Work from the ticket `.tickets/DAEO-jpr0.md` (its KPIs and the interface its README states:
`GOV_VECTOR_CACHE_DIR`, `GOV_VECTOR_CACHE_MAX_BYTES`, `vector_cache` `{hits, misses, skipped}`), DEC-1042, DEC-1033,
the W2-54 ticket `.tickets/DAEO-0rfi.md` and README. Look at how `gov accept` reads a map:
`src/gov/accept/` on `w2/integrate`.

## The work
1. Revise W2-54's sharing case (and any other W2-54 case that asserts projects never share a query vector) to the
   rule in force: two projects asking the same text of the same model and revision get the same vector, the second
   from the machine-wide cache; what each project's cache must still keep apart (a different model or revision, a
   different text) stays checked. Each case gets its own cache folder (`GOV_VECTOR_CACHE_DIR` in its temporary
   directory). Commit with `--trailer "Rewrite-Reason: DEC-1033"`, `Task: DAEO-0rfi`, `Implements: DEC-1042,DEC-1033`.
2. Fix W2-126's README map so `gov accept DAEO-jpr0` reads every row (header naming, `test_x[param]` forms as
   `gov accept` expects); no case changes. Commit with `Task: DAEO-jpr0`, `Implements: DEC-1042`.
   Both with `Role: independent-test-designer`.
3. The hold on heavy runs: until the CTO says the confined gate is live, run only `gov accept`'s map read (it is
   light) and single small files; the W2-54 file's run waits for the word unless it rebuilds no store and scans no
   secrets (check its fixtures first).

Return DONE with the head (12 digits), each changed case old -> new with one line on what it checks, and the map's
check (`gov accept DAEO-jpr0 --list` or its equivalent, if it has one; else how you verified it). Estimate: 40 minutes.

# SANDBOX-GUARD-EXP-1's harness (DEC-1098 (4), DEC-1099 (1), DEC-1101 (2)-(3))

- **Design:** `governance/project/orchestration/packages/SANDBOX-GUARD-EXP-1.md`, approved by DEC-1099 (1).
- **Declaration:** `packages/SANDBOX-GUARD-EXP-DECLARATION.md`.
- **Seal:** `packages/ACT-SANDBOX-SEAL-1.md`, with its files in `drafts/sandbox-seal/`.
- **Status:** drafts only. Nothing here has run on the corpus. Nothing live is changed, and nothing is committed.

## Order
1. **The walls ACT (ACT-INDEP-WALLS-1),** with the seal's path-map patch inside it, rehearsed and applied by the
   owner's operator.
2. **The launch script** for the automated independent sessions, tests first, with one review (DEC-1101 (3)).
3. **The four briefs below,** to the owner for approval once. Their sha256s go into the declaration §12, and the
   declaration is committed.
4. **`extract_corpus.py --sets-root <root>`.** It writes the tuning half to `~/gov-os-runs/SANDBOX-GUARD-EXP-1/tuning/`
   and the held-out half to the sealed folder. It prints counts only.
5. **Writer 1 and writer 2,** started by the launch script under their briefs.
6. **Labeller 1 and labeller 2.** Then `score.py agree`, both halves, with the disputes going to the owner. The labels
   are then hashed.
7. **`run_a.py trees`, then `bash prepare_a.sh`.** `prepare_a.sh check` confirms the copies are byte for byte as live.
8. **`run_a.py run --half tuning --round 0`,** then `score.py score --setup A --half tuning --round 0 --ids-out …`
   for the tuner.
9. **Set-up B's environment and runner,** built and reviewed (deferred, below). Then B's control and round 0.
10. **Tuning rounds 1 to 3** per set-up, each re-scored on the whole tuning half.
11. **The freeze.**
    - Run `run_a.py run --half held-out --sets-root <root> --round live`.
    - Then run `--round tuned --hook <frozen>/pretooluse.py`.
    - Then run B's held-out run.
    - Then run `score.py score` and `score.py compare` on the held-out half. These print counts only.
12. **One independent review,** then both results to the owner.

## What is built (this folder)
| File | What it does | sha256 (drafts) |
|---|---|---|
| `common.py` | Shared places, the record, the sealed folder joined in code, the rewrite onto the substituted home, counts-only output. Reviewed earlier. | `f22faecd00f2…` |
| `extract_corpus.py` | The corpus and the split by session. Reviewed earlier. | `69c3520f0902…` |
| `prepare_a.sh` | Set-up A's place: the clone in a substituted home, the live hook files copied byte for byte and checked, sparse worktrees, and the sets-root map stub. **Plants no protected content.** Has `--dry` and `check`. | `19b4f6af041c…` |
| `run_a.py` | Set-up A's runner: each action passed to the copied hook, its own decision recorded (no execution). Covers the held-out half's `live` and `tuned` rounds, each run once; the frozen-hook check; the brake (`--max-seconds`); stops by process group; and `--dry`. | `af0ecadfe310…` |
| `score.py` | `score`: per rule class, false refusals, wrong allows, unjudged and dropped, plus by source and stratum, counts only, with `--dry` and `--ids-out` for the tuning half only. `agree`: the second labeller's overlap. `compare`: Q8. | `a1096fc75359…` |
| `tests/test_run_a_score.py` | 18 tests on a planted label file of `SGX1-MARKER` stand-ins, with a stand-in hook; one smoke test on the live hook file (read-only). | `ae13d2d2e2b4…` |
| `briefs/labeller.md` | The labeller's fixed brief. | `53d7a7b20dfe53815e9cd18a3929c47e6ee6651e808150e3eb3057f9520398b7` |
| `briefs/labeller-2.md` | The second labeller's fixed brief (blind 10 % overlap). | `1e24e09fd61f1c9e031571d80f41a2498afe3cbd32ad292122225eb16694dad2` |
| `briefs/writer-tuning.md` | Planted-case writer 1 (tuning half). | `f339928e9d8e8c5c9308f47e5080d6bb631775ae2309c0e922ac382c77b5ed1c` |
| `briefs/writer-heldout.md` | Planted-case writer 2 (held-out half, after the seal). | `d8aceb806498e16bd88d76ad097c20cadeb04798176a7baabf06e5d48da0e206` |

**Tests:**
`<pin python> -m pytest tests/test_run_a_score.py -q -p no:cacheprovider` gives **18 passed** in 2.6 s. The smoke test
gives the live hook's decisions as expected: allow for an engineer's Read, deny for sudo, deny for a worker's install.

**Speed:** the live hook judged 120 harmless actions in 1.8 s on 6 workers, about 67 a second.

## What is left (deferred until the design and the declaration are reviewed)
- **Set-up B's runner and its environment:**
  - the generator of the per-role sandbox settings;
  - the substituted home's stand-ins for the protected places B must execute against;
  - the launched sessions;
  - the control run and the classifier (the declaration §7 (b)).

  Earlier drafts of a file-access watcher and of an environment builder with planted stand-ins were stopped by a
  safety check. They were not rewritten here. B's design as declared needs neither a watcher nor planted secrets
  beyond marker stand-ins, but how its environment is built is for the review to settle.
- **The launch script and the walls ACT** (DEC-1101 (3)), which come before any brief is used.
- **The values only the run fills:** pins, counts, seeds and the briefs' approved hashes (the declaration's
  bracketed blanks).

## Residuals of set-up A's place (named, not hidden)
- **Worktrees:** these are sparse checkouts at the pinned commit, not each ticket's branch. A rule that reads a
  branch's own files could judge differently than live.
- **Run clones:** the sessions' run clones under `~/gov-os-runs/` are not rebuilt in the substituted home, so they
  are no tree roots there. A rule keyed on "a tree of this repository" sees fewer trees.
- **The judge:** the hook imports `gov` from the pinned python, as live does. The judge is the pin's, not the clone's.

## Projected cost and time (the declaration §11; brakes at twice these)
- **Set-up A:** about 15 min per pass over a half beside D-10. That is 5 passes (rounds 0 to 3 on the tuning half,
  plus the held-out half twice), so under 2 h in all. CPU only.
- **Set-up B:** about 33 CPU hours, 5 h elapsed on 8 cores, the control included.
- **Tokens:** about 20 M (harness 4 M, labellers 7 M, writers 2 M, tuning 6 M, one review 1 M). That is roughly
  $150–300 at the fresh 80's rates. **No cap; the brake is at 40 M.**
- **Elapsed:** 3–4 working days after the walls ACT and the launch script. Labelling is the longest step.
- **The owner's time:** approving the four briefs once, settling the labellers' disputes, and the two results.

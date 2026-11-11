# ACT-P95-1: the gate's working size is written as the p95 of the sampled sizes, not the maximum (DEC-1133 (3))

- **For:** the owner's operator (class (b): it needs the owner's yes) and the independent reviewer, in two steps: the tool and
  its rehearsal now, the live bundle on the sample day (section 5).
- **By:** an ACT-preparation helper for the CTO (Sonnet, high; RUBRIC-2), 2026-11-11 evening. **Nothing live was changed,
  applied, launched or committed.** The live gate file and the live samples file were only read (hashed before and after the
  rehearsal: unchanged). The main tree stayed clean (`git status` empty at the end).
- **Sources:** DEC-1133 (3) ("the sample day after ACT A is in, on a working day with leads running; then `--remeasure` writes the
  p95, not the maximum"); DEC-1105 (the sample day, then `--remeasure`); `governance/project/orchestration/packages/LOAD-BALANCER-1.md`
  section 4 (point 2: the maximum is far above the p95; the p95 write needs its own ACT); ACT-A's package, section 10;
  `governance/project/operator/class-rules.yaml`; `src/gov/resources/{measure,config,gate,command}.py`.
- **Folder:** `.gov-runtime/scratch/orchestrator/drafts/act-p95/` (`tools/`, `tests/`, `acts/REHEARSAL-ONLY-ACT-P95-1/`, `rehearsal.log`).

## 1. Where the maximum is computed and written (found in the code)
- **Computed:** `src/gov/resources/measure.py`, `figures()`, line `"working_size_bytes": (max(outside) if outside else None, ...)`:
  the largest session sample taken while no verification run held the lock (a slot holder, a bool or a non-integer is skipped).
  `verification_peak_bytes` (largest of all session samples) and `rebuild_peak_bytes` (largest rebuild-holder sample) are maxima too.
- **Written:** `remeasure()` in the same file builds `{"value", "date", "source": "...the largest of N sample(s)..."}` for each of the
  three keys and calls `config.write()` (whole file, temp file, `os.replace`, mode 0600). `gov resources --remeasure` has **no
  option** for a percentile (`command.py` has only the mode flag).
- **What the gate reads:** `$HOME/.gov-os/machine/gate.json` (`config.load()`); `working_size_bytes` is the per-session charge in
  the memory rule `available + live >= floor + working_size x (sessions + 1)` (`gate.py`). It is today 2,191,601,664 B (2.04 GiB,
  dated 10-29); the live file is in the product's own form (round-trips byte for byte), the floor is still 3 GiB.
- **Who writes it:** the product code is W2-20's (a ticket's path, class (O) catch-all `src/**`); the file is a machine path:
  row `machine-gate` of `class-rules.yaml`, `~/.gov-os/machine/**`, **class (b), control** (checked with the operator's own
  `act_class.py`, read only: class b, row `machine-gate`, no script hit).

## 2. The route, and why
| Route | Verdict |
|---|---|
| **(b) a config or flag change** | **Not possible.** `--remeasure` has no percentile option and the config has no key for one. |
| **(a) a code change in `src/` (W2-20's ticket)** | The durable fix (section 7 has its ticket text), but slow: designer, engineer, review, merge, then the owner's re-pin by hand, about 3 to 4 hours of the CTO's time plus the owner's step. It cannot be on the pin before tomorrow's sample day ends, and a re-pin is a large step for a ten-line change. |
| **(c) a CTO-side tool and an ACT** | **Chosen.** Smallest correct: no `src/` change, no re-pin; the only live change is the one file the ACT names, one key of it, and it is reviewed and undoable. Built and rehearsed now. |

**What (c) is exactly.** The ACT cannot be frozen before the sample day: its "after" file holds the measured figure. So there are two
parts. (1) `tools/p95_remeasure.py` (now; scratch, class (O), not an ACT's business; nothing in the repository) reads
`samples.jsonl` and the live `gate.json` and **freezes an operator bundle** whose after file differs from the before in exactly one
key, `working_size_bytes`, set to the nearest-rank p95 (the ceil(0.95 n)-th smallest session sample, an observed size) with a dated,
sourced entry. The bundle holds the evidence (the samples, the parameters, a figures text) so `verify` can **recompute the after file
byte for byte**. (2) `apply.sh` (the form of ACT-NIGHTLY-RESTART-1 and ACT-EFFORT-HIGH-2: decides by sha256 alone, refuses unless the
live file is the frozen before, a `mktemp` file beside it, mode kept) is the same script for every build.
- **It refuses to write a p95 that is the maximum in all but name:** fewer than 40 session samples outside verification, or a span
  under 6 hours, writes nothing (both are options of `build`, shown in the bundle's `params.json`).
- **What it writes and what it leaves:** `working_size_bytes` only. `verification_peak_bytes` (a peak is a maximum by meaning; the
  memory rule no longer uses it, DEC-983) and `rebuild_peak_bytes` (no sample of it exists) are not touched, so both stay named "due for
  re-measure". If the owner wants `verification_peak_bytes` re-measured as the maximum in the same ACT, it is one more key in
  `make_after` (question for the owner, section 8).
- **Same population as the product** (`figures()`): same filter (checked in the tests against `measure.figures` itself). One thing
  to know: `/tmp/gov-os-verify.lock` has not been used since 10-31, so every sample counts as "outside verification" and a lead's
  test runs are inside the population; the p95 keeps them out only if they take under 5 % of the samples.

## 3. Class and the yes line
- **Class (b)**, row `machine-gate` (`home:.gov-os/machine/gate.json`); `claimed_class` is `b`; no command, no script hit.
- **The yes line has the form `yes ACT-P95-1 <sha8>`**, `<sha8>` the first 8 hex digits of the **live bundle's** manifest sha256
  (printed by `p95_remeasure.py manifest` on the sample day). The planted bundle's `f324e873` is for the form only: **do not submit
  `acts/REHEARSAL-ONLY-ACT-P95-1/`**: its after file writes planted figures.
- **DEC-1136 (2): no exemption is needed.** The ACT touches one file under HOME and its commit is empty (`--allow-empty`, as
  ACT-GATE-CONFIG-2): it changes nothing under `tests/acceptance/`. The tests in `tests/` here are scratch; if the CTO later commits
  them, they go under `tests/unit/` (class (O), not acceptance): still no exemption.

## 4. Checks, undo, rehearsal
**Manifest checks** (run as written with `bash -c`, from the repository root, HOME planted with the file; none needs pytest, none names a live path; the path rule passes):
0. `python3 -I -m json.tool "$HOME/.gov-os/machine/gate.json"`: valid JSON.
1. The figure, date and source prefix are the frozen ones, the key order is unchanged, and **the rest of the file hashes as the
   before's** (so nothing but `working_size_bytes` moved).
2. The product's own reader (`gov.resources.config.load()` from the clone's `src/`): no fault, `working_size_bytes` is the figure,
   and it is not "due".

**Undo:** `bash apply.sh undo` puts the frozen before copy back, byte for byte, only while the file is as this ACT left it (a later
change is never overwritten). Both rehearsed.

**Rehearsal** (`bash tools/rehearse.sh`, log `rehearsal.log`, ends `failures: 0`, fixed text only, **identical on two runs**):
a planted HOME holding only a copy of the live gate file, a copy of `src/` (git archive), the operator's clean environment.
| Step | Result |
|---|---|
| B. `tests/test_p95_remeasure.py` (17 tests) | green on the tool; **red on a mutant that returns the maximum** (7 tests red) |
| C. the product's own `--remeasure` on the planted day | writes **9,500,000,000** (the maximum); the bundle writes **2,475,000,000** (the p95), only that key differs |
| D. checks 0-2 as written | on the before: 0 green, 1 and 2 red; apply (plain, no option); then all three green; one file changed, none added, mode 600, no temp file; second apply no change |
| E. the maximum written instead: checks 1 and 2 red; a moved file, a link, a missing or tampered frozen copy: refused (3 or 4), nothing touched; undo byte for byte | all as stated |
| F. the operator's `act_class.py` | class b, no hits |
| G. the live gate and samples files | unchanged |

Differences from the real run: the planted samples are synthetic (192 samples, 5 outliers); the operator's dry run clones the whole
repository, the rehearsal copies only `src/` (the checks read nothing else); the operator's own program was not run.

## 5. The live bundle on the sample day (about 15 minutes, then one short review round)
After the sampler ends (section 6), all by the CTO, in the repository, HOME the real one:
```
T=.gov-runtime/scratch/orchestrator/drafts/act-p95/tools
python3 -I $T/p95_remeasure.py figures --since <the sampler's first line time>    # read-only: p50, p95, max per role
python3 -I $T/p95_remeasure.py build --out .gov-runtime/scratch/orchestrator/acts/ACT-P95-1 --since <the same time>
python3 -I $T/p95_remeasure.py manifest .gov-runtime/scratch/orchestrator/acts/ACT-P95-1 --rehearsal .gov-runtime/scratch/orchestrator/drafts/act-p95/rehearsal.log
python3 -I $T/p95_remeasure.py verify  .gov-runtime/scratch/orchestrator/acts/ACT-P95-1
```
The reviewer's job on the live bundle is short: run `verify` (the after file is the p95 of the evidence, byte for byte), read
`figures.txt`, confirm the one-key diff. The tool, `apply.sh` and the rehearsal are reviewed once, now. The owner then reads the two
figures (the maximum `--remeasure` would have written and the p95) in the package's reply and gives `yes ACT-P95-1 <sha8>`.

## 6. The sample day (DEC-1133 (3), DEC-1105): when, what, who
1. **When:** the first working day on which **ACT A is applied and at least one lead is running**; tomorrow (2026-11-12, a working
   day) if ACT A (after the error-path and listing-rule fixes of DEC-1133 (2), and its companion tests) is applied by the morning.
   **Do not start the sampler before a lead shows in the registry**: without ACT A, only small sessions are sampled (LOAD-BALANCER-1 §4
   point 1). If ACT A is not in by tomorrow noon, move the day.
2. **Start (the CTO, once):** register the CTO's own session (`gov resources --register <claude pid> --ticket DAEO-sdxk --session-role
   orchestrator`; it counts as one session in the memory rule, so it belongs in the sample), confirm a lead is listed (`gov resources
   --sample --json` returns it in `samples`), copy `gate.json` and `samples.jsonl` to scratch, then start
   `setsid -f bash drafts/load-balancer/resources_sample_day_v2.sh` (96 samples, 300 s apart, **8 hours**, `N=` and `EVERY=` change it;
   it does not run `--remeasure`). Stop early only by pid with `tools/proc.sh` from `log/resources-sample-day.log.pid` or by the stop file.
3. **Meanwhile:** the dispatcher keeps starting leads as usual (ACT A registers each one); the CTO does nothing special. The day needs
   at least 40 samples and 6 hours to be usable; a lead-free stretch lowers the figure honestly, so note how many leads ran when.
4. **After the day (the CTO):** section 5 (figures, build, manifest, verify), a short review, the owner's yes, the operator applies,
   `bash apply.sh verify`, then `gov resources --json` (gate reading; `working_size_bytes` dated today, no longer "due").
5. **How the gate then sets the lead count:** the memory rule admits a new session only if `available + live >= 3 GiB + working_size x
   (running + 1)`. `available + live` stays about the same as sessions start (each takes from one and adds to the other), so the number
   of sessions the gate allows is **floor((available + live - 3 GiB) / working_size)**. With about 15.2 GB of `available + live`
   (LOAD-BALANCER-1's reading, illustration only): at today's 2.19 GB, 5 sessions; at a p95 of 3.2 GB, 3; at 4.09 GB, 2; at the maximum
   9.5 GB, **1** (what `--remeasure` alone would have left). The CTO's own registered session is one of them. This is the count that
   replaces the manual cap: **the cap can go when** (a) ACT A has been applied for at least one full working day and every lead showed
   in the registry, (b) ACT-P95-1 is applied and `gov resources --json` shows the p95 and an open gate, (c) the owner says yes.
   **Who:** the owner decides (a DEC; the next free id is DEC-1137); the CTO then deletes `max_leads` from
   `.gov-runtime/scratch/orchestrator/dispatch/config.json` (a dispatcher state file, class (O), no ACT; keep the old file as
   `config.json.pre-p95` as DEC-1049 did). Two effects to know: the dispatcher's own forecast still admits first, and `idle_headroom()` reports
   only when a cap is set, so with no cap the "idle with headroom" inbox item stops; setting `max_leads` to a high number (8) instead keeps
   the item and leaves the gate as the real limit. The gate checks only at a start: a running lead that grows is the trip-wire's and
   `mem_guard.py`'s business, not the gate's.

## 7. Route (a), for later: the ticket text (not needed for tomorrow)
Retire the tool when this lands and is pinned. **Ticket (W2-20 follow-up, id for the CTO to give), profile LITE**, allowed paths
`src/gov/resources/measure.py`, `src/gov/resources/command.py` (help text), `tests/acceptance/<id>/**`, `tests/unit/resources/**`:
- **K1:** On a planted day of 192 session samples outside verification with 5 outliers (maximum 9,500,000,000, nearest-rank p95
  2,475,000,000), `gov resources --remeasure` under a planted HOME writes `working_size_bytes` 2,475,000,000. Verify: the
  planted-home run reads the value back from `gate.json`.
- **K2:** The entry's `source` says "p95", the sample count and the span, and the date is today. Verify: the entry's three fields.
- **K3:** With fewer than 40 such samples or a span under 6 hours, `working_size_bytes` keeps its old value and the result names why
  (error code `RESOURCE_SAMPLES_TOO_FEW`). Verify: both cases, the file byte-identical.
- **K4:** `verification_peak_bytes` and `rebuild_peak_bytes` are still the maxima; the other keys, the key order and mode 0600 are
  unchanged. Verify: byte compare of every other key; `stat`.
- **K5:** The population is the one `figures()` has (slot holders, samples taken during verification, bool and string sizes out).
  Verify: the existing W2-20 cases stay green.
- **Brief:** designer from K1-K5 alone (no reading of `measure.py`); engineer a ten-line change (a `nearest_rank` helper and the
  threshold check in `remeasure()`); one reviewer round. About 45 + 45 + 40 minutes of workers, then the merge, then the owner's re-pin.
  The planted data of `tools/plant_samples.py` and the nearest-rank rule of `tools/p95_remeasure.py` are the specification.

## 8. Risks and questions
- **The percentile and the floors are my choice** (nearest rank; 40 samples; 6 hours): the owner said "the p95". They are options of
  `build` and printed in the bundle, so the owner or the CTO can say different ones before the live build.
- **Question for the owner:** leave `verification_peak_bytes` and `rebuild_peak_bytes` as they are (this ACT) or write the first as the
  maximum too? Neither is used by the memory rule.
- **A lead's size is a tree size:** a lead whose test run takes more than 5 % of the day lifts the p95 toward the test run's size
  (the verification lock does not tell them apart, LOAD-BALANCER-1 §4 point 2). The honest answer is a test-run marker or a rule
  change in W2-20, a ticket, not this ACT.
- **The CTO's own session in the pool:** registering it adds about 96 samples of the CTO's tree to the day's; if the CTO's tree is
  larger than a lead's it lifts the p95. The gate charges it like a lead, so it belongs in the pool; say so in the reply.
- **DEC-1133 (3) arguably already authorises the CTO to run the write** (as DEC-1105 does for `--remeasure`); this ACT exists because the
  gate file is a (b) control path and the brief asked for one. `apply.sh` can also be run by hand if the owner prefers that route.
- **A shut sample:** `gov resources --sample` reads the registry; if it is unreadable the sample day writes nothing and says so
  in `log/resources-sample-day.log`; look at that log at midday.

## 9. The files (scratch; sha256 first 12)
| File | sha256 | What |
|---|---|---|
| `tools/p95_remeasure.py` | `e184b8b29eea` | `figures`, `build`, `manifest`, `verify` |
| `tools/apply.sh` | `cf6073f40284` | the bundle's apply.sh (check, apply, undo, verify), the same for every build |
| `tools/plant_samples.py` | `3d2754b4a47a` | the planted day |
| `tools/rehearse.sh` | `2c7750f7b357` | the rehearsal |
| `tests/test_p95_remeasure.py` | `bab3fa5cc559` | 17 tests, red on the maximum |
| `rehearsal.log` | `e2abfd80935c` | ends `failures: 0` |
| `acts/REHEARSAL-ONLY-ACT-P95-1/manifest.json` | `f324e87343b0` | the planted bundle's manifest (form only; never submit) |

[DEC-1133 (3), DEC-1105, DEC-983, DEC-947, DEC-1136 (2), DEC-1120, DEC-1049; ACT-A (`drafts/act-a/ACT-LOAD-BALANCER-A.md`); LOAD-BALANCER-1]

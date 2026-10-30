# P-REPIN-2 — The second re-pin as soon as W2-07 round 2 merges (W2-57 and W2-07 round 2); W2-68 and W2-71 in a third

From: the W2 orchestrator, 2026-10-28, at the owner's request (DEC-932 item 3: "re-pins are cheap; pin each judge improvement as it lands"). Gates: ACT-W2-57-LS-2, and the closes of W2-58, W2-63, W2-07 and W2-57.

## 1. Context

- **Today's judge** is `pin-6a4696eb` (DEC-922). The plan bundled the second re-pin as W2-68, W2-71 and W2-07 round 2 (DEC-899, DEC-924). W2-68 and W2-71 have not started.
- **Judge code merged since the pin** is W2-57's alone (`57e363c5`), in four files: `src/gov/adapters/portability.py`, `src/gov/close/command.py`, `src/gov/close/serial.py` (new) and `src/gov/doctor/command.py`. Nothing under `template/` changed, so this re-pin needs **no settings regeneration** (ACT-REPIN-1's Part B).
- **W2-07 round 2** is in its last run: its lead merges `w2/integrate` back and re-verifies (run 5, started 2026-10-28 00:47, about 2 hours). It changes `src/gov/close/gates.py`, gate (h)'s line in `src/gov/close/command.py` and possibly `src/gov/close/history.py`.

## 2. The proposal

- **Re-pin 2:** the merge of W2-07 round 2 on `w2/integrate`, carrying W2-57 and W2-07 round 2.
- **Re-pin 3:** W2-68 and W2-71, when they land.
- **Cadence from now (owner, standing, if accepted):** a re-pin as each judge improvement lands, at a quiet moment, never during a close queue or a close's quiet window.
- **The ladder before the ACT, as for ACT-REPIN-1:**
  - W2-07 round 2 merged, with `tools/probe_impact.py` after it;
  - the full regression in the close's form on a fresh clone of the head to be pinned, with that head's own code (the code the pin will be);
  - two wheel builds from clean exports of that head with the same sha256;
  - clean history: the trailer gate and containment find nothing, and W1-01's history cases pass;
  - a sweep for every test or tool that names `pin-6a4696eb` (the hooks and the declared checks follow `~/.local/bin/gov`; my tools name the pin's path, so they move with it, as after ACT-REPIN-1).
- **The ACT:** Part A of ACT-REPIN-1 only (export, build, check the sha256, install in `pin-<sha>`, link `~/.local/bin/gov`, verify, commit the registry entry `Role: owner`), in `packages/ACT-REPIN-2.md` and a commands file, in a plain terminal (DEC-928 item 3: it reinstalls gov). `pin-6a4696eb` stays for the rollback.
- **After it, in order:**
  1. my smoke test (the pinned `gov check`, one guard decision allowed and one refused, the declared checks and hooks on the new pin);
  2. ACT-W2-57-LS-2 (W1-46's 23 and W1-19's warm p95 leave `load_sensitive`), validated by a full run in the close's form with the new pin (DEC-931 item 2);
  3. a close queue: W2-58, W2-63, W2-07, W2-57 (and W2-67 after its merge-back and re-probe).

## 3. Why it matters

- **Three closes are blocked by today's judge.** The pinned gate (h) still refuses W2-58, W2-63 and W2-07 on old decision-record commits; W2-07 round 2's rule measures them.
- **The live tests leave the close.** W2-57's nightly route takes W1-46's live sessions and W1-19's real models out of every close: shorter closes, fewer load reds, and ACT-W2-57-LS-2 can follow.
- **A bundle waits on the slowest.** W2-68 and W2-71 have not started; bundling holds four closes for days.

## 4. Options

- **(a) Re-pin 2 as soon as W2-07 merges** (W2-57 and W2-07 round 2), W2-68 and W2-71 in a third.
  - Costs: about 1.5 hours of my validation run, about 10 minutes of the owner's plain terminal, and my 15-minute smoke test, with no close during them.
  - **Could let through:** with the live and real-model tests out of the close, only a nightly run tests them. The pinned nightly command (`gov.close.nightly`) is not run until row W2-M406's fix (DEC-915; W2-57's proposal P-1 makes running both routes its entry criterion). Until then my `tools/nightly.sh` runs the whole suite on the head every night. A live-session regression would be found a night late, not at its close.
- **(b) Keep the bundle** (W2-07 round 2 with W2-68 and W2-71). One re-pin fewer; the four closes and ACT-W2-57-LS-2 wait until W2-68 and W2-71 land.
- **(c) Re-pin W2-57 alone now,** W2-07 round 2 in a third. Live tests leave the close a few hours sooner, but W2-58, W2-63 and W2-07 still wait for another re-pin, and W2-07's merge is about 2 hours away.

## 5. Recommendation

**(a)**, with the cadence as a standing rule. Option (a)'s gap (live tests only nightly) is the same in every option once W2-57 is pinned; P-1 is what closes it.

## 6. What I need from you

Your choice. On (a), I prepare ACT-REPIN-2 once W2-07 has merged and the ladder passes, and ping ACT.

# ACT-REPIN-2 — The second re-pin: W2-57 and W2-07 round 2 in the judge (DEC-933 item 1, P-REPIN-2 (a))

From: the W2 orchestrator, 2026-10-28. **Where: a plain terminal, not a Claude session** (it reinstalls gov, DEC-928 item 3). Your acts are in `.gov-runtime/scratch/orchestrator/pin/REPIN-COMMANDS-5c401220.sh`.

## 1. What it pins

`5c401220` on `w2/integrate`, the code of:
- **W2-57:** the rulesync and doctor probes, the serial pass, and the nightly route that takes W1-46's live sessions and W1-19's real models out of the close;
- **W2-07 round 2:** gate (h) measures DEC-891's records under any ACCEPTED decision, and the owner's lists.

Commits since `5c401220` change records only (no `src/`, `template/` or `pyproject.toml`). Nothing under `template/` changed since `6a4696eb`, so **no settings regeneration**.

## 2. The ladder (P-REPIN-2 §2), all passed

- **Merges:** W2-57 (`57e363c5`), W2-07 round 2 (`8555aafc`, merged second, re-verified in full: 16,479 passed, 0 failed; serial 180), and W2-57's judgement-only re-probe after it (`4904a60f`, pass). `probe_impact.py` after each.
- **The full regression in the close's form on a fresh clone of `5c401220`, with its own code** (2026-10-28 10:17 to 11:52):
  - parallel: 16,478 passed, 31 skipped, 1 failed. The failure was W2-54's time-limit case, which passed alone: a flaky candidate, the known row W2-L429;
  - serial: 180 passed.
- **The wheel's dry run** (`pin/repin_dry2.sh`): two builds from clean exports give the same sha256, `e4f35131d8cff32f124863c6780efad368c2500be59824dc7fe9458d126905d0`. The wheel holds `gov/close/serial.py` and `gov/close/gates.py`.
- **Clean history:** the trailer gate finds 0 lacking and 0 unresolved for W2-57 (after your `6367e965`) and for W2-07.
- **Gate (b) after your `6367e965`:** `gov check` exit 0, 15 GREEN and 2 known YELLOW. The record checks pass.
- **The sweep:** no test or product file names the pin's path. My tools now read the pin from `~/.local/bin/gov`, so they follow it. The prompt's one mention I update after the smoke test.
- **The registry script** (`pin/repin2_registry.py`) refuses before the install, as it should. It replaces DEC-922's entry and names DEC-933.

## 3. Your acts, in order

1. **Before you start:** no Claude session may be running a gov command. I confirm in the chat that no lead, close or nightly run is going.
2. **Run** `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/pin/REPIN-COMMANDS-5c401220.sh` in a plain terminal:
   - A1, A2: export `5c401220`, build the wheel and check its sha256;
   - A3, A4: install it in `pin-5c401220` and link `~/.local/bin/gov` to it;
   - A5: verify (the gov path, W2-57's and W2-07's modules, the dependencies);
   - A6: write the registry entry and commit it (`Role: owner`, `Implements: DEC-933`).
3. **Tell me it is done.** I run the smoke test:
   - the pinned `gov check`;
   - one guard decision allowed and one refused;
   - the declared checks and hooks on the new pin;
   - the nightly route reading the list.
   
   Then ACT-W2-57-LS-2, validated with the new pin, and the close queue (W2-58, W2-63, W2-07, W2-57).

**What to see:**
- A2 prints `OK` for the sha256.
- A5 prints `.../pin-5c401220/bin/gov`, `W2-57 and W2-07 in the pin` and `deps ok`.
- A6 prints the new registry entry, then makes the commit.

## 4. Rollback (one command; the first re-pin's judge comes back)

`ln -sfn ~/.local/share/gov-os/pin-6a4696eb/bin/gov ~/.local/bin/gov; hash -r`, then revert the registry commit. `pin-6a4696eb` stays installed.

# P-W2-111-YAML-REST: the same fail-open loader in the guard's other YAML reads (W2-111 r5, after rv-3's F1)

## 1. What was found
- rv-3's F1 is closed in W2-111. libyaml's fast loader accepts some malformed texts that the pure SafeLoader refuses
  (a tab inside a value, `? ` in a flow item, a late byte-order mark). W2-111's loader now takes libyaml only for a
  text with none of those, and otherwise falls back to the pure loader.
  - Evidence: 0 differences over 100 real texts, a 40,000-text fuzz, 15,124 product decisions and 7,562 live-hook
    decisions.
  - S10's cases run at 61-72 ms quiet; `gov accept` gave 249 passed, 0 failed.
- The lead found the same direct call elsewhere in the guard. I checked each one on w2/integrate:
  - `src/gov/util/role_paths.py:85` (the role_paths block) and `:165` (a ticket's front matter): **outside W2-111's
    paths**;
  - `src/gov/util/parts.py:234` (a ticket's front matter): already inside W2-111's paths;
  - the applied live hook's `.claude/hooks/role_reads.py:111` and `:171`, there since 28c586930 (W2-150,
    2026-11-09), before W2-111.
- **Effect:** a role_paths block with a tab in an entry is applied by libyaml. The pure parser would refuse it, which
  stops every role-checked call. So such a malformed block opens role-scoped access instead of closing it.
- **Classification:** ordinary work no (a tab inside a block entry); consequence: fails open.
- The non-guard uses (`links/check.py`, `retrieval/graph_route.py`) are not decisions and are left as they are.

## 2. Options
- **(a) Widen W2-111 now by one file (`src/gov/util/role_paths.py`). Recommended.**
  - The engineer routes the four guard reads (`role_paths.py` twice, `parts.py:234`, and the live hook's
    `role_reads.py` twice, in the diff) through the same checked loader, with a planted-tab case each.
  - The narrow re-check covers it, and ACT-GUARD-FIX-7 and release 0.1.1 both carry the fix.
  - Cost: about 1 hour on W2-111 (0.1.1 then about 05:30-06:00). Risk: low; same pattern, same corpus.
- **(b) A follow-up row.** The live part rides in ACT-GUARD-FIX-7 if I widen the ACT. The product part (`role_paths.py`)
  waits for another ticket, which needs your P1. 0.1.1 ships with the product's fail-open in place.
- **(c) A Wave 3 row only.** The fail-open stays in the product and in the live hook.

## 3. Recommendation
**(a)**, confidence high. It is rv-3's F1 class, found by the same round. Fixing it in the round that introduces the
fast loader's guard keeps one rule for every guard YAML read, and the release about to be cut does not carry a known
fail-open.

**Your line:** `P-W2-111-YAML-REST (a)` (or (b), (c)).

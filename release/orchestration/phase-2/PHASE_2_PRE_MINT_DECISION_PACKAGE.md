# Phase 2 pre-mint decision package — the tool-install and authority surface, third adversarial review

| Field | Value |
|---|---|
| Date | 2026-09-22 |
| For | the product owner |
| From | the Phase-2 outer orchestrator |
| Trigger | P2-ADJ-0006's stopping rule: one structural round, then escalate rather than iterate a fourth time |
| Tree | `phase2/repair-2-failclosed` `c34c439`, `product_code_digest b6f75daf…2929`. Verified serially by the orchestrator **and** independently by the reviewer: build 0 warnings, unit 280/0, certification **244/0**, `gov contract verify` `CONTRACT_SOURCE_BOUND` |
| No candidate exists | `cap2-candidate-2` has **not** been minted |

## 1. What repair iteration 2 achieved

| Class | State |
|---|---|
| BC-P2-33 adoption | repaired, verified |
| BC-P2-32 failure memory | repaired, verified |
| BC-P2-37 update ingress | repaired, verified |
| BC-P2-07 health tiers | repaired, verified |
| BC-P2-41 review binding | repaired — subjectless reviews now authorise nothing |
| BC-P2-45 overlay precedence | repaired for every mechanism found, **except AR75-F2 below** |
| BC-P2-53 command classification | default inverted — **except AR75-F1 below** |

**All eighteen findings from the two earlier adversarial reviews are closed**, each re-verified by its own reproduction.
Every negative control passes, and ordinary acquisition still works: the only disclosed cost is that an unlisted package
manager, named directly rather than wrapped in a pinned script, now gates.

## 2. What is still broken — two HIGH defects

**AR75-F1 — two names on the positive list have the very semantics the list assumes they lack.** `cp` and `curl` are
admitted as "plain argument" programs. But `cp` writes through a symlink, and `curl -K` reads the rest of its command line
from a file. Combined with the per-token scan treating a token as a path *only if it contains a slash*, six shapes install
ungated and write outside the project root — five of them with no slash, no `..` and no absolute path anywhere in the
command. Two of the six re-fire on every later health check.

The reviewer is careful, and I agree with its framing: **the inversion itself held.** An arbitrary unnamed program gates;
unnamed wrappers gate; a project cannot touch the lists. What failed is the premise of two list entries.

**AR75-F2 — `class` is authority-bearing and the overlap check does not compare it.** Appending a rule that is *stricter*
on every compared dimension, but declares `class: derived`, makes an undeclared, out-of-scope write close cleanly: task
close goes from refused to accepted, the observed mutation disappears, and every reporting surface stays clean. The check
saw the overlap and passed the rule — this is not a pattern miss.

**AR75-F3 (LOW)** is the second pair of eyes the previous builder asked for, and it matters for honesty: the justification
written into that code is **factually wrong**, though the defect is not exploitable today.

## 3. Why I stopped instead of ordering a fourth round

I committed to this in writing before the review ran, and the reason still holds: three rounds on this surface have each
closed the previous reviewer's findings and left the class open. I judged that continuing on my own authority — having
told you I would not — would be the wrong call even though both remaining defects now have concrete fixes.

Both fixes are narrow and do **not** rely on enumeration:

- **AR75-F1**: resolve every non-flag token against the project root and refuse what escapes, instead of only inspecting
  tokens that contain a slash. This touches neither the list nor the conforming path, and the reviewer offered it having
  declined to implement it.
- **AR75-F2**: compare `class` in the restrictiveness check, since `class` confers an exemption from a governance control.

## 4. Options

- **A — Authorise one bounded round for exactly AR75-F1 and AR75-F2, with the two fixes above, then a fourth review, then
  mint.** My recommendation. Both are specific and principled; the inversion that took three attempts is holding; and the
  alternative is handing a formal verifier two HIGH defects we already understand.
- **B — Mint `cap2-candidate-2` now, with both defects disclosed, and let the formal Opus 5 verification judge them.**
  Honest, and it exercises the verification path — but AC-3 and AC-4 would almost certainly fail again on defects we could
  have fixed first, spending a full nine-role verification to tell us what we already know.
- **C — Amend scope**: place the residual tool-install command-shape risk at a later lifecycle (R2 certification) with the
  compensating controls recorded, mint, and let verification judge the rest. Yours alone to decide; it changes what must
  hold now rather than what is true.
- **D — Stop Phase 2 here** and commission a meta-review of the loop before any further repair.

## 5. What is preserved

Everything is committed: the repair branches, three adversarial reviews with their probes and re-runnable evidence, the
`globprobe` measurement tool the reviewers built, every decision and adjudication (OD-P2-03, OD-P2-05, OC-P2-04,
P2-ADJ-0004, -0005, -0006), and the run records with per-worker telemetry for Opus, Sonnet and the paused DeepSeek
experiment. State verifies consistent. Nothing moves until you choose.

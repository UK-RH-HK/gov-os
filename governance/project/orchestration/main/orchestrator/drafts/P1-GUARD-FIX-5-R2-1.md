# P1-GUARD-FIX-5-R2-1: ACT-GUARD-FIX-5 failed its last review round; how should the live hook's heredoc gap be closed?

**(1) Context.** You chose GUARD-HEREDOC (a) (DEC-1171): fix the live hook so that `bash -euo pipefail <<'EOF'` and
similar spellings are judged, with no hold on launches. Round 1 failed (it loosened one form and left bytecode in the
bundle). Round 2 was rebuilt as stricter-only (manifest ef9078eb: 52 checks ok, 1,280 matrix calls, 720 replayed
calls). An independent reviewer reviewed it (Opus, fresh session, verdict block in
`reviews/act-guard-fix-5-r2.md`). Round 2 was the last round.

**(2) What the review found, and my run.**
- **The verdict is NOT READY.** Checks 1 to 5 pass: the bundle, hashes, apply, verify and undo in a fresh clone, and
  the class (b). Check 6 fails on F1, which blocks.
- **F1:** after the ACT, the hook reads a shell heredoc's body as commands. A comment in that body with an apostrophe
  (`# don't overwrite`) looks like an unclosed quote. The scan then gives up on the **whole call**. The fallback parser
  gives up the same way, and an unresolvable target is let through (G-1). So a write into `tests/acceptance/` later in
  the same call was refused before the ACT and is allowed after it. The same holds for an auditor's write outside its
  records.
- **I ran the reviewer's four reversal calls** (`reviews/act-guard-fix-5-f1-run.md`): all four are **deny before and
  allow after**. That includes plain `bash <<EOF`, which the live hook refuses today. The control case without the
  apostrophe stays refused. F1 is confirmed, so the bundle must not be applied.
- **Rows** (not blocking): F2, a lone apostrophe in a top-level comment already leaves any Bash call unjudged today;
  F3; F4, check 4 uses python3 from PATH; F5, a stale W2-42a ref in the package.

**(3) Why it matters.** Applied as it stands, the ACT would close the `-o pipefail` gap but open a wider one: any
heredoc whose comments use a contraction, which is common. Today's gap is covered by the tripwire at session end
(DEC-789), and nothing shows it has been used.

**(4) Options.**
- **(a) Round 3: rebuild with a fallback, then one fresh review.**
  - The change: a body the new reading cannot tokenise is noted as unresolvable, and the rest of the call is still
    judged as before the ACT. Comment text in a body is dropped before tokenising.
  - Tests: F1's four cases, plus apostrophe comments in each options form, added to the cases, to check 4 and to the
    replay.
  - Route: a helper builds it, a fresh reviewer reviews it, then your yes.
  - Cost: about 2 to 3 hours to your yes. It needs your line, because round 2 was the last.
- **(b) Withdraw ACT-GUARD-FIX-5 and copy W2-42a's fix once W2-42a has merged** (its land is starting now). The ACT
  then reuses a fix that passed review in the product. That fix must first be checked for the same apostrophe case.
  Cost: about half a day; the gap stays open meanwhile, covered by the tripwire.
- **(c) Apply as is and accept F1 as a row.** Not recommended: it refuses less than today for a common form.

**(5) Recommendation: (a)**, with W2-42a's merged fix as the reference, and a check of F1's case against the product
parser in the same round (if the product has it, a row for W2-42a). Confidence: high.

**(6) What it blocks.** No lead waits on it. The live hook stays open on the `-o pipefail` spelling until the fix is
applied, as today.

Your line: `GUARD-FIX-5 (a)`, or `(b)`, `(c)`.

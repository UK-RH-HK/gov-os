#!/usr/bin/env bash
# P2-AR-0034: pair every audit-of-record re-run of ./audit-after/ with ./audit-base-53897c1/ (verdict lines only).
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
norm() { grep -v "^#\|/tmp/" "$1" | sed -E 's/"updated_at": "[^"]*"//; s/S-[0-9a-f]{12}/S-x/g; s/duration_ms.: [0-9]+/duration_ms: n/g'; }
verdicts() { grep -hE '^CHECK|^\[(PASS|FAIL)\]' "$1" | sed 's/ -- .*//'; }
echo "# P2-AR-0034 audit-of-record re-runs: base 53897c1 vs this tree, through the round-2 integration builder's root-channel adapters (run-audit-probe.P2-AR-0034.sh)"
for f in audit-after/*.out; do
  b="audit-base-53897c1/$(basename "$f")"
  echo; echo "== $(basename "$f" .out)"
  echo "   after: $(grep -m1 '^# gov under test' "$f" | grep -o 'gov-[a-z]*-[0-9a-f]*' | head -1); $(grep -cE '(^|\s)PASS(\s|:|$)|\[PASS\]' "$f") PASS, $(grep -cE '(^|\s)FAIL(\s|:|$)|\[FAIL\]' "$f") FAIL, $(grep -c Traceback "$f") traceback(s), $(tail -1 "$f"); first stop: $(grep -m1 'required command failed\|unexpected failure\|Error:\|TypeError' "$f" | cut -c1-110)"
  if [ -f "$b" ]; then
    echo "   base : $(grep -m1 '^# gov under test' "$b" | grep -o 'gov-[a-z]*-[0-9a-f]*' | head -1); $(grep -cE '(^|\s)PASS(\s|:|$)|\[PASS\]' "$b") PASS, $(grep -cE '(^|\s)FAIL(\s|:|$)|\[FAIL\]' "$b") FAIL, $(grep -c Traceback "$b") traceback(s), $(tail -1 "$b"); first stop: $(grep -m1 'required command failed\|unexpected failure\|Error:\|TypeError' "$b" | cut -c1-110)"
    if diff <(verdicts "$b") <(verdicts "$f") > /dev/null; then echo "   verdict lines: identical"; else echo "   verdict line differences (base < > after):"; diff <(verdicts "$b") <(verdicts "$f") | sed 's/^/     /'; fi
  else
    echo "   base : none (a labelled derived copy for this tree; see the pairing below)"
  fi
done
echo; echo "== D6 (derived copy, both binaries): snapshot differences after deleting the whole runtime directory"
echo "   base : $(grep -h '^\[B\] differences' audit-base-53897c1/beta-r.D6-rebuild-guarantee.claimable.P2-AR-0034.out)"
echo "   after: $(grep -h '^\[B\] differences' audit-after/beta-r.D6-rebuild-guarantee.claimable.P2-AR-0034.out)"
echo; echo "== A5: the unedited base run vs the derived (store-path) after run, normalised (volatile ids/timestamps removed)"
if diff <(norm audit-base-53897c1/alpha-r.A5-emergency-controls.out) <(norm audit-after/alpha-r.A5-emergency-controls.store-path.P2-AR-0034.out) > /dev/null; then echo "   identical after normalisation"; else diff <(norm audit-base-53897c1/alpha-r.A5-emergency-controls.out) <(norm audit-after/alpha-r.A5-emergency-controls.store-path.P2-AR-0034.out) | cut -c1-200 | sed 's/^/     /'; fi

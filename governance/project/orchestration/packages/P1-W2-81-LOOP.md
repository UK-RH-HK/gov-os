# P1-W2-81-LOOP — W2-81's reviews do not converge (DEC-096): five reviews, each finding new fail-open edges

## 1. Context
W2-81 (the proving ground's runner and its synthetic repositories, FULL, test-designer-built) has had five
independent reviews over three rounds (DEC-993, DEC-997, DEC-1005). Each round fixed what the last review found;
each new review found new ways a malformed hidden half could turn NOT_READY into READY. DEC-096: a loop that has not
converged after three iterations goes to the owner. I declared round 3 myself (DEC-1005, "converging"); it was not.

## 2. What happened (review 5, on `165d3057146a`)
- **F1 (fails open):** a forbidden citation that names no file of the built repository (a typo in a literal path, a
  path written as a YAML scalar, an unquoted `{name}`, `{stale}.bak`) is still dropped silently; end to end, NOT_READY
  (stacked share 95) became READY.
- **F2 (fails open):** READY does not require the measurement half's planted-problem variants (none, an empty list or
  one kind only still gave READY).
- **F3 (low):** with pytest's `-l` a failing case prints synthetic secret values (not with the README's `-q`).
- All three are reachable only when someone writes the hidden half (W2-93 authors it; nothing reads one today).

## 3. Why it matters
The proving ground judges whether the Gov OS works on a product before EXAMIN's copy; a READY it should not give is
a false pass. But each round costs about 1.5 h and 40 USD, and the findings are moving outward to inputs no one has
written yet.

## 4. Options
- **(a) One more round, your exception for its review:** batch 8 fixes F1 (refuse any forbidden citation that names
  no built file), F2 (READY requires at least one hidden variant per kind) and F3 (no secret values in assertion
  locals), then one review. About 1.5 h, 40 USD. Risk: a sixth review finds the next edge.
- **(b) Land W2-81 now; F1 and F2 become W2-93's entry criteria (DEC-803: a risk that exists only when a feature is
  switched on belongs to the ticket that switches it on); F3 a row.** W2-93 writes the hidden half; its KPIs gain:
  "every forbidden citation names a file of the built repository, else refused", "READY needs one hidden variant per
  kind", and its own review probes both. Cost: W2-93's KPIs grow by two lines; W2-81 lands today. Risk: if W2-93's
  KPIs slip, the false READY becomes reachable.
- **(c) Park W2-81** (a Wave 3 row): the proving ground is in EXAMIN's minimum (K9), so this delays the copy.

## 5. Recommendation
**(b)**, confidence medium. The findings need an input that does not exist yet; DEC-803 puts them with the ticket that
creates it, and W2-93's review then judges them against the real hidden half. Classification (DEC-809): F1, F2
ordinary work yes (once a hidden half is written) / fails open; F3 ordinary work no (needs `-l`) / other.

## 6. What it blocks
W2-81's landing; W2-88 (depends on W2-81) and the proving ground's runs. Waiting costs W2-88's start.

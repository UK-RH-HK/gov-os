I ran the third and last probe of DAEO-rmbe at `e00fd14a`. **Verdict: pass.** No finding is both ordinary work and fail-open. One finding does fail open in a narrow band: a private key wrapped in base64 (or a similar encoding) that comes out longer than 24,000 bytes. The base finds it and this head does not. I judge it a row beside W2-L419, not a round, but the classification is close and the owner may judge otherwise.

task: Third and last review (DEC-909) of DAEO-rmbe (W2-69) at e00fd14a, above all the last repair 2f03393d, probing for lost work, writes outside scope, changed acceptance tests, a fail-open check or filter, and a chance red that returns.
status: DONE. Probe complete, verdict pass. One fail-open case: a key export wrapped in base64, hex or percent-encoding, longer than 24,000 bytes once wrapped (a wrapped key word, below). It is judged "Ordinary work: no", the same class as W2-L419.
work_completed: Step 0 first. (a) The write outside the worktree was refused (Errno 30, read-only file system). (b) `git hash-object -w` and `git update-index --refresh` both exited 0. GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-rmbe, toplevel /home/usain/gov-os-worktrees/W2-69, branch w2/W2-69, HEAD e00fd14a26be19069aeb904418d2dfa7ac868dcb; all as expected. `gov.__file__` = /home/usain/gov-os-worktrees/W2-69/src/gov/__init__.py. Read refusals met (DEC-849): 0. `gov retrieve` used once: FACET_UNAVAILABLE (lexical and semantic facets stale), so the sources were read by name. Then I read the ticket, DEC-909, DEC-853, P-W2-69-R2-1, rows W2-L419, W2-M404, W2-M395 and W2-L373, research-note §15, the README's third batch, and the module at head and at the last repair's diff. I ran 9 probe scripts against the real gitleaks 8.30.1, comparing this head with the base (w2/integrate) and with ed2de0eb (just before the last repair), each loaded from a single copied module file. One `gov rebuild --json --no-embeddings` ran in a temporary project of my own. I also ran the unit tests and the whole third acceptance batch.
files_changed: none. Nothing was written in the repository and HEAD is unchanged. The untracked root entries `git status` shows are the sandbox's placeholder device files (char 1,3, owner nobody, 16 Oct). Probe scripts and temporary projects are only under $TMPDIR/p.
evidence: Commands and outputs are in the payload below. Real stores (copies of store.db 247,947,264 B, code.db 95,223,808 B, _config.db, query-vector-cache.db): head 41.2 s and 40.8 s, clean both runs, 1,423,188 pieces, 433,832,960 B, 0 key pieces. ed2de0eb 40.3 s. Base 109.5 s. The other 2,260 runtime files (75,538,473 B), judged in place and read-only: 0 key pieces, none flagged, 105.3 s with no clean result reused. Scratch: 28 K and 9 inodes at the start, 461 MB and 652 before the store copy, 860 MB and 2,708 at the end; within the 4 GB and 100,000 share. Other refusals: the guard's hook refused one heredoc, misreading a `>` comparison as a write to `/home/usain/gov-os-worktrees/W2-69/S._PIECE:`, so I wrote the scripts with the Write tool into $TMPDIR instead. One compound command was refused as "quoted text can't be checked". The permission prompt for `rm` of my own probe folder was refused twice, so I stopped there and deleted nothing.
tests: tests/unit/secrets_check plus tests/unit/rebuild/test_compaction.py: 35 passed (20 s). test_w2_69_last_round_fragments_around_key_blocks.py: 27 passed (96 s, -n 8). test_w2_69_last_round_key_blocks.py plus test_w2_69_last_round_index_filter.py: 72 passed (347 s, -n 8, load up to 72). That is the whole third batch, 99 of 99, all at this head.
discoveries: gitleaks 8.30.1 decodes base64, hex and percent-encoding by default (`--max-decode-depth 5`), so it finds a wrapped private-key export. This head's pieces hold one word whole only up to 24,000 bytes, so a wrapped export beyond that is missed (wrapped key word, below); the base found it. In minified JSON this head beats the base: the base misses wrapped keys from 8.7 KB encoded at 2 of 12 placements. A guard snapshot file under .gov-runtime/snapshots/ vanished between my driver's walk and its read; base and head share that walk-then-read pattern (finding on vanished files, below). No BEGIN…END pair occurs in any long value of this worktree's runtime folder, so the last repair changes no verdict and no cost there today.
risks: The wrapped key word is judged "no" on ordinary work. It is close: a typical export at the top of its range (13.6 KB), wrapped in base64 twice, crosses 24,000 bytes, and the owner may judge it ordinary. Copies of the real stores (343 MB of indexed repository text, scanned clean) remain in $TMPDIR/p/real because `rm` was refused twice; the lead may remove them.
lessons: Compare with the base, not only against the KPI. The miss is in a form gitleaks reaches only by decoding, which the key-piece fix doesn't see. The guard reads `>` inside a heredoc as a redirect, so write probe scripts with the Write tool. Load the base and ed2de0eb modules from single copied files with the record functions stubbed out, so full scans run and nothing is written.
proposed_decisions: Classification (DEC-809): wrapped key word, no / fails open; double-spaced block, no / fails open; many markers, no / other; vanished file, yes / other (pre-existing). Recommendation: (a) widen row W2-L419 to cover a key block's encoded form, measured on the length gitleaks must read whole (over 24,000 bytes after base64, hex or percent-encoding), with the same fix it already names (a stream reader that does not cut a block, Wave 3). Fold in the double-spaced corner (W2-L419's bound applies to the length after form feeds), and add a row for the many-markers cost. Confidence: medium. Other options, should the owner judge the wrapped key word ordinary: (b) apply now, giving each long base64 or hex word a piece of its own of up to 24,900 bytes, as key blocks get. This gains only about 900 bytes, because no piece can pass gitleaks' 25,000-byte look-ahead, so matching the base needs (a)'s reader. (c) Re-baseline: state that the bound is 24,000 bytes per word gitleaks must read whole, wrapped forms included.
unresolved: Whether the wrapped key word counts as ordinary work is the owner's call (DEC-909 item 7). The code-graph daemon cases were not run, since my sandbox refuses the tool's daemon folder; they are the lead's. The finding on vanished files was reproduced with a driver of the check's walk-then-read pattern, not through `gov check` itself.
recommended_next_action: The lead writes this probe record and passes the wrapped key word, with its classification, to the orchestrator for the owner, recommending (a) a widened W2-L419 row.

---

Verdict: pass

**Head probed:** `e00fd14a26be19069aeb904418d2dfa7ac868dcb` (w2/W2-69), above all the last repair `2f03393d`. The base `w2/integrate` and `ed2de0eb` (just before the last repair) were run beside it.

**Step 0:** (a) refused (Errno 30); (b) worked. Role, ticket, worktree, branch and head as expected. `gov.__file__` = /home/usain/gov-os-worktrees/W2-69/src/gov/__init__.py. Read refusals: 0. `gov retrieve`: used, FACET_UNAVAILABLE.

**Classification (DEC-809):** wrapped key word no / fails open; double-spaced block no / fails open; many markers no / other; vanished file yes / other (pre-existing, outside the ticket). No finding is "yes" with "fails open" or "loses work".

### Findings

**Wrapped key word: a key export wrapped as one word over 24,000 bytes is missed by the check and the filter at every placement; the base finds it.** Severity: medium.

- **What was done:**
  - Armoured PGP and PEM private-key blocks were wrapped in base64 on one line, as a Kubernetes Secret's `data` value or a CI variable holds them.
  - Placements: a standalone manifest file; a 200 KiB Markdown document, past gitleaks' first read, at 6 to 40 placements per size; and minified JSON.
  - Hex, percent-encoding and base64 applied twice were tried as well.
  - Each case was judged by this head, the base and ed2de0eb, then run through `gov rebuild` in a temporary project.
- **What happened:**
  - gitleaks alone finds every wrapping (exit 3 on the first rule set).
  - With base64 applied once, this head finds the export at every placement while the wrapped word is at most 23,868 bytes (a block of 17,900 bytes). It misses it at every placement and in every layout from 24,136 bytes (a block of 18,100), even as a standalone 24 KB manifest file.
  - Base64 applied twice: missed from 24,492 bytes encoded (a block of 13,774).
  - Hex, in a long document: missed from 24,502 bytes (a block of 12,250).
  - Percent-encoding, in a long document: missed from 25,661 bytes (a block of 23,500).
  - The base finds:
    - every standalone file tested, up to 32,004 bytes encoded;
    - in a long document, 12 of 12 placements up to 24,668 bytes, then 9, 5 and 1 of 12 at 26,004, 27,336 and 28,668;
    - every hex case tested.
  - End to end, `gov rebuild` indexed both a standalone Secret manifest and a long runbook, each holding an 18,375-byte export wrapped once (24,504 bytes). The lexical store held the wrapped key whole in one chunk (24,520 bytes), and the check then exited 0.
  - On the same two files, the base's filter kept both out and this head's let both in. A literal 13,900-byte block in the same project was kept out.
  - ed2de0eb behaves exactly as this head does. The miss comes from the 24,000-byte pieces, not from the last repair, which covers only literal BEGIN…END text.
- **What should have happened:** the check and the filter find what gitleaks and the base find, since the check must not be weakened (P-W2-62-G1).
- **Ordinary work: no, because** it needs a private-key export whose wrapped form passes 24,000 bytes in one word.
  - Wrapped once in base64, that means an export over about 18 KB. Typical RSA-4096 exports with subkeys are 10.4 to 13.6 KB (P-W2-69-R2-1), and those are found at every placement when wrapped once.
  - Only the rarer double-base64 or hex wrappings bring the bound down to about 13.8 or 12.3 KB.
  - This is W2-L419's case ("rarely", a key export over 24 KB), measured on the wrapped length.
- **Consequence:** fails open.

**Double-spaced block: a literal key block at the top size whose blank lines push it past 24,900 bytes gets no whole piece and is missed.** Severity: low.

- **What was done:** 25 export forms at 5 sizes from 9,300 to 24,576 bytes, each placed where no ordinary piece holds the block whole, past the first read: 306 placements in all.
- **What happened:**
  - All were found by both the check and the filter except one form: a 24,576-byte block with a blank line after every line was missed at 3 of 3 placements.
  - Each blank line gains a form feed, which takes that block past the 24,900-byte bound for a whole piece.
  - The same form at 24,000 bytes was found.
- **What should have happened:** a block of up to 24 KiB is found (DEC-909).
- **Ordinary work: no, because** it takes a key block within about 50 bytes of 24 KiB that also carries about 325 or more blank lines.
- **Consequence:** fails open.

**Many markers: every BEGIN marker gets its own piece up to the first END within 24 KiB, so many BEGINs before one END multiply the bytes given to gitleaks.** Severity: low.

- **What happened:**
  - Ordinary texts stay cheap:
    - a real CA bundle: 1.0 times its bytes, 0.6 s;
    - a document listing 120 BEGIN headers before one END: 11.8 times, 0.6 s;
    - 23 BEGINs per END, 1 MB: 12 times, 0.8 s.
  - A crafted text of 2,000 bare BEGIN lines per END grows 590 times (755 MB from 1.28 MB) and takes 25 s, with memory to match.
  - A text with no END adds nothing; finding the markers costs 2.2 s per 100,000.
- **What should have happened:** cost stays proportional.
- **Ordinary work: no, because** it needs thousands of BEGIN lines without their END inside 24 KiB, which is a construction.
- **Consequence:** other. It costs time and memory; a scan that cannot finish still raises.

**Vanished file (pre-existing, outside this ticket): a file under `.gov-runtime/` that vanishes between the walk and its read makes the check raise.** Severity: low.

- **What happened:** my read-only driver, which follows the check's walk-then-read pattern, met a guard snapshot file under `.gov-runtime/snapshots/` that had vanished between the listing and the read.
- **Status:** reproduced with that driver, not through `gov check` itself. Base and head share the code.
- **What should have happened:** a file gone before its read is not a scan failure.
- **Ordinary work: yes, because** the guard writes and removes those snapshot files during tool calls in the same worktree.
- **Consequence:** other. It fails closed (the check raises and records nothing).

### Probed and found sound

1. **The key-piece forms.** 306 placements cover these export forms:
   - plain key formats: PEM RSA, EC, encrypted PKCS#8, traditional encrypted PEM (Proc-Type headers and a blank line), OpenSSH, and PGP with CRLF and a Comment header;
   - line endings: CRLF, and CR-CR-LF;
   - quoting and indentation: a Markdown "> " quote, YAML indentation, tab indentation, trailing spaces, lower-case markers;
   - escaped and embedded forms: JSON with `\n`, `\r\n` and `\/`, JSON inside JSON, Python string concatenation, HTML `<br>`, XML `&#10;`, and an environment one-liner;
   - surrounding text: a certificate plus key bundle, a stray BEGIN in prose before the block, a six-dash lead.

   All were found by both the check and the filter, except the double-spaced block above. The control file was clean and let in.
2. **Read edges.** A key piece begins and ends with a dash and comes from one value only, so no read begins or ends inside a word there and no values are joined. Reading the code and the 27 fragment cases (passed) agree.
3. **The bounds.** A key piece plus its separator is at most 24,902 bytes, inside gitleaks' 25,000-byte look-ahead in every delivery. The 24,576-byte blocks were found in 24 of 25 forms. The code's bound applies to the whole block, as reading R13 has it.
4. **Today's stores and cost.** On the real stores the last repair costs nothing (41 s against 40 s before it; the base took 110 s), and they were clean on two runs. No key piece arises anywhere in this worktree's runtime folder.
5. **Freed space.** A deleted 13,900-byte block in an uncompacted store with 64 KiB pages is whole in one freed region and is flagged. With 4 KiB pages it is spread over pages and missed, which is an already recorded row.
6. **Clean-result reuse across the upgrade (DEC-853).**
   - The scan's form goes to 4. ed2de0eb's check (form 3) missed a block and recorded the file clean.
   - This head did not trust that record, found the block, and wrote a form-4 record without the finding. It found the block again on a second run.
   - The older code in turn does not trust a form-4 record.
7. **Shared gitleaks call.** The filter, the path-name judgement and the check share one gitleaks call. The filter matched the check at all 306 placements.
8. **The rebuild.** `gov rebuild` kept the document holding a literal block out of the lexical index and compacted `store.db`.
9. **Coverage unchanged.** Every file under `.gov-runtime/` is still walked and judged with both rule sets (the code there is the base's). A scan that cannot finish still raises.
10. **No lost work.** No case lost work, wrote outside the ticket's paths, or touched the acceptance tests: the last repair changes only the secrets module's pieces and its scan form.
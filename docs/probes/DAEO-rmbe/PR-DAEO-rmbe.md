---
type: probe
task: DAEO-rmbe
reviewer_session: 208f834e-a48b-4868-99c4-9306635b1959
implementer_session: 00af067b-d55b-4467-8332-ca3d002f72d1
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: e00fd14a26be19069aeb904418d2dfa7ac868dcb
---

# Probe record: W2-69 (DAEO-rmbe), the third and last review (DEC-909, the owner's exception to DEC-413)

- **What was probed.** Head `e00fd14a26be19069aeb904418d2dfa7ac868dcb` of `w2/W2-69` (CP-DAEO-rmbe-0008): the ticket's whole change against `w2/integrate` (merged in at `0be248c0`, DEC-909), above all the last repair `2f03393d` (engineer, session `00af067b-d55b-4467-8332-ca3d002f72d1`): each BEGIN…END key block of up to 24 KiB also goes to gitleaks whole, as a piece of its own, and the scan's form goes to 4. The base `w2/integrate` and `ed2de0eb` (just before the last repair) were run beside it.
- **The earlier reviews.** Review 1 (session `5d686dce-46fb-4d57-81c0-1977585bf649`, head `3fd2b5a1`) failed on F1 (key blocks over 4 KB cut by a piece edge); review 2 (session `1097b092-6b28-4a54-b722-5997c78dc932`, head `cfea8a26`) failed on F1′ (key blocks over 9,216 bytes past gitleaks' first read). Their records stay drafts. Each finding was given as described behaviour to a test-design batch (`512cb1cb`…`f3f4a4b3`; `755850bb`, `ed2de0eb`, session `797ad45b-a08e-42fa-8fcf-51dae1cfa242`), then to a fresh engineer (`8663196d`; `2f03393d`). The owner allowed this third review by DEC-909 and made it the last. This review finds F1′ answered.
- **Who probed.** A fresh read-only reviewer (role `independent-auditor`, session `208f834e-a48b-4868-99c4-9306635b1959`, 2026-10-24), started through `gov launch` under its OS sandbox with the reading tools alone, at effort max; commissioned and judged by the ticket lead (an orchestrator-role session, DEC-137). It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in this worktree.
- **Step 0.** The write outside the worktree was refused (read-only file system); `git hash-object -w` and `git update-index --refresh` worked. `gov.__file__` = `/home/usain/gov-os-worktrees/W2-69/src/gov/__init__.py`. Read refusals: 0.
- **Threat model (DEC-801, DEC-808).** Reviewers and probes judge against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Every finding carries two lines, `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`; only "yes" with "fails open" or "loses work" fails the probe.
- **Verdict: pass.** Classification (DEC-809): wrapped key word no / fails open; double-spaced block no / fails open; many markers no / other; vanished file yes / other (pre-existing, outside the ticket). No finding is "yes" with "fails open" or "loses work". The lead's judgement agrees: the first three are rows (the first two widen W2-L419), the fourth is a row for the check's walk. The reviewer calls the first finding's classification close; the lead returns it to the orchestrator as a residual with that note.

## Findings

### Wrapped key word: a key export wrapped as one word over 24,000 bytes is missed by the check and the filter at every placement; the base finds it (severity: medium)

- **What was done:** armoured PGP and PEM private-key blocks were wrapped in base64 on one line (as a Kubernetes Secret's `data` value or a CI variable holds them), and in hex, percent-encoding and base64 applied twice; placed in a standalone manifest, in a 200 KiB Markdown document past gitleaks' first read (6 to 40 placements a size), and in minified JSON; judged by this head, the base and `ed2de0eb`, and run through `gov rebuild` in a temporary project.
- **What happened:** gitleaks alone finds every wrapping (it decodes base64, hex and percent-encoding by default). With base64 once, this head finds the export at every placement while the wrapped word is at most 23,868 bytes (a block of 17,900 bytes), and misses it at every placement from 24,136 bytes (a block of 18,100), even as a standalone file. Base64 twice: missed from 24,492 bytes (a block of 13,774); hex: from 24,502 (a block of 12,250); percent-encoding: from 25,661. The base finds every standalone file tested and, in a long document, 12 of 12 placements up to 24,668 bytes, fewer beyond. `gov rebuild` indexed a manifest and a runbook each holding an 18,375-byte export wrapped once, and the check then exited 0; the base's filter kept both out. `ed2de0eb` behaves as this head: the miss comes from the 24,000-byte pieces, not from the last repair. In minified JSON this head does better than the base.
- **What should have happened:** the check and the filter find what gitleaks and the base find (P-W2-62-G1: the check must not be weakened).
- Ordinary work: no, because it needs a private-key export whose wrapped form passes 24,000 bytes in one word: wrapped once, an export over about 18 KB, beyond the typical RSA-4096 exports with subkeys (10.4 to 13.6 KB, found at every placement when wrapped once); only the rarer double-base64 or hex wrappings bring it to about 13.8 or 12.3 KB. It is W2-L419's case measured on the wrapped length.
- Consequence: fails open

### Double-spaced block: a literal key block at the top size whose blank lines push it past the whole-piece bound is missed (severity: low)

- **What was done:** 25 export forms at 5 sizes from 9,300 to 24,576 bytes, each placed where no ordinary piece holds it whole, past the first read: 306 placements.
- **What happened:** all were found by the check and the filter but one: a 24,576-byte block with a blank line after every line, missed at 3 of 3 placements, because each blank line gains a form feed and the block passes the 24,900-byte bound of a whole piece. The same form at 24,000 bytes was found.
- **What should have happened:** a block of up to 24 KiB is found (DEC-909).
- Ordinary work: no, because it takes a key block within about 50 bytes of 24 KiB that also carries about 325 or more blank lines.
- Consequence: fails open

### Many markers: each BEGIN marker gets its own piece up to the first END within 24 KiB, so many BEGINs before one END multiply the bytes given to gitleaks (severity: low)

- **What happened:** ordinary texts stay cheap (a real CA bundle 1.0 times its bytes, 0.6 s; 120 BEGIN headers before one END, 11.8 times, 0.6 s; 23 BEGINs per END over 1 MB, 12 times, 0.8 s). A crafted text of 2,000 bare BEGIN lines per END grows 590 times (755 MB from 1.28 MB) and takes 25 s. A text with no END adds nothing.
- **What should have happened:** cost stays proportional.
- Ordinary work: no, because it needs thousands of BEGIN lines without their END inside 24 KiB, which is a construction.
- Consequence: other (time and memory; a scan that cannot finish still raises)

### Vanished file (pre-existing, outside this ticket): a file under `.gov-runtime/` that vanishes between the walk and its read makes the check raise (severity: low)

- **What happened:** the reviewer's read-only driver, which follows the check's walk-then-read pattern, met a guard snapshot file under `.gov-runtime/snapshots/` that vanished between the listing and the read. Reproduced with that driver, not through `gov check` itself; base and head share the code.
- **What should have happened:** a file gone before its read is not a scan failure.
- Ordinary work: yes, because the guard writes and removes those snapshot files during tool calls in the same worktree.
- Consequence: other (it fails closed: the check raises and records nothing)

## Probed and found sound

1. **The key-piece forms:** PEM RSA and EC, encrypted PKCS#8, traditional encrypted PEM (Proc-Type headers and a blank line), OpenSSH, PGP with CRLF and a Comment header; CRLF and CR-CR-LF line ends; a Markdown `> ` quote, YAML and tab indentation, trailing spaces, lower-case markers; JSON with `\n`, `\r\n` and `\/`, JSON inside JSON, Python string concatenation, HTML `<br>`, XML `&#10;`, an environment one-liner; a certificate and key bundle, a stray BEGIN in prose before the block, a six-dash lead. 306 placements: all found by the check and the filter, but the double-spaced block above. The control was clean and let in.
2. **Read edges:** a key piece begins and ends with a dash and comes from one value only, so no read begins or ends inside a word there and no values are joined; the 27 fragment cases pass.
3. **The bounds:** a key piece and its separator are at most 24,902 bytes, inside gitleaks' 25,000-byte look-ahead in every delivery; 24,576-byte blocks were found in 24 of 25 forms; the bound applies to the whole block (reading R13).
4. **Today's stores and cost:** on copies of the real stores the last repair costs nothing (41.2 s and 40.8 s against 40.3 s before it; the base 109.5 s), clean on two runs; no key piece arises anywhere in this worktree's runtime folder (the other 2,260 files, 105.3 s, none flagged).
5. **Freed space:** a deleted 13,900-byte block in an uncompacted store with 64 KiB pages is whole in one freed region and flagged; with 4 KiB pages it spreads over pages and is missed (an already recorded row).
6. **Clean-result reuse across the upgrade (DEC-853):** `ed2de0eb`'s check (form 3) missed a block and recorded the file clean; this head did not trust that record, found the block, recorded nothing for it, and found it again on a second run; the older code does not trust a form-4 record.
7. **Shared gitleaks call:** the filter, the path-name judgement and the check share one call; the filter matched the check at all 306 placements.
8. **The rebuild:** `gov rebuild` kept a document holding a literal block out of the lexical index and compacted `store.db`.
9. **Coverage unchanged:** every file under `.gov-runtime/` is still walked and judged with both rule sets; a scan that cannot finish still raises.
10. **No lost work:** no case lost work, wrote outside the ticket's paths or touched the acceptance tests; the last repair changes only the secrets module's pieces and its scan form.
11. **Tests at this head (the reviewer's runs):** `tests/unit/secrets_check` and `tests/unit/rebuild/test_compaction.py` 35 passed; the third acceptance batch 99 of 99. The code-graph daemon cases are the lead's (the sandbox refuses the tool's daemon folder): they passed in the lead's serial run at this head's code.

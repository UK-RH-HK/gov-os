# Probe record: W2-62 (DAEO-juee), the CIT-P review

- **What was probed:** head `7d8e49d84aff` on `w2/W2-62` (tests `87cad875`, implementation `7d8e49d8`), in a session with the role independent-auditor and ticket DAEO-juee, running this worktree's own `src/` (DEC-732).
  - **Suites:** W2-62 57 passed (the live case deselected), the hook unit tests 31 passed, W1-49 with W1-29 139 passed.
  - **Probes:** 25, about 75 cases. Each case ran `template/governance/kernel/hooks/sessionstart.py` as Claude Code runs it, on a temporary git project in the scratch folder; most cases also ran the base hook from `162f17ea`.
  - **Real files:** the head hook ran read-only on the main tree's real orchestrator checkpoint and on this worktree's lead checkpoint. Claude Code 2.1.292's Read tool was used on probe files to compare the stated lines with what a session receives.

- **What it found:** findings first, most severe first, then what was sound.

  1. **A fence the section reader does not recognise ends the section early, and the shortened part is called whole.**
     - *What was done:* a RESUME HERE section with a step to run before the merge, written as a block fenced by three tildes. A second case used a four-backtick block quoting a brief whose own three-backtick block holds the command. Inside the block, at the left margin, was a shell comment (a hash, a space, text). The section's next steps and real last line came after the block.
     - *What happened:* the head hook ended the section at the comment line. It stated "lines 3-8, 77 characters" against the 12 lines and 223 characters written (the quoting case: lines 3-10, 110 against 250), and injected that part under the words "The whole RESUME HERE section". When the real section was long (15,226 characters), the hook still stated the short range and injected it as whole. The next steps reached the session neither by injection nor by the stated range.
     - *Compared with the base:* the base hook ended the section at the same line, so the boundary comes from W1-49. What is new is the "whole" label and the stated range.
     - *What should have happened:* the section runs to the next heading of its level outside every fenced block, or the hook does not call it whole when it cannot be sure (W2-M372: "otherwise refuses to pass it as complete").
     - *Mitigation:* the first sentence of the injection still tells the session to read the whole checkpoint file.
     - *By design, related:* a heading of the same level as RESUME HERE ends the section too. The skill's resume rule does not tell the writer to put the parts of the resume under deeper headings.
     - *Severity:* medium, mitigated; a row.
     - Ordinary work: no, because it needs a tilde fence, or a fence nested inside a longer fence, holding a hash-space line at the left margin inside RESUME HERE. The two real checkpoints probed contain no fenced block at all, and the real orchestrator puts its five parts at the third level under a second-level RESUME HERE.
     - Consequence: loses work

  2. **The bound is counted in code points; Claude Code very likely counts UTF-16 units.**
     - *What was done:* a section with two green-circle status emoji (outside the Basic Multilingual Plane, BMP) on each line, sized so the injection is exactly 10,000 characters as the hook counts them.
     - *What happened:* the hook judged it to fit and injected the section whole. The same injection is 10,712 UTF-16 units, the length JavaScript gives, and the lead saw 10,300 ASCII characters not injected. With em-dashes the two counts agree (10,000 and 10,000), so the lead's em-dash probe could not tell them apart.
     - *What should have happened:* the hook counts in the unit Claude Code uses, or keeps a margin under the measured bound.
     - *If Claude Code moves such an injection to a file:* the preview opens with the instruction (path, line range, size) and the saved file holds the whole text, so the section still reaches the session through the stated lines.
     - Not reproduced live (no network). *Severity:* low.
     - Ordinary work: yes, because status emoji outside the BMP occur in agent-written notes and the bound has no margin, though the two real checkpoints hold none.
     - Consequence: other

  3. **A lead in a linked worktree is pointed at its branch's roster and its branch's copy of the prompt.**
     - *What was done:* a main tree and a linked worktree cut before the roster names the prompt, then the roster line committed on main.
     - *What happened:* the main tree's orchestrator was told to read the named prompt. The lead in the worktree was told to read no prompt, and the pointer to appendix A5 dropped out of its sentence. That lasts until its branch merges main.
     - *Once the branch's roster names the prompt:* the lead reads the branch's copy. In this repository, this branch's appendix A5 still says "if you pass about 300k tokens, write the checkpoint and return LEAD_CHECKPOINT". DEC-838 replaced that rule on main, and main's A5 differs in 6 lines.
     - *What should have happened:* the lead is pointed at the prompt in force (main's), or the record says that leads read their branch's copy.
     - Pre-existing in kind: the base hook also named a path inside the worktree. *Severity:* low.
     - Ordinary work: yes, because every lead works in a worktree cut from main at one moment, while the owner revises the prompt during the wave (A5 changed on 2026-10-19).
     - Consequence: other

  4. **The change record is incomplete for CAP-33.d.**
     - *(a) Corroboration:* the research record holds only the orchestrator's sizes (9,500 whole; 12,000 and 60,000 moved to a file). Those put the threshold between 9,500 and 12,000, yet the record concludes context "arrives whole only up to about 10,000 characters" and keeps the cap at exactly 10,000. The corroboration that supports exactly 10,000 is missing, though CAP-33.d and the change skill ask for it: the lead's probe of 2026-10-19 (10,000 ASCII characters whole; 9,000 and 4,000 em-dashes whole; 10,300 not injected; the bound counts characters, not bytes).
     - *(b) Impact table:* it says the W1-29 suite was revised, but its files are unchanged; it inherits the W1-49 fixture. It also names no impact beyond the hook and the skill, missing the three generated copies of the checkpoint skill that must be rebuilt (the W1-38 and `gov check` red).
     - *(c) Sources:* `decisions_carried` leaves out DEC-851, a ticket source. DEC-851 puts the standing rules into RESUME HERE so that they come back after every compaction, which is why the section will outgrow the bound.
     - *(d) Live case:* the record does not say that the live case also passes on the base hook.
     - *What should have happened:* the record, or its CIT-E, carries these. *Severity:* low (documentation).
     - Ordinary work: yes, because the CIT-E author and the next reviewer rely on the record as written.
     - Consequence: other

  5. **Until the roster line lands, no session in this repository is told its prompt.**
     - *What was done:* the head hook run read-only on the main tree's real orchestrator checkpoint and on this worktree's lead checkpoint.
     - *What happened:* both sections were delivered whole and correctly ranged (lines 3-72, 6,429 characters; lines 3-21, 5,753 characters; injections of 6,748 and 6,117 characters). No prompt was named, because the roster has no prompt key yet. The orchestrator's real RESUME HERE does not give the prompt's path either, so only CLAUDE.md names it.
     - The line the CIT-P proposes, added to a copy of the real roster, is read correctly.
     - *What should have happened:* the roster line lands in the same batch as the merge (the known package). *Severity:* low (sequencing).
     - Ordinary work: yes, because every orchestrator and lead session after the merge is affected until the line lands.
     - Consequence: other

  6. **The acceptance suite does not test the route it was written for, and misses ordinary forms.**
     - *Live case:* it passes on the base hook too (the lead's run), so it shows the session reading, not that the new route is what delivers the section. The W2-62 README's red reason for it ("on the base it would fail") is contradicted by that run.
     - *Deterministic cases:* they use only ASCII sections of short lines and backtick fences at the left margin. None has CRLF, non-ASCII text at the edge, characters outside the BMP, long unwrapped lines, tilde or nested fences, two RESUME HERE headings, or a worktree whose roster differs from main's.
     - *What should have happened:* a note to the test designer through the orchestrator (MR-3). *Severity:* low (coverage).
     - Ordinary work: yes, because the gaps are ordinary checkpoint forms.
     - Consequence: other

  7. **With CRLF line ends, the stated size counts the carriage returns.**
     - *What was done:* the ordinary checkpoint written with CRLF line ends, with a state block appended by the PreCompact hook.
     - *What happened:* the range was right (lines 3-27, the author's section), the block was recognised and the staleness warning given. The size read 685 characters against the 660 written (one more per line), and the injected section carried the carriage returns. Nothing was lost.
     - *Severity:* cosmetic.
     - Ordinary work: yes, because a checkpoint touched by a Windows tool on this WSL machine can carry CRLF, though the real ones carry none.
     - Consequence: other

  8. **The first RESUME HERE heading wins.**
     - *What was done:* an older section renamed "RESUME HERE (superseded …)" kept above a newer "RESUME HERE".
     - *What happened:* the head hook, like the base, delivered the superseded section with its range and called it whole; the newer state was not injected.
     - *What should have happened:* one RESUME HERE block at the top, as DEC-792 asks; the reader could warn when it finds two.
     - Pre-existing. *Severity:* low; a row.
     - Ordinary work: no, because DEC-792 asks for one RESUME HERE block at the top, updated in place, and the real checkpoints hold exactly one.
     - Consequence: loses work

  **Probed and found sound:**
  - **The stated lines match what the Read tool returns.**
    - The hook counts lines on line feeds only, and so does Claude Code 2.1.292's Read tool. CRLF is one line in both. A lone carriage return, a form feed, NEL and the Unicode line separator split a line in neither. The base hook split lines on more characters than this.
    - The Read tool returned a 4,999-character line and a 24,513-character line whole.
    - In every ordinary case the stated lines are exactly the section the author meant. The cases: LF and CRLF; em-dashes; a heading with trailing text and an em-dash; nested third-level headings; backtick fences holding hash lines; a fence inside a list item; a state block after the section; unwrapped paragraphs of 3,297 characters; sections of 9,522, 9,629, 39,614 and 6.2 million characters.
  - **Real checkpoints.** The main tree's orchestrator checkpoint (one second-level RESUME HERE, ended by its archive heading, state block recognised) and this worktree's lead checkpoint parse as their authors meant. Both are delivered whole, inside the bound.
  - **The bound.** An injection of exactly 10,000 characters with em-dashes is delivered whole and is 10,000 UTF-16 units. One character more and the section is delivered by instruction alone. The instruction and the staleness warning are never cut.
  - **The trimming.** Under a 30,000-character ready list, the ready list is the part trimmed: cut mid-line without a marker, as on the base. The context packet produced no summary in the temporary project and the checkpoint brief did not appear, so their trimming was not observed directly.
  - **By design:** a first-level RESUME HERE above second-level history runs to the end of the written part (lines 1-3007, 355,958 characters, by instruction). It costs context but loses nothing.
  - **The prompt.**
    - Every ordinary roster form names the path: plain, with a trailing comment, quoted, as a block literal, with CRLF, with a byte-order mark.
    - Each of these names none: an empty value, null, a blank string, a list, a number, a mapping, invalid YAML, the key one level too high, no roster, a directory, bytes that are not UTF-8.
    - PyYAML imports for the live `python3`.
    - With the key set, a lead is sent to appendix A5 of the named prompt, and the Wave 2 prompt has it ("### A5. Ticket lead").
  - **No fail-open, no block.**
    - Six role values other than exactly "orchestrator" got no orchestrator injection: engineer, independent-auditor, empty, "Orchestrator", " orchestrator", unset.
    - Eight stdin forms all exited 0 within 0.11 s with the instruction: empty, an array, a string, null, a number, no source, a source that is not a string, 5 MB of input.
    - A 12 MB checkpoint took 0.10 s. The hook writes nothing.
  - **Scope and tests.**
    - The implementation commit touches only the ticket's four paths, and the acceptance tests are unchanged since the test designer's commit.
    - The test designer's W1-49 revisions only replace "head kept, said truncated" with "line range given, never truncated", and add a fixture roster.
    - The engineer's unit-test edits replace the Wave 1 constant with a roster prompt and make the cut test stricter.
  - **The skill.** The resume rule states the full session state, retrieval and context packets, a checkpoint at every handover and the lifted 8,000 limit, and it describes the delivery the hook performs. Version 1.1.0.

- **Judgement:** **pass.** No finding answers "yes" to ordinary work together with "fails open" or "loses work".
  - Findings 1 and 8 can lose part of a section, but each needs a checkpoint form that the project's rules and its real checkpoints do not use. They are rows for W2-10 (which holds the hooks next) or the Wave 3 hardening pass.
  - Findings 2 to 7 are "other"; their fixes ride along with the CIT-E and the merge batch (DEC-802).

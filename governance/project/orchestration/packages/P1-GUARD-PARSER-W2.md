# P1-GUARD-PARSER-W2: the product's guard reads what a Bash command writes, in Wave 2 (before EXAMIN's copy)

For the owner. Asked for in DEC-1027 ("propose bringing ACT-GUARD-FIX-3's eight parser lines into a Wave 2 ticket
before EXAMIN's copy, as a P1"). A new ticket, so yours (DEC-974).

## 1. Context
ACT-GUARD-FIX-3 (applied by your operator this morning, `e662684a`) fixed this repository's own five-rule hook:
`.claude/hooks/bash_writes.py` reads what a Bash command writes (heredocs, the command's own variables, loops,
substitutions inside quotes, keywords and prefixes, line continuations, inline Python), so rules 1 and 5 stopped
refusing on words. The product's guard, which every adopted repository runs, was not touched: its hook calls
`gov.guard.decide.decide` and `gov.guard.reads.policy_refusal`, whose Bash parser (`_extract_bash_write_targets`,
`src/gov/guard/decide.py`) has the same weakness, and it refuses **any** unresolvable Bash write for every role. The
package named the product half and placed it in W2-42 (`DAEO-fau3`, FULL), deferred to Wave 3 (ACT-GUARD-FIX-3 §7).

## 2. What happened (the evidence)
- On the 61 logged commands, the product's parser cannot resolve the writes of **22** (36 %); with the fix's
  shell-level reading it would be **1** (row 39's glob). The product refuses each of the 22.
- The fix's evidence: 61-row corpus 31 → 2 refused; 0 of 167 planted writes missed (today's hook 75); a 4,893-command
  history differential (67 newly passed, none writing the tests; 13 newly refused, failing closed); two independent
  review rounds, the second PASS with READY computed; 270 stable tests (`packages/ACT-GUARD-FIX-3.md`, `.diff`,
  `test_guard_fix_3.py`).
- The first false positive under the new hook arrived at 10:39 (guard 71, mine: inline Python writing `.tickets/`
  through an f-string while its text named the acceptance folder; the fix's F4 rule failing closed, as designed).

## 3. Why it matters
EXAMIN's agents run the product's guard, not ours. Ordinary commands (a heredoc that writes a helper script, a loop
over files, `B=/tmp/x; mkdir $B/r`, `"$( … )"`, `timeout 60 …`) would be refused about a third of the time in our
measured mix. Each refusal is an honest agent stopped (fails closed, so no security risk), costs 1 to 4 minutes and a
brief gap, and erodes trust in the guard during the copy that is meant to prove the Gov OS. It is K9's measure in
practice: EXAMIN's copy is judged on ordinary work getting done under the guard.

## 4. Options
- **(a) A new Wave 2 ticket, W2-42a (recommended):** the eight parser KPI lines of ACT-GUARD-FIX-3 §7 (heredocs not
  read as shell; the command's own variables and literal loops; substitutions in quotes, `sh -c`, `eval`, keywords and
  prefixes; an unmatched glob is its literal path; `git checkout`/`restore`/`rm`/`mv`, `dd of=`, `truncate`,
  `sort -o`, `rsync` read as writes and patch appliers as unresolvable; the read judge's `$((…))` and data heredocs;
  backslash continuations; a written heredoc body that the command may run judged as that file's code), in
  `src/gov/guard/decide.py` and `src/gov/guard/reads.py` (`_set_aside`, `_Judge.tool`/`command`). FULL (the guard is
  core: QA one by one, DEC-959 item 3). The engineer may port the reviewed `bash_writes.py` as its basis; the test
  designer writes from the KPIs and may take the 167 planted cases and the 61-row corpus as fixtures (no secrets in
  them). W2-42 keeps its other rows in Wave 3. **Order:** after W2-09 or beside it with the files split (W2-09 and
  W2-10 hold `src/gov/guard/**`; W2-10 is dropped, DEC-954); before EXAMIN's copy. **Cost:** about 1 to 1.5 days of
  lead time (port and adapt about 1,400 lines, two review rounds at most); the machine's embedder is not involved.
  **After it lands:** the five-rule hook can call the product's parser and `bash_writes.py` slims away (a later ACT).
- **(b) Bring W2-42 forward whole into Wave 2.** All its eight rows (missing role, links, late paths, atomic saves)
  plus the parser lines. About 3 days; a bigger review; more risk to the timeline.
- **(c) Leave it in Wave 3.** EXAMIN's copy runs with about a third of ordinary Bash writes refused; measured cost
  1 to 4 minutes each; the copy's results would mostly measure the guard's friction.

## 5. Recommendation
**(a), confidence high** on the need (the measurements), medium on the estimate (the port's adaptation to the
product's two call sites). Classification: no finding; a known fail-closed friction in the product's guard, ordinary
work yes, consequence other.

## 6. What it blocks, and what waiting costs
It blocks nothing today. Waiting past EXAMIN's copy costs the copy's measure (K9). It needs a slot in the K3 stream
before 2026-11-14's estimate; it does not touch memory's chain.

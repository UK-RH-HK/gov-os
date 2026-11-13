# R2 — why leads "read about 3 % of their brief" (DEC-1050 (7))

**Headline.**
1. **The 3 % figure measured something else.** It is 3 % of the brief's *mandated decision reading list*: a median 7,950 of 240,139 characters (A1-10). The brief itself reaches every lead whole, as its first prompt. Leads follow it closely: **11 of the 14 commands I measured were run by 83 to 100 % of the leads whose brief named them.**
2. **Leads skip the reading list because the brief already restates what it holds.** The list asks for 106 decisions. The brief's own body cites 103, and DEC-851 copies every standing rule into it. Leads look up a median of **2** decisions by id, and **0** from the list.
3. **Nobody designed the brief. It grew by itself.** 46 of its 50 commits are `decision-record` commits by the orchestrator, made as a side effect of DEC-851 (every rule copied in) and DEC-943 (every gap gets a line). Across all commits, 274 lines were added and 75 deleted. The 2.6k-character ticket part sets the run, but it is followed by 53k of common text written for every kind of run.
4. **Where leads really lose time is doing, not reading.**
   - 25 % of their tool calls are waits in a poll loop (4,528 calls).
   - 12 % are ceremony steps (2,135 calls).
   - Each lead re-writes the verification wrapper: 343 scripts in 117 of 159 sessions.
   - Leads hit 218 harness permission denials (`rm` the most common) and 75 blocked `sleep N; …` chains.
   - 52 % of the minutes they report as brief gaps were spent on machine contention, which no brief line can fix.
5. **Better templates work when they give a working form.** Once the command forms were in the brief (29 Oct), the share of lead sessions with a guard refusal fell **from 68 % to 17 %**. The refusals left are mostly Rule 1 false positives (G-1).

| id | what | where (paths, tickets, decisions) | cost (machine / tokens / owner; source) | what it protects | DEC-1010 test: in aim? ordinary work? fails open or loses work? | recommendation | what lifting takes (code, tests, tickets, config) | depends on |
|---|---|---|---|---|---|---|---|---|
| R2-1 | **The "3 %" is 3 % of the mandated decision list, not of the brief.** The brief is the lead's whole stdin prompt, and leads act on it. | A1-10; `LEAD-w2-common.md` l.80-88; R-2 | None in itself. The misreading points the fix at reading, when the cost is in doing (R2-5 to R2-9). | — | — | **Correct the reading** in P1-LIFT-1 and the plan. The template's measure is "did the lead do it": §E1 below shows how to count it. | Text in the plan. | — |
| R2-2 | **The mandated reading list**: 106 decisions, 8 sections of the w2 prompt, 4 sections of the WBS, the skill, 4 templates and JUDGEMENT | `LEAD-w2-common.md` l.80-88 (1,643 chars) | T: small, because it is ignored. 135/159 sessions touch the register, but the median is 2 distinct DECs per session, and 0 of the 106 (mean 0.7, max 15). 61 of the 106 were never opened by any lead. **Measured, 159 transcripts** | A shared reading of the rules | In aim: weakly, because the brief already restates the rules (DEC-851). Ordinary work: yes. Fails open: no | **Replace** with what leads do use: the ticket file, its `sources`, the WBS card, and `gov retrieve "<which decision governs X>"` for anything else (see R2-16) | Brief lines 80-88; a template line | R-2; R3 |
| R2-3 | **How it grew: no owner, two growth engines.** DEC-851 writes every standing owner rule "into each place a session reads it". DEC-943 turns each gap into a line "the same week". | `git log` of `LEAD-w2-common.md`: 50 commits. 43 signed `Role: orchestrator`, 4 `owner` (19-20 Oct), 3 unsigned (24 Oct). 46 are `Task: decision-record`, 1 is DAEO-sdxk. Size 22,401 (19 Oct) → 54,474 (now). Lines +274 / −75 | O: one more edit per decision (part of R-9's 2-3 edits). T: about 17k tokens per launch (A1-9, est. $0.48 a launch; tokens are not the owner's measure, O-1) | A rule reaching the next session | In aim: yes for rules that change a lead's actions. No for history, rationale and lifted lists. Ordinary work: yes. Fails open: no | **Scope DEC-851**: the template gets a rule only where it changes what a lead does, in imperative form, with no history. The decision id goes in brackets. **Give the template one owner** (product-spec writes it; the CTO approves). Test each change against one lead run (§E1's counts), not by adding a paragraph | Amend DEC-851 item 1 (owner) and DEC-943 item 1 (R2-13) | R-9, R3 |
| R2-4 | **Structure: the run is in the 5 % at the top. The common 95 % covers every kind of run.** | Ticket part about 2.6k (e.g. `briefs/W2-126-part-run1.md` 2,599 of 55,982). Common sections: "Owner decisions in force" 21,344, standing rules 14,387, **the loop 9,900 (18 %)**, return 3,817, reading 1,644. 471 A5 briefs by name: 242 runs, 29 resumes, 100+ "head/note" follow-ups, lands; 14 parts are tests only | A tests-only run (W2-126) and a land (W2-112 r3) still get the full loop: review rounds, probe records, serial phases | — | Not in aim where a section does not apply to the run | **One short template per kind of run**: tests only; implement and verify; review round; resume; land. Order: identity → this run's steps → the exact commands (as scripts) → paths → return. Rules come as a numbered list of the five guard rules plus the role boundaries. The decisions' text goes to the register. | `build_lead_brief.py` (47 lines) picks the template by run kind; the template texts | R3 (templates) |
| R2-5 | **Ceremonies leads do faithfully.** Of the sessions whose brief named each one: `.git/hooks` check 157/158 (576 calls); `du --inodes` 96/97 (345); disk gate 90/97 (260); tripwire 113/124 (369); `keyword_warn.py` 79/86 (169); `trailer_gate.py` 65/73 (110); collect-only 75/107 (105); `gov checkpoint` 137/158 (216); `gov.__file__` 130/156 (231); `printenv` 159/159 | Brief l.39, 44-52, 100, 105, 113, 116, 164, 166 | **2,135 calls, 11.6 % of all 18,469 lead calls; median 14 per lead.** At A1's median context of 141,723 tokens a call, that is about 2.0 M cache-read tokens a lead (est.). The lead's time: one turn each | Hooks: W1 containment. Tripwire: worker writes. du/disk: the disk. keyword_warn: gitleaks (off, DEC-1045). trailer_gate and collect-only: lifted by the brief's own line 20 | The hooks check, `keyword_warn`, collect-only and `trailer_gate` fail the test (nothing to guard, or lifted). The tripwire and the disk gate pass (§4 of the combined list) | **The template carries only what passes.** The tripwire and the disk gate go inside one script (R2-9), not as separate steps. `keyword_warn`, collect-only, `trailer_gate`, the hooks check and the three `du` measures leave it. A step a lead obeys costs a turn every time, so a line needs a reason to be in the brief, whether or not leads read it | Brief edits | **Owner**: R-4 and R-5 refused as written. New evidence: compliance is 83-100 %, so these lines cost work, not reading |
| R2-6 | **Waiting is a quarter of a lead's work.** The brief's rule: Monitor is refused by the guard (DEC-685); wait with `until [ -s f ]; do sleep 20; done` in the foreground, under the 10-minute tool limit, repeated | Brief l.33, 103; Claude Code blocks `sleep N; cmd` | **4,528 `until`/`sleep` calls; median 25 a lead; 24.5 % of calls.** The harness blocked 75 `sleep N; …` chains, and its message tells leads to "use Monitor", which the guard refuses. 104 gap lines and 3,824 of 7,424 stated minutes (52 %) are about waiting for slots, locks, queues or the nightly. Tokens: about 4,528 × 141.7k ≈ 0.64 B cache-read tokens (est.) | Long runs survive the tool's limits | Ordinary work: yes. The cost is real, but no brief line removes the wait | **Give one wait tool.** `wait_for.sh <exit-file> [<max-s>]` blocks up to 9.5 min and prints the tail and the exit code: one call per 9.5 min instead of a hand-written loop. Or let the guard accept `Monitor` (a known harness tool now). The contention itself belongs to the dispatcher (LB, P1-LOAD-BALANCE-1) | One 20-line script with a test; or a guard tool-list change (CIT-P) | The guard's tool list (G-rows); LB |
| R2-7 | **Command forms: the brief fix that worked.** "No shell variable as a write target, no here-doc, no backticks, no long `python3 -c`; put it in a script file" | Brief l.54-60, added in 47e95647 (29 Oct, DEC-941 4a) | **Before: 102 guard refusals in 93 sessions (63 sessions, 68 %). After: 21 in 66 (11 sessions, 17 %).** Before, these were 55 unresolvable or variable writes and 37 "cannot be read (pause)". After: 17 Rule 1 refusals of *reads* under `tests/acceptance/` (`ls`, `grep`, `git diff`, `head`: false positives), 3 variable writes and 1 pause form | The guard reading a command whole | In aim: yes (roles apart, rule 1). Ordinary work: yes | **Keep, in positive form**: give the forms that work (a literal path, a script file under scratch, the Write tool), not only the forbidden ones. **G-1** (approved) removes the 17 read refusals | Template text; G-1's code | G-1 |
| R2-8 | **Harness permission denials the brief never names.** The brief explains the guard only. Claude Code's own approval prompts refuse a headless session | `permission_denials` in the lead logs; brief l.69 ("you cannot remove your own temp folder… never try another form") | **218 denials in 110 of about 170 lead logs:** `rm` 55, `python3` 39, `git` 16, `mkdir` 15, `until` 12. In the transcripts: 29 "requested permissions" and 23 `rm` approvals. 17 gap lines in 16 returns | Nothing in the aim; these are the harness's defaults | No / yes / no | **Lift with O-7** (approved, DEC-1050 (8): `rm` free except catastrophic deletes). The template states which commands the harness allows (from the settings' allow list), so a lead never meets a prompt it cannot answer | Settings allow rules (owner operator); template line | O-7 |
| R2-9 | **Each lead re-builds the verification wrapper.** The brief gives 400-900-character command lines (the parallel and serial runs, l.155-156; launches, l.93 and 97) instead of scripts | Leads' `Write` calls | **692 helper scripts written:** 343 run, verify or suite wrappers in **117 of 159 sessions**; 84 JUnit, JSON or log summarisers in 44; 16 wait scripts. 45 gap lines and 1,470 minutes are about selection, the serial phase and verification (e.g. "`GOV_CLOSE_SERIAL_ONLY_GIVEN` must hold only the entries run", 18 lines in 14 returns, before T-5) | The close's form of the run | In aim: yes (tests that match the KPIs, pass green) | **Ship the commands as tools**: `lead_verify.sh <tree> <W2> <ID>` (selection, then parallel, then serial in the close's own phase, JUnit, a summary line, an exit file, under its slot) and `launch_worker.sh <role> <effort> <brief>`. The template names them in one line each | Two scripts of about 60 lines each, with tests (tools lane); template lines | T-5 (done), R-1's "commands move into tools" |
| R2-10 | **The worker-brief templates sit inside the CTO's 116 KB prompt.** Appendix A (A1-A5, 8,643 chars) plus the kernel's `brief-*.md` (4 files, 17,345 chars) | `prompts/w2-orchestrator.md` l.372-430; `template/governance/kernel/templates/` | **94/159 leads open the w2 prompt (208 accesses, median 26,498 chars read).** At least 50 of them, a lower bound, go to Appendix A or name it. 81/159 open the kernel templates. Leads then write **399 worker briefs, median 12,605 chars**, 2 a lead. 12 sessions copied other tickets' briefs (26 calls, 164k chars) | Worker briefs that carry the rules | In aim: yes (roles apart; the builder never reads its tests) | **One template per worker role, filled by a builder** (as `build_lead_brief.py` does for leads). The lead writes only the ticket's facts (behaviours, sources, paths). Appendix A leaves the CTO prompt. | A builder of about 50 lines; the templates (R3) | R3, O-1 (the prompt) |
| R2-11 | **Two lead templates disagree.** The kernel's `brief-lead.md` (10,070 chars) says "Run everything in the foreground… nothing started in the background is ever read". The project brief requires background runs (DEC-731) | `template/governance/kernel/templates/brief-lead.md`; `LEAD-w2-common.md` l.24, 92 | Confusion for any adopter, and for the next wave | One lead procedure | In aim: yes (the product's own template) | **One template**: the kernel's is the base and the project fills its settings. The product's version must be the one that works here | Kernel template (CIT-P) | R3, K-1 |
| R2-12 | **Stale and contradictory lines still in the brief after DEC-1050's edit** | l.22 "Until the guard is cut to its four rules" (it has five now). l.38 and l.73 "until W2-58 lands" (closed). l.159 "until W2-70 merges" (closed). l.20 "Lifted: … no separate collection run; `trailer_gate.py` as a stop" against l.39 and l.113, which still require both. l.116 W2-L423 after DEC-1045. l.72 repeats l.21. Step 7's checkpoint record *after* verification against "DONE with the exact head you verified" (2 returns report this). l.106 "a full rebuild before your verification" (M-3) | 16 gap lines (169 min) name a stale or contradictory line. Each stale line still gets obeyed (R2-5: collect-only 70 %, `trailer_gate` 89 %) | Nothing | No | **Fix in the template rewrite.** A line with "until X" carries the ticket id and is removed when that ticket closes (the builder can refuse a closed id) | Brief edits; a 10-line check in `build_lead_brief.py` | R-3 (refused as written; this is the same evidence) |
| R2-13 | **The brief-gaps loop (DEC-943) collects, but does not close.** | Returns' `brief_gaps:`; `governance/project/orchestration/brief-gaps.md` | **511 gap lines and 7,424 stated minutes in 83 returns.** The register holds 18 rows, all from 30 Oct, and 2 are fixed. Gaps per return: 6.7 (30 Oct), 7.1, 5.8, 5.1 (2 Nov), while the brief grew 40 %. Kinds: contention 104 lines / 3,824 min; ticket-specific 93 / 829; guard forms 70 / 685; paths, environment and tools 58 / 555; sandbox and `gov launch` 51 / 375; decision reading 50 / 301; harness 35 / 263; selection 34 / 423; stale 16 / 169 | The template's feedback | In aim: yes, as the measure R3 needs. As written (a paragraph per gap): no | **Keep the one-line `brief_gaps:` form; change what happens to it.** The template owner counts the gaps weekly by kind. A gap closes through a tool or a template line that is then measured (§E1), never through a paragraph. Gaps about contention go to the dispatcher's list | Amend DEC-943 item 1; a 40-line counter (this report's `gaps.py`) | R-5 (refused as written), R3 |
| R2-14 | **Delivery: one stdin prompt; the ticket part first, then the common text.** The builder drops the common text's first three paragraphs and fills 8 placeholders | `.gov-runtime/scratch/orchestrator/tools/build_lead_brief.py`; in the transcripts the first user message is the brief (`promptSource: sdk`); median 37,941 chars over the period, 55-59k now | T: about 17k tokens per call (A1-9) | — | — | **Keep the mechanism** (it works and is simple). Change only what it assembles (R2-4) | — | R2-4 |
| R2-15 | **Orientation before any work** | Transcripts | **Median 24 tool calls (p25 16, p75 34) and 107k chars of tool results before the first worker launch** (145 of 159 sessions launch one). Of what is read: the w2 prompt 14 %, `src/` 13 %, the register 10 %, `tests/acceptance` 10 %, packages and docs 7 % | — | — | **The template gives the lead its first 10 calls**: identity check, resume check, the ticket file, the paths. The ticket part names the code to read (a `gov retrieve` question, or 3 to 5 paths) | Template lines; ticket part | R3 |
| R2-16 | **Leads seldom use the memory tool themselves** | Brief l.30 tells leads to put `gov retrieve` into worker briefs, not to use it themselves | **22 of 118 sessions (19 %) whose brief named it ran `gov retrieve`.** The register is reached by `grep` 188 times, `sed` 116, `awk` 28, `Read` 24 | The aim's item 1 (memory) | In aim: yes | **The template tells the lead to ask `gov retrieve` first** ("which decision governs X", "where is Y implemented") and to grep only by id. This replaces R2-2's list | Template line | Memory tickets (W2-126 and others) |

Re-reading is **not** where leads get lost: 94 re-reads of one file in 159 sessions (median 0). Wrong paths are mostly harmless:
- 42 of the 125 "missing file" errors are the brief's own resume probe (`ls .gov-runtime/scratch/lead/CHECKPOINT.md`).
- 29 are polls for a file not yet written.
- 54 are wrong paths in commands. These are often `.git/config.lock` contention from parallel `git worktree add/remove`, which belongs to the machine, not the brief.

## What a lead in a 170,000-line repository needs, and what in today's brief is noise

**Needs:**
- **Who and where:** ticket, branch, worktree, profile, allowed paths.
- **This run's steps:** the ticket part, which is good today.
- **The five guard rules and the role boundaries,** in 10 lines.
- **The commands that work, as scripts:**
  - verify;
  - launch a worker;
  - wait;
  - rebuild;
  - merge the tests.
- **The command forms the guard and the harness accept.**
- **How to ask memory:** `gov retrieve`.
- **The return:** the twelve fields, `guard_refusals:` and `brief_gaps:`.
- **What to do when blocked:** PACKAGES with the six parts.

Measured from today's brief, this is about the loop (9.9k) plus the return (3.8k) plus the forms (0.7k), most of which shrinks into script names.

**Noise, measured against what leads do:**
- the 21k "decisions in force" (history and rationale; leads look up a median of 2 DECs);
- the reading list;
- the lifted list, and the stale "until X" lines (R2-12);
- ceremonies that guard nothing in the aim (R2-5);
- the duplicated lines (l.72 = l.21; DEC-898's lines twice, l.44-52 and l.66-70);
- for every kind of run, the sections that do not apply to it (R2-4).

## Evidence

All scripts and outputs are in `/tmp/gov-os-inv-R2/`.

**E1. Corpus and compliance.**
- `extract.py` reads every `~/.claude/projects/-home-usain-gov-os-worktrees-W2-*/*.jsonl` whose first non-sidechain user message starts with "You are the ticket lead": **159 lead sessions, 18,469 tool calls** (Bash 15,005, Write 1,623, Read 862, Edit 790, Grep 117). The output is `leads.json`.
- `briefflags.py` checks each session's own first prompt for each rule's text.
- `an2.py` counts sessions that ran each command:

| rule | briefs that carried it | leads that ran it |
|---|---|---|
| printenv | 159 | 159 (100 %) |
| .git/hooks | 158 | 157 (99 %) |
| du --inodes | 97 | 96 (99 %) |
| disk_gate | 97 | 90 (93 %) |
| keyword_warn | 86 | 79 (92 %) |
| tripwire | 124 | 113 (91 %) |
| trailer_gate | 73 | 65 (89 %) |
| gov checkpoint | 158 | 137 (87 %) |
| select_tests | 49 | 41 (84 %) |
| gov.__file__ | 156 | 130 (83 %) |
| tests worktree | 48 | 35 (73 %) |
| collect-only | 107 | 75 (70 %) |
| full gov check | 113 | 78 (69 %) |
| verify_lock | 49 | 26 (53 %) |
| gov accept | 47 | 13 (28 %) |
| gov retrieve | 118 | 22 (19 %) |

`brief_gaps:` appeared in 60 of the 63 finals whose brief asked for it, and `guard_refusals:` in 46 of 49.

This is the measure the templates need: **for each line of the template, the share of runs that did it**.

**E2. Decisions opened.** `an3.py`:
- Register access by form: grep 188, sed 116, awk 28, Read 24, tail 14, cat 14.
- Distinct DEC ids in register commands: median 2 a session; 29 sessions with none. Of the 106 on the list: median 0, mean 0.7.
- Most looked-up: DEC-941 (12 sessions), 959, 954 (7), 895, 957, 963 (6).
- `sed -n a,bp` line ranges carry no id, so this is a lower bound.

**E3. Who wrote it.** `git log --follow` of `governance/project/briefs/LEAD-w2-common.md` gives size per commit in `/tmp/gov-os-inv-R2/history.txt`:

| date | size (chars) |
|---|---|
| 19 Oct | 22,401 |
| 22 Oct | 28,568 |
| 26 Oct | 33,648 |
| 29 Oct | 37,112 |
| 30 Oct | 48,154 |
| 31 Oct | 48,829 |
| 1 Nov | 53,268 |
| 2 Nov | 54,474 |

The biggest single steps came with decision records: DEC-952/953 +4,075; DEC-958 +641; DEC-959 +1,085; DEC-963 +1,550. No commit is a review or a test of the brief. The only test file that names it is `tests/acceptance/W2-59/README.md`, which pins no text, so rewriting the brief breaks no test. The brief section sizes come from an `awk` pass over the headings.

**E4. Refusals.** `an4.py` and the inline scripts:
- **Errored calls:** 764 of 18,469 (4.1 %), median 4 a session.
- **Guard (`PreToolUse`) refusals:** 124 in 74 sessions:
  - 58 `Bash write to … denied`;
  - 38 "cannot be read… gov pause";
  - 17 acceptance-test writes (all of them reads, listed in the run log);
  - 8 settings or held-out reads.
- **Split at 47e95647** (2026-10-29 16:28): 102 refusals in 93 sessions before, 21 in 66 after.
- **Harness blocks:** 75 `Blocked: sleep N followed by …`, 29 "requested permissions", 23 `rm` approvals.
- **`permission_denials` in the lead logs:** 218 in 110 logs (`rm` 55, `python3` 39, `git` 16, `mkdir` 15).

**E5. Brief gaps.** `gaps.py` parses the `brief_gaps:` lines (the `|`-separated form) in `.gov-runtime/scratch/orchestrator/log/W2-*.json`:
- 173 returns; 83 with the section; **511 lines; 7,424 stated minutes**. A1 found 533 and 7,669 with a looser parse.
- By place: common brief 256 lines / 4,068 min; ticket part 180 / 1,902; tool 51 / 1,133; skill 9 / 103.
- Kinds: keyword classes, first match wins (see R2-13). The classes are mine: an estimate of kind, not of minutes.
- Recurring gaps (lines / distinct returns):
  - `gov check` slow or timing out: 31 / 26;
  - serial list GIVEN or phase: 18 / 14;
  - `rm` or approval prompts: 17 / 16;
  - the 2-hour limit: 16 / 16;
  - load wait: 15 / 14;
  - a stale JUDGEMENT.md or brief in the worktree: 10 / 10;
  - the claim not committed, so `gov launch` refuses: 7 / 7;
  - STORE_MISSING: 7 / 7.

**E6. Work mix.** Lead calls by purpose (a regex over Bash commands, est.):
- reading and inspecting: 31.3 %;
- wait or poll: 27.0 % (strict `until`/`sleep` only: 24.5 %);
- ceremony: 11.6 %;
- Write: 8.8 %;
- git: 4.7 %;
- Read: 4.7 %;
- Edit: 4.3 %;
- test or verify runs: 4.0 %;
- worker launches: 2.6 %.

Writes and edits by target:
- helper scripts: 692 written, 77 edited;
- CHECKPOINT.md: 283 writes and 431 edits;
- worker briefs: 399 written, 217 edited;
- probe records: 44.

Cost per call: A1's median context of 141,723 tokens and its fitted cache-read price of about $0.20/M (both estimates).

## Notes for the combiner (outside R2)
- The kernel `brief-lead.md` contradicts the project's background-run rule (R2-11). That is a product defect for adopters: K-1 or CIT-P.
- `.git/config.lock` contention from parallel `git worktree add/remove` caused several of the "wrong path" errors and two gap lines: a dispatcher or queue matter.
- `JUDGEMENT.md` and the brief in a ticket worktree go stale against `w2/integrate`: 10 returns. The builder reads the main tree, but leads open the worktree's copy.

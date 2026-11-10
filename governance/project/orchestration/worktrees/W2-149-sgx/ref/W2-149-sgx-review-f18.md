- **sandbox_check:** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-149` failed with `OSError: [Errno 30] Read-only file system`, as required; (b) `git hash-object -w --stdin` worked (`1ae28402a109c3397a44b19239a00adfa9472eb0`) and so did `git update-index --refresh`.
- **ps_check:** I ran `ps -eo pid,args` on its own (no pipe, DEC-1080). It shows only my shell and `ps`: no ollama or llama-server process of mine.
- **task:** DAEO-52ku (W2-149): the narrow, independent, read-only review of the fixes for the wiring review's F18–F23 (S25 and S27 changed; S29, S30, S31 new; DEC-1112 (3)), on `w2/W2-149-sgx` from `944f39165` to the head `d388da2f2`.
- **status:** DONE
- **work_completed:** Read: the first review's F18–F23; the ticket's S25, S27 and S29–S31 and its last note; JUDGEMENT.md; the labeller, labeller-2 and overlap-auditor briefs; the five set-up A result schemas. Read the launch script's whole diff, and each changed function in place, including `main`'s fail-closed path. Read the designer's 51 new and 6 revised cases, the helpers and the README's F18–F23 interface; the engineer's unit tests and the evidence's F18–F23 section. Ran two probes in memory and one collect-only count.
- **files_changed:** none in any tree. `git status --porcelain` was empty at the start and is empty now; HEAD is `d388da2f22585eaabfe69af35a190852c77d1af9` both times. Nothing of mine was written to the scratch folder either.
- **evidence:** The script's sha256 at the head is `95fe78dd…aade5f1d0`, the same as the evidence's. The range touches only the script, the two unit files, the evidence and `tests/acceptance/W2-149/**`; the template's two files and the schemas are unchanged. The designer's commit stays in the acceptance folder; the engineer's stay in `allowed_paths`. Collect-only: 200 acceptance cases (3 of them live) and 72 + 83 = 155 unit cases. Probe 1 (F36): see the finding. Probe 2: a 400 kB nested-array rule output (under the cap) raises `RecursionError`, which falls through to the fail-closed path. Scratch at the end: `du -sh` 20K, `du -s --inodes` 8, all the harness's own entries.
- **tests:** I ran no test case: the role says to re-run nothing the lead ran. I accepted the lead's outside run at `d388da2f2` (289 passed, 0 failed, every `bwrap` case included; 3 live passed), the engineer's sandbox runs (`gov accept` 165 passed, 0 failed, 35 skipped; unit 152 passed, 3 skipped) and the designer's red record (32 red in the sandbox, 21 more `bwrap` red outside). The one `--collect-only -qq` went through the heavy slot (`-p no:cacheprovider --optin=lifted --optin=breadth`, empty scratch HOME, no bytecode). It ran no case, so it carried no `-m`/`-k` exclusion; it counted `test_s6_two_real_builds_draw_different_63_bit_seeds` without running it.
- **discoveries:** The designer's counts reconcile: 51 new; 9 + 23 = 32 `bwrap` cases; 21 of the 23 newly `bwrap` were red before the build. The lead's 289 does not reconcile (see unresolved). README note N-6 is right: in a real run the half does not change between rounds, so round 2's 18 is a second guard. My own slip: one read-only `git show --stat` line named the three reviewed commits (no range, but more than one `git diff` needs).
- **risks:** If F36 stays as it is, the auditor sees one consistent "default" side in the disputes that involve a script label. A labeller-1 round 1 rejected by the check has to be rerun blind: the labeller cannot run its script, and with F37 the log does not say why. For the held-out half, the rejected script stays in the walls folder's tar.
- **lessons:** The Write tool to my sandbox TMPDIR was not granted (the same happened to the previous reviewer). I did not retry it. Instead I ran the probes in memory with `python3 -B -c`, which writes no file and no bytecode; I name that form here as the common rules require.
- **proposed_decisions:** For the CTO. F36: either (a) accept it as a known limit and name it in the install ACT's package — my recommendation, confidence medium, because nothing the auditor may read describes the first labeller's script — or (b) blank every dispute's reasons. F37: a row, or a one-line log change (`rejected rules <word>`) if the script changes again before the ACT.
- **unresolved:** The lead's outside count, 289 passed, is 63 short of the 352 non-live cases the three targets collect (197 acceptance + 155 unit). The sandbox runs cover the 317 non-`bwrap` cases (165 + 152). The record should say whether all 35 `bwrap` cases (32 acceptance + 3 unit) were among the 289, and what the other 63 were.
- **recommended_next_action:** READY by `verdict.py`: no finding is in scope, ordinary work and fails open or loses work. No round (DEC-1010); merge in one command. The CTO rules on F36 before ACT-W2-149-INSTALL-1 is rebuilt; F37 is a row. Reconcile the lead's count in the merge note.

---

**Identity:** HEAD is `d388da2f2` on `w2/W2-149-sgx`; the tree was clean at the start and is clean at the end.
**task:** DAEO-52ku
**decisions:** DEC-1112 (3), DEC-1113 (2), DEC-1099 (1) Q5, DEC-1101 (2)-(3), DEC-1010, DEC-801, DEC-802, DEC-808, DEC-1014, DEC-1073, DEC-1080, DEC-1092 (1). I found no superseded or PROPOSED rule in use.

## Checks 1–5

**1. Each fix does what its line says, and only that.** Yes, all six, read in the code path.
- **F18, the round-1 check (S25):**
  - At labeller 1's round-1 delivery the launcher reads both out/ files once and checks both destinations.
  - It then runs the session's `label_rules.py` through the same confined check over the half's staged lines.
  - Any refusal or OS error there gives `rejected`, 20, before anything is written. The same bytes then land.
  - The check's output is discarded. The check applies to labeller 1's round 1 only.
- **F19, a stopped result (S29), for every flow:**
  - The result check records the valid result's `stopped` word for every set-up A flow and round.
  - The delivery refuses 20 as its very first step, before any landing exists.
  - All five schemas require `stopped` (both round forms for the labellers), and their word lists sit inside the script's, so `out.stopped` always carries the word.
  - Memory flows are untouched. Writer 2's `not-sealed` is now 20; before, it was delivered.
- **F20, labeller 2's check (S30):**
  - The check refuses a repeated, missing or extra id, comparing against the same ids staged as `input/sample.jsonl`.
  - Each line must have exactly the six keys, a listed label, a valid class, clauses as a list of strings, `how` `hand` and a string reason. Otherwise 20, inside the all-or-nothing landing.
  - Delivered in the session's order, with the class as an integer.
- **F21, the reason blanking (S27):**
  - The blanking works on copies: when either side's reason is empty or missing, both become `""`.
  - The labels files and `owner.jsonl` keep the real reasons.
- **F22, the settled-line form (S27):**
  - A settled line becomes exactly `{id, label, rule_class (integer), clauses = basis, reason, how: audit}`. The reason is always `""`, because the brief requires it empty when the flag is `none`.
  - A flagged line is labeller 1's, unchanged, with `how: owner`.
  - The old bytes go to `history/` first.
- **F23, the `rule_class` forms (S31):**
  - Accepted: an integer from 1 to 14 (never a boolean), or a string matching `(?:[1-9]|1[0-4])` in full. The ranges are code points, so no other Unicode digits; a full match also refuses a trailing newline.
  - Accepted in all four places: the rule script's output, the hand labels, labeller 2's labels and the auditor's decisions.
  - Stored as an integer in `script-labels.jsonl` (a string line is re-serialised), `labels.jsonl`, `labels-2.jsonl`, the delivered decisions, the settled lines and `owner.jsonl`'s decision.
  - Refused: 18 at round 2, 20 everywhere else.

**2. Round 1's check is the same confinement as round 2's.** Nothing is weaker at round 1.
- Both rounds call the same helper with the same inputs: the staged lines as stdin, the same ids, the same HOME and the same protected list. The protected list is now computed once for every set-up A flow.
- So the `bwrap` command line, the binds, the prelude's limits and seccomp filter, the 20 s cap, the output cap, the empty environment and the group kill are all identical.
- Every failure is 20 with nothing landing:
  - every 18 word (program, python, bind, place, start, cap, exit, output) and any OS error become 20 before the first file is staged for landing;
  - anything else ends in `main`'s fail-closed path with stage 20: `rejected`, the wall packed. That covers a deeply nested output, whose `RecursionError` I reproduced in memory, and an interrupt.
- A missing `bwrap` gives 20; the case for it runs in the default run. A missing interpreter also gives 20.
- The only differences: the log word (F37), and each round re-reads the half's lines at its own build (N-6).

**3. Independence.**
- **Closed:**
  - the reason channel (F21);
  - key order: the same field order on both sides;
  - the `rule_class` form: integers on both sides;
  - the JSON spacing.
- **What remains:**
  - **(i) F36:** the script side's signature.
  - **(ii) The labellers' own wording:** their citation style in clauses, and in reasons when both sides keep them. The brief requires that content, so the launcher cannot change it.
- **Neither names a labeller from anything the auditor may read.** I searched the register for "rule script" and found nothing; per DEC-1092 (1) I searched once more in other words and read DEC-1099 (1) Q5 and DEC-1113. Neither describes the first labeller's script, the auditor's brief does not, and the labeller briefs are left out of its tree.
- The x/y map stays outside the wall.

**4. No regression.**
- **Memory flows:** the memory delivery, the result check's memory branch and every non-set-up-A line of the build are unchanged.
- **S1–S24, S26, S28:**
  - S20's sample bytes are identical, and S24 is unchanged.
  - S26's merge is identical for integer classes.
  - S28 is unchanged apart from recording `stopped`.
  - S16 changes only as S25 and S30 require.
- **Revised cases:**
  - S25's five round-2 scripts now misbehave only once the trigger line is in their input. The markers, listener, caps and assertions are the same, and a broken wall would still fail the case.
  - Two cases only gained the `bwrap` marker.
  - S16's labeller-2 case compares the parsed lines, and still checks the ids, the order and the overlap.
  - The two S27 cases now compare settled and flagged lines exactly, which is stronger than before.
  - The trailer `Rewrite-Reason: DEC-1112 (3) …` is present.
- **F26:** the test now listens on a port of its own (127.0.0.1:0), expects 18 and asserts that no connection arrived. No 11434 or 11435 is left in W2-149's tests.

**5. Failure lines.** None now passes where it should fail.
- Line 7 (a delivery from a stopped session) now holds under both readings for set-up A.
- Line 11 (a failure or partial output treated as a pass) now holds at round 1 too.
- Lines 2 and 8: the new 20s pack the wall.
- Line 6: the new log words (`rules`, `stopped`, `labels`) are fixed words, and `out.stopped` is a word from the schema's list.
- F24's override is still the only fail-open path, unchanged.

## Findings

**F36 — In the disputes F21 blanks, the script's side can still be picked out.**
- **What happens:**
  - S26's merge keeps the script's own label only for lines the script put in class 14, not uncertain and not sampled. It gives them an empty reason.
  - F21 blanks both reasons in exactly those disputes.
  - Labeller 2 gives each line a reason, and when it disagrees with an allow/14 line it gives refuse or ask with a class from 1 to 13.
  - So in nearly every dispute where both reasons are now empty, exactly one side is class 14 (with an ordinary script, also with no clause), and that side is labeller 1's.
  - My probe drove the script's own merge and dispute staging with 20 actions: every script-kept line was class 14 with an empty reason, and in all 15 both-blank disputes the class-14 side was labeller 1's.
- **What should happen:** the brief's "You do not know which labeller wrote which label" holds for these cases too, or the limit is named to the owner.
- Ordinary work: yes, because it arises by itself in every dispute over a script label; no agent has to do anything.
- Consequence: other. Nothing lands wrongly. S27's line ("no side is told apart by it", the reason) is met, and nothing the auditor may read lets it name a labeller.
- Scope: in (S27, F21's fix).
- **Options for the CTO:** (a) accept and tell the owner; (b) blank every dispute's reasons. Option (b) costs the auditor labeller 2's arguments, which its brief treats as arguments, not evidence.
- **Reverses if:** the CTO holds that the auditor cannot learn or infer what the first labeller's script lines look like. On F21's own premise that it can, the fix leaves the side readable in nearly every case it was meant to hide.

**F37 — A round-1 rejection loses the rule check's own reason word.**
- **What happens:**
  - When labeller 1's round-1 delivery fails its rule check, the run log says only `rejected rules`.
  - At round 2 the same failure logs its word, such as `refused 18 program` or `refused 18 cap`.
  - So at round 1 a missing `bwrap` or interpreter (an environment fault) looks the same as a script that crashed or ran past its cap (which needs a labeller rerun).
- **What should happen:** the round-1 log carries the same fixed word. Fixed words keep S13 and S28 intact.
- Ordinary work: yes, because a round-1 rejection is F18's own premise. The CTO must then choose between fixing the environment and paying for a rerun (30 USD, up to 3 h).
- Consequence: other.
- Scope: in (S25, F18's fix).
- **Reverses if:** the CTO's procedure for a round-1 rejection checks `bwrap` and `~/.local/bin/gov` by hand first anyway.

## Probed and found sound
- The bytes checked at round 1 are the bytes that land: they are read once, so nothing can be swapped in between.
- The stopped refusal comes before the round-1 rule check, as the README allows.
- The flow schemas' `stopped` words all fall inside the script's list.
- The class pattern refuses `"07"`, `" 7"`, `"+7"`, `"7\n"` and Unicode digits.
- A JSON line with a repeated key keeps the last value, which is then checked.
- The blanking never changes `labels.jsonl` or `owner.jsonl`.
- After F22, the old `labels.jsonl` is preserved in `history/`, and `owner.jsonl` keeps both labels in full.
- No product of a refused run is destroyed: it stays in the wall's tar.
- Each role wrote only within its own paths, and the engineer did not touch the acceptance tests.
- Labeller 2's check is stricter than labeller 1's hand-label check (extra keys refused here, ignored there). Both follow their interface.

## Classification
Two findings (F36, F37), both in scope, ordinary work yes, consequence other. None fails open or loses work, so nothing blocks. Recommendation: READY, no round. F36 is a CTO ruling before the install ACT; F37 is a row.

```verdict
{"kpis": [{"kpi": "S25", "verdict": "pass", "findings": [{"id": "F37", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S27", "verdict": "pass", "findings": [{"id": "F36", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S29", "verdict": "pass", "findings": []}, {"kpi": "S30", "verdict": "pass", "findings": []}, {"kpi": "S31", "verdict": "pass", "findings": []}]}
```
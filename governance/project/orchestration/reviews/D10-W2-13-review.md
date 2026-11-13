# D-10's red-fix list: the review of W2-13's latency cases routed by serial-only.txt (W2-13, DAEO-zqvn)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W2-13-review.md`; branch `w2/W2-13-d10-tests at 1d3cdeb1f`; reviewer log `/home/usain/gov-os-worktrees/W2-13-d10-tests/.gov-runtime/scratch/lead/log/D10-W2-13-review.json`.
- verdict.py: READY (no blocking finding).

I've reviewed the revision and the readers. Here is my record.

---

**sandbox_check:** passed. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-13` failed: OSError 30, read-only file system. (b) `echo sandbox-trial | git hash-object -w --stdin` wrote blob `1ae28402a109`, and `git update-index --refresh` exited 0.
**ps_check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing at the start or at the end. I started no model, embedder or reranker.

**task:** DAEO-zqvn (W2-13): D-10's review of the latency routes in `serial-only.txt`, revision `9ca161a6f..1d3cdeb1f`, HEAD `5452875d224b`.
**status:** DONE
**work_completed:**
- Checked identity: HEAD is `5452875d224b` and the tree was clean.
- Read the diff and the list's header, then the close's plugin and serial phase. Read both nightlies: the product's `gov.close.nightly` and the orchestrator's `nightly.sh`, `nightly_alone.py` and `nightly_cron.sh`.
- Read W2-13's test file, conftest, README, ticket and evidence row. Read W1-30's r11 reader, the root conftest's opt-in rule and `gov accept`'s runner. Read D10-REDS item 13 and the DEC-1112 (3) line.
- Ran W1-30's two reds at HEAD and at `9ca161a6f`, then again with the opt-ins. Ran two collect-only probes of the nightly's serial phase.

**files_changed:** none. `git status --porcelain` was empty at the end.
**evidence:** the runs are listed under "tests" below. My scratch folder was 97M and 4394 inodes before I removed it. The 9ca161a6f copy was a `git archive` extract inside it.
**tests:**
- At HEAD, the three W1-30 r11 cases: 2 failed and 1 passed (the format case).
- At `9ca161a6f`, the same three: the same 2 failed with identical messages, and 1 passed.
- At HEAD with `GOV_TESTS_OPTIN=lifted,breadth` in the environment, the two reds: 2 passed.
- Collect-only of the nightly's serial phase given only the ui_off entry: exit 4, "no case is named by the entry … test_w1_16_ui_off.py". The same with both opt-ins: 9 cases collected.
- Exclusion: I ran named cases only, never a whole folder, so the `-m/-k` exclusion did not apply. No real-model case was run.

**discoveries:**
- F1: the nightly's serial phase stops before running anything, and the night can still read green.
- No nightly has run since 11-02.
- `gov accept W2-13` still runs the real-model case.
- W2-13's evidence row for S3 still says pass.

**risks:** once the nightly resumes, every case routed to it (W1-19's, W1-21's and W2-54's real-model cases, the live-session cases, both W2-13 cases) runs nowhere, and the night can still report green (F1).
**lessons:** a route is only as visible as the run it sends the case to. W1-30's "an entry that names nothing" check is only green when the opt-ins are named, and the nightly runs without them.
**proposed_decisions:** none of my own. The options for F1 are under the recommendation below.
**unresolved:**
- I did not run the full nightly serial phase over all entries: the Write tool's permission for a probe script wasn't granted. One empty entry is enough to stop the run, by the plugin's own rule.
- I did not run the real-model case (sandbox rule).

**recommended_next_action:**
- Merge per the computed verdict.
- Fix F1 before the nightly resumes.
- File the latency on W2-13's ticket and its evidence row (F3).
- Hand F2 to W2-115 and F4 to the nightly's owner as rows.

**decisions:** DEC-889 item 5 and DEC-1112 (3), both ACCEPTED, are the rules this revision rests on. Also relevant: DEC-372, DEC-1052 Q-10, DEC-1061, DEC-549, DEC-852 item 3, DEC-933, DEC-1083, DEC-1109, DEC-801, DEC-808, DEC-1010, DEC-1014. I found no superseded or PROPOSED rule in use.

## Answers to the checks

**1. Are the routes the file's rules? Yes, and neither loosens the limit.**
- **Real-model case → `nightly: real-model`.** It rebuilds the dev tiers with the real embedder and times each question through the embedder and the reranker. The header says a real-model case goes to the nightly.
  - It is also a latency case. Where a case is both, the list's precedent is the real-model route: W1-19's real-model file ("one case is a warm p95", line 101) and W2-54's time-limit case (line 107).
  - W1-30's kind table agrees, and its format case passes with both new entries.
- **Lexical case → `serial: latency`.** It asserts a time bound and starts no model, which is what the header's latency kind means.
  - Before this revision it was on no line, so it ran in the close's parallel phase, against its own docstring ("run this file alone", DEC-372).
- **No loosening.**
  - The budget is still `WARM_P95_LIMIT_S = 0.5` (`w2_13_support.py:89`), and from base to HEAD only README lines changed in W2-13's folder.
  - The instruction (DEC-1112 (3), `DECISIONS-IN-FORCE.md:430-431`) allows "the existing load-sensitive route or the nightly, never a looser 0.5 s limit". The load-sensitive list is frozen (DEC-1052 Q-10), so the nightly is the one route left.
  - The lexical case still runs in every full close and in every scoped close that selects W2-13.
- **Both entries name cases that collect.** W1-30's "every entry names cases" check names only the ui_off entry as empty. Both new entries name single functions, with no whole-file entry and no duplicate.

**2. Does the red stay visible? Partly. Today the nightly would not show it (F1), and no nightly has run since 11-02.** A reader sees it now in four places:
- the reason on `serial-only.txt:109`;
- W2-13's `README.md:74-76`;
- D-10's package, `D10-REDS.md:189-191` (item 13);
- `gov accept W2-13`, which runs the whole acceptance folder with no route plugin and no marker filter (`src/gov/accept/runner.py:335`). There S3's real-model case runs and goes red where Ollama and the reranker are up. It skips where they aren't.

In the nightly it would show as a `red-alone` line in `run.txt`, a red verdict and a P1 ping. That needs F1 fixed, the nightly running again, and Ollama and the reranker up at 04:00; otherwise the case is a skip. It is not filed in W2-13's own records either (F3).

**3. The two W1-30 reds are older, not this revision's.**
- At `9ca161a6f` the same two cases fail with identical messages: W1-16's counts "6 … 36 … I3 F7 counts 94 and 67", and the ui_off entry naming no case. HEAD is identical.
- The cause is how the reader is run. These cases ask a fresh pytest to collect, and it inherits the environment but not the outer run's `--optin` options. Without the opt-ins, the lifted and breadth cases are dropped.
- With `GOV_TESTS_OPTIN=lifted,breadth` in the environment, both pass at HEAD. W1-30's r11 file is itself on the `lifted` list (`optin-lifted.txt:76`, home W2-115). This is F2, a row.

**4. Trailers are right.**
- `1d3cdeb1f` carries `Task: DAEO-zqvn`, `Implements: DEC-1109, DEC-889`, `Role: independent-test-designer`, the brief's exact `Rewrite-Reason` and `Co-Authored-By`.
- Only `tests/acceptance/serial-only.txt` (+2) and `tests/acceptance/W2-13/README.md` (+3) changed. The test file and budget are untouched.
- The later merge `5452875d2` (Task DAEO-sdxk) touches neither file nor W2-13's folder.

**Probed and found sound:**
- Both entries say their route, kind and reason in words.
- Each entry takes only its own function, not a function whose name merely begins the same way.
- The close reads the route line by line: the real-model entry goes to the nightly, the lexical one stays serial.
- The lexical entry is on no opt-in list, so it can't add a new "names nothing" stop.
- The README bullet sits above the KPI map, holds no test id, and the S3 row still names both cases.

## Findings

**F1 — The nightly's serial phase stops before running any case, and the night can still read green.**
- **What happens:**
  - `nightly.sh` hands its serial phase every entry of the list and names no opt-in suite. Neither it nor `nightly_cron.sh`, which exports only HOME, LANG and PATH, sets one.
  - Since D-4's cut, all of W1-16's ui_off cases are in the `breadth` suite (`optin-lifted-breadth.txt:274-280` on integrate). The run drops them, so the ui_off entry (`serial-only.txt:84`) names no case, and the close's plugin stops the whole phase at collection with exit 4.
  - Nothing in the serial phase runs, including both W2-13 cases. The lexical case ran in the nightly's parallel phase before this revision; it is now in the serial phase.
  - The nightly's verdict counts only failing cases in its JUnit files, not the serial phase's exit code. So the night can read "verdict: green", send no ping and delete its clone.
  - In a full, unscoped close, the same stop is reported as a finding and refuses the close, so the close fails closed.
- **What should happen:** the serial phase runs every entry, and a serial phase that ends without running counts as red.
- **Evidence:**
  - My collect-only of that form with the ui_off entry alone stopped with exit 4; with the opt-ins it collected 9 cases.
  - The plugin stops on any one empty entry (`gov_close_serial_only.py:54-60`).
  - The nightly's log folder has no run after 11-02; the digest's last line is 2026-11-02 09:24.
- **Reversed by:** the nightly's serial phase over all entries, without opt-ins, collecting with no usage error; or an opt-in found in the nightly's environment.
- **Decisions:** DEC-889 item 5, DEC-1061, DEC-549, DEC-852 item 3, DEC-933.
- Ordinary work: yes, because the 04:00 nightly runs exactly this form.
- Consequence: fails open
- Scope: out. It predates this revision and doesn't depend on it, but it is why "it runs in the nightly" does not hold today.

**F2 — W1-30's r11 reader goes red when the opt-ins are named on the command line.**
- **What happens:** two of its cases, W1-16's counts and the ui_off entry, go red because their inner collection doesn't see the outer run's `--optin`. They are green with `GOV_TESTS_OPTIN` set in the environment.
- **What should happen:** the cases should get the opt-ins however the run names them, or say they need the environment variable.
- **Evidence:** identical failures at `9ca161a6f` and at HEAD; 2 passed with the variable set.
- **Reversed by:** the two cases red at HEAD with the variable set.
- **Decisions:** DEC-1061.
- Ordinary work: yes, because the designer's brief said "with both opt-ins" and the option is the natural way to give them.
- Consequence: other (a false red; nothing passes that should fail).
- Scope: out. It is red without this revision. Home: W2-115.

**F3 — "Filed against W2-13" points at nothing in W2-13's own records.**
- **What happens:**
  - The ticket's last note (D9-FATES, DEC-1083) reads "lines met: all 8", and S3's latency is one of those lines.
  - The S3 evidence row (`docs/changes/W2-13-evidence.md:31`) still says pass: 2 of 2 alone at load 1.1.
  - Only the list's comment, the README and D10-REDS item 13 record the 11-10 red of 0.543 to 0.578 s.
  - The designer could write only the two files, so filing it is the CTO's step.
- **What should happen:** a line on the ticket and on the evidence row recording the red and its route.
- **Reversed by:** a ticket, evidence, register or decided-not-done row that records it.
- **Decisions:** DEC-1083, DEC-1112 (3).
- Ordinary work: yes, because the lift reads the ticket's "all 8".
- Consequence: other (a record gap; `gov accept W2-13` still runs the case and fails it where the models are up).
- Scope: out. The fix is outside the revision's two files.

**F4 — The product's own nightly never runs a case routed to the nightly.**
- **What happens:**
  - `python3 -m gov.close.nightly` runs the close's own runs (`nightly.py:347`). Those leave routed entries out of the parallel phase and drop them from the serial phase (`command.py:920`).
  - The list's header promises every entry runs in the nightly. Only `nightly.sh`, and W2-57's own test-local simulation (`w2_57_list_support.py:165-181`), actually do that.
  - This project runs `nightly.sh`; the main tree has no product nightly records.
- **What should happen:** the product nightly runs every listed entry alone after its parallel run.
- **Evidence:** read only, not run (it would need a full regression).
- **Reversed by:** a product nightly record that lists a routed case as run.
- **Decisions:** DEC-889 item 5, DEC-852 item 3.
- Ordinary work: yes, because that is the product's documented nightly command.
- Consequence: fails open
- Scope: out. Owners: W2-66 and W2-57; a row.

**Classification:** 0 findings in scope. 4 out of scope: F1 (yes, fails open), F2 (yes, other), F3 (yes, other), F4 (yes, fails open). None blocks.

**Recommendation:**
- The revision is correct and READY.
- Until F1 is fixed, don't count the nightly as the place this red is seen. Today that place is `gov accept W2-13` plus the three documents above.
- For F1, make a serial phase that runs nothing count as red in the nightly's verdict. Then either:
  - keep the cases the serial run is given, the way cases named by function on the command line are already kept; or
  - have `nightly.sh` name both opt-ins for its serial phase.
- My preference is the verdict fix plus keeping the given cases. Confidence: medium.

```verdict
{"kpis": [{"kpi": "w2-13-latency-route", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```

# D-10 gate: the review of serial-only.txt's W1-16 ui_off entry taken out (W2-13, DAEO-zqvn)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-serial-only-1a-review.md`; branch `w2/W2-13-d10b-tests` at `6afff5d74`; reviewer log `/home/usain/gov-os-worktrees/W2-13-d10b-tests/.gov-runtime/scratch/lead/log/D10-serial-only-1a-review.json`.
- verdict.py: READY (no blocking finding).

Approve. The change fixes the stop, and nothing in it fails open or loses work. It does cause one new red that nobody has named yet (F1).

**sandbox_check:** passed. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-13` failed with OSError 30 (read-only file system). (b) `echo sandbox-trial | git hash-object -w --stdin` wrote blob `1ae28402a109`, and `git update-index --refresh` exited 0.
**ps_check:** at the end, `ps -eo pid,args --no-headers -C ollama,llama-server` showed only my own shell and `ps` (the sandbox sees only its own processes). No ollama or llama-server process is mine. I started no model, embedder or reranker.

**task:** DAEO-zqvn (W2-13): D-10's gate review of `6afff5d74` (parent `af850b6f2`), which comments out serial-only.txt's W1-16 ui_off entry. HEAD is `4e63a8adc`.
**status:** DONE
**work_completed:**
- Checked identity: HEAD is `4e63a8adc` and the tree is clean.
- The later merge `4e63a8adc` touched none of the files I reviewed: serial-only.txt, the plugin and close code, `tests/conftest.py`, the opt-in lists, W1-16 and W1-30.
- Read the diff, the plugin (`gov_close_serial_only.py`), the close's serial phase (`command.py:886-924`, `serial.py`), and the root conftest's opt-in rule (`tests/conftest.py:286-317`).
- Read all four opt-in lists against all 66 entries, plus W1-30's r11 reader, the ui_off test file and W1-16's README.
- Read D10-REDS item 1 (the serial-phase stop), DECISIONS-IN-FORCE:437-439, the earlier D-10 review and the register entries.
- Ran one reproduction of F1.

**files_changed:** none. `git status --porcelain` is empty.
**evidence:** my scratch folder was 24K and 7 inodes before I removed it. I opened nothing under `~/gov-os-eval/` or `~/gov-os-runs/`.
**tests:**
- One run through `heavy_slot.sh` (it waited for a slot, then ran) at HEAD, with `GOV_TESTS_OPTIN=lifted,breadth`, an empty HOME and `PYTHONDONTWRITEBYTECODE=1`. It ran two W1-30 r11 cases by node id: 1 failed, 1 passed, in 1.75 s.
  - The failure is F1.
  - The pass is `test_every_entry_names_cases_that_exist`.
- The `-m/-k` exclusion was not applied, because I ran named cases, not a folder. Both cases only collect, so no W1-16 case and no real-model case ran.
**discoveries:** F1 (a new W1-30 red in runs opted in through the environment); the designer's eighth node-id entry is a nightly-route one; F3 (node-id entries also *run* in a default close).
**risks:** until fix (b), the nine ui_off daemon cases run in the parallel phase of any close that has breadth in `GOV_TESTS_OPTIN`. The contention risk is low (check 2), and a failure there would show as a red, not a false green.
**lessons:** taking an entry out of the list changes its cases' route. W1-30's r11 is the reader that enforces routes, so check it in the opted-in form as well as the default one.
**proposed_decisions:** none.
**unresolved:**
- I did not re-run the designer's collect-only of the close's serial phase. I checked it statically instead (check 1).
- I did not run the ui_off cases in parallel to measure contention.
- I did not run F1's case at the parent commit. Two things support the "before" state: the count assertion just above it passed at HEAD, so only the nine ui_off ids fail; and the earlier review found the case green with the same variable.
**recommended_next_action:**
- Merge per the computed verdict.
- Record F1 in D10-REDS (and on W2-115's row for W1-30) as the expected cost of (a), cleared when (b) brings the line back, so nobody "fixes" W1-30.
- F2's wording can ride along with (b) (DEC-802).
- Hand F3 to (b)'s engineer as a design input.

**decisions:** DEC-1112 (3), DEC-1061 and DEC-1109 are all ACCEPTED (checked in the register); DEC-1112 and DEC-1109 have item (3) standing. Also relevant: DEC-889 item 5 and DEC-549 (status not checked), and DEC-801, DEC-808, DEC-1010, DEC-1014. I found no superseded or PROPOSED rule in use.

## Answers to the checks

**1. Fixes the stop: yes.**
- In a default run the close's serial phase gets the 48 serial-route entries; `serial.phase` drops the 18 nightly ones.
- The 44 `file::function` entries go on the command line by node id, from the project root (`command.py:922`, `:999`). The root conftest keeps any case named that way, whatever an opt-in list says (`tests/conftest.py:298-306`).
- The 4 whole-file entries each still have cases in a default run:
  - W1-20's code file, W2-57's designer-read p95 file and W1-16's one-daemon file are on no opt-in list.
  - W1-16's secret-exclusion file has 5 of its 11 functions in breadth (`optin-lifted-breadth.txt:269-273`), which leaves 6.
- No other form of empty entry:
  - No conftest and no serial-route or nightly-route folder skips at module level or ignores files at collection.
  - The skips that depend on the machine (the tool, gitleaks, namespaces) are fixture skips, so the cases are still collected.
  - The scoped close adds only pytest-timeout options, with no `-m` or `-k` (`command.py:1370`).
- This agrees with the designer's collect-only result (exit 4 before, 0 after). "90 of 96" fits the 6 secret-exclusion breadth cases being dropped; I inferred that, I didn't run it.
- **The eight entries:** the reasoning is right. 7 are serial-route:
  - W2-69 ×2 (the lifted folder);
  - W1-15's scan bound (lifted file);
  - W1-16 token_rule ×2 and builtin_allowlist ×1 (lifted files);
  - W1-09's review race (breadth cap).
- The eighth is nightly-route: W1-50's freeze_live_pause case, whose whole file is on `optin-lifted-guard.txt:150`. The close never gives it to the serial phase.

**2. No fail-open.**
- **Named:** yes, in the comment itself and in the CTO's delegated line (`DECISIONS-IN-FORCE.md:437-439`, which names (b)). I did not look for (b)'s ticket.
- **Bounded:**
  - The close can only get an opt-in from `GOV_TESTS_OPTIN`. It strips `PYTEST_ADDOPTS`, and `command.py` has no opt-in option.
  - A default close and `nightly.sh` never collect the ui_off cases.
  - The file runs every command that can start the daemon in a user and network namespace of its own, so the UI port 9749 belongs to that command alone (`test_w1_16_ui_off.py:14-16`). Each case also builds its own repository.
  - What's left is CPU load. The likely failure under load is a timeout. A false "UI off" pass would need all three signs to miss at once, including the daemon log and the home's setting, which are read after the fact.
- **What depends on the entry:**
  - W1-30's r11 daemon-serial case (F1).
  - Nothing else. The plugin, `serial.py`, `select.py`, the product nightly and the orchestrator's nightly tools read entries generically. W2-57's and W2-66's tests use planted lists. Elsewhere ui_off is mentioned only in prose.

**3. Trailers: right.**
- Task DAEO-zqvn, Implements DEC-1109 and DEC-1112, Role independent-test-designer, a Rewrite-Reason that cites DEC-1112 (3) and DEC-1061, and the Co-Authored-By line are all present.
- Only `tests/acceptance/serial-only.txt` changed (+5, −1).

**Probed and found sound:**
- The edit is in the file's own style. Every added line starts with `#`, so `entries()`, `serial.nightly()` and W1-30's reader see no entry.
- The old line is kept, and no other entry names the file.
- The comment gives the reason, the decision and the condition for the line to come back.

## Findings

**F1: W1-30's r11 check goes red with both opt-ins in the environment, and the revision doesn't say so.**
- **What happens:** with `GOV_TESTS_OPTIN=lifted,breadth`, `test_w1_16_s_daemon_cases_stay_serial_and_its_cases_that_start_no_daemon_are_not_declared` fails. It names exactly ui_off's nine cases as "not declared serial". The count assertion just before it (94 and 67) passes.
  - This is a true red: the check is reporting the route change that (a) makes.
  - W1-30's r11 file is itself on the lifted list, so it runs only in opted-in runs, including D-10's report-only runs.
- **What should have happened:** the commit, or D10-REDS, names this as an expected red of (a), cleared by (b).
- **Evidence:** my run above: 1 failed, 1 passed.
- **Reversed by:** the same case passing at HEAD with the same variable, or a record that already names this red.
- **Decisions:** DEC-889 item 5, DEC-1061, DEC-1112 (3).
- Ordinary work: yes, because a lifted run with breadth in the environment is the standard way to run these cases in D-10's window.
- Consequence: other (a red that fails closed; nothing passes that should fail).
- Scope: in.

**F2: the new comment and the section header are imprecise.**
- **What happens:**
  - The comment says "its seven cases"; the file has seven functions but nine cases.
  - It says "a run with --optin=breadth"; the close gets breadth only through `GOV_TESTS_OPTIN`.
  - The daemon section's header (line 48) still says "W1-16's 67 cases", but 58 are listed now.
- **What should have happened:** the comment says nine cases and names the environment variable, and the header gives 58 or notes the exception.
- **Reversed by:** a breadth collect-only of the file that shows 7 cases, or the close accepting `--optin` from its caller.
- **Decisions:** DEC-1112 (3), DEC-1061.
- Ordinary work: yes, because whoever restores the line under (b) checks the restore against these numbers.
- Consequence: other.
- Scope: in.

**F3 (existed before this revision): a default close's serial phase runs the opted-out cases that are named by node id.**
- **What happens:** because the close passes entries on the command line, the conftest's node-id rule makes the default close *run* the seven serial-route node-id entries' cases that D-4's cut opted out. Six are lifted cases, which should be report-only; one is breadth.
- **What should have happened:** (b) decides whether these are "in this run", the same way for whole-file entries and node-id entries.
- **Reversed by:** a default close's serial-phase log that shows those cases deselected.
- **Decisions:** DEC-1061, DEC-549.
- Ordinary work: yes, because every default close does this.
- Consequence: other (more is run and blocks the close, not less).
- Scope: out. It goes to (b) and W2-57's code.

**Classification:** 2 findings in scope, F1 and F2 (both ordinary work yes, consequence other); 1 out of scope, F3 (yes, other). None blocks.

**Recommendation:** READY; merge, record F1 as expected, and let F2 and F3 ride with (b). Confidence: high.

```verdict
{"kpis": [{"kpi": "serial-only-ui-off", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```

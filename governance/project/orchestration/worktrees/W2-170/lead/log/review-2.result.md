```
task: Review 2 (the last) of W2-170 (DAEO-61vm): a fresh, read-only FULL probe of head 6ba5a6edab5b against S1-S6, F1-F5 and Interface sections 1-10, above all the fix of round 1's RV1
status: DONE. RV1 is fixed in the cycle's real order, and no finding blocks: none is in scope, reachable in ordinary work and fails open or loses work. Two new rows: one yes/other, one no
work_completed: Read the ticket (Interface section 10, readings 1-9), the package's section 3.3, round 1's record, the source and evidence changes since ad664fc87755, preflight.run, declare.py, layout.py, and the acceptance world helpers and batch-2 case list. Ran 4 probe processes (1 template build plus 3 probe runs) on 21 planted worlds under TMPDIR, all removed afterwards
files_changed: none
evidence: Step 0: (a) the write to the worktrees folder FAILED ("Read-only file system"); (b) `echo sandbox-trial | git hash-object -w --stdin` returned 1ae28402a109, and `git update-index --refresh` worked (an earlier form of the same check also wrote the empty blob e69de29bb2d1 into the shared object store); GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-61vm. Head at start 6ba5a6edab5b and at end 6ba5a6edab5b. gov.__file__ = /home/usain/gov-os-worktrees/W2-170/src/gov/__init__.py. Session id: probably 4beddb85-559a (from the sandbox's task path). TMPDIR at end: 20K, 8 inodes (du -sh, du -s --inodes); every planted world was removed. Read refusals met: 0. One Write-tool refusal, for a probe script under TMPDIR: not retried and not worked around; the probes ran as inline `python3 -c` commands instead (as in round 1). `git status --porcelain` is empty at the end. The engineer's commit 6ba5a6eda carries Task: DAEO-61vm and Role: engineer, and touches only common.py, declare.py, preflight.py, two unit test files and the evidence file.
tests: none run (the lead's unit 84, acceptance 179, lead_verify and gov accept were not repeated); 3 probe processes on planted roots only
discoveries: (RV6) If a subsystem sits at its cap, a round-2 rewrite plus a drop elsewhere ends in a dead end: re-pre-flighting after void is refused with PF-SPREAD, which void itself tolerates. Pre-flighting before void avoids it. (RV7) A set pre-flighted at the audit commit can be declared at a different commit when the store is at that commit.
risks: The fix makes "pre-flight again after writer round 2" a step the cycle must take. Its place matters: before void it always works for a clean set; after void it can dead-end (RV6). Nothing in W2-170 states where that step goes.
lessons: Probe the re-pre-flight in both places, before void and after it: the second pre-flight checks the kept set as a fresh delivery at the kept count, whereas void tolerates a subsystem over its scaled cap.
proposed_decisions: Add to PKG-W2-170-TD2-1 (the CTO's, about the missing way back after void): W2-172's cycle runs the pre-flight after every writer round, before void, as an entry criterion of W2-172 (DEC-803's pattern). That closes RV6, and in practice TD2-1's case too. Recommend, confidence high. RV7: a Wave 3 row, or one line in W2-172's entry criteria ("one resolved audit commit is passed to every subcommand"). Recommend the entry-criterion line, confidence medium.
unresolved: PKG-W2-170-TD2-1 is still the CTO's. I agree it fails closed. After void, a fixed file would need the checker's judgement again anyway, so refusing is defensible; what is missing is a stated way back, for example a new audit name.
recommended_next_action: READY on RV1's fix; the CTO folds RV6 and RV7 into W2-172's entry criteria with PKG-W2-170-TD2-1, and nothing in W2-170 needs another round
```

task: DAEO-61vm
decisions: DEC-1101 (1), DEC-1125 (2), DEC-1052, DEC-801, DEC-803, DEC-808, DEC-1010, DEC-1014, DEC-1131, DEC-1133
probed_commit: 6ba5a6edab5b32285c619721bbaaee5535575620

## Scope
- **In scope:** KPI lines S1-S6 and F1-F5, Interface sections 1-10 with section 10's reading 9, and the fix of RV1.
- **Out of scope:** the measure (W2-171), the cycle and schedule (W2-172), the launch script's follow-ups (W2-173), and the files the `w2/integrate` merges brought in.

## Method
- I built one template world with `w2_170_world.build` under TMPDIR, with an empty HOME, every root flag explicit and this tree's `src/` first on PYTHONPATH. Each case ran in a copy of it.
- Writer round 2 was modelled as the launch script delivers it: `hidden/` replaced whole, `selection.json` kept, then the checker's notes in `XCHECK-r2.md`.
- I compared the sets root before and after each `declare` (bytes and mtime of every file). A direct pre-flight afterwards showed what the checks would have said.
- The cases ran in three processes:
  - **A1-A12:** round-2 defects after a clean pre-flight.
  - **B1-B2 and C1-C3:** the re-pre-flight placed before void and after void, plus a subsystem at its cap.
  - **D1-D2, E1, F1:** a record from before the fix, a record missing one id, a mismatch between the commit used to pre-flight and the one used to declare, and S5 on the new record.

## Probed and found sound
1. **RV1's fix, in the cycle's real order.** Each case: pre-flight clean, round-2 replacement, notes accepting all, then void (exit 0).
   - **Refused, nothing written:** `declare` exited 1 with `DC-PREFLIGHT` for:
     - each defect a check catches: wrong commit, missing source, a source under an evaluation namespace, a dropped key, a category moved (quota), a draw outside its list, a nonexistent id that does exist;
     - a reword that still passes every check (A8);
     - a new id, q41 in place of q05 (A9);
     - a comment appended after void (A12, which also gets `DC-DROPS`).

     In every case the sets root was unchanged: no map entry, no `DECLARATION.json`, no ledger line, no `USED`. The ledger read `preflight, drop` only.
   - **Declared, correctly:** a removed id (39 delivered, all byte-equal to pre-flighted files) was declared with n 39. A file replaced and then dropped (A11) was declared with n 39, because `dropped/` is not compared.
   - **Re-pre-flight lets the cycle go on:**
     - before void (B1): ledger `preflight, preflight, drop, declaration, used`, `DECLARATION.json`'s mtime earlier than `USED`'s, set digest equal to the shell's, n 37;
     - after void (B2): `DC-PREFLIGHT`, then the re-pre-flight, then declared and `USED`.
2. **What the fix could have broken:**
   - **S3 flow:** order of the five writes, file times and ledger are all as stated (B1).
   - **void and exit codes:** `drops.py` was not touched; refused 1, void 2, used 3, as before.
   - **A `PREFLIGHT.json` from before the fix** (no record; D1) is refused with nothing written. A record missing one id (D2) is refused.
   - **S5/F1:** the record's keys are the 40 `q<nn>` ids and its values are 64-hex digests equal to the files' sha256. S5's unique words appear in no run-folder file and in no stdout or stderr of the three subcommands. No folder word is printed.
3. **False refusals the fix adds:** none in the honest single-pass flow (C3), nor when the pre-flight runs again before void (C2). The one case found is RV6, after void.
4. **F5:** `git diff --name-only w2/integrate...6ba5a6edab5b` lists only `src/gov/memaudit/**`, `tests/unit/memaudit/**`, `governance/project/test-map.yaml`, `docs/changes/W2-170-evidence.md` and the designer's `tests/acceptance/W2-170/**`.
5. **Other:** round 1's rows RV2-RV5 rest on code the fix did not touch and stand unchanged as rows. The engineer's readings P1-P5 stand.

## Findings

**RV6: a re-pre-flight after void can dead-end when a subsystem sits at its cap** (scope: in, S1/S3 through reading 9)
- **What was done:** a clean 40 with retrieval at 10 (allowed at 40) was pre-flighted clean. Round 2 reworded q12 (still valid). The round-2 notes rejected q36. Then void ran (kept 39, `subsystem_over: [retrieval]`, exit 0) and declare (`DC-PREFLIGHT`, as reading 9 intends). Then the pre-flight was run again, where the refusal is reported, after void.
- **What happened:**
  - The re-pre-flight refused `PF-SPREAD subsystem retrieval 10`, because the cap at 39 is 9.
  - `declare` still refused `DC-PREFLIGHT`, and void refused `DR-DONE`. Fixing a file would change the digest, so `DC-DROPS` would refuse.
  - No way on remains, yet void's own rule says a subsystem over after drops does not void. Without the reword (C3), or with the re-pre-flight before void (C2), the same set is declared.
- **What should have happened:** an honest cycle that re-pre-flights its round-2 set is declared. Either the step is placed before void, or the re-pre-flight after void tolerates what void tolerates.
- Ordinary work: yes, because round 2 is the normal path, the re-pre-flight naturally comes after void (that is where `declare` reports the refusal), and the brief allows a subsystem at 10.
- Consequence: other (fails closed; nothing is lost, but the week's audit cannot be declared without a hand repair). A row.
- **What would reverse it:** W2-172's cycle stating the pre-flight after writer round 2 and before void; or a CTO reading that a subsystem over after drops must block the declaration.

**RV7: a set pre-flighted at one commit can be declared at another** (scope: in, S3)
- **What was done:** a clean pre-flight and void at the audit commit, then `declare --commit <later>` with a store whose fingerprints head is that later commit.
- **What happened:** exit 0, `USED` written. `DECLARATION.json`'s `audit_commit` is the later commit, while `PREFLIGHT.json`'s commit and every question's `commit` field are the audit commit. The sources were never checked at the declared commit.
- **What should have happened:** a refusal when the commit given to `declare` differs from the pre-flight's (it can be read from `PREFLIGHT.json`).
- Ordinary work: no, because the cycle (W2-172) resolves the audit commit once and passes it to every subcommand. Reaching this needs a hand-run `declare` with a commit resolved separately, and a store rebuilt to that commit.
- Consequence: fails open. A row (Wave 3, or an entry criterion of W2-172).
- **What would reverse it:** a stated flow where `declare` is run by hand with its own `--commit HEAD`, or a store routinely rebuilt between the pre-flight and the declaration.

**PKG-W2-170-TD2-1 (the test designer's open point):** I see it as stated: after void, a replaced set that the pre-flight refuses has no way back, and it fails closed. RV6 is a second route to the same end. Both are closed by placing the re-pre-flight before void in W2-172's cycle.

**Classification:** 0 yes/fails open or loses work; 1 yes/other (RV6); 1 row marked no (RV7). Round 1's rows RV2-RV5 stand unchanged.

**Recommendation:** RV1 is fixed and nothing blocks. RV6 and RV7 go into W2-172's entry criteria together with PKG-W2-170-TD2-1. No further round is needed (DEC-1010, DEC-802).

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "RV6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": [{"id": "RV7", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}, {"kpi": "F5", "verdict": "pass", "findings": []}]}
```
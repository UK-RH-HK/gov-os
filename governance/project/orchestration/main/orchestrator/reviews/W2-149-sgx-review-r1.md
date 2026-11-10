The review of set-up A's wiring at `7df7c35e3` is finished. I recommend READY: of the 13 findings, none is in scope, reachable in ordinary work and fails open or loses work, so nothing blocks. Six of them are worth fixing or ruling on before the first real labeller run.

**Sandbox check (Step 0):** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-149` failed with `OSError: [Errno 30] Read-only file system`, as required. (b) `git hash-object -w --stdin` worked (`1ae28402a109c3397a44b19239a00adfa9472eb0`) and so did `git update-index --refresh`.

**ps check:** I ran `ps -eo pid,args` on its own rather than the piped form. It shows only my shell and `ps`: no ollama or llama-server process of mine.

**Identity:** HEAD is `7df7c35e3bb701ce594e42c6e97b564fe398fe55` on `w2/W2-149-sgx`. `git status --porcelain` was empty at the start and is empty now.

**decisions:** DEC-1112 (3), DEC-1113 (2), DEC-1101 (2)-(3), DEC-1099 (1), DEC-1010, DEC-801, DEC-802, DEC-808, DEC-1014, DEC-1073. I found no superseded or PROPOSED rule in use: the code follows amendment A5 (seeds drawn by the script), not the old blank in §5.

---

- **task:** DAEO-52ku (W2-149), the independent read-only review (FULL profile) of set-up A's wiring: S16, S20, S22–S28 and the new failure line (DEC-1112 (3)).
- **status:** DONE
- **work_completed:**
  - Read the rulings at `4fd701aba`: DECISIONS-IN-FORCE's last entry and the declaration's A5, §4–§6 and §12.
  - Read the five reference briefs; their sha256s equal §12's.
  - Read the ticket's changed lines and its last note, JUDGEMENT.md, and the README section "Set-up A's wiring: the interface".
  - Read `indep_launch.py` end to end (2,397 lines) and its whole diff from `7b08bd12d`, plus the five result schemas and the counts schema.
  - Read the designer's four new case files, `w2_149_setup_a.py`, the support changes and the four revised cases; the engineer's unit tests and the evidence's set-up A section.
  - Checked the folder layout the launcher reads against the experiment's own scripts (`common.py`, `extract_corpus.py`, `score.py`, `run_a.py`).
  - Checked the real path map's seal entries and where the pinned interpreter really lives.
  - Checked the seccomp filter in the rule-script wrapper by hand.
- **files_changed:** none in any tree. One scratch file in my sandbox TMPDIR (a saved diff) was made and then removed.
- **evidence:**
  - The five briefs: `bbff1249…`, `e13b5f96…`, `82134b3d…`, `137a73d1…`, `b212a424…`, each equal to §12.
  - `~/.local/bin/gov`'s first line names `/home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python`, which resolves to `/usr/bin/python3.12`. So the real run needs no bind outside `/usr`.
  - The real path map (lines 537–541 and 582–588) holds the seal's set and covers it, so writer 2 would get `{"sealed": true}`.
  - Nothing gov-related exists under `/usr/local` or `/usr/lib/python3*/dist-packages`.
  - Scratch folder at the end: `du -sh` 20K, `du -s --inodes` 8.
- **tests:** none run. Following the role file, I did not re-run what the lead ran: 227 passed including the 9 `bwrap` cases, and 3 live passed, outside the sandbox. I accepted the designer's record of 61 red cases before the build. No heavy-slot job.
- **discoveries:**
  - The half folders, file names and experiment folder (`EXP`, `SEALED_REL`) match the experiment's scripts exactly.
  - The unit tests launch with the repository's real template, so the real `kinds.yaml` is exercised with the five briefs' front matter.
  - **My own slip:** early on, one read-only `git diff` Bash line named the two template files under `governance/project/indep-walls/`, against the brief's "Read tool only" rule. It ran and wrote nothing; every later read of that folder used the Read tool.
- **risks:**
  - F18 with F23 is the likeliest stall. The rule script is first tried at round 2, after round 1's files are frozen, so a rejected script means redoing round 1.
  - F19 and F20 leave a delivered file sitting in its destination, which blocks a clean rerun (code 20).
  - For the held-out half, removing such a file needs an operator ACT.
- **lessons:** In this session the Write tool to my TMPDIR was not granted. I did not retry it or work around it, so F28 was settled by reading the guard's rules rather than running a probe.
- **proposed_decisions (CTO):**
  - F18: run the confined check at round 1's delivery, so a broken script never lands.
  - F19: a set-up A result whose `stopped` is not `none` delivers nothing.
  - F20: give labeller 2's lines the same check labeller 1 gets.
  - F21: accept the empty-reason tell as a known limit, or drop reasons from a dispute unless both sides have one.
  - F22: an audited case's `rule_class` follows the auditor.
  - F23: accept `rule_class` as an integer or a decimal string 1–14.
- **unresolved:**
  - F28: the five new documented lines have not been driven through the guard hook (my probe file was not granted).
  - The `bwrap` cases cannot run in this sandbox; I rely on the lead's run for them.
- **recommended_next_action:**
  - READY by `verdict.py`; no review round (DEC-1010).
  - Cheap fixes to ride along with the next resume (DEC-802): F19, F20, F23, F26.
  - Rulings for the CTO before set-up A's first labeller run: F18, F21, F22.
  - Wave 3 or recorded rows: F24, F25, F27, F29, F30. F28 needs one hook run per new line.

---

## Checks 1–7

**1. The briefs pass unchanged.** Yes. I read the code path for each of the five:
- **Stage 10:** `model` comes from the kind (`claude-opus-5-5`), `result_schema` from the brief's entry, `sample` from the front matter (writers: 400) or the entry (0). Budgets and timeouts are within each kind's. The tools used are the kind's, and they equal each brief's `tools:` list.
- **Inputs, as each brief names them:**
  - Writer 1: `selection.json`. Besides what the brief names, it carries S5's `changed` and `last_audit` fields (by the interface; harmless).
  - Writer 2: the same, plus `seal.json`.
  - Labeller 1, round 1: `half.json`, `actions.jsonl` and `cases.jsonl`, each line cut to the brief's fields.
  - Labeller 1, round 2: the same, plus `round1/`, `script-labels.jsonl` and `sample.json`.
  - Labeller 2, round 1: `half.json` only.
  - Labeller 2, round 2: `half.json`, `round1/rulebook-2.md` and `sample.jsonl`. Its brief does not list `half.json` for round 2; it is harmless and the interface includes it.
  - Overlap auditor: `half.json` with `cases`, `disputes.jsonl` (the action's 7 fields, x and y each with label, class, clauses and reason) and `tickets.jsonl` (`id role wbs_id allowed_paths`).
- **Outputs land where the briefs say:**
  - The writers' `cases.jsonl` goes to the half's `planted/`; `aims.jsonl` stays in the wall's tar only.
  - Each labeller's round 1 goes to `labels/r1-<id>/`.
  - Labeller 1's round 2 produces the merged `labels.jsonl`; labeller 2's round 2 produces `labels-2.jsonl`.
  - The auditor's decisions are mapped back, the x/y map is written, `labels.jsonl` is rewritten with its old copy in `history/`, and flagged cases go to `owner.jsonl`.
- **Results:** the five closed schemas match each brief's result forms and its list of `stopped` words.
- No brief needs a change to work.

**2. The confined rule script.**
- **Read:** it sees an empty, read-only root holding only `/usr`, the `/lib*` links, the loader cache, a fresh `/dev`, a `/proc` for its own process namespace, and the script file. Its environment is empty, and so is the environment of the sandbox's first process.
- **Write:** no byte reaches any file (read-only root; file-size limit 0; the `/dev` area is private and discarded).
- **Network:** none (its own network namespace, and socket creation is refused).
- **Process:** none (fork, clone and exec are refused; process limit 0).
- **Outliving its cap:** no. At 20 s wall-clock the sandbox's process group is killed, and when the namespace's first process dies the kernel kills the script. At 15 s CPU the kernel kills it. It also dies with its parent.
- **Partial or forged labels:** its output must give every staged id exactly once with valid fields; anything else is 18.
- **The seccomp filter, checked by hand:** 17 instructions; any architecture but x86_64 is killed; x32 calls and the 10 listed calls get EPERM; everything else is allowed.
- **Every failure is 18, never a pass:** a missing `bwrap` or interpreter, a forbidden bind, a start error, a cap, a non-zero exit, bad output, or any unexpected error at that stage.
- **Fail-open paths:** none except a test override left on a real run (F24). See also F18, F23 and F25.

**3. Independence.**
- Each labeller's walls stage only its own round-1 files and the half's lines; labeller 2's round 1 gets `half.json` only. Neither labeller's wall can reach the other's files (the run outputs and the sets root are denied).
- The x/y map stays in memory, is written only at delivery, and is never in the wall or the tar. The labellers' names appear only in the delivered decisions file. But see F21: the auditor can still tell which side is the first labeller's script.
- The overlap uses the declaration's rule with the seed of the labeller-2 round-2 wall (A5).
- Seeds are the script's own 63-bit draw; `--seed` is refused (17) without `--dry`.
- No caller input chooses content: `--set` picks only the half, and `--audit` is recorded only.

**4. Deliveries.**
- All or nothing: each file is written beside its destination under a temporary name and read back, then linked into place (or replaced, for the two files allowed); any failure undoes every step, including on SIGTERM and SIGHUP. A hard kill mid-commit is not covered; that is an accident, not ordinary work.
- Only `labels.jsonl` and `owner.jsonl` are ever overwritten.
- `labels.jsonl`'s old bytes go to `history/` first, and the rewrite is refused (20) if the file changed since the build.
- The set-up A path never writes `AUDITS.log`.
- Folders are made only on the way to a destination and removed if the delivery fails.
- S18 counts what set-up A adds for good (the tar and the landed files). F30 is a small transient gap.

**5. No regression.**
- The only removed lines are the old generic labeller flow and the old front-matter-only stage 10. The memory writer, checker and auditor delivery and AUDITS.log code is unchanged.
- Two intended side effects reach memory briefs: a missing `model` now falls back to the kind's, and the briefs folder is now left out of every tree.
- The template changed as the rulings say, plus F29.

**6. The cases.**
- The oracles recompute independently: the staged lines, both seeded draws, the disputes, the map and the merge.
- No case is weakened.
- Every revised case carries a `Rewrite-Reason` trailer (`59030819b`, `45fa65963`).
- The S16 writer fix (comparing a string with a path) is correct: a stray copy of the aims marker anywhere but the wall's tar still fails the case.
- Gaps: F28 (S19's lines), F21 (the empty-reason tell is not checked).

**7. Failure lines.** None now passes where it should fail. Line 7 depends on how "a stopped session" is read (F19). Line 11 holds except through the override (F24).

---

## Findings

Classification: 13 findings (F18–F30). None is in scope, reachable in ordinary work and fails open or loses work. F24 fails open but needs a deliberate override (a Wave 3 row). F27 is out of scope. The rest are in scope with consequence "other". Recommendation: READY, no round.

**F18 — The rule script is first tried at round 2.**
- **What happens:** labeller 1's round 1 delivers `label_rules.py` without running it. At round 2 a script that crashes on the real half refuses 18. Round 1's files are frozen by design, so round 1 must be redone. But a fresh round 1 refuses 20 because its destination files already exist, until someone removes them by hand. For the held-out half that means an operator ACT inside the sealed folder.
- **What should happen:** round 1's delivery runs the same confined check and refuses 20, landing nothing, when the script does not give every staged id once within the caps.
- Ordinary work: yes, because the labeller writes a program it cannot run (it has no shell, and its brief does not state the caps) against about 11,000 actions of mixed shapes.
- Consequence: other
- Scope: in (S25, S16).
- **Reverses if:** a procedure clears `r1-<id>/` without an ACT, or trials show honest scripts run first time.

**F19 — A result that says it stopped is still delivered** (the engineer's note b).
- **What happens:** a session whose `result.json` says `stopped` is not `none` still has its out/ files delivered: a writer's partial `cases.jsonl`, a labeller's round-1 files, or labeller 2's `labels-2.jsonl`. The launcher reports `status: delivered`, exit 0; only `out.stopped` in counts.json says otherwise. The rerun after the owner's ruling then refuses 20 until the partial file is removed. Labeller 1's round 2 and the auditor are already protected by their completeness checks (S26, S27).
- **What should happen:** nothing is delivered when `stopped` is not `none`; the product stays in the tar.
- Ordinary work: yes, because every brief provides this stop, and a writer writing class by class leaves a partial file.
- Consequence: other
- Scope: in (S16, S28).
- **Reverses if:** the CTO reads failure line 7's "a delivery from a stopped session" as including the brief's own `stopped` word. Then this fails open and S16 fails.

**F20 — Labeller 2's labels land unchecked** (the engineer's note a).
- **What happens:** `labels-2.jsonl` is delivered byte for byte. A malformed line surfaces only when the overlap auditor's launch refuses 10, and the bad file then blocks a corrected rerun (20). Missing or mistyped ids silently drop out of the overlap.
- **What should happen:** S26's style of check: every line valid and the ids exactly the staged sample, else 20.
- Ordinary work: yes, because a session writes hundreds of JSON lines by hand.
- Consequence: other
- Scope: in (S16, S27).
- **Reverses if:** the CTO rules that labeller 2's completeness is the scorer's job.

**F21 — The auditor can tell the first labeller's script labels.**
- **What happens:** S26's merge gives script-labelled lines an empty `reason`, and labeller 2's brief requires a reason on every line. So in every dispute where labeller 1's side came from the script, the empty reason tells the auditor which side is labeller 1's — despite its brief saying "You do not know which labeller wrote which label". The x/y map itself never enters the wall.
- **What should happen:** a CTO ruling: accept this as a known limit and tell the owner, or carry reasons in a dispute only when both sides have one.
- Ordinary work: yes, because it happens automatically on every dispute over a script label.
- Consequence: other
- Scope: in (S27, check 3).
- **Reverses if:** the x/y blind is treated as a guarantee the launcher must hold. Then this fails open for those cases.

**F22 — An audited line mixes the auditor's label with labeller 1's class.**
- **What happens:** a settled dispute changes only `label` and `how`. The line keeps labeller 1's `rule_class`, `clauses` and `reason`, and the scorer counts per class from `labels.jsonl`. The interface fixed this form.
- **What should happen:** a ruling on whether a settled case takes the auditor's `rule_class` as well.
- Ordinary work: yes, because label disputes are usually class disputes too.
- Consequence: other (pass or fail is unchanged; the per-class tallies move; the decisions file keeps the auditor's class).
- Scope: in (S27).
- **Reverses if:** the scorer reads the classes of audited cases from the decisions file.

**F23 — The type of `rule_class`.**
- **What happens:** the cases the labellers read carry `rule_class` as a string (the writers' form, `"<class>"`), and no brief states its type. The launcher accepts only a JSON integer in the rule script's output (else 18, which with F18 means redoing round 1), in the hand labels (else 20) and in the decisions (else 20).
- **What should happen:** accept an integer or a decimal string 1–14 and store an integer.
- Ordinary work: yes, because a session that copies its input's form writes "7".
- Consequence: other
- Scope: in (S25, S26, S27).
- **Reverses if:** trials show sessions write integers.

**F24 — The rule script's test overrides are not recorded.**
- **What happens:** `GOV_INDEP_BWRAP` and `GOV_INDEP_RULES_PYTHON` are honoured on any run. A stand-in program named there runs the script without the read and network walls, and nothing in WALL.json, counts.json or the log says so. The runs and trees overrides are recorded (reading 2).
- **What should happen:** record both overrides, or refuse them unless the sets root is planted.
- Ordinary work: no, because it needs an override typed on the real line and a script that opens files.
- Consequence: fails open
- Scope: in (S25). A Wave 3 row.
- **Reverses if:** the CTO's launch environment strips `GOV_INDEP_*`.

**F25 — All of `/usr` is visible.**
- **What happens:** the whole of `/usr` is bound, which is more than S25's "the interpreter's own files". Nothing protected lies under it on this machine.
- Ordinary work: no, because an honest rule script opens no file.
- Consequence: other
- Scope: in (S25).
- **Reverses if:** the CTO rules that `/usr` counts as the interpreter's files.

**F26 — A unit test aims at the shared Ollama port.**
- **What happens:** the engineer's network-wall unit test connects to 127.0.0.1:11434. Confined, it never connects. If the wall it checks were broken, it would touch the owner's shared Ollama server, which the common rules forbid.
- **What should happen:** use a planted listener, as the acceptance case does.
- Ordinary work: yes, because it runs on every `bwrap` run.
- Consequence: other
- Scope: in (S25's tests).
- **Reverses if:** n/a (fixed by changing the target).

**F27 — The two labellers can collide when launched in the same second.**
- **What happens:** run ids are made of the second, the half and the round, so the two labellers launched in the same second can draw one id. In a sub-millisecond interleaving, one run's start failure packs and removes the other's new wall, and the two share a counts folder. This is pre-existing code; set-up A just makes parallel same-kind launches natural.
- Ordinary work: no, because it needs a millisecond-wide window.
- Consequence: other (both runs fail at their start).
- Scope: out.
- **Reverses if:** launches are serialised.

**F28 — The five new documented lines are not driven through the guard.**
- **What happens:** S19's cases drive their own six lines, not the five new set-up A lines (README N-5). By reading the guard's rules they pass: no hidden folder is named, and the held-out list names only the qualification oracle. But no case shows it.
- Ordinary work: yes, because the CTO will run exactly these lines.
- Consequence: other (a refusal would fail closed).
- Scope: in.
- **Reverses if:** one hook run per line is allowed.

**F29 — `kinds.yaml` changed slightly beyond the rulings' list.**
- **What happens:** the labeller kind's `input:` and `delivers:` lines were also rewritten. No code reads either value.
- Ordinary work: no, because no code reads them.
- Consequence: other
- Scope: in (check 5).
- **Reverses if:** the CTO rules that descriptive lines may follow the code.

**F30 — S18's set-up A estimate counts one product file.**
- **What happens:** flows that leave more than one file in out/ (a writer's `aims.jsonl`, labeller 1's second round-1 file, a `conflicts.md`) exceed the estimate by one or two while the wall exists. What stays for good (the tar and the landed files) is within it.
- Ordinary work: no, because it needs the hidden part within two files of 8,000.
- Consequence: other
- Scope: in (check 4).
- **Reverses if:** the CTO rules that S18 bounds only what stays.

**Probed and found sound:** the engineer's note (c), writer 2 ending `rejected` 20 with `out.stopped: not-sealed`. A not-sealed run cannot happen with a commit that passes stages 10 and 11, because the template's `briefs:` entries came after the seal.

```verdict
{"kpis": [{"kpi": "S16", "verdict": "pass", "findings": [{"id": "F19", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F20", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S20", "verdict": "pass", "findings": []}, {"kpi": "S22", "verdict": "pass", "findings": [{"id": "F29", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S23", "verdict": "pass", "findings": []}, {"kpi": "S24", "verdict": "pass", "findings": [{"id": "F27", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F28", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F30", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S25", "verdict": "pass", "findings": [{"id": "F18", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F23", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F24", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F25", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F26", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S26", "verdict": "pass", "findings": []}, {"kpi": "S27", "verdict": "pass", "findings": [{"id": "F21", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F22", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S28", "verdict": "pass", "findings": []}]}
```
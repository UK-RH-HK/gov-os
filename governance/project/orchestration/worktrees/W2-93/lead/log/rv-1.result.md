## Step 0: sandbox check (run first)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-93','w').write('x')"` failed with `OSError: [Errno 30] Read-only file system`, and no file exists. Pass.
- (b) `echo sandbox-trial | git hash-object -w --stdin` printed `1ae28402a109…` with exit 0, and `git update-index --refresh` exited 0. Pass.
- `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.
- `git rev-parse HEAD` is `0a693c61aecb4c985dde0cb2a50d5ba18908a488`, the probed head.
- `git status --porcelain` was empty before and after my probes.

```
---
type: probe
task: DAEO-6y0x
reviewer_session: see launch log
implementer_session: b17b46d4-cc7a-4953-9d7a-565fc1a30089
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: 0a693c61aecb4c985dde0cb2a50d5ba18908a488
---
```

# Probe record: DAEO-6y0x (W2-93), narrow independent check

## Summary

**Judgement: pass.** No finding is in scope, reachable in ordinary work, and fails open or loses work. The four ranked findings below are rows for the Wave 3 hardening pass. None is a round.

### What I read
- `fixtures/evaluation/adoption-proving-ground/validate_hidden.py`, whole.
- The `w2_81_run.py` diff.
- `w2_81_questions.resolve`, `_apply_one` and `build_all`, `w2_81_manifest.validate`, and `w2_81_git.tree`, `blob` and `git_env`.
- W2-81's README section "The hidden half's form, for W2-93".
- The approved writer brief, only for the lines on `forbidden`.
- The ticket.
- All W2-93 tests, `conftest.py` and `w2_93_standin.py`.
- The real `adoption-proving-ground` entry in `governance/project/path-map.yaml`, and `gov.guard.reads.policy_refusal`.

I did not open anything under `~/gov-os-eval` or any `hidden/` folder, and I quote no question or answer.

### What I ran
No pytest, since you ran the W2-93 folder. All probes ran in my own `$TMPDIR` on stand-ins built with `w2_93_standin`, as subprocesses of the real scripts, in Python 3.12 with `PYTHONPATH=<tree>/src`.

- **Validator probes:** about 55 cases. They covered:
  - **Counts:** a valid stand-in, 9 questions, `forbidden` removed from every question.
  - **S4 and S5:** a gold line not at HEAD, a gold fact missing from a question and from an answer, a forbidden path naming no file or only a directory.
  - **S2 variants:** a variant dropped, an empty variant list, an unknown repository, an unknown kind, a variant in the clean twin, a variant labelled with a kind its steps don't plant.
  - **Fail closed:** a named pipe, a BOM, YAML with an error snippet, a Python tag, an 8 MB file, an empty file, `null`, `chmod 0`, a symlinked hidden folder, an extra file, an extra folder, a hostile file name.
  - **Type fuzz:** about 20 wrong-type mutations of questions and variants.
  - **Repository and temp folder:** a direct run from `/` without the bytecode environment variable, then a check of the repository and the temp folder afterwards.
- **Runner probes:**
  - **`--sets-root` missing the folder:** the root has no folder, doesn't exist, or its `hidden` is a file, in all three modes.
  - **Both flags together:** `--sets-root` with `--hidden`, in build and read.
  - **`--hidden`:** a missing folder, and a valid one.
  - **`--sets-root` against `--hidden`:** a build with `--sets-root` and one with `--hidden`, then a read of each.
- **Guard:** `policy_refusal` directly on a stand-in project that carries the real map entry. Bash routes `git log -p`, `git log -p --all`, `grep -rn` from the root, `git show`, `git grep` and `cat <hidden file>` were refused for `engineer` and `independent-auditor`. `git log --stat` and `git diff` were allowed. They print file names only, with no content.

### Per KPI line

**S1 (form, at least 10 per repository): pass.**
- The valid stand-in exits 0 with `<repo>: 10 hidden questions` for each of the six repositories and `valid: 60 …` (`validate_hidden.py:341-347`).
- 9 questions in one repository gives `refused: python-app: 9 hidden questions, at least 10 needed`.
- The id, category, question, gold_answer and sources checks are at `:125-150`. A missing field or wrong type names the question's id, or `<repo> question #n` when the id is unusable.
- `forbidden` absent is accepted. Present, it must be a list of non-empty strings, and `null`, a dict or a non-string element is refused (`:148-150`).

**S2 (variants): pass, with one finding (R-1).**
- The rule is computed from the visible build, never a fixed list (`:200-202`, `:239-245`). It reads each repository's manifest entries that are not `hidden`, and takes the visible kinds from a second, variant-free build when the variants fail to build (`:327`).
- Dropping any one required variant, or emptying the list, is refused naming the repository and kind.
- A variant in `python-app-clean` is refused as `hidden variant #1 (<id>): the clean twin … takes no variant`.
- An unknown repository or kind, or malformed steps, gives `hidden variant #n (<id>): cannot be built`, with no content in the line.
- A mapping with no `id`, a duplicate id and a non-list top level are each refused.

**S3 (found only under the hidden folder): pass for the code in this diff.**
- Both tools read only `<root>/fixtures/evaluation/adoption-proving-ground/hidden`.
- The validator also refuses any other entry in that folder (`_entries`, `:88-104`).
- The planted words reached no output across all my probes. The two exceptions are in R-5, and they concern the file-name echo and the tests' own reach.
- The delivery's run record (the walled writer's run name, the brief's sha256) is the CTO's, after landing, and is not in this diff. I judge only what the diff does.

**S4 and F2 (gold held on a built copy): pass.**
- A source `holds` not at HEAD gives `refused: python-app-h01: a gold source is not in the built repository as stated`.
- A fact missing from a question or a gold answer gives `refused: python-app-h01: a template names a fact the repository does not have`.
- A wrong source path, a traversal path and a `HEAD:x` path are refused the same way.
- Each is checked question by question with `questions.resolve(..., "hidden")` (`:219-226`). No message carries a template, fact or value. Only a fixed phrase is passed through, and the `<id>: ` prefix is stripped.

**S5 (forbidden, fail closed, untouched W2-81): pass, with findings R-2 and R-3.**
- A forbidden path naming no file, or a directory, is refused naming the id.
- Every unreadable input was refused naming the file only. This included a named pipe (`O_NONBLOCK`, `S_ISREG`), a symlink (`O_NOFOLLOW`), a file over 8 MB, `chmod 0`, bad YAML, a Python tag, a hidden folder that is itself a symlink, and an extra file or folder.
- Any exception ends as `refused: the check: <class>` and never a traceback.
- Every refusal exits 2. The temp folder was always removed (the child's `TMPDIR` was empty after every case, pass or refuse), and the repository stayed clean.
- W2-81's files are untouched except `w2_81_run.py` and `test_w2_81_runner.py` (`git diff --stat a7b36bcfd98a 0a693c61aecb`).
- Gaps in what S5 guarantees are in R-2.

**S6 (`--sets-root` on both tools): pass, with note R-4.**
- The validator, the runner and `--hidden` all read the same hidden folder. The runner built 13 hidden variants through `--sets-root` and 13 through `--hidden` (`w2_81_run.py:113-128`).
- A root without the folder is refused with `refused: --sets-root holds no hidden half: fixtures/evaluation/adoption-proving-ground/hidden` and exit 2, in build, run and read modes. No run folder was created. The same happens for a root that doesn't exist or whose `hidden` is a file.
- `--sets-root` with `--hidden` is refused with exit 2 and no folder.
- A missing `--hidden` is still refused with exit 2, in both build and read modes.

**F1 (a measured session cannot read the hidden half): pass.**
- `test_w2_93_guard.py` reads the real map's entry (`:30`) and runs the guard's `policy_refusal` for each measured role over Read, Grep and Bash routes.
- A route passes only if the guard refuses it or the equivalent command finds the planted word 0 times. The planted file is committed, so `git log -p` finds it if it isn't refused. The case is not vacuous.
- My direct run matches this: Read, Grep and `git log -p` routes are refused for a measured role, with the hidden half's own reason.

### The lead's two decisions
- **The S2 reading** is within the interface and does not fail S2 as written. Each core kind a planted repository's visible build lacks needs a hidden variant there (11 for the stand-in). `legacy-document` and `large-file` need one each in some repository that doesn't visibly plant them. The clean twin takes none. It fits the approved 13-variant brief. A stricter per-repository reading for `legacy-document` and `large-file` would ask for more variants. It is a reading the CTO fixed, not a defect, and I record it only as R-6.
- **`forbidden` optional** does not fail S1 as written. W2-81's README form is the visible form, and 15 of the 61 visible questions have none. The same fact opens R-2.

## Findings

**R-1 (S2, scope out).** A variant's kind is only its label. A variant labelled `stale-spec` that carries `legacy-document` steps and evidence passes with exit 0. So does one whose `evidence` is `{}`. W2-81's builder checks evidence only for `secret`, in `w2_81_manifest.validate`, and the ticket forbids touching W2-81's builder.
- Ordinary work: no, because a writer working by kind from the brief's skeletons writes kind, steps and evidence together; a mismatch needs a copy-paste slip that the owner's record doesn't treat as ordinary, and the judge and builder own that check.
- Consequence: fails open
- Reversed by: a W2-81 builder or judge change that validates evidence per kind, or a recorded run of a mislabelled hidden variant that the judge accepts silently.

**R-2 (S1 and S5, scope out).** The validator needs no forbidden citation anywhere. With `forbidden` removed from all 60 questions, including the five planted repositories, it printed `valid` and exited 0. The approved brief (item on `forbidden`) requires at least one forbidden file per stale, superseded or misleading-name variant, and the validator can't see it. The valid output also prints no forbidden counts, so the CTO's recorded run can't show a gap either.
- Ordinary work: no, because the approved brief asks for them and omitting every one in a repository is a gross omission, not an ordinary slip.
- Consequence: fails open
- Reversed by: the README or the KPI text making at least one forbidden citation mandatory per planted repository, or the writer's run showing an all-empty planted repository.
- Recommendation for the Wave 3 row: print `forbidden=<n>` per repository, counts only.

**R-3 (S5, scope out).** A variant step path with `..` segments is written by the builder hook outside the validator's temp folder. A marker file went to the child's `TMPDIR` and was left behind. W2-81's `outside_this_repository` only refuses paths inside this repository, and this is the builder, not the validator.
- Ordinary work: no, because it needs a deliberately constructed path, and the writer's file paths are relative names.
- Consequence: other
- Reversed by: an approved hidden variant that legitimately needs a `..` path.

**R-4 (S6, scope out).** `--hidden` refusal order changed. A missing `--hidden` is now refused first, in `run()`, in every mode. Before, a build created the empty run folder first, and a read mode with no run record gave the "no run.json" refusal. The refusal is still exit 2 and still names the same cause. The new behaviour is stricter and harmless.
- Ordinary work: yes, because a direct call with a typo in `--hidden` hits it.
- Consequence: other
- Reversed by: a caller that depends on the old message order.

**R-5 (S3, scope out).** Two notes on what the tests and output cover:
- (a) The S3 commit-message and ticket grep (`test_w2_93_sets_root.py:79-90`) checks only the stand-in's planted words. It can't catch the real hidden half's words. It stays a guard for the process, and the README says so.
- (b) A hidden-folder entry name is echoed after being reduced to plain characters and 60 characters, so a hostile file name would be shown. Only the name is shown, as the interface says.
- Ordinary work: no, because the real half's words are checked only by the CTO's own run, and a question-like file name needs a deliberate choice.
- Consequence: other
- Reversed by: a real hidden file name containing question text.

**R-6 (S2, scope out).** `legacy-document` and `large-file` are required once across the six repositories, not once per repository. This is the reading above. The test for the clean twin, and the (b) rule, don't test a variant placed where the visible build already plants that kind.
- Ordinary work: no, because the CTO fixed this reading to the approved brief.
- Consequence: other
- Reversed by: the owner reading S2's "per repository" as covering all seven kinds.

### Probed and found sound
- Every output line was a fixed phrase, an id, a file name or a repository name.
- A YAML parse error's snippet never reached any line.
- Each refusal exits 2.
- A secret variant's value is checked against the output as a last step.
- The validator wrote no bytecode in the repository (`sys.dont_write_bytecode` is set before the imports), and it reads W2-81's modules from its own checkout, found from `__file__`, even when run from `/`.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "R-2", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "R-1", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}, {"id": "R-6", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": [{"id": "R-5", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "R-3", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "R-2", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "S6", "verdict": "pass", "findings": [{"id": "R-4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}]}
```
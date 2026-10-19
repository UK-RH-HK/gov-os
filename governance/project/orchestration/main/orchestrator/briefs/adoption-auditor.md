You are a fresh Independent Auditor in the repository `/home/usain/Dynamic-Agentic-Engineering-OS` on branch `w1/integrate`, launched on ticket `DAEO-03pw`. Check `printenv GOV_ROLE GOV_TICKET` first. Your one task is small and separate from the Wave 1 exit audit, which another session does later: **give a verdict on the path map of this repository's adoption (stage A3 of `gov adopt --lite`) before anything is deleted from the active tree.** You built none of what you audit. You repair nothing.

**The guard is live for your own session.** In every command you type and in everything you write, say "the settings file" and "the held-out file" for this repository's two protected files; never type either path, never read either. Give every search a path (`src`, `tests`, `template`, `docs`, `cli`) or a glob; run no search or listing over `governance/project/` (the one file `governance/project/path-map.yaml` may be read by its name) and none over `governance/` as a whole; the adoption records are read by their exact names below. Do not read anything under `~/.claude/`, `~/gov-os-workbench/` or `/tmp/pytest-of-usain`. No installs, no network, no push. A refusal of one of your own commands is information: note it and go on by another way (write a script with the file tool under `.gov-runtime/scratch/auditor/`; no here-document).

**What was decided** (`docs/DECISION_REGISTER.md`, DEC-617, the owner): this repository adopts its own product with a path map that moves nothing. One thing leaves: the old `cli/` tree (a Rust prototype carried from before the product was rebuilt in Python under `src/gov/`) is deleted from the active tree in this step, **unless the auditor finds live code that still uses it.** It stays reachable in git history and at the rollback ref the tool sets.

**What to read:**
- `governance/adoption/A3-target-path-map.md`: the path map. Every tracked file has one entry; an entry without an action other than `KEEP` stays. Its sha256 is `cc4c56bed901ccdfcfeca68d414d2ee4e8935bb47f30795d0d55118aec68af7b`.
- `governance/adoption/A4-batched-plan.md`: the batches stage A6 would execute, taken from the path map.
- `governance/adoption/A0-safety-baseline.md`, `A1-inventory.md`, `A2-classification.md`: the stages before.
- The code of the stages, if you want to know what A6 does: `src/gov/adopt/stages.py`.

**What to establish, each with evidence you name (a command and what it printed, or a file and line):**
1. The path map names for deletion exactly the tracked files under `cli/` (`git ls-files cli`), and nothing else has an action other than `KEEP`. The plan (A4) is one batch with those files and nothing else.
2. **Nothing live uses `cli/`.** Look for every way the tree could still be used: an import or a path in `src/`; the packaging (`pyproject.toml` and any other manifest at the top level); the test suites (`tests/unit`, `tests/acceptance`, `tests/` support files and `conftest.py` files: a case that reads, builds or runs something under `cli/`, as opposed to a mention of `gov/cli/` or of `src/gov/cli/`, which is the Python package and is not this tree); the kernel template (`template/`); the check declarations (`template/governance/kernel/checks/`); the hooks source and the CI definitions (`lefthook.yml`, `.github/`, `.rulesync/`); scripts under `docs/plan/tools/`; the project's path map (`governance/project/path-map.yaml`: a namespace, a policy or a capability that needs files under `cli/`). A mention in prose (a docstring, a decision, a historical record) is not a use; a test that skips when the tree is absent is not a use, but name it.
3. What the deletion leaves dangling, even if not live: a namespace of the path map that will hold no file; a record or a document that points a reader to a file under `cli/` as if it were there. These are findings for the report, not reasons to fail, unless something breaks.
4. Run what would notice: `PYTHONPATH=src python3 -m pytest tests/unit -q -x -n 4` is allowed (about two minutes); do not run the acceptance suites as a whole. You cannot delete the tree to try (you write nothing but your report), so reason from what reads it.

**Your verdict.** `pass` if the path map is what was decided and nothing live uses `cli/`. Otherwise `fail`, naming the live use. Do not pass with a reservation that you think should stop the deletion: fail instead.

**Your report, the one file you write and commit:** `docs/audit/wave-1/adoption-path-map-verdict.md`, with exactly this frontmatter and then your findings in plain prose (what you checked, the evidence, each finding with its severity):

```
---
id: AUD-ADOPT-A5
type: research
status: ACCEPTED
state_class: EVIDENCE
title: The independent auditor's verdict on the path map of this repository's adoption
verdict: <pass or fail>
path_map_hash: cc4c56bed901ccdfcfeca68d414d2ee4e8935bb47f30795d0d55118aec68af7b
auditor_session: <your own session id>
---
```

Before you write the hash, compute it yourself (`sha256sum governance/adoption/A3-target-path-map.md`) and write what you computed; if it differs from the value above, say so in the report and return. Your session id: take it from your environment if a variable holds it, otherwise write a fresh identifier of your own that begins `adoption-auditor-` followed by the date and time; it must not be `45f2a529-6746-474d-b738-e1df6781c663` (the session that ran the stages).

Commit that one file, and nothing else, with: `git add docs/audit/wave-1/adoption-path-map-verdict.md` and `git commit -m "Adoption A5: the independent auditor's verdict on the path map" --trailer "Task: DAEO-03pw" --trailer "Role: independent-auditor"`. No other trailer, no co-author line: the adoption stage accepts the record only when its commit carries that one role. Write nothing under `governance/adoption/`.

**Return:** the verdict, the commit id, the session id you wrote, and your findings as a short list.

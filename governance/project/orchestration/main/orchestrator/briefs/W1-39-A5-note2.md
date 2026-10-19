
## Run 2: your packages are decided; resume from your checkpoint

You are a fresh lead resuming run 1 (`.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree; branch head `ef974555` plus a merge of `w1/integrate` that brings the register and the ticket's new allowed paths). Read DEC-488 and DEC-493 in `docs/DECISION_REGISTER.md` (the last sections) and the ticket file again (its `allowed_paths` have changed).

- **P-1:** the comparison of a project with its lock is this ticket's own public function (DEC-488: never a match without having hashed; an absent or empty manifest is not a match; a kernel file the manifest does not list is drift, named; only `__pycache__/` folders are left out, not git-ignored files in general; the lock's tag and commit are compared with the answers file). `src/gov/doctor/command.py` and `tests/unit/doctor/**` are now in the ticket's paths **for the call of that function only** (DEC-493): the engineer replaces doctor's own lock part by the call and changes nothing else in that file; you check the diff of that file line by line.
- **P-2:** `template/governance/project/**` is in the paths: a minimal path map, which `copier update` never overwrites. Nothing else is shipped there, and nothing of this repository's own `governance/project/` is copied into it (the held-out file above all: no worker reads, copies or names it).
- **P-3:** the update procedure is documented in the template's messages after copy and after update and in a comment header of the generated lock (DEC-488).
- **P-4:** `copier copy` does not run the adapter generation; it is a documented step, named in the procedure (DEC-488).
- **P-5:** the answers file is Copier's standard `.copier-answers.yml` (DEC-023); the allowed path is now `template/.copier-answers.yml*`.
- **`template/.gitignore`** is in the paths: it ignores `.gov-runtime/` and `__pycache__/` in an installed project. If Copier or a worker's tools refuse a file name (a launched engineer's Write tool refused `lefthook.yml` in another ticket), the worker does not route around it: return the refusal's text and the content.
- A test designer first brings the cases to these decisions where they differ (the open point on git-ignored files; the overlay case; the ignore file) and tags any rewritten case's commit with a `Rewrite-Reason:` trailer if an engineer commit already exists; then the engineer.
- From now your own merge commits carry `Implements:` too (the ticket's capability id), besides `Task:` and `Role: orchestrator`: `gov close` refuses a ticket with a commit that lacks it.
- Then the loop as before: verify every suite, read the diff for places that say "matches" without having hashed, return DONE or PACKAGES.

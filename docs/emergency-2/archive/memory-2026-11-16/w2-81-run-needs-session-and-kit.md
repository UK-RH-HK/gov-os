---
name: w2-81-run-needs-session-and-kit
description: W2-81 --mode run is a smoke form (A0-A2 only, never READY); from the 0.1.0 wheel A0 refuses without the kit (template/.gitleaks.toml not shipped); full run = build, kit+A0, adopting session, --mode read
metadata:
  type: project
---

On 2026-11-15 my W2-81 page gave the owner's operator `--mode run`. It ended NOT_READY with A0 exit 1 in all six repositories.

**Causes:**
- The 0.1.0 wheel's `_shipped/` lacks `template/.gitleaks.toml`, which A0 and MA read through W2-88 S24's `fabric.shipped`. So A0 refuses SHIPPED_FILE_MISSING in a repository without the kit.
- `--mode run` only runs A0-A2 anyway, so it can never reach READY.
- The runner drops each stage's stdout and stderr. To find a cause, reproduce on a `git clone` in scratch with `env -i` and the runner's `_env`.

**Why:** I promised a run result that the run mode cannot give, and I missed the kit step that EXAMIN's Part A had.

**How to apply:** a W2-81 full run is:
1. build;
2. for each repository: the kit from the tag, held-out.yaml (the sets root and `<run>/manifests/**`), adapters, A0 and the review tickets;
3. one adopting session, A1-A10 lite;
4. `--mode read` with `--close-ticket` and `--sets-root`.

Package P-W2-81-FULLRUN. Related: [[adopted-review-ticket-fields]].

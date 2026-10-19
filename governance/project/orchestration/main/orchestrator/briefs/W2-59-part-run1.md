You are the ticket lead for ticket `DAEO-kh9l` (`W2-59`, "The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-59` on branch `w2/W2-59`, cut from the integration branch `w2/integrate` at `c5100159`. You run the ticket loop for this one ticket and return one summary. You are a headless session: nobody answers questions while you work, and only your final message is read.

**This is run 1.** `git log --oneline -1` must show `c5100159`, and `git status --short` must show nothing (anything else: stop and return PACKAGES naming it). Your ticket file `.tickets/DAEO-kh9l.md` holds the KPIs; read it first.

## Why you start now

Keystone 1 of the accepted revised plan (DEC-831) is the pinned judge. The owner installed the bootstrap pin on 2026-10-19 (DEC-822 step 1: `~/.local/bin/gov` -> `~/.local/share/gov-os/pin-fecb870c/bin/gov`, a non-editable wheel of `fecb870c`; no `gov` importable by the system `python3`). The pin's `gov check` that evening showed the gap this ticket closes: the declared checks still run the working tree's `src` (`secrets-indexing` ran from `/home/usain/Dynamic-Agentic-Engineering-OS/src/gov/…`). The owner approved the scope (DEC-835) and this start beside W2-05 (DEC-854).

## The owner's decisions for this run (2026-10-19; DEC-831 to DEC-852 are in this worktree's register at `a5789de1`; DEC-853 to DEC-855 are staged for the owner's next commit — apply them as written here)

- **DEC-822 (in your register):** step 2, the hook command lines call the pin's environment, after the independent test designer has checked W1-38's hook-source tests against the change (MR-3); item 3, DEC-732's per-command `PYTHONPATH` stays and now chooses only the code under test, not the judge.
- **DEC-835 (in your register):** the scope, with the two packaging gaps: `retrieve_baseline.yaml` as package data, and every module that finds the repository from its own install path finds it from the project root (today `retrieval/canary.py:10` and `retrieval/retrieve_check.py:16`); proven from an installed wheel.
- **DEC-854 (staged): you start beside W2-05.** W2-05 (`w2/W2-05`, unmerged, idle) changes `_run_command`'s `env = dict(os.environ)` to `env = git_env(root)` (from `gov.util.gitenv`, which exists only on its branch), adds `env=git_env(root)` to three git calls in `runner.py`, and adds an import of `git_env` and an environment-clearing block to `retrieve_check.py`'s `main`. Your engineer keeps its edits of those lines small and composable, never imports `gov.util.gitenv`, and its CIT-P names the overlap; W2-05's resume takes the conflict, keeping both sides (DEC-750, DEC-754). Read `git diff w2/integrate...w2/W2-05 -- src/gov/check/runner.py src/gov/retrieval/retrieve_check.py` yourself so your engineer's brief can describe it as behaviour.
- **DEC-853 (staged):** W2-50's resume fixes the secrets scan's time limit (today `secrets-indexing` times out on the 250 MB store, so it is RED here; that red is known, not yours). After your merge, the owner re-pins at a commit that holds both.

## Facts for the design (give them to the test designer as behaviour, never as code names)

- Two installs exist: the pin's venv `~/.local/share/gov-os/pin-fecb870c/` (its `bin/python`, `bin/gov`, and `lib/python3.12/site-packages/gov/`), and this worktree's `src/` (the code under test, by `PYTHONPATH` per command, DEC-732).
- **The pin's path names a version** (`pin-fecb870c`), and the owner moves the pin with each release (the pin ladder). Hook command lines and the runner must not hard-code a versioned path that the next re-pin breaks. If a stable name for the pin's interpreter is needed (for example a link the owner's pin script maintains), return a package naming the exact owner command, and keep everything else going.
- `.rulesync/hooks.jsonc` is the source of the hook lines; the generated settings file is the owner's to regenerate (never read or write it: the guard refuses it).
- A wheel can be built and installed for the "proven from an installed wheel" cases into a temporary folder made by the test (never under `.gov-runtime/`, DEC-673; never in `~/.local`).
- A full rebuild here takes about 21 minutes (the per-file gitleaks gate; package P-W2-50 is with the owner): plan for it, run it in the background with an exit-code file, and wait for load as the common brief below says.

## This run's order

1. **Tests first:** a fresh independent test designer, launched sandboxed (`--effort high`), on the five success KPIs and the failure KPI, STANDARD proportion, with W1-38's hook-source tests checked against the hook-line change (it names any W1-38 test the change needs revised; a revision is a package).
2. Check red yourself.
3. **Implement:** a fresh engineer, launched sandboxed (`--effort high`), inside the allowed paths only.
4. **Verify** as the loop says. Known reds you did not cause: W1-42's two accepted reds; `secrets-indexing` RED in `gov check` (the timeout above).
5. **Independent review of the CIT-P (CAP-33):** although the profile is STANDARD, this is a judge change, so after green run one fresh read-only reviewer (brief A3 with `JUDGEMENT.md`, `--effort max`) on the final code and `docs/changes/W2-59-CIT-P.md`. Commit its probe record under `docs/probes/DAEO-kh9l/` only if it passes.
6. Return.

---


**Resume note (third start of this round; read it before the rest, and where it differs from the rest, it holds).** Rewrite `.gov-runtime/scratch/lead/CHECKPOINT.md` first; what is there is your predecessor's.

## What went wrong in the second start (three things; none may happen again)

1. **The lead ended its turn with "Waiting for the reviewer to complete."** A headless lead's turn ends there; the review was lost and nothing was returned. You wait in the foreground (`until [ -s (the log) ]; do sleep 20; done`, repeated) and you never end a message on a running worker.
2. **Tests wrote into the real `~/.local/state/gov-os/`,** which this round's first safety rule forbids: six entries from 16:59 (keys beginning `03be1807`, `1a695699`, `259da0a3`, `2a81cd42`, `5cdc6024`, `cd022d1a`), and the folder's modification time moved again at 17:48, after the supposed fix, so something still creates and removes an entry there. None of the six is this repository's key, so nothing is frozen. **Nobody removes those six entries: they are the owner's to remove.** They are your baseline.
3. **The lead wrote a test file itself** (`tests/unit/pause/test_pause.py`, commit `6b9103b2`, no `Role:` trailer) and the reviewer was not started through `gov launch` (no log of it exists). A lead writes nothing under `src/`, `template/`, `tests/`, `docs/`; every worker, the reviewer included, goes through `gov launch` with a log under `.gov-runtime/scratch/lead/log/`.

## Where you are

Branch `w1/W1-50-mirror` at `775b0089` (the main orchestrator removed `6b9103b2` from the tip, DEC-412; the second start's head is kept on `w1/W1-50-mirror-run2`, read-only for you: never check it out, merge it or cherry-pick from it). On the branch: the design `219e7e33`, its alignment to DEC-437 `38f7a41a`, the engineer's `9f294a9e` (source, 155 lines; **it has no `Role:` trailer: a record, name it**), two designer revisions `36f6b5bb` and `775b0089`. Your predecessor reported every suite green at the old head; that report is not a verification of this head.

## What you do, in this order

**A. Make a write to the real mirror impossible to miss, before any test runs again.** Before and after every test run of yours, and of every worker (tell them), record `stat -c '%Y %n' ~/.local/state/gov-os` and `ls ~/.local/state/gov-os | sort`: the six names and the modification time must be unchanged. If either changes, stop that run's work, find the test by bisection of the suites (never by guessing), and it is fixed before anything else.

**B. Test designer** (`gov launch independent-test-designer DAEO-xnbx`, fresh):
   - audits every acceptance suite that runs `gov pause`, the guard's freeze reading or the containment check on a project (`grep -rl pause tests/acceptance` names W1-02, W1-04, W1-07, W1-28, W1-50; also every case that starts a hook or a launched session, W1-46 and W1-47 among them) and makes each such case run with a throwaway home, in the test's own process and in every subprocess it starts, so that the mirror it writes is under the test's temporary directory; each revised case in another ticket's suite is named in the W1-50 README with the reason "owner decision DEC-429: the freeze mirror; the test's home is a throwaway";
   - adds a tripwire that needs no discipline: `tests/acceptance/conftest.py` (a new file at the top of the acceptance tests; if a file there would change how other suites collect, say so and put it where it is safe), a session-wide automatic fixture that records the real mirror folder's listing and modification time at the start and **fails the session at its end, by name, if either changed**. It reads the folder's listing and time only; it never creates the folder, never removes or opens an entry. The real folder is located from the password database (`pwd.getpwuid(os.getuid()).pw_dir`), not from `HOME`, so a test that changes `HOME` cannot blind it;
   - a case that the tripwire itself works (on a stand-in folder).
   Commit with `Task: DAEO-xnbx` and `Role: independent-test-designer`.

**C. Engineer** (`gov launch engineer DAEO-xnbx`, fresh, a short turn): the same for the unit tests in its paths (`tests/unit/pause`, `guard`, `containment`, `launch`, `install`): every test that runs the pause command or the guard gets a throwaway home (the content of the removed `6b9103b2` is the idea for `tests/unit/pause/test_pause.py`; it is redone by the engineer, not copied by you), and the same tripwire for the unit folders it may write. No source change unless a test shows a defect. **Its commit carries `Role: engineer`; you check it before going on.**

**D. Verify on this head,** every suite to its end, never `-x`, with step A's record around each run: the suites of the brief's step 5 below, plus `tests/acceptance/W1-22`, `W1-24`, `W1-26` only after step E.

**E. Merge-back.** `w1/integrate` has moved a long way (W1-22, W1-24 and W1-26 merged; each of the last two added lines to `tests/acceptance/W1-07/w1_07_support.py`, which this branch also changed, and your designers revised W1-07 and W1-28 cases). Compare the paths under `tests/acceptance` and `.tickets` changed on each side since the merge base. For every path on both lists a test designer first brings this branch's file to hold exactly `w1/integrate`'s version plus this branch's own changes (DEC-412), in its own commit. Then one committing command: `git merge w1/integrate` with `-m` and the trailers `Task: DAEO-xnbx` and `Role: orchestrator`; never `--no-commit` (DEC-436). After it, `git diff --stat w1/integrate HEAD -- tests/acceptance` lists only this round's own files and its own lines in the files it revised; anything else: return PACKAGES saying what you saw and repair nothing. Then verify again, the three newly merged suites included.

**F. One reviewer** (`gov launch independent-auditor DAEO-xnbx`, fresh, read-only, its log under your scratch), with the probes of the brief's step 6 below and one more: any test or code path that can still write to the real mirror, and whether the tripwire can be blinded. Wait for it in the foreground. Fixes after it as the brief says (only a fail-open or a silent change to tests or ticket files; case first, by a test designer).

**G. Return**, as the brief's step 7 says, and also: step A's record for every run (unchanged or what changed), the list of revised cases in other tickets' suites with their reason, and the six stale entries as an item for the owner.

---

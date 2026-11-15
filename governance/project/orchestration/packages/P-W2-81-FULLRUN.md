# P-W2-81-FULLRUN: why W2-81's run on 0.1.0 stopped at A0, the fix, and the full run's options

## 1. What happened
Your operator ran `--mode run` (seed 1324021, the pinned gov of release 0.1.0). In all six repositories
`gov adopt --lite --stage A0` ended with exit 1, so nothing after it ran. The verdict was NOT_READY, with every stage
ABSENT or NOT_BUILT.

## 2. A0's cause (reproduced; no report file and no hidden material opened)
The runner keeps no A0 output (it captures and drops it). I cloned one built repository (`python-app-clean`) into
scratch and ran A0 there, with the runner's own environment and the same pinned gov:

`SHIPPED_FILE_MISSING: template/.gitleaks.toml: Gov OS ships no such file where this gov can find it`

- A0's set-up gives a repository without `.gitleaks.toml` the template's copy (W2-23 S5). MA's assessment reads the
  same file.
- W2-88's S24 (bdbaa37a5, 11-14) routed both reads through one resolver for shipped files. It looks in the Gov OS
  source tree, then in the wheel's `gov/_shipped/`, then in the project's own copy.
- The wheel's package data lists 11 files under `_shipped/`, and `template/.gitleaks.toml` is not among them.
  - From a source tree the file was found, so development runs passed.
  - From the release wheel, only a repository whose kit is installed gets past, because `copier copy` puts
    `.gitleaks.toml` at its root. EXAMIN passed for that reason: your operator installed its kit before A0.
  - W2-81's synthetic repositories carry no kit, so A0 stopped.
- With the file committed in the copy, A0 and A1 pass. A2 then refuses `ADOPT_NO_PATH_MAP`, which is right: there is
  no path map until the kit or A3 gives one.
- A0 refused before writing anything, so the six built repositories are untouched.

**The leaked tmux identity was not involved:**
- The runner builds its environment from nothing. It passes PATH, a fresh HOME and TMPDIR under the run folder,
  LC_ALL, git's config and identity, and `GOV_REBUILD_LOCK`, and nothing else (`w2_81_run.py` `_env`). Its own text
  says it "never uses the dev-tier variable".
- Your operator ran it from a plain terminal.
- The same refusal comes back under `env -i`.

## 3. Why `--mode run` can never be READY by itself
`--mode run` runs only the stages that need no session (A0 to A2). A3 to A10 need sessions: the path map's writer and
the A5, A7 and A10 auditors. The close needs `--close-ticket`. W2-81's real run has three parts (its README, "build",
"read"):
1. build;
2. a launched session adopts each repository, leaving its outputs under `<run>/outputs/<repository>/`;
3. `--mode read`, with `--close-ticket` per repository and `--sets-root`.

The manifests must be walled from the adopting session (`held-out.yaml`, or the guard refusing `<run>/manifests/**`).

## 4. The fix (product)
Ship `template/.gitleaks.toml` in the wheel (`gov/_shipped/template/.gitleaks.toml` and its line in the package data),
plus a unit check that every file the shipped-file resolver is asked for is in the package data. This is
**W2-88 (DAEO-2bdu) reopened within S24's purpose** ("A9 works from an installed release ... from shipped bytes"). S24
made the resolver and moved A0's and MA's read onto it, but never shipped this file.
- Size: about 10 lines and one test.
- Run: STANDARD, with a narrow independent check.
- Delivery: release 0.1.1, beside W2-111's and W2-174's parts.
- What it unblocks: an adopter who starts A0 or MA without the kit. The full run below installs the kit, so it does
  not need this fix.

## 5. The full run's options
- **(a) The full run on release 0.1.0, starting tomorrow morning. Recommended.**
  - **The CTO's preparation tonight:**
    - one operator script (tested on a clone first) that, for each of the six built repositories (seed 1324021,
      untouched), does what EXAMIN's Part A did:
      - installs the kit from v0.1.0 (`--skip .gitignore`);
      - writes `governance/project/held-out.yaml` naming the evaluation sets' root and `<run>/manifests/**`;
      - runs `gov adapters generate` and A0;
      - writes the coordination ticket's fields and creates the A5, A7 and A10 review tickets with their report paths
        (DEC-1188 (1)'s route, so no ticket is written by hand mid-run);
    - the adopting session's brief, for your bytes approval.
  - **Tomorrow:**
    - your operator runs the script, then starts one adopting session (tmux, a clean environment) that takes the six
      repositories through A1 to A10 lite, with fresh auditors at A5, A7 and A10;
    - at the end your operator runs `--mode read` with `--close-ticket` per repository and `--sets-root`, and the
      summary command as before.
  - **Why it is recommended:** it measures 0.1.0, the release W2-27 measures, so W2-28 judges one release (DEC-1178
    (3)(e)).
  - **Cost:**
    - about 20 minutes of your operator's time;
    - the session about 6 to 10 hours: six small repositories and 18 auditor sessions;
    - tokens comparable to W2-27's adoption.
  - **Risk:** medium. A stage refusing in one repository becomes a finding, and the session moves on to the next
    repository.
- **(b) The full run on release 0.1.1,** after W2-174's apply and the gitleaks fix land and 0.1.1 is cut and
  re-pinned. The product makes its own review tickets, so the operator writes no ticket fields. It starts a day or
  more later, measures a release W2-27 did not, and adds a release sitting before it can begin.
- **(c) A smoke check only:** the gitleaks fix, then `--mode run` again. It reaches A2 at most and stays NOT_READY by
  design. Little evidence; not recommended.

## 6. Recommendation
**(a)**, confidence medium-high, with the fix in section 4 for 0.1.1. Classification of the finding: ordinary work
yes (every adopter without the kit), consequence other (a named refusal, nothing written).

**Your line:** `P-W2-81-FULLRUN (a)` (or (b), (c)), plus `W2-88-GITLEAKS-SHIP yes` for section 4's reopen (or no).

---
task: DAEO-0cd2
kind: package (interim, the ticket lead; DEC-1052: an interface not stated in the ticket before the pair starts)
blocks: S12 and F7 only (the weekly secret scan and push, DEC-1182 (2)); S1-S11 go on
---
# PACKAGE W2-187-S12: S12 and F7's interface is not stated in the ticket

**What is missing.** S12 says the push is declared "in the key I11 names", and the CTO's amendment says "I11 names the
key; absent means no push". At 530635305 (w2/integrate merged) I11 names no key, and nothing states where the scan and
push code lives, how gitleaks is called, what is printed, how `cron.log` carries it (I11 fixes "its line's six keys
unchanged"), or the exits. The test designer and the engineer would each have to invent these, so by DEC-1052 they come
back here before the pair starts. Each item below has a recommendation. Answering "as recommended" lets this run take
S12 and F7 at once: about 120-160 lines plus tests.

1. **Where a repository declares its weekly push.**
   - (a) **Recommended:** the cron line's environment, `GOV_MEMAUDIT_PUSH="<remote> <branch>"`, written by the
     repository's owner in the line ACT.md step 6 gives. Absent or empty means no push. There is no new file in the
     repository, and Gov OS (DEC-1182 (1)) declares nothing. Cost: none beyond the wrapper.
   - (b) A committed file, `governance/project/memaudit.yaml` with `push: {remote, branch}`. Cost: a new governed
     file per repository, and an adoption step to write it.
   - (c) git config, `gov.memaudit.push`. Cost: invisible in the tree, so a review cannot see it.
2. **Where the code lives.**
   - (a) **Recommended:** a subcommand `python3 -m gov.memaudit push --sets-root R [--repo D] [--gitleaks EXE]` in a
     new `src/gov/memaudit/push.py`, so `say` stays the only printer and F7's "the module's scan call is the only
     gitleaks call" has one module to scan. The wrapper calls it as its last step, after the fresh cycle.
   - (b) Inline in `memaudit_cron.sh`. Cost: the counts-only rule and the redaction live in bash, harder to test.
3. **The scan.**
   - (a) **Recommended:** run `gitleaks detect --source <repo> --no-banner --redact --report-format json
     --report-path <a 0600 temporary file outside the repository>`. The tool counts the report's entries, then deletes
     the report. Exit 0 is clean; exit 1 with entries is `findings <k>`; any other exit, a timeout
     (`GOV_MEMAUDIT_SCAN_TIMEOUT_S`, default 600) or no binary is `scan failed <reason word>`. `--gitleaks`, else
     `$GOV_MEMAUDIT_GITLEAKS`, else `gitleaks` on PATH.
4. **What is printed and logged** (counts and reason words only, F7).
   - (a) **Recommended:** one stdout line:
     - `PUSH none: no declaration`, exit 0;
     - `PUSH pushed <remote> <branch> <12 hex>`, exit 0;
     - `PUSH blocked: findings <k>`, exit 1;
     - `PUSH blocked: scan failed <word>`, exit 1;
     - `PUSH failed: git push exit <c>`, exit 2 (git's own output kept in a 0600 file in the key folder, never
       printed).

     The same line goes to the cycle's latest `DIGEST.txt` in the key folder as its last line. It also goes to one
     more `cron.log` line with the six keys unchanged and the step named `push`, so I11's line form stays.
5. **Where it runs.** Only in the wrapper's weekly cycle, after the audit steps that ran, and only when a standing or
   fresh step started that cycle. It never runs in `maintain`, at a refresh or at a close. A cycle where nothing was due
   runs neither the scan nor the push.
6. **A9's ACT.md step 6.** The step adds: "The cycle runs the audit and measure, then one gitleaks scan, then
   `git push` only on a clean scan; declare the push with `GOV_MEMAUDIT_PUSH=\"<remote> <branch>\"` on this line; leave
   it out for no push."

**Size.** The ticket's code is already 1447 source insertions against est 700, and the O8 (a) split (S10 and S11 to
W2-187b) was not taken: the designer's estimate was under the trigger, and S10 and S11 were built by then. S12 builds
on S11's wrapper. If the CTO prefers, S12 and F7 can go to a W2-187b with this interface. That needs the owner's P1 for
a new ticket (DEC-974); O8 (a) pre-approved only S10 and S11.

**Recommendation:** items 1-6 as (a). Confidence: medium-high. **What it blocks:** S12 and F7 only.

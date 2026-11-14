#!/usr/bin/env python3
"""DEC-1182: secret scanning and pushes (owner, 2026-11-14 ~16:00), and P-Q02-V2 (b). Run from the repo root on a
clean tree. Edits the register, the DIF, DEC-1045's Changed-by mark, W2-187's ticket (S12, F7, I11 note, sources) and
the DND rows. The EXAMIN CTO brief (scratch) is edited by brief.py beside this file."""
import re


def edit(p, o, n, count=1):
    t = open(p, encoding='utf-8').read()
    assert t.count(o) == count, (p, o[:60], t.count(o))
    open(p, 'w', encoding='utf-8').write(t.replace(o, n))


BASIS = ('"Secret scanning and pushes, my decisions: - Gov OS stays private: no repository scan, at closes or anywhere else. '
         '- EXAMIN will be hosted in the cloud later, so it gets one full gitleaks scan a week, before its weekly push to '
         'GitHub, in the same weekly cycle as the memory audit: audit and measure, then the scan, then the push, only on a '
         'clean scan. No scan at a ticket\'s close or at a store refresh. - The memory store is refreshed on the changes '
         'only, never rebuilt whole after a merge; confirm that is how the refresh works, for EXAMIN and here. - The '
         'guard\'s per-command gitleaks check stays on everywhere. I accept the remaining risk of a key slipping into the '
         'files or the store between weekly scans: this balances practicality against risk. Confirm the check stays '
         'within W2-111\'s 100 ms bound. Apply these to the EXAMIN CTO\'s brief (its scan: on), to W2-187\'s weekly cycle '
         'and to EXAMIN\'s A9 ACT package; record them as a decision, and tell me what changes." (~16:00); "yes q02 '
         'variant v2 7aa6d88c" (~16:03)')

ENTRY = f"""
### DEC-1182 — Secret scanning and pushes: no repository scan on Gov OS; EXAMIN one full gitleaks scan a week before its weekly push, in the memory audit's weekly cycle, never at a close or a refresh; the guard's per-command secret rule stays on; q02's variant version 2
- **Status:** ACCEPTED (owner, 2026-11-14 ~16:00 and ~16:03, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-14)`; (1) to (4) standing) · **Under:** DEC-1045, DEC-1179, DEC-1180, DEC-1181, DEC-1101 (2) · **Changes:** DEC-1045 (1) (its "a full scan runs once a week only when the owner approves it": no repository scan on Gov OS at all); DEC-1180 (2) (q02's variant: version 2, 7aa6d88c, in place of 0703aebf)
- **Decision:**
  - (1) **Gov OS stays private: no repository scan**, at closes or anywhere else, weekly included. Its `secrets.yaml` stays `scan: off` (DEC-1045).
  - (2) **EXAMIN: one full gitleaks scan a week, before its weekly push to GitHub, in the memory audit's weekly cycle:** audit and measure, then the scan, then the push, only on a clean scan. No scan at a ticket's close or at a store refresh: EXAMIN's `secrets.yaml` holds `scan: off` (the one switch that governs the refresh, strict-close and nightly scans, `config/loader.py:427-431`), and the weekly cycle runs gitleaks itself. W2-187 takes the scan and push steps (S12, F7, the CTO within the owner's decision); A9's ACT package's cron line runs that cycle; the push step runs only once the repository declares its remote (EXAMIN's remote is removed at the operator's setup and comes back when it is hosted). The EXAMIN CTO's brief: `secrets.yaml` with `scan: off`, the weekly scan on (the owner's "its scan: on" read as the weekly scan), and no push by the EXAMIN CTO itself.
  - (3) **The guard's per-command secret check stays on everywhere, and the owner accepts the remaining risk** of a key reaching the files or the store between weekly scans. As built, the per-command check is the guard's secret-path rule (`src/gov/guard/reads.py`): reads and writes of secret, key and credential paths are refused by name on every call. It does not run gitleaks on a command. A gitleaks run per command cannot fit 100 ms (a staged scan of a planted repository takes 0.34-0.38 s). The owner's two questions on this (Q-SCAN-1, Q-SCAN-2) went to the owner on 2026-11-14 ~16:15.
  - (4) **The store refresh** is a seeded rebuild (`gov rebuild --seed`, W2-122, `src/gov/rebuild/seed.py`): only files whose content differs from the base are re-embedded and re-checked, while the lexical, graph and other stores are re-derived from the files on every refresh (51-130 s on 11-14). A cold, whole rebuild runs only when the code that builds the stores changes (every re-pin) or no usable base exists. EXAMIN works the same way. This is not yet the owner's "changes only, never rebuilt whole after a merge" for the derived stores; Q-REFRESH-1 went to the owner on 2026-11-14 ~16:15.
  - (5) **`yes q02 variant v2 7aa6d88c` (P-Q02-V2 (b)):** q02's fix runs the self-contained version 2 of the writer variant (sha256 `7aa6d88c3a7769c1abe34ffd54b8ced4f4110fb2208ed1f316d1a7c000b021b6`, independent review PASS, 0 blocking, F1-F8 rows) in place of 0703aebf. The CTO made the launch clone's scaffold 3 (`6325d7ff17a3`); the operator's four commands at W2-94's land carry v2's sha and that commit.
- **Basis:** the owner's messages of 2026-11-14: {BASIS}
- **Governing sources:** DEC-1045 (1); DEC-1179 (5), (6); DEC-1180 (2); DEC-1181 (3); DEC-1101 (2); W2-111 (DAEO-qvff, the 100 ms bound); W2-122 (`gov rebuild --seed`); W2-187 (DAEO-0cd2) S10, S11, I11; `src/gov/config/loader.py:427-431`; `src/gov/rebuild/seed.py`; `src/gov/guard/reads.py`; the CTO's investigation of 2026-11-14 ~16:10.
"""

R = 'docs/DECISION_REGISTER.md'
t = open(R, encoding='utf-8').read()
anchor = "W2-94's lead return (66dd6e77abbd).\n"
assert t.count(anchor) == 1, 'anchor'
t = t.replace(anchor, anchor + ENTRY)
v = re.search(r'^\| 0\.562 \| 2026-11-14 \|.*Next free id: DEC-1182\. \|\n', t, re.M).group(0)
t = t.replace(v, v + '| 0.563 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1182 (no repository scan on Gov OS; '
              'EXAMIN one full gitleaks scan a week before its weekly push, in the memory audit\'s weekly cycle; the guard\'s '
              'per-command secret rule on; q02\'s variant version 2; DEC-1045 (1) and DEC-1180 (2) changed). Next free id: DEC-1183. |\n')
# DEC-1045's Changed-by mark
h = '### DEC-1045 — Gitleaks scanning lifted on this repository'
i = t.index(h)
j = t.index('- **Decision:**', i)
seg = t[i:j]
assert 'Changed by DEC-1182' not in seg
k = t.index('\n', t.index('- **Status:**', i))
t = t[:k] + ' · **Changed by:** DEC-1182 (1) (no repository scan on Gov OS at all, weekly included)' + t[k:]
open(R, 'w', encoding='utf-8').write(t)

D = 'governance/project/orchestration/DECISIONS-IN-FORCE.md'
t = open(D, encoding='utf-8').read()
i = t.index('- DEC-1181 (2026-11-14, (5) standing)')
j = t.index('\n', i)
t = t[:j + 1] + ('- DEC-1182 (2026-11-14, (1)-(4) standing): **no repository scan on Gov OS, anywhere; EXAMIN: one full gitleaks '
                 'scan a week, before its weekly push, in the memory audit\'s weekly cycle (audit and measure, scan, push only on '
                 'a clean scan), never at a ticket\'s close or a store refresh (`secrets.yaml` `scan: off`); the guard\'s '
                 'per-command secret rule stays on everywhere, the risk between weekly scans accepted by the owner.** Basis: '
                 '"Gov OS stays private: no repository scan, at closes or anywhere else ... one full gitleaks scan a week, before '
                 'its weekly push to GitHub ... only on a clean scan. No scan at a ticket\'s close or at a store refresh."\n') + t[j + 1:]
open(D, 'w', encoding='utf-8').write(t)

T = '.tickets/DAEO-0cd2.md'
t = open(T, encoding='utf-8').read()
S12 = ("  - 'S12 The weekly secret scan and push (DEC-1182 (2)): after the weekly audit and measure (the maintenance pass, the "
       "standing run and, when due, the fresh cycle), a repository that declares its weekly push (its remote and branch, in "
       "the key I11 names) gets one full gitleaks scan of the repository, then `git push <remote> <branch>` only when that "
       "scan is clean; a scan that finds anything, fails or cannot run blocks the push and is named in `cron.log` and the "
       "digest by count and reason only; a repository that declares no push (Gov OS, DEC-1182 (1)) skips both steps, named; "
       "no scan runs in the maintenance pass''s refresh. A9''s ACT package''s step 6 names the cycle''s order (audit and "
       "measure, scan, push on a clean scan) and how the repository''s owner declares the push [DEC-1182 (2), DEC-1179 (5), "
       "DEC-1101 (2)] Verify: a planted repository with a declared bare remote and a clean tree is scanned once and pushed "
       "after its audit; a planted secret in a tracked file blocks the push (the remote unchanged) and the log names a count, "
       "never the secret; a failing or missing gitleaks blocks the push, named; a planted repository with no declaration runs "
       "neither step and says so; a planted A9 run''s ACT.md step 6 names the order'\n")
one_s11_end = t.index("  failure:\n")
t = t[:one_s11_end] + S12 + t[one_s11_end:]
F7 = ("  - 'F7 A push after a scan that found anything, failed or did not run; a finding''s text (a secret, a match, a line) in "
      "`cron.log`, the digest, the ACT text or the push''s output; a scan or a push at a refresh, a close or a repository "
      "that declared no push. Verify: S12''s planted runs; the module''s scan call is the only gitleaks call in the cycle'\n")
# failure lines end where the next top-level key starts after F6
f6 = t.index("  - 'F6 ")
end = t.index('\n', f6) + 1
t = t[:end] + F7 + t[end:]
assert t.count('sources: [DEC-1179,') == 1
t = t.replace('sources: [DEC-1179,', 'sources: [DEC-1182, DEC-1179,', 1)
t = t.rstrip('\n') + '\n\n' + (
    "**Amended 2026-11-14 by the CTO within the owner's DEC-1182 (2) (listed for the owner's reading): S12 and F7, the "
    "weekly secret scan and push.** EXAMIN gets one full gitleaks scan a week, before its weekly push, in this weekly "
    "cycle: audit and measure, then the scan, then the push only on a clean scan; never a scan at a close or a refresh "
    "(EXAMIN's `secrets.yaml` holds `scan: off`). I11 gains: the wrapper, after its last audit step, reads the "
    "repository's push declaration (I11 names the key; absent means no push), runs `gitleaks detect` over the repository "
    "once, and pushes only on its exit 0; A9's ACT.md step 6 states that order. The running lead was not told (no "
    "mechanism): its next round takes S12 and F7 with the path case W2-187-P1 (a).") + '\n'
open(T, 'w', encoding='utf-8').write(t)

N = 'governance/project/orchestration/packages/DECIDED-NOT-DONE.md'
t = open(N, encoding='utf-8').read()
row = re.search(r'^\| 209 \|.*$', t, re.M).group(0)
t = t.replace(row, row + '\n' + '\n'.join([
    "| 210 | DEC-1182 (2): EXAMIN's weekly gitleaks scan and push in the memory audit's weekly cycle (W2-187 S12, F7; A9's "
    "ACT step 6); EXAMIN's `secrets.yaml` `scan: off` (the EXAMIN CTO's brief) | IN PROGRESS 11-14: W2-187 amended, the "
    "brief edited; W2-187's next round builds S12 |",
    "| 211 | DEC-1182 (3), (4): Q-SCAN-1 (the per-command check: the path rule, and whether EXAMIN also gets the staged "
    "commit scan), Q-SCAN-2 (the 100 ms bound measured W2-111's way), Q-REFRESH-1 (a seeded rebuild, not changes-only, "
    "for the derived stores) | WAITS on the owner's answers and the measurement |",
    "| 212 | DEC-1182 (5): q02's run with variant v2 at W2-94's land | WAITS on W2-94's land (the four commands) |"]), 1)
open(N, 'w', encoding='utf-8').write(t)
print('ok')

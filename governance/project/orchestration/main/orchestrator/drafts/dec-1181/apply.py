#!/usr/bin/env python3
"""DEC-1181: the owner's answers of 2026-11-14 ~15:40. Run from the repo root, after the land, on a clean tree."""
import re

def edit(p, o, n, count=1):
    t = open(p, encoding='utf-8').read()
    assert t.count(o) == count, (p, o[:60], t.count(o))
    open(p, 'w', encoding='utf-8').write(t.replace(o, n))

BASIS = ('"yes W2-188 adopt skill 6a884cf1 / SETUP-B-OWNER S2 (a), S14 (a), S18 (a); B4 (a) stands as the route for '
         'workers\' ranked search. / yes P-Q02-RUN-1 0703aebf, effective once W2-94\'s review passes and it lands: send my '
         'operator\'s four commands the moment it does. / My operator removes the stale .git/config.lock now. / In every '
         'status block, name each ticket reopened since the last report and why, so the closed count never drops '
         'unexplained."')

ENTRY = f"""
### DEC-1181 — The owner's answers of 2026-11-14 ~15:40: W2-188's adopt-skill bytes approved; set-up B's last three items retired and B4 (a) standing; q02's run at W2-94's land; the stale config lock removed; every status block names each reopened ticket and why
- **Status:** ACCEPTED (owner, 2026-11-14 ~15:40, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-14)`; (5) standing) · **Under:** CAP-33, DEC-1128 (4), DEC-1168 (1), DEC-1179, DEC-1180, DEC-1169 (2)
- **Decision:**
  - (1) **`yes W2-188 adopt skill 6a884cf1`:** the kernel `adopt/SKILL.md` and its two `.rulesync` copies, byte-equal at sha256 `6a884cf1…9489` (version 1.1.0: step 6 makes the Wave 0 verdict set the repository's standing set, judged on DEC-1179's cadence at 95 %, counts only; the weekly cron line comes in A9's ACT package, never installed by adoption), are approved under CAP-33 (CIT-P `docs/changes/W2-188-CIT-P.md`; the CIT-P may change wording only, not these bytes). After W2-187 lands (W2-188's `waits_on`): the owner's approval goes into the CIT-P, the kernel-approved rows are added, W2-188 merges by hand (Task DAEO-zlog), and ACT-CLAUDE-COPIES-12 follows with its own owner line. The CTO's within-purpose calls P-W2-188-S5 (a) and P-C12-1 (a) stand, listed for the owner's reading.
  - (2) **SETUP-B-OWNER S2 (a), S14 (a), S18 (a) (DND row 137):** S2: Wave 3 row W3-P28 (ranked search for sandboxed workers by a socket allowance) is retired; the unranked, named search fallback stays (DEC-1035 (2)). S14: W2-40's three lifted sandbox-measurement lines are retired and its hook time-limit line is kept; W2-40 (DAEO-6ox0) is closed, so its ticket is not edited (DEC-1088 (6)): this entry and SWITCHED-OFF-1's S14 row carry the fact. S18: the scratch folder `drafts/sandbox-exp/` (set-up B's code, never run) was deleted at 15:42; the record branch keeps a copy. **B4 (a) stands as the route for workers' ranked search:** SANDBOX-1-B4 (DEC-1168 (1)), W2-186 (DAEO-sq3a).
  - (3) **`yes P-Q02-RUN-1 0703aebf`, effective once W2-94's review passes and it lands:** the CTO sends the owner's operator the four commands (the variant's install with a `Role: owner` commit, its APPROVED line, the fix-flow launch, `check_gold` expecting 20 of 20), each with its tree check, the moment W2-94 lands. The review passed at `fac8d2026` (`docs/probes/DAEO-g87r/PR-DAEO-g87r-fix.md`, findings P1-P8, all rows); W2-94's land is `66dd6e77abbd`. Its P1 (the walled writer is not given the fixed brief that the variant binds word for word, so a result may be refused with exit 20 and cost a re-run) went to the owner at once as package P-Q02-V2; without another answer, this yes runs version 1 as approved.
  - (4) **The stale `.git/config.lock`** (empty, read-only, 14:08, no holder) is removed by the owner's operator; the guard refuses every session's delete inside `.git`.
  - (5) **Standing: every status block names each ticket reopened since the last report and why**, so the closed count never drops unexplained (with DEC-1169 (2)'s new tickets and their approving decisions). `tools/status_block.py` prints the line itself from the tickets' history since the last report, each with its commit's reason.
- **Basis:** the owner's message of 2026-11-14 ~15:40: {BASIS}
- **Governing sources:** CAP-33; DEC-1035 (2); DEC-1088 (6); DEC-1114 (1); DEC-1128 (4); DEC-1168 (1); DEC-1169 (2); DEC-1178 (5); DEC-1179; DEC-1180 (2), (4); `governance/project/orchestration/packages/SWITCHED-OFF-1.md` S2, S14, S18; W2-94's lead return (66dd6e77abbd).
"""

R = 'docs/DECISION_REGISTER.md'
t = open(R, encoding='utf-8').read()
anchor = '- **Governing sources:** DEC-1178 (1), (5); DEC-1179 (6); DEC-1156 (8); DEC-1157 (12); DEC-974; W2-61h\'s N2 row (lead return 40f997704f53); P-Q02-RUN-1 (chat 13:38).\n'
assert t.count(anchor) == 1
t = t.replace(anchor, anchor + ENTRY)
v = ('| 0.561 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1180 (N2 (b): changed heading-cited sections '
     'listed for the walled writer; P-Q02-RUN-1 (a): a one-question fix flow, W2-94 reopened, run today; the EXAMIN CTO '
     'tonight after the re-pin and the operator\'s setup; standing: no deferral). Next free id: DEC-1181. |\n')
assert t.count(v) == 1
t = t.replace(v, v + '| 0.562 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1181 (W2-188\'s adopt-skill '
              'bytes 6a884cf1 approved; SETUP-B-OWNER S2, S14, S18 (a), B4 (a) standing; P-Q02-RUN-1 run at W2-94\'s land; '
              'the stale config lock removed; standing: each reopened ticket named in every status block). Next free id: DEC-1182. |\n')
open(R, 'w', encoding='utf-8').write(t)

D = 'governance/project/orchestration/DECISIONS-IN-FORCE.md'
t = open(D, encoding='utf-8').read()
i = t.index('- DEC-1180 (2026-11-14, (4) standing)')
j = t.index('\n', i)
t = t[:j + 1] + ('- DEC-1181 (2026-11-14, (5) standing): **every status block names each ticket reopened since the last report '
                 'and why, so the closed count never drops unexplained** (with DEC-1169 (2)\'s new tickets); `tools/status_block.py` '
                 'prints it. Also: W3-P28 and W2-40\'s three lifted sandbox lines retired, B4 (a) (W2-186) the route for '
                 'workers\' ranked search. Basis: "In every status block, name each ticket reopened since the last report and '
                 'why, so the closed count never drops unexplained."\n') + t[j + 1:]
open(D, 'w', encoding='utf-8').write(t)

P = 'docs/plan/WAVE_3_PARKING.md'
edit(P, '| W3-P28 | **A ticket (DEC-1114 (1)).**',
     '| W3-P28 | RETIRED 2026-11-14 (DEC-1181 (2), SETUP-B-OWNER S2 (a): the unranked, named search fallback stays, '
     'DEC-1035 (2); B4 (a), W2-186, is the route for workers\' ranked search): **A ticket (DEC-1114 (1)).**')

S = 'governance/project/orchestration/packages/SWITCHED-OFF-1.md'
t = open(S, encoding='utf-8').read()
for k, note in (('S2', 'retired (W3-P28 marked RETIRED)'),
                ('S14', 'the three lifted lines retired, the hook-limit line kept; W2-40 closed, its ticket not edited (DEC-1088 (6))'),
                ('S18', 'deleted 2026-11-14 15:42')):
    m = re.search(r'^\| %s \|.*$' % k, t, re.M)
    assert m, k
    line = m.group(0)
    t = t.replace(line, line.rstrip().rstrip('|').rstrip() + ' **Owner 2026-11-14: (a), DEC-1181 (2): %s.** |' % note, 1)
open(S, 'w', encoding='utf-8').write(t)

N = 'governance/project/orchestration/packages/DECIDED-NOT-DONE.md'
t = open(N, encoding='utf-8').read()
m = re.search(r'^\| 137 \| (.*?) \| DONE 2026-11-14 except the owner\'s S2, S14, S18 \(asked 11-14\)', t, re.M)
assert m
t = t.replace("| DONE 2026-11-14 except the owner's S2, S14, S18 (asked 11-14)",
              "| DONE 2026-11-14 (the owner's S2, S14, S18: (a), DEC-1181 (2), applied)", 1)
row206 = re.search(r'^\| 206 \|.*$', t, re.M).group(0)
t = t.replace(row206, row206 + '\n' + '\n'.join([
    '| 207 | DEC-1181 (1): W2-188\'s adopt-skill bytes 6a884cf1 approved: owner_approval into the CIT-P, the kernel-approved '
    'rows, the hand merge (Task DAEO-zlog), then ACT-CLAUDE-COPIES-12 with its own owner line | WAITS on W2-187\'s land '
    '(W2-188\'s waits_on) and W2-188\'s P-C12-1 round |',
    '| 208 | DEC-1181 (3): q02\'s run, effective at W2-94\'s land: the operator\'s four commands sent at the land; W2-94 '
    'closes on `check_gold` 20 of 20 | WAITS on W2-94\'s land (66dd6e77abbd) and the owner\'s P-Q02-V2 answer |',
    '| 209 | DEC-1181 (5): each reopened ticket named in every status block | DONE 2026-11-14: `tools/status_block.py` '
    'prints the reopened and new tickets since the last report |']), 1)
open(N, 'w', encoding='utf-8').write(t)
print('ok')

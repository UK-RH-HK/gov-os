#!/usr/bin/env python3
"""DEC-1182 (2) into the EXAMIN CTO's first brief (scratch; backup beside it). Prints the new sha256."""
import hashlib
import shutil

p = '/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/examin-release/EXAMIN-CTO-first-brief.md'
b = open(p, 'rb').read()
assert hashlib.sha256(b).hexdigest().startswith('adbef8c3'), 'not the approved bytes'
shutil.copyfile(p, p + '.approved-adbef8c3')
t = b.decode('utf-8')


def one(o, n):
    global t
    assert t.count(o) == 1, o[:50]
    t = t.replace(o, n)


one("7. **No push, no tag**, and no `sudo`.\n",
    "7. **No push, no tag**, and no `sudo`. EXAMIN's weekly push is not yours: it runs in the weekly memory-audit cycle\n"
    "   that the owner's operator installs from A9's ACT package, after the audit and a clean gitleaks scan (DEC-1182 (2)).\n")
one("   - No `secrets.yaml`, or one with `scan: on`. `gov check` must show the secrets-indexing check measured.\n",
    "   - `governance/project/secrets.yaml` holds `scan: off`: no secret scan at a ticket's close or at a store refresh\n"
    "     (DEC-1182 (2)). EXAMIN's scan is on as one full gitleaks scan a week, in the weekly memory-audit cycle, before its\n"
    "     weekly push; it is not yours to run. `gov check` must show the secrets-indexing check switched off by\n"
    "     configuration, and the guard's secret-path rule still refusing a planted read of a secret path.\n")
open(p, 'w', encoding='utf-8').write(t)
print(hashlib.sha256(t.encode('utf-8')).hexdigest())

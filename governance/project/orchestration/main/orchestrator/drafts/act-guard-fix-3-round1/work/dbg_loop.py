import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bash_writes as bw
from gov.guard.decide import _expand_token, _extract_bash_write_targets
cmd = sys.argv[1] if len(sys.argv) > 1 else "for d in /tmp tests/acceptance/W2-64; do touch $d/t.py; done"
t, _ = bw.heredocs(cmd)
l, _ = bw.lift(t)
print(bw.simples(bw.tokens(l)))
print(bw.variants(l, lambda v, e: v))
j = bw.judge(cmd, "/home/usain/Dynamic-Agentic-Engineering-OS", _extract_bash_write_targets, _expand_token)
print(j.shell, j.findings)

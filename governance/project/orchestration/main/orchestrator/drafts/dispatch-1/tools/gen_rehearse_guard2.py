"""Generates rehearse_guard2.sh from rehearse.sh's frame (sections A) and the guard-2 body. python3 gen_rehearse_guard2.py"""
import os

D = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(D, "rehearse.sh")).read()
s = s.replace("# ACT-DISPATCH-1's rehearsal", "# ACT-IDLE-GUARD-2's rehearsal")
s = s.replace("CL=$RUN/rclone\n", "CL=$RUN/rclone2\n").replace("under /home/usain/gov-os-runs/W2-00/dispatch-1/rclone", "under /home/usain/gov-os-runs/W2-00/dispatch-1/rclone2")
s = s.replace("PH=$D/tmp/home\nACT=$D/acts/ACT-DISPATCH-1\nLOG=$D/rehearsal.log", "PH=$D/tmp/home2\nACT=$D/acts/ACT-IDLE-GUARD-2\nLOG=$D/rehearsal-guard2.log")
s = s.replace("RELS=(governance/project/orchestration/tools/dispatch/dispatcher.py governance/project/orchestration/tools/dispatch/balancer.py tests/unit/orchestration/test_dispatcher.py tests/unit/orchestration/test_balancer.py)\nTESTS=(tests/unit/orchestration/test_dispatcher.py tests/unit/orchestration/test_balancer.py)",
              "RELS=(governance/project/orchestration/tools/stop_idle_check.py tests/unit/orchestration/test_stop_idle_check.py)\nTESTS=(tests/unit/orchestration/test_stop_idle_check.py)")
s = s.replace('chmod -R u+w "${D:?}/tmp/rt" 2>/dev/null; rm -rf "${D:?}/tmp/rt" 2>/dev/null; mkdir -p "$D/tmp/rt"',
              'chmod -R u+w "${D:?}/tmp/rt2" 2>/dev/null; rm -rf "${D:?}/tmp/rt2" 2>/dev/null; mkdir -p "$D/tmp/rt2"').replace('TMPDIR="$D/tmp/rt"', 'TMPDIR="$D/tmp/rt2"')
s = s.replace("checks-dispatch.json", "checks-guard2.json")
assert "tmp/rt2" in s and "checks-guard2.json" in s and 'TMPDIR="$D/tmp/rt"' not in s
head = s[:s.index('echo "--- A. the bundle and the clone"')]
a = s[s.index('echo "--- A. the bundle and the clone"'):s.index('echo "--- B.')]
rest = open(os.path.join(D, "guard2_body.sh")).read()
open(os.path.join(D, "rehearse_guard2.sh"), "w").write(head + a + rest)
print("rehearse_guard2.sh written")

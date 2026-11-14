import sys
sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-130/tests/acceptance/W2-130")
import w2_130_support as s
R = "/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/ref/drafts/"
pa = set()
for n in ("a1-marks-no-hint.patch", "a2-marks-rest.patch"):
    p = s.patch_register_pairs(open(R + n).read(), s.START)
    print(n, len(p))
    pa |= p
c1 = s.committed_pairs(s.FIRST)
print("committed e12", len(c1), "patch", len(pa), "patch-committed", sorted(pa - c1), "committed-patch", sorted(c1 - pa))
c2 = s.committed_pairs(s.SECOND)
p3 = s.patch_register_pairs(open(R + "final/f5-marks.patch").read(), s.parent(s.SECOND))
print("committed c44", len(c2), "f5", len(p3), "f5-c", sorted(p3 - c2), "c-f5", sorted(c2 - p3))
c4 = s.committed_pairs("bce798c3a")
print("bce", sorted(c4))

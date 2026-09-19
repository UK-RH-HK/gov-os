# DERIVED COPY (P2-AR-0037, WS-6 repair round 3) of release/capability-baseline/audit-0/delta-r/evidence/N1-N2-checkpoints.py
# ORIGINAL-PROBE-ID: delta-r/N1-N2-checkpoints
# Changes, and nothing else:
#  1. only line N2.b4 is kept (with the probe's imports, helpers and `q = Proj("n2")`): on the integrated round-2 tree
#     the unedited probe stops before it at its first task close (RECEIPT_INVALID / UNTRACEABLE_IMPLEMENTATION: WS-5
#     BC-P2-20, a discovery task that writes product/ declares nothing it realises), a refusal by design that is not
#     this workstream's.
#  2. the checkpoints the removed lines created before N2.b4 are replaced by one `checkpoint create` (N2.b4 asks
#     whether a significant mutation writes a checkpoint after earlier ones exist); the N2.b4 block itself — 30 new
#     product files, `rebuild-memory --incremental`, the checkpoint count — is byte-for-byte the original's.
"""N1 Structured checkpoint (Contract v3 lines 717-727; framework §59) and N2 Mandatory triggers (lines 729-737; §60).

N1 records: b1 session/role/task/mode/claim  b2 last completed step  b3 next action  b4 pending decisions/questions
            b5 open transactions  b6 files changed  b7 test status  b8 context packet hash  b9 memory snapshot/state reference
N2 triggers: b1 task transition  b2 material decision  b3 accepted CIT  b4 significant mutation  b5 before handoff
             b6 before model/provider switch  b7 before session close  b8 before known compaction

Run:  python3 N1-N2-checkpoints.py > N1-N2-checkpoints.out 2>&1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary, json_file, cit_through, cit_via_cli  # noqa: E402

def ck_count(q):
    return len([f for f in os.listdir(q.path("spec/reports/checkpoints")) if f.startswith("CKPT-")])


def trig_of_latest(q):
    l = q.ok(["checkpoint", "latest"])
    return l.get("trigger") if l else None


q = Proj("n2")
q.ok(["checkpoint", "create", "--next-action", "continue the n2 probe", "--step", "set-up (derived copy)"])
s0 = ck_count(q)
for i in range(30):
    q.write(f"product/bulk_{i}.txt", f"{i}\n")
q.ok(["rebuild-memory", "--incremental"])
s1 = ck_count(q)
check("N2.b4", s1 > s0, "a significant mutation (30 new product files indexed) writes a checkpoint", {"before": s0, "after": s1})
summary()

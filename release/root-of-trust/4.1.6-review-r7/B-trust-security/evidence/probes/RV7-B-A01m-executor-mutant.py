#!/usr/bin/env python3
"""RV7-B-A01m (AR-0020): is RV7-B-A01 an executor defect only? A scratch COPY of the reference executor is mutated so that `accept`
applies every verified revocation statement present in the bundle (as `17` S5 states for running machines), not only those the
selected Trust State lists. Then A01's omitting state is presented (a) with the revocation statement in the bundle, (b) with the
transport withholding it. The sources publish codes, the FCA, the procedure and gov-admit bytes, never revocation statements (`32`
R-FCS-3), so (b) is what a first-install machine behind the transport sees. The committed executor is not modified.
Environment: A01M_SCRATCH, PACK. Output: JSON on stdout."""
import importlib.util, json, os, re, shutil, sys, tempfile
sys.dont_write_bytecode = True
PACK = os.environ["PACK"]
SCR = tempfile.mkdtemp(prefix="a01m-", dir=os.environ["A01M_SCRATCH"])
src_dir = os.path.join(PACK, "evidence", "r7")
mdir = os.path.join(SCR, "mutant")
os.makedirs(mdir)
shutil.copy(os.path.join(src_dir, "w7world.py"), mdir)
code = open(os.path.join(src_dir, "gov_admit_reference_r7.py")).read()
needle = '            if s["digest"] in set(tp.get("revocation_statements", [])):\n'
assert code.count(needle) == 1
open(os.path.join(mdir, "gov_admit_reference_r7.py"), "w").write(code.replace(needle, '            if True:  # AR-0020 mutant: every verified revocation statement held\n'))
sys.path.insert(0, mdir)
import w7world as W  # noqa: E402  (loads the mutant executor beside it)
GA = W.GA
V = GA.Verifier(SCR)
REVOC_R9 = W.envelope("revocation+json", {"revokes": [W.R9.D], "reason": "R9 found malicious after publication (held-out A01)", "issued_at": "2026-09-10T00:00:00Z"}, ["rv1", "rv2"])
b = W.T11["payload"]
T11o = W.tss(11, "2026-09-14T00:00:00Z", W.ROOT2, 2, W.TPS2, W.FCA2, W.PRIOR11, b["registrations"], b["published_binaries"], b["revocations"], revocation_statements=b["revocation_statements"])
res = {"mutant_executor_statement_in_bundle": W.admit(W.R9.binary, W.FCA2, T11o, W.FULL + [REVOC_R9, T11o], verifier=V, workdir=SCR)["result"],
       "mutant_executor_statement_withheld_by_transport": W.admit(W.R9.binary, W.FCA2, T11o, W.FULL + [T11o], verifier=V, workdir=SCR)["result"],
       "mutant_is_the_loaded_executor": "AR-0020 mutant" in open(GA.__file__).read()}
res["verdicts"] = {"executor_fix_refuses_when_the_statement_is_delivered": res["mutant_executor_statement_in_bundle"] == "BINARY_REVOKED",
                   "executor_fix_does_not_close_the_class_when_withheld": res["mutant_executor_statement_withheld_by_transport"] == "ACCEPTED"}
print(re.sub(r"/tmp/[^\"\s]*", "<scratch>", json.dumps(res, indent=1, sort_keys=True)))

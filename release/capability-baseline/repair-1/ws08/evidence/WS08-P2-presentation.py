#!/usr/bin/env python3
"""P2-AR-0020 (WS-8) — BC-P2-36 (presentation/disclosure part): an installation whose authenticity is not established
is never presented as current, verified or certified, and the surfaces disclose it.

Builder evidence (regression, Contract v3 O3). Run against the repaired binary and, as the negative control, against
the base commit's binary:  PROBE_TMP=<scratch> GOV=<gov> python3 WS08-P2-presentation.py

P1  default UNPROVISIONED machine, installs from an unsigned source and from the embedded payload: the command-result
    envelope of every surface, `gov status`, `gov doctor`'s own payload, `gov update --check`, `gov trust status`.
P2  control — PROVISIONED machine, authentic install: presented as CURRENT (the marking-free healthy case of R1).
P3  control — no installation in context (`gov version` outside any project): nothing to present about, CURRENT
    (the R1 hv_b b2/b4 property is preserved).
The doctor VERDICT is recorded as an observation: making it non-HEALTHY needs the doctor check WS-2 owns
(integration point IP-1, `crate::srr::installation::doctor_check`).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ws08_common import *  # noqa

print("## P1 unprovisioned machine")
U = Sandbox("ws08-p2-U")
relU = Releases(U)
r15 = relU.build("r15")
pu = U.new_repo("pu")
oi = U.gov("init", "--source", os.path.join(r15, "kernel"), "--name", "pu", "--alias", "pu-a", "--skip-index", cwd=pu, quiet=True)
print("[P1] init from an unsigned release: ok =", oi.get("ok"), "| authenticity =",
      ((oi.get("result") or {}).get("release_authenticity") or {}).get("authenticity"), "| envelope presented_as =", presented(oi))
surfaces = {}
for args in (["status"], ["doctor"], ["version"], ["gate", "list"], ["kernel", "trust"], ["policy", "overrides"],
             ["update", "--check", "--source", os.path.join(r15, "kernel")]):
    r = U.gov(*args, cwd=pu, quiet=True)
    surfaces[" ".join(args[:2])] = {"presented_as": presented(r), "disclosure": bool((r.get("release_trust") or {}).get("disclosure"))}
surfaces["init"] = {"presented_as": presented(oi), "disclosure": bool((oi.get("release_trust") or {}).get("disclosure"))}
w("P1a", all(v["presented_as"] == "UNAUTHENTICATED" and v["disclosure"] for v in surfaces.values()),
  "no command-result envelope presents the unauthenticated installation as current, and each carries the disclosure", surfaces)
st = U.gov("status", cwd=pu, quiet=True).get("result") or {}
rt = st.get("release_trust") or {}
w("P1b", rt.get("verified_release") is None and rt.get("verified_payload_hash") is None and rt.get("authenticity") == "UNKNOWN",
  "`gov status` makes no `verified_release` claim for an install this machine never verified", rt)
d = U.gov("doctor", cwd=pu, quiet=True)
dres = d.get("result") or (d.get("error") or {}).get("details") or {}
drt = dres.get("release_trust") or {}
w("P1c", drt.get("presented_as") == "UNAUTHENTICATED" and drt.get("disclosure"),
  "`gov doctor`'s own report discloses that authenticity is not established", {"presented_as": drt.get("presented_as"), "disclosure": drt.get("disclosure")})
o("P1c-verdict", f"doctor verdict = {dres.get('verdict')}; a doctor CHECK that fails on it is WS-2's to add (IP-1: crate::srr::installation::doctor_check)")
ts = U.gov("trust", "status", quiet=True).get("result") or {}
inst = ts.get("installations") or []
w("P1d", ts.get("installed_release") is None and any(i.get("authenticity") == "UNKNOWN" for i in inst),
  "`gov trust status` reports no verified release, and lists the installation with authenticity UNKNOWN",
  {"installed_release": ts.get("installed_release"), "installations": inst})
ck = U.gov("update", "--check", "--source", os.path.join(r15, "kernel"), cwd=pu, quiet=True).get("result") or {}
w("P1e", ck.get("certification") != "CERTIFIED" and "nothing to do" != ck.get("recommendation") and "not established" in str(ck.get("recommendation")),
  "`gov update --check` neither calls the installation certified nor says there is nothing to do",
  {"certification": ck.get("certification"), "up_to_date": ck.get("up_to_date"), "recommendation": ck.get("recommendation")})
pe = U.new_repo("pe")
oe = U.gov("init", "--name", "pe", "--alias", "pe-a", "--skip-index", cwd=pe, quiet=True)
se = U.gov("status", cwd=pe, quiet=True)
w("P1f", presented(se) == "UNAUTHENTICATED", "the embedded payload (the README path) on an unprovisioned machine is not presented as current either", presented(se))

print("\n## P2 control: provisioned machine, authentic install")
P = Sandbox("ws08-p2-P")
provision(P)
relP = Releases(P)
rp = relP.build("r15")
kp = relP.sign(rp, sequence=10)
pp = P.new_repo("pp")
P.gov("init", "--source", kp, "--name", "pp", "--alias", "pp-a", "--skip-index", cwd=pp, quiet=True)
got = {" ".join(a): presented(P.gov(*a, cwd=pp, quiet=True)) for a in (["status"], ["doctor"], ["version"], ["gate", "list"])}
w("P2a", all(v == "CURRENT" for v in got.values()), "an authenticated installation on a provisioned machine is presented as current", got)

print("\n## P3 control: no installation in context")
nowhere = U.path("not-a-project")
os.makedirs(nowhere, exist_ok=True)
v = U.gov("version", cwd=nowhere, quiet=True)
w("P3a", presented(v) == "CURRENT" and not (v.get("release_trust") or {}).get("disclosure"),
  "a command that acts on no installation says nothing about one (R1 hv_b b2/b4 preserved)", v.get("release_trust"))
summary()

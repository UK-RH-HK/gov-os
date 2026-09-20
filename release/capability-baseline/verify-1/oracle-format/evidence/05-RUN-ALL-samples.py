#!/usr/bin/env python3
"""P2-AR-0045 RUN-ALL: drive `gov oracle validate` over every labelled sample.

valid/*   must be ACCEPTED.
invalid/* must be REFUSED with a typed error code; the Contract v3 element the refusal names is printed.
Score-report samples are additionally cross-checked against samples/valid/oracle.json (the binding layer).
Run from the repository root. One PASS/FAIL line per sample; exit 0 only if every expectation held.
"""
import glob, json, os, subprocess, sys

GOV = "target/release/gov"
ROOT = "release/capability-baseline/verify-1/oracle-format/samples"
ORACLE = f"{ROOT}/valid/oracle.json"
REPORT_PREFIXES = ("v4-", "arith-", "outcome-", "bind-")


def is_report(name):
    return os.path.basename(name).startswith(REPORT_PREFIXES) or "score-report" in name


def run(path):
    cmd = [GOV, "--json", "oracle", "validate", path]
    if is_report(path):
        cmd += ["--oracle", ORACLE]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(p.stdout or p.stderr)
    except Exception:
        return {"ok": False, "error": {"code": "NO_JSON", "message": (p.stdout + p.stderr)[:300]}}


def describe(env):
    err = env.get("error") or {}
    code = err.get("code", "?")
    det = err.get("details") or {}
    vs = det.get("violations") or []
    first = ""
    if vs:
        v = vs[0]
        first = f'{v.get("at","")} :: {v.get("problem","")[:90]}'
        if v.get("element"):
            first += f' [{v["element"]}]'
    elif det.get("findings"):
        f = det["findings"][0]
        first = f'{f.get("at","")} :: {f.get("problem","")[:90]}'
    else:
        first = err.get("message", "")[:110]
    return code, len(vs), first


fails = 0
total = 0
for path in sorted(glob.glob(f"{ROOT}/valid/*.json")) + sorted(glob.glob(f"{ROOT}/invalid/*.json")):
    total += 1
    want_ok = "/valid/" in path
    env = run(path)
    got_ok = bool(env.get("ok"))
    name = os.path.relpath(path, ROOT)
    if want_ok and got_ok:
        print(f"PASS  accepted   {name}")
    elif (not want_ok) and (not got_ok):
        code, n, first = describe(env)
        print(f"PASS  refused    {name}  -> {code} ({n} violation(s)) {first}")
    else:
        fails += 1
        code, n, first = describe(env)
        print(f"FAIL  {'accepted' if got_ok else 'refused '}   {name}  -> {code} {first}")

print()
print(f"{total} samples, {total - fails} as expected, {fails} unexpected")
sys.exit(1 if fails else 0)

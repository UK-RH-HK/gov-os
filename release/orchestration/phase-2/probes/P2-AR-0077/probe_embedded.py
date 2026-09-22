#!/usr/bin/env python3
"""P2-AR-0077: bound the class behind E1/E2 -- an absolute path that is not the
WHOLE token.

`token_values()` yields the token and, if it contains `=`, the right-hand side.
`leaves_project()` then tests `starts_with('/')`, `starts_with('~')`, a drive
letter, or a whole `..` SEGMENT; `resolves_outside_project()` otherwise joins the
token's segments under the root. So an absolute path behind ANY prefix character
(`@`, `%output{`, `file://`, `+`, `:`) is read as a relative in-project path.

Classification only -- nothing here is executed against a real network host.
"""
import json
from harness4 import fresh, descriptor, install, save

p = fresh("embedded")
p.write("payload.txt", "x\n")
rows = []
n = 0


def classify(name, argv, note=""):
    global n
    n += 1
    tool = f"TOOL-EMB-{n:02d}"
    d = descriptor(None, install_cmd=argv, tool_id=tool)
    d.pop("security_review_record", None)
    e = install(p, d, f"emb-{name}", execute=False)
    r = e.get("result") or (e.get("error") or {}).get("details") or {}
    cc = r.get("change_class") or {}
    env = cc.get("authority_envelope") or {}
    row = {"shape": name, "argv": argv, "note": note,
           "expands_authority": env.get("expands_authority"),
           "triggers": env.get("triggers_fired"),
           "undetermined_count": len(env.get("undetermined") or []),
           "network_endpoints": env.get("network_endpoints") or cc.get("network_endpoints"),
           "SEEN_AS_ESCAPE": bool(env.get("expands_authority"))}
    rows.append(row)
    print(f"{'GATES ' if row['SEEN_AS_ESCAPE'] else 'CLEAN '}{name:34s} {argv}")
    return row


ABS = "/etc/hostname"
classify("bare-absolute", ["cp", "payload.txt", ABS], note="control: a bare absolute path IS caught")
classify("at-prefixed", ["curl", "-d", "@" + ABS, "https://pypi.org/simple/"],
         note="curl's @file convention: read the POST body from a host file")
classify("writeout-brace", ["curl", "-w", "%%output{%s}X" % ABS, "https://pypi.org/simple/"],
         note="curl --write-out %output{<abs>}: write to a host file")
classify("file-url", ["curl", "-o", "out.txt", "file://" + ABS],
         note="a file:// URL with an empty authority")
classify("FILE-url-upper", ["curl", "-o", "out.txt", "FILE://" + ABS], note="uppercase scheme")
classify("file-url-upload", ["curl", "-T", "payload.txt", "file://" + ABS],
         note="upload INTO a host path")
classify("colon-prefixed", ["curl", "-o", "out.txt", "x:" + ABS], note="any prefix at all")
classify("equals-rhs", ["curl", "--output-dir=" + ABS, "https://pypi.org/simple/"],
         note="the `=` right-hand side IS split out by token_values -- should be caught")
classify("netrc-file", ["curl", "--netrc-file", ABS, "https://pypi.org/simple/"],
         note="a plain path operand -- should be caught")
classify("file-url-relative-dotdot", ["curl", "-o", "out.txt", "file://../x"],
         note="a .. segment inside the URL -- should be caught lexically")

save("embedded", rows)
clean = [r for r in rows if not r["SEEN_AS_ESCAPE"]]
print(f"\n=== {len(clean)}/{len(rows)} shapes classify with NO authority expansion ===")
for r in clean:
    print("  ", r["shape"])

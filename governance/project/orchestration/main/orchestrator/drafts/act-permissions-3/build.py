#!/usr/bin/env python3
"""Builds ACT-PERMISSIONS-3's bundle (the operator's form: manifest.json, apply.sh, list.txt, before/, after/, and
rehearsal.log once the rehearsal has run). The live settings file is only read.

    python3 build.py            before/, after/, list.txt  (and the manifest, without a rehearsal, if there is no log)
    python3 build.py --seal     also the manifest with rehearsal.log's sha256 (after rehearse.py)

The change is a text insertion, so the diff is exactly the comma on the last allow line and the two new lines.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE / "act" / "ACT-PERMISSIONS-3"
LIVE = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.claude/settings.local.json")
REL = ".claude/settings.local.json"
NEW = ["Edit(//tmp/gov-os-emg-*/**)", "Read(//tmp/gov-os-emg-*/**)"]
# The project's own deny list (.claude/settings.json) names Edit(**/*.key), Edit(**/*.pem) and Edit(**/.env*): these are
# the same names under the allowed folders, for Edit and for Read (a deny rule wins over every allow).
DENY = [f"{tool}(//tmp/gov-os-emg-*/**/{name})" for tool in ("Edit", "Read") for name in ("*.key", "*.pem", ".env*")]
sha = lambda b: hashlib.sha256(b).hexdigest()

before_bytes = LIVE.read_bytes()
text = before_bytes.decode()
data = json.loads(text)
allow = data["permissions"]["allow"]
assert not any(r in allow for r in NEW), "already applied"
last = allow[-1]
anchor = f'      "{last}"\n    ],\n    "deny"'
assert text.count(anchor) == 1, "the allow list's end is not where the insertion expects it"
insert = f'      "{last}",\n' + "".join(f'      "{r}"' + (",\n" if i < len(NEW) - 1 else "\n") for i, r in enumerate(NEW)) \
    + '    ],\n    "deny"'
after_text = text.replace(anchor, insert)
deny = data["permissions"]["deny"]
assert not any(r in deny for r in DENY), "deny already applied"
anchor2 = f'      "{deny[-1]}"\n    ],\n    "additionalDirectories"'
assert after_text.count(anchor2) == 1, "the deny list's end is not where the insertion expects it"
insert2 = f'      "{deny[-1]}",\n' + "".join(f'      "{r}"' + (",\n" if i < len(DENY) - 1 else "\n") for i, r in enumerate(DENY)) \
    + '    ],\n    "additionalDirectories"'
after_text = after_text.replace(anchor2, insert2)
after = json.loads(after_text)
expected = json.loads(text)
expected["permissions"]["allow"] = allow + NEW
expected["permissions"]["deny"] = deny + DENY
assert after == expected and list(after["permissions"]) == list(data["permissions"])

(BUNDLE / "before/repo/.claude").mkdir(parents=True, exist_ok=True)
(BUNDLE / "after/repo/.claude").mkdir(parents=True, exist_ok=True)
(BUNDLE / "before/repo" / REL).write_bytes(before_bytes)
(BUNDLE / "after/repo" / REL).write_bytes(after_text.encode())
b, a = sha(before_bytes), sha(after_text.encode())
(BUNDLE / "list.txt").write_text(f"repo|{REL}|{b}|{a}\n")

n_allow, n_deny = len(allow), len(data["permissions"]["deny"])
dirs = data["permissions"]["additionalDirectories"]
check0 = ("python3 -I -c 'import json,sys; p=json.load(open(\".claude/settings.local.json\"))[\"permissions\"]; "
          "a=p[\"allow\"]; "
          f"sys.exit(0 if a[-2:]==[\"{NEW[0]}\",\"{NEW[1]}\"] and len(a)=={n_allow + 2} "
          f"and p[\"deny\"][-6:]=={json.dumps(DENY)} and len(p[\"deny\"])=={n_deny + 6} "
          f"and len(p[\"additionalDirectories\"])=={len(dirs)} "
          "and not any(x.startswith(\"Write(\") or \"//tmp/**\" in x for x in a) else 1)'")
check1 = "python3 -I -m json.tool .claude/settings.local.json > /dev/null"
manifest = {
    "act": "ACT-PERMISSIONS-3",
    "dec": "DEC-1126",
    "author": "cto",
    "claimed_class": "b",
    "touched": [{"root": "repo", "path": REL, "before": b, "after": a}],
    "files": {
        f"before/repo/{REL}": b,
        f"after/repo/{REL}": a,
        "apply.sh": sha((BUNDLE / "apply.sh").read_bytes()),
        "list.txt": sha((BUNDLE / "list.txt").read_bytes()),
    },
    "checks": [{"cmd": check0, "exit": 0, "count": None}, {"cmd": check1, "exit": 0, "count": None}],
    "commands": [],
}
log = BUNDLE / "rehearsal.log"
if "--seal" in sys.argv:
    assert log.is_file(), "no rehearsal.log: run rehearse.py first"
    manifest["files"]["rehearsal.log"] = sha(log.read_bytes())
    manifest["rehearsal"] = {"log": "rehearsal.log", "sha256": sha(log.read_bytes())}
(BUNDLE / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
print(f"before {b[:12]}  after {a[:12]}  allow {n_allow} -> {n_allow + 2}  sealed: {'--seal' in sys.argv}")
print("manifest sha256", sha((BUNDLE / "manifest.json").read_bytes()))

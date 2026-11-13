"""W2-157's three gate.json entries (docs/changes/W2-157-evidence.md lines 47-49; DEC-1067, DEC-1068 (4); DEC-1142 (10)).
python3 -I <this file> check | apply. The machine's own file ~/.gov-os/machine/gate.json, class (O), the owner's operator.
'check' exits 0 only when none of the three keys is present and the file parses; 'apply' adds exactly the three keys, every other
key unchanged, keeps a copy as gate.json.pre-W2-157, writes by a temporary file and a rename, and parses the result."""
import json
import os
import shutil
import sys
import tempfile

P = os.path.expanduser("~/.gov-os/machine/gate.json")
ADD = {
    "gpu_backstop_limit_mib": {"value": 15872, "date": "2026-11-04",
                               "source": "DEC-1067 (GPU safety), DEC-1068 (4): 15.5 GiB, 15,872 MiB"},
    "gpu_backstop_every_s": {"value": 5, "date": "2026-11-04",
                             "source": "DEC-1067 (GPU safety), DEC-1068 (4): the poll every 5 seconds"},
    "gpu_backstop_embedders": {"value": [{"port": 11434, "log": "/home/usain/.ollama/serve-11434.log"},
                                         {"port": 11435, "log": "/home/usain/.ollama/serve-11435.log"}],
                               "date": "2026-11-04",
                               "source": "DEC-1067 (GPU safety), DEC-1068 (4), DEC-1030: the two shared embedding servers and their logs"},
}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    data = json.load(open(P, encoding="utf-8"))
    have = [k for k in ADD if k in data]
    if have:
        print(f"gatejson: REFUSED: already present: {have}")
        sys.exit(3)
    if mode == "check":
        print(f"gatejson: ready ({len(data)} keys now; 3 to add)")
        return
    shutil.copy2(P, P + ".pre-W2-157")
    new = dict(data)
    new.update(ADD)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(P), prefix=".gate-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=2)
        f.write("\n")
    os.chmod(tmp, os.stat(P).st_mode)
    os.replace(tmp, P)
    back = json.load(open(P, encoding="utf-8"))
    assert all(back[k] == v for k, v in ADD.items()) and all(back[k] == data[k] for k in data)
    print(f"gatejson: applied ({len(back)} keys; the old file kept as gate.json.pre-W2-157)")


main()

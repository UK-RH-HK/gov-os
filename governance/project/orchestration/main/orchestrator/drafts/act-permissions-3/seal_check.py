"""After the seal: the operator's own code, read only, over the sealed bundle."""
import hashlib, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/operator")
import act_class, operator_run
B = Path(sys.argv[1])
m = json.loads((B / "manifest.json").read_text())
operator_run.validate_manifest(m)
operator_run.path_rule(str(B), m, {"repo": "/home/usain/Dynamic-Agentic-Engineering-OS", "home": str(Path.home())})
bad = [k for k, v in m["files"].items() if hashlib.sha256((B / k).read_bytes()).hexdigest() != v]
print("validate_manifest ok; path rule ok; files not hashing as listed:", bad)
c = act_class.classify(str(B))
print("class", c["class"], [(f["root"], f["path"], f["row"]) for f in c["files"]], "hits", c["hits"])
print("rehearsal sha ok:", m["rehearsal"]["sha256"] == hashlib.sha256((B / "rehearsal.log").read_bytes()).hexdigest())
print("manifest sha256", hashlib.sha256((B / "manifest.json").read_bytes()).hexdigest())

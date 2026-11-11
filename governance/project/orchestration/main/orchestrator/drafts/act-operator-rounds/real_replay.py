"""Read-only: the new G4 count over the live operator's frozen copies (acts/*/review.md and manifest.json are only read)."""
import os, re, sys
sys.dont_write_bytecode = True
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, "after_pkg"))
import importlib.util
def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
sys.path.insert(0, os.path.join(H, "clone/governance/project/operator"))
run = load("operator_run_new", os.path.join(H, "clone/governance/project/operator/operator_run.py"))
vm = load("verdict_new", os.path.join(H, "clone/governance/project/operator/verdict.py"))
root = os.path.expanduser("~/gov-os-operator")
acts = sorted(os.listdir(os.path.join(root, "acts")))
for n in acts:
    act = re.sub(r"-[0-9a-f]{12}$", "", n)
    r = run.Run({"operator_root": root}, act, "0" * 64, (None, None, None, {}))
    r.frozen = os.path.join(root, "acts", n)
    text = open(os.path.join(r.frozen, "review.md"), encoding="utf-8").read()
    blocks = vm.BLOCK.findall(text)
    ok, why = vm.ready(text)
    print(f"{act:28} builds={sum(1 for x in acts if re.sub(r'-[0-9a-f]{12}$','',x)==act)} own_blocks={len(blocks)} act_rounds={r.act_rounds(vm, blocks)} ready_new={ok} {why}")

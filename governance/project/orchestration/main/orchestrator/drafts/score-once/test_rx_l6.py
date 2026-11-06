"""L6 in the score-once harness copy (DEC-1079 L6, D4B-SCORE-ONCE v7): ``work_tier`` puts the named paths one tier
step below the default, the other tiers as the path map reads them. No model, no reranker, no store, no GPU, no
``gov retrieve``; a made-up path map only, and no evaluation set is read.

    python3 test_rx_l6.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RX = HERE / "rx.py"
CLONE_SRC = Path.home() / "gov-os-runs/D4B/g1/repo/src"
RESULTS: list[bool] = []

CHILD = r'''
import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("rx_l6", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
from gov.retrieval import authority
root = Path(sys.argv[2])
order = authority.order(root, [], [], lambda p, s: None)
paths = json.loads(sys.argv[3])
print(json.dumps({p: order.steps(p, 1) for p in paths}))
'''

PATHS = ["docs/contract/a.md", "docs/plan/b.md", "docs/close/W2-1.md", "governance/project/orchestration/reviews/r.md",
         "tests/unit/test_x.py", "docs/changes/W2-1-evidence.md"]


def report(name: str, passed: bool, detail: str = "") -> None:
    RESULTS.append(bool(passed))
    print(f"{'ok  ' if passed else 'FAIL'} {name}{': ' + detail if detail and not passed else ''}")


def child(root: Path, home: Path, variant: dict):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
    env.update({"HOME": str(home), "GOV_RX_NO_MAIN": "1", "GOV_RX": json.dumps(variant),
                "GOV_RX_CACHE": str(home / "cache"), "PYTHONPATH": str(CLONE_SRC)})
    got = subprocess.run([sys.executable, "-c", CHILD, str(RX), str(root), json.dumps(PATHS)], env=env,
                         capture_output=True, text=True, timeout=120)
    if got.returncode != 0:
        return None, got
    return json.loads(got.stdout.strip().splitlines()[-1]), got


def tree(base: Path, tiers: str) -> Path:
    root = base / "root"
    (root / "governance/project").mkdir(parents=True)
    (root / "governance/project/path-map.yaml").write_text(
        "retrieval_authority:\n  lift: {fused: 0.004, rerank: 1.0}\n  default: middle\n  tiers:\n" + tiers)
    return root


TIERS = ("    - name: governing\n      paths: ['docs/contract/**']\n    - name: middle\n"
         "    - name: reports\n      paths: ['tests/**']\n")
WORK = ["docs/close/**", "governance/project/orchestration/reviews/**"]

with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    (base / "home/cache").mkdir(parents=True)
    root = tree(base, TIERS)
    off, got = child(root, base / "home", {"depth": 40})
    report("1 absent: the path map's tiers (governing +1, middle 0, reports -1, the rest 0)",
           off == {"docs/contract/a.md": 1, "docs/plan/b.md": 0, "docs/close/W2-1.md": 0,
                   "governance/project/orchestration/reviews/r.md": 0, "tests/unit/test_x.py": -1,
                   "docs/changes/W2-1-evidence.md": 0}, f"{off} {got.stderr[-400:]}")
    on, got = child(root, base / "home", {"depth": 40, "work_tier": WORK})
    report("2 work_tier: the named paths one step below the default, every other path as before",
           on == {**(off or {}), "docs/close/W2-1.md": -1, "governance/project/orchestration/reviews/r.md": -1},
           f"{on} {got.stderr[-400:]}")
    report("3 reports keep their step (-1), not pushed lower", (on or {}).get("tests/unit/test_x.py") == -1)

with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    (base / "home/cache").mkdir(parents=True)
    root = tree(base, "    - name: governing\n      paths: ['docs/contract/**']\n    - name: middle\n")
    none, got = child(root, base / "home", {"depth": 40, "work_tier": WORK})
    report("4 no tier below the default: refused, not silently ignored",
           none is None and "work_tier needs a tier below the default" in (got.stderr + got.stdout),
           got.stderr[-400:])

print(f"{sum(RESULTS)} of {len(RESULTS)} passed")
sys.exit(0 if all(RESULTS) else 1)

"""The lead's check against today's code (W2-87): with the block absent, the bundle at the base's code and at the
head's code is the same, item for item, on the planted repository of the acceptance tests.

Run: python3 check_today.py <workdir>. Each side runs through a checkout's src/ on PYTHONPATH (DEC-877).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-87/tests/acceptance/W2-87")
import w2_87_support as support  # noqa: E402

SIDES = {"base": Path("/home/usain/gov-os-runs/W2-87/base/src"),
         "head": Path("/home/usain/gov-os-worktrees/W2-87/src")}
work = Path(sys.argv[1])
work.mkdir(parents=True, exist_ok=True)
api = support.Api(work / "api")
support.SRC = SIDES["head"]
root = support.build_project(work / "repo", support.ABSENT)
api.build(root)
superseded_root = support.build_project(work / "repo-superseded-last", support.ABSENT,
                                        support.SUPERSEDED_LAST_REGISTER_TEXT)
api.build(superseded_root)

CALLS = [(support.PHRASE, {}, ()), (support.PHRASE, {}, (support.FAVOURED,)),
         (support.CUT_PHRASE, {"batch_size": 2}, ()), (support.CUT_PHRASE, {"batch_size": 1}, (support.FAVOURED,)),
         (support.UNRELATED, {}, ()), (support.PHRASE, {"bundle_budget": 40}, ())]
for name, tree in (("register-last-accepted", root), ("register-last-superseded", superseded_root)):
    same = []
    for query, kwargs, favour in CALLS:
        bundles = {}
        for side, src in SIDES.items():
            support.SRC = src
            bundles[side] = api.retrieve(tree, query, favour=favour, **kwargs)
        equal = json.dumps(bundles["base"], sort_keys=True) == json.dumps(bundles["head"], sort_keys=True)
        same.append(equal)
        print(f"{name} | {query!r} {kwargs} favour={list(favour)} | items base {len(bundles['base']['evidence'])} "
              f"head {len(bundles['head']['evidence'])} | identical: {equal}")
        if not equal:
            print("   base:", [(e["path"], e["start_line"]) for e in bundles["base"]["evidence"]],
                  bundles["base"]["merge"]["dropped"])
            print("   head:", [(e["path"], e["start_line"]) for e in bundles["head"]["evidence"]],
                  bundles["head"]["merge"]["dropped"])
    print(f"{name}: {sum(same)} of {len(same)} identical")

"""For each marks commit: gov links --all on the commit's tree with the marks it appends taken off (as the cases'
variant_findings does); print committed pairs and which are flagged text. Writes rec/variants.json."""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-130/tests/acceptance/W2-130")
import w2_130_support as s

OUT = Path("/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/rec")
TMP = Path("/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/tmp/variants")
HOME = Path("/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/empty-home")
res = {}
for c in sys.argv[1:]:
    sha = s.full(c)
    d = TMP / sha[:12]
    shutil.rmtree(d, ignore_errors=True)
    d.parent.mkdir(parents=True, exist_ok=True)
    tree = s.make_clone(d, sha)
    (tree / s.REGISTER).write_text(s.variant_register(sha), encoding="utf-8")
    s.commit_all(tree, "variant")
    f = s.links_json(tree, HOME)
    um = s.by_pair(f)
    committed = sorted(s.committed_pairs(sha))
    text = sorted(k for k, v in um.items() if v.get("text"))
    res[sha] = {"committed": committed, "text_flagged": text,
                "committed_text": sorted(set(committed) & set(text)),
                "committed_not_flagged": sorted(set(committed) - set(um)),
                "marks": {f"{m['changed']}<-{m['changer']}": um.get((m['changed'], m['changer']), {}).get("mark") for m in s.added_marks(sha)},
                "tails": {f"{m['changed']}<-{m['changer']}": m["tail"] for m in s.added_marks(sha)}}
    print(c, "committed", len(committed), "committed&text", res[sha]["committed_text"], "not flagged", len(res[sha]["committed_not_flagged"]))
    shutil.rmtree(d, ignore_errors=True)
(OUT / "variants.json").write_text(json.dumps(res, indent=1))

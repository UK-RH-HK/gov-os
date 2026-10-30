"""Builds the two ACT versions of the path map from the base's path map (never commits anything).

ACT-1: the project-overlay namespace gains governance/project/records/** (before the merge).
ACT-2: the four moved lists, with their comments, leave the path map (after the merge and the re-pin).
Usage: python3 make_act.py <base path-map file> <out folder>
"""
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
lines = src.read_text(encoding="utf-8").split("\n")

anchor = '      - "governance/project/prompts/**"'
assert lines.count(anchor) == 1, "anchor"
at = lines.index(anchor) + 1
act1 = lines[:at] + ['      # DEC-941 item 5 (W2-78): the moved lists, record files of their own',
                     '      - "governance/project/records/**"'] + lines[at:]
(out / "path-map.act1.yaml").write_text("\n".join(act1), encoding="utf-8")


def drop_block(ls, key, comment_start):
    """Removes the comment lines that start at `comment_start` and the list under `key` (to the next top-level line)."""
    k = next(i for i, l in enumerate(ls) if l == key or l.startswith(key + " "))
    c = next(i for i, l in enumerate(ls) if l.startswith(comment_start))
    assert c < k and all(l.startswith("#") for l in ls[c:k]), key
    e = k + 1
    while e < len(ls) and (ls[e].startswith(" ") or ls[e] == ""):
        if ls[e] == "":
            break
        e += 1
    return ls[:c] + ls[e:]


act2 = list(act1)
act2 = drop_block(act2, "accepted_history:", "# Commits after the base that the trailer gate")
act2 = drop_block(act2, "acceptance_exemptions:", "# Commits that W1-01's MR-3 history case accepts")
act2 = drop_block(act2, "accepted_reds:", "# gov close's owner-accepted known reds")
act2 = drop_block(act2, "load_sensitive:", "# gov close's named load-sensitive tests")
act2.insert(next(i for i, l in enumerate(act2) if l.startswith("close_timeout:")) - 2,
            "# The four owner-committed lists (accepted_history, acceptance_exemptions, accepted_reds, load_sensitive)\n"
            "# live in record files of their own under governance/project/records/ (DEC-941 item 5, W2-78).")
(out / "path-map.act2.yaml").write_text("\n".join(act2), encoding="utf-8")
print("act1 lines", len(act1), "act2 lines", len(act2))

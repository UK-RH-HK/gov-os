"""The planted test of code_route_counts.py: a fake sets root, a fake clone and fake kept outputs in the measures' own
layout (E0's runs/w4-e0/r80 and r60, the fresh 80's runs/fresh-80/attempt-1/kept), with every count worked out by
hand below. Nothing of ~/gov-os-eval is read.

    ~/.local/share/gov-os/pin-bcea09060ebc/bin/python -I test_planted.py [--work <empty folder>]

Checks: (1) every printed count equals the hand count; (2) no question id, question text, answer or sets-root path
is printed; (3) a kept output left over is refused; (4) a session the sets measure is refused; (5) a clone at another
commit is refused. Exit 0 when all pass.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "code_route_counts.py"
TEXT = "x" * 40


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def item(path, a, b, routes):
    return {"path": path, "start_line": a, "end_line": b, "text": TEXT, "routes": routes, "chunk_id": f"{path}:{a}"}


def out(evidence, facets=None, routing=None, continuation=None, stopping="SATURATED"):
    f = {"lexical": {"available": True}, "semantic": {"available": True}}
    f.update(facets or {})
    result = {"stopping_reason": stopping, "evidence": evidence, "facets": f, "continuation": continuation,
              "rerank": {"by": "service"}}
    if routing is not None:
        result["routing"] = routing
    return json.dumps({"ok": True, "result": result})


CODE_ON = {"code": {"available": True, "reason": None}}
CODE_OFF = {"code": {"available": False, "reason": "the code index is missing"}}
MOD, REC = "src/pkg/mod.py", "docs/rec.md"


def question(qid, category, path, lines):
    return (f"id: {qid}\nquestion: 'PLANTEDTEXT {qid} which function calls it?'\ngold_answer: 'GOLDTEXT {qid}'\n"
            f"category: {category}\nsources:\n  - path: {path}\n    lines: [{lines[0]}, {lines[1]}]\n")


def build(work: Path) -> dict:
    clone, sets, e0out = work / "clone", work / "sets", work / "e0out"
    write(clone / MOD, "".join(f"line {n}\n" for n in range(1, 41)))
    write(clone / REC, "".join(f"rec {n}\n" for n in range(1, 41)))
    git = ["git", "-C", str(clone)]
    subprocess.run(["git", "init", "-q", str(clone)], check=True)
    subprocess.run(git + ["add", "."], check=True)
    subprocess.run(git + ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "planted"], check=True)
    head = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()

    ev = "fixtures/evaluation"
    write(sets / "governance/project/path-map.yaml", (
        "evaluation_sets:\n"
        f"  memory-retrieval:\n    visible: [{ev}/memory-retrieval/visible/**]\n"
        f"    hidden: [{ev}/memory-retrieval/hidden/**]\n    measures: {{roles: [independent-auditor]}}\n"
        f"  memory-verdict:\n    hidden: [{ev}/memory-verdict/hidden/**]\n    measures: {{roles: [independent-auditor]}}\n"
        f"  memory-verdict-2:\n    hidden: [{ev}/memory-verdict-2/hidden/**]\n"
        "    measures: {roles: [independent-auditor]}\n"))
    write(sets / ev / "memory-retrieval/visible/QSECRETV1.yaml", question("QSECRETV1", "callers", MOD, (10, 12)))
    write(sets / ev / "memory-retrieval/hidden/QSECRETH1.yaml", question("QSECRETH1", "plain", REC, (1, 5)))
    write(sets / ev / "memory-verdict/hidden/QSECRETM1.yaml", question("QSECRETM1", "callers", MOD, (10, 12)))
    write(sets / ev / "memory-verdict/hidden/QSECRETM2.yaml", question("QSECRETM2", "nonexistent-id", REC, (30, 31)))
    write(sets / ev / "memory-verdict-2/hidden/QSECRETF1.yaml", question("QSECRETF1", "callers", MOD, (5, 8)))
    write(sets / ev / "memory-verdict-2/hidden/QSECRETF2.yaml", question("QSECRETF2", "plain", MOD, (36, 40)))
    write(sets / ev / "memory-verdict-2/hidden/QSECRETF3.yaml", question("QSECRETF3", "nonexistent-id", REC, (30, 31)))

    r80, r60 = sets / "runs/w4-e0/r80", sets / "runs/w4-e0/r60"
    # V1 (callers): gold at rank 2 by the code route alone; 3 items, 2 by code (1 alone); code hit routed ahead
    write(r80 / "00001.json", out([item(REC, 1, 3, ["lexical"]), item(MOD, 9, 14, ["code"]),
                                   item(MOD, 20, 25, ["lexical", "code"])], CODE_ON, {"code": ["c1"]}))
    # H1 (plain): gold at rank 1, lexical and semantic; no code facet
    write(r80 / "00002.json", out([item(REC, 2, 4, ["lexical", "semantic"]), item(MOD, 1, 5, ["semantic"])]))
    write(e0out / "r80/measure.txt", "families: none\ntotal: hit@5 2 of 2 (100.0 %, floor 85); full evidence ...\n")
    # M1 (callers): first gold at rank 2 by lexical; a later gold by lexical and code; 3 items, 2 by code (1 alone)
    write(r60 / "00001.json", out([item(MOD, 30, 35, ["code"]), item(MOD, 10, 12, ["lexical"]),
                                   item(MOD, 12, 13, ["lexical", "code"])], CODE_ON))
    # M2 (nonexistent-id): the stated gap, empty, its code facet unavailable
    write(r60 / "00002.json", out([], CODE_OFF, stopping="UNRESOLVED_IDS"))
    write(e0out / "r60/measure.txt", "families: none\ntotal: hit@5 1 of 2 (50.0 %, floor 85); full evidence ...\n")

    att = sets / "runs/fresh-80/attempt-1"
    kept = att / "kept"
    # F1 (callers): gold at rank 6 by the code route alone (not within five); 6 items, 1 by code
    write(kept / "00001.json", out([item(REC, 10, 12, ["lexical"]), item(REC, 13, 14, ["semantic"]),
                                    item(REC, 15, 16, ["lexical"]), item(REC, 17, 18, ["lexical"]),
                                    item(REC, 19, 20, ["lexical"]), item(MOD, 5, 8, ["code"])], CODE_ON))
    # F2 (plain): two calls; the first holds no code item and no facet; the second a gold by semantic and code
    write(kept / "00002.json", out([item(REC, 1, 2, ["lexical"])], continuation="tok1"))
    write(kept / "00003.json", out([item(REC, 1, 2, ["lexical"]), item(MOD, 36, 38, ["semantic", "code"])],
                                   CODE_ON))
    # F3 (nonexistent-id): empty
    write(kept / "00004.json", out([], stopping="UNRESOLVED_IDS"))
    write(att / "measure.txt", "families: none\ntotal: hit@5 1 of 3 (33.3 %, floor 85); full evidence ...\n")
    write(att / "DONE", "x\n")
    write(sets / "runs/fresh-80/COUNTS", "attempt-1\n")
    return {"clone": clone, "sets": sets, "e0out": e0out, "head": head, "kept": kept}


# the hand counts: (line beginning, value)
WANT = {
    "-- the 138, all its questions": [
        ("  questions:", "4"),
        ("  the code route asked (its facet in the first call's bundle):", "3 (75.0 %)"),
        ("    of which its facet unavailable:", None),
        ("  the routing put a code hit ahead (code_first):", "1 (25.0 %)"),
        ("  the bundle (first call) holds a code-route item:", "2 (50.0 %)"),
        ("  the stacked context holds a code-route item:", "2 (50.0 %)"),
        ("  a gold-matching item in the stacked context (any route):", "3 (75.0 %)"),
        ("  the first gold-matching item came by the code route (code among its routes):", "1 (25.0 %)"),
        ("    the same, by the code route alone:", None),
        ("    the same, and within the first five (hit@5 by the code route):", "1 (25.0 %)"),
        ("  some gold-matching item came by the code route:", "2 (50.0 %)"),
        ("  the code route's share of bundle items (first call):", "4 of 8 (50.0 %); by the code route alone: 2 (25.0 %)"),
        ("  the code route's share of stacked items:", "4 of 8 (50.0 %); by the code route alone: 2 (25.0 %)"),
        ("    callers:", "2; 2; 1; 1; 1; 2"),
        ("    nonexistent-id:", "1; 0; 0; 0; 0; 0"),
        ("    plain:", "1; 0; 0; 0; 0; 0"),
    ],
    "-- the 80, all its questions": [
        ("  questions:", "3"),
        ("  the code route asked (its facet in the first call's bundle):", "1 (33.3 %)"),
        ("  the bundle (first call) holds a code-route item:", "1 (33.3 %)"),
        ("  the stacked context holds a code-route item:", "2 (66.7 %)"),
        ("  a gold-matching item in the stacked context (any route):", "2 (66.7 %)"),
        ("  the first gold-matching item came by the code route (code among its routes):", "2 (66.7 %)"),
        ("    the same, and within the first five (hit@5 by the code route):", "1 (33.3 %)"),
        ("  some gold-matching item came by the code route:", "2 (66.7 %)"),
        ("  the code route's share of bundle items (first call):", "1 of 7 (14.3 %); by the code route alone: 1 (14.3 %)"),
        ("  the code route's share of stacked items:", "2 of 8 (25.0 %); by the code route alone: 1 (12.5 %)"),
        ("    callers:", "1; 1; 1; 1; 0; 1"),
        ("    plain:", "1; 0; 1; 0; 1; 1"),
        ("    nonexistent-id:", "1; 0; 0; 0; 0; 0"),
    ],
    "-- the 80, without the category nonexistent-id (scored apart)": [
        ("  questions:", "2"),
        ("  the first gold-matching item came by the code route (code among its routes):", "2 (100.0 %)"),
    ],
}


def block(lines, title):
    i = lines.index(title)
    end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith(("-- ", "== "))), len(lines))
    return lines[i + 1:end]


def run(p, env_role="orchestrator", commit=None):
    env = {k: v for k, v in os.environ.items() if k not in ("GOV_ROLE", "GOV_TICKET", "PYTHONPATH")}
    env["GOV_ROLE"] = env_role
    done = subprocess.run([sys.executable, "-I", str(SCRIPT), "--sets-root", str(p["sets"]), "--clone",
                           str(p["clone"]), "--commit", commit or p["head"], "--e0-out", str(p["e0out"])],
                          capture_output=True, text=True, env=env)
    return done.returncode, done.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work")
    a = ap.parse_args()
    work = Path(a.work) if a.work else Path(tempfile.mkdtemp(prefix="code-route-planted-"))
    work.mkdir(parents=True, exist_ok=True)
    if any(work.iterdir()):
        sys.exit(f"the work folder is not empty: {work}")
    p = build(work)
    fails = []
    code, text = run(p)
    lines = text.splitlines()
    print(text)
    if code != 0:
        fails.append(f"exit {code}")
    for title, want in WANT.items():
        if title not in lines:
            fails.append(f"missing block: {title}")
            continue
        got = block(lines, title)
        for start, value in want:
            line = next((x for x in got if x.startswith(start)), None)
            if line is None:
                fails.append(f"{title}: no line {start!r}")
            elif value is not None and line[len(start):].strip() != value:
                fails.append(f"{title}: {start!r} gave {line[len(start):].strip()!r}, want {value!r}")
    for word in ("QSECRET", "PLANTEDTEXT", "GOLDTEXT", str(p["sets"]), "fixtures/evaluation"):
        if word in text:
            fails.append(f"printed something it must not: {word[:20]}")
    if "the measure's recorded total 2 of 2 (the same)" not in text or "recorded total 1 of 3 (the same)" not in text:
        fails.append("the recorded totals were not checked as the same")
    if text.count("first gold rank as the measure scores it: ") != 3 or "WARNING" in text:
        fails.append("the rebuilt ranks did not agree with the measure's")

    write(p["kept"] / "00005.json", out([]))  # (3) a kept output left over
    code, text = run(p)
    if code != 2 or "REFUSED: the measure refused memory-verdict-2" not in text or "QSECRET" in text:
        fails.append(f"a left-over kept output was not refused: exit {code}: {text[-200:]}")
    (p["kept"] / "00005.json").unlink()
    code, text = run(p, env_role="independent-auditor")  # (4) a measured session
    if code != 2 or "REFUSED" not in text:
        fails.append(f"a measured session was not refused: exit {code}")
    code, text = run(p, commit="0" * 40)  # (5) another commit
    if code != 2 or "REFUSED: the clone is at" not in text:
        fails.append(f"a clone at another commit was not refused: exit {code}")
    print("PLANTED TEST:", "PASS" if not fails else "FAIL")
    for f in fails:
        print("  -", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())

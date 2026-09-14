#!/usr/bin/env python3
"""RV6-B-A03 — generated consequence statements versus the calculator's own atoms (review r6 reviewer B, AR-0016).
Computed. Scratch only for part 3 (a copy of the pack directory); the repository is never written.

Instruments, loaded by path and NOT modified:
  * `release/root-of-trust/4.1.6/evidence/r6/CS6-derivation-calculator.py` (functions `compact`, `atoms_for`, `ATOMS`);
  * the committed calculator output `evidence/r6/CS6-derivation-calculator.json` (`minimal_sets_table`, `statements`);
  * `release/root-of-trust/4.1.6/decision-register/statements_check.py`, executed on a scratch copy of the pack.

Question. `29` §5.5 and `21` state that every consequence statement is a generated calculator block and that
`statements_check.py` fails if a block differs or a hand-written set is not a computed minimal set. Does the rendered text say
what the calculator computed?

  1  `compact()` on minimal sets holding the atom `repo` (A2, the repository writer delivers a release) and on sets holding a
     reproducer key.
  2  Every G_CONTENT configuration of the committed `minimal_sets_table`: sets containing `repo`; whether any G_CONTENT
     configuration has a reproducer atom at all; rows of the generated CONTENT block that print "reproducer key".
  3  `statements_check.py` on a scratch copy of the pack with one hand-written line appended to `21-OWNER-OPTIONS.md`
     outside every block: (i) the set as rendered ("… 1 reproducer key …"), (ii) the same set naming `repo`.

Environment: REVIEW_REPO (export of 4106885), SCRATCH. Output: JSON on stdout.
"""
import importlib.util, json, os, re, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
PK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
SCR = tempfile.mkdtemp(prefix="a03-", dir=os.environ["SCRATCH"])

spec = importlib.util.spec_from_file_location("cs6", os.path.join(PK, "evidence", "r6", "CS6-derivation-calculator.py"))
CS6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS6)
committed = json.load(open(os.path.join(PK, "evidence", "r6", "CS6-derivation-calculator.json")))
out = {"probe": "RV6-B-A03 generated statement rendering (AR-0016)"}

# 1
examples = {
    "repo_set": ["regk1", "regk2", "va1", "repo", "ts", "rc", "rf"],
    "reproducer_key_set": ["regk1", "regk2", "va1", "rep1", "ts", "rc", "rf"],
    "use_row_pipeline": ["regk1", "regk2", "va1", "repo", "pipeline", "ts"],
}
out["part1_compact"] = {k: {"set": v, "rendered": CS6.compact(v)} for k, v in examples.items()}
out["part1_repo_and_rep1_render_identically"] = CS6.compact(examples["repo_set"]) == CS6.compact(examples["reproducer_key_set"])

# 2
table = committed["minimal_sets_table"]
content_keys = [k for k in table if k.startswith("G_CONTENT|")]
rows_with_repo, rows_with_rep = 0, 0
repo_sets = []
for k in content_keys:
    for s in table[k]:
        members = s.split(" + ")
        if "repo" in members:
            rows_with_repo += 1
            if len(repo_sets) < 6:
                repo_sets.append({"configuration": k, "set": members, "rendered": CS6.compact(members)})
        if any(re.fullmatch(r"(rep|rp)\d", m) for m in members):
            rows_with_rep += 1
cfg_example = {"reg": "root", "V": 1, "repro": "n2q2", "victim": "USE", "fc": "-", "op4": "sep", "tc": "accept", "env": "a"}
out["part2"] = {
    "G_CONTENT_configurations": len(content_keys),
    "G_CONTENT_minimal_sets_containing_repo": rows_with_repo,
    "G_CONTENT_minimal_sets_containing_a_reproducer_atom": rows_with_rep,
    "G_CONTENT_atoms_for_USE_victim": CS6.atoms_for("G_CONTENT", cfg_example),
    "examples": repo_sets,
}
content_block = committed["statements"]["CONTENT"]
block_rows = [l for l in content_block.splitlines() if l.startswith("| root") or l.startswith("| delegated")]
rep_rows = [l for l in block_rows if "reproducer key" in l]
out["part2"]["CONTENT_block_rows"] = len(block_rows)
out["part2"]["CONTENT_block_rows_printing_reproducer_key"] = len(rep_rows)
out["part2"]["CONTENT_block_rows_printing_reproducer_key_examples"] = rep_rows[:2]
placed = {}
for root, _, files in os.walk(PK):
    for f in files:
        if f.endswith(".md"):
            p = os.path.join(root, f)
            t = open(p).read()
            for m in re.finditer(r"<!-- CS6:BEGIN CONTENT -->(.*?)<!-- CS6:END CONTENT -->", t, re.S):
                placed[os.path.relpath(p, PK)] = placed.get(os.path.relpath(p, PK), 0) + m.group(1).count("reproducer key")
out["part2"]["pack_files_with_CONTENT_block_and_count_of_reproducer_key_mentions"] = placed

# 3
copy = os.path.join(SCR, "pack")
shutil.copytree(PK, copy)
def run_check(extra_line):
    target = os.path.join(copy, "21-OWNER-OPTIONS.md")
    base = open(os.path.join(PK, "21-OWNER-OPTIONS.md")).read()
    open(target, "w").write(base + "\n" + extra_line + "\n")
    env = {"PATH": "/usr/bin:/bin", "HOME": SCR, "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-B", os.path.join(copy, "decision-register", "statements_check.py"), "--pack", copy], capture_output=True, text=True, env=env)
    try:
        j = json.loads(r.stdout)
    except Exception:
        j = {"raw": r.stdout[-400:]}
    s2 = j.get("checks", {}).get("S2", j.get("S2"))
    return {"line": extra_line, "exit": r.returncode, "S2": s2 if s2 is not None else {k: v for k, v in j.items() if k != "instrument"}}
out["part3_as_rendered"] = run_check("Hand-written (review probe): USE under OP-2 (a), OP-8 = 1 needs {2 registration keys, 1 verification key, 1 reproducer key, ts, rc, rf}.")
out["part3_true_atom"] = run_check("Hand-written (review probe): USE under OP-2 (a), OP-8 = 1 needs {2 registration keys, 1 verification key, repo, ts, rc, rf}.")
out["part3_control_unchanged_pack_exit"] = subprocess.run([sys.executable, "-B", os.path.join(PK, "decision-register", "statements_check.py"), "--pack", PK],
                                                         capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "HOME": SCR, "PYTHONDONTWRITEBYTECODE": "1"}).returncode

out["verdicts"] = {
    "repo_rendered_as_reproducer_key": out["part1_repo_and_rep1_render_identically"],
    "no_G_CONTENT_configuration_has_a_reproducer_atom": out["part2"]["G_CONTENT_minimal_sets_containing_a_reproducer_atom"] == 0,
    "CONTENT_block_prints_reproducer_key": out["part2"]["CONTENT_block_rows_printing_reproducer_key"] > 0,
    "statements_check_S1_passes_the_unchanged_pack_whose_CONTENT_block_prints_reproducer_key": out["part3_control_unchanged_pack_exit"] == 0,
    "statements_check_S2_rejects_the_block_text_when_written_outside_a_block": out["part3_as_rendered"]["exit"] != 0,
    "statements_check_S2_accepts_the_true_atom_form_outside_a_block": out["part3_true_atom"]["exit"] == 0,
}
txt = json.dumps(out, indent=1, sort_keys=True)
txt = txt.replace(SCR, "<scratch>").replace(REPO, "<export>")
print(txt)

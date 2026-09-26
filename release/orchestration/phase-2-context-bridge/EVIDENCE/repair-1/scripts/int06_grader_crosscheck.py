"""BR-AR-0028 check 6 (BR-DAG-AMEND-R1-3 + GD-7) as an evidence run, using the SAME synthetic generators as
tests/integration/test_repair1_integration.py (so the committed synthetic inputs are exactly what the tests grade).

Writes EVIDENCE/repair-1/synthetic-grading/{syn-oracle,syn-queries,syn-state,syn-answers}.yaml (all synthetic, CX-*/SYN-*
ids over the compile fixture repo), then runs, as subprocesses of the real CLIs:
  (1) DEMONSTRATION/oracle-tools/check_oracle.py <syn-oracle> --queries <syn-queries> --state <syn-state> --require-binding
  (2) govbridge demo grade  --packet <fixture main packet>                       (the D-2 scoping / PENDING_RUBRIC check)
  (3) govbridge demo grade  --packet <fixture main> --packet <fixture supplementary packet>   (D-5 / G1 over supplementary)
  (4) govbridge demo grade  --packet <REAL CONTROL-A seed0> --packet <its supplementary/CA-WHY>  (the same, real view)
Usage: $PY int06_grader_crosscheck.py <scratch_dir> <real_seed0_dir>
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

D = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(D))
sys.path.insert(0, str(D / "tests" / "integration"))
sys.path.insert(0, str(D / "tests" / "fixtures" / "compile"))
PY = sys.executable


def run(argv, env=None):
    r = subprocess.run(argv, capture_output=True, text=True, cwd=str(D), env=env)
    return r.returncode, r.stdout, r.stderr


def main():
    scratch, real_seed0 = Path(sys.argv[1]), Path(sys.argv[2])
    scratch.mkdir(parents=True, exist_ok=True)
    os.environ["GOVBRIDGE_STORE"] = str(scratch / "isolated-store")
    import test_repair1_integration as T
    tmp = Path(tempfile.mkdtemp(prefix="int06-", dir=str(scratch)))
    repo, ts, main_pkt, reg = T._compile_fixture_packet(tmp)
    supp = T._supplementary_packet(tmp, ts, repo.c2)
    out_dir = D / "EVIDENCE" / "repair-1" / "synthetic-grading"
    paths = T._write_synthetic_grading_inputs(out_dir, repo.c2)
    print(f"# synthetic inputs (committed): {sorted(Path(p).name for p in paths.values())}")
    print(f"# fixture repo {repo.root} c2={repo.c2}; main packet {main_pkt}; supplementary packet {supp}")
    rc, o, e = run([PY, str(D / "DEMONSTRATION" / "oracle-tools" / "check_oracle.py"), paths["oracle"],
                    "--queries", paths["queries"], "--state", paths["state"], "--require-binding"])
    print(f"## (1) check_oracle.py --require-binding -> exit {rc}\n{o}{e[-500:]}")
    env = dict(os.environ)
    base = [PY, "-m", "govbridge", "demo", "grade", "--oracle", paths["oracle"], "--answers", paths["answers"],
            "--queries", paths["queries"], "--repo", str(repo.root)]
    rc, o, e = run(base + ["--packet", str(main_pkt)], env=env)
    try:
        rep = json.loads(o)
        ch = rep["gates"]["G4_chains"]["chains"][0]["stages"]
        s = {x["stage"]: x for x in ch}
        print(f"## (2) demo grade, main packet only -> exit {rc}; verdict {rep['verdict']}; G1 {rep['gates']['G1_packet_validity']['result']}")
        print(f"   D-2: stage_01 fact present={s['stage_01']['must_state'][0]['present']} (its own claim states it); "
              f"stage_03 fact present={s['stage_03']['must_state'][0]['present']} (text only in stage_02's claim -> judged absent)")
        print(f"   every stage must_state_ok: {sorted({m['must_state_ok'] for x in ch for m in x['must_state']})}; "
              f"query-bound (G5 SYN-Q1) must_state_ok: {rep['gates']['G5_query_classes']['per_query'][0]['must_state_ok']}; "
              f"G8 control must_state_ok: {[q.get('must_state_ok') for q in rep['gates']['G8_controls'].get('per_query', [])]}")
        print(f"   G7: {json.dumps({k: rep['gates']['G7_no_dumping'][k] for k in ('result', 'packet_bytes', 'corpus_bytes', 'problems')})}")
    except Exception as exc:
        print(f"## (2) demo grade main only -> exit {rc}; unparsable: {exc}; stderr tail {e[-800:]}")
    rc, o, e = run(base + ["--packet", str(main_pkt), "--packet", str(supp)], env=env)
    print(f"## (3) demo grade, main + one supplementary packet (fixture) -> exit {rc}; stdout {len(o)} bytes; stderr tail:\n{e[-700:]}")
    env_real = dict(os.environ)
    env_real["GOVBRIDGE_STORE"] = os.environ.get("REAL_STORE", "")
    real_supp = real_seed0 / "supplementary" / "CA-WHY"
    rc, o, e = run([PY, "-m", "govbridge", "demo", "grade", "--oracle", paths["oracle"], "--answers", paths["answers"],
                    "--queries", paths["queries"], "--packet", str(real_seed0), "--packet", str(real_supp)], env=env_real)
    print(f"## (4) demo grade, REAL CONTROL-A seed0 + its supplementary/CA-WHY -> exit {rc}; stderr tail:\n{e[-700:]}")
    rc, o, e = run([PY, "-m", "govbridge", "demo", "grade", "--oracle", paths["oracle"], "--answers", paths["answers"],
                    "--queries", paths["queries"], "--packet", str(real_seed0)], env=env_real)
    try:
        rep = json.loads(o)
        g7 = rep["gates"]["G7_no_dumping"]
        print(f"## (5) demo grade, REAL CONTROL-A seed0 ONLY (its 5 supplementary/ packets present on disk) -> exit {rc}; "
              f"G1 {rep['gates']['G1_packet_validity']['result']}; G7 packet_bytes {g7['packet_bytes']} (main packet.md only: "
              f"{(real_seed0 / 'packet.md').stat().st_size}); corpus_bytes {g7['corpus_bytes']}; G7 result {g7['result']}")
    except Exception as exc:
        print(f"## (5) unparsable: {exc}; stderr {e[-500:]}")


if __name__ == "__main__":
    main()

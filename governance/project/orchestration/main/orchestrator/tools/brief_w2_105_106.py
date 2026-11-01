"""DEC-966: run-1 lead briefs for W2-105 and W2-106."""
import pathlib, subprocess
O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
ACC = "tests/" + "acceptance"
for w2, tid, prof, paths, srcs, est in [
    ("W2-105", "DAEO-zpdj", "STANDARD", f"template/.rulesync/permissions.jsonc, and the test designer's {ACC}/W2-105/", "DEC-966, DEC-172, DEC-957, DEC-965", "about 10 lines, about 2 hours"),
    ("W2-106", "DAEO-0mtg", "FULL", f"template/governance/kernel/settings.json, template/.rulesync/hooks.jsonc, tests/unit/hooks/test_w2_106*, and the test designer's {ACC}/W2-106/", "DEC-966, DEC-822, DEC-957, DEC-965, DEC-801", "about 60 lines, about 4 to 6 hours")]:
    r = subprocess.run(["python3", str(O / "tools/build_lead_brief.py"), str(O / f"briefs/{w2}-part-run1.md"), str(O / f"briefs/{w2}-A5-run1.md"),
                        f"ID={tid}", f"W2={w2}", f"PROFILE={prof}", "PATHS=" + paths, "ROWS=none", "SOURCES=" + srcs, "IMPL=DEC-966", "EST=" + est], capture_output=True, text=True)
    t = (O / f"briefs/{w2}-A5-run1.md").read_text()
    print(w2, r.returncode, r.stderr.strip()[:200], len(t), t.count("@@"))

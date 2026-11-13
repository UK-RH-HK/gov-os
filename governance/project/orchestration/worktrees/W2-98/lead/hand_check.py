"""Lead's hand checks of check_spec.py on planted specs (W2-98 run 3). Writes only under /tmp/gov-os-lead-W2-98/hand."""
import shutil
import subprocess
import sys
from pathlib import Path

CHECK = "/home/usain/gov-os-worktrees/W2-98/template/governance/kernel/skills/spec-writing/check_spec.py"
FORM = "/home/usain/gov-os-worktrees/W2-98/template/governance/kernel/skills/spec-writing/spec-form.md"
ROOT = Path("/tmp/gov-os-lead-W2-98/hand")
shutil.rmtree(ROOT, ignore_errors=True)
ROOT.mkdir(parents=True)

HEAD = "| source | kind | owner | licence or recipe | privacy | secrets | hidden half | secured |\n|---|---|---|---|---|---|---|---|\n"
ROW_OK = "| public repos | imported | Ana, steward | MIT | none | none; scanned | yes | yes |\n"
ROW_SYN = "| twelve questions | synthetic | Bo, lead | written by hand | none | none | n/a | yes |\n"


def spec(kpis="- K1: A member sees the welcome page, e.g. after sign-up, within 1.5 seconds (or less).\n  Fails if: no page.\n",
         rows=ROW_OK + ROW_SYN, drop=()):
    parts = {"Problem": "Members are confused.", "Users and scenarios": "- Dana registers.", "Goals": "- Clarity.",
             "Non-goals": "- Payments.", "KPIs": kpis, "Test data": HEAD + rows, "Out of scope": "- Training.",
             "Open questions": "- Question: x?\n  - Options: a (cost: b)\n  - Recommendation: a", "Accepted by": "- Sam."}
    return "# T\n\n" + "\n".join(f"## {k}\n\n{v}\n" for k, v in parts.items() if k not in drop)


def run(name, text, *extra):
    p = ROOT / name
    p.write_text(text, encoding="utf-8")
    r = subprocess.run([sys.executable, CHECK, *extra, str(p)], capture_output=True, text=True)
    print(f"--- {name}: exit {r.returncode}\n{r.stdout.strip()}{r.stderr.strip()}")
    return r


run("clean.md", spec())
run("prose.md", spec(kpis="- K1: The sign-up page, i.e. the first one, loads for forty-eight members (all of them).\n  Fails if: it does not.\n- K2: A member reads version 2.0 of the terms.\n  Fails if: they cannot.\n"))
for i, k in enumerate(["`send()`", "send_welcome( is called", "src/app/signup.py runs", "account.create fires",
                       "send_welcome runs", "Node.js serves it", "the option(s) appear"]):
    run(f"code{i}.md", spec(kpis=f"- K1: A member sees it.\n  Fails if: no.\n- K2: {k}.\n  Fails if: no.\n"))
run("nofails.md", spec(kpis="- K1: A member sees it.\n- K2: Another.\n  Fails if: no.\n"))
run("wrapped.md", spec(kpis="- K1: A member sees it when\n  send_welcome runs.\n  Fails if: no.\n"))
run("noowner.md", spec(rows="| public repos | imported |  | MIT | none | none | yes | yes |\n"))
run("nohidden.md", spec(rows="| public repos | imported | Ana | MIT | none | none |  | yes |\n"))
r = run("unsec.md", spec(rows=ROW_OK + "| scraped chats | imported | Ana | unknown | personal data | may hold tokens | yes | no |\n"))
print("P1 files:", sorted(x.name for x in ROOT.glob("*.P1.md")))
run("missing2.md", spec(drop=("Problem", "Test data")))
run("nonetable.md", spec(rows="").replace(HEAD, "No data is needed.\n"))
run("form.md", Path(FORM).read_text(encoding="utf-8"))

# imports
f = ROOT / "imp"
f.mkdir()
(f / "a.md").write_text("text <!-- imported: alpha --> and <!-- imported: beta --> and <!-- imported: <part> -->\n")
(f / "imports.yaml").write_text("imports:\n  - part: alpha\n    source: x\n    version: '1'\n    licence: MIT\n"
                                "  - part: beta\n    source: y\n    version: '2'\n    licence: GPL-3.0\n")
subprocess.run([sys.executable, CHECK, "--imports", str(f)])
(f / "imports.yaml").write_text("imports:\n  - {part: alpha, source: x, version: '1', licence: MIT}\n")
print("flow-style record:")
subprocess.run([sys.executable, CHECK, "--imports", str(f)])
shutil.rmtree(ROOT)

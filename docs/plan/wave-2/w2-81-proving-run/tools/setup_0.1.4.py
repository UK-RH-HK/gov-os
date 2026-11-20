#!/usr/bin/env python3
"""W2-81's full re-run on release 0.1.1 (DEC-1197 (3), DEC-1202): the owner's operator's set-up of the six built
repositories (built first by `w2_81_run.py --mode build --seed 1324021`).

Run from a plain terminal (no GOV_* variable):
    python3 -I <this file> --run /home/usain/gov-os-runs/W2-81/run-0.1.1      (--run is required: DEC-1196 (5))
For each repository under <run>/repos/ (seed 1324021, each still at its recorded head), as EXAMIN's Part A did:
  1. governance/project/held-out.yaml: the evaluation sets' root, the workbench, and this run's manifests and reports;
  2. the kit from tag v0.1.1 by `copier copy --skip .gitignore` (nothing the repository has is overwritten),
     then `gov adapters generate`; one commit;
  3. `gov adopt --lite --stage A0` (it creates the coordination ticket and the roster key);
  4. the coordination ticket's launch fields, the A5, A7 and A10 review tickets (each with its report folder) and an
     adoption ticket (profile LITE, acceptance_tests.path tests/acceptance/<its id>/, F-027) for the runner's
     `--close-ticket`; one commit (DEC-1188 (1)'s route; tk cannot write the fields).
It writes <run>/setup.json (per repository: the coordination, review and adoption tickets) and prints the start
lines. It stops at the first refusal, naming the repository and the step; a repository already set up is refused.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

if "--run" not in sys.argv:
    sys.exit("STOP: name the run folder with --run <path> (no default, DEC-1196 (5))")
RUN = Path(sys.argv[sys.argv.index("--run") + 1])
GOV = "/home/usain/.local/bin/gov"
PIN = "/home/usain/.local/share/gov-os/pin-961db6546490/bin/gov"
SRC = "/home/usain/Dynamic-Agentic-Engineering-OS"
STAGES = ("A5", "A7", "A10")
TRAILER = "\n\nRole: orchestrator\nTask: DAEO-l78m"
CLEAN_ENV = {"PATH": "/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin", "HOME": os.environ["HOME"], "LANG": "C.UTF-8"}


def stop(msg: str) -> None:
    sys.exit(f"STOP: {msg}")


def sh(cwd: Path, *args: str) -> str:
    done = subprocess.run(args, cwd=cwd, text=True, capture_output=True, env=CLEAN_ENV)
    if done.returncode:
        stop(f"{cwd.name}: {' '.join(args[:4])} exited {done.returncode}: {(done.stderr or done.stdout).strip()[-600:]}")
    return done.stdout


def insert(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    end = text.index("\n---\n", 4)
    head = text[:end]
    for key in ("\nrole:", "\nallowed_paths:", "\nkpis:", "\nprofile:", "\nacceptance_tests:"):
        if key in head:
            stop(f"{path} already has {key.strip()}")
    if "\nstate_class:" in head:
        block = "\n".join(l for l in block.split("\n") if not l.startswith("state_class:"))
    path.write_text(head + "\n" + block.rstrip("\n") + text[end:], encoding="utf-8")


def coord_block() -> str:
    return """state_class: AUTHORITATIVE
role: orchestrator
reads: []
needs: []
waits_on: []
allowed_paths:
- '**'
kpis:
  success:
  - line: "The repository is adopted with gov adopt --lite: each stage's record stands under governance/adoption/, and A5, A7 and A10 each rest on a fresh independent auditor's committed verdict"
    verify: "gov adopt --lite --stage <each stage> --json exits 0 in turn; the session's reports under the run's outputs/<repository>/ name each stage's commit"
  failure:
  - line: "A stage is skipped, or a verdict is committed by a session that ran a stage"
    verify: "gov adopt --lite --stage A5 (A7, A10) refuses VERDICT_NOT_INDEPENDENT for such a verdict"
"""


def review_block(stage: str) -> str:
    folder = f"governance/project/audits/adoption-{stage}"
    what = {"A5": "the A3 path map before any move (CAP-44.c)",
            "A7": "the A6 migration against the A3 path map and the A4 plan reviewed at A5 (CAP-44.f, lite)",
            "A10": "the A9 lite index and embeddings against the path map (CAP-44.f, lite)"}[stage]
    return f"""state_class: AUTHORITATIVE
role: independent-auditor
reads:
- governance/project/path-map.yaml
- governance/adoption
needs: []
waits_on: []
non_goals:
- It repairs nothing it reviews and runs no stage of gov adopt
- It writes nothing outside {folder}/
allowed_paths:
- {folder}/**
kpis:
  success:
  - line: "The verdict record {folder}/verdict.md reviews {what}; its front matter has verdict (pass or fail), path_map_hash equal to the hash of the A3 record as it stands, and auditor_session naming this session, which ran no stage; it is committed with Role: independent-auditor alone and writes nothing under governance/adoption/"
    verify: "the orchestrator's gov adopt --lite --stage {stage} --verdict {folder}/verdict.md --json exits 0 on a pass verdict"
  - line: "Each finding names its evidence (a path, a record line or a command and its output) and its effect"
    verify: "the verdict's findings section: every finding has a path or command and an effect"
  failure:
  - line: "A pass verdict over a record the review did not read, or a verdict committed by a session that ran a stage"
    verify: "the verdict lists each record it read; gov adopt refuses VERDICT_NOT_INDEPENDENT for a stage session's verdict"
"""


def adoption_block(name: str, tid: str) -> str:
    return f"""state_class: AUTHORITATIVE
role: orchestrator
profile: LITE
acceptance_tests:
  path: tests/acceptance/{tid}
reads: []
needs: []
waits_on: []
non_goals:
- No change to a file of the repository outside a reviewed batch (A6) or the adoption's own records
allowed_paths:
- '**'
kpis:
  success:
  - line: "S1: each stage A0 to A10 of gov adopt --lite has its record under governance/adoption/, committed"
    verify: "an acceptance test under tests/acceptance/{tid}/ lists governance/adoption/ at HEAD and finds one committed record per stage A0 to A10"
  - line: "S2: the A5, A7 and A10 verdicts are committed under governance/project/audits/adoption-<stage>/verdict.md, each naming an auditor_session that differs from the session named in the A3 record"
    verify: "an acceptance test reads the three verdicts' front matter and the A3 record's session"
  failure:
  - line: "F1: a stage record changed by hand: every commit touching governance/adoption/ carries Role: orchestrator in its final trailer block"
    verify: "an acceptance test reads git log for governance/adoption/ and checks each commit's trailers"
"""


def main() -> None:
    if [k for k in os.environ if k.startswith("GOV_")]:
        stop("a GOV_ variable is set; use a plain terminal")
    if os.path.realpath(GOV) != os.path.realpath(PIN):
        stop(f"{GOV} is not the 0.1.4 pin ({os.path.realpath(GOV)})")
    record = json.loads((RUN / "run.json").read_text())
    heads = record["heads"]
    for name in heads:  # every check before anything is written
        repo = RUN / "repos" / name
        if sh(repo, "git", "status", "--porcelain"):
            stop(f"{name}: the tree is not clean")
        if not sh(repo, "git", "rev-parse", "HEAD").startswith(heads[name]):
            stop(f"{name}: HEAD is not the recorded head {heads[name]}")
        if (repo / "governance").exists():
            stop(f"{name}: governance/ exists already (set up before?)")
    out = {}
    for name in heads:
        repo = RUN / "repos" / name
        sh(repo, "copier", "copy", "--trust", "--defaults", "--quiet", "--skip", ".gitignore", "--vcs-ref", "v0.1.4", SRC, ".")
        sh(repo, GOV, "adapters", "generate")
        sh(repo, "git", "add", "-A")
        sh(repo, "git", "commit", "-q", "-m", "Gov OS kit 0.1.4 from tag v0.1.4 (copier) and the adapters generated (W2-81's proving run on 0.1.4)" + TRAILER)
        if sh(repo, "git", "status", "--porcelain"):
            stop(f"{name}: the tree is not clean after the kit's commit")
        a0 = json.loads(sh(repo, GOV, "adopt", "--lite", "--stage", "A0", "--json"))
        coord = (a0.get("result") or {}).get("coordination_ticket")
        if not coord:
            stop(f"{name}: A0 created no coordination ticket: {json.dumps(a0)[:400]}")
        insert(repo / ".tickets" / f"{coord}.md", coord_block())
        tickets = {"coordination": coord}
        for stage in STAGES:
            tid = sh(repo, "tk", "create", f"{stage}: independent review (gov adopt --lite)", "-p", "1",
                     "--parent", coord, "--tags", "adoption,audit").strip().split()[-1]
            insert(repo / ".tickets" / f"{tid}.md", review_block(stage))
            tickets[stage] = tid
        tid = sh(repo, "tk", "create", f"W2-81: adopt {name} with gov adopt --lite (A1 to A10)", "-p", "1",
                 "--parent", coord, "--tags", "adoption").strip().split()[-1]
        insert(repo / ".tickets" / f"{tid}.md", adoption_block(name, tid))
        tickets["adoption"] = tid
        sh(repo, "git", "add", ".tickets")
        sh(repo, "git", "commit", "-q", "-m", f"W2-81's proving run on 0.1.4: the coordination ticket {coord} given its launch fields; the A5, A7, A10 review tickets and the adoption ticket {tid}" + TRAILER)
        if sh(repo, "git", "status", "--porcelain"):
            stop(f"{name}: the tree is not clean after the tickets' commit")
        out[name] = tickets
        print(f"{name}: ok  {json.dumps(tickets)}")
    (RUN / "setup.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"\nwrote {RUN / 'setup.json'}")
    print("queue tickets for --mode read: " + " ".join(f"--queue-ticket {n}={t['adoption']}" for n, t in out.items()))


main()

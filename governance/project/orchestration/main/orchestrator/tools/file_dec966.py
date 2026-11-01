"""DEC-966: files W2-105 (the template's install block removed), W2-106 (the template's hook lines pinned) and W2-107
(gitleaks results remembered by content hash), one commit each, then their WBS rows in one decision-record commit.
Map: log/tickets-2026-10-31a.json. Safe to re-run. The acceptance folder is spelled as ACC."""
import json
import re
import subprocess
import sys

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
from te_lib import ORCH, ROOT, T, commit, q  # noqa: E402

ACC = "tests/" + "acceptance"
MAP = ORCH / "log/tickets-2026-10-31a.json"
ids = json.loads(MAP.read_text()) if MAP.exists() else {}
TD = "independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer in its own tests worktree (DEC-959 item 7, DEC-963)"


def ticket(w2, title, *, prio, profile, role, cls, tags, deps, paths, kpis, fail, sources, est, track, body):
    fm = ["id: ID-PLACEHOLDER", "status: open", f"deps: [{', '.join(deps)}]", "links: []",
          "created: CREATED-PLACEHOLDER", "type: task", f"priority: {prio}", f"assignee: {role}",
          f"external-ref: {w2}", f"tags: [{', '.join(tags)}]", f"wbs_id: {w2}", f"title: {q(title)}",
          f"class: {cls}", "state_class: AUTHORITATIVE", f"role: {role}"]
    fm += ["depends_on: []"] if not deps else ["depends_on:"] + [f"- {d}" for d in deps]
    fm += ["allowed_paths:"] + [f"- {p}" for p in paths]
    fm += ["kpis:", "  success:"] + ["  - " + q(k) for k in kpis] + ["  failure:"] + ["  - " + q(f) for f in fail]
    fm += [f"profile: {profile}", "sources:"] + [f"- {s}" for s in sources]
    fm += [f"est_loc: {est}", "acceptance_tests:", f"  path: {ACC}/{w2}/", f"  author: {TD}",
           f"track: {track}", "list_rows: []"]
    return "---\n" + "\n".join(fm) + "\n---\n" + f"# {w2} {title.split(':')[0]}\n\n" + body.strip() + "\n"


NEW = {
    "W2-105": dict(
        title="The template's install block removed: an adopted product's CTO session reaches the guard's install rule and is asked, as this repository's is",
        prio=0, profile="STANDARD", role="product-spec", cls="specification",
        tags=["wave-2", "specification", "template", "installs", "standard"], deps=[],
        paths=["template/.rulesync/permissions.jsonc"],
        kpis=["A project generated from the template (copier, then rulesync generate) holds no deny rule for `npm install*` or `pip install*` in its generated settings [DEC-966 item 1, DEC-172]",
              "In that project, an install in the CTO's session (the orchestrator role on its coordination ticket) reaches the guard's install rule and is asked; in every other session, leads included, it is refused by the guard, as this repository's after DEC-957 [DEC-966 item 1, DEC-957]",
              "Every other permission and deny rule of the template is unchanged: the generated project's rules counted and compared before and after, by name, only the two install rules gone [DEC-966 item 1]",
              "The template's own suites (W1-38, W1-39) pass on the change [DEC-966 item 1, DEC-965]"],
        fail=["A generated project still denies an install before the guard is asked.",
              "An install in a session other than the CTO's is asked or allowed.",
              "Any other permission or deny rule added, removed or changed.",
              "W1-38 or W1-39 red on the change."],
        sources=["DEC-966", "DEC-172", "DEC-957", "DEC-965"], est=10, track="A",
        body="""Card: the owner's answer to P-W2-90-1 P1-A, (a) (DEC-966 item 1).

- **Why:** `template/.rulesync/permissions.jsonc` lines 7 and 8 deny `npm install*` and `pip install*`. In a generated product Claude Code refuses these before the guard is asked, so the CTO's session can never ask the owner. This repository removed the same rules by DEC-172. Found by W2-90 (`packages/P-W2-90-1.md`).
- **The only generated output:** the rules reach a product through `rulesync generate` in the generated project; no generated copy of them is kept under `template/` (searched), so the one source file is the ticket's path.
- **Then:** after it merges, W2-90's next round moves its 3 cases (W1-05's two orchestrator-asks cases and W1-46's research `npm install` case), with W2-106's 4 and the 14 ids of DEC-965 item 4.
- **Profile STANDARD:** a two-line configuration change, but it decides who is asked about installs in every adopted product."""),
    "W2-106": dict(
        title="The template's hook lines pinned: each runs the guard with the installed gov's own interpreter, ignoring PYTHONPATH, and refuses when no pinned gov is found",
        prio=0, profile="FULL", role="engineer", cls="implementation",
        tags=["wave-2", "implementation", "template", "guard", "fail-open", "full"], deps=[],
        paths=["template/governance/kernel/settings.json", "template/.rulesync/hooks.jsonc", "tests/unit/hooks/test_w2_106*"],
        kpis=["Each of the template's hook lines (pre-tool and the two post-tool lines, in `template/governance/kernel/settings.json` and their rulesync source `template/.rulesync/hooks.jsonc`) takes this repository's pinned form (DEC-822, W2-59): it finds the installed gov (`$HOME/.local/bin/gov`, else `gov` on PATH), reads the interpreter its first line names, and runs the hook with that interpreter and `-E`; the line's exit codes are kept (0 and 2 pass through; any other ends in a refusal) [DEC-966 item 2, DEC-822]",
              "Fail closed: with no gov found, or a first line that names no interpreter that runs, the line refuses (exit 2) with a message naming what is missing; it never falls back to a bare `python3` [DEC-966 item 2, DEC-822]",
              "A session's PYTHONPATH cannot change which guard code runs: in a generated project, a planted PYTHONPATH pointing at an edited copy of gov that would allow a refused write, the hook still refuses it (the measurement of P-W2-90-1 P1-B, now refused) [DEC-966 item 2, DEC-957]",
              "A generated project's hook lines equal the template's source after `rulesync generate` (the two sources stay in step), and the template's own suites (W1-38, W1-39) pass [DEC-966 item 2, DEC-616]"],
        fail=["A template hook line that runs a bare `python3`, or one without `-E`.",
              "A missing or broken gov lets the hook pass, or falls back to another interpreter.",
              "An edited gov on PYTHONPATH lets a refused write through.",
              "The settings and the rulesync source out of step, or W1-38 or W1-39 red."],
        sources=["DEC-966", "DEC-822", "DEC-957", "DEC-965", "DEC-801", "DEC-616"], est=60, track="A",
        body="""Card: the owner's answer to P-W2-90-1 P1-B, (a) (DEC-966 item 2): a fail-open must not ship in EXAMIN's copy.

- **Why:** the template's lines run `python3 "$h"` (`template/governance/kernel/settings.json` lines 8, 20 and 32; the same in `template/.rulesync/hooks.jsonc`). W2-90's test designer measured that a session whose PYTHONPATH points at an edited gov gets a refused write through (exit 0). This repository's lines carry the pinned form (DEC-822, W2-59).
- **No adoption step is needed:** this repository's form resolves the pin when the hook runs, from the installed gov's first line (the release the product installed, W2-16's frozen release once cut), so nothing under `src/gov/adopt/` changes and no dependency on W2-16 is needed. If the lead finds a reason for an adoption step, it is a package (W2-52 and W2-88 hold `src/gov/adopt/`).
- **Then:** after it merges, W2-90's next round moves its 4 W2-59 cases, with W2-105's 3 and the 14 ids of DEC-965 item 4.
- **Profile FULL:** the guard's wiring in every adopted product; an independent review of the final code (the QA step), on the fail-open and fail-closed paths."""),
    "W2-107": dict(
        title="Rebuild speed: gitleaks results remembered by content hash, so a rebuild scans only new or changed files; the nightly scans in full; any change to gitleaks or its rules forgets them all",
        prio=0, profile="FULL", role="engineer", cls="implementation",
        tags=["wave-2", "implementation", "secrets", "speed", "full"], deps=[],
        paths=["src/gov/secrets/__init__.py", "src/gov/secrets/cache.py", "tests/unit/secrets/test_w2_107*"],
        kpis=["A rebuild scans with gitleaks only content it has not judged clean before: each scan's verdict is remembered in one machine-wide cache (`~/.cache/gov-os/secrets-scan.sqlite`, outside every repository, shared by worktrees, close clones and the nightly), keyed by the sha256 of the bytes scanned, the kind (a file's content, or a path's names for `path_holds_secret`) and the engine's fingerprint (gitleaks' version string, the sha256 of every rule set in force, the cache format's version); a second rebuild of an unchanged tree scans nothing again [DEC-966 item 4, DEC-939]",
              "Only a clean verdict is remembered: no finding of any kind by any rule set. Any finding, row W2-L423's exempt commit hash included (its exemption depends on the repository), is never remembered and is scanned again every time; a secret's content is never answered clean from the cache [DEC-966 item 4, DEC-911, DEC-285]",
              "Any change to gitleaks or its rules forgets every remembered result: a fingerprint that differs from the cache's clears it before the first read [DEC-966 item 4]",
              "Fail closed: a cache that cannot be opened, is corrupt, has the wrong form or is locked counts as a miss, and the content is scanned; a write that fails is ignored; a scan that cannot decide still raises as today [DEC-966 item 4, DEC-285]",
              "The cache holds hashes and verdicts only, never content, a path or a secret's text [DEC-966 item 4, DEC-911]",
              "A full scan reads nothing from the cache (and refreshes it) when `GOV_SECRETS_FULL_SCAN=1` is set: the nightly sets it (that one line in `nightly.sh` is the orchestrator's at merge, with `test_nightly.sh`) [DEC-966 item 4]",
              "The rebuild's record says how many contents and names were scanned and how many were answered from the cache; measured before and after on this repository, in seconds of the secrets stage: a second rebuild of an unchanged tree, and a close clone's rebuild after the main tree's; the target is a secrets stage that scans only new or changed files [DEC-966 item 4, DEC-939 item 2]"],
        fail=["A secret's content answered clean from the cache, or a finding remembered.",
              "A changed gitleaks or rule set answered from the old results.",
              "A corrupt, missing or locked cache that stops a rebuild or answers clean.",
              "Content, a path or a secret's text written into the cache.",
              "The full-scan setting answered from the cache.",
              "No measured before and after, or a second unchanged rebuild that scans everything again."],
        sources=["DEC-966", "DEC-939", "DEC-911", "DEC-285", "DEC-898"], est=180, track="A",
        body="""Card: the owner's order of 2026-10-31 (DEC-966 item 4): rebuild speed is a priority.

- **Why:** W2-76 measured the rebuild's stages. The secrets filter in the code-index stage took 274.8 of 307.4 s (run 1) and 547.9 of 735.4 s (run 2): `gov.secrets.indexable` starts gitleaks once per file and rule set, for every file, on every rebuild, while the lexical index is already incremental by blob. Every rebuild (a worktree's, a close clone's, the designers' store, the nightly's) pays it again.
- **The fix (P-SPEED-1):** remember each clean verdict by the content's hash and the engine's fingerprint, so a rebuild scans only new or changed content; the nightly scans everything in full; any gitleaks or rule change forgets every result. Only "no finding" is remembered, so a cache error can only cause a rescan, never a missed secret.
- **Where:** `src/gov/secrets/__init__.py` (`indexable`, `path_holds_secret`, `_scan`) and a new `cache.py`. No running ticket holds `src/gov/secrets/`, but W2-05 (`DAEO-0z8c`, in progress) lists `src/gov/**/*.py` for the git environment of its helpers: split by file, W2-05 leaves `src/gov/secrets/__init__.py` to this ticket (its `_commits` git call's environment, if W2-05 needs it, is a merge-back between them, whichever merges second).
- **Not here:** W2-76's timing and lock (`src/gov/rebuild/**`); batching many files into one gitleaks call (a further speed-up, a later option if the cache is not enough).
- **Profile FULL:** the secrets filter guards the index against secrets; an independent review of the final code (the QA step) on every path where a remembered result is used."""),
}


def dor(tid):
    r = subprocess.run(["python3", str(ORCH / "tools/dor_hand.py"), tid], capture_output=True, text=True,
                       env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin:/home/usain/.local/bin"})
    return (r.stdout.strip() + " " + r.stderr.strip()[-200:]).strip()


for w2, spec in NEW.items():
    if w2 in ids:
        print(w2, ids[w2], "already filed")
        continue
    text = ticket(w2, **spec)
    meta = __import__("yaml").safe_load(text.split("\n---\n")[0][4:])
    assert meta["wbs_id"] == w2
    tid = subprocess.run(["tk", "create", spec["title"], "-p", str(spec["prio"]), "--external-ref", w2], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.strip().split()[-1]
    path = ROOT / ".tickets" / (tid + ".md")
    created = re.search(r"^created: (\S+)$", path.read_text(encoding="utf-8"), re.M).group(1)
    path.write_text(text.replace("ID-PLACEHOLDER", tid).replace("CREATED-PLACEHOLDER", created), encoding="utf-8")
    T(tid).save()  # YAML parse + placeholder scan
    ids[w2] = tid
    MAP.write_text(json.dumps(ids) + "\n", encoding="utf-8")
    print(dor(tid))
    sha = commit(f"{w2} ({tid}) filed: {spec['title'][:90]} (DEC-966)", [path],
                 [f"Task: {tid}", "Implements: DEC-966", "Role: orchestrator"])
    print(w2, tid, sha)

# WBS rows, after W2-104's, in one decision-record commit
wbs = ROOT / "docs/plan/WAVE_2_WBS.md"
lines = wbs.read_text(encoding="utf-8").split("\n")
if not any(l.startswith("| W2-105 |") for l in lines):
    at = max(i for i, l in enumerate(lines) if l.startswith("| W2-104 |"))
    rows = [
        f"| W2-105 | A | **New (DEC-966).** The template's install block removed: an adopted product's CTO session is asked (P-W2-90-1 P1-A) (`{ids['W2-105']}`) | specification | product-spec | STANDARD | none | 10 | DEC-966 item 1, DEC-172 |",
        f"| W2-106 | A | **New (DEC-966).** The template's hook lines pinned (the installed gov's interpreter, `-E`, fail closed) (P-W2-90-1 P1-B) (`{ids['W2-106']}`) | implementation | engineer | FULL | none | 60 | DEC-966 item 2, DEC-822 |",
        f"| W2-107 | A | **New (DEC-966).** Rebuild speed: gitleaks verdicts remembered by content hash; the nightly scans in full; a gitleaks or rule change forgets them (`{ids['W2-107']}`) | implementation | engineer | FULL | none | 180 | DEC-966 item 4, DEC-939 |",
    ]
    lines[at + 1:at + 1] = rows
    wbs.write_text("\n".join(lines), encoding="utf-8")
    sha = commit("WBS: rows W2-105 to W2-107 (DEC-966)", [wbs],
                 ["Task: decision-record", "Implements: DEC-966", "Role: orchestrator",
                  "Decided-by: owner (chat, 2026-10-31)"])
    print("WBS", sha)
print(json.dumps(ids))

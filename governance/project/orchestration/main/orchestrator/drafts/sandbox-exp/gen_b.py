"""SANDBOX-GUARD-EXP-1, set-up B's generator (the design §3, the declaration §7 (b)): Claude Code sandbox settings and
permission rules for one role and ticket, generated from the path map's role paths, its evaluation sets, its sets-root
and session blocks, the held-out list and the ticket's allowed paths, as one JSON settings file per role and ticket.

What it writes (every path literal and absolute: the Linux sandbox skips patterns, W2-56 KPI 3):
  sandbox.filesystem.allowWrite  the role's write paths (write_patterns: the ticket's allowed paths; the test
                                 designer's tests/acceptance; an auditor's rule-5 record paths and /tmp), a lead's
                                 tree, the session's temp folder (added by the runner at launch),
                                 its run folder, the tree's scratch and git's folders. A pattern that cannot be made
                                 literal is enumerated to the entries that exist and NAMED in the report, never widened.
  sandbox.filesystem.denyWrite   the acceptance tests (every role but the test designer), .tickets, .claude,
                                 .gov-runtime outside scratch, the hidden folders, and (workers) the write fence: every
                                 entry beside the path to an allowed path, since the sandbox's default write set holds
                                 the working folder (the launcher's research fence, generalised).
  sandbox.filesystem.denyRead    secrets (the hook's names, found by a names-only walk of the tree, plus ~/.ssh and the
                                 CLI's key files); the held-out material's FILES (not its folder, so a names-only
                                 listing still runs: Q3); the hidden halves of the sets that measure the role, in every
                                 tree and under the sets root; the sets root's hidden part for its refused roles; the
                                 session-hidden folders for their role and ticket; the test designer's {ticket_impl}.
                                 Left out: the engineer's {ticket_tests} (DEC-873, Q2).
  sandbox.filesystem.allowRead   the shared test files inside a denied {ticket_impl} folder (DEC-963).
  permissions.deny               Read(...) and Edit(...) rules mirroring the lists, for the file tools.
  permissions.allow              Bash, Read, Grep, Glob, and Edit(...) for the allowWrite paths only (an Edit allow
                                 rule widens the sandbox's write set, so it never names more than allowWrite).
  sandbox.network                strictAllowlist, the research allowlist for research only, and the two sockets of Q9
                                 (the reranker's, ~/.cache/gov-os/rerank.sock, and the WSL interop socket if given).
  env                            GOV_ROLE, GOV_TICKET.
The CTO's own session (orchestrator on W2-00, or no ticket) gets no sandbox (Q4): it is scored on the hook's decision.

  python3 gen_b.py one --role R --ticket T --tree DIR --home H --out FILE [--map M] [--held-out F] [--tickets D]
        [--sets-root S] [--run-folder F] [--engineer-tree D] [--config-dir D] [--wsl-socket P] [--allowlist F ...]
  python3 gen_b.py all --actions FILE ... --home H --clone DIR --out-dir DIR [as above]
      writes <out-dir>/<role>--<ticket>--<tree hash>.json and .report.json for every role, ticket and session tree
      the actions name (the runner builds the same in memory; this is for review).
Both print counts only: never a path (a held-out file's name included).
"""
from __future__ import annotations

import argparse
import collections
import fnmatch
import glob as globmod
import json
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

WORKER_ROLES = ("engineer", "independent-test-designer", "independent-auditor", "research", "product-spec")
ACCEPTANCE = "tests/acceptance"
PROTECTED_TREES = (".tickets", ".claude")
RUNTIME, SCRATCH = ".gov-runtime", "scratch"
CTO_TICKETS = (None, "", "W2-00")
SHARED_TEST = ("conftest.py", "__init__.py", "*support*.py", "*helper*.py")
# Rule 5's record paths (the live hook's REVIEW_PATHS, .claude/hooks/pretooluse.py), tree-relative folders.
REVIEW_PATHS = ("docs/probes/", "docs/audit/", "docs/assessment/", ".gov-runtime/scratch/review/",
                ".gov-runtime/scratch/audit/", ".gov-runtime/scratch/orchestrator/reviews/")
RERANK_SOCKET = (".cache", "gov-os", "rerank.sock")
READ_TOOLS_ALLOW = ["Bash", "Read", "Grep", "Glob"]
_GLOB = re.compile(r"[*?\[]")


# -- inputs -------------------------------------------------------------------------------------------------------------
def load_yaml(path: str):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def frontmatter(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    return (yaml.safe_load(text[3:end]) or {}) if end > 0 else {}


def load_ticket(tickets_dir: str, tid: str | None) -> dict:
    """The ticket by its id or its wbs_id (the guard's way); {} when absent."""
    if not tid or "/" in tid or not os.path.isdir(tickets_dir):
        return {}
    p = os.path.join(tickets_dir, f"{tid}.md")
    if os.path.isfile(p):
        return frontmatter(p)
    for name in sorted(os.listdir(tickets_dir)):
        if name.endswith(".md"):
            fm = frontmatter(os.path.join(tickets_dir, name))
            if fm.get("wbs_id") == tid:
                return fm
    return {}


# -- literal paths ------------------------------------------------------------------------------------------------------
def literal(base: str, pattern: str) -> tuple[list[str], bool]:
    """A tree-relative pattern made literal under base: (paths, placed). A plain path, or a plain folder followed by
    /**, is placed as one literal path (whether or not it exists). Any other pattern is enumerated to the entries that
    exist now, and is not placed: the caller names it (never widened to a folder)."""
    p = pattern.strip().rstrip("/")
    if not p:
        return [], True
    if not _GLOB.search(p):
        return [os.path.join(base, p)], True
    if p.endswith("/**") and not _GLOB.search(p[:-3]):
        return [os.path.join(base, p[:-3])], True
    found = sorted(globmod.glob(os.path.join(base, p), recursive=True))
    return found, False


def dir_prefix(base: str, pattern: str) -> str | None:
    """For a deny: the deepest literal folder of a glob (fixtures/x/hidden/** -> base/fixtures/x/hidden). A deny of a
    folder that holds only the pattern's matches is exact; where the pattern narrows inside a folder (a name pattern),
    the matches that exist are listed instead (see deny_glob)."""
    parts = pattern.strip().rstrip("/").split("/")
    lit = []
    for part in parts:
        if _GLOB.search(part):
            break
        lit.append(part)
    if len(lit) == len(parts) or parts[len(lit):] == ["**"]:
        return os.path.join(base, *lit) if lit else None
    return None


def deny_glob(base: str, pattern: str) -> tuple[list[str], bool]:
    """A hidden glob as deny paths under base: (paths that exist, exact). Exact when the glob is a folder's whole
    content; otherwise the existing matches are listed and the pattern is named."""
    d = dir_prefix(base, pattern)
    if d is not None:
        return ([d] if os.path.lexists(d) else []), True
    return sorted(globmod.glob(os.path.join(base, pattern), recursive=True)), False


def is_secret(path: str, home: str) -> bool:
    """The hook's secret names (src/gov/guard/reads.py, Reads.secret), for the generator's names-only walk."""
    name = os.path.basename(path)
    ssh = os.path.join(home, ".ssh")
    key = os.path.join(home, ".claude", ".credentials.json")
    return (name.endswith(".env") or name.startswith(".env.") or name == ".secrets" or "/.secrets/" in path
            or name.endswith((".pem", ".key"))
            or (name.startswith("secrets") and os.path.basename(os.path.dirname(path)) == "config")
            or path == ssh or path.startswith(ssh + "/") or path == key)


def secrets_in(tree: str, home: str) -> list[str]:
    """Secret-named entries in the tree, by a names-only walk (no file is opened; .git is skipped)."""
    out = []
    for dirpath, dirnames, filenames in os.walk(tree):
        dirnames[:] = sorted(d for d in dirnames if d != ".git")
        for name in list(dirnames) + sorted(filenames):
            p = os.path.join(dirpath, name)
            if is_secret(p, home):
                out.append(p)
        dirnames[:] = [d for d in dirnames if not is_secret(os.path.join(dirpath, d), home)]
    return out


def files_under(path: str) -> list[str]:
    """Every file under a folder (names only), or the path itself when it is a file."""
    if os.path.isfile(path) or os.path.islink(path):
        return [path]
    out = []
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames.sort()
        out += [os.path.join(dirpath, n) for n in sorted(filenames)]
    return out


def git_dirs(tree: str) -> list[str]:
    """git's folders for the tree: its .git folder, or for a worktree the folder its .git file names and the common
    folder that one names."""
    g = os.path.join(tree, ".git")
    if os.path.isdir(g):
        return [g]
    if not os.path.isfile(g):
        return []
    with open(g, encoding="utf-8") as f:
        line = f.read().strip()
    if not line.startswith("gitdir:"):
        return []
    wt = os.path.normpath(os.path.join(tree, line[len("gitdir:"):].strip()))
    out = [wt]
    cd = os.path.join(wt, "commondir")
    if os.path.isfile(cd):
        with open(cd, encoding="utf-8") as f:
            out.append(os.path.normpath(os.path.join(wt, f.read().strip())))
    return out


def open_folders(tree: str, allowed: list[str]) -> list[str]:
    """The folders on the path from the tree to an allowed path: the fence denies what exists beside the path, so a
    NEW name made in one of these folders stays writable (the working folder is in the sandbox's default write set).
    Named in the report (W2-56 KPI 3), never hidden."""
    rels = {os.path.relpath(a, tree) for a in allowed}
    rels = {r for r in rels if not r.startswith("..") and r != "."}
    out = set()
    for r in rels:
        parts = r.split(os.sep)
        for i in range(len(parts)):
            anc = os.sep.join(parts[:i])
            if not any(anc == x or anc.startswith(x + os.sep) for x in rels):
                out.add(os.path.join(tree, anc) if anc else tree)
    return sorted(out)


def fence(tree: str, allowed: list[str]) -> list[str]:
    """Every entry that exists beside the path from the tree to an allowed path: denied to writes, so that the working
    folder (writable by the sandbox's default) holds writes to the allowed paths only. Left out: the allowed paths and
    their ancestors, .git and .gov-runtime at the root (their own rules), and names the sandbox would read as patterns."""
    rels = {os.path.relpath(a, tree) for a in allowed}
    rels = {r for r in rels if not r.startswith("..")}
    if "." in rels:
        return []  # the whole tree is allowed: no fence

    def under_allowed(d: str) -> bool:
        return any(d == r or d.startswith(r + os.sep) for r in rels)

    ancestors = set()
    for r in rels:
        parts = r.split(os.sep)
        for i in range(len(parts)):
            anc = os.sep.join(parts[:i])
            if not under_allowed(anc):
                ancestors.add(anc)
    keep = rels | ancestors
    out = []
    for d in sorted(ancestors):
        here = os.path.join(tree, d) if d else tree
        if not os.path.isdir(here) or os.path.islink(here):
            continue
        for name in sorted(os.listdir(here)):
            rel = os.path.join(d, name) if d else name
            if rel in keep or _GLOB.search(name) or (not d and name in (".git", RUNTIME)):
                continue
            out.append(os.path.join(here, name))
    return out


def runtime_entries(tree: str) -> list[str]:
    """.gov-runtime's entries other than scratch, as they exist (DEC-180)."""
    base = os.path.join(tree, RUNTIME)
    if not os.path.isdir(base):
        return []
    return [os.path.join(base, n) for n in sorted(os.listdir(base)) if n != SCRATCH and not _GLOB.search(n)]


def allowlist(paths: list[str]) -> list[str]:
    hosts = set()
    for p in paths:
        if os.path.isfile(p):
            data = load_yaml(p) or {}
            hosts |= {h for h in (data.get("hosts") or []) if isinstance(h, str)}
    return sorted(hosts)


def trees_of(home: str, clone: str) -> list[str]:
    """Every tree of the repository in the substituted home: the clone and each worktree there."""
    out = [clone]
    wt = os.path.join(home, "gov-os-worktrees")
    if os.path.isdir(wt):
        out += [os.path.join(wt, n) for n in sorted(os.listdir(wt)) if os.path.isdir(os.path.join(wt, n))]
    return out


def uniq(xs) -> list[str]:
    seen, out = set(), []
    for x in xs:
        x = os.path.normpath(x)
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def write_patterns(role: str, ticket: dict, report: dict) -> list[str]:
    """The tree-relative paths a worker writes (DEC-820 (4)), by role: the test designer its acceptance tests (MR-3,
    its role file); a reviewer or auditor its record paths (rule 5, DEC-954) and, on its own auditor ticket, that
    ticket's report paths, with /tmp beside them (written as the absolute /tmp by the caller); every other worker the
    ticket's allowed paths."""
    if role == "independent-test-designer":
        return [ACCEPTANCE + "/**"]
    if role == "independent-auditor":
        own = list(ticket.get("allowed_paths") or []) if ticket.get("role") == "independent-auditor" else []
        report["notes"].append("an auditor: rule 5's record paths and /tmp (DEC-954) beside DEC-820 (4)")
        return own + [p + "**" for p in REVIEW_PATHS]
    return [str(p) for p in ticket.get("allowed_paths") or []]


# -- the build ----------------------------------------------------------------------------------------------------------
def build(role: str, ticket_id: str | None, *, tree: str, home: str, map_path: str, held_out_path: str | None,
          tickets_dir: str, clone: str | None = None, sets_root: str | None = None, run_folder: str | None = None,
          engineer_tree: str | None = None, config_dir: str | None = None, wsl_socket: str | None = None,
          allowlists: tuple = (), write_mode: str = "fence") -> tuple[dict, dict]:
    """(settings, report) for one role and ticket. The report holds counts, the patterns named, and notes.

    write_mode "fence" (the default) denies every existing entry beside the path to an allowed path, and names the
    folders where a new name stays writable. "root-deny" denies the whole tree to writes and relies on the narrower
    allowWrite paths winning inside it: how the CLI resolves that overlap for writes is not measured, so it is a
    tuning option, never the default."""
    tree, home = os.path.realpath(tree), os.path.realpath(home)
    clone = os.path.realpath(clone) if clone else tree
    pm = load_yaml(map_path) or {}
    ticket = load_ticket(tickets_dir, ticket_id)
    wbs = ticket.get("wbs_id") or ticket_id
    env = {"GOV_ROLE": role, **({"GOV_TICKET": ticket_id} if ticket_id else {})}
    report = {"role": role, "ticket": ticket_id, "wbs": wbs, "sandboxed": True, "unplaced": [], "enumerated": [],
              "notes": []}
    if role == "orchestrator" and (ticket_id in CTO_TICKETS or wbs in CTO_TICKETS):
        report["sandboxed"] = False
        report["notes"].append("the CTO's own session: no sandbox (Q4); scored on the hook's decision")
        return {"env": env}, report
    lead = role == "orchestrator"
    worker = role in WORKER_ROLES
    sroot = os.path.realpath(os.path.expanduser(sets_root) if sets_root else
                             (pm.get("sets_root_hidden") or {}).get("root", "~/gov-os-eval").replace("~", home, 1))

    # allowWrite --------------------------------------------------------------------------------------------------
    allow_w = []
    if worker:
        for p in write_patterns(role, ticket, report):
            paths, placed = literal(tree, str(p))
            allow_w += paths
            if not placed:
                report["unplaced"].append({"pattern": str(p), "existing": len(paths)})
    if role == "independent-auditor":
        allow_w.append("/tmp")
    if lead:
        allow_w.append(tree)  # the sandbox's default for the working folder, stated (no fence for a lead)
    allow_w += [os.path.join(tree, RUNTIME, SCRATCH)] + git_dirs(tree)
    if run_folder:
        allow_w.append(run_folder)
    allow_w = uniq(allow_w)

    # denyWrite ---------------------------------------------------------------------------------------------------
    deny_w = []
    if worker:
        inside = [a for a in allow_w if a.startswith(tree + os.sep)]
        if write_mode == "root-deny":
            deny_w.append(tree)
            report["notes"].append("root-deny: the tree denied to writes, allowWrite narrower inside it (unmeasured)")
        else:
            deny_w += fence(tree, inside)
            report["open_folders"] = len(open_folders(tree, inside))
    trees = PROTECTED_TREES if role == "independent-test-designer" else (ACCEPTANCE, *PROTECTED_TREES)
    deny_w += [os.path.join(tree, t) for t in trees]
    deny_w += runtime_entries(tree)

    # denyRead ----------------------------------------------------------------------------------------------------
    deny_r, allow_r = [], []
    deny_r += secrets_in(tree, home)
    for p in (os.path.join(home, ".ssh"), os.path.join(home, ".claude", ".credentials.json")):
        if os.path.lexists(p):
            deny_r.append(p)
    if config_dir:
        for n in (".credentials.json", ".claude.json"):
            p = os.path.join(os.path.realpath(config_dir), n)
            if os.path.lexists(p):
                deny_r.append(p)
    if held_out_path and os.path.isfile(held_out_path):
        for raw in (load_yaml(held_out_path) or {}).get("held_out_paths") or []:
            p = C.rewrite(str(raw), home).rstrip("/")
            found = files_under(p) if os.path.lexists(p) else []
            deny_r += found
            if not found:
                report["notes"].append("a held-out entry with nothing at it (no rule; the sandbox would plant a name)")
    hidden_w = []
    for name, spec in sorted((pm.get("evaluation_sets") or {}).items()):
        m = (spec or {}).get("measures") or {}
        if role in (m.get("roles") or []) or (wbs and wbs in (m.get("tickets") or [])):
            for g in spec.get("hidden") or []:
                for base in [sroot] + trees_of(home, clone):
                    paths, exact = deny_glob(base, g)
                    deny_r += paths
                    if not exact:
                        report["enumerated"].append({"pattern": g, "existing": len(paths)})
        for g in (spec or {}).get("hidden") or []:  # a write into a hidden folder is refused to every role
            hidden_w += deny_glob(sroot, g)[0]
    srh = pm.get("sets_root_hidden") or {}
    for g in srh.get("hidden") or []:
        paths, exact = deny_glob(sroot, g)
        hidden_w += paths
        if role in (srh.get("refused_roles") or []):
            deny_r += paths
            if not exact:
                report["enumerated"].append({"pattern": g, "existing": len(paths)})
    for entry in pm.get("session_hidden") or []:
        if role in (entry.get("roles") or []) and (not entry.get("tickets") or wbs in entry["tickets"]
                                                  or ticket_id in entry["tickets"]):
            p = os.path.realpath(str(entry.get("root", "")).replace("~", home, 1))
            if os.path.lexists(p):
                deny_r.append(p)
    if role == "independent-test-designer" and wbs:
        etree = os.path.realpath(engineer_tree or os.path.join(home, "gov-os-worktrees", str(wbs)))
        for p in ticket.get("allowed_paths") or []:
            p = str(p)
            if p.startswith(ACCEPTANCE + "/") or p == ACCEPTANCE:
                continue
            paths, placed = literal(etree, p)
            for q in paths:
                if not os.path.lexists(q):
                    continue
                if os.path.isdir(q):
                    deny_r.append(q)
                    allow_r += [f for f in files_under(q)
                                if any(fnmatch.fnmatch(os.path.basename(f), s) for s in SHARED_TEST)]
                elif not any(fnmatch.fnmatch(os.path.basename(q), s) for s in SHARED_TEST):
                    deny_r.append(q)
            if not placed:
                report["unplaced"].append({"pattern": p, "existing": len(paths), "for": "ticket_impl"})
    if role == "engineer":
        report["notes"].append("{ticket_tests} left to the hook (DEC-873, Q2)")
    deny_w += hidden_w
    deny_w, deny_r, allow_r = uniq(deny_w), uniq(deny_r), uniq(allow_r)
    allow_w = [a for a in allow_w if a not in set(deny_w)]

    # permissions -------------------------------------------------------------------------------------------------
    def rules(tool, paths):
        out = []
        for p in paths:
            out.append(f"{tool}(/{p})")
            if os.path.isdir(p) and not os.path.islink(p):
                out.append(f"{tool}(/{p}/**)")
        return out

    deny = rules("Read", deny_r) + rules("Edit", deny_w)
    allow = READ_TOOLS_ALLOW + rules("Edit", allow_w)
    sockets = [os.path.join(home, *RERANK_SOCKET)] + ([wsl_socket] if wsl_socket else [])
    settings = {
        "env": env,
        "permissions": {"allow": allow, "deny": deny},
        "sandbox": {
            "enabled": True,
            "failIfUnavailable": True,
            "allowUnsandboxedCommands": False,
            "network": {"strictAllowlist": True, "allowedDomains": allowlist(list(allowlists)) if role == "research"
                        else [], "allowUnixSockets": sockets},
            "filesystem": {"allowWrite": allow_w, "denyWrite": deny_w, "denyRead": deny_r, "allowRead": allow_r},
        },
    }
    if lead:
        report["notes"].append("a lead: no write fence (a tuning choice); its tree stays writable as the sandbox's default")
    report["counts"] = {"allowWrite": len(allow_w), "denyWrite": len(deny_w), "denyRead": len(deny_r),
                        "allowRead": len(allow_r), "permissions.deny": len(deny), "permissions.allow": len(allow),
                        "sockets": len(sockets)}
    return settings, report


def control_settings(role: str, ticket_id: str | None) -> dict:
    """The permissive control (the declaration §7 (b)): the sandbox off, no deny rule, every tool allowed. The hook
    still runs (the runner asks it first)."""
    return {"env": {"GOV_ROLE": role, **({"GOV_TICKET": ticket_id} if ticket_id else {})},
            "permissions": {"allow": READ_TOOLS_ALLOW + ["Edit(//**)"], "deny": []},
            "sandbox": {"enabled": False}}


def faults(settings: dict) -> list[str]:
    """Why a sandboxed settings value is not strict, literal and absolute; empty when it is (the launcher's
    sandbox_faults, plus the experiment's own checks)."""
    out = []
    sb = settings.get("sandbox")
    if not isinstance(sb, dict):
        return ["no sandbox block"]
    if sb.get("enabled") is not True:
        out.append("sandbox.enabled is not true")
    if sb.get("failIfUnavailable") is not True:
        out.append("sandbox.failIfUnavailable is not true")
    if sb.get("allowUnsandboxedCommands") is not False:
        out.append("sandbox.allowUnsandboxedCommands is not false")
    if "excludedCommands" in sb:
        out.append("sandbox.excludedCommands is set")
    if (sb.get("network") or {}).get("strictAllowlist") is not True:
        out.append("sandbox.network.strictAllowlist is not true")
    for k, v in (sb.get("filesystem") or {}).items():
        for p in v:
            if not p.startswith("/") or _GLOB.search(p):
                out.append(f"sandbox.filesystem.{k}: a path that is not literal and absolute")
                break
    aw = set((sb.get("filesystem") or {}).get("allowWrite") or [])
    for r in (settings.get("permissions") or {}).get("allow") or []:
        if r.startswith("Edit("):
            p = r[len("Edit(/"):-1]
            p = p[:-3] if p.endswith("/**") else p
            if p not in aw and not any(p == a for a in aw):
                out.append("an Edit allow rule names more than allowWrite")
                break
    return out


# -- the command line ---------------------------------------------------------------------------------------------------
def _common(p):
    p.add_argument("--home", required=True)
    p.add_argument("--map")
    p.add_argument("--held-out")
    p.add_argument("--tickets")
    p.add_argument("--sets-root")
    p.add_argument("--run-folder")
    p.add_argument("--engineer-tree")
    p.add_argument("--config-dir")
    p.add_argument("--wsl-socket", default=os.environ.get("SGX_WSL_SOCKET"))
    p.add_argument("--allowlist", action="append", default=[])


def _defaults(a, tree):
    a.map = a.map or os.path.join(tree, "governance", "project", "path-map.yaml")
    a.held_out = a.held_out or os.path.join(tree, "governance", "project", "held-out.yaml")
    a.tickets = a.tickets or os.path.join(tree, ".tickets")
    if not a.allowlist:
        a.allowlist = [os.path.join(tree, "template/governance/kernel/launch/research-allowlist.yaml"),
                       os.path.join(tree, "governance/project/research-allowlist.yaml")]


def write_one(path: str, settings: dict, report: dict) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    data = json.dumps(settings, indent=1, sort_keys=True) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
    with open(path[:-len(".json")] + ".report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, sort_keys=True)
    return C.sha(data)


def settings_name(role: str, ticket: str | None, tree: str = "") -> str:
    """One file per role, ticket and tree (a tree's name, hashed, so no path is in a file name)."""
    return f"{role}--{ticket or 'none'}--{C.sha(os.path.realpath(tree))[:8] if tree else 'tree'}.json"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("one")
    o.add_argument("--role", required=True)
    o.add_argument("--ticket")
    o.add_argument("--tree", required=True)
    o.add_argument("--clone")
    o.add_argument("--out", required=True)
    _common(o)
    al = sub.add_parser("all")
    al.add_argument("--actions", action="append", required=True)
    al.add_argument("--clone", required=True)
    al.add_argument("--out-dir", required=True)
    _common(al)
    a = p.parse_args(argv)
    kw = lambda: dict(home=a.home, map_path=a.map, held_out_path=a.held_out, tickets_dir=a.tickets,  # noqa: E731
                      sets_root=a.sets_root, run_folder=a.run_folder, engineer_tree=a.engineer_tree,
                      config_dir=a.config_dir, wsl_socket=a.wsl_socket, allowlists=tuple(a.allowlist))
    if a.cmd == "one":
        _defaults(a, a.tree)
        s, r = build(a.role, a.ticket, tree=a.tree, clone=a.clone or a.tree, **kw())
        digest = write_one(a.out, s, r)
        C.say(f"settings for one role: sandboxed {r['sandboxed']}; counts {r.get('counts', {})}; patterns named "
              f"{len(r['unplaced'])}, enumerated {len(r['enumerated'])}; faults {len(faults(s)) if r['sandboxed'] else '-'};"
              f" sha256 {digest[:12]}")
        return 0
    _defaults(a, a.clone)
    import run_a  # the session's tree, as set-up A places it
    home = os.path.realpath(a.home)
    keys = collections.Counter()
    for path in a.actions:
        if os.path.exists(path):
            for rec in C.read_jsonl(path):
                cwd = C.rewrite(rec.get("cwd") or C.MAIN, home)
                keys[(rec.get("role") or "unknown", rec.get("ticket"),
                      run_a.session_tree(cwd, home, os.path.realpath(a.clone)))] += 1
    bad = 0
    for (role, ticket, tree) in sorted(keys, key=lambda k: (k[0], str(k[1]), k[2])):
        s, r = build(role, ticket, tree=tree, clone=a.clone, **kw())
        write_one(os.path.join(a.out_dir, settings_name(role, ticket, tree)), s, r)
        bad += bool(r["sandboxed"] and faults(s))
    C.say(f"settings: {len(keys)} role, ticket and tree files; with faults {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

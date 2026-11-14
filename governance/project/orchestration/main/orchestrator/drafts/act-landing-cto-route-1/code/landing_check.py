#!/usr/bin/env python3
"""The landing check (OPERATOR-AGENT-1 §3, S16, DEC-1104 (2)): commits outside a ticket on a control path.

    python3 landing_check.py --repo <repo> <rev range>

Prints a JSON list, one item per flagged first-parent commit of the range:
    {"commit": "<40 hex>", "priority": "P1", "paths": [...], "rows": [...], "subject": "...", "reason": "..."}

A commit is outside a ticket as the landing selection reads it (ACT-SELECT-HOOK-1 §1 step 3): it carries
`Role: owner`, or no `Task: DAEO-<ticket>` other than DAEO-sdxk (the CTO's own). It is flagged when its own change
(against its first parent) touches a (b) or (O) control path of the rule table (class-rules.yaml's rows marked
`control: true`; the (O) catch-all and the "none" rows are not control paths, N-5), unless it carries `Role: owner`,
or `Role: operator` together with an `Act:` trailer. Each flagged commit is one inbox P1 item for the trigger to file.

The CTO's route (ACT-LANDING-CTO-ROUTE-1, DEC-1167 (5)): a commit with `Role: orchestrator`, one `Act: <ACT id>` and one
`Act-sha: <manifest sha256>` trailer also passes, when and only when all three hold, and anything else stays the P1 it
is. (1) The CTO's approvals log (APPROVALS) holds a line for that ACT with that manifest whose `route` begins "the CTO"
(the applier; a route that only mentions the CTO, such as the operator agent's queue, is not it). (2) The ACT is class
(b): the manifest, found under the CTO's acts folder (ACTS_DIR) by the sha256 of its bytes, names that ACT, claims (b),
and the classifier's own vote on its bundle is (b); and the class of the commit's paths by the rule table is (b), never
(O). (3) The commit's paths are exactly the manifest's `touched` list (every entry of root repo).
"""
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import act_class  # noqa: E402

CTO_TASK = "DAEO-sdxk"
# The CTO route's two inputs (the CTO's own scratch folder). Fixed here and never read from the environment or the
# command line: the CTO's session starts this check, so a seam it could set would let it name its own approvals.
CTO_ORCH = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator"
APPROVALS = os.path.join(CTO_ORCH, "log", "act-approvals.jsonl")
ACTS_DIR = os.path.join(CTO_ORCH, "acts")
ACT_ID_RE = re.compile(r"^ACT-[A-Za-z0-9][A-Za-z0-9._-]*$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, env=env, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:2])} failed: {r.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return r.stdout.decode("utf-8", "replace")


def trailer_values(repo, commit, key):
    out = git(repo, "log", "-1", f"--format=%(trailers:key={key},valueonly,separator=%x1f)", commit)
    return [v.strip() for v in out.strip().split("\x1f") if v.strip()]


def outside_a_ticket(roles, tasks):
    if any(r.replace(" ", "") == "owner" for r in roles):
        return True
    return not any(re.match(r"^DAEO-[a-z0-9]+$", t.replace(" ", "")) and t.replace(" ", "") != CTO_TASK for t in tasks)


def control_paths(rules, paths):
    hits = []
    for p in paths:
        row = act_class.row_for(rules, "repo", p)
        if row is not None and row.get("control") is True:
            hits.append((p, row.get("id")))
    return hits


def path_class(rules, path):
    """The class a path alone gives (the highest the rule table allows it): a fixed row its class, a list-shaped row the
    higher of its `else` and `ratchet_class` (its content-dependent (a) is not counted on); a path no row names is (O)."""
    row = act_class.row_for(rules, "repo", path)
    if row is None:
        return "O"
    if "list" in row:
        return act_class.top(row.get("else", "O"), row.get("ratchet_class", "a"))
    return act_class.top(row.get("class", "O"))


def cto_approved(approvals, act, sha):
    """Condition 1: a line of the approvals log for this ACT and this manifest whose route begins "the CTO"."""
    try:
        with open(approvals, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return False
    for ln in lines:
        try:
            e = json.loads(ln)
        except ValueError:
            continue
        if not isinstance(e, dict) or e.get("act") != act:
            continue
        if sha not in (e.get("manifest"), e.get("manifest_sha256")):
            continue
        route = e.get("route")
        if isinstance(route, str) and route.strip().lower().startswith("the cto"):
            return True
    return False


def find_manifest(acts_dir, act, sha):
    """The bundle folder under acts_dir (<ACT> or <ACT>.<anything>) whose manifest.json hashes as sha, with the manifest."""
    import hashlib
    try:
        names = sorted(os.listdir(acts_dir))
    except OSError:
        return None, None
    for name in names:
        if name != act and not name.startswith(act + "."):
            continue
        d = os.path.join(acts_dir, name)
        m = os.path.join(d, "manifest.json")
        if os.path.islink(d) or os.path.islink(m) or not os.path.isfile(m):
            continue
        try:
            raw = open(m, "rb").read()
            if hashlib.sha256(raw).hexdigest() != sha:
                continue
            return d, json.loads(raw.decode("utf-8"))
        except (OSError, ValueError):
            continue
    return None, None


def cto_route(rules, roles, acts, shas, paths, approvals, acts_dir):
    """(passes, why not). The route's three conditions, on a commit that carries Role: orchestrator, Act: and Act-sha:."""
    if [r.replace(" ", "") for r in roles] != ["orchestrator"] or len(acts) != 1 or len(shas) != 1:
        return False, "it needs exactly one Role: orchestrator, one Act: and one Act-sha: trailer"
    act, sha = acts[0].replace(" ", ""), shas[0].replace(" ", "")
    if not ACT_ID_RE.match(act) or not SHA_RE.match(sha):
        return False, "its Act: or Act-sha: is not an ACT id and a sha256"
    if not cto_approved(approvals, act, sha):
        return False, f"no line of the CTO's approvals log names {act} with that manifest and a CTO route"
    bundle, manifest = find_manifest(acts_dir, act, sha)
    if manifest is None or not isinstance(manifest, dict) or manifest.get("act") != act:
        return False, f"no manifest of {act} hashes as its Act-sha"
    if manifest.get("claimed_class") != "b":
        return False, f"the manifest claims class ({manifest.get('claimed_class')}), not (b)"
    if act_class.classify(bundle, rules)["class"] != "b":
        return False, "the classifier's vote on the ACT's bundle is not (b)"
    classes = {p: path_class(rules, p) for p in paths}
    if not classes or act_class.top(*classes.values()) != "b":
        return False, "the class of the commit's paths is not (b)"
    touched = manifest.get("touched")
    if not isinstance(touched, list) or not touched or any(not isinstance(t, dict) or t.get("root") != "repo"
                                                          for t in touched):
        return False, "the manifest's touched list is not a list of repository paths"
    if sorted(t.get("path") for t in touched) != sorted(paths):
        return False, "the commit's paths are not the manifest's touched list"
    return True, ""


def check(repo, rev_range, rules=None, approvals=None, acts_dir=None):
    rules = rules or act_class.load_rules()
    items = []
    commits = [c for c in git(repo, "rev-list", "--first-parent", rev_range).split() if c]
    for c in commits:
        parents = git(repo, "rev-list", "--parents", "-n", "1", c).split()[1:]
        if not parents:
            continue
        roles = trailer_values(repo, c, "Role")
        tasks = trailer_values(repo, c, "Task")
        if not outside_a_ticket(roles, tasks):
            continue
        if any(r.replace(" ", "") == "owner" for r in roles):
            continue
        acts = trailer_values(repo, c, "Act")
        if any(r.replace(" ", "") == "operator" for r in roles) and acts:
            continue
        paths = [p for p in git(repo, "-c", "core.quotePath=false", "diff", "--no-renames", "--name-only",
                                parents[0], c).splitlines() if p]
        hits = control_paths(rules, paths)
        if not hits:
            continue
        shas = trailer_values(repo, c, "Act-sha")
        route = ""
        if any(r.replace(" ", "") == "orchestrator" for r in roles) and acts and shas:
            ok, route = cto_route(rules, roles, acts, shas, paths, APPROVALS if approvals is None else approvals,
                                  ACTS_DIR if acts_dir is None else acts_dir)
            if ok:
                continue
            route = f"; the CTO's route refuses: {route}"
        subject = git(repo, "log", "-1", "--format=%s", c).strip()
        why = ("Role: operator without an Act: trailer" if any(r.replace(" ", "") == "operator" for r in roles)
               else "neither Role: owner nor Role: operator with Act:") + route
        items.append({"commit": c, "priority": "P1", "paths": [p for p, _ in hits],
                      "rows": sorted({r for _, r in hits}), "subject": subject[:200],
                      "reason": f"a commit outside a ticket touches a (b) or (O) control path, {why}"})
    return items


def main(argv):
    if len(argv) != 4 or argv[1] != "--repo":
        sys.stderr.write("usage: landing_check.py --repo <repo> <rev range>\n")
        return 2
    try:
        items = check(argv[2], argv[3])
    except Exception as exc:  # fail closed: a range it cannot read is an item for the owner, not silence
        print(json.dumps([{"commit": None, "priority": "P1", "paths": [], "rows": [],
                           "reason": f"the landing check could not read the range ({exc})"}]))
        return 1
    print(json.dumps(items))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

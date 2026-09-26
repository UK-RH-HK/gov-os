#!/usr/bin/env python3
"""Bridge orchestration state checker (non-product orchestration tooling).

verify          exit 0 when ORCHESTRATOR_STATE.yaml agrees with Git and the domain; else print
                ORCHESTRATION_STATE_CONFLICT with reasons and exit 2. Beyond the Phase-2 checks it enforces the
                bridge's own invariants:
                  * mutation boundary -- nothing outside the bridge domain differs from bridge_base_commit
                    (committed or uncommitted), so the frozen product and the Phase-2 records are untouched;
                  * the frozen product still resolves (branch tip == commit, product_code_digest recomputes);
                  * the Review-8 evidence objects at the review commit are the recorded blobs;
                  * owner records, Contract v3, the V8.2 panel and immutable evidence hash to recorded values;
                  * every COMPLETED run has a typed report and a builder checkpoint (see integrate-check).
checkpoint [--reason R] [--commit]   OD-BR-04: write + validate an outer lifecycle checkpoint (mechanical;
                safe to run from a PreCompact/SessionEnd hook). During a demonstration freeze it writes on the freeze
                side branch so the view does not move.
integrate-check RUN_ID   the ENFORCED checkpoint a run must pass before its branch may be merged: the branch's diff
                touches only the run's declared mutation_scope (all inside the domain), and the branch carries
                AGENT_RUNS/RUN_ID.report.yaml (typed return) and AGENT_RUNS/RUN_ID.checkpoint.yaml (commands,
                exit codes and output hashes). Exit 2 refuses integration.
seal            set updated_at (UTC) and state_hash (sha256 of the file with `state_hash: null`).
show            print the resume view.

Adapted from release/orchestration/phase-2/tools/check_state.py, which this tool never reads or writes.
"""
import datetime
import fnmatch
import hashlib
import os
import re
import subprocess
import sys

import yaml

DOMAIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.path.join(DOMAIN_DIR, "..", "..", ".."))
STATE = os.path.join(DOMAIN_DIR, "ORCHESTRATOR_STATE.yaml")
GATES = os.path.join(DOMAIN_DIR, "GATES", "GATE-REGISTER.yaml")
IDENTITY = os.path.join(ROOT, "release", "orchestration", "phase-2", "tools", "product_identity.py")
HEX = re.compile(r"^[0-9a-f]{7,40}$")

REPORT_KEYS = {"run_id", "role", "model_observed", "branch", "commit", "status", "claims", "evidence",
               "mutation_scope_respected", "open_issues"}
CHECKPOINT_KEYS = {"run_id", "commit", "commands"}
COMMAND_KEYS = {"cmd", "exit_code", "output_path", "output_sha256"}
# OD-BR-04 A: the worker completion checkpoint (schema 2) for every run dispatched after 2026-09-26 (checkpoint_schema: 2)
CHECKPOINT_V2_KEYS = CHECKPOINT_KEYS | {"role", "model_observed", "input_manifest", "task_contract", "artifacts_changed",
                                        "findings", "failed_approaches", "unresolved", "decisions", "lessons",
                                        "next_consumer", "final_commit"}
TASK_CONTRACT_KEYS = {"handoff_path", "handoff_sha256", "mutation_scope"}
# OD-BR-04 B: the outer-orchestrator lifecycle checkpoint
OUTER_CP_KEYS = {"id", "kind", "created_at", "reason", "lifecycle_id", "lifecycle_state", "state_source", "state_hash",
                 "bridge_tip", "role_branches", "freeze", "completed_runs", "running_work", "live_evidence",
                 "index_stores", "active_decisions", "open_findings", "evidence_status", "next_deterministic_action",
                 "resume", "content_sha256"}
CP_DIR = os.path.join(DOMAIN_DIR, "CHECKPOINTS")
SUBAGENT_GLOB = os.path.expanduser("~/.claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS/*/subagents/agent-*.jsonl")


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(None, None, f"duplicate key {key!r}", key_node.start_mark)
        seen.add(key)
    return loader.construct_mapping(node, deep)


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    with open(path, "rb") as fh:
        return sha256_bytes(fh.read())


def canonical_hash(text):
    body = re.sub(r"(?m)^state_hash:.*$", "state_hash: null", text)
    return hashlib.sha256(body.encode()).hexdigest()


def load_yaml_text(text):
    return yaml.load(text, Loader=UniqueKeyLoader)


def domain_rel():
    return os.path.relpath(DOMAIN_DIR, ROOT).replace(os.sep, "/")


def outside_domain(paths):
    prefix = domain_rel() + "/"
    return [p for p in paths if p and not p.startswith(prefix)]


def product_code_digest(commit):
    out = subprocess.run([sys.executable, IDENTITY, commit], capture_output=True, text=True).stdout
    m = re.search(r"product_code_digest: ([0-9a-f]{64})", out)
    return m.group(1) if m else None


def check_typed(doc, keys, label, problems):
    if not isinstance(doc, dict):
        problems.append(f"{label}: not a mapping")
        return False
    missing = sorted(keys - set(doc))
    if missing:
        problems.append(f"{label}: missing typed fields {missing}")
        return False
    return True


def check_checkpoint(doc, label, problems, read_output):
    if not check_typed(doc, CHECKPOINT_KEYS, label, problems):
        return
    cmds = doc.get("commands") or []
    if not cmds:
        problems.append(f"{label}: no commands recorded")
    for i, c in enumerate(cmds):
        if not check_typed(c, COMMAND_KEYS, f"{label}.commands[{i}]", problems):
            continue
        data = read_output(c["output_path"])
        if data is None:
            problems.append(f"{label}.commands[{i}]: output {c['output_path']} missing")
        elif sha256_bytes(data) != c["output_sha256"]:
            problems.append(f"{label}.commands[{i}]: output {c['output_path']} hash mismatch")


def check_checkpoint_v2(doc, label, problems, read_output, changed=None, branch=None):
    """OD-BR-04 A. A run whose state entry carries checkpoint_schema: 2 is complete only when this passes."""
    check_checkpoint(doc, label, problems, read_output)
    if not check_typed(doc, CHECKPOINT_V2_KEYS, label, problems):
        return
    tc = doc.get("task_contract") or {}
    check_typed(tc, TASK_CONTRACT_KEYS, f"{label}.task_contract", problems)
    for i, m in enumerate(doc.get("input_manifest") or []):
        if not isinstance(m, dict) or not {"path", "sha256"} <= set(m):
            problems.append(f"{label}.input_manifest[{i}]: needs path and sha256")
    if not doc.get("input_manifest"):
        problems.append(f"{label}: input_manifest is empty")
    if not str(doc.get("next_consumer") or "").strip():
        problems.append(f"{label}: next_consumer is empty")
    if changed is not None:
        listed = {str(a.get("path") if isinstance(a, dict) else a) for a in (doc.get("artifacts_changed") or [])}
        missing = [c for c in changed if c not in listed and not c.endswith((".checkpoint.yaml", ".report.yaml"))]
        if missing:
            problems.append(f"{label}: artifacts_changed omits {len(missing)} changed path(s), e.g. {missing[:3]}")
    if branch and git("merge-base", "--is-ancestor", str(doc.get("final_commit")), branch).returncode != 0:
        problems.append(f"{label}: final_commit {doc.get('final_commit')} is not on {branch}")


def latest_outer_checkpoint(cp_dir=CP_DIR):
    best = None
    if os.path.isdir(cp_dir):
        for f in os.listdir(cp_dir):
            m = re.match(r"BR-CP-(\d{4})\.yaml$", f)
            if m and (best is None or int(m.group(1)) > best[0]):
                best = (int(m.group(1)), os.path.join(cp_dir, f))
    return best


def verify(text, state):
    problems, notes = [], []
    if state.get("state_hash") and state["state_hash"] != canonical_hash(text):
        problems.append("state_hash does not match file content (edited after seal)")
    repo = state["repository"]
    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != repo["bridge_branch"]:
        problems.append(f"HEAD branch {branch!r} != bridge_branch {repo['bridge_branch']!r}")
    base = repo["bridge_base_commit"]
    last = repo.get("last_recorded_commit")
    for c in (base, last):
        if c and git("merge-base", "--is-ancestor", c, "HEAD").returncode != 0:
            problems.append(f"{c} is not an ancestor of HEAD")
    # mutation boundary: committed and uncommitted
    committed = git("diff", "--name-only", base, "HEAD").stdout.splitlines()
    uncommitted = [l[3:] for l in git("status", "--porcelain", "--untracked-files=all").stdout.splitlines()]
    for p in outside_domain(committed):
        problems.append(f"MUTATION BOUNDARY: committed change outside the bridge domain: {p}")
    for p in outside_domain(uncommitted):
        problems.append(f"MUTATION BOUNDARY: uncommitted change outside the bridge domain: {p}")
    # frozen product
    fp = state["frozen_phase_2_product"]
    tip = git("rev-parse", fp["branch"]).stdout.strip()
    if tip != fp["commit"]:
        problems.append(f"frozen product branch {fp['branch']} -> {tip}, recorded {fp['commit']} (product moved?)")
    d = product_code_digest(fp["commit"])
    if d != fp["product_code_digest"]:
        problems.append(f"frozen product_code_digest recomputes to {d}")
    # review 8 evidence
    r8 = state["review_8"]
    for path, blob in r8["evidence_objects_at_review_commit"].items():
        got = git("rev-parse", f"{r8['review_commit']}:{path}").stdout.strip()
        if got != blob:
            problems.append(f"review-8 evidence {path} at {r8['review_commit']} is {got or 'missing'}, recorded {blob}")
    # hashed anchors
    anchors = [state["contract_v3"], state["operator_ui"]] + list(state.get("owner_records", []))
    anchors += [{"path": r8["full_return_copy_path"], "sha256": r8["full_return_copy_sha256"]}]
    anchors += list(state.get("immutable_evidence", []))
    anchors += [i for i in (state.get("mandatory_bridge_inputs") or {}).get("items", []) if i.get("path") and i.get("sha256")]
    for a in anchors:
        p = os.path.join(ROOT, a["path"])
        if not os.path.isfile(p):
            problems.append(f"anchor missing: {a['path']}")
        elif a.get("sha256") and sha256_file(p) != a["sha256"]:
            problems.append(f"anchor {a['path']} hashes to {sha256_file(p)}, recorded {a['sha256']}")
    # every YAML in the domain parses without duplicate keys
    for dirpath, _, files in os.walk(DOMAIN_DIR):
        if "/.cache" in dirpath or "__pycache__" in dirpath:
            continue
        for f in files:
            if f.endswith((".yaml", ".yml")):
                fpath = os.path.join(dirpath, f)
                try:
                    with open(fpath) as fh:
                        yaml.load(fh, Loader=UniqueKeyLoader)
                except yaml.YAMLError as e:
                    problems.append(f"{os.path.relpath(fpath, ROOT)} invalid YAML: {str(e).splitlines()[0]}")
    # completed runs: typed report + checkpoint present in tree
    for run in state.get("agent_runs", []):
        if str(run.get("status", "")).startswith("COMPLETED") and run.get("requires_checkpoint", True):
            for kind, keys in (("report", REPORT_KEYS), ("checkpoint", CHECKPOINT_KEYS)):
                rp = os.path.join(DOMAIN_DIR, "AGENT_RUNS", f"{run['run_id']}.{kind}.yaml")
                if not os.path.isfile(rp):
                    problems.append(f"run {run['run_id']} {run['status']} but AGENT_RUNS/{run['run_id']}.{kind}.yaml missing")
                    continue
                with open(rp) as fh:
                    doc = yaml.load(fh, Loader=UniqueKeyLoader)
                if kind == "report":
                    check_typed(doc, keys, f"{run['run_id']}.report", problems)
                else:
                    check_checkpoint(doc, f"{run['run_id']}.checkpoint", problems,
                                     lambda p: open(os.path.join(ROOT, p), "rb").read()
                                     if os.path.isfile(os.path.join(ROOT, p)) else None)
    # OD-BR-04 A: schema-2 runs must carry the full worker completion checkpoint
    for run in state.get("agent_runs", []):
        if str(run.get("status", "")).startswith("COMPLETED") and run.get("checkpoint_schema") == 2:
            rp = os.path.join(DOMAIN_DIR, "AGENT_RUNS", f"{run['run_id']}.checkpoint.yaml")
            if os.path.isfile(rp):
                with open(rp) as fh:
                    check_checkpoint_v2(yaml.load(fh, Loader=UniqueKeyLoader), f"{run['run_id']}.checkpoint(v2)",
                                        problems, lambda p: open(os.path.join(ROOT, p), "rb").read()
                                        if os.path.isfile(os.path.join(ROOT, p)) else None)
    # OD-BR-04 B: once adopted, every sealed state must have an outer checkpoint captured for exactly that state
    if state.get("checkpoint_discipline") == "OD-BR-04":
        latest = latest_outer_checkpoint()
        if latest is None:
            problems.append("OD-BR-04: no outer checkpoint in CHECKPOINTS/")
        else:
            with open(latest[1]) as fh:
                cp = yaml.load(fh, Loader=UniqueKeyLoader)
            missing = sorted(OUTER_CP_KEYS - set(cp or {}))
            if missing:
                problems.append(f"OD-BR-04: {os.path.basename(latest[1])} lacks {missing}")
            elif cp.get("state_hash") != state.get("state_hash"):
                problems.append(f"OD-BR-04: latest outer checkpoint {os.path.basename(latest[1])} was captured for state "
                                f"{str(cp.get('state_hash'))[:12]}, not the current sealed state "
                                f"{str(state.get('state_hash'))[:12]} -- run `check_state.py checkpoint` after sealing")
            else:
                body = {k: v for k, v in cp.items() if k != "content_sha256"}
                if sha256_bytes(yaml.safe_dump(body, sort_keys=True).encode()) != cp.get("content_sha256"):
                    problems.append(f"OD-BR-04: {os.path.basename(latest[1])} content_sha256 does not match its content")
    # commit references resolve
    def leaves(node, path=()):
        if isinstance(node, dict):
            for k, v in node.items():
                yield from leaves(v, path + (str(k),))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                yield from leaves(v, path + (str(i),))
        else:
            yield path, node
    for path, value in leaves(state):
        key = next((p for p in reversed(path) if not p.isdigit()), "")
        if isinstance(value, str) and (key == "commit" or key.endswith("_commit")) and HEX.match(value):
            if git("cat-file", "-e", value + "^{commit}").returncode != 0:
                problems.append(f"{'.'.join(path)}: commit {value} not found")
    notes.append(f"HEAD {git('rev-parse', 'HEAD').stdout.strip()} on {branch}; {len(uncommitted)} uncommitted entries")
    return problems, notes


def integrate_check(state, run_id):
    problems = []
    run = next((r for r in state.get("agent_runs", []) if r["run_id"] == run_id), None)
    if run is None:
        return [f"run {run_id} not in agent_runs"]
    br = run.get("branch")
    if not br or git("rev-parse", "--verify", br).returncode != 0:
        return [f"run {run_id}: branch {br!r} does not resolve"]
    target = state["repository"]["bridge_branch"]
    mb = git("merge-base", target, br).stdout.strip()
    changed = git("diff", "--name-only", mb, br).stdout.splitlines()
    scope = run.get("mutation_scope") or []
    prefix = domain_rel() + "/"
    for s in scope:
        if not s.startswith(prefix):
            problems.append(f"declared mutation_scope entry outside the domain: {s}")
    for p in changed:
        if not any(fnmatch.fnmatch(p, s) for s in scope):
            problems.append(f"{br} changes {p}, outside run {run_id}'s mutation_scope")
    def read_on_branch(p):
        r = subprocess.run(["git", "-C", ROOT, "show", f"{br}:{p}"], capture_output=True)
        return r.stdout if r.returncode == 0 else None
    for kind, keys in (("report", REPORT_KEYS), ("checkpoint", CHECKPOINT_KEYS)):
        rel = f"{prefix}AGENT_RUNS/{run_id}.{kind}.yaml"
        data = read_on_branch(rel)
        if data is None:
            problems.append(f"{br} lacks {rel}")
            continue
        try:
            doc = load_yaml_text(data.decode())
        except yaml.YAMLError as e:
            problems.append(f"{rel} invalid YAML: {str(e).splitlines()[0]}")
            continue
        if kind == "report":
            if check_typed(doc, keys, rel, problems):
                if git("merge-base", "--is-ancestor", str(doc["commit"]), br).returncode != 0:
                    problems.append(f"{rel}: reported commit {doc['commit']} is not on {br}")
                if doc.get("mutation_scope_respected") is not True:
                    problems.append(f"{rel}: mutation_scope_respected is not true")
        elif run.get("checkpoint_schema") == 2:
            check_checkpoint_v2(doc, rel, problems, read_on_branch, changed=changed, branch=br)
        else:
            check_checkpoint(doc, rel, problems, read_on_branch)
    return problems


def show(state):
    print(f"lifecycle {state['lifecycle_id']} ({state['lifecycle_name']})")
    print(f"build-stage token {state['build_stage_token']}  acceptance token {state['acceptance_token']} (not ours)")
    print(f"state {state['lifecycle_state']}  loop {state['loop_status']}  updated {state.get('updated_at')}")
    r = state["repository"]
    print(f"branch {r['bridge_branch']}  worktree {r['bridge_worktree']}  last_recorded {r['last_recorded_commit']}")
    print(f"frozen product {state['frozen_phase_2_product']['commit']}  review-8 {state['review_8']['verdict']} at {state['review_8']['review_commit']}")
    for run in state.get("agent_runs", []):
        print(f"run {run['run_id']:<11} {run.get('role',''):<34} {run.get('status','')}  model {run.get('model_observed','?')}")
    if os.path.exists(GATES):
        with open(GATES) as fh:
            for g in (yaml.safe_load(fh) or {}).get("gates", []):
                print(f"gate {g['id']:<40} {g['status']}")
    for q in state.get("unresolved_questions", []):
        print("open:", q if isinstance(q, str) else q.get("id"))
    print("next:", " ".join(str(state["next_deterministic_action"]).split()))


def _worktrees():
    out, cur = [], {}
    for line in git("worktree", "list", "--porcelain").stdout.splitlines():
        if line.startswith("worktree "):
            cur = {"path": line[9:]}
            out.append(cur)
        elif line.startswith("branch "):
            cur["branch"] = line[7:].replace("refs/heads/", "")
    return out


def cmd_checkpoint(reason, do_commit, next_override=None):
    """OD-BR-04 B/C: write and validate an outer-orchestrator lifecycle checkpoint, mechanically (no model needed),
    so a hook can run it before compaction or session end. The sealed state is read from the working file when this
    tool runs in the bridge worktree, and from the bridge branch ref otherwise (a freeze side branch). During a
    demonstration freeze the checkpoint is written to the freeze side-branch worktree so the view does not move."""
    here_branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    with open(STATE) as fh:
        local = load_yaml_text(fh.read())
    bridge_branch = local["repository"]["bridge_branch"]
    rel_state = f"{domain_rel()}/ORCHESTRATOR_STATE.yaml"
    if here_branch == bridge_branch:
        state_text, state_source = open(STATE).read(), f"working file on {bridge_branch}"
    else:
        state_text = git("show", f"{bridge_branch}:{rel_state}").stdout
        state_source = f"git show {bridge_branch}:{rel_state}"
    state = load_yaml_text(state_text)
    freeze = state.get("demonstration_freeze") or {}
    home_domain = DOMAIN_DIR
    wts = _worktrees()
    if str(freeze.get("status", "")).startswith("IN FORCE") and here_branch == bridge_branch:
        side = [w for w in wts if w.get("branch", "").startswith("bridge/orch-pending-")]
        if side:
            home_domain = os.path.join(side[-1]["path"], domain_rel())
    cp_dir = os.path.join(home_domain, "CHECKPOINTS")
    os.makedirs(cp_dir, exist_ok=True)
    nums = [latest_outer_checkpoint(cp_dir)]
    for ref in [bridge_branch] + [w["branch"] for w in wts if w.get("branch", "").startswith("bridge/orch-pending-")]:
        for name in git("ls-tree", "--name-only", f"{ref}:{domain_rel()}/CHECKPOINTS").stdout.split():
            m = re.match(r"BR-CP-(\d{4})\.yaml$", name)
            if m:
                nums.append((int(m.group(1)), name))
    n = max([x[0] for x in nums if x] + [0]) + 1
    role_branches = {}
    for line in git("for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads/bridge/").stdout.splitlines():
        b, c = line.split()
        role_branches[b] = c
    live = {"python_processes": [], "recent_subagent_transcripts": []}
    own = {str(os.getpid()), str(os.getppid())}
    for pid in os.listdir("/proc"):
        if not pid.isdigit() or pid in own:  # never report this checker (or its shell) as live work
            continue
        try:
            comm = open(f"/proc/{pid}/comm").read().strip()
            cwd = os.readlink(f"/proc/{pid}/cwd")
        except OSError:
            continue
        if comm.startswith("python") and "/.claude/worktrees/" in cwd and ("/br" in cwd or "bridge-p2" in cwd):
            cmdline = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace")[:200]
            live["python_processes"].append({"pid": int(pid), "cwd": cwd, "cmdline": cmdline})
    import glob, time
    now = time.time()
    for f in glob.glob(SUBAGENT_GLOB):
        age = now - os.path.getmtime(f)
        if age < 900:
            meta = f[:-6] + ".meta.json"
            name = None
            if os.path.isfile(meta):
                import json
                name = json.load(open(meta)).get("name")
            live["recent_subagent_transcripts"].append({"name": name, "transcript": os.path.basename(f),
                                                        "seconds_since_last_write": int(age)})
    stores = {}
    for run in state.get("agent_runs", []):
        if run.get("store"):
            stores[run["store"]] = None
    if freeze.get("demonstration_store"):
        stores[str(freeze["demonstration_store"]).split(" ")[0]] = None
    for s in list(stores):
        mp = os.path.join(os.path.expandvars(s), "manifest.json")
        if os.path.isfile(mp):
            import json
            try:
                stores[s] = json.load(open(mp)).get("manifest", {}).get("manifest_sha256")
            except ValueError:
                stores[s] = "UNREADABLE"
        else:
            stores[s] = "ABSENT"
    pending = os.path.join(home_domain, "PENDING-STATE-UPDATES.md")
    cp = {
        "id": f"BR-CP-{n:04d}",
        "kind": "CONTEMPORANEOUS",
        "created_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reason": reason,
        "lifecycle_id": state.get("lifecycle_id"),
        "lifecycle_state": state.get("lifecycle_state"),
        "loop_status": state.get("loop_status"),
        "state_source": state_source,
        "state_hash": state.get("state_hash"),
        "bridge_tip": git("rev-parse", bridge_branch).stdout.strip(),
        "written_in_worktree_branch": git("-C", home_domain, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip(),
        "role_branches": role_branches,
        "freeze": freeze,
        "pending_state_updates": ({"path": os.path.relpath(pending, ROOT) if pending.startswith(ROOT) else pending,
                                   "sha256": sha256_file(pending)} if os.path.isfile(pending) else None),
        "completed_runs": [{"run_id": r["run_id"], "status": r.get("status"),
                            "final_commit": r.get("final_commit") or (r.get("pass_1") or {}).get("final_commit"),
                            "model_observed": r.get("model_observed")}
                           for r in state.get("agent_runs", []) if str(r.get("status", "")).startswith(("COMPLETED", "AWAITING"))],
        "running_work": state.get("running_work", []),
        "live_evidence": live,
        "index_stores": stores,
        "active_decisions": {"owner_records": [o.get("id") for o in state.get("owner_records", [])],
                             "rulings": [r.get("id") for r in state.get("rulings", [])],
                             "dag_amendments": [a.get("id") for a in (state.get("dag") or {}).get("amendments", [])]},
        "open_findings": {"observations": [o.get("id") for o in state.get("observations", [])],
                          "unresolved_questions": state.get("unresolved_questions", [])},
        "evidence_status": state.get("evidence_status"),
        "next_deterministic_action": next_override or state.get("next_deterministic_action"),
        "next_action_source": ("orchestrator --next (the sealed state is frozen; see pending_state_updates)"
                               if next_override else "sealed state"),
        "state_next_action_as_sealed": state.get("next_deterministic_action"),
        "resume": ("A fresh outer session resumes from THIS file: (1) `git worktree list`; (2) in the bridge worktree run "
                   "`python3 release/orchestration/phase-2-context-bridge/tools/check_state.py show` then `verify`; "
                   "(3) read ORCHESTRATOR_STATE.yaml, the newest PHASE_LEDGER.md entry, and -- if pending_state_updates "
                   "is set -- that file on its side branch; (4) for every run in running_work check liveness from its "
                   "transcript and branch, never from elapsed time; (5) execute next_deterministic_action."),
    }
    cp["content_sha256"] = sha256_bytes(yaml.safe_dump({k: v for k, v in cp.items()}, sort_keys=True).encode())
    missing = sorted(OUTER_CP_KEYS - set(cp))
    bad = [f"{k}={v}" for k, v in role_branches.items() if git("cat-file", "-e", v + "^{commit}").returncode != 0]
    if missing or bad:
        print("CHECKPOINT_INVALID", missing, bad)
        sys.exit(2)
    path = os.path.join(cp_dir, f"{cp['id']}.yaml")
    with open(path, "w") as fh:
        yaml.safe_dump(cp, fh, sort_keys=False, width=140)
    back = yaml.load(open(path), Loader=UniqueKeyLoader)
    body = {k: v for k, v in back.items() if k != "content_sha256"}
    if sha256_bytes(yaml.safe_dump(body, sort_keys=True).encode()) != back["content_sha256"]:
        print("CHECKPOINT_INVALID content hash does not round-trip")
        sys.exit(2)
    if do_commit:
        g = lambda *a: subprocess.run(["git", "-C", home_domain, *a], capture_output=True, text=True)
        g("add", os.path.relpath(path, home_domain))
        r = g("commit", "-q", "-m", f"Bridge: outer checkpoint {cp['id']} ({reason})\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
              "--", os.path.relpath(path, home_domain))  # commit ONLY the checkpoint file, never other staged work
        print("committed" if r.returncode == 0 else f"commit failed: {r.stderr.strip()[:200]}")
    print(f"CHECKPOINT_WRITTEN {cp['id']} {path} state_hash={str(cp['state_hash'])[:12]}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    with open(STATE) as fh:
        text = fh.read()
    try:
        state = load_yaml_text(text)
    except yaml.YAMLError as e:
        print("ORCHESTRATION_STATE_CONFLICT")
        print(" - YAML error (duplicate keys are refused):", e)
        sys.exit(2)
    if cmd == "seal":
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        text = re.sub(r"(?m)^updated_at:.*$", f"updated_at: '{now}'", text)
        text = re.sub(r"(?m)^state_hash:.*$", "state_hash: null", text)
        text = re.sub(r"(?m)^state_hash:.*$", f"state_hash: {canonical_hash(text)}", text)
        with open(STATE, "w") as fh:
            fh.write(text)
        print(f"sealed {now}")
    elif cmd == "verify":
        problems, notes = verify(text, state)
        for n in notes:
            print(n)
        if problems:
            print("ORCHESTRATION_STATE_CONFLICT")
            for p in problems:
                print(" -", p)
            sys.exit(2)
        print("STATE_CONSISTENT")
    elif cmd == "integrate-check":
        problems = integrate_check(state, sys.argv[2])
        if problems:
            print("INTEGRATION_REFUSED")
            for p in problems:
                print(" -", p)
            sys.exit(2)
        print("INTEGRATION_PERMITTED")
    elif cmd == "checkpoint":
        reason = "manual"
        if "--reason" in sys.argv:
            reason = sys.argv[sys.argv.index("--reason") + 1]
        nxt = sys.argv[sys.argv.index("--next") + 1] if "--next" in sys.argv else None
        cmd_checkpoint(reason, "--commit" in sys.argv, nxt)
    elif cmd == "show":
        show(state)
    else:
        sys.exit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()

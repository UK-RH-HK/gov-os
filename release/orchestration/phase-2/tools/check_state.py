#!/usr/bin/env python3
"""Phase 2 orchestration state checker (non-product tooling).

verify  exit 0 when ORCHESTRATOR_STATE.yaml agrees with Git and the evidence tree;
        otherwise print ORCHESTRATION_STATE_CONFLICT with reasons and exit 2.
        Also checks: the Contract v3 owner source and the V8.2 control panel still hash to the recorded values,
        every candidate tag resolves to its recorded commit, every candidate's product_code_digest recomputes,
        every COMPLETED run has its report, and the YAML carries no duplicate keys.
seal    set updated_at (UTC) and state_hash (sha256 of the file with `state_hash: null`).
show    print the resume view: lifecycle, candidate, gates, running work, next action.

Adapted from release/orchestration/phase-1/tools/check_state.py; Phase-1 state is never read or written by this tool.
"""
import datetime
import hashlib
import os
import re
import subprocess
import sys

import yaml

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(PHASE_DIR, "ORCHESTRATOR_STATE.yaml")
GATES = os.path.join(PHASE_DIR, "GATES", "GATE-REGISTER.yaml")
IDENTITY = os.path.join(PHASE_DIR, "tools", "product_identity.py")
HEX = re.compile(r"^[0-9a-f]{7,40}$")


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


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def canonical_hash(text):
    body = re.sub(r"(?m)^state_hash:.*$", "state_hash: null", text)
    return hashlib.sha256(body.encode()).hexdigest()


def leaves(node, path=()):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from leaves(v, path + (str(k),))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from leaves(v, path + (str(i),))
    else:
        yield path, node


def key_of(path):
    for part in reversed(path):
        if not part.isdigit():
            return part
    return ""


def product_code_digest(commit):
    out = subprocess.run([sys.executable, IDENTITY, commit], capture_output=True, text=True).stdout
    m = re.search(r"product_code_digest: ([0-9a-f]{64})", out)
    return m.group(1) if m else None


def verify(text, state):
    problems, notes = [], []
    if state.get("state_hash") and state["state_hash"] != canonical_hash(text):
        problems.append("state_hash does not match file content (edited after seal)")
    repo = state["repository"]
    root = repo["path"]
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != repo["integration_branch"]:
        problems.append(f"HEAD branch {branch!r} != integration_branch {repo['integration_branch']!r}")
    last = repo.get("last_recorded_commit")
    if last and git(root, "merge-base", "--is-ancestor", last, "HEAD").returncode != 0:
        problems.append(f"last_recorded_commit {last} is not an ancestor of HEAD")
    for anchor in ("contract_v3", "operator_ui"):
        a = state.get(anchor, {})
        p = os.path.join(root, a.get("path", ""))
        if not os.path.isfile(p):
            problems.append(f"{anchor}: {a.get('path')} missing")
        elif sha256_file(p) != a.get("sha256"):
            problems.append(f"{anchor}: {a.get('path')} hashes to {sha256_file(p)}, recorded {a.get('sha256')}")
    for cand in state.get("candidates", []):
        tag, commit = cand.get("tag"), cand.get("commit")
        if tag and commit:
            r = git(root, "rev-list", "-n1", tag)
            if r.returncode != 0 or r.stdout.strip() != commit:
                problems.append(f"candidate {cand.get('id')}: tag {tag} -> {r.stdout.strip() or 'missing'}, recorded {commit}")
        if commit and cand.get("product_code_digest"):
            d = product_code_digest(commit)
            if d != cand["product_code_digest"]:
                problems.append(f"candidate {cand.get('id')}: product_code_digest recomputes to {d}")
    try:
        with open(GATES) as fh:
            yaml.load(fh, Loader=UniqueKeyLoader)
    except (yaml.YAMLError, OSError) as e:
        problems.append(f"GATES/GATE-REGISTER.yaml is not valid YAML: {str(e).splitlines()[0]}")
    for rf in sorted(os.listdir(os.path.join(PHASE_DIR, "AGENT_RUNS"))):
        if rf.endswith(".yaml"):
            try:
                with open(os.path.join(PHASE_DIR, "AGENT_RUNS", rf)) as fh:
                    yaml.load(fh, Loader=UniqueKeyLoader)
            except yaml.YAMLError as e:
                problems.append(f"AGENT_RUNS/{rf} is not valid YAML (or has duplicate keys): {str(e).splitlines()[0]}")
    for run in state.get("agent_runs", []):
        if str(run.get("status", "")).startswith("COMPLETED"):
            rp = os.path.join(PHASE_DIR, "AGENT_RUNS", f"{run['run_id']}.report.yaml")
            if not os.path.isfile(rp):
                # a run completed but not yet integrated keeps its report on its own branch until merged
                rel = os.path.relpath(rp, root)
                on_branch = run.get("branch") and git(root, "cat-file", "-e", f"{run['branch']}:{rel}").returncode == 0
                if not (run["status"] == "COMPLETED_AWAITING_INTEGRATION" and on_branch):
                    problems.append(f"run {run['run_id']} {run['status']} but its report is missing (checked tree and branch)")
    for path, value in leaves(state):
        key = key_of(path)
        if not isinstance(value, str):
            continue
        if (key == "commit" or key.endswith("_commit")) and HEX.match(value):
            if git(root, "cat-file", "-e", value + "^{commit}").returncode != 0:
                problems.append(f"{'.'.join(path)}: commit {value} not found")
        elif (key.endswith("_path") or key.endswith("_paths") or key == "path") and not key.startswith("expected_"):
            if value and not value.startswith("/") and not os.path.exists(os.path.join(root, value)):
                problems.append(f"{'.'.join(path)}: path {value} missing")
    for item in state.get("immutable_evidence", []):
        p, c = item["path"], item["commit"]
        if git(root, "diff", "--quiet", c, "HEAD", "--", p).returncode != 0:
            problems.append(f"immutable evidence {p} changed since {c}")
        if git(root, "diff", "--quiet", "--", p).returncode != 0:
            problems.append(f"immutable evidence {p} has uncommitted modifications")
    dirty = git(root, "status", "--porcelain").stdout.splitlines()
    notes.append(f"HEAD {git(root, 'rev-parse', 'HEAD').stdout.strip()} on {branch}; {len(dirty)} uncommitted entries")
    for line in dirty[:20]:
        notes.append("  " + line)
    return problems, notes


def show(state):
    print(f"phase {state['phase']} ({state['phase_name']})  target {state['target_token']}")
    print(f"lifecycle {state['lifecycle_state']}  loop {state['loop_status']}  updated {state.get('updated_at')}")
    print(f"branch {state['repository']['integration_branch']}  last_recorded {state['repository']['last_recorded_commit']}")
    cur = state.get("current_candidate") or {}
    print(f"candidate {cur.get('id')} {cur.get('commit')} tag {cur.get('tag')}")
    it = state.get("iteration", {})
    print(f"iteration {it.get('current')}  consecutive_new_class_iterations {it.get('consecutive_new_class_iterations')}")
    print(f"owner gates pending {state['owner_gates']['pending']}")
    for run in state.get("running_work", []):
        print(f"running {run['run_id']} {run['role']} {run['status']} -> {run.get('run_record_path')}")
    if os.path.exists(GATES):
        with open(GATES) as fh:
            for g in yaml.safe_load(fh)["gates"]:
                print(f"gate {g['id']:<36} {g['status']}")
    print("next:", " ".join(str(state["next_deterministic_action"]).split()))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    with open(STATE) as fh:
        text = fh.read()
    try:
        state = yaml.load(text, Loader=UniqueKeyLoader)
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
    elif cmd == "show":
        show(state)
    else:
        sys.exit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Phase 1 orchestration state checker (non-product tooling).

verify  exit 0 when ORCHESTRATOR_STATE.yaml agrees with Git and the evidence tree;
        otherwise print ORCHESTRATION_STATE_CONFLICT with reasons and exit 2.
seal    set updated_at (UTC) and state_hash (sha256 of the file with `state_hash: null`).
show    print the resume view: lifecycle, gates, running work, next action.
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
HEX = re.compile(r"^[0-9a-f]{7,40}$")


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)


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
    for path, value in leaves(state):
        key = key_of(path)
        if not isinstance(value, str):
            continue
        if (key == "commit" or key.endswith("_commit")) and HEX.match(value):
            if git(root, "cat-file", "-e", value + "^{commit}").returncode != 0:
                problems.append(f"{'.'.join(path)}: commit {value} not found")
        elif (key.endswith("_path") or key.endswith("_paths")) and not key.startswith("expected_"):
            if not value.startswith("/") and not os.path.exists(os.path.join(root, value)):
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
    print(f"phase {state['phase']}  lifecycle {state['lifecycle_state']}  updated {state.get('updated_at')}")
    print(f"branch {state['repository']['integration_branch']}  last_recorded {state['repository']['last_recorded_commit']}")
    arch = state.get("architecture", {})
    print(f"architecture rev {arch.get('current_revision')}  accepted {arch.get('latest_accepted_revision')}  "
          f"rejected {arch.get('latest_rejected_revision')}  streak {arch.get('orchestrated_rejection_streak')}")
    print(f"owner gates pending {state['owner_gates']['pending']}")
    print(f"capability contract {state['capability_contract']['upload_state']}  prompt2 {state['prompt2']['status']}")
    for run in state.get("running_work", []):
        print(f"running {run['run_id']} {run['role']} {run['status']} -> {run['run_record_path']}")
    if os.path.exists(GATES):
        with open(GATES) as fh:
            for g in yaml.safe_load(fh)["gates"]:
                print(f"gate {g['id']:<24} {g['status']}")
    print("next:", " ".join(str(state["next_deterministic_action"]).split()))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    with open(STATE) as fh:
        text = fh.read()
    state = yaml.safe_load(text)
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

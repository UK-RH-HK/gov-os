"""The planted launch script (``--launch <file>``; W2-172 Interface items 1 and 2).

Called as the real ``indep_launch.py`` is called (``<py> <this file> --sets-root R --kind K --brief B --brief-sha256 H
--commit C --set A [--round N] [--audit A]``). It logs the call, answers from a plan, and on a delivery writes what the
real script would write, in the planted sets root and the planted runs folder: a writer's set (and a SEEDS.log line), a
checker's notes ``XCHECK-r<n>.md``, an auditor's ``miss-classes.json`` and the ``AUDITS.log`` line. Standard output
ends with the counts object (``indep-counts.schema.json``'s keys), after one noise line that the driver must not print.

Files: the state folder named by ``W172_STATE``:
  ``world.json``         ``{"delivery": <folder>, "audit_commit": <sha>}``
  ``launch_plan.json``   ``{"<step>": [<spec for the 1st call>, <spec for the 2nd>, ...]}`` (the last spec repeats);
                          a step is ``writer-1``, ``checker-1``, ``writer-2``, ``checker-2`` or ``auditor``; a spec:
                          ``exit`` (default 0), ``cost`` (the session's cost_usd, default 0.25), ``sleep`` (seconds,
                          before answering), ``remove`` (ids a writer does not deliver), ``rewrite_commit`` (a sha put in
                          each delivered question's ``commit``), ``revise`` / ``reject`` (ids a checker marks),
                          ``revise_n`` / ``rejected_n`` (override the counts a checker reports), ``no_audits_line``.
  ``launch_calls.jsonl`` one line per call: the step, the argv, the cwd, the runs folder the environment names, and for
                          an auditor whether ``misses.jsonl`` existed and how many lines it held.
"""
import fcntl
import json
import os
import shutil
import sys
import time

STATE = os.environ.get("W172_STATE") or os.path.join(os.path.dirname(os.path.realpath(__file__)), "state")
CLASSES = ("gold_wrong", "question_ambiguous", "out_of_scope", "retrieval_miss", "answer_wrong")
REASONS = {10: "brief", 11: "template", 12: "wall_exists", 13: "seed_order", 14: "commit", 15: "file_budget",
           16: "canary", 17: "argument", 18: "rules", 20: "result", 21: "stopped", 22: "trace"}
NOISE = "launch stub noise line: nothing here may be printed by the driver"
STDERR_WORD = "stubstderrmarker"


def parse(argv):
    flags, i = {}, 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--") and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            flags[a], i = argv[i + 1], i + 2
        else:
            flags[a], i = True, i + 1
    return flags


def locked_append(name, text):
    fd = os.open(os.path.join(STATE, name), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, text.encode("utf-8"))
    finally:
        os.close(fd)


def read_json(name, default):
    try:
        with open(os.path.join(STATE, name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def calls_so_far(step):
    path = os.path.join(STATE, "launch_calls.jsonl")
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as f:
        return sum(1 for x in f if x.strip() and json.loads(x).get("step") == step)


def counts_object(flags, kind, code, spec, rnd, delivered_files, revise, rejected, checked):
    status = ("delivered" if code == 0 else "rejected" if code == 20 else "stopped" if code in (21, 22) else "refused")
    out = {k: None for k in ("schema_ok", "files", "questions", "by_kind", "by_area", "checked", "accepted", "revise",
                             "rejected", "misses", "labelled", "allow", "refuse", "agree", "disagree")}
    if code == 0 and kind == "checker":
        out.update(schema_ok=True, checked=checked, accepted=checked - revise - rejected, revise=revise,
                   rejected=rejected)
    elif code == 0 and kind == "writer":
        out.update(schema_ok=True, files=delivered_files, questions=delivered_files)
    elif code == 0 and kind == "auditor":
        out.update(schema_ok=True, misses=delivered_files)
    return {
        "act": "ACT-INDEP-WALLS-1", "kind": kind, "run": f"20261110T120000Z-{kind}-r{rnd or 1}",
        "set": flags.get("--set"), "round": rnd, "commit": flags.get("--commit"),
        "brief_sha256": flags.get("--brief-sha256"), "approved_sha256": flags.get("--brief-sha256"),
        "seed_sha256": None, "effort": None, "template_ok": True, "override": False,
        "selection": {"changed": None, "sample": None, "overlap": None},
        "session": {"exit": 0, "is_error": False, "turns": 1, "cost_usd": float(spec.get("cost", 0.25)),
                    "duration_s": 1.0, "refusals": {}},
        "out": out, "delivered": {"files": delivered_files if code == 0 else None, "sha256": None,
                                  "to": {"writer": "set", "checker": "notes", "auditor": "classes"}[kind]
                                  if code == 0 else None},
        "traces": 0, "status": status, "code": code, "reason": REASONS.get(code),
    }


def set_dir(flags):
    return os.path.join(flags["--sets-root"], "fixtures", "evaluation", flags["--set"])


def deliver_writer(flags, spec, world):
    dst = set_dir(flags)
    shutil.copytree(world["delivery"], dst, dirs_exist_ok=True)
    hidden = os.path.join(dst, "hidden")
    for qid in spec.get("remove", []):
        os.unlink(os.path.join(hidden, qid + ".yaml"))
    if spec.get("rewrite_commit"):
        for name in os.listdir(hidden):
            path = os.path.join(hidden, name)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            with open(path, "w", encoding="utf-8") as f:
                f.write(text.replace(world["audit_commit"], spec["rewrite_commit"]))
    runs = os.environ.get("GOV_INDEP_RUNS_DIR")
    if runs:
        os.makedirs(os.path.join(runs, "indep"), exist_ok=True)
        seed = 424242
        import hashlib
        with open(os.path.join(runs, "indep", "SEEDS.log"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"time": "2026-11-10T01:00:00Z", "kind": "writer", "run": "writer-1",
                                "commit": flags.get("--commit"), "seed": seed,
                                "seed_sha256": hashlib.sha256(f"{seed}\n".encode()).hexdigest(),
                                "set": flags.get("--set"), "round": 1, "dry": False}) + "\n")
    return len([n for n in os.listdir(hidden) if n.endswith(".yaml")])


def deliver_checker(flags, spec, rnd):
    dst = set_dir(flags)
    hidden = os.path.join(dst, "hidden")
    ids = sorted(n[:-5] for n in os.listdir(hidden) if n.startswith("q") and n.endswith(".yaml"))
    revise, reject = set(spec.get("revise", [])), set(spec.get("reject", []))
    lines = ["# Cross-check notes", "## Questions"]
    for qid in ids:
        if qid in reject:
            lines.append(f"{qid} | reject | R1-WRONG | also: none | the anchor does not hold.")
        elif qid in revise:
            lines.append(f"{qid} | revise | R1-WRONG | also: none | the anchor needs a new line.")
        else:
            lines.append(f"{qid} | accept | - | also: none | the anchor holds the deciding line.")
    lines += ["## The set", "domains: code 14, decisions 8, tickets 4, plan 4, contract 4, none 6",
              "keyword: any 1, all 0", "set codes: none"]
    with open(os.path.join(dst, f"XCHECK-r{rnd}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return len(ids), len(revise & set(ids)), len(reject & set(ids))


def deliver_auditor(flags, spec):
    sets = flags["--sets-root"]
    audit = flags["--audit"]
    run = os.path.join(sets, "runs", audit)
    misses = os.path.join(run, "misses.jsonl")
    ids = []
    if os.path.exists(misses):
        with open(misses, encoding="utf-8") as f:
            ids = [json.loads(x)["id"] for x in f if x.strip()]
    if ids:
        with open(os.path.join(run, "miss-classes.json"), "w", encoding="utf-8") as f:
            json.dump({qid: {"class": CLASSES[k % 5], "reason": "planted"} for k, qid in enumerate(sorted(ids))}, f)
    runs = os.environ.get("GOV_INDEP_RUNS_DIR")
    if runs and not spec.get("no_audits_line"):
        os.makedirs(os.path.join(runs, "indep"), exist_ok=True)
        with open(os.path.join(runs, "indep", "AUDITS.log"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"time": "2026-11-10T13:00:00Z", "commit": flags.get("--commit"),
                                "run": "20261110T130000Z-auditor-r1", "audit": audit}) + "\n")
    return len(ids)


def main():
    argv = sys.argv[1:]
    flags = parse(argv)
    kind = flags.get("--kind")
    rnd = int(flags["--round"]) if flags.get("--round") not in (None, True) else None
    step = "auditor" if kind == "auditor" else f"{kind}-{rnd}"
    os.makedirs(STATE, exist_ok=True)
    world = read_json("world.json", {})
    plan = read_json("launch_plan.json", {})
    n = calls_so_far(step)
    specs = plan.get(step) or [{}]
    spec = specs[min(n, len(specs) - 1)]
    entry = {"step": step, "argv": argv, "cwd": os.getcwd(), "runs": os.environ.get("GOV_INDEP_RUNS_DIR"), "n": n + 1}
    if kind == "auditor":
        misses = os.path.join(flags.get("--sets-root", ""), "runs", flags.get("--audit", ""), "misses.jsonl")
        entry["misses_exists"] = os.path.exists(misses)
        entry["misses_lines"] = (sum(1 for x in open(misses, encoding="utf-8") if x.strip())
                                 if os.path.exists(misses) else None)
    locked_append("launch_calls.jsonl", json.dumps(entry) + "\n")
    if spec.get("sleep"):
        time.sleep(float(spec["sleep"]))
    sys.stderr.write(STDERR_WORD + "\n")
    print(NOISE)
    code = int(spec.get("exit", 0))
    files, revise, rejected, checked = 0, 0, 0, 0
    if code == 0:
        if kind == "writer" and rnd == 1:
            files = deliver_writer(flags, spec, world)
        elif kind == "writer":
            files = len([x for x in os.listdir(os.path.join(set_dir(flags), "hidden")) if x.endswith(".yaml")])
        elif kind == "checker":
            checked, revise, rejected = deliver_checker(flags, spec, rnd)
            revise = int(spec.get("revise_n", revise))
            rejected = int(spec.get("rejected_n", rejected))
        elif kind == "auditor":
            files = deliver_auditor(flags, spec)
    print(json.dumps(counts_object(flags, kind, code, spec, rnd, files, revise, rejected, checked)))
    return code


if __name__ == "__main__":
    sys.exit(main())

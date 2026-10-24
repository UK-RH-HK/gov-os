"""W2-67 batch 6's planted faults (lens I2 §2.7), applied to ``gov.close`` as it loads in a ``gov`` process.

``GOV_TD6_PLANT`` names one fault; ``GOV_TD6_MARKER`` is a file that gets a line each time the planted behaviour
runs, so a run shows that the plant reached the ``gov close`` the case started. Nothing here writes a source file.
"""

import hashlib
import importlib.machinery
import os
import sys

PLANT = os.environ.get("GOV_TD6_PLANT", "")
MARKER = os.environ.get("GOV_TD6_MARKER", "")


def mark(what):
    if MARKER:
        with open(MARKER, "a", encoding="utf-8") as told:
            told.write(f"{PLANT} pid={os.getpid()} argv={' '.join(sys.argv[1:3])}: {what}\n")


ZERO = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}


def command(m):
    if PLANT == "PF1":  # DISPOSITIONS loses "owner"
        m.DISPOSITIONS = tuple(name for name in m.DISPOSITIONS if name != "owner")
        run = m.run

        def planted_run(root, args, config):
            if getattr(args, "disposition", None) == "owner":
                mark("--disposition owner meets the planted DISPOSITIONS without owner")
            return run(root, args, config)
        m.run = planted_run
    elif PLANT == "PF2":  # a refusal with a class no longer says the context failed (details["context"])
        refuse = m._refuse

        def planted_refuse(root, ticket, code, message, lines, details, **named):
            if "context" in details:
                details = {key: value for key, value in details.items() if key != "context"}
                mark("details['context'] dropped from the refusal")
            else:
                mark(f"_refuse reached without details['context'] (code {code}): the planted line is not on this path")
            return refuse(root, ticket, code, message, lines, details, **named)
        m._refuse = planted_refuse
    elif PLANT == "PF2b":  # a refusal with a class records a fallback context hash when no context was built
        refuse_for = m._refuse_for

        def planted_refuse_for(root, ticket, found, disposition, packet, *given, **named):
            if disposition and packet is None:
                ticket_file = root / ".tickets" / f"{ticket}.md"
                packet = {"hash": hashlib.sha256(ticket_file.read_bytes()).hexdigest()}
                mark("a fallback context hash (sha256 of the ticket file) given to a refusal with a class")
            return refuse_for(root, ticket, found, disposition, packet, *given, **named)
        m._refuse_for = planted_refuse_for
    elif PLANT == "PF4":  # the containment judgement returns before it judges
        def planted_containment(root, commits):
            mark(f"containment returned before judging {len(commits)} commits")
        m._check_containment = planted_containment
    elif PLANT == "PF5":  # the acceptance run is never made and reports one pass
        def planted_acceptance(*given, **named):
            mark("the acceptance run was not made; one pass reported")
            return {**ZERO, "passed": 1}
        m._check_acceptance = planted_acceptance
    elif PLANT == "PF9":  # the close record's packet_hash is a constant, not the context's hash
        build = m._build_context

        def planted_context(root, ticket):
            packet = build(root, ticket)
            mark(f"the packet hash {str(packet.get('hash'))[:12]} replaced by a constant")
            return {**packet, "hash": "0" * 64}
        m._build_context = planted_context
    elif PLANT == "PF11":  # the regression stops at its first failure
        for name in ("_one_test_run", "_told_run"):
            wrap_maxfail(m, name)
    elif PLANT in ("PF12", "PF16"):
        check_tests = m._check_tests

        def planted_tests(root, test_path, timeout, ignore=None, *given, **named):
            if ignore is None:
                return check_tests(root, test_path, timeout, ignore, *given, **named)
            if PLANT == "PF16":  # the regression is never run and counts nothing
                mark("the regression run was not made; nothing counted")
                return dict(ZERO)
            try:  # PF12: a failing regression test refuses nothing
                return check_tests(root, test_path, timeout, ignore, *given, **named)
            except m._Finding as finding:
                mark(f"the regression's findings were dropped: {finding.findings[:3]}")
                return dict(finding.details.get("tests_run") or ZERO)
        m._check_tests = planted_tests
    elif PLANT == "PF13":  # the trailer gate judges nothing
        def planted_trailers(root, commits, ticket, history):
            mark(f"the trailer gate judged none of {len(commits)} commits")
        m._check_trailers = planted_trailers
    elif PLANT == "PF15":  # a ticket's commits are matched by substring of their Task:
        from gov.close import repo

        def planted_commits(root, ticket):
            found = [c for c in repo.read_commits(root, "HEAD", "--fixed-strings", f"--grep=Task: {ticket}")
                     if any(ticket in value for value in c["trailers"].get("Task", []))]
            exact = [c for c in found if ticket in c["trailers"].get("Task", [])]
            mark(f"commits of {ticket} matched by substring: {len(found)}, of them exactly: {len(exact)}")
            return found
        repo.ticket_commits = planted_commits
        m._ticket_commits = planted_commits


def wrap_maxfail(m, name):
    original = getattr(m, name)

    def planted(root, cmd, *given, **named):
        if "--ignore" in cmd and "--maxfail=1" not in cmd:
            cmd = list(cmd) + ["--maxfail=1"]
            mark(f"--maxfail=1 added to the regression run ({name})")
        return original(root, cmd, *given, **named)
    setattr(m, name, planted)


def state(m):
    if PLANT == "PF10":  # the decision checker's findings are never read when an owner decision lifts an escalation
        lift = m.lift_escalation

        def planted_lift(root, ticket, dec_id, counter, register=None):
            import gov.decisions as decisions
            real = decisions.check

            def unread(where):
                findings = real(where)
                mark(f"the checker was asked about {dec_id}; its {len(findings)} findings were not read")
                return []
            decisions.check = unread
            try:
                return lift(root, ticket, dec_id, counter, register)
            finally:
                decisions.check = real
        m.lift_escalation = planted_lift


TARGETS = {"gov.close.command": command, "gov.close.state": state}


class _PlantFinder:
    """Finds the target modules as the path finder does, and applies the plant right after each is executed."""

    def find_spec(self, name, path=None, target=None):
        if name not in TARGETS:
            return None
        spec = importlib.machinery.PathFinder.find_spec(name, path)
        if spec is None or spec.loader is None:
            return spec
        execute = spec.loader.exec_module

        def exec_module(module):
            execute(module)
            TARGETS[name](module)
        spec.loader.exec_module = exec_module
        return spec


if PLANT:
    sys.meta_path.insert(0, _PlantFinder())

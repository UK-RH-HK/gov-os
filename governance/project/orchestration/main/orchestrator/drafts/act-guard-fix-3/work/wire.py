import sys
p = sys.argv[1]
s = open(p).read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)


rep('''runs this file. The product's full guard (template/governance/kernel/hooks/pretooluse.py, src/gov/guard/) stays built
and tested; it is not wired here until the Gov OS is whole. Fail closed: an error or the 20-second deadline refuses.
"""''', '''runs this file. The product's full guard (template/governance/kernel/hooks/pretooluse.py, src/gov/guard/) stays built
and tested; it is not wired here until the Gov OS is whole. Fail closed: an error or the 20-second deadline refuses.
Rules 1 and 5 read a Bash command through bash_writes.py beside this file (ACT-GUARD-FIX-3): heredoc bodies, the
command's own variables, substitutions and inline Python are judged by what they are, not by the words they hold.
"""''')
rep('''def tree_roots(root):''', '''def bash_judgement(command, cwd):
    """ACT-GUARD-FIX-3: what ``command`` writes, read by bash_writes.py with the product's parser; None when the
    command cannot be read for certain, which is then judged as before the fix."""
    import bash_writes
    from gov.guard.decide import _UNRESOLVABLE, _expand_token, _extract_bash_write_targets
    if bash_writes.SENT != _UNRESOLVABLE:
        raise RuntimeError("bash_writes.SENT differs from the parser's sentinel")
    try:
        return bash_writes.judge(command, cwd, _extract_bash_write_targets, _expand_token)
    except bash_writes.Unreadable:
        return None


def code_writes_acceptance(findings, root, cwd):
    """Rule 1 for the code a command runs inline (ACT-GUARD-FIX-3): a target that names or lands in the acceptance
    tests refuses; one the guard cannot work out refuses when the code or its command names them."""
    from bash_writes import SENT, UNKNOWN
    for targets, scope in findings:
        for raw, full in targets:
            if raw != SENT and "tests/acceptance" in raw:
                return True
            if raw == SENT or full is None or full.startswith(UNKNOWN):
                if ACCEPTANCE in scope:
                    return True
            elif under_acceptance(full, root, cwd) or "/tests/acceptance/" in full + "/":
                return True
    return False


def tree_roots(root):''')
rep('''    why = reads._Judge(root, parts).tool(tool, tin, cwd)''', '''    seen = tin
    if tool == "Bash" and isinstance(tin.get("command"), str):
        # ACT-GUARD-FIX-3: a heredoc that cat or tee takes as data is no read; $((n+6)) is no listing.
        import bash_writes
        seen = dict(tin, command=bash_writes.reads_view(tin["command"]))
    why = reads._Judge(root, parts).tool(tool, seen, cwd)''')
rep('''            from gov.guard.decide import _UNRESOLVABLE, _extract_bash_write_targets
            # The parser answers None for a read-only command, and a list of targets (the sentinel among them
            # for a write it cannot resolve) otherwise (DEC-958 fix: None was read as "cannot read").
            targets = _extract_bash_write_targets(tin.get("command") or "", cwd)''', '''            from gov.guard.decide import _UNRESOLVABLE, _extract_bash_write_targets
            # The parser answers None for a read-only command, and a list of targets (the sentinel among them
            # for a write it cannot resolve) otherwise (DEC-958 fix: None was read as "cannot read"). The shell's
            # own writes are judged; inline code is not, as before (ACT-GUARD-FIX-3).
            judged = bash_judgement(tin.get("command") or "", cwd)
            targets = (judged.shell or None) if judged is not None else \\
                _extract_bash_write_targets(tin.get("command") or "", cwd)''')
rep('''            command = tin.get("command") or ""
            found = _extract_bash_write_targets(command, cwd)
            # None is a read-only command (running or reading the tests is open, DEC-820); a write the parser
            # cannot resolve, or inline interpreter code, is refused only when it names the acceptance tests.
            unresolved = found is not None and _UNRESOLVABLE in found and ACCEPTANCE in command
            if unresolved or inline_writes_acceptance(command):
                answer("deny", "a command that may write the acceptance tests, which only the "
                               "independent test designer writes")
            targets = [t for t in (found or []) if t != _UNRESOLVABLE]''', '''            command = tin.get("command") or ""
            judged = bash_judgement(command, cwd)
            if judged is None:
                # Not read for certain (ACT-GUARD-FIX-3): judged as before.
                found = _extract_bash_write_targets(command, cwd)
                # None is a read-only command (running or reading the tests is open, DEC-820); a write the parser
                # cannot resolve, or inline interpreter code, is refused only when it names the acceptance tests.
                unresolved = found is not None and _UNRESOLVABLE in found and ACCEPTANCE in command
                inline = inline_writes_acceptance(command)
            else:
                found = judged.shell
                unresolved = _UNRESOLVABLE in found and ACCEPTANCE in command
                inline = code_writes_acceptance(judged.findings, root, cwd)
            if unresolved or inline:
                answer("deny", "a command that may write the acceptance tests, which only the "
                               "independent test designer writes")
            targets = [t for t in (found or []) if t != _UNRESOLVABLE]''')
open(p, "w").write(s)
print("wired")

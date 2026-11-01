import sys
p = sys.argv[1]
s = open(p).read()
old = '''    for words, _, sep in cmds:
        pos += 1
        head = lead(words)
        first = words[0] if words else ""
        if head and os.path.basename(head[0]) in ("source", ".", "eval"):
            opaque = True  # may set any variable
        if words and all(_ASSIGN.match(w) for w in words):
            # In a pipeline or in the background the assignment is a subshell's: not the command's own.
            alone = before not in ("|", "|&", "&") and sep not in ("|", "|&", "&")
            for w in words:
                m = _ASSIGN.match(w)
                sets.append((m.group(1), m.group(2), depth if alone else -1, pos))
        elif first in ("export", "readonly", "declare", "typeset", "local"):
            for w in words[1:]:'''
new = '''    for whole_words, _, sep in cmds:
        pos += 1
        if whole_words[:1] and whole_words[0] in _STARTS:
            depth += 1  # if, while, until, for, case, {: what follows is inside
        # The keywords before a command (then, do, else, !, {) are not part of it: "then B=x" assigns B.
        k = 0
        while k < len(whole_words) and whole_words[k] in _OPENS + ("for",) and \\
                not (whole_words[k] == "for" and k + 1 < len(whole_words)):
            k += 1
        while k < len(whole_words) and whole_words[k] in _OPENS:
            k += 1
        words = whole_words[k:]
        head = lead(words)
        first = words[0] if words else ""
        if head and os.path.basename(head[0]) in ("source", ".", "eval"):
            opaque = True  # may set any variable
        if words and all(_ASSIGN.match(w) for w in words):
            # In a pipeline or in the background the assignment is a subshell's: not the command's own.
            alone = before not in ("|", "|&", "&") and sep not in ("|", "|&", "&")
            for w in words:
                m = _ASSIGN.match(w)
                sets.append((m.group(1), m.group(2), depth if alone else -1, pos))
        elif first in ("export", "readonly", "declare", "typeset", "local"):
            for w in words[1:]:'''
assert s.count(old) == 1
s = s.replace(old, new)
old2 = '''        before = sep
        if first in _STARTS:
            depth += 1
        if first in _ENDS or (sep == ")"):'''
new2 = '''        before = sep
        if first in _ENDS or (sep == ")"):'''
assert s.count(old2) == 1, "old2"
s = s.replace(old2, new2)
open(p, "w").write(s)
print("patched")

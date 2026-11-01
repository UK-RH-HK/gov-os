import sys
p = sys.argv[1]
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)
rep('''    cmds = simples(tokens(text))
    depth, sets, loops, bare = 0, [], {}, {}
    pos = 0
    for words, _, sep in cmds:
        pos += 1
        head = lead(words)
        first = words[0] if words else ""
        if words and all(_ASSIGN.match(w) for w in words):
            for w in words:
                m = _ASSIGN.match(w)
                sets.append((m.group(1), m.group(2), depth, pos))''', '''    cmds = simples(tokens(text))
    depth, sets, loops, bare = 0, [], {}, {}
    pos, opaque, before = 0, False, ""
    for words, _, sep in cmds:
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
                sets.append((m.group(1), m.group(2), depth if alone else -1, pos))''')
rep('''        if first in _STARTS:
            depth += 1''', '''        before = sep
        if first in _STARTS:
            depth += 1''')
rep('''    env, drop, loopvals = {}, set(), {}
    for name in names:''', '''    env, drop, loopvals = {}, set(), {}
    if opaque:
        return env, loopvals, names
    for name in names:''')
open(p, "w").write(s)
print("patched")

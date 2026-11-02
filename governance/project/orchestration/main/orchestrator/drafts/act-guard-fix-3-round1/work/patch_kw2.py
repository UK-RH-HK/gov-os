import sys
p = sys.argv[1]
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)
rep('''    # The ";" go in from the last to the first, so the positions taken above stay right.
    return " ".join(out)''', '''    return " ".join(out)''')
rep('''        env, loopvals, drop = variants(text, expand)
        for one in each(env, loopvals):
            with environ(one, drop):
                self.shell += self.parse(text, cwd) or []''', '''        env, loopvals, drop = variants(text, expand)
        ptext = parser_text(text)
        for one in each(env, loopvals):
            with environ(one, drop):
                self.shell += self.parse(ptext, cwd) or []''')
open(p, "w").write(s)

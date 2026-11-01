import sys
p = sys.argv[1]
s = open(p).read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)
# 13: local markers from heredocs(), made global once by run().
rep('''            out.append(f" < __gov_heredoc_{pending[-1][3]}__ ")''', '''            out.append(f" < __gov_hdl_{pending[-1][3]}__ ")''')
rep('''    ``< __gov_heredoc_<k>__`` (an input redirect the parser skips), so the reader is known by position. Raises''',
    '''    ``< __gov_hdl_<k>__`` (an input redirect the parser skips), so the reader is known by position. Raises''')
rep('''        text = re.sub(r"__gov_heredoc_(\\d+)__", lambda m: f"__gov_heredoc_{base + int(m.group(1))}__", text)''',
    '''        # This command's own heredocs get their number among all met so far (a nested command's marks are
        # already numbered so).
        text = re.sub(r"__gov_hdl_(\\d+)__", lambda m: f"__gov_heredoc_{base + int(m.group(1))}__", text)''')
rep('''        at += [(int(m), len(stage) - 1) for r in reds for m in re.findall(r"^__gov_heredoc_(\\d+)__$", r[1])]''',
    '''        at += [(int(m), len(stage) - 1) for r in reds for m in re.findall(r"^__gov_hdl_(\\d+)__$", r[1])]''')
# 1: the walk's variables are this command's, restored after it.
rep('''    def run(self, command, cwd, whole, depth=0):
        if depth > MOST_DEPTH:
            self.shell.append(SENT)
            return
        text, bodies = heredocs(command)''', '''    def run(self, command, cwd, whole, depth=0):
        outer = self.ctx
        try:
            self._run(command, cwd, whole, depth)
        finally:
            self.ctx = outer  # a nested command's variables are not this one's

    def _run(self, command, cwd, whole, depth):
        if depth > MOST_DEPTH:
            self.shell.append(SENT)
            return
        text, bodies = heredocs(command)''')
rep('''                for w in words + [r[1] for r in reds]:
                    for k in map(int, re.findall(r"__gov_sub_(\\d+)__", w)):
                        self.sub(subs[k], ecwd, whole, depth)''', '''                for w in words + [r[1] for r in reds]:
                    for k in map(int, re.findall(r"__gov_sub_(\\d+)__", w)):
                        self.sub(subs[k], ecwd, whole, depth)
                self.ctx = (env, loopvals, drop)''')
open(p, "w").write(s)
print("patched")

import sys
p = sys.argv[1]
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)
rep('''                elif _PY.match(name):
                    self.inline_python(args, part, ecwd, whole, depth)''', '''                elif _PY.match(name):
                    self.inline_python(args, part, ecwd, whole, depth)
                elif name in ("git", "dd", "truncate", "sort", "rsync", "patch"):
                    # Writes the product's parser does not read (rule 1 judges them; rule 5 as before).
                    targets = [self.place(t, where) for t, where in _more_targets(name, args, ecwd)]
                    if targets:
                        self.findings.append((targets, part))''')
rep('''    def cd(self, name, args, ecwd):''', '''    def place(self, raw, ecwd):
        """A target word as (text, absolute path or None); SENT when it does not expand."""
        exp = self.expand(raw)
        if exp is None or "`" in exp:
            return SENT, None
        if os.path.isabs(exp):
            return exp, os.path.normpath(exp)
        return exp, (None if ecwd is None or ecwd.startswith(UNKNOWN) else os.path.normpath(os.path.join(ecwd, exp)))

    def cd(self, name, args, ecwd):''')
rep('''def _kind(words):''', '''def _more_targets(name, args, ecwd):
    """The targets of writes the product's parser does not read: git checkout, restore, rm and mv on paths; dd
    of=; truncate; sort -o; rsync's destination; patch's file and -o. Each as (word, the folder it is read in)."""
    out = []
    if name == "git":
        i, where = 0, ecwd
        while i < len(args) and args[i].startswith("-"):
            if args[i] == "-C" and i + 1 < len(args):
                where = None if where is None else os.path.join(where, args[i + 1])
            i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
        sub, rest = (args[i], args[i + 1:]) if i < len(args) else ("", [])
        if sub in ("checkout", "restore", "rm", "mv"):
            if "--" in rest:
                words = rest[rest.index("--") + 1:]
            else:
                words, skip = [], False
                for w in rest:
                    if skip:
                        skip = False
                    elif w in ("-s", "--source", "-b", "-B", "--orphan", "--conflict"):
                        skip = True
                    elif not w.startswith("-"):
                        words.append(w)
            out = [(w, where) for w in words]
    elif name == "dd":
        out = [(a[3:], ecwd) for a in args if a.startswith("of=")]
    elif name == "truncate":
        skip = False
        for a in args:
            if skip:
                skip = False
            elif a in ("-s", "-r", "--size", "--reference"):
                skip = True
            elif not a.startswith("-"):
                out.append((a, ecwd))
    elif name == "sort":
        for k, a in enumerate(args):
            if a in ("-o", "--output") and k + 1 < len(args):
                out.append((args[k + 1], ecwd))
            elif a.startswith("--output="):
                out.append((a[9:], ecwd))
            elif a.startswith("-o") and len(a) > 2 and not a.startswith("--"):
                out.append((a[2:], ecwd))
    elif name == "rsync":
        operands = [a for a in args if not a.startswith("-")]
        out = [(operands[-1], ecwd)] if len(operands) >= 2 else []
    elif name == "patch":
        operands = [a for a in args if not a.startswith("-")]
        out = [(operands[0], ecwd)] if operands else []
        for k, a in enumerate(args):
            if a in ("-o", "--output") and k + 1 < len(args):
                out.append((args[k + 1], ecwd))
    return out


def _kind(words):''')
open(p, "w").write(s)
print("patched")

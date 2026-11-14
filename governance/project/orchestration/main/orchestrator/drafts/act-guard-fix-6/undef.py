"""Undefined global names of a module, by symtable (no pyflakes here): python3 -B -I undef.py <file>... Prints
file:function:name for each global a function (or the module) reads that the module never defines, nor builtins hold.
Exit 1 when any."""
import builtins
import symtable
import sys

bad = 0
for path in sys.argv[1:]:
    src = open(path).read()
    top = symtable.symtable(src, path, "exec")
    defined = {s.get_name() for s in top.get_symbols() if s.is_assigned() or s.is_imported() or s.is_namespace()}
    defined |= set(dir(builtins)) | {"__file__", "__name__", "__doc__"}

    def walk(table, scope):
        global bad
        for s in table.get_symbols():
            if s.is_global() and s.is_referenced() and s.get_name() not in defined:
                print(f"{path}:{scope}:{s.get_name()}")
                bad = 1
            elif (not s.is_local() and not s.is_free() and not s.is_global() and s.is_referenced()
                  and table.get_type() == "module" and s.get_name() not in defined):
                print(f"{path}:<module>:{s.get_name()}")
                bad = 1
        for child in table.get_children():
            walk(child, scope + "." + child.get_name() if scope else child.get_name())
    walk(top, "")
sys.exit(bad)

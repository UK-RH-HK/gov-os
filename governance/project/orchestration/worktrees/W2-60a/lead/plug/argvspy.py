import sys
def pytest_collection_finish(session):
    mod = sys.modules.get("w1_46_support")
    if mod is None: return
    orig = mod.caller_args_then_template_pair
    def spy(argv, args, *a, **k):
        r = orig(argv, args, *a, **k)
        sys.stderr.write(f"\nARGVSPY result={r} tail={list(argv)[-(len(args)+3):]}\n")
        return r
    mod.caller_args_then_template_pair = spy

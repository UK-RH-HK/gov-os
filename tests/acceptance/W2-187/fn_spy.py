# W2-187's function spy (appended to W2-172's sitecustomize.py by the world's template; one sitecustomize per process).
# When W187_FNSPY names a file, a profile hook counts the calls of every function defined in the reader's, the grader's, the
# prompts' and the matcher's modules, per process, and writes {"argv", "counts"} there when the process ends (S3, F4).
_FN_PATH = os.environ.get("W187_FNSPY")
if _FN_PATH:
    import atexit
    import threading
    _FN_MODULES = ("gov.memaudit.judge", "gov.memaudit.prompts", "gov.memaudit.claude", "gov.memaudit.matcher")
    _FN_COUNTS = {}

    def _fn_profile(frame, event, arg):
        if event == "call":
            module = frame.f_globals.get("__name__")
            if module in _FN_MODULES:
                name = f"{module}.{getattr(frame.f_code, 'co_qualname', frame.f_code.co_name)}"
                _FN_COUNTS[name] = _FN_COUNTS.get(name, 0) + 1

    def _fn_write():
        sys.setprofile(None)
        if _FN_COUNTS:
            fd = os.open(_FN_PATH, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            try:
                os.write(fd, (json.dumps({"argv": list(getattr(sys, "orig_argv", sys.argv)), "counts": _FN_COUNTS}) + "\n").encode())
            finally:
                os.close(fd)

    sys.setprofile(_fn_profile)
    threading.setprofile(_fn_profile)
    atexit.register(_fn_write)

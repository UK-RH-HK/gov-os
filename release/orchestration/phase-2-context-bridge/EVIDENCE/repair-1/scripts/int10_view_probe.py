"""BR-AR-0028 check 10 (BR-DAG-AMEND-R1-23): a DYNAMIC resolution-count probe around one govbridge CLI operation.

Usage (from the domain, with $PY):
    $PY EVIDENCE/repair-1/scripts/int10_view_probe.py <probe-json-out> <stdout-out> -- <govbridge argv...>

Before govbridge.cli is imported, this wraps (in-process only):
  * govbridge.core.view.load_view      -- records every config path loaded;
  * govbridge.core.view.resolve_view   -- counts calls; records the named commits each call resolved;
  * subprocess.Popen                   -- records EVERY git subprocess whose argv names a SYMBOLIC ref (anything
                                          under refs/, HEAD, or a '<ref>:<path>' whose <ref> is not a hex object id)
                                          and every 'for-each-ref' -- i.e. every tip resolution, whichever Python
                                          function (govbridge or not) issued it, and whether or not it went through
                                          resolve_view;
  * govbridge.core.gitobj.CatFileBatch.read -- records any object name that is not a hex id (a tip read through a
                                          long-lived cat-file stream would otherwise be invisible to the Popen hook).
The probe never changes behaviour: every wrapper calls the original and returns its result unchanged.
"""
import json
import os
import re
import subprocess
import sys
import time

# the domain (three levels up from EVIDENCE/repair-1/scripts/) on sys.path, so `govbridge` imports exactly as with
# `python -m` from the domain; a script file only puts its own directory on sys.path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

HEX = re.compile(r"^[0-9a-f]{7,40}(\^\{commit\})?$")
probe = {"argv": None, "load_view_paths": [], "resolve_view_calls": [], "git_symbolic_ref_calls": [],
         "for_each_ref_calls": [], "catfile_symbolic_reads": [], "nesting": 0}
_in_resolve = [0]


def _is_symbolic(tok: str) -> bool:
    if tok in ("HEAD",) or tok.startswith("refs/"):
        return True
    if ":" in tok and not tok.startswith("-"):
        rev = tok.split(":", 1)[0]
        if rev and not HEX.match(rev) and not rev.startswith("/"):
            return True
    return False


_orig_popen_init = subprocess.Popen.__init__


def _popen_init(self, args, *a, **kw):
    try:
        argv = [str(x) for x in (args if isinstance(args, (list, tuple)) else [args])]
        if argv and os.path.basename(argv[0]) == "git":
            gitargs = argv[1:]
            if "-C" in gitargs:
                i = gitargs.index("-C")
                gitargs = gitargs[:i] + gitargs[i + 2:]
            if gitargs and gitargs[0] == "for-each-ref":
                probe["for_each_ref_calls"].append({"args": gitargs, "inside_resolve_view": _in_resolve[0] > 0})
            else:
                sym = [t for t in gitargs[1:] if _is_symbolic(t.replace("^{commit}", ""))]
                if sym:
                    probe["git_symbolic_ref_calls"].append({"args": gitargs[:6], "symbolic": sym,
                                                            "inside_resolve_view": _in_resolve[0] > 0})
    except Exception:
        pass
    return _orig_popen_init(self, args, *a, **kw)


subprocess.Popen.__init__ = _popen_init

from govbridge.core import view as viewmod  # noqa: E402
from govbridge.core import gitobj  # noqa: E402

_orig_load = viewmod.load_view
_orig_resolve = viewmod.resolve_view
_orig_cat_read = gitobj.CatFileBatch.read


def _load(path):
    probe["load_view_paths"].append(os.path.abspath(path))
    return _orig_load(path)


def _resolve(config, repo=None):
    _in_resolve[0] += 1
    try:
        rv = _orig_resolve(config, repo=repo)
    finally:
        _in_resolve[0] -= 1
    probe["resolve_view_calls"].append({"view_id": config.view_id,
                                        "named": {n: r.commit for n, r in rv.named.items()},
                                        "history_count": len(rv.history),
                                        "t": round(time.monotonic(), 3)})
    return rv


def _cat_read(self, oid):
    rev = oid.split(":", 1)[0]
    if not HEX.match(rev):
        probe["catfile_symbolic_reads"].append(oid[:120])
    return _orig_cat_read(self, oid)


viewmod.load_view = _load
viewmod.resolve_view = _resolve
gitobj.CatFileBatch.read = _cat_read


def main():
    out_json, out_stdout = sys.argv[1], sys.argv[2]
    assert sys.argv[3] == "--"
    argv = sys.argv[4:]
    probe["argv"] = argv
    from govbridge import cli
    import contextlib
    import io
    buf = io.StringIO()
    t0 = time.monotonic()
    rc = None
    err = None
    try:
        with contextlib.redirect_stdout(buf):
            rc = cli.main(argv)
    except SystemExit as e:
        rc = e.code
    except Exception as e:  # recorded, re-raised after the probe is written
        err = repr(e)
    probe["wall_seconds"] = round(time.monotonic() - t0, 3)
    probe["exit_code"] = rc
    probe["error"] = err
    with open(out_stdout, "w", encoding="utf-8") as fh:
        fh.write(buf.getvalue())
    probe["summary"] = {
        "resolve_view_count": len(probe["resolve_view_calls"]),
        "distinct_named_resolutions": len({json.dumps(c["named"], sort_keys=True) for c in probe["resolve_view_calls"]}),
        "load_view_paths_distinct": sorted(set(probe["load_view_paths"])),
        "git_symbolic_ref_calls_total": len(probe["git_symbolic_ref_calls"]),
        "git_symbolic_ref_calls_outside_resolve_view": sum(1 for c in probe["git_symbolic_ref_calls"]
                                                            if not c["inside_resolve_view"]),
        "for_each_ref_calls_total": len(probe["for_each_ref_calls"]),
        "for_each_ref_calls_outside_resolve_view": sum(1 for c in probe["for_each_ref_calls"]
                                                        if not c["inside_resolve_view"]),
        "catfile_symbolic_reads": len(probe["catfile_symbolic_reads"]),
    }
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(probe, fh, indent=1, sort_keys=True)
    if err:
        print(err, file=sys.stderr)
        return 3
    return rc or 0


if __name__ == "__main__":
    sys.exit(main())

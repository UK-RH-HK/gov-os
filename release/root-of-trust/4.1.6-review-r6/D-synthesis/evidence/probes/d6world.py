"""AR-0018 shared world loader for the RV6-D probes (review r6 synthesis D).

It loads the architect's FA5 statement builders and world against the revision-6 reference executor exactly as the
architect's FA6 S1 does: a scratch copy of `evidence/r5/FA5-first-admission.py` with FA6's five substitutions (`SUBS`,
copied verbatim from `evidence/r6/FA6-first-admission.py`, AR-0015), executed up to its "CONFORMANCE VECTORS" marker, with
`evidence/r6/gov_admit_reference_r6.py` copied beside it under the name FA5 imports. Reviewer B's RV6-B-A01 and RV6-B-A04
(AR-0016) load the world the same way; attribution to both. No pack instrument is modified.
Environment: REVIEW_REPO (export holding the revision-6 pack), SCRATCH, GOV (legacy 4.1.5; used only where FA5's prefix uses it).
"""
import contextlib, io, os, shutil, sys

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
PK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
R6 = os.path.join(PK, "evidence", "r6")
R6_PATH = os.path.join(R6, "gov_admit_reference_r6.py")
FA5_PATH = os.path.join(PK, "evidence", "r5", "FA5-first-admission.py")
CS6_PATH = os.path.join(R6, "CS6-derivation-calculator.py")
SUBS = [  # FA6 SUBS (AR-0015), verbatim
    ('"inputs_manifest_digest": INP7}', '"inputs_manifest_digest": INP7, "kernel_tree_digest": sha256d(b"kernel-R7")}'),
    ('"inputs_manifest_digest": INP8}', '"inputs_manifest_digest": INP8, "kernel_tree_digest": sha256d(b"kernel-R8")}'),
    ('"verification_records": [VA7["digest"]], "units": {}}', '"verification_records": [VA7["digest"]], "units": {}, "constitution": {"kernel_tree_digest": sha256d(b"kernel-R7"), "units": {}}}'),
    ('"verification_records": [VA8["digest"]], "units": {}}', '"verification_records": [VA8["digest"]], "units": {}, "constitution": {"kernel_tree_digest": sha256d(b"kernel-R8"), "units": {}}}'),
    ('json_path = os.path.join(HERE, "FA5-first-admission.json")', 'json_path = os.path.join(HERE, "FA5-on-r6.json")'),
]


def load(scr):
    d1 = os.path.join(scr, "fa5-on-r6")
    os.makedirs(d1)
    shutil.copyfile(R6_PATH, os.path.join(d1, "gov_admit_reference.py"))
    src = open(FA5_PATH).read()
    for a, b in SUBS:
        src = src.replace(a, b)
    open(os.path.join(d1, "FA5-first-admission.py"), "w").write(src)
    cut = src.index("# ========== CONFORMANCE VECTORS ==========")
    os.environ["FA5_SCRATCH"] = os.path.join(scr, "fa5prefix")
    os.makedirs(os.environ["FA5_SCRATCH"], exist_ok=True)
    g = {"__file__": os.path.join(d1, "FA5-first-admission.py"), "__name__": "fa5_prefix"}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src[:cut], "FA5-prefix", "exec"), g)
    adm_bytes = open(os.path.join(d1, "gov_admit_reference.py"), "rb").read()
    assert g["GA"].sha256d(adm_bytes) == g["ADMITTER_DIGEST"]
    return g, d1, adm_bytes


def pack(name):
    return open(os.path.join(PK, name)).read()


def lines(text, pred):
    return [l for l in text.splitlines() if pred(l)]

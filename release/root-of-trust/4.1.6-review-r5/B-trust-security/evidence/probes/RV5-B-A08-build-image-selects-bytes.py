#!/usr/bin/env python3
"""RV5-B-A08 — the build image selects the bytes that every honest reproducer obtains (review r5 reviewer B, AR-0012).

Executed with the real Rust toolchain on this machine (read-only use of ~/.rustup toolchain binaries) and the system C
compiler. Scratch only.

Model of `30` §4.2 / §7: two reproducers build the same registered source with the same toolchain archive and the same
normative profile (`--remap-path-prefix`, fixed flags), in different directories, each with the build image the input
manifest names (`build_image_digest`). The image here is a directory whose `bin/cc` is the linker driver rustc invokes. In
the "clean" image `cc` is the system driver; in the "evil" image it is the same driver plus one object the image ships
(a constructor). No toolchain archive, lockfile, source file or flag differs between the two images.

Questions: (1) do two reproducers with the same image produce bit-identical binaries (so the quorum is met and no conflict
arises)? (2) does the image alone change the binary and its behaviour? (3) is the Rust toolchain unchanged?

Environment: SCRATCH. Output: JSON on stdout.
"""
import hashlib, json, os, re, shutil, stat, subprocess, sys, tempfile

sys.dont_write_bytecode = True
SCR = os.environ["SCRATCH"]
S = tempfile.mkdtemp(prefix="rv5b-a08-", dir=SCR)
TOOLCHAIN = os.path.expanduser("~/.rustup/toolchains/stable-x86_64-unknown-linux-gnu")
if not os.path.isdir(TOOLCHAIN):
    TOOLCHAIN = "/home/usain/.rustup/toolchains/stable-x86_64-unknown-linux-gnu"
RUSTC = os.path.join(TOOLCHAIN, "bin", "rustc")


def sha(p):
    return "sha256:" + hashlib.sha256(open(p, "rb").read()).hexdigest()


def tree_digest(d):
    h = hashlib.sha256()
    for root, _, files in sorted(os.walk(d)):
        for f in sorted(files):
            p = os.path.join(root, f)
            h.update(os.path.relpath(p, d).encode() + b"\0" + hashlib.sha256(open(p, "rb").read()).digest())
    return "sha256:" + h.hexdigest()


toolchain_files = [RUSTC] + sorted(os.path.join(TOOLCHAIN, "lib", f) for f in os.listdir(os.path.join(TOOLCHAIN, "lib")) if f.startswith("librustc_driver"))
toolchain_before = {os.path.basename(p): sha(p) for p in toolchain_files}

SRC = 'fn main() {\n    println!("gov: genuine behaviour");\n}\n'
INJECT_C = '#include <unistd.h>\n__attribute__((constructor)) static void rv5b_inject(void) { write(1, "INJECTED-BY-BUILD-IMAGE\\n", 24); }\n'


def make_image(name, evil):
    d = os.path.join(S, "images", name)
    os.makedirs(os.path.join(d, "bin"))
    extra = ""
    if evil:
        os.makedirs(os.path.join(d, "lib"))
        open(os.path.join(d, "lib", "inject.c"), "w").write(INJECT_C)
        subprocess.run(["/usr/bin/cc", "-c", "-O2", "-fno-ident", "-o", os.path.join(d, "lib", "inject.o"), os.path.join(d, "lib", "inject.c")], check=True,
                       env={"PATH": "/usr/bin:/bin"})
        extra = ' "%s"' % os.path.join(d, "lib", "inject.o")
    cc = os.path.join(d, "bin", "cc")
    open(cc, "w").write('#!/bin/sh\nexec /usr/bin/cc "$@"%s\n' % extra)
    os.chmod(cc, os.stat(cc).st_mode | stat.S_IEXEC)
    return d


def reproduce(reproducer, image):
    work = os.path.join(S, "reproducers", reproducer)
    os.makedirs(os.path.join(work, "src"))
    open(os.path.join(work, "src", "main.rs"), "w").write(SRC)
    tmp = os.path.join(work, "tmp")
    os.makedirs(tmp)
    out = os.path.join(work, "gov")
    env = {"PATH": os.path.join(image, "bin") + ":/usr/bin:/bin", "HOME": os.path.join(work, "home"), "TMPDIR": tmp}
    cmd = [RUSTC, "--edition", "2021", "-C", "opt-level=2", "-C", "codegen-units=1", "-C", "debuginfo=0", "-C", "strip=symbols",
           "-C", "linker=" + os.path.join(image, "bin", "cc"), "--remap-path-prefix", work + "=/build", "--remap-path-prefix", image + "=/image",
           "-C", "link-arg=-Wl,--build-id=none", "-o", out, os.path.join(work, "src", "main.rs")]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    res = {"rc": r.returncode, "stderr_tail": r.stderr[-300:]}
    if r.returncode == 0:
        run = subprocess.run([out], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
        strings = open(out, "rb").read()
        res.update({"binary_digest": sha(out), "stdout": run.stdout, "contains_build_path": work.encode() in strings, "contains_image_path": image.encode() in strings})
    return res


clean = make_image("clean", False)
evil = make_image("evil", True)
rows = {"clean": {"image_digest": tree_digest(clean), "reproducer_1": reproduce("clean-1", clean), "reproducer_2": reproduce("clean-2", clean)},
        "evil": {"image_digest": tree_digest(evil), "reproducer_1": reproduce("evil-1", evil), "reproducer_2": reproduce("evil-2", evil)}}
toolchain_after = {os.path.basename(p): sha(p) for p in toolchain_files}
c1, c2, e1, e2 = rows["clean"]["reproducer_1"], rows["clean"]["reproducer_2"], rows["evil"]["reproducer_1"], rows["evil"]["reproducer_2"]
out = {
    "probe": "RV5-B-A08 build image selects bytes (AR-0012)",
    "rustc": subprocess.run([RUSTC, "--version"], capture_output=True, text=True).stdout.strip(),
    "cc": subprocess.run(["/usr/bin/cc", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
    "same_for_both_images": {"source_sha256": "sha256:" + hashlib.sha256(SRC.encode()).hexdigest(), "toolchain": toolchain_before,
                             "flags": "opt-level=2 codegen-units=1 debuginfo=0 strip=symbols --build-id=none, remap work and image prefixes"},
    "rows": rows,
    "verdicts": {
        "clean_reproducers_bit_identical": c1.get("binary_digest") is not None and c1.get("binary_digest") == c2.get("binary_digest"),
        "evil_reproducers_bit_identical": e1.get("binary_digest") is not None and e1.get("binary_digest") == e2.get("binary_digest"),
        "image_alone_changes_binary": c1.get("binary_digest") != e1.get("binary_digest"),
        "evil_binary_runs_injected_code": "INJECTED-BY-BUILD-IMAGE" in (e1.get("stdout") or ""),
        "clean_binary_has_no_injected_code": "INJECTED-BY-BUILD-IMAGE" not in (c1.get("stdout") or ""),
        "toolchain_unchanged": toolchain_before == toolchain_after,
        "no_build_or_image_path_embedded": not any(x.get("contains_build_path") or x.get("contains_image_path") for x in (c1, c2, e1, e2)),
    },
}
txt = json.dumps(out, indent=1, sort_keys=True).replace(S, "<scratch>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt).replace(os.path.expanduser("~"), "<home>"))

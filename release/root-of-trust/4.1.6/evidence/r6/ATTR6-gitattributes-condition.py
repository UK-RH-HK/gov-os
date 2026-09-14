#!/usr/bin/env python3
"""ATTR6 — the `governance/trust/.gitattributes` member (`* -text`) against line-ending conversion (RV5-M6, RV5-C-M1; `26` §2,
`18` §9.1). Real Git, scratch only. Complements reviewer C's `gitops` rows re-run by LAY6 (`evidence/r6/LAY6/`), which
exercise the full installation-state predicate; this probe isolates which Git configurations still override the member,
so that `26` can state the condition exactly.

A repository holds `governance/trust/.gitattributes` = `* -text\n` and `governance/trust/kernel/POLICY.yaml` with LF line
endings. It is cloned under each configuration; the question per row is whether the checked-out kernel file equals the
committed bytes. Control rows use a trust tree without the member.

Rows (RV5-C-M1 configurations, then the stated override condition, then controls)
  C1 `core.autocrlf=true` (Git for Windows default)
  C2 a committed project `.gitattributes` `* text=auto` with `core.eol=crlf`
  C2b a committed project `.gitattributes` `* text eol=crlf`
  O1 `.git/info/attributes` `* text` with `core.autocrlf=true`      O2 `.git/info/attributes` `* text` with `core.eol=crlf`
  O3 `.git/info/attributes` `* text eol=crlf`                        O4 `.git/info/attributes` `* text=auto` with `core.eol=crlf`
  K1/K2 controls without the member under C1/C2
`.git/info/attributes` has the highest attribute precedence in Git, above every in-tree `.gitattributes`; the O rows show
that it overrides the member. That is the condition `26` §2 states: such a clone's kernel bytes differ from the lock's
digests, so the installation state is `PARTIAL(kernel_content_mismatch)` (fail closed), and doctor names the source.
Environment: SCRATCH. Output: JSON on stdout.
"""
import json, os, re, subprocess, sys, tempfile

sys.dont_write_bytecode = True
S = tempfile.mkdtemp(prefix="attr6-", dir=os.environ["SCRATCH"])
ENV = {"PATH": "/usr/bin:/bin", "HOME": os.path.join(S, "home"), "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}
os.makedirs(ENV["HOME"], exist_ok=True)
KERNEL = b"version: 1\nsecret_content_patterns:\n  - id: aws-access-key\n    regex: '(AKIA|ASIA)[0-9A-Z]{16}'\n"


def git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=cwd, env=ENV, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode())
    return r.stdout


def origin(name, with_member, project_attributes=None):
    d = os.path.join(S, name)
    os.makedirs(os.path.join(d, "governance", "trust", "kernel"))
    git(["init", "-q"], d)
    open(os.path.join(d, "governance", "trust", "kernel", "POLICY.yaml"), "wb").write(KERNEL)
    if project_attributes is not None:
        open(os.path.join(d, ".gitattributes"), "w").write(project_attributes)
    if with_member:
        open(os.path.join(d, "governance", "trust", ".gitattributes"), "wb").write(b"* -text\n")
    git(["add", "-A"], d)
    git(["commit", "-q", "-m", name], d)
    return d


def clone(src, name, config=(), info_attributes=None):
    d = os.path.join(S, name)
    git(["clone", "-q", "--no-checkout"] + sum([["-c", c] for c in config], []) + [src, d], S)
    if info_attributes is not None:
        os.makedirs(os.path.join(d, ".git", "info"), exist_ok=True)
        open(os.path.join(d, ".git", "info", "attributes"), "w").write(info_attributes)
    git(["checkout", "-q", "HEAD", "--", "."], d)
    got = open(os.path.join(d, "governance", "trust", "kernel", "POLICY.yaml"), "rb").read()
    return {"config": list(config), "info_attributes": info_attributes, "kernel_bytes_equal_committed": got == KERNEL, "crlf_introduced": b"\r\n" in got}


with_m, without_m = origin("origin-member", True), origin("origin-control", False)
with_m_auto, without_m_auto = origin("origin-member-textauto", True, "* text=auto\n"), origin("origin-control-textauto", False, "* text=auto\n")
with_m_eol = origin("origin-member-eolcrlf", True, "* text eol=crlf\n")
rows = {
    "C1_autocrlf_true": clone(with_m, "c1", ["core.autocrlf=true"]),
    "C2_project_text_auto_eol_crlf": clone(with_m_auto, "c2", ["core.eol=crlf"]),
    "C2b_project_text_eol_attribute_crlf": clone(with_m_eol, "c2b", []),
    "O1_info_text_autocrlf_true": clone(with_m, "o1", ["core.autocrlf=true"], "* text\n"),
    "O2_info_text_eol_crlf": clone(with_m, "o2", ["core.eol=crlf"], "* text\n"),
    "O3_info_text_eol_attribute_crlf": clone(with_m, "o3", [], "* text eol=crlf\n"),
    "O4_info_text_auto_eol_crlf": clone(with_m, "o4", ["core.eol=crlf"], "* text=auto\n"),
    "K1_control_no_member_autocrlf_true": clone(without_m, "k1", ["core.autocrlf=true"]),
    "K2_control_no_member_project_text_auto_eol_crlf": clone(without_m_auto, "k2", ["core.eol=crlf"]),
}
out = {"probe": "ATTR6 .gitattributes member and line-ending overrides (AR-0015)", "git": subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip(),
       "rows": rows}
out["verdicts"] = {
    "member_protects_under_RV5-C-M1_configurations": all(rows[k]["kernel_bytes_equal_committed"] for k in ("C1_autocrlf_true", "C2_project_text_auto_eol_crlf", "C2b_project_text_eol_attribute_crlf")),
    "controls_show_the_harm_without_member": rows["K1_control_no_member_autocrlf_true"]["crlf_introduced"] and rows["K2_control_no_member_project_text_auto_eol_crlf"]["crlf_introduced"],
    "stated_condition_git_info_attributes_text_overrides_member": all(rows[k]["crlf_introduced"] for k in ("O1_info_text_autocrlf_true", "O2_info_text_eol_crlf", "O3_info_text_eol_attribute_crlf", "O4_info_text_auto_eol_crlf")),
}
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", json.dumps(out, indent=1, sort_keys=True).replace(S, "<scratch>")))

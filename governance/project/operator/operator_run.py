#!/usr/bin/env python3
"""The operator agent's one program (OPERATOR-AGENT-1 §4, DEC-1104 (2)): an ACT applied only when every gate passes.

    python3 operator_run.py [--config <file.json>] run <ACT> <manifest sha>     G1 to G9, the apply, the after-checks
    python3 operator_run.py [--config <file.json>] undo <ACT> <manifest sha>    the owner's undo (S22)
    python3 operator_run.py [--config <file.json>] digest [--since <ISO>]       the digest (S21)
    python3 operator_run.py [--config <file.json>] recover                      the journal's undo (the launcher's)

The gates, in order; each passes or refuses, and every gate fails closed (an error is a refusal):
  G1 frozen (the bundle copied to acts/<id>-<sha12>/, read-only, every file as the manifest hashes it);
  G2 under an ACCEPTED decision; G3 rehearsed with 0 failures; G4 READY by the pinned verdict.py, the reviewer's
  brief as APPROVED, the reviewer not the author, at most two rounds; G5 the request's, the verdict's and the
  recomputed manifest sha the same; G6 the class (three votes, the highest applies; (O) refused; (b) the owner's yes
  from the CTO session's transcript); the recompute from the frozen copy; G7 the live state as stated (apply.sh
  check); G8 the dry run in a clone with a planted HOME (check, apply, checks, undo byte for byte, the changed set
  equal to the touched list; then the live files re-hashed); G9 the holds (it waits; it never refuses for a hold).
Then the apply: the commit freeze (install/act-in-progress.txt, DEC-1106 (3)), a journal, apply.sh apply, the checks,
the touched-file check, the staged list, the commit with its trailers, the after-checks for (a) (the control files,
the guard replay, its call set first checked against the guard's call log both ways, DEC-1108 (2)); any failure undoes.
The restore rule (F15, DEC-1106 (1)): the agent writes back only a live file it can show is its own change (a touched
file at the frozen after-copy). Anything else that differs is left exactly as it is, the lock held, a P1 naming it.
Test hook points (GOV_OPERATOR_TEST_HOOK <point> <frozen>): after-G1, after-G6, in-G8, in-apply-checks.
The result is the last line of stdout, one JSON object; exit 0 when applied, undone (the undo step) or digested.
The undo step and the journal's recovery that leave a file not the ACT's own say "refused" and exit 1 (DEC-1107).
"""
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
from datetime import timedelta

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import opcommon as oc  # noqa: E402
import act_class  # noqa: E402

TEST_HOOK = "GOV_OPERATOR_TEST_HOOK"
CONTROL_REPO_TREES = (".claude", ".rulesync", ".git/hooks")
CONTROL_REPO_FILES = ("governance/project/orchestration/tools/deadman.py",
                      "governance/project/orchestration/tools/sentinel-brief.md",
                      "governance/project/path-map.yaml")
CONTROL_HOME_FILES = (".local/bin/gov",)
REPLAY_FILES = ("governance/project/path-map.yaml",)
DENY_LIST_FILE = re.compile(r"^(\.claude/settings[^/]*\.json|\.rulesync/permissions\.jsonc)$")
REPLAY_WINDOW_H = 48
LOG_SLACK = timedelta(minutes=2)    # the set's and the log's clocks may differ by this much (DEC-1108 (2))
LIVE_SESSION = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
LIVE_TREES = ("main", "worktree")
UNDO_DAYS = 7


def load_verdict():
    import importlib.util
    spec = importlib.util.spec_from_file_location("operator_verdict", os.path.join(HERE, "verdict.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_ok(check, rc, out):
    """A manifest check is green when its exit code is the stated one and, with a count, the last non-empty stdout
    line is that integer."""
    if rc != check.get("exit"):
        return False
    if check.get("count") is None:
        return True
    lines = [ln.strip() for ln in out.decode("utf-8", "replace").splitlines() if ln.strip()]
    try:
        return bool(lines) and int(lines[-1]) == int(check["count"])
    except ValueError:
        return False


def validate_manifest(m):
    """The manifest's form (the interface's fields); raises ValueError on anything else."""
    if not isinstance(m, dict):
        raise ValueError("the manifest is not a JSON object")
    for k in ("touched", "files", "checks"):          # dec is G2's, rehearsal G3's, the class G6's
        if k not in m:
            raise ValueError(f"the manifest has no {k}")
    if not isinstance(m["touched"], list):
        raise ValueError("touched is not a list")
    seen = set()
    for t in m["touched"]:
        if not isinstance(t, dict) or t.get("root") not in ("repo", "home", "crontab"):
            raise ValueError("a touched entry has no root of repo, home or crontab")
        if oc.safe_rel(t.get("path")) is None or (t["root"] == "crontab" and t["path"] != "crontab"):
            raise ValueError(f"a touched entry's path is not a plain relative path: {t.get('path')!r}")
        for k in ("before", "after"):
            if t.get(k) is not None and not (isinstance(t[k], str) and oc.SHA_RE.match(t[k])):
                raise ValueError(f"{t['path']}: {k} is neither a sha256 nor null")
        if t.get("before") is None and t.get("after") is None:
            raise ValueError(f"{t['path']}: neither before nor after")
        key = (t["root"], t["path"])
        if key in seen:
            raise ValueError(f"{t['path']} is listed twice")
        seen.add(key)
    if not isinstance(m["files"], dict):
        raise ValueError("files is not an object")
    for p, h in m["files"].items():
        if oc.safe_rel(p) is None or p in ("manifest.json", "review.md") or not (isinstance(h, str) and oc.SHA_RE.match(h)):
            raise ValueError(f"files: a malformed entry {p!r}")
    if not isinstance(m["checks"], list):
        raise ValueError("checks is not a list")
    for c in m["checks"]:
        if not isinstance(c, dict) or not isinstance(c.get("cmd"), str) or not isinstance(c.get("exit"), int) \
                or isinstance(c.get("exit"), bool) or not (c.get("count") is None or
                                                            (isinstance(c["count"], int) and not isinstance(c["count"], bool))):
            raise ValueError("a check is not {cmd, exit, count}")
    if m.get("commands") is not None and not isinstance(m["commands"], list):
        raise ValueError("commands is not a list")


# ===================================================================================================== the path rule
PATH_RULE = ("the frozen script must work relative to its cwd and HOME: no live repository path or real HOME named "
             "literally (absolute, ~, $HOME or ${HOME} form), no cd to either")
_CD = re.compile(r"(?:^|[\s;&|(`\"'{])(?:builtin\s+)?(?:cd|pushd)(?=$|[\s;&|)`\"'])(?:[ \t]+(?:-[LPe@]+[ \t]+)*"
                 r"(?P<t>[^\s;&|)`]*))?")
HOME_WORDS = ("~", "$HOME", "${HOME}")


def _literal(path):
    return re.compile(r"(?<![\w.\-/])" + re.escape(path) + r"(?![\w.\-])")


def live_path_refs(text, s):
    """Why a shell text breaks the path rule (F2), or None: it names the live repository's path or the real HOME
    literally (absolute, or the repository as ~/<rel>, $HOME/<rel>, ${HOME}/<rel>), or cds to either (a bare cd,
    cd ~, cd $HOME). The dry run plants HOME and clones the repository, so a script that reaches either by name would
    act on the live files during the dry run."""
    if not isinstance(text, str) or not text:
        return None
    lines = [ln for ln in re.sub(r"\\\n", " ", text).splitlines() if not ln.lstrip().startswith("#")]
    body = "\n".join(lines)
    repo, home = s["repo"], s["home"]
    repos = list(dict.fromkeys(p.rstrip("/") for p in (repo, os.path.realpath(repo)) if p.rstrip("/")))
    homes = list(dict.fromkeys(p.rstrip("/") for p in (home, os.path.realpath(home)) if p.rstrip("/")))
    for r in repos:
        if _literal(r).search(body):
            return f"it names the live repository's path ({r})"
    rels = []
    for h in homes:
        for r in repos:
            if r.startswith(h + "/"):
                rels.append(r[len(h) + 1:])
    for rel in dict.fromkeys(rels):
        rx = re.compile(r"(?:~|\$HOME|\$\{HOME\}|\"\$HOME\"|\"\$\{HOME\}\")/" + re.escape(rel) + r"(?![\w.\-])")
        if rx.search(body):
            return f"it names the live repository through HOME (~/{rel})"
    for h in homes:
        if _literal(h).search(body):
            return f"it names the real HOME's path ({h})"
        user = os.path.basename(h)
        if user and re.search(r"(?<![\w$])~" + re.escape(user) + r"(?![\w.\-])", body):
            return f"it names the real HOME as ~{user}"
    for m in _CD.finditer(body):
        t = (m.group("t") or "").strip("\"'")
        if t in ("",) or t.rstrip("/") in HOME_WORDS:
            return f"it cds to HOME ({m.group(0).strip()[:40]})"
    return None


def path_rule(frozen, manifest, s):
    """The path rule over apply.sh, the manifest's commands and its checks; raises Refused at G1 on a break."""
    try:
        with open(os.path.join(frozen, "apply.sh"), encoding="utf-8", errors="replace") as f:
            texts = [("apply.sh", f.read())]
    except OSError:
        raise oc.Refused("G1", "apply.sh cannot be read")
    texts += [("a manifest command", c) for c in manifest.get("commands") or [] if isinstance(c, str)]
    texts += [("a check", c["cmd"]) for c in manifest.get("checks") or [] if isinstance(c, dict)]
    for where, text in texts:
        why = live_path_refs(text, s)
        if why:
            raise oc.Refused("G1", f"the path rule: {where} breaks it, {why}; {PATH_RULE}")


# =========================================================================================================== the run
class Run:
    def __init__(self, s, act, sha, approved):
        self.s, self.act, self.sha = s, act, sha
        self.approved_sha, self.approved_lines = approved[1], approved[3]
        self.votes = None
        self.cls = None
        self.code_vote = None
        self.frozen = None
        self.manifest = None
        self.msha = None
        self.review_sha = None
        self.verdict = None
        self.yes = None
        self.commit = None
        self.checks = None
        self.disagreement = False
        self.at = None                     # the gate being run (F10: an error at G7 or later is pushed)
        self.freeze = None                 # the commit freeze's text this run wrote (its token), DEC-1106 (3)

    # ----------------------------------------------------------------------------------------------------- helpers
    def line(self, gate, result, **extra):
        undo = extra.pop("undo", None)
        fields = {"class": self.cls}
        fields.update(extra)
        return oc.log_event(self.s, self.act, self.sha, gate, result, votes=self.votes, commit=self.commit,
                            checks=self.checks, undo=undo, **fields)

    def result(self, result, gate=None, reason=None, **extra):
        r = {"result": result, "act": self.act, "manifest_sha256": self.sha}
        if gate:
            r["gate"] = gate
        if reason:
            r["reason"] = reason
        r["class"] = self.cls
        r["votes"] = self.votes
        r["commit"] = self.commit
        r["approved_sha256"] = self.approved_sha
        r.update(extra)
        return r

    def hook(self, point):
        exe = os.environ.get(TEST_HOOK)
        if exe and self.frozen:
            oc.run([exe, point, self.frozen], env=dict(os.environ), timeout=600)

    def live_env(self):
        return oc.clean_env(self.s, self.s["home"], extra={"PYTHONDONTWRITEBYTECODE": "1"})

    def apply_sh(self, step, cwd, env):
        rc, out, err = oc.run(["bash", os.path.join(self.frozen, "apply.sh"), step], cwd=cwd, env=env,
                              timeout=self.s["check_timeout_s"])
        return rc, out, err

    def repo_touched(self):
        return [t for t in self.manifest["touched"] if t["root"] == "repo"]

    # ---------------------------------------------------------------------------------------------------------- G1
    def g1(self):
        s = self.s
        src = os.path.join(s["scratch"], "acts", self.act)
        if not os.path.isdir(src) or os.path.islink(src):
            raise oc.Refused("G1", f"no bundle at <scratch>/acts/{self.act}/")
        acts = oc.ensure_dir(os.path.join(s["operator_root"], "acts"))
        final = os.path.join(acts, f"{self.act}-{self.sha[:12]}")
        if os.path.lexists(final):
            self.g1_reuse(src, final)
            return
        tmp = os.path.join(acts, f".{self.act}-{self.sha[:12]}.tmp-{os.getpid()}")
        oc.remove_tree(tmp)
        try:
            for top, dirs, files in os.walk(src):
                for n in dirs + files:
                    p = os.path.join(top, n)
                    if os.path.islink(p) or not (os.path.isdir(p) or os.path.isfile(p)):
                        raise oc.Refused("G1", f"the bundle holds a link or a special file ({os.path.relpath(p, src)})")
            shutil.copytree(src, tmp, symlinks=True)
            mpath = os.path.join(tmp, "manifest.json")
            if not os.path.isfile(mpath):
                raise oc.Refused("G1", "the bundle has no manifest.json")
            raw = open(mpath, "rb").read()
            self.msha = oc.sha256_bytes(raw)
            try:
                m = json.loads(raw.decode("utf-8"))
                validate_manifest(m)
            except (ValueError, UnicodeDecodeError) as exc:
                raise oc.Refused("G1", f"the manifest is malformed: {exc}")
            listed = dict(m["files"])
            found = set()
            for top, dirs, files in os.walk(tmp):
                for fn in files:
                    rel = os.path.relpath(os.path.join(top, fn), tmp).replace(os.sep, "/")
                    if rel in ("manifest.json", "review.md"):
                        continue
                    found.add(rel)
                    if rel not in listed:
                        raise oc.Refused("G1", f"the bundle holds a file the manifest does not list ({rel})")
                    if oc.sha256_file(os.path.join(tmp, rel)) != listed[rel]:
                        raise oc.Refused("G1", f"{rel} does not hash as the manifest says: changed after review")
            reh = m.get("rehearsal") if isinstance(m.get("rehearsal"), dict) else {}
            missing = sorted(set(listed) - found - {reh.get("log")})   # a missing rehearsal log is G3's
            if missing:
                raise oc.Refused("G1", f"the manifest lists a file the bundle does not hold ({missing[0]})")
            if "apply.sh" not in listed:
                raise oc.Refused("G1", "the bundle has no apply.sh")
            os.rename(tmp, final)          # never over an existing copy (F8): g1_reuse handles that
            oc.make_read_only(final)
        finally:
            oc.remove_tree(tmp)
        self.g1_done(final, m)

    def g1_done(self, final, m, **extra):
        self.frozen = final
        self.manifest = m
        rp = os.path.join(final, "review.md")
        self.review_sha = oc.sha256_file(rp) if os.path.isfile(rp) else None
        path_rule(final, m, self.s)
        self.line("G1", "pass", frozen=os.path.relpath(final, self.s["operator_root"]), **extra)
        self.hook("after-G1")

    def g1_reuse(self, src, final):
        """A second request for a sha already frozen (F8): the existing copy is never removed or replaced. It is reused
        only when it hashes as its manifest says (and its manifest as the request); otherwise the run refuses and leaves
        it as it is (an applied ACT's undo needs it). Only the review record, which the manifest does not hash, is
        taken afresh from the bundle, so a later review round on the same manifest is read."""
        if os.path.islink(final) or not os.path.isdir(final):
            raise oc.Refused("G1", "the frozen copy is not a folder: changed after review")
        try:
            raw = open(os.path.join(final, "manifest.json"), "rb").read()
            m = json.loads(raw.decode("utf-8"))
            validate_manifest(m)
        except (OSError, ValueError, UnicodeDecodeError):
            raise oc.Refused("G1", "the existing frozen copy's manifest cannot be read: changed after review")
        self.msha = oc.sha256_bytes(raw)
        if self.msha != self.sha:
            raise oc.Refused("G1", "the existing frozen copy's manifest is not the requested sha: changed after review")
        listed = m["files"]
        reh = m.get("rehearsal") if isinstance(m.get("rehearsal"), dict) else {}
        found = set()
        for top, dirs, files in os.walk(final):
            for n in dirs + files:
                p = os.path.join(top, n)
                if os.path.islink(p) or not (os.path.isdir(p) or os.path.isfile(p)):
                    raise oc.Refused("G1", "the existing frozen copy holds a link or a special file: changed after review")
            for fn in files:
                rel = os.path.relpath(os.path.join(top, fn), final).replace(os.sep, "/")
                if rel in ("manifest.json", "review.md"):
                    continue
                found.add(rel)
                if rel not in listed or oc.sha256_file(os.path.join(top, fn)) != listed[rel]:
                    raise oc.Refused("G1", f"the existing frozen copy's {rel} does not hash as its manifest says: "
                                           "changed after review")
        if set(listed) - found - {reh.get("log")}:
            raise oc.Refused("G1", "the existing frozen copy lacks a file its manifest lists: changed after review")
        rp_src, rp = os.path.join(src, "review.md"), os.path.join(final, "review.md")
        new = None
        if os.path.isfile(rp_src) and not os.path.islink(rp_src):
            with open(rp_src, "rb") as f:
                new = f.read()
        old = open(rp, "rb").read() if os.path.isfile(rp) else None
        if new != old:
            os.chmod(final, 0o755)
            try:
                if old is not None:
                    os.chmod(rp, 0o644)
                    os.unlink(rp)
                if new is not None:
                    with open(rp, "wb") as f:
                        f.write(new)
                    os.chmod(rp, 0o444)
            finally:
                os.chmod(final, 0o555)
        self.g1_done(final, m, reused=True)

    # ---------------------------------------------------------------------------------------------------------- G2
    def g2(self):
        dec = self.manifest.get("dec")
        text = " ".join(dec) if isinstance(dec, list) and all(isinstance(x, str) for x in dec) else \
            (dec if isinstance(dec, str) else "")
        ids = re.findall(r"DEC-\d+", text)
        if not ids:
            raise oc.Refused("G2", "the manifest names no DEC id")
        reg = self.register_path()
        try:
            with open(reg, encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except OSError:
            raise oc.Refused("G2", "the decision register cannot be read")
        for did in dict.fromkeys(ids):
            head = re.compile(r"^#{2,4}\s+" + re.escape(did) + r"(?!\d)")
            statuses = []
            for i, ln in enumerate(lines):
                if head.match(ln):
                    st = None
                    for ln2 in lines[i + 1:i + 60]:
                        if re.match(r"^#{1,4}\s", ln2):
                            break
                        mm = re.search(r"\*\*Status:?\*\*:?\s*\**\s*([A-Za-z][A-Za-z_-]*)", ln2)
                        if mm:
                            st = mm.group(1)
                            break
                    statuses.append(st)
            if not statuses:
                raise oc.Refused("G2", f"{did} is not in the register")
            if any(st != "ACCEPTED" for st in statuses):
                raise oc.Refused("G2", f"{did} is not ACCEPTED in the register ({statuses[0]})")
        self.line("G2", "pass", dec=ids)

    def register_path(self):
        repo = self.s["repo"]
        pm = os.path.join(repo, "governance/project/path-map.yaml")
        rel = "docs/DECISION_REGISTER.md"
        try:
            with open(pm, encoding="utf-8", errors="replace") as f:
                for ln in f:
                    mm = re.match(r"^decision_register:\s*['\"]?([^'\"\s#]+)", ln)
                    if mm and oc.safe_rel(mm.group(1)):
                        rel = mm.group(1)
                        break
        except OSError:
            pass
        return os.path.join(repo, rel)

    # ---------------------------------------------------------------------------------------------------------- G3
    def g3(self):
        r = self.manifest.get("rehearsal")
        if not isinstance(r, dict):
            raise oc.Refused("G3", "the manifest names no rehearsal")
        log, want = r.get("log"), r.get("sha256")
        if oc.safe_rel(log) is None or not (isinstance(want, str) and oc.SHA_RE.match(want)):
            raise oc.Refused("G3", "the manifest's rehearsal names no log and sha256")
        if self.manifest["files"].get(log) != want:
            raise oc.Refused("G3", "the rehearsal log is not hashed in the manifest's files as stated")
        p = os.path.join(self.frozen, log)
        if not os.path.isfile(p):
            raise oc.Refused("G3", "the rehearsal log is missing")
        if oc.sha256_file(p) != want:
            raise oc.Refused("G3", "the rehearsal log does not hash as stated")
        lines = [ln.strip() for ln in open(p, encoding="utf-8", errors="replace").read().splitlines() if ln.strip()]
        mm = re.match(r"^failures:\s*(\d+)$", lines[-1]) if lines else None
        if not mm:
            raise oc.Refused("G3", "the rehearsal log does not end with 'failures: <n>'")
        if int(mm.group(1)) != 0:
            raise oc.Refused("G3", f"the rehearsal ended with {mm.group(1)} failures")
        self.line("G3", "pass")

    # ---------------------------------------------------------------------------------------------------------- G4
    def g4(self):
        vmod = load_verdict()
        p = os.path.join(self.frozen, "review.md")
        if not os.path.isfile(p):
            raise oc.Refused("G4", "no review record (review.md)")
        try:
            text = open(p, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            raise oc.Refused("G4", "the review record cannot be read (fail closed)")
        blocks = vmod.BLOCK.findall(text)
        if not blocks:
            raise oc.Refused("G4", "the review record holds no verdict block")
        if len(blocks) >= 3:
            oc.notify(self.s, self.act, "P1", "to-owner",
                      f"{self.act}: a third review round; refused, to the owner", manifest_sha256=self.sha)
            raise oc.Refused("G4", f"a third review round ({len(blocks)} verdict blocks): to the owner")
        try:
            v = json.loads(blocks[-1])
            assert isinstance(v, dict)
        except (ValueError, AssertionError):
            raise oc.Refused("G4", "the last verdict block is malformed (fail closed)")
        ready, reasons = vmod.ready(text)
        if ready is not True:
            raise oc.Refused("G4", "not READY by verdict.py: " + ("; ".join(reasons) or "no verdict"))
        kpis = v.get("kpis")
        if not isinstance(kpis, list) or not kpis or any(not isinstance(k, dict) or k.get("verdict") != "pass"
                                                         for k in kpis):
            raise oc.Refused("G4", "a KPI is not marked pass (for an ACT any fail refuses)")
        if v.get("manifest_sha256") != self.msha:
            raise oc.Refused("G4", "the verdict block names another manifest sha: changed after review")
        if v.get("class") not in oc.CLASSES:
            raise oc.Refused("G4", "the verdict block names no class a, b or O")
        reviewer = v.get("reviewer")
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise oc.Refused("G4", "the verdict block names no reviewer")
        author = self.manifest.get("author")
        if not isinstance(author, str) or not author.strip():
            raise oc.Refused("G4", "the manifest names no author, so the reviewer cannot be shown not to be the author")
        if reviewer.strip().casefold() == author.strip().casefold():
            raise oc.Refused("G4", "the reviewer is the ACT's author")
        want = self.approved_lines.get("reviewer-brief.md")
        if not want or v.get("reviewer_brief_sha256") != want:
            raise oc.Refused("G4", "the reviewer's brief does not hash as its line in APPROVED")
        rtime = oc.parse_iso(v.get("time"))
        if rtime is None:
            raise oc.Refused("G4", "the verdict block's time is not an ISO time with an offset")
        rr = v.get("replay_refused", [])
        if rr is None:
            rr = []
        if not isinstance(rr, list) or not all(isinstance(x, (str, int)) for x in rr):
            raise oc.Refused("G4", "replay_refused is not a list of call ids")
        self.verdict = dict(v, _time=rtime, replay_refused=[str(x) for x in rr])
        self.line("G4", "pass", rounds=len(blocks), review_sha256=self.review_sha)

    # ---------------------------------------------------------------------------------------------------------- G5
    def g5(self):
        trio = {"request": self.sha, "verdict": self.verdict.get("manifest_sha256"), "recomputed": self.msha}
        if len(set(trio.values())) != 1:
            diff = ", ".join(f"{k} {str(v)[:12]}" for k, v in trio.items())
            raise oc.Refused("G5", f"the manifest sha differs ({diff}): changed after review")
        self.line("G5", "pass")

    # ---------------------------------------------------------------------------------------------------------- G6
    def g6(self):
        code = act_class.classify(self.frozen)
        self.code_vote = code["class"]
        claim = self.manifest.get("claimed_class")
        review = self.verdict.get("class")
        self.votes = {"code": self.code_vote, "claim": claim, "review": review}
        self.cls = oc.highest(self.code_vote, claim, review)
        self.code_why = code.get("why")
        if len({self.code_vote, claim, review}) != 1:
            self.disagreement = True
            oc.notify(self.s, self.act, "P1", "disagreement",
                      f"{self.act}: the votes disagree (code {self.code_vote}, claim {claim}, review {review}); "
                      f"the highest, ({self.cls}), applies", manifest_sha256=self.sha, votes=self.votes,
                      short=f"G6 votes disagree: code {self.code_vote}, claim {claim}, review {review}; "
                            f"({self.cls}) applies")
        if self.cls == "O":
            raise oc.Refused("G6", f"class (O): yours, not the operator's ({code.get('why')})")
        if self.cls == "b":
            wanted = f"yes {self.act} {self.sha[:8]}"
            found = oc.find_owner_line(self.s, wanted, self.verdict["_time"])
            if not found:
                raise oc.Refused("G6", f"class (b): no owner's line '{wanted}' after the review in the CTO "
                                       "session's transcript")
            raw, entry, ts = found
            self.yes = ts
            oc.append_jsonl(self.s["approvals"], {
                "time": oc.iso(oc.now(self.s)), "act": self.act, "manifest_sha256": self.sha, "text": wanted,
                "typed": oc.iso(ts), "session": oc.cto_session(self.s), "line": raw})
        self.line("G6", "pass", why=code.get("why"), disagreement=self.disagreement,
                  notice="disagreement" if self.disagreement else None)
        self.hook("after-G6")

    def recompute(self, log_pass=True):
        again = act_class.classify(self.frozen)["class"]
        if again != self.code_vote:
            raise oc.Refused("recompute", f"the class recomputed from the frozen copy, ({again}), differs from the "
                                          f"class recorded at G6, ({self.code_vote})")
        bad = self.frozen_changed()
        if bad:
            raise oc.Refused("recompute", f"the frozen copy changed ({bad}): changed after review")
        if log_pass:
            self.line("recompute", "pass")

    def frozen_changed(self):
        try:
            raw = open(os.path.join(self.frozen, "manifest.json"), "rb").read()
        except OSError:
            return "manifest.json"
        if oc.sha256_bytes(raw) != self.sha:
            return "manifest.json"
        for rel, want in self.manifest["files"].items():
            p = os.path.join(self.frozen, rel)
            if not os.path.isfile(p) or oc.sha256_file(p) != want:
                return rel
        return None

    # ---------------------------------------------------------------------------------------------------------- G7
    def g7(self, log_pass=True):
        env = self.live_env()
        for t in self.manifest["touched"]:
            if oc.live_hash(self.s, t["root"], t["path"], env) != t["before"]:
                raise oc.Refused("G7", f"{t['root']}:{t['path']} is not as the manifest states it before: "
                                       "rebuild, rehearse, re-review")
        rc, out, err = self.apply_sh("check", self.s["repo"], env)
        if rc != 0:
            raise oc.Refused("G7", f"apply.sh check exited {rc}: rebuild, rehearse, re-review")
        if log_pass:
            self.line("G7", "pass")

    # ---------------------------------------------------------------------------------------------------------- G8
    def live_snapshot(self, env):
        """The live touched files' and the control files' bytes (§3's list), to prove the dry run left them alone."""
        snap = control_snapshot(self.s, env)
        for t in self.manifest["touched"]:
            snap[(t["root"], t["path"])] = oc.live_file(self.s, t["root"], t["path"], env)
        return snap

    def g8(self):
        env = self.live_env()
        before = self.live_snapshot(env)
        tmp = tempfile.mkdtemp(prefix="gov-operator-dry-")
        try:
            self._g8(tmp)
        finally:
            oc.remove_tree(tmp)
            self.hook("in-G8")             # DEC-1106 (1): the dry run's steps done, the live re-hash next
            # F2: whatever the dry run's outcome, the live files must be as they were before it
            after = self.live_snapshot(env)
            changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
            if changed:
                self.live_changed(before, after, changed, env)
        self.line("G8", "pass")

    def live_changed(self, before, after, changed, env):
        """Live files differ after the dry run (F15, DEC-1106 (1)). Only a touched file whose live bytes are the frozen
        after-copy's (absent, for a deletion) is the dry run's own change: it is restored to the bytes read before the
        dry run. Anything else (a control file, a file created or removed, a touched file at third bytes) is someone
        else's or cannot be shown to be ours: it is left exactly as it is, the lock is held and the P1 names each file.
        Always refused at G8; the P1 follows from the refusal after G7 and its text says live files changed."""
        s = self.s
        touched = {(t["root"], t["path"]): t for t in self.manifest["touched"]}
        own, left, problems = [], [], []
        for key in changed:
            t = touched.get(key)
            (own if t is not None and is_after(t, after.get(key)) else left).append(key)
        for key in own:
            try:
                restore_live_file(s, key[0], key[1], before.get(key), env)
            except OSError as exc:
                problems.append(f"{key[0]}:{key[1]} ({exc.__class__.__name__})")
        if not problems:
            again = self.live_snapshot(env)
            problems = [f"{r}:{p} (not back to its bytes before the dry run)" for r, p in own
                        if again.get((r, p)) != before.get((r, p))]
        names = [f"{r}:{p}" for r, p in changed]
        own_n, left_n = [f"{r}:{p}" for r, p in own], [f"{r}:{p}" for r, p in left]
        parts = [f"live files changed during the dry run ({', '.join(names)})"]
        if own_n:
            parts.append("the dry run's own change restored to the bytes read before it: " + ", ".join(own_n))
        if left_n:
            parts.append("left exactly as written, not shown to be the dry run's change (someone else's, or "
                         "unknown): " + ", ".join(left_n))
        if problems:
            parts.append("NOT RESTORED: " + ", ".join(problems))
        hold = bool(left_n or problems)
        reason = "; ".join(parts) + ("; lock held, nothing else is applied" if hold else "") + f"; {PATH_RULE}"
        if hold:
            hold_lock(s, self.act, self.sha, reason)
        raise oc.Refused("G8", reason, live_changed=names, restored=not hold, restored_files=own_n, left=left_n,
                         lock=hold)

    def _g8(self, tmp):
        s = self.s
        clone, home, stub = os.path.join(tmp, "clone"), os.path.join(tmp, "home"), os.path.join(tmp, "bin")
        cronf = os.path.join(tmp, "crontab.txt")
        os.makedirs(home)
        os.makedirs(stub)
        rc, head, _ = oc.git(s["repo"], "rev-parse", "HEAD")
        if rc != 0:
            raise oc.Refused("G8", "the live head cannot be read")
        head = head.decode().strip()
        rc, _, err = oc.run(["git", "clone", "-q", "--no-checkout", s["repo"], clone], timeout=1800)
        if rc != 0:
            raise oc.Refused("G8", f"the clone failed: {err.decode('utf-8', 'replace')[:200]}")
        rc, _, err = oc.git(clone, "checkout", "-q", "--detach", head, timeout=1800)
        if rc != 0:
            raise oc.Refused("G8", "the clone's checkout failed")
        env0 = self.live_env()
        for t in self.manifest["touched"]:
            if t["root"] == "repo" and t["before"] is not None:
                # a listed file the clone does not hold as stated (an untracked or ignored file, a git hook): the
                # live bytes, when they are as stated, are copied in
                dst = os.path.join(clone, t["path"])
                have = read_bytes(dst)
                if have is None or oc.sha256_bytes(have) != t["before"]:
                    live = oc.live_file(s, "repo", t["path"], env0)
                    if live is not None and oc.sha256_bytes(live) == t["before"]:
                        write_file(dst, live)
            if t["root"] == "home" and t["before"] is not None:
                b = oc.live_file(s, "home", t["path"], env0)
                dst = os.path.join(home, t["path"])
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "wb") as f:
                    f.write(b or b"")
        live_cron = oc.crontab_bytes(env0)
        if live_cron is not None:
            with open(cronf, "wb") as f:
                f.write(live_cron)
        with open(os.path.join(stub, "crontab"), "w") as f:
            f.write(CRONTAB_STUB)
        os.chmod(os.path.join(stub, "crontab"), 0o755)
        env = oc.clean_env(s, home, extra={"OPERATOR_CRONTAB_FILE": cronf, "PYTHONDONTWRITEBYTECODE": "1"},
                           path_prefix=stub)
        listed = {(t["root"], t["path"]) for t in self.manifest["touched"]}

        def state():
            st = {("repo", p): h for p, h in tree_state(clone)[0].items()}
            st.update({("repo", ".git/hooks/" + p): h for p, h in walk_state(os.path.join(clone, ".git/hooks")).items()})
            cfg = read_bytes(os.path.join(clone, ".git/config"))            # F11: core.hooksPath and the rest
            st[("repo", ".git/config")] = None if cfg is None else oc.sha256_bytes(cfg)
            for r, p in listed:
                if r == "repo":
                    b = read_bytes(os.path.join(clone, p))
                    st[(r, p)] = None if b is None else oc.sha256_bytes(b)
            st.update({("home", p): h for p, h in walk_state(home).items()})
            st[("crontab", "crontab")] = oc.sha256_file(cronf) if os.path.isfile(cronf) else None
            return st

        a = state()
        a_cron = a[("crontab", "crontab")]
        self.record_call("bash " + os.path.join(self.frozen, "apply.sh") + " check")
        rc, _, _ = self.apply_sh("check", clone, env)
        if rc != 0:
            raise oc.Refused("G8", f"the dry run's apply.sh check exited {rc}")
        self.record_call("bash " + os.path.join(self.frozen, "apply.sh") + " apply")
        rc, _, _ = self.apply_sh("apply", clone, env)
        if rc != 0:
            raise oc.Refused("G8", f"the dry run's apply.sh apply exited {rc}")
        b = state()
        changed = diff_states(a, b, clean_key_value(a_cron))
        extra = sorted(changed - listed)
        if extra:
            raise oc.Refused("G8", "the dry run changed a file not on the touched list (unlisted): "
                                   + ", ".join(f"{r}:{p}" for r, p in extra[:5]))
        missing = sorted(listed - changed)
        if missing:
            raise oc.Refused("G8", "a listed file was not changed by the dry run (missing): "
                                   + ", ".join(f"{r}:{p}" for r, p in missing[:5]))
        for t in self.manifest["touched"]:
            if b.get((t["root"], t["path"]), CLEAN) != dry_want(t, a):
                raise oc.Refused("G8", f"the dry run left {t['root']}:{t['path']} not as the manifest states it after")
        for c in self.manifest["checks"]:
            self.record_call(c["cmd"])
            rc, out, _ = oc.run(["bash", "-c", c["cmd"]], cwd=clone, env=env, timeout=s["check_timeout_s"])
            if not check_ok(c, rc, out):
                raise oc.Refused("G8", f"a check is red in the dry run: {c['cmd'][:120]} (exit {rc})")
        cstate = state()
        self.record_call("bash " + os.path.join(self.frozen, "apply.sh") + " undo")
        rc, _, _ = self.apply_sh("undo", clone, env)
        if rc != 0:
            raise oc.Refused("G8", f"the dry run's apply.sh undo exited {rc}")
        d = state()
        for key in changed | listed:
            if d.get(key, CLEAN) != a.get(key, CLEAN):
                raise oc.Refused("G8", f"the undo did not restore {key[0]}:{key[1]} byte for byte")
        stray = sorted(diff_states(cstate, d, clean_key_value(a_cron)) - listed)
        if stray:
            raise oc.Refused("G8", "the dry run's undo changed a file not on the touched list (unlisted): "
                                   + ", ".join(f"{r}:{p}" for r, p in stray[:5]))

    def record_call(self, command):
        # the agent's own dry-run commands, in its own file: never in the CTO's call set (DEC-1108 (2))
        try:
            oc.append_jsonl(os.path.join(self.s["log_dir"], "operator-calls.jsonl"), {
                "id": oc.uuid.uuid4().hex, "time": oc.iso(oc.now(self.s)), "role": "operator", "ticket": self.act,
                "event": {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": "."}})
        except (OSError, ValueError, IndexError):
            pass

    # ---------------------------------------------------------------------------------------------------------- G9
    def g9(self):
        held_since, last = None, None
        while True:
            why = oc.holds(self.s)
            if not why:
                break
            if why != last:
                self.line("G9", "held", why=why)
                last = why
            if held_since is None:
                held_since = time.monotonic()
            if self.s["hold_max_s"] and time.monotonic() - held_since > self.s["hold_max_s"]:
                return "timeout"
            time.sleep(max(0.05, self.s["poll_s"]))
        self.line("G9", "pass")
        return "held" if held_since is not None else "clear"

    # ------------------------------------------------------------------------------------------------------ apply
    def apply(self):
        s = self.s
        env = self.live_env()
        repo = s["repo"]
        rc, head, _ = oc.git(repo, "rev-parse", "HEAD")
        head = head.decode().strip() if rc == 0 else None
        st = UndoState(self, head)
        st.controls = control_snapshot(s, env)
        st.tree_before = tree_state(repo, ignored=False, keep=True)
        hooks_before = git_controls(repo)
        oc.write_atomic(journal_path(s), json.dumps({
            "act": self.act, "manifest_sha256": self.sha, "frozen": self.frozen, "class": self.cls,
            "stage": "applying", "head": head, "commit": None, "time": oc.iso(oc.now(s)), "freeze": self.freeze}))
        try:
            rc, out, err = self.apply_sh("apply", repo, env)
            if rc != 0:
                return st.fail("apply", f"apply.sh apply exited {rc}; undone from the backups", "refused")
            for t in self.manifest["touched"]:
                if oc.live_hash(s, t["root"], t["path"], env) != t["after"]:
                    return st.fail("apply", f"{t['root']}:{t['path']} is not as the manifest states it after the "
                                            "apply; undone", "refused")
            after_tree = tree_state(repo, ignored=False, keep=False)
            mine = {("repo", t["path"]) for t in self.repo_touched()}
            extra = sorted(p for p in diff_states({("repo", k): v for k, v in st.tree_before[0].items()},
                                                  {("repo", k): v for k, v in after_tree[0].items()}, CLEAN)
                           if p not in mine)
            hooks_after = git_controls(repo)
            extra += sorted(("repo", p) for p in set(hooks_before) | set(hooks_after)
                            if hooks_before.get(p) != hooks_after.get(p) and ("repo", p) not in mine)
            self.checks = []
            red = None
            for c in self.manifest["checks"]:
                rc, out, _ = oc.run(["bash", "-c", c["cmd"]], cwd=repo, env=env, timeout=s["check_timeout_s"])
                ok = check_ok(c, rc, out)
                last = [ln.strip() for ln in out.decode("utf-8", "replace").splitlines() if ln.strip()]
                self.checks.append({"cmd": c["cmd"], "exit": rc, "count": last[-1] if last else None, "ok": ok})
                if not ok and red is None:
                    red = c["cmd"]
            if extra:
                return st.fail("unlisted", "the apply changed a file not on the touched list (unlisted): "
                               + ", ".join(p for _, p in extra[:5]) + "; undone", "undone")
            if red is not None:
                return st.fail("checks", f"a check is red after the apply ({red[:120]}); undone", "undone",
                               kind="red")
            committed = stageable(repo, self.repo_touched(), env)
            paths = [t["path"] for t in committed]
            if paths:
                rc, _, err = oc.git(repo, "add", "-A", "--", *paths, env=env)
                if rc != 0:
                    return st.fail("staged", "git add failed; undone", "refused")
                st.staged = True
                if staged_list(repo, env) != expected_staged(committed):
                    return st.fail("staged", "git diff --cached --name-status is not the touched list; undone",
                                   "refused")
                rc, commit = self.git_commit(env, undo=False)
                if rc != 0:
                    return st.fail("commit", "the commit failed; undone", "refused")
                self.commit = commit
                st.committed = commit
                j = json.load(open(journal_path(s)))
                j.update(stage="committed", commit=commit)
                oc.write_atomic(journal_path(s), json.dumps(j))
            self.hook("in-apply-checks")   # DEC-1106 (1): applied, checks green, committed; the after-check next
            if self.cls == "a":
                why = after_checks(self, st, env)
                if why:
                    return st.fail("after-check", why + "; undone", "undone")
        except Exception as exc:  # fail closed: an error mid-apply undoes
            return st.fail("apply", f"an error mid-apply ({exc.__class__.__name__}: {exc}); undone", "refused")
        oc.remove_tree(journal_path(s))
        notice = None
        when = oc.now(s)
        if self.cls == "b" or oc.within_first_14_days(s, when):
            notice = "applied"
        self.line("apply", "applied", undo="ready", notice=notice, touched=self.manifest["touched"],
                  review_sha256=self.review_sha, replay=getattr(self, "replay_detail", None))
        if notice:
            green = "checks green" if self.checks is not None else "no checks"
            oc.notify(s, self.act, "info", "applied",
                      f"Applied {self.act} ({self.cls}) {when.strftime('%H:%M')}, {green}; to undo, say "
                      f"`undo {self.act} {self.sha[:8]}`", manifest_sha256=self.sha, commit=self.commit,
                      short=f"applied ({self.cls}) {when.strftime('%H:%M')}, {green}, commit {(self.commit or '-')[:12]}",
                      undo=f"to undo, say: undo {self.act} {self.sha[:8]}")
        return self.result("applied", undo=f"undo {self.act} {self.sha[:8]}", checks=self.checks), 0

    def git_commit(self, env, undo=False, extra_trailers=()):
        repo = self.s["repo"]
        subject = (f"{self.act}: undone by the operator" if undo else
                   f"{self.act}: applied by the operator agent, class ({self.cls})")
        trailers = [f"Role: operator", f"Act: {self.act}", f"Act-sha: {self.sha}", f"Class: {self.cls}",
                    f"Review: {self.review_sha}"]
        if self.cls == "b" and self.yes is not None:
            trailers.append(f"Approved-by: owner (chat, {oc.iso(self.yes)})")
        trailers += list(extra_trailers)
        cenv = dict(env)
        rc, out, _ = oc.git(repo, "config", "user.email", env=env)
        if rc != 0 or not out.strip():
            cenv.update(GIT_AUTHOR_NAME="operator", GIT_AUTHOR_EMAIL="operator@localhost",
                        GIT_COMMITTER_NAME="operator", GIT_COMMITTER_EMAIL="operator@localhost")
        rc, _, err = oc.git(repo, "commit", "-q", "-m", subject, "-m", "\n".join(trailers), env=cenv)
        if rc != 0:
            return rc, None
        rc2, sha, _ = oc.git(repo, "rev-parse", "HEAD", env=env)
        return 0, sha.decode().strip()

    # -------------------------------------------------------------------------------------------------------- run
    def go(self):
        for name, step in (("G1", self.g1), ("G2", self.g2), ("G3", self.g3), ("G4", self.g4), ("G5", self.g5),
                           ("G6", self.g6), ("recompute", self.recompute), ("G7", self.g7), ("G8", self.g8)):
            self.at = name
            step()
        while True:
            self.at = "G9"
            held = self.g9()
            if held == "timeout":
                raise oc.Refused("G9", "the hold outlasted hold_max_s")
            self.recompute(log_pass=False)
            if held == "held":
                self.g7(log_pass=False)
            # the commit freeze (DEC-1106 (3)), written only when no one holds it; a run that finds it taken
            # between G9 and here waits at G9 again (it never refuses for a hold)
            self.freeze = oc.claim_freeze(self.s, self.act, self.sha)
            if self.freeze:
                break
        self.at = "apply"
        try:
            return self.apply()
        finally:
            oc.release_freeze(self.s, self.freeze)     # only its own: never a freeze another run wrote


CLEAN = "clean"
CRONTAB_STUB = """#!/bin/bash
# The dry run's crontab: reads and writes $OPERATOR_CRONTAB_FILE, never the live crontab.
f="$OPERATOR_CRONTAB_FILE"
case "${1:-}" in
  -l) [ -f "$f" ] && { cat "$f"; exit 0; }; echo "no crontab for $USER" >&2; exit 1 ;;
  -r) rm -f "$f"; exit 0 ;;
  -) cat > "$f"; exit 0 ;;
  "") cat > "$f"; exit 0 ;;
  -*) echo "crontab stub: $1 not supported" >&2; exit 2 ;;
  *) cat "$1" > "$f"; exit 0 ;;
esac
"""


def clean_key_value(v):
    return v


def is_after(t, data):
    """True when a touched file's bytes (None: absent) are the ACT's own after-state: the frozen after-copy's sha, or
    absent for a deletion (DEC-1106 (1))."""
    if t["after"] is None:
        return data is None
    return data is not None and oc.sha256_bytes(data) == t["after"]


def is_before(t, data):
    if t["before"] is None:
        return data is None
    return data is not None and oc.sha256_bytes(data) == t["before"]


def dry_want(t, a):
    want = t["after"]
    return want if want is not None else None


def diff_states(a, b, cron_default=None):
    """The keys whose value differs between two states (a key missing from a tree state is clean)."""
    out = set()
    for k in set(a) | set(b):
        if a.get(k, CLEAN) != b.get(k, CLEAN):
            out.add(k)
    return out


def tree_state(repo, ignored=True, keep=False):
    """{path: sha256 or None} for every path git status reports in a tree (a path not reported is clean, as HEAD).
    With keep, also the bytes of each dirty file (to restore it): returns (state, contents)."""
    args = ["status", "--porcelain", "-z", "--untracked-files=all", "--no-renames"]
    if ignored:
        args.append("--ignored=matching")
    rc, out, err = oc.git(repo, "-c", "core.quotePath=false", *args, timeout=1800)
    if rc != 0:
        raise oc.Refused("G8" if ignored else "apply", f"git status failed in {repo}")
    st, contents = {}, {}
    toks = out.decode("utf-8", "surrogateescape").split("\0")
    i = 0
    while i < len(toks):
        tok = toks[i]
        i += 1
        if len(tok) < 4:
            continue
        xy, path = tok[:2], tok[3:]
        if xy[0] in "RC":
            i += 1
        full = os.path.join(repo, path)
        if path.endswith("/"):
            for p, h in walk_state(full).items():
                st[path + p] = h
            continue
        if os.path.islink(full):
            st[path] = oc.sha256_bytes(("link:" + os.readlink(full)).encode())
        elif os.path.isfile(full):
            st[path] = oc.sha256_file(full)
            if keep and os.path.getsize(full) <= 32 << 20:
                with open(full, "rb") as f:
                    contents[path] = f.read()
        else:
            st[path] = None
    return st, contents


def git_controls(repo):
    """{repo-relative path: sha256} for the git hooks and the git config (F11), for the live unlisted-file check."""
    out = {".git/hooks/" + p: h for p, h in walk_state(os.path.join(repo, ".git/hooks")).items()}
    cfg = read_bytes(os.path.join(repo, ".git/config"))
    out[".git/config"] = None if cfg is None else oc.sha256_bytes(cfg)
    return out


def walk_state(folder):
    out = {}
    for top, dirs, files in os.walk(folder):
        for d in list(dirs):
            if os.path.islink(os.path.join(top, d)):
                rel = os.path.relpath(os.path.join(top, d), folder).replace(os.sep, "/")
                out[rel] = oc.sha256_bytes(("link:" + os.readlink(os.path.join(top, d))).encode())
                dirs.remove(d)
        for fn in files:
            full = os.path.join(top, fn)
            rel = os.path.relpath(full, folder).replace(os.sep, "/")
            if os.path.islink(full):
                out[rel] = oc.sha256_bytes(("link:" + os.readlink(full)).encode())
            elif os.path.isfile(full):
                out[rel] = oc.sha256_file(full)
    return out


def staged_list(repo, env):
    rc, out, _ = oc.git(repo, "-c", "core.quotePath=false", "diff", "--cached", "--name-status", "--no-renames",
                        env=env)
    if rc != 0:
        return None
    rows = set()
    for ln in out.decode("utf-8", "replace").splitlines():
        parts = ln.split("\t")
        if len(parts) == 2:
            rows.add((parts[0][:1], parts[1]))
        elif ln.strip():
            rows.add(("?", ln))
    return rows


def expected_staged(touched, reverse=False):
    rows = set()
    for t in touched:
        b, a = (t["after"], t["before"]) if reverse else (t["before"], t["after"])
        rows.add(("A" if b is None else "D" if a is None else "M", t["path"]))
    return rows


def stageable(repo, touched, env):
    """The listed repository files a commit can hold: never a path under .git/, never an ignored untracked file
    (`.claude/settings.local.json`): those are applied and checked, not committed."""
    out = []
    for t in touched:
        if t["path"].startswith(".git/"):
            continue
        rc, _, _ = oc.git(repo, "check-ignore", "-q", "--", t["path"], env=env)
        if rc == 0:
            continue
        out.append(t)
    return out


def journal_path(s):
    return os.path.join(s["log_dir"], "journal.json")


def lock_path(s):
    return os.path.join(s["log_dir"], "operator.lock")


# ======================================================================================================= the controls
def control_snapshot(s, env):
    """The control files' bytes (S15): the hook folder and the rest of .claude/**, .rulesync/**, the git hooks,
    `crontab -l`, the pin, the dead-man's and the sentinel's code, the path map, and the operator's install."""
    snap = {}
    repo = s["repo"]
    for tree in CONTROL_REPO_TREES:
        base = os.path.join(repo, tree)
        if os.path.isdir(base):
            for top, dirs, files in os.walk(base):
                dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(top, d))]
                for fn in files:
                    full = os.path.join(top, fn)
                    rel = os.path.relpath(full, repo).replace(os.sep, "/")
                    snap[("repo", rel)] = read_bytes(full)
    for rel in CONTROL_REPO_FILES:
        snap[("repo", rel)] = read_bytes(os.path.join(repo, rel))
    # F11: the repository's git config (core.hooksPath lives there) and the folder core.hooksPath names, wherever
    snap[("repo", ".git/config")] = read_bytes(os.path.join(repo, ".git/config"))
    hp = hooks_path(repo, env)
    if hp:
        rel_hp = os.path.relpath(hp, repo)
        if not (rel_hp == ".git/hooks" or rel_hp.startswith(".git/hooks/")):
            for p, data in walk_bytes(hp).items():
                snap[("path", os.path.join(hp, p))] = data
    for rel in CONTROL_HOME_FILES:
        snap[("home", rel)] = read_bytes(os.path.join(s["home"], rel))
    snap[("crontab", "crontab")] = oc.crontab_bytes(env)
    inst = s["install"]
    for top, dirs, files in os.walk(inst):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            full = os.path.join(top, fn)
            rel = os.path.relpath(full, inst).replace(os.sep, "/")
            if rel == oc.FREEZE_NAME or os.path.abspath(full) == s["freeze"]:
                continue                   # the commit freeze is not a control file (DEC-1106 (3))
            snap[("install", rel)] = read_bytes(full)
    return snap


def hooks_path(repo, env=None):
    """The absolute folder git's core.hooksPath names for a repository, or None when it is not set."""
    try:
        rc, out, _ = oc.git(repo, "config", "--get", "core.hooksPath", env=env, timeout=60)
    except OSError:
        return None
    if rc != 0 or not out.strip():
        return None
    p = os.path.expanduser(out.decode("utf-8", "replace").strip())
    return os.path.normpath(p if os.path.isabs(p) else os.path.join(repo, p))


def walk_bytes(folder):
    out = {}
    if not os.path.isdir(folder):
        return out
    for top, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(top, d))]
        for fn in files:
            full = os.path.join(top, fn)
            out[os.path.relpath(full, folder).replace(os.sep, "/")] = read_bytes(full)
    return out


def read_bytes(path):
    if os.path.islink(path):
        return ("link:" + os.readlink(path)).encode()
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return f.read()


def after_checks(run, st, env):
    """S15 for an (a) ACT: the controls as before but for the touched files at their computed after-hashes; for
    path-map or deny-list additions, the guard replayed on the last 48 hours of calls turns no allowed call to
    refused but those the review listed. Returns the reason for an undo, or None."""
    s = run.s
    now_snap = control_snapshot(s, env)
    touched = {(t["root"], t["path"]): t for t in run.manifest["touched"]}
    bad = []
    for key in sorted(set(st.controls) | set(now_snap)):
        before, after = st.controls.get(key), now_snap.get(key)
        if before == after:
            continue
        if key in touched and is_after(touched[key], after):
            continue
        bad.append(f"{key[0]}:{key[1]}")
    if bad:
        # the undo that follows undoes the ACT's own touched files only; these are left as they are (DEC-1106 (1))
        return "a control file changed (" + ", ".join(bad) + ")"
    lists = [t for t in run.repo_touched() if t["path"] in REPLAY_FILES or DENY_LIST_FILE.match(t["path"])]
    if not lists:
        return None
    try:
        turned = replay(run, st, lists, env)
    except oc.Refused as r:
        return r.reason
    unlisted = sorted(set(turned) - set(run.verdict.get("replay_refused") or []))
    if unlisted:
        return "the guard replay turns an allowed call to refused that the review did not list: " + ", ".join(unlisted[:5])
    return None


def action_sha(tool, tin):
    """The guard's sha256 of a call (its action_bytes, .claude/hooks/pretooluse.py; read there, not imported)."""
    return hashlib.sha256(json.dumps({"tool": tool if isinstance(tool, str) else None, "input": tin}, sort_keys=True,
                                     separators=(",", ":"), ensure_ascii=False).encode("utf-8", "surrogatepass")).hexdigest()


def _refuse(why):
    raise oc.Refused("after-check", "the guard replay refused: " + why)


def _dict_line(text):
    try:
        d = json.loads(text)
    except ValueError:
        return None
    return d if isinstance(d, dict) else None


def read_call_set(s):
    """The CTO's call set (DEC-1108 (2)): (since, until, the calls and dropped calls in the window), each line with its
    recomputed `_sha`. Refuses on no header, a window ahead of the clock, stale or short, and a malformed line."""
    if not os.path.isfile(s["calls"]):
        _refuse("no call set is configured (the calls setting's file does not exist)")
    try:
        with open(s["calls"], encoding="utf-8") as f:
            rows = [ln for ln in f.read().splitlines() if ln.strip()]
    except (OSError, UnicodeDecodeError):
        _refuse("the call set cannot be read")
    head = _dict_line(rows[0]) if rows else None
    w = head.get("window") if head else None
    since, until = (oc.parse_iso(w.get("since")), oc.parse_iso(w.get("until"))) if isinstance(w, dict) else (None, None)
    if since is None or until is None:
        _refuse("no header (the set's first line must give its window)")
    clock = oc.now(s)
    if until > clock + oc.timedelta(minutes=5):
        _refuse(f"the window's until ({w['until']}) is ahead of the clock")
    if until < clock - oc.timedelta(hours=s["replay_stale_h"]):
        _refuse(f"window stale (until {w['until']}, more than {s['replay_stale_h']:g} hours ago)")
    if until - since < oc.timedelta(hours=REPLAY_WINDOW_H):
        _refuse(f"window short (since {w['since']} to until {w['until']}, under {REPLAY_WINDOW_H} hours)")
    out = []
    for n, ln in enumerate(rows[1:], start=2):
        c = _dict_line(ln)
        if c is not None and isinstance(c.get("event"), dict):
            c["_sha"] = action_sha(c["event"].get("tool_name"), c["event"].get("tool_input"))
        elif c is not None and isinstance(c.get("sha256"), str) and oc.SHA_RE.match(c["sha256"]) \
                and isinstance(c.get("dropped"), str) and c["dropped"].strip():
            c["_sha"] = c["sha256"]
        else:
            _refuse(f"the call set has a malformed line (line {n}; fail closed)")
        c["_session"] = c.get("session") if isinstance(c.get("session"), str) else None
        t = c["_t"] = oc.parse_iso(c.get("time"))
        if t is None or since <= t <= until:          # outside the window: neither checked nor re-judged
            out.append(c)
    return since, until, out


def read_guard_log(s, since, until):
    """The guard's call log's lines on the UTC days from since - 2 min to until + 2 min, each with its parsed `_t`."""
    where = s["guard_calls"]
    if not os.path.isdir(where):
        _refuse(f"log missing ({where} is not a folder)")
    day, last = (since - LOG_SLACK).astimezone(oc.timezone.utc).date(), (until + LOG_SLACK).astimezone(oc.timezone.utc).date()
    out = []
    while day <= last:
        p = os.path.join(where, f"{day.isoformat()}.jsonl")
        if os.path.lexists(p + ".capped"):
            _refuse(f"log capped ({day.isoformat()}: the guard stopped writing that day)")
        if os.path.lexists(p):
            try:
                with open(p, encoding="utf-8") as f:
                    rows = [ln for ln in f.read().splitlines() if ln.strip()]
            except (OSError, UnicodeDecodeError):
                rows = ["\0"]
            for ln in rows:
                r = _dict_line(ln)
                t = oc.parse_iso(r.get("time")) if r else None
                if t is None or not isinstance(r.get("session"), str) or not (
                        r.get("sha256") is None or (isinstance(r["sha256"], str) and oc.SHA_RE.match(r["sha256"]))):
                    _refuse(f"log malformed ({day.isoformat()}; fail closed)")
                r["_t"] = t
                out.append(r)
        day += oc.timedelta(days=1)
    return out


def check_against_log(s, since, until, lines):
    """DEC-1108 (2), both ways by sha256 before anything is re-judged. Returns {id(call line): its log lines}."""
    log = read_guard_log(s, since, until)
    by_key = {}
    for r in log:
        if since - LOG_SLACK <= r["_t"] <= until + LOG_SLACK and r["sha256"]:
            by_key.setdefault((r["session"], r["sha256"]), []).append(r)
    no_log = [str(c.get("id")) for c in lines if (c["_session"], c["_sha"]) not in by_key]
    have = {(c["_session"], c["_sha"]) for c in lines}
    missing = list(dict.fromkeys(
        f"{r['session'][:8]} {(r['sha256'] or 'null')[:12]} {r['time']}" for r in log
        if since + LOG_SLACK <= r["_t"] <= until - LOG_SLACK and LIVE_SESSION.match(r["session"])
        and r.get("tree") in LIVE_TREES and (not r["sha256"] or (r["session"], r["sha256"]) not in have)))
    parts = []
    if no_log:
        parts.append(f"{len(no_log)} set call(s) with no line in the guard's log: " + ", ".join(no_log[:5]))
    if missing:
        parts.append(f"{len(missing)} logged live call(s) missing from the set (session, sha256, time): "
                     + ", ".join(missing[:5]))
    if parts:
        _refuse("the call set does not match the guard's call log by sha256 (DEC-1108 (2)): " + "; ".join(parts))
    return {id(c): by_key[(c["_session"], c["_sha"])] for c in lines}


def with_log_role(call, rows):
    """The call as the guard ran it: the role and ticket of its matching log line (the nearest in time) win."""
    t = call["_t"]
    r = min(rows, key=lambda x: abs((x["_t"] - t).total_seconds())) if t is not None else rows[0]
    return dict(call, role=r.get("role") or None, ticket=r.get("ticket") or None)


def replay(run, st, lists, env):
    """The ids of calls allowed by the old map and the old deny lists that the new ones refuse; first the call set
    is checked against the guard's call log both ways (DEC-1108 (2)), and refused on any mismatch."""
    s = run.s
    since, until, lines = read_call_set(s)
    matched = check_against_log(s, since, until, lines)
    dropped = {}
    for c in lines:
        if "event" not in c:
            dropped[c["dropped"]] = dropped.get(c["dropped"], 0) + 1
    calls = [with_log_role(c, matched[id(c)]) for c in lines if "event" in c]
    run.replay_detail = {"calls": len(calls), "turned": [], "dropped": dropped,
                         "window": [oc.iso(since), oc.iso(until)]}
    if not calls:
        return []
    tmp = os.path.abspath(tempfile.mkdtemp(prefix="gov-operator-replay-"))
    calls_dir = os.path.join(tmp, "guard-calls")      # the replay's own hook runs never write the live log
    os.makedirs(calls_dir, mode=0o700)
    try:
        # One tree: the repository at the head before the apply (a clone outside the live tree), with the live
        # .claude/ as it was before (untracked files too); the lists written before, the calls replayed; then the
        # lists written after, the calls replayed again.
        tree = os.path.join(tmp, "tree")
        if st.head:
            rc, _, _ = oc.run(["git", "clone", "-q", "--no-checkout", s["repo"], tree], timeout=1800)
            rc = rc or oc.git(tree, "checkout", "-q", "--detach", st.head, timeout=1800)[0]
            if rc != 0:
                raise oc.Refused("after-check", "the replay's tree cannot be built")
        else:
            os.makedirs(tree)
        for key, data in st.controls.items():
            if key[0] == "repo" and key[1].startswith(".claude/") and data is not None:
                write_file(os.path.join(tree, key[1]), data)

        def put(side):
            for t in lists:
                data = read_bytes(os.path.join(run.frozen, side, "repo", t["path"]))
                if data is None:
                    raise oc.Refused("after-check", f"the bundle does not hold {t['path']} {side} for the replay")
                write_file(os.path.join(tree, t["path"]), data)

        put("before")
        old = {i: guard_decision(s, tree, c, calls_dir) for i, c in enumerate(calls)}
        put("after")
        added = added_deny_rules(run, lists)
        turned, detail = [], []
        for i, c in enumerate(calls):
            ev = c.get("event") or {}
            tin = ev.get("tool_input") or {}
            what = {"id": c.get("id"), "role": c.get("role"), "tool": ev.get("tool_name"),
                    "target": str(tin.get("file_path") or tin.get("path") or tin.get("command") or "")[:160]}
            if old[i] != "allow":
                detail.append(dict(what, old=old[i]))
                continue
            new = guard_decision(s, tree, c, calls_dir)
            if new == "allow" and any(rule_matches(r, c, tree, s["home"]) for r in added):
                new = "refuse (an added deny rule)"
            detail.append(dict(what, old=old[i], new=new))
            if new != "allow":
                turned.append(str(c.get("id")))
        run.replay_detail.update(turned=turned, decisions=detail[:50])
        return turned
    finally:
        oc.remove_tree(tmp)


def write_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def guard_decision(s, tree, call, calls_dir):
    """The guard's decision on one call, run on a tree as Claude Code runs it: allow, or refuse (exit 2, a deny,
    or any error: fail closed). The hook logs to calls_dir, the replay's own folder, never the live log."""
    hook = os.path.join(tree, ".claude/hooks/pretooluse.py")
    if not os.path.isfile(hook):
        return "refuse"
    ev = dict(call["event"])        # the call's paths stay as logged (relative to the repository); its cwd is the tree's
    cwd = ev.get("cwd") or "."
    ev["cwd"] = os.path.normpath(os.path.join(tree, cwd)) if not str(cwd).startswith("/") else cwd
    env = oc.clean_env(s, s["home"], extra={"CLAUDE_PROJECT_DIR": tree, "PYTHONPATH": os.path.join(s["repo"], "src")})
    env["CLAUDE_PROJECT_DIR"] = tree
    env["GOV_GUARD_CALLS_DIR"] = calls_dir
    if call.get("role"):
        env["GOV_ROLE"] = str(call["role"])
    if call.get("ticket"):
        env["GOV_TICKET"] = str(call["ticket"])
    rc, out, _ = oc.run(["python3", hook], cwd=tree, env=env, timeout=60, input_bytes=json.dumps(ev).encode())
    if rc == 2:
        return "refuse"
    if rc != 0:
        return "refuse"
    try:
        o = json.loads(out.decode("utf-8", "replace").strip().splitlines()[-1]) if out.strip() else {}
    except (ValueError, IndexError):
        o = {}
    dec = ((o or {}).get("hookSpecificOutput") or {}).get("permissionDecision") if isinstance(o, dict) else None
    return "refuse" if dec == "deny" else "allow"


def added_deny_rules(run, lists):
    out = []
    for t in lists:
        if not DENY_LIST_FILE.match(t["path"]):
            continue
        b = read_bytes(os.path.join(run.frozen, "before", "repo", t["path"]))
        a = read_bytes(os.path.join(run.frozen, "after", "repo", t["path"]))
        try:
            if t["path"].endswith(".jsonc"):
                ob = json.loads(act_class.strip_jsonc(b.decode())) if b else {}
                oa = json.loads(act_class.strip_jsonc(a.decode())) if a else {}
                for tool, rules in ((oa.get("permission") or {}).items()):
                    old = (ob.get("permission") or {}).get(tool) or {}
                    for pat, v in (rules or {}).items():
                        if v == "deny" and old.get(pat) != "deny":
                            out.append(f"{tool.capitalize()}({pat})")
            else:
                ob = json.loads(b.decode()) if b else {}
                oa = json.loads(a.decode()) if a else {}
                old = set(((ob.get("permissions") or {}).get("deny")) or [])
                out += [r for r in ((oa.get("permissions") or {}).get("deny") or []) if r not in old]
        except (ValueError, AttributeError, UnicodeDecodeError):
            raise oc.Refused("after-check", f"{t['path']} cannot be parsed for the replay")
    return out


def rule_matches(rule, call, tree, home):
    import fnmatch
    m = re.match(r"^([A-Za-z_]+)(?:\((.*)\))?$", str(rule).strip())
    ev = call.get("event") or {}
    if not m or m.group(1).lower() != str(ev.get("tool_name", "")).lower():
        return False
    spec = m.group(2)
    if spec is None or spec in ("", "*"):
        return True
    tin = ev.get("tool_input") or {}
    if m.group(1).lower() == "bash":
        cmd = str(tin.get("command") or "")
        if spec.endswith(":*"):
            return cmd.startswith(spec[:-2])
        return fnmatch.fnmatchcase(cmd, spec)
    target = tin.get("file_path") or tin.get("path") or tin.get("notebook_path")
    if not isinstance(target, str):
        return False
    target = target if target.startswith("/") else os.path.join(tree, target)
    if spec.startswith("//"):
        pat = spec[1:]
    elif spec.startswith("~/"):
        pat = os.path.join(home, spec[2:])
    elif spec.startswith("/"):
        pat = os.path.join(tree, spec[1:])
    else:
        pat = os.path.join(tree, spec)
    return fnmatch.fnmatchcase(os.path.normpath(target), pat.replace("**", "*"))


# =========================================================================================================== the undo
class UndoState:
    """What an undo needs: the head before, the controls' bytes, the tree's dirty files before, staged, committed."""

    def __init__(self, run, head):
        self.run, self.head = run, head
        self.controls = {}
        self.tree_before = ({}, {})
        self.staged = False
        self.committed = None
        self.left = []                     # live differences not the ACT's own, left as written (DEC-1106 (1))

    def fail(self, gate, reason, result, kind="undo"):
        run, s = self.run, self.run.s
        ok, why = undo_live(run, self)
        left = left_text(self.left)
        if not ok:
            hold_lock(s, run.act, run.sha, f"{reason}; the undo failed too: {why}{left}")
            run.line(gate, "refused", undo="failed", reason=reason + left, notice="lock", left=self.left)
            oc.notify(s, run.act, "P1", "lock", f"{run.act}: {reason}; the UNDO FAILED ({why}){left}: lock held, "
                                                "nothing else is applied", manifest_sha256=run.sha,
                      short=f"{gate}: {reason}", undo=f"UNDO FAILED ({why[:40]}): lock held")
            return run.result("refused", gate, f"{reason}; the undo failed ({why}){left}: lock held", undo="failed",
                              checks=run.checks, left=self.left), 1
        if self.left:
            reason = f"{reason}; the ACT's own touched files undone{left}; lock held, nothing else is applied"
            hold_lock(s, run.act, run.sha, reason)
        run.line(gate, result, undo="done", reason=reason, notice=kind, replay=getattr(run, "replay_detail", None),
                 left=self.left, lock=bool(self.left))
        oc.notify(s, run.act, "P1", kind, f"{run.act}: {reason}", manifest_sha256=run.sha, short=f"{gate}: {reason}",
                  undo="own files undone; others left: lock held" if self.left else "undone byte for byte")
        return run.result(result, gate, reason, undo="done", checks=run.checks, left=self.left,
                          lock=bool(self.left)), 1


def left_text(left):
    """The P1's words for the files left as written: each named by its path relative to its root."""
    if not left:
        return ""
    return ("; left exactly as written, not shown to be the ACT's own change (someone else's, or unknown): "
            + ", ".join(left))


def hold_lock(s, act, sha, why):
    oc.write_atomic(lock_path(s), json.dumps({"act": act, "manifest_sha256": sha, "time": oc.iso(oc.now(s)),
                                              "why": why}) + "\n")


def undo_live(run, st):
    """The restore rule (F15, DEC-1106 (1)): the agent writes back only what it can show is its own change. A touched
    file at the ACT's after-copy is undone (by the frozen apply.sh undo; when some touched file is at third bytes,
    apply.sh is not run, as it would write over them, and each own file is put back from the frozen before/ copy);
    a touched file at third bytes, a control file the ACT does not list, or any other tree difference is left exactly
    as it is and named in st.left (the caller holds the lock and names each in its P1). The undo commit holds only the
    own files; a commit someone else made meanwhile stays in HEAD's history. (ok, why)."""
    s = run.s
    env = run.live_env()
    repo = s["repo"]
    tlist = run.manifest["touched"]
    touched = {(t["root"], t["path"]) for t in tlist}
    live = {(t["root"], t["path"]): oc.live_file(s, t["root"], t["path"], env) for t in tlist}
    third = [t for t in tlist if not is_after(t, live[(t["root"], t["path"])])
             and not is_before(t, live[(t["root"], t["path"])])]
    mine = [t for t in tlist if t not in third]
    left = {f"{t['root']}:{t['path']}" for t in third}
    if not third:
        rc, _, err = run.apply_sh("undo", repo, env)
        if rc != 0:
            st.left = sorted(left)
            return False, f"apply.sh undo exited {rc}"
    else:
        for t in mine:
            if not is_after(t, live[(t["root"], t["path"])]):
                continue
            data = None
            if t["before"] is not None:
                data = read_bytes(os.path.join(run.frozen, "before", t["root"], t["path"]))
                if data is None or oc.sha256_bytes(data) != t["before"]:
                    st.left = sorted(left)
                    return False, f"{t['root']}:{t['path']} has no frozen before/ copy to undo it from"
            try:
                restore_live_file(s, t["root"], t["path"], data, env)
            except OSError as exc:
                st.left = sorted(left)
                return False, f"{t['root']}:{t['path']} could not be undone ({exc.__class__.__name__})"
    for t in mine:
        if oc.live_hash(s, t["root"], t["path"], env) != t["before"]:
            st.left = sorted(left)
            return False, f"{t['root']}:{t['path']} is not restored byte for byte"
    try:
        left |= foreign_differences(s, st, touched, env)
    except Exception as exc:  # fail closed: what cannot be compared is not written either
        left.add(f"the live state could not be compared ({exc.__class__.__name__})")
    st.left = sorted(left)
    committed = stageable(repo, [t for t in mine if t["root"] == "repo"], env)
    paths = [t["path"] for t in committed]
    if paths and st.committed:
        rc, _, _ = oc.git(repo, "add", "-A", "--", *paths, env=env)
        if rc != 0 or staged_list(repo, env) != expected_staged(committed, reverse=True):
            return False, "the undo's staged list is not the touched list"
        rc, commit = run.git_commit(env, undo=True, extra_trailers=("Undo: yes",))
        if rc != 0:
            return False, "the undo's commit failed"
        run.undo_commit = commit
    elif paths:
        oc.git(repo, "reset", "-q", "--", *paths, env=env)
    oc.remove_tree(journal_path(s))
    return True, ""


def foreign_differences(s, st, touched, env):
    """The live differences since the undo state was taken that are not a touched file: the control files (S15's
    list) and the repository's tree as git status reports it. Named by root and path; never written."""
    out = set()
    now_c = control_snapshot(s, env)
    for key in set(st.controls) | set(now_c):
        if key not in touched and st.controls.get(key) != now_c.get(key):
            out.add(f"{key[0]}:{key[1]}")
    before = st.tree_before[0]
    after = tree_state(s["repo"], ignored=False, keep=False)[0]
    for path in set(before) | set(after):
        if ("repo", path) not in touched and before.get(path, CLEAN) != after.get(path, CLEAN):
            out.add(f"repo:{path}")
    return out


def root_base(s, root):
    """The folder a snapshot key's root names; the root "path" keys carry an absolute path (core.hooksPath's)."""
    return {"repo": s["repo"], "home": s["home"], "install": s["install"], "path": "/"}[root]


def restore_live_file(s, root, rel, data, env):
    """One live touched file put back to `data` (None: absent)."""
    if root == "crontab":
        if data is None:
            oc.run(["crontab", "-r"], env=env, timeout=60)
        else:
            oc.run(["crontab", "-"], env=env, timeout=60, input_bytes=data)
        return
    full = os.path.join(root_base(s, root), rel)
    if data is None:
        if os.path.lexists(full):
            os.unlink(full)
        return
    mode = os.stat(full).st_mode & 0o7777 if os.path.isfile(full) and not os.path.islink(full) else 0o644
    if os.path.lexists(full):
        os.unlink(full)
    write_file(full, data)
    os.chmod(full, mode)


# ===================================================================================================== the undo step
def undo_step(s, act, sha, approved):
    run = Run(s, act, sha, approved)
    events = oc.read_jsonl(oc.log_path(s))
    applied = [e for e in events if e.get("act") == act and e.get("manifest_sha256") == sha
               and e.get("result") == "applied"]
    if not applied:
        raise oc.Refused("undo", "this ACT and sha were never applied by the operator")
    last = applied[-1]
    at = oc.parse_iso(last.get("time"))
    later = events[events.index(last) + 1:]
    # an undo that left another's file says "refused" (DEC-1107) but its line still carries undo "done"
    if any(e.get("act") == act and e.get("manifest_sha256") == sha
           and (e.get("result") == "undone" or e.get("undo") == "done") for e in later):
        raise oc.Refused("undo", "already undone")
    run.cls = last.get("class")
    run.votes = last.get("votes")
    run.commit = last.get("commit")
    now = oc.now(s)
    if at is None or now - at > oc.timedelta(days=UNDO_DAYS):
        raise oc.Refused("undo", f"the undo is ready for {UNDO_DAYS} days only")
    frozen = os.path.join(s["operator_root"], "acts", f"{act}-{sha[:12]}")
    run.frozen = frozen
    try:
        raw = open(os.path.join(frozen, "manifest.json"), "rb").read()
        run.manifest = json.loads(raw.decode("utf-8"))
        validate_manifest(run.manifest)
    except (OSError, ValueError, UnicodeDecodeError):
        raise oc.Refused("undo", "the frozen copy cannot be read")
    if oc.sha256_bytes(raw) != sha or run.frozen_changed():
        raise oc.Refused("undo", "the frozen copy changed: changed after review")
    mine = {(t["root"], t["path"]) for t in run.manifest["touched"]}
    for e in later:
        if e.get("result") == "applied" and e.get("act") != act:
            other = {(t.get("root"), t.get("path")) for t in e.get("touched") or [] if isinstance(t, dict)}
            if other & mine:
                raise oc.Refused("undo", f"a later ACT ({e.get('act')}) changed the same files")
    wanted = f"undo {act} {sha[:8]}"
    found = oc.find_owner_line(s, wanted, at)
    if not found:
        raise oc.Refused("undo", f"no owner's line '{wanted}' after the apply in the CTO session's transcript")
    run.review_sha = last.get("review_sha256") or (oc.sha256_file(os.path.join(frozen, "review.md"))
                                                   if os.path.isfile(os.path.join(frozen, "review.md")) else None)
    env = run.live_env()
    # a touched file at third bytes is someone else's: undo_live leaves it as written and undoes the ACT's own files
    # (DEC-1106 (1)); with none at third bytes, a file back at its before-copy still refuses here, nothing written
    states = [(t, oc.live_file(s, t["root"], t["path"], env)) for t in run.manifest["touched"]]
    third = [t for t, data in states if not is_after(t, data) and not is_before(t, data)]
    if not third:
        for t, data in states:
            if not is_after(t, data):
                raise oc.Refused("undo", f"{t['root']}:{t['path']} moved since the apply")
    rc, head, _ = oc.git(s["repo"], "rev-parse", "HEAD")
    st = UndoState(run, head.decode().strip() if rc == 0 else None)
    st.controls = control_snapshot(s, env)
    st.tree_before = tree_state(s["repo"], ignored=False, keep=True)
    st.committed = run.commit
    token = oc.claim_freeze(s, act, sha, what="operator-undo")
    if not token:
        raise oc.Refused("undo", "the commit freeze (install/act-in-progress.txt) is held by another run or left "
                                 "stale; nothing written; say the undo again once it is gone")
    try:
        oc.write_atomic(journal_path(s), json.dumps({
            "act": act, "manifest_sha256": sha, "frozen": frozen, "class": run.cls, "stage": "undoing",
            "head": st.head, "commit": run.commit, "time": oc.iso(now), "freeze": token}))
        run.undo_commit = None
        ok, why = undo_live(run, st)
    finally:
        oc.release_freeze(s, token)
    left = left_text(st.left)
    if not ok:
        hold_lock(s, act, sha, f"the owner's undo failed: {why}{left}")
        run.line("undo", "refused", undo="failed", reason=why + left, notice="lock", left=st.left)
        oc.notify(s, act, "P1", "lock", f"{act}: the owner's UNDO FAILED ({why}){left}: lock held",
                  manifest_sha256=sha)
        return run.result("refused", "undo", f"the undo failed ({why}){left}: lock held", undo="failed",
                          left=st.left), 1
    run.commit = getattr(run, "undo_commit", None) or run.commit
    if st.left:
        # DEC-1107: another's file left untouched is never reported as a success: "refused", exit 1, the P1 naming
        # each file and the lock held; the ACT's own touched files are undone all the same
        text = (f"{act}: refused: the owner's undo ({oc.iso(found[2])}) undid the ACT's own touched files only{left}; "
                "lock held, nothing else is applied")
        hold_lock(s, act, sha, text)
        run.line("undo", "refused", undo="done", notice="undo", typed=oc.iso(found[2]), reason=text,
                 left=st.left, lock=True)
        oc.notify(s, act, "P1", "undo", text, manifest_sha256=sha,
                  short=f"undo refused: others left ({oc.iso(found[2])})",
                  undo="own files undone; others left: lock held")
        return run.result("refused", "undo", text[len(act) + 2:], undo="done", left=st.left, lock=True), 1
    text = f"Undone {act} on the owner's line ({oc.iso(found[2])})"
    run.line("undo", "undone", undo="done", notice="undo", typed=oc.iso(found[2]), left=[], lock=False)
    oc.notify(s, act, "P1", "undo", text, manifest_sha256=sha,
              short=f"undone on the owner's line ({oc.iso(found[2])})", undo="undone byte for byte")
    return run.result("undone", undo="done", left=[], lock=False), 0


# ================================================================================================= the journal's undo
def recover(s, approved):
    """The next launch after a session died mid-apply: the journal's ACT undone first, a P1 pushed."""
    jp = journal_path(s)
    try:
        j = json.load(open(jp))
        act, sha, frozen = j["act"], j["manifest_sha256"], j["frozen"]
        assert oc.ACT_RE.match(act) and oc.SHA_RE.match(sha)
    except (OSError, ValueError, KeyError, AssertionError, TypeError):
        hold_lock(s, None, None, "an unreadable journal")
        oc.notify(s, None, "P1", "lock", "the operator's journal cannot be read: lock held")
        return {"result": "refused", "gate": "journal", "reason": "an unreadable journal: lock held",
                "approved_sha256": approved[1]}, 1
    run = Run(s, act, sha, approved)
    run.frozen = frozen
    run.cls = j.get("class")
    try:
        raw = open(os.path.join(frozen, "manifest.json"), "rb").read()
        run.manifest = json.loads(raw.decode("utf-8"))
        validate_manifest(run.manifest)
        assert oc.sha256_bytes(raw) == sha
    except (OSError, ValueError, UnicodeDecodeError, AssertionError):
        hold_lock(s, act, sha, "the journal's frozen copy cannot be read")
        run.line("journal", "refused", undo="failed", notice="lock")
        oc.notify(s, act, "P1", "lock", f"{act}: an unfinished journal whose frozen copy cannot be read: lock held")
        return run.result("refused", "journal", "the journal's frozen copy cannot be read: lock held"), 1
    rp = os.path.join(frozen, "review.md")
    run.review_sha = oc.sha256_file(rp) if os.path.isfile(rp) else None
    env = run.live_env()
    st = UndoState(run, j.get("head"))
    st.committed = j.get("commit")
    st.controls = control_snapshot(s, env)
    st.tree_before = tree_state(s["repo"], ignored=False, keep=True)
    already = all(oc.live_hash(s, t["root"], t["path"], env) == t["before"] for t in run.manifest["touched"])
    if already and not st.committed:
        paths = [t["path"] for t in run.repo_touched()]
        if paths:
            oc.git(s["repo"], "reset", "-q", "--", *paths, env=env)
        oc.remove_tree(jp)
        ok, why = True, ""
    else:
        run.undo_commit = None
        ok, why = undo_live(run, st)
    # the dead run's commit freeze: removed only when it still holds the token that run recorded in its journal
    # (a freeze anyone else wrote, or one with other text, stays and holds G9; DEC-1106 (3))
    if ok and isinstance(j.get("freeze"), str):
        oc.release_freeze(s, j["freeze"])
    left = left_text(st.left)
    if not ok:
        hold_lock(s, act, sha, f"the journal's undo failed: {why}{left}")
        run.line("journal", "refused", undo="failed", reason=why + left, notice="lock", left=st.left)
        oc.notify(s, act, "P1", "lock", f"{act}: an unfinished journal; its UNDO FAILED ({why}){left}: lock held",
                  manifest_sha256=sha)
        return run.result("refused", "journal", f"the journal's undo failed ({why}){left}: lock held",
                          undo="failed", left=st.left), 1
    if st.left:
        # DEC-1107: as the owner's undo: "refused", exit 1, the P1 naming each file left, the lock held
        text = (f"{act}: refused: a session died mid-apply; the ACT's own touched files undone at the next launch"
                f"{left}; lock held, nothing else is applied")
        hold_lock(s, act, sha, text)
        run.line("journal", "refused", undo="done", notice="recovered", reason=text, left=st.left, lock=True)
        oc.notify(s, act, "P1", "recovered", text, manifest_sha256=sha)
        return run.result("refused", "journal", text[len(act) + 2:], undo="done", left=st.left, lock=True), 1
    text = f"{act}: a session died mid-apply; undone at the next launch"
    run.line("journal", "undone", undo="done", notice="recovered", left=st.left, lock=False)
    oc.notify(s, act, "P1", "recovered", text, manifest_sha256=sha)
    return run.result("undone", "journal", text[len(act) + 2:], undo="done", left=st.left, lock=False), 0


# ========================================================================================================= the digest
def expected_notice(e, s):
    if "notice" in e:
        return e.get("notice")
    if e.get("disagreement") is True and e.get("gate") == "G6":
        return "disagreement"
    if e.get("result") == "undone":
        return "undo"
    if e.get("result") == "refused" and e.get("gate") in oc.AFTER_G7:
        return "refused"
    return None


def digest(s, since, approved):
    now = oc.now(s)
    since = since or (now - oc.timedelta(hours=24))
    events = oc.read_jsonl(oc.log_path(s))
    pings = oc.read_jsonl(s["pings_log"])
    sent = {}
    for p in pings:
        k = (p.get("act"), p.get("kind"))
        sent[k] = sent.get(k, 0) + 1
    applied, disagreements, missing, refused, undone = [], [], [], [], []
    need = {}
    for e in events:
        t = oc.parse_iso(e.get("time"))
        kind = expected_notice(e, s)
        if kind:
            k = (e.get("act"), kind)
            need[k] = need.get(k, 0) + 1
            if need[k] > sent.get(k, 0) and t is not None and since <= t <= now:
                missing.append({"time": e.get("time"), "act": e.get("act"), "kind": kind, "gate": e.get("gate"),
                                "result": e.get("result"), "manifest_sha256": e.get("manifest_sha256")})
        if t is None or not (since <= t <= now):
            continue
        sha = e.get("manifest_sha256") or ""
        if e.get("result") == "applied":
            applied.append({"act": e.get("act"), "class": e.get("class"), "votes": e.get("votes"),
                            "touched": e.get("touched"), "commit": e.get("commit"),
                            "undo": f"undo {e.get('act')} {sha[:8]}", "time": e.get("time"), "manifest_sha256": sha})
        if e.get("disagreement") is True and e.get("gate") == "G6":
            disagreements.append({"act": e.get("act"), "manifest_sha256": sha, "votes": e.get("votes"),
                                  "time": e.get("time")})
        if e.get("result") == "refused":
            refused.append({"act": e.get("act"), "gate": e.get("gate"), "reason": e.get("reason"),
                            "time": e.get("time")})
        if e.get("result") == "undone":
            undone.append({"act": e.get("act"), "gate": e.get("gate"), "time": e.get("time")})
    return {"result": "digest", "approved_sha256": approved[1], "since": oc.iso(since), "until": oc.iso(now),
            "applied": applied, "disagreements": disagreements, "missing_notices": missing, "refused": refused,
            "undone": undone, "lock": os.path.exists(lock_path(s))}, 0


# =========================================================================================================== the main
def parse_args(argv):
    config, i = None, 0
    if i < len(argv) and argv[i] == "--config":
        if i + 1 >= len(argv):
            raise ValueError("--config needs a file")
        config, i = argv[i + 1], i + 2
    elif i < len(argv) and argv[i].startswith("--config="):
        config, i = argv[i].split("=", 1)[1], i + 1
    rest = argv[i:]
    if not rest:
        raise ValueError("no step")
    return config, rest[0], rest[1:]


def main(argv):
    approved = oc.approved_state()
    base = {"approved_sha256": approved[1]}
    try:
        config, step, args = parse_args(argv)
        s = oc.load_settings(config)
    except (ValueError, OSError) as exc:
        oc.finish(dict(base, result="refused", gate="request", reason=f"usage: {exc}"), 2)
    if not approved[0]:
        act = args[0] if args else None
        try:
            oc.log_event(s, act, args[1] if len(args) > 1 else None, "approved", "refused", reason=approved[2])
        except OSError:
            pass
        oc.finish(dict(base, result="refused", gate="approved", reason="APPROVED mismatch: " + approved[2]), 1)
    if step == "digest":
        since = None
        if args[:1] == ["--since"] and len(args) == 2:
            since = oc.parse_iso(args[1])
            if since is None:
                oc.finish(dict(base, result="refused", gate="request", reason="--since is not an ISO time"), 2)
        elif args:
            oc.finish(dict(base, result="refused", gate="request", reason="usage: digest [--since <ISO>]"), 2)
        res, code = digest(s, since, approved)
        oc.finish(res, code)
    if step == "recover":
        if not os.path.exists(journal_path(s)):
            oc.finish(dict(base, result="idle", reason="no journal"), 0)
        res, code = recover(s, approved)
        oc.finish(res, code)
    if step not in ("run", "undo") or len(args) != 2:
        oc.finish(dict(base, result="refused", gate="request", reason="usage: run|undo <ACT> <manifest sha>"), 2)
    act, sha = args
    if not oc.ACT_RE.match(act) or not oc.SHA_RE.match(sha):
        oc.finish(dict(base, result="refused", gate="request", act=act, manifest_sha256=sha,
                       reason="the request is not ACT-<id> and a 64-hex manifest sha"), 2)
    if os.path.exists(lock_path(s)):
        why = "the lock is held (an undo failed, or a live change not the operator's own was left for the owner)"
        oc.log_event(s, act, sha, "lock", "refused", reason=why)
        oc.finish(dict(base, result="refused", gate="lock", act=act, manifest_sha256=sha,
                       reason=why + "; nothing else is applied"), 1)
    if step == "undo":
        try:
            res, code = undo_step(s, act, sha, approved)
        except oc.Refused as r:
            oc.log_event(s, act, sha, r.gate, "refused", reason=r.reason)
            res, code = dict(base, result="refused", gate=r.gate, reason=r.reason, act=act, manifest_sha256=sha), 1
        except Exception as exc:  # fail closed
            oc.log_event(s, act, sha, "undo", "refused", reason=f"error: {exc}")
            res, code = dict(base, result="refused", gate="undo", reason=f"error: {exc}", act=act,
                             manifest_sha256=sha), 1
        oc.finish(res, code)
    run = Run(s, act, sha, approved)
    gate = "G1"
    try:
        res, code = run.go()
    except oc.Refused as r:
        notice = "refused" if r.gate in oc.AFTER_G7 else None
        extra = dict(r.extra)
        if r.gate == "G6":
            extra.update(disagreement=run.disagreement, why=getattr(run, "code_why", None))
            notice = "disagreement" if run.disagreement else None
        run.line(r.gate, "refused", reason=r.reason, notice=notice, **extra)
        if notice:
            oc.notify(s, act, "P1", "refused", f"{act}: refused at {r.gate}: {r.reason}", manifest_sha256=sha,
                      short=f"refused at {r.gate}: {r.reason}")
        res, code = run.result("refused", r.gate, r.reason, **r.extra), 1
    except Exception as exc:  # fail closed: a gate that errors refuses
        gate = "error"
        why = f"{exc.__class__.__name__}: {exc}"
        # F10: an error at G7 or later (the live state has been read or touched) is pushed as a P1, and the log
        # line names the notice so the digest counts it when it is missing
        after_g7 = run.at in oc.AFTER_G7
        notice = "refused" if after_g7 else None
        run.line(gate, "refused", reason=why, notice=notice, at=run.at)
        if after_g7:
            oc.notify(s, act, "P1", "refused", f"{act}: an unexpected error at {run.at}: {why}; refused",
                      manifest_sha256=sha, short=f"error at {run.at}: {why}")
        res, code = run.result("refused", gate, f"an error ({why}): refused"), 1
    oc.finish(res, code)


if __name__ == "__main__":
    main(sys.argv[1:])

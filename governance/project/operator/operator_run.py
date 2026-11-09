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
  equal to the touched list); G9 the holds (it waits; it never refuses for a hold).
Then the apply: the commit freeze, a journal, apply.sh apply, the checks, the touched-file check, the staged list,
the commit with its trailers, the after-checks for (a) (the control files, the guard replay); any failure undoes.
The result is the last line of stdout, one JSON object; exit 0 when applied, undone (the undo step) or digested.
"""
import json
import os
import re
import shutil
import sys
import tempfile
import time

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
    for k in ("act", "dec", "author", "claimed_class", "touched", "files", "rehearsal", "checks"):
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
    if not isinstance(m.get("rehearsal"), dict):
        raise ValueError("rehearsal is not an object")
    if m.get("commands") is not None and not isinstance(m["commands"], list):
        raise ValueError("commands is not a list")


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
            missing = sorted(set(listed) - found)
            if missing:
                raise oc.Refused("G1", f"the manifest lists a file the bundle does not hold ({missing[0]})")
            if "apply.sh" not in listed:
                raise oc.Refused("G1", "the bundle has no apply.sh")
            oc.remove_tree(final)
            os.rename(tmp, final)
            oc.make_read_only(final)
        finally:
            oc.remove_tree(tmp)
        self.frozen = final
        self.manifest = m
        rp = os.path.join(final, "review.md")
        self.review_sha = oc.sha256_file(rp) if os.path.isfile(rp) else None
        self.line("G1", "pass", frozen=os.path.relpath(final, s["operator_root"]))
        self.hook("after-G1")

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
        r = self.manifest["rehearsal"]
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
        if isinstance(author, str) and reviewer.strip().casefold() == author.strip().casefold():
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
                      f"the highest, ({self.cls}), applies", manifest_sha256=self.sha, votes=self.votes)
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
    def g8(self):
        tmp = tempfile.mkdtemp(prefix="gov-operator-dry-")
        try:
            self._g8(tmp)
        finally:
            oc.remove_tree(tmp)
        self.line("G8", "pass")

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
        try:
            oc.append_jsonl(os.path.join(self.s["log_dir"], "calls.jsonl"), {
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
        oc.write_atomic(journal_path(s), json.dumps({
            "act": self.act, "manifest_sha256": self.sha, "frozen": self.frozen, "class": self.cls,
            "stage": "applying", "head": head, "commit": None, "time": oc.iso(oc.now(s))}))
        oc.write_atomic(s["freeze"], f"{self.act} {self.sha} {oc.iso(oc.now(s))} operator\n")
        try:
            rc, out, err = self.apply_sh("apply", repo, env)
            if rc != 0:
                return st.fail("apply", f"apply.sh apply exited {rc}; undone from the backups", "refused")
            for t in self.manifest["touched"]:
                if oc.live_hash(s, t["root"], t["path"], env) != t["after"]:
                    return st.fail("apply", f"{t['root']}:{t['path']} is not as the manifest states it after the "
                                            "apply; undone", "refused")
            after_tree = tree_state(repo, ignored=False, keep=False)
            extra = sorted(p for p in diff_states({("repo", k): v for k, v in st.tree_before[0].items()},
                                                  {("repo", k): v for k, v in after_tree[0].items()}, CLEAN)
                           if p not in {("repo", t["path"]) for t in self.repo_touched()})
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
            paths = [t["path"] for t in self.repo_touched()]
            if paths:
                rc, _, err = oc.git(repo, "add", "-A", "--", *paths, env=env)
                if rc != 0:
                    return st.fail("staged", "git add failed; undone", "refused")
                st.staged = True
                if staged_list(repo, env) != expected_staged(self.repo_touched()):
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
            if self.cls == "a":
                why = after_checks(self, st, env)
                if why:
                    return st.fail("after-check", why + "; undone", "undone")
        except Exception as exc:  # fail closed: an error mid-apply undoes
            return st.fail("apply", f"an error mid-apply ({exc.__class__.__name__}: {exc}); undone", "refused")
        oc.remove_tree(journal_path(s))
        oc.remove_tree(s["freeze"])
        notice = None
        when = oc.now(s)
        if self.cls == "b" or oc.within_first_14_days(s, when):
            notice = "applied"
        self.line("apply", "applied", undo="ready", notice=notice, touched=self.manifest["touched"],
                  review_sha256=self.review_sha)
        if notice:
            green = "checks green" if self.checks is not None else "no checks"
            oc.notify(s, self.act, "info", "applied",
                      f"Applied {self.act} ({self.cls}) {when.strftime('%H:%M')}, {green}; to undo, say "
                      f"`undo {self.act} {self.sha[:8]}`", manifest_sha256=self.sha, commit=self.commit)
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
        self.g1()
        self.g2()
        self.g3()
        self.g4()
        self.g5()
        self.g6()
        self.recompute()
        self.g7()
        self.g8()
        held = self.g9()
        if held == "timeout":
            raise oc.Refused("G9", "the hold outlasted hold_max_s")
        self.recompute(log_pass=False)
        if held == "held":
            self.g7(log_pass=False)
        return self.apply()


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
    for rel in CONTROL_HOME_FILES:
        snap[("home", rel)] = read_bytes(os.path.join(s["home"], rel))
    snap[("crontab", "crontab")] = oc.crontab_bytes(env)
    inst = s["install"]
    for top, dirs, files in os.walk(inst):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            full = os.path.join(top, fn)
            snap[("install", os.path.relpath(full, inst).replace(os.sep, "/"))] = read_bytes(full)
    return snap


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
    allowed = {(t["root"], t["path"]): t["after"] for t in run.manifest["touched"]}
    for key in sorted(set(st.controls) | set(now_snap)):
        before, after = st.controls.get(key), now_snap.get(key)
        if before == after:
            continue
        if key in allowed and (None if after is None else oc.sha256_bytes(after)) == allowed[key]:
            continue
        return f"a control file changed ({key[0]}:{key[1]})"
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


def replay(run, st, lists, env):
    """The ids of calls allowed by the old map and the old deny lists that the new ones refuse."""
    s = run.s
    calls_path = s["calls"]
    if not os.path.isfile(calls_path):
        raise oc.Refused("after-check", "the guard's call log cannot be read for the replay")
    cutoff = oc.now(s) - oc.timedelta(hours=REPLAY_WINDOW_H)
    calls = []
    with open(calls_path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            if not ln.strip():
                continue
            try:
                c = json.loads(ln)
                assert isinstance(c, dict) and isinstance(c.get("event"), dict)
            except (ValueError, AssertionError):
                raise oc.Refused("after-check", "the guard's call log has a malformed line (fail closed)")
            t = oc.parse_iso(c.get("time"))
            if t is not None and t < cutoff:
                continue
            calls.append(c)
    if not calls:
        return []
    tmp = tempfile.mkdtemp(prefix="gov-operator-replay-")
    try:
        old_tree, new_tree = os.path.join(tmp, "old"), os.path.join(tmp, "new")
        for tree, side in ((old_tree, "before"), (new_tree, "after")):
            for key, data in st.controls.items():
                if key[0] == "repo" and (key[1].startswith(".claude/") or key[1] in REPLAY_FILES) and data is not None:
                    write_file(os.path.join(tree, key[1]), data)
            for t in lists:
                data = read_bytes(os.path.join(run.frozen, side, "repo", t["path"]))
                if data is None:
                    raise oc.Refused("after-check", f"the bundle does not hold {t['path']} {side} for the replay")
                write_file(os.path.join(tree, t["path"]), data)
        added = added_deny_rules(run, lists)
        turned = []
        for c in calls:
            old = guard_decision(s, old_tree, c)
            if old != "allow":
                continue
            new = guard_decision(s, new_tree, c)
            if new != "allow" or any(rule_matches(r, c, new_tree, s["home"]) for r in added):
                turned.append(str(c.get("id")))
        return turned
    finally:
        oc.remove_tree(tmp)


def write_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def guard_decision(s, tree, call):
    """The guard's decision on one call, run on a tree as Claude Code runs it: allow, or refuse (exit 2, a deny,
    or any error: fail closed)."""
    hook = os.path.join(tree, ".claude/hooks/pretooluse.py")
    if not os.path.isfile(hook):
        return "refuse"
    ev = dict(call["event"])
    tin = dict(ev.get("tool_input") or {})
    for k in ("file_path", "path", "notebook_path"):
        v = tin.get(k)
        if isinstance(v, str) and v and not v.startswith(("/", "~")):
            tin[k] = os.path.join(tree, v)
    ev["tool_input"] = tin
    cwd = ev.get("cwd") or "."
    ev["cwd"] = os.path.normpath(os.path.join(tree, cwd)) if not str(cwd).startswith("/") else cwd
    env = oc.clean_env(s, s["home"], extra={"CLAUDE_PROJECT_DIR": tree, "PYTHONPATH": os.path.join(s["repo"], "src")})
    env["CLAUDE_PROJECT_DIR"] = tree
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

    def fail(self, gate, reason, result, kind="undo"):
        run, s = self.run, self.run.s
        ok, why = undo_live(run, self)
        if not ok:
            hold_lock(s, run.act, run.sha, f"{reason}; the undo failed too: {why}")
            run.line(gate, "refused", undo="failed", reason=reason, notice="lock")
            oc.notify(s, run.act, "P1", "lock", f"{run.act}: {reason}; the UNDO FAILED ({why}): lock held, nothing "
                                                "else is applied", manifest_sha256=run.sha)
            return run.result("refused", gate, f"{reason}; the undo failed ({why}): lock held", undo="failed",
                              checks=run.checks), 1
        run.line(gate, result, undo="done", reason=reason, notice=kind)
        oc.notify(s, run.act, "P1", kind, f"{run.act}: {reason}", manifest_sha256=run.sha)
        return run.result(result, gate, reason, undo="done", checks=run.checks), 1


def hold_lock(s, act, sha, why):
    oc.write_atomic(lock_path(s), json.dumps({"act": act, "manifest_sha256": sha, "time": oc.iso(oc.now(s)),
                                              "why": why}) + "\n")


def undo_live(run, st):
    """apply.sh undo on the live tree; the touched files byte for byte as before; the controls and any unlisted tree
    file restored; the index or the commit put back. (ok, why)."""
    s = run.s
    env = run.live_env()
    repo = s["repo"]
    rc, _, err = run.apply_sh("undo", repo, env)
    if rc != 0:
        return False, f"apply.sh undo exited {rc}"
    for t in run.manifest["touched"]:
        if oc.live_hash(s, t["root"], t["path"], env) != t["before"]:
            return False, f"{t['root']}:{t['path']} is not restored byte for byte"
    touched = {(t["root"], t["path"]) for t in run.manifest["touched"]}
    try:
        restore_controls(s, st.controls, touched, env)
        restore_tree(repo, st, touched, env)
    except Exception as exc:  # fail closed
        return False, f"a control or tree file could not be restored ({exc})"
    paths = [t["path"] for t in run.repo_touched()]
    if paths and st.committed:
        rc, _, _ = oc.git(repo, "add", "-A", "--", *paths, env=env)
        if rc != 0 or staged_list(repo, env) != expected_staged(run.repo_touched(), reverse=True):
            return False, "the undo's staged list is not the touched list"
        rc, commit = run.git_commit(env, undo=True, extra_trailers=("Undo: yes",))
        if rc != 0:
            return False, "the undo's commit failed"
        run.undo_commit = commit
    elif paths:
        oc.git(repo, "reset", "-q", "--", *paths, env=env)
    oc.remove_tree(journal_path(s))
    oc.remove_tree(s["freeze"])
    return True, ""


def restore_controls(s, snap, touched, env):
    now_snap = control_snapshot(s, env)
    for key, data in snap.items():
        if key in touched or now_snap.get(key) == data:
            continue
        root, rel = key
        if root == "crontab":
            if data is None:
                oc.run(["crontab", "-r"], env=env, timeout=60)
            else:
                oc.run(["crontab", "-"], env=env, timeout=60, input_bytes=data)
            continue
        base = {"repo": s["repo"], "home": s["home"], "install": s["install"]}[root]
        full = os.path.join(base, rel)
        if data is None:
            if os.path.lexists(full):
                os.unlink(full)
        elif data.startswith(b"link:") and not os.path.isfile(full):
            pass
        else:
            mode = os.stat(full).st_mode & 0o7777 if os.path.exists(full) else 0o644
            os.makedirs(os.path.dirname(full), exist_ok=True)
            if os.path.islink(full):
                os.unlink(full)
            with open(full, "wb") as f:
                f.write(data)
            os.chmod(full, mode)
    for key in now_snap:
        if key not in snap and key not in touched and key[0] in ("repo", "home", "install"):
            base = {"repo": s["repo"], "home": s["home"], "install": s["install"]}[key[0]]
            full = os.path.join(base, key[1])
            if os.path.lexists(full):
                os.unlink(full)


def restore_tree(repo, st, touched, env):
    before, contents = st.tree_before
    after = tree_state(repo, ignored=False, keep=False)[0]
    for path in sorted(set(before) | set(after)):
        if ("repo", path) in touched or before.get(path, CLEAN) == after.get(path, CLEAN):
            continue
        full = os.path.join(repo, path)
        if path in before:
            if before[path] is None:
                if os.path.lexists(full):
                    os.unlink(full)
            elif path in contents:
                write_file(full, contents[path])
        elif st.head:
            rc, data, _ = oc.git(repo, "cat-file", "-p", f"{st.head}:{path}", env=env)
            if rc == 0:
                write_file(full, data)
            elif os.path.lexists(full):
                os.unlink(full)


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
    if any(e.get("act") == act and e.get("manifest_sha256") == sha and e.get("result") == "undone" for e in later):
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
    for t in run.manifest["touched"]:
        if oc.live_hash(s, t["root"], t["path"], env) != t["after"]:
            raise oc.Refused("undo", f"{t['root']}:{t['path']} moved since the apply")
    rc, head, _ = oc.git(s["repo"], "rev-parse", "HEAD")
    st = UndoState(run, head.decode().strip() if rc == 0 else None)
    st.controls = control_snapshot(s, env)
    st.tree_before = tree_state(s["repo"], ignored=False, keep=True)
    st.committed = run.commit
    oc.write_atomic(journal_path(s), json.dumps({
        "act": act, "manifest_sha256": sha, "frozen": frozen, "class": run.cls, "stage": "undoing",
        "head": st.head, "commit": run.commit, "time": oc.iso(now)}))
    oc.write_atomic(s["freeze"], f"{act} {sha} {oc.iso(now)} operator undo\n")
    run.undo_commit = None
    ok, why = undo_live(run, st)
    if not ok:
        hold_lock(s, act, sha, f"the owner's undo failed: {why}")
        run.line("undo", "refused", undo="failed", reason=why, notice="lock")
        oc.notify(s, act, "P1", "lock", f"{act}: the owner's UNDO FAILED ({why}): lock held", manifest_sha256=sha)
        return run.result("refused", "undo", f"the undo failed ({why}): lock held", undo="failed"), 1
    run.commit = getattr(run, "undo_commit", None) or run.commit
    run.line("undo", "undone", undo="done", notice="undo", typed=oc.iso(found[2]))
    oc.notify(s, act, "P1", "undo", f"Undone {act} on the owner's line ({oc.iso(found[2])})", manifest_sha256=sha)
    return run.result("undone", undo="done"), 0


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
        oc.remove_tree(s["freeze"])
        ok, why = True, ""
    else:
        run.undo_commit = None
        ok, why = undo_live(run, st)
    if not ok:
        hold_lock(s, act, sha, f"the journal's undo failed: {why}")
        run.line("journal", "refused", undo="failed", reason=why, notice="lock")
        oc.notify(s, act, "P1", "lock", f"{act}: an unfinished journal; its UNDO FAILED ({why}): lock held",
                  manifest_sha256=sha)
        return run.result("refused", "journal", f"the journal's undo failed ({why}): lock held", undo="failed"), 1
    run.line("journal", "undone", undo="done", notice="recovered")
    oc.notify(s, act, "P1", "recovered", f"{act}: a session died mid-apply; undone at the next launch",
              manifest_sha256=sha)
    return run.result("undone", "journal", "a session died mid-apply; undone at the next launch", undo="done"), 0


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
        oc.log_event(s, act, sha, "lock", "refused", reason="an undo failed earlier: the lock is held")
        oc.finish(dict(base, result="refused", gate="lock", act=act, manifest_sha256=sha,
                       reason="an undo failed earlier: the lock is held; nothing else is applied"), 1)
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
        extra = {}
        if r.gate == "G6":
            extra = {"disagreement": run.disagreement, "why": getattr(run, "code_why", None)}
            notice = "disagreement" if run.disagreement else None
        run.line(r.gate, "refused", reason=r.reason, notice=notice, **extra)
        if notice:
            oc.notify(s, act, "P1", "refused", f"{act}: refused at {r.gate}: {r.reason}", manifest_sha256=sha)
        res, code = run.result("refused", r.gate, r.reason), 1
    except Exception as exc:  # fail closed: a gate that errors refuses
        gate = "error"
        run.line(gate, "refused", reason=f"{exc.__class__.__name__}: {exc}")
        res, code = run.result("refused", gate, f"an error ({exc.__class__.__name__}: {exc}): refused"), 1
    oc.finish(res, code)


if __name__ == "__main__":
    main(sys.argv[1:])

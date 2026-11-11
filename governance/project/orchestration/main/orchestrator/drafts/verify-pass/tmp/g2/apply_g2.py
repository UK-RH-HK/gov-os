"""Group 2 of the Verify pass: insert `Verify: ...` into the KPI lines named, before their trailing [..] brackets."""
import re
import sys

import yaml

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/"

V = {}

V["DAEO-fau3"] = {
    "S1": "a unit test calls the guard's decision with the role argument missing: the write scope is empty and every write is refused",
    "S2": "a planted project that declares a held-out file which is absent: the guard denies on every call (fail closed) and `gov doctor` prints a finding naming the missing file",
    "S3": "a planted halt of a save between the temp file and the rename leaves the old whole file, never a part; a planted broken edit of the guard file: the next decision call still returns a decision and a session can write the repair, so no session is locked out",
    "S4": "a test in a launched session that creates a new `.gov-runtime/<name>` after launch: a write to that name is refused",
    "S5": "a planted Bash call that writes the main `.git/refs` (`git update-ref`, a redirect) is refused; the session's own `git commit` advances its ref",
    "S6": "a planted symbolic link and a planted hard link to a file under `tests/acceptance/`: a write through either is refused; a link to an allowed path is judged as its target",
    "S7": "a planted allowed file whose folder does not exist: the guard creates the folder and allows the write, and does not refuse",
    "S8": "planted commands `echo x > \"$NAME\"` with NAME set to a path outside the allowed paths and to one inside: judged as the literal path the shell writes, refused and allowed respectively",
}

V["DAEO-neam"] = {
    "S1": "a planted repository of 200 decisions and 20,000 commits: `gov check` runs the decision checker and its recorded time is within the gov check budget (the budget's value printed beside it)",
    "S2": "planted checks, one exiting 0 with a finding and one exiting 0 with \"unmeasured\" in its result: both are reported not green; a planted clean check exiting 0 is green",
    "S3": "a planted hard-block check whose tool is absent from the path: its result is red, never yellow",
    "S4": "a planted check map that covers a hard-block key only by a check of a lower tier is refused naming the key; the same key covered by a hard-block-tier check is accepted",
    "S5": "the limit's value is printed in the runner's result, and a planted check that runs past it is stopped and reported as timed out, by a unit test",
}

V["DAEO-nn1s"] = {
    "S1": "the exit run's record holds the full uncached regression and the dev-tier regression, each with its command, its date and exit code 0",
    "S2": "the record holds a planted specification change on a-dev, its CIT-P to CIT-E trace and the impact set it listed, set beside the expected impact set with no difference",
    "S3": "the record lists every Wave 2 close record with its exit code; a count of the close records on the integration branch equals the number of rows",
    "S4": "the record holds the governance share for each programme, EXAMIN's pilot included, each with the command that measured it",
    "S5": "the record holds the `gov doctor` run in EXAMIN with its output and exit code 0",
    "S6": "the record holds ten rows, AR-1 to AR-10 in order, each with an evidence path that exists on disk; each AR line whose ticket moved to Wave 3 is named as Wave 3, and EXP-003's row points to W2-15a",
    "F1": "a count of the AR rows in the record under ten, or an AR row with no evidence path, is the failure; neither is found in the record",
}

V["DAEO-jip3"] = {
    "S1": "a script lists every Wave 2 covers item, Contract v4.2 lite item, AR line and MR clause and compares it with the report's finding rows: no item is without a row",
    "S2": "the report's loop record shows each finding's repair round under DEC-096 and its end (closed or taken to the owner); no open finding is without a round",
    "S3": "the verdict record holds the auditor's session as fresh and read-only (its role record and the guard's log show no write but the report), Track A's pass or fail, each BLOCKER with the commit that fixed it, and each other finding with an owner entry",
}

V["DAEO-ecac"] = {
    "S1": "planted launches that end by exit 0, by a non-zero exit and by DEC-392's signal: each leaves one record keyed by its session id holding every listed key (a planted rate-limit event included), with role, ticket and task class taken from W2-60a's launch record",
    "S2": "a planted session log: each value in the record names its source; a value the log does not give is \"not measured\" with its reason and is never 0",
    "S3": "a planted log holding one unique sentence: a grep of the record for it finds 0 hits; the Claude Code version is present",
    "S4": "a planted log of a 1M-window session with three compactions: the record states the 1M window and 3 compactions",
    "S5": "a planted unwritable record path: the session's exit code is unchanged, stderr holds one line naming the record, and no part of a record is left on disk",
    "S6": "the CIT-E states the record's path and keys; a unit test writes a record and reads it back by ticket and session id through them",
    "S7": "a planted kernel role file for a sixth role launches with no code change; a planted missing or unreadable role file refuses the launch; the five roles launch as before (the existing launcher tests pass unchanged)",
    "S8": "a planted ticket naming a role with no role file: `gov launch` refuses and its message names the role",
    "S9": "a unit test: `qa-engineer` is in KNOWN_ROLES and in the reviewer set, and its planted write outside its findings report is refused; `git diff` shows only that set changed in `decide.py` and this repository's own hook unchanged",
    "S10": "a planted live writing session record in a worktree: a second writing launch is refused naming it; a planted reviewer or QA engineer session is not counted; `gov launch --tests-worktree` makes a worktree on its own branch at the ticket's head",
    "F1": "a search of `launcher.py` finds no fixed WORKER_ROLES or OWN_TICKET_ROLES tuple; the S7 planted sixth role launches with no code change",
    "F2": "planted logs with no cost value and with a log sentence: the record shows not measured (no 0 for it) and holds 0 hits of the sentence",
    "F3": "a planted record-write failure leaves the session's exit code as it was; after each planted launch (one ended early included) a record exists for its session id",
}

V["DAEO-4k3l"] = {
    "S1": "planted cases (an unreadable ticket file, an unreadable register, a missing store, a condition that cannot be judged): each gives NOT_READY with the code UNJUDGED and its reason; a planted ready ticket gives READY",
    "S2": "`git diff --stat` shows the vendored tk untouched and no guard or containment rule changed; the existing tests of `gov.tasks.queue` and `gov readiness` pass unchanged; the scoped set in the close's form is green; every red the ticket did not cause is named in its return",
    "S3": "planted ready and not-ready tickets: the light check answers READY and NOT_READY with the same codes as W2-128 S10's check; a grep of the module finds no readiness rule of its own, only the call to that check",
    "F1": "a planted ticket with a condition that cannot be judged is never answered READY",
    "F2": "`git diff` shows no change to the vendored tk, and no rule of this repository (a path, a decision id) in the judge or the kernel files",
}

V["DAEO-fu3n"] = {
    "S1": "pytest on the seven named cases on the head with W2-105 and W2-106 merged prints seven passed",
    "S2": "the cases W2-90b's return names as needing W2-105 or W2-110, run on the head with them merged, all pass; the README maps each to its return line",
    "S3": "a diff of the revised files shows no deleted test, no skip or xfail marker and no weaker assertion; each revised file's commit carries the Rewrite-Reason trailer; the README lists every case",
    "S4": "the README says the live sessions and the freeze launcher judge the pinned guard; a planted change in the worktree's `src/` changes the result of a non-live case and does not change a live one; a diff shows no case deleted, skipped, xfailed or weakened",
    "F1": "a grep of the revised cases for this repository's live settings path finds none, and the run with W2-105, W2-106 and W2-110 merged shows no red among them",
    "F2": "a diff of the revised files shows no deleted case, no skip, no xfail and no weaker verdict",
}

V["DAEO-6y0x"] = {
    "S1": "`validate_hidden.py` on a planted stand-in hidden folder prints, for each repository, a question count of 10 or more and exits 0; a planted folder with 9 for one repository is refused; each planted question holds the fields the README states",
    "S2": "`validate_hidden.py` on a planted stand-in set prints, for each kind of planted problem the visible builders do not produce, the number of hidden variants per repository; a planted set missing one kind is refused",
    "S3": "the commits of the hidden half carry the independent session's role; `git diff --stat` shows hidden files only under the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits",
    "S4": "`validate_hidden.py` on a built copy of a planted stand-in repository: every gold answer is found in it; a planted answer the built copy does not hold is refused naming its id",
    "S5": "planted stand-in cases: a must-not-cite file absent from the built copy refuses, a kind with no variant refuses, an unreadable file refuses (non-zero exit); `git diff` shows W2-81's files untouched; each commit of the hidden half has a recorded run",
    "F1": "a planted stand-in hidden file: a read, a grep and a `git log` from a measured session's sandbox (the guard's path map) are refused or find it 0 times",
    "F2": "`validate_hidden.py` on a planted stand-in question whose gold answer the built copy does not hold exits non-zero and names the question id",
}

V["DAEO-g87r"] = {
    "S1": "a planted stand-in set: a count outside 10 to 20 is refused; the record holds the seed and the draw; the visible and hidden folders each hold half (within one) with each category in both halves",
    "S2": "the record names the clone's path under `~/gov-os-runs/W2-94/examin/`; after the run `git status` in the workbench and in EXAMIN's real repository shows no change, and the owner's copy's file times are unchanged",
    "S3": "the guard's log shows no session of W2-26, W2-27, W2-88 or a retrieval ticket opened the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits",
    "S4": "a script run by the writer prints only counts and ids: for each question, its gold source exists at the copy's recorded commit and holds the answer (\"n of n hold\"); a planted source that is absent or does not hold its answer is reported by id",
    "S5": "a grep of W2-61's close record finds KPI 6 named as moved to W2-94; this ticket's visible and hidden folders hold the split of S1",
    "F1": "a planted stand-in hidden file: a read, a grep and a `git log` from a measured session's sandbox (the guard's path map) are refused or find it 0 times",
    "F2": "`git status` in the workbench, the owner's copy and EXAMIN's real repository shows no change after the run; a `find` for a clone of the copy outside `~/gov-os-runs/W2-94/` finds none",
    "F3": "the S4 script on a planted source that does not hold its answer reports that question's id as failing",
}

TRAIL = re.compile(r"(\s*(?:\[[^\]]*\]\s*)+)(\.?)$")


def requote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def process(tk: str, verifies: dict) -> list:
    path = ROOT + tk + ".md"
    lines = open(path, encoding="utf-8").read().split("\n")
    out, section, counters, done = [], None, {"S": 0, "F": 0}, []
    in_kpis = False
    for line in lines:
        if line == "kpis:":
            in_kpis = True
            out.append(line)
            continue
        if in_kpis and re.match(r"^\S", line):
            in_kpis = False
        if in_kpis:
            m = re.match(r"^  (success|failure|lifted):\s*(\[\])?$", line)
            if m:
                section = m.group(1)
                out.append(line)
                continue
            if section in ("success", "failure") and line.startswith("  - "):
                prefix = "S" if section == "success" else "F"
                counters[prefix] += 1
                label = f"{prefix}{counters[prefix]}"
                content = line[4:]
                if label in verifies:
                    if content.startswith("'"):
                        assert content.endswith("'"), (tk, label)
                        text = content[1:-1].replace("''", "'")
                    else:
                        assert not content.startswith('"'), (tk, label)
                        text = content
                    assert "Verify:" not in text, (tk, label, "has Verify")
                    m2 = TRAIL.search(text)
                    clause = "Verify: " + verifies[label]
                    if m2:
                        head, tail = text[: m2.start()], m2.group(1).strip() + m2.group(2)
                        text = head.rstrip() + " " + clause + " " + tail
                    else:
                        text = text.rstrip() + " " + clause
                    line = "  - " + requote(text)
                    done.append(label)
        out.append(line)
    new = "\n".join(out)
    open(path, "w", encoding="utf-8").write(new)
    return done


def kpi_count(tk: str) -> int:
    text = open(ROOT + tk + ".md", encoding="utf-8").read()
    front = yaml.safe_load(text.split("---")[1])
    k = front["kpis"]
    return len(k.get("success") or []) + len(k.get("failure") or [])


if __name__ == "__main__":
    for tk in V:
        before = kpi_count(tk)
        done = process(tk, V[tk])
        missing = set(V[tk]) - set(done)
        after = kpi_count(tk)
        print(tk, "edited", len(done), "missing", sorted(missing), "kpis", before, after)

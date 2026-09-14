#!/usr/bin/env python3
"""AR-0021 held-out attacks on admission as transactional state, against the pack's own revision-7 reference executor
`evidence/r7/gov_admit_reference_r7.py` (imported unmodified). Model evidence (the product does not exist).

Where the reference has one parameter for something the text leaves open (which account's verifier trust store a first admission
moves aside; where two machines' stores live), the probe WRAPS the reference's path functions (`account_store`) to name the
account or the machine explicitly; the reference's own `write_admission`, `is_first_admission`, `read_floors` and `gov_run` run
unchanged.

  X1  multi-account machine: account B's store was written before account A's first admission (or by B's own pre-admission code):
      which store does the first admission move aside, and what of B's store survives (`31` R-ADM-8″ "moves the account verifier
      trust store for the lineage aside"; AD-2′ bound)?
  X2  protected store lost, account store kept (OS reinstall with a restored home; a new machine with a migrated home): the next
      gov-admit is a FIRST admission and moves aside per-project records holding E10 sequences, strength vectors and pending
      `registration_change` / `policy_lowering` obligations (`19` §9 item 4 "cleared only by their gates") and open transactions.
  X3  two machines sharing one home (network home): machine M2's first admission moves aside the account store machine M1 is using.
  X4  clock high-water from an ordinary wrong clock: an anchoring event recorded while the clock was ahead; after correction the
      machine is C0-R until real time passes the recorded value or a root-signed clock_reset (`24` §4.5).
  X5  floors.json written by the reference with a non-atomic write while a governed run reads floors (TOCTOU / torn read).
Usage: adm7x.py <scratch-dir> <path-to-gov_admit_reference_r7.py-dir>   (JSON on stdout)
"""
import json, os, sys, threading, time
sys.dont_write_bytecode = True
S = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.abspath(sys.argv[2]))
import gov_admit_reference_r7 as GA  # noqa: E402

os.makedirs(S, exist_ok=True)
LIN = "sha256:" + "7" * 64
ADM = "sha256:" + "a" * 64
T = "x86_64-unknown-linux-musl"
B1 = b"#!/bin/sh\n# gov ar21 r1\n"
D1 = GA.sha256d(B1)
NOW = "2026-09-14T06:00:00Z"
FLOORS = {"state_sequence": 11, "state_digest": "sha256:" + "b" * 64, "root_version": 2, "policy_version": 2, "fca_sequence": 2, "negatives": [],
          "accepted_tbm": {"root": 0, "policy": 0, "state": 0}, "security_minimum": 9}
ORIG_ACCOUNT_STORE = GA.account_store
out = {}


def rec(d=D1, now=NOW):
    return GA.make_record(d, T, "R", LIN, "gov-fct:x", "gov-fcs:y", ADM, now, "workstation")


def listing(p):
    if not os.path.isdir(p):
        return None
    return sorted(os.path.relpath(os.path.join(dp, f), p) for dp, dn, fn in os.walk(p) for f in fn)


def plant(store, pending=False, open_tx=False):
    for sub in ("projects", "confirmations"):
        os.makedirs(os.path.join(store, sub), exist_ok=True)
    json.dump([{"sequence": 11, "digest": "sha256:" + "b" * 64, "method": "human", "anchored_at": "2026-09-13T06:00:00Z"}], open(os.path.join(store, "anchors.json"), "w"))
    prj = {"project_trust_id": "P1", "identity": [1, 2], "paths": ["/work/p1"], "highest_sequence": 11, "strength_vector": ["overlay:DATA_SENSITIVITY.restricted"],
           "failing": ["overlay:DATA_SENSITIVITY.restricted"], "pending": ["registration_change"] if pending else [], "open_tx": ["TX-" + "0e" * 16] if open_tx else []}
    json.dump(prj, open(os.path.join(store, "projects", "P1.json"), "w"))
    json.dump({"gate_kind": "framework_update", "bound_digests": ["sha256:" + "1" * 64]}, open(os.path.join(store, "confirmations", "c1.json"), "w"))
    json.dump({"clock_high_water": "2026-09-13T06:00:00Z", "state_sequence": 11}, open(os.path.join(store, "high-water.json"), "w"))


# X1 multi-account
root = os.path.join(S, "x1")
ACC = {"who": "alice"}
GA.account_store = lambda root_dir, lineage: os.path.join(root_dir, "home-" + ACC["who"], ".local/state/gov/trust", lineage.split(":", 1)[1])
bob_store = GA.account_store(root, LIN) if ACC.update(who="bob") is None else None
plant(bob_store)
ACC["who"] = "alice"
alice_store = GA.account_store(root, LIN)
plant(alice_store)
w = GA.write_admission(rec(), FLOORS, root, LIN)
out["X1_multi_account"] = {"first_admission": w["first_admission"], "moved_aside": w["account_store_moved_aside"] is not None,
                           "alice_store_after": listing(alice_store), "bob_store_after": listing(bob_store),
                           "bob_planted_anchor_confirmation_and_project_record_survive": listing(bob_store) == ["anchors.json", "confirmations/c1.json", "high-water.json", "projects/P1.json"],
                           "note": "the reference's write_admission takes one account store; `31` R-ADM-8″ and `24` §8 name no account (the invoking user, SUDO_USER, every account, the job account of a CI image)"}
GA.account_store = ORIG_ACCOUNT_STORE

# X2 protected store lost, account store kept
root = os.path.join(S, "x2")
acc = GA.account_store(root, LIN)
plant(acc, pending=True, open_tx=True)
before = listing(acc)
first = GA.is_first_admission(root, LIN)
w = GA.write_admission(rec(), FLOORS, root, LIN)
out["X2_protected_store_lost_account_store_restored"] = {
    "account_store_before": before, "is_first_admission": first, "moved_aside_to": os.path.basename(w["account_store_moved_aside"] or ""),
    "account_store_after": listing(acc), "per_project_record_with_pending_registration_change_and_open_tx_still_read": os.path.isfile(os.path.join(acc, "projects", "P1.json")),
    "floors_read_after": {k: (GA.read_floors(root, LIN) or {}).get(k) for k in ("state_sequence", "security_minimum", "negatives")},
    "consequence": "E10 sequence 11, the recorded strength vector with its failing requirement, the pending registration_change obligation and the open "
                   "transaction registration are never read again; the project is judged as on a machine without a record (LR-4, RR-2′); the "
                   "open transaction's journal becomes FOREIGN_TRANSACTION_ARTEFACT (`18` §5.1) and is never recovered from"}

# X3 two machines, one home
M1, M2 = os.path.join(S, "x3-m1"), os.path.join(S, "x3-m2")
shared = os.path.join(S, "x3-shared-home", ".local/state/gov/trust", LIN.split(":", 1)[1])
GA.account_store = lambda root_dir, lineage: shared
GA.write_admission(rec(), FLOORS, M1, LIN)            # M1 first admission (store empty at that time)
plant(shared, pending=True)                            # M1's admitted gov then records anchors, projects, confirmations
m1_view_before = listing(shared)
w2 = GA.write_admission(rec(), FLOORS, M2, LIN)        # M2 (own /var/lib/gov) first admission
m1_run = GA.gov_run(B1, "C1", M1, LIN, NOW, [], [ADM], anchor={"class": "workstation", "anchored_at": "2026-09-13T06:00:00Z", "names_effective_state": True})
out["X3_shared_home_two_machines"] = {"m2_first_admission": w2["first_admission"], "m2_moved_shared_store_aside": w2["account_store_moved_aside"] is not None,
                                      "m1_account_store_before": m1_view_before, "m1_account_store_after": listing(shared),
                                      "m1_gov_run_C1_with_the_anchor_it_had": m1_run["result"],
                                      "note": "the reference's gov_run takes the anchor as an argument; in `24` §3.2 a retained anchor is read from the account store, which M2 moved aside"}
GA.account_store = ORIG_ACCOUNT_STORE

# X4 clock high-water from an ordinary wrong clock (anchoring event recorded while the clock was ahead)
root = os.path.join(S, "x4")
GA.write_admission(rec(), FLOORS, root, LIN)
rows = {}
for label, anchored_at, now in (("correct_clock", "2026-09-14T05:00:00Z", NOW),
                                ("event_recorded_10h_ahead_then_clock_corrected", "2026-09-14T16:00:00Z", NOW),
                                ("same_after_real_time_passes_the_value", "2026-09-14T16:00:00Z", "2026-09-14T16:04:00Z"),
                                ("event_recorded_with_rtc_in_2099_then_corrected_one_year_later", "2099-01-01T00:00:00Z", "2027-09-14T06:00:00Z")):
    rows[label] = GA.gov_run(B1, "C2", root, LIN, now, [], [ADM], anchor={"class": "workstation", "anchored_at": anchored_at, "names_effective_state": True})["result"]
out["X4_clock_high_water_from_ordinary_clock_error"] = {"results": rows,
    "text": "`24` §4.5: the recorded high-water includes 'the time of the anchoring event and of the currency proof in use'; lowering it needs a root-signed "
            "Trust Policy bootstrap.clock_reset; no rule bounds an anchoring event's recorded time by the confirmed Trust State's issued_at"}

# X5 non-atomic floors write versus concurrent reads
root = os.path.join(S, "x5")
GA.write_admission(rec(), FLOORS, root, LIN)
stop, errs, reads, torn = [False], [], [0], [0]


def writer():
    i = 0
    while not stop[0]:
        i += 1
        GA.write_admission(GA.make_record(GA.sha256d(b"w%d" % i), T, "R", LIN, "c", "c", ADM, NOW, "workstation"), dict(FLOORS, state_sequence=11 + i % 3), root, LIN)


def reader():
    while not stop[0]:
        try:
            f = GA.read_floors(root, LIN)
            reads[0] += 1
            if f is None or f.get("state_sequence", 0) < 11:
                torn[0] += 1
        except Exception as e:  # noqa: BLE001
            errs.append(type(e).__name__)


th = [threading.Thread(target=writer)] + [threading.Thread(target=reader) for _ in range(3)]
[t.start() for t in th]
time.sleep(4)
stop[0] = True
[t.join() for t in th]
out["X5_floors_write_vs_read"] = {"reads": reads[0], "exceptions": len(errs), "exception_types": sorted(set(errs)), "reads_below_held_floor": torn[0],
                                  "note": "R-ADM-7″ makes the record write atomic; `24` §8 and `31` state no atomicity for floors.json or the account store's high-water.json"}
print(json.dumps({"probe": "adm7x (AR-0021) against gov_admit_reference_r7.py (unmodified; path functions wrapped where the text names no account or machine)", "results": out},
                 indent=1, sort_keys=True).replace(S, "<s>"))

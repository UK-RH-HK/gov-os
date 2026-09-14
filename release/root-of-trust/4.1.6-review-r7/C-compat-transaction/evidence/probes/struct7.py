#!/usr/bin/env python3
"""AR-0021 structural tampering and journal-honouring checks under the revision-7 predicate (`18` §3, §5.1, §9, §9.1; `26` §2).

Each case is a copy of R7 (or R7OPEN) with one change; `state_r7` under every reading records whether the change fails closed.
Cases carried from earlier reviews (re-asked with AR-0021's own predicate): occupation entry -> symlink / wrong type; symlink below
governance/trust; the .gitattributes member deleted or altered; kernel file edited / added / removed; foreign file in state/ and at
the trust top level; occupation removed; a hard link to a kernel file and to an occupation file (VU-12 is use-time; the layout
predicate records link counts).
New (revision 7): a planted journal at trust-tx/<TX>/journal.json not listed in the record; a journal listed in the record but
tracked by Git; the honoured open transaction with the record's identity changed (another clone), path changed (moved checkout),
project_trust_id changed; a completed done/<TX> archive not listed as done in the record; a layout-migration phase journal left
beside a COMPLETE tree after the record lost it; an honoured journal whose phase is `layout-occupation` on a tree that is otherwise
COMPLETE.
Usage: struct7.py <trees.raw.json>   (JSON on stdout)
"""
import json, os, shutil, sys, tempfile
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c7lib as L  # noqa

T = json.load(open(sys.argv[1]))
S = T["scratch"]
BASE = tempfile.mkdtemp(prefix="struct7-", dir=S)
rcs, R7, OPEN = T["rcs"], T["trees"]["R7"], T["trees"]["R7OPEN"]
TXO = T["tx"]["open"]
gh = os.path.join(BASE, "gh")
os.makedirs(gh)


def ident(p):
    c = L.git(p, "rev-parse", "--git-common-dir", home=gh, check=False).stdout.strip()
    c = c if os.path.isabs(c) else os.path.join(p, c)
    st = os.stat(os.path.realpath(c))
    return [st.st_dev, st.st_ino]


def case(name, src, mutate, record_fn=None):
    d = os.path.join(BASE, name)
    shutil.copytree(src, d, symlinks=True)
    rec = json.loads(json.dumps(T["records"]["R7OPEN" if src == OPEN else "R7"]))
    rec["identity"], rec["paths"] = ident(d), [os.path.realpath(d)]
    note = mutate(d) or ""
    if record_fn:
        rec = record_fn(rec, d)
    st = L.state_r7(d, rec, ident(d), rcs)
    return {"state": st["state"], "by_reading": st["by_reading"], "reasons": st["reasons"], "reports": st["reports"], "honoured": st["honoured"], "kernel_tampered": st.get("kernel_tampered"), "note": note}


def unlink_replace_symlink(d, p):
    os.unlink(os.path.join(d, p)); os.symlink("/etc/hostname", os.path.join(d, p))


def first_kernel_file(d):
    k = os.path.join(d, "governance/trust/kernel")
    for dp, dn, fn in sorted(os.walk(k)):
        for n in sorted(fn):
            return os.path.relpath(os.path.join(dp, n), d)


out = {}
out["occupation_file_to_symlink"] = case("occ_symlink", R7, lambda d: unlink_replace_symlink(d, "governance/kernel"))
out["occupation_dir_to_file"] = case("occ_dir_file", R7, lambda d: (os.unlink(os.path.join(d, "governance/framework.lock", L.OCC_DIR_SENTINEL)), os.rmdir(os.path.join(d, "governance/framework.lock")), open(os.path.join(d, "governance/framework.lock"), "w").write("{}")) and None)
out["symlink_below_trust"] = case("trust_symlink", R7, lambda d: os.symlink("../overlay", os.path.join(d, "governance/trust/state/x.dsse.json")))
out["gitattributes_member_deleted"] = case("ga_del", R7, lambda d: os.unlink(os.path.join(d, "governance/trust/.gitattributes")))
out["gitattributes_member_altered"] = case("ga_alt", R7, lambda d: open(os.path.join(d, "governance/trust/.gitattributes"), "w").write("* text\n"))
out["kernel_file_edited"] = case("k_edit", R7, lambda d: open(os.path.join(d, first_kernel_file(d)), "a").write("\n# edited\n"))
out["kernel_file_added"] = case("k_add", R7, lambda d: open(os.path.join(d, "governance/trust/kernel/EXTRA.md"), "w").write("x"))
out["kernel_file_removed"] = case("k_rm", R7, lambda d: os.unlink(os.path.join(d, first_kernel_file(d))))
out["foreign_file_in_state"] = case("state_foreign", R7, lambda d: open(os.path.join(d, "governance/trust/state/notes.txt"), "w").write("x"))
out["foreign_top_level_trust_entry"] = case("top_foreign", R7, lambda d: os.makedirs(os.path.join(d, "governance/trust/cache")))
out["occupation_removed"] = case("occ_rm", R7, lambda d: os.unlink(os.path.join(d, ".governance-runtime/migration")))


def hardlink_kernel(d):
    f = os.path.join(d, first_kernel_file(d))
    os.link(f, os.path.join(d, "product", "kernel-hardlink"))
    return "hard link count now %d" % os.lstat(f).st_nlink


def hardlink_occ(d):
    f = os.path.join(d, "governance/project")
    os.link(f, os.path.join(d, "product", "occ-hardlink"))
    return "occupation link count %d" % os.lstat(f).st_nlink


out["hard_link_to_kernel_file"] = case("hl_k", R7, hardlink_kernel)
out["hard_link_to_occupation_file"] = case("hl_occ", R7, hardlink_occ)


def plant_journal(d):
    t = os.path.join(d, ".governance-runtime/trust-tx", "TX-" + "99" * 16)
    os.makedirs(t)
    json.dump({"operation": "update", "phase": "swapped"}, open(os.path.join(t, "journal.json"), "w"))


out["planted_unregistered_journal"] = case("j_planted", R7, plant_journal)


def tracked_journal(d):
    L.git(d, "add", "-f", ".governance-runtime/trust-tx/%s/journal.json" % TXO, home=gh)


out["registered_journal_tracked_by_git"] = case("j_tracked", OPEN, tracked_journal)
out["open_tx_identity_changed"] = case("j_ident", OPEN, lambda d: None, lambda r, d: dict(r, identity=[0, 0]))
out["open_tx_path_changed"] = case("j_path", OPEN, lambda d: None, lambda r, d: dict(r, paths=["/elsewhere"]))
out["open_tx_record_ptid_differs_from_journal_ptid"] = case("j_ptid", OPEN, lambda d: None, lambda r, d: dict(r, tx_ptid={TXO: "other-ptid"}))
out["done_archive_not_registered_as_done"] = case("done_unreg", R7, lambda d: None, lambda r, d: dict(r, done_tx=[]))


def layout_phase_foreign(d):
    t = os.path.join(d, ".governance-runtime/trust-tx", "TX-" + "77" * 16)
    os.makedirs(t)
    json.dump({"operation": "update", "phase": "layout-occupation", "first_install_layout_migration": True}, open(os.path.join(t, "journal.json"), "w"))


out["layout_migration_journal_not_registered_on_COMPLETE_tree"] = case("lm_foreign", R7, layout_phase_foreign)


def layout_phase_honoured(d):
    json.dump({"operation": "update", "phase": "layout-occupation"}, open(os.path.join(d, ".governance-runtime/trust-tx", TXO, "journal.json"), "w"))


out["honoured_layout_phase_on_COMPLETE_tree"] = case("lm_honoured", OPEN, layout_phase_honoured)
verdict = {
    "every_structural_tamper_not_COMPLETE_any_reading": all(all(s != "COMPLETE" for s in out[k]["by_reading"].values()) for k in (
        "occupation_file_to_symlink", "occupation_dir_to_file", "symlink_below_trust", "gitattributes_member_deleted", "gitattributes_member_altered", "kernel_file_edited",
        "kernel_file_added", "kernel_file_removed", "foreign_file_in_state", "foreign_top_level_trust_entry", "occupation_removed")),
    "hard_links_fail_closed_at_layout_level": {k: out[k]["state"] for k in ("hard_link_to_kernel_file", "hard_link_to_occupation_file")},
    "planted_or_mismatched_journals_never_IN_TRANSACTION": all(out[k]["state"] != "IN_TRANSACTION" for k in ("planted_unregistered_journal", "registered_journal_tracked_by_git", "open_tx_identity_changed", "open_tx_path_changed", "open_tx_record_ptid_differs_from_journal_ptid")),
    "foreign_layout_migration_journal_leaves_COMPLETE (18 §9: state computed as if absent)": out["layout_migration_journal_not_registered_on_COMPLETE_tree"]["state"] == "COMPLETE",
}
print(L.scrub(json.dumps({"probe": "struct7 (AR-0021)", "cases": out, "verdicts": verdict}, indent=1, sort_keys=True)).replace(BASE, "<b>"))

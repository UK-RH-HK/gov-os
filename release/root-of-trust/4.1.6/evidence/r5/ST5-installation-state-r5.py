#!/usr/bin/env python3
"""ST5: RoT-1 revision-5 installation-state predicate and root discovery.

Encodes the normative predicates specified by AR-0011 for revision 5:
  - installation_state_r5(root)  — extends reviewer C's r4 encoding with 5 additional checks
  - rot1_root_discovery(start_dir) — walk-up ancestor discovery with PPS refusal

Imports reviewer C's c4lib (from the review-r4 evidence directory) for the r4 encoding,
entry kinds and child_env.

Origin: NEW (not copied from any reviewer script).
Usage:
  python3 ST5-installation-state-r5.py <trees.json>
  python3 ST5-installation-state-r5.py --check <root-dir>
"""
import hashlib, json, os, stat, sys

sys.dont_write_bytecode = True

# Import reviewer C's c4lib by path
C_EV = os.path.join(os.environ.get("AR7_WT", ""), "release/root-of-trust/4.1.6-review-r4/C-compat-transaction/evidence")
sys.path.insert(0, C_EV)
import c4lib as c4  # noqa: E402

# The closed set of allowed top-level entries in governance/trust/
TRUST_TOP_ALLOWED_R5 = {
    "FORMAT": "file",
    "framework.lock": "file",
    "kernel": "dir",
    "release.dsse.json": "file",
    "development.json": "file",
    "registration.dsse.json": "file",
    "lineage": "dir",
    "state": "dir",
    "root": "dir",
    "profiles": "dir",
}

# Statement directories that must contain only .dsse.json regular files, no subdirs
STATEMENT_DIRS = ("state", "root", "lineage", "profiles")

# Protected Path Set components (relative to project root)
PPS_PREFIXES = ("governance/trust/", "governance/trust")
OCCUPATION_DIR_PREFIX = "governance/framework.lock/"
OCCUPATION_DIR = "governance/framework.lock"
# Occupation files (not directories) that are part of the PPS
OCCUPATION_FILES = (
    "governance/kernel", "governance/project", "governance/generated",
    "spec/audits/GOVERNANCE-ADOPTION", ".governance-runtime/migration",
)


def _sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _lstat_kind(p):
    """Return (kind, is_symlink). kind is 'file', 'dir', 'link', 'special', 'absent'."""
    try:
        st = os.lstat(p)
    except FileNotFoundError:
        return "absent", False
    if stat.S_ISLNK(st.st_mode):
        return "link", True
    if stat.S_ISDIR(st.st_mode):
        return "dir", False
    if stat.S_ISREG(st.st_mode):
        return "file", False
    return "special", False


def _recursive_paths(base):
    """Return dict of {relpath: ('file'|'dir'|'link'|'special', digest_or_None)} under base, lstat, no follow."""
    result = {}
    if not os.path.isdir(base):
        return result
    for dp, dns, fns in os.walk(base, followlinks=False):
        dns.sort()
        for name in sorted(dns + fns):
            p = os.path.join(dp, name)
            rel = os.path.relpath(p, base)
            kind, is_sym = _lstat_kind(p)
            if kind == "file":
                result[rel] = ("file", _sha256_file(p))
            elif kind == "dir":
                result[rel] = ("dir", None)
            else:
                result[rel] = (kind, None)
    return result


def _pristine_kernel_content_set(root):
    """Build the reference content set from the pristine kernel as built by build_trees.py.
    The framework.lock does not record a per-file map, so we use the tree itself."""
    kernel_dir = os.path.join(root, "governance", "trust", "kernel")
    return _recursive_paths(kernel_dir)


def installation_state_r5(root, pristine_kernel_ref=None):
    """Revision-5 installation-state predicate.

    Starts from reviewer C's r4 encoding, then applies 5 additional checks
    that can demote COMPLETE to PARTIAL.

    Args:
        root: project root directory
        pristine_kernel_ref: optional dict of {relpath: (kind, digest)} for the reference kernel.
                            If None, uses the tree's own kernel (pristine self-check).

    Returns dict with: state, reasons[], nested_legacy_projects[], state_r4, content_set_source,
                       plus diagnostic details.
    """
    # Get the r4 state first
    r4 = c4.installation_state(root)
    r4_state = r4["state"]

    reasons = []
    nested_legacy_projects = []
    details = {}

    # If r4 is not COMPLETE, r5 cannot be COMPLETE either (r5 is strictly stricter)
    if r4_state != "COMPLETE":
        return {
            "state": r4_state,
            "reasons": [f"r4_state_{r4_state}"],
            "nested_legacy_projects": [],
            "state_r4": r4_state,
            "content_set_source": None,
            "details": {"r4_result": r4},
        }

    trust_dir = os.path.join(root, "governance", "trust")

    # CHECK 1: Closed top-level set
    if os.path.isdir(trust_dir):
        actual_entries = {}
        for name in os.listdir(trust_dir):
            kind, is_sym = _lstat_kind(os.path.join(trust_dir, name))
            actual_entries[name] = kind
        for name, kind in actual_entries.items():
            if name not in TRUST_TOP_ALLOWED_R5:
                reasons.append("foreign_trust_entry")
                details.setdefault("foreign_trust_entries", []).append({"name": name, "kind": kind})
            elif kind != TRUST_TOP_ALLOWED_R5[name]:
                reasons.append("foreign_trust_entry")
                details.setdefault("trust_entry_wrong_type", []).append(
                    {"name": name, "expected": TRUST_TOP_ALLOWED_R5[name], "observed": kind}
                )
            elif is_sym:
                reasons.append("foreign_trust_entry")
                details.setdefault("trust_entry_is_symlink", []).append(name)

    # CHECK 2: Kernel content set
    content_set_source = None
    # Check if framework.lock records a file map
    lock_path = os.path.join(trust_dir, "framework.lock")
    lock_has_file_map = False
    if os.path.isfile(lock_path):
        try:
            lock_data = json.load(open(lock_path))
            if isinstance(lock_data, dict) and "kernel_file_map" in lock_data:
                lock_has_file_map = True
        except Exception:
            pass

    if lock_has_file_map:
        content_set_source = "framework_lock_file_map"
        # Would use lock_data["kernel_file_map"] here
        ref = lock_data["kernel_file_map"]
    elif pristine_kernel_ref is not None:
        content_set_source = "pristine_tree_reference"
        ref = pristine_kernel_ref
    else:
        content_set_source = "pristine_tree_self_check"
        ref = None  # self-check: the tree is the reference

    kernel_dir = os.path.join(root, "governance", "trust", "kernel")
    if os.path.isdir(kernel_dir):
        current_kernel = _recursive_paths(kernel_dir)
        if ref is not None:
            # Compare current to reference
            added = sorted(set(current_kernel) - set(ref))
            removed = sorted(set(ref) - set(current_kernel))
            changed_digest = []
            for p in sorted(set(current_kernel) & set(ref)):
                cur_kind, cur_dig = current_kernel[p]
                ref_kind, ref_dig = ref[p]
                if cur_kind != ref_kind or (cur_dig is not None and ref_dig is not None and cur_dig != ref_dig):
                    changed_digest.append(p)
            if added or removed or changed_digest:
                reasons.append("kernel_content_mismatch")
                details["kernel_content_mismatch"] = {
                    "added": added[:20], "removed": removed[:20], "changed": changed_digest[:20],
                    "added_count": len(added), "removed_count": len(removed), "changed_count": len(changed_digest),
                }
        # else: self-check, reference IS the current tree, always matches

    # CHECK 3: Statement directories contain only .dsse.json regular files, no subdirs
    for sd_name in STATEMENT_DIRS:
        sd_path = os.path.join(trust_dir, sd_name)
        if not os.path.isdir(sd_path):
            continue
        for item in os.listdir(sd_path):
            item_path = os.path.join(sd_path, item)
            kind, is_sym = _lstat_kind(item_path)
            if is_sym:
                reasons.append("foreign_trust_entry")
                details.setdefault("statement_dir_symlinks", []).append(f"{sd_name}/{item}")
            elif kind == "dir":
                reasons.append("foreign_trust_entry")
                details.setdefault("statement_dir_subdirs", []).append(f"{sd_name}/{item}")
            elif kind == "file" and not item.endswith(".dsse.json"):
                reasons.append("foreign_trust_entry")
                details.setdefault("statement_dir_non_dsse", []).append(f"{sd_name}/{item}")

    # CHECK 4: Occupation directory governance/framework.lock/ contains exactly ROT-1-TRUST-FORMAT
    occ_dir = os.path.join(root, "governance", "framework.lock")
    if os.path.isdir(occ_dir):
        entries = os.listdir(occ_dir)
        if sorted(entries) != ["ROT-1-TRUST-FORMAT"]:
            reasons.append("foreign_occupation_entry")
            details["occupation_dir_entries"] = sorted(entries)
        else:
            # Verify it's a regular file
            rot1_path = os.path.join(occ_dir, "ROT-1-TRUST-FORMAT")
            kind, is_sym = _lstat_kind(rot1_path)
            if kind != "file" or is_sym:
                reasons.append("foreign_occupation_entry")
                details["occupation_dir_rot1_kind"] = kind
                details["occupation_dir_rot1_is_symlink"] = is_sym

    # CHECK 5: Nested legacy markers
    nested_inside_governance = []
    nested_outside = []
    for dp, dns, fns in os.walk(root, followlinks=False):
        rel = os.path.relpath(dp, root)
        if rel.split(os.sep, 1)[0] == ".git":
            dns[:] = []
            continue
        if rel == ".":
            continue
        if os.path.basename(dp) == "governance":
            parent_rel = os.path.relpath(os.path.dirname(dp), root)
            if parent_rel == ".":
                continue  # this is the project's own governance/
            # Check for legacy markers
            has_lock = "framework.lock" in fns or ("framework.lock" in dns and os.path.isfile(os.path.join(dp, "framework.lock")))
            has_manifest = os.path.isfile(os.path.join(dp, "kernel", "KERNEL_MANIFEST.json")) if "kernel" in dns else False
            if has_lock or has_manifest:
                marker_rel = os.path.relpath(dp, root)
                gov_prefix = "governance/"
                if marker_rel.startswith(gov_prefix) or marker_rel == "governance":
                    nested_inside_governance.append(marker_rel)
                    reasons.append("nested_legacy_install")
                else:
                    nested_outside.append(marker_rel)

    # Deduplicate reasons
    reasons_deduped = sorted(set(reasons))

    state = "PARTIAL" if reasons_deduped else "COMPLETE"
    nested_legacy_projects = nested_outside  # diagnostic only, does not change state

    return {
        "state": state,
        "reasons": reasons_deduped,
        "nested_legacy_projects": nested_legacy_projects,
        "nested_inside_governance": nested_inside_governance,
        "state_r4": r4_state,
        "content_set_source": content_set_source,
        "details": details,
    }


def rot1_root_discovery(start_dir):
    """Revision-5 RoT-1 root discovery from a working directory.

    Walk up ancestors; the nearest ancestor A such that A/governance/trust/FORMAT
    is a regular file is the project root. If the resolved working directory is
    inside the Protected Path Set, refuse.

    Returns dict with: project_root (relative to start_dir), refuse, code, nested_markers_on_path[].
    """
    start = os.path.realpath(start_dir)
    project_root = None

    # Walk up ancestors
    cur = start
    while True:
        fmt_path = os.path.join(cur, "governance", "trust", "FORMAT")
        kind, is_sym = _lstat_kind(fmt_path)
        if kind == "file" and not is_sym:
            project_root = cur
            break
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent

    if project_root is None:
        return {
            "project_root": None,
            "refuse": False,
            "code": "NO_PROJECT_FOUND",
            "nested_markers_on_path": [],
        }

    # Determine if start_dir is inside the PPS
    try:
        rel = os.path.relpath(start, project_root)
    except ValueError:
        rel = None

    refuse = False
    refuse_code = None

    if rel and rel != ".":
        # Check if inside governance/trust or governance/trust/**
        if rel == "governance/trust" or rel.startswith("governance/trust/"):
            refuse = True
            refuse_code = "WORKING_DIRECTORY_IN_PROTECTED_PATH"
        # Check if inside governance/framework.lock or governance/framework.lock/**
        elif rel == "governance/framework.lock" or rel.startswith("governance/framework.lock/"):
            refuse = True
            refuse_code = "WORKING_DIRECTORY_IN_PROTECTED_PATH"
        # Check occupation files (these are files, not directories; unlikely to be a cwd)
        elif rel in OCCUPATION_FILES:
            refuse = True
            refuse_code = "WORKING_DIRECTORY_IN_PROTECTED_PATH"

    # Find nested legacy markers on the path between start_dir and project_root
    nested_markers = []
    if rel and rel != ".":
        parts = rel.split(os.sep)
        for i in range(1, len(parts) + 1):
            subpath = os.path.join(project_root, *parts[:i])
            gov_path = os.path.join(subpath, "governance")
            if os.path.isdir(gov_path) and subpath != project_root:
                lock_path = os.path.join(gov_path, "framework.lock")
                manifest_path = os.path.join(gov_path, "kernel", "KERNEL_MANIFEST.json")
                if os.path.isfile(lock_path) or os.path.isfile(manifest_path):
                    nested_markers.append(os.path.relpath(gov_path, project_root))

    return {
        "project_root": os.path.relpath(project_root, start_dir) if project_root else None,
        "refuse": refuse,
        "code": refuse_code or "OK",
        "nested_markers_on_path": nested_markers,
    }


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--check":
        root = os.path.abspath(sys.argv[2])
        r = installation_state_r5(root)
        print(json.dumps(r, indent=1, sort_keys=True))
        return

    trees_json = sys.argv[1]
    T = json.load(open(trees_json))
    S = T["scratch"]
    results = {}

    # Build reference kernel from pristine R4
    r4_pristine_kernel = _pristine_kernel_content_set(T["trees"]["R4"])

    for label in ("R4", "R4RES", "R4APP", "L0"):
        tree = T["trees"][label]
        if label == "L0":
            ref = None  # L0 has no governance/trust/kernel
        else:
            ref = r4_pristine_kernel
        r5 = installation_state_r5(tree, pristine_kernel_ref=ref)
        disc = rot1_root_discovery(tree)
        results[label] = {
            "installation_state_r5": r5,
            "rot1_root_discovery": disc,
        }

    text = json.dumps(results, indent=1, sort_keys=True, default=str)
    text = text.replace(S, "<scratch>")
    print(text)


if __name__ == "__main__":
    main()

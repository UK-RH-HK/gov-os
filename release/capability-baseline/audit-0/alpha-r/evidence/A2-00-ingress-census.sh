#!/usr/bin/env bash
# A2 bullet 3 / AC-16 (S3/S4/S5 <-> A2): static census of the privileged-ingress call sites, to pair with the
# behavioural evidence in A2-02 (every ingress refuses the same attack classes). Static text is orientation, not
# evidence of behaviour; it is used only to show that no install path exists outside the verified sites.
cd "$(dirname "$0")/../../../../.." || exit 1
echo "## commit"; git rev-parse HEAD
echo "## calls of the single verifier srr::admit (excluding its definition and tests)"
grep -rn "srr::admit(" runtime/src cli/src | grep -v "^runtime/src/srr/verifier.rs"
echo "## calls of install_kernel (the only function that writes governance/kernel)"
grep -rn "install_kernel(" runtime/src cli/src | grep -v "pub fn install_kernel"
echo "## install_kernel signature (takes the sealed AuthenticatedRelease)"
grep -n "pub fn install_kernel" runtime/src/kernel.rs
echo "## Ingress variants and where each is constructed"
grep -n "enum Ingress" -A12 runtime/src/srr/verifier.rs | head -14
grep -rn "Ingress::[A-Z][a-z]*" runtime/src cli/src | grep -v "^runtime/src/srr/verifier.rs" | sed 's/^\([^:]*:[0-9]*\):.*\(Ingress::[A-Za-z]*\).*/\1 \2/'
echo "## gov recover installs no kernel bytes (no install/admit call in recovery.rs)"
grep -n "install_kernel\|admit(" runtime/src/recovery.rs || echo "(none)"
echo "## other writers into governance/kernel outside kernel.rs/srr (should be none)"
grep -rn "kernel_dir()" runtime/src cli/src | grep -E "write|create_dir|remove|rename|copy" | grep -v "^runtime/src/kernel.rs\|^runtime/src/srr/" || echo "(none)"

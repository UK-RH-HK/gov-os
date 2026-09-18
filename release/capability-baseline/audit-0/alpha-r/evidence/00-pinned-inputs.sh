#!/usr/bin/env bash
# Verifies every pinned input named by P2-HO-0000 / P2-HO-0009 before any evidence relies on it.
cd "$(dirname "$0")/../../../../.." || exit 1
echo "## git"; git rev-parse HEAD; git log --oneline -3; git status --porcelain | head
echo "## product identity (HEAD, candidate tag, srr1-r1-accepted)"
python3 release/orchestration/phase-2/tools/product_identity.py HEAD
python3 release/orchestration/phase-2/tools/product_identity.py cap2-candidate-0
python3 release/orchestration/phase-2/tools/product_identity.py srr1-r1-accepted
echo "## tags"; echo "cap2-candidate-0 -> $(git rev-parse cap2-candidate-0^{commit})"; echo "srr1-r1-accepted -> $(git rev-parse srr1-r1-accepted^{commit})"
echo "## product diff HEAD vs candidate (expect only release/orchestration)"; git diff --stat cap2-candidate-0 HEAD | tail -3
echo "## hashes"
sha256sum Governance_OS_Capability_Acceptance_Contract_v3.md framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md \
  release/orchestration/phase-2/GATES/PHASE-2-FROZEN-GATE-CONTRACT.md \
  release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md \
  release/orchestration/phase-2/HANDOFFS/P2-HO-0000-audit-0-common-protocol.md \
  release/orchestration/phase-2/HANDOFFS/P2-HO-0001-audit-0-alpha.md \
  release/orchestration/phase-2/HANDOFFS/P2-HO-0009-audit-0-reaudit-common.md
echo "## ORCHESTRATOR_STATE frozen_gate_contract.sha256"; grep -A2 '^frozen_gate_contract:' release/orchestration/phase-2/ORCHESTRATOR_STATE.yaml
echo "## toolchain"; ~/.cargo/bin/cargo --version; ~/.cargo/bin/rustc --version; python3 --version; uname -sr

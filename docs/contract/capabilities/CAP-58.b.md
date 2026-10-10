---
id: CAP-58.b
type: capability
status: PROPOSED
state_class: DERIVED
title: 'Permission classes of Framework §32 as role permissions: WRITE_REPO_SCOPED = allowed_paths guard; PACKAGE_INSTALL/SYSTEM_INSTALL per DEC-083; SECRET_READ denied (DEC-074 Q9); READ_REPO, RUN_TESTS allowed; NETWORK_*, DB_*, CLOUD_*, CI_TRIGGER, DEPLOY_* denied unless the role definition grants them; a launched worker session''s network grant comes from the launcher''s network profile (`CAP-61.c`), which the role definition names'
depends_on:
- CAP-58
---

# CAP-58.b: Permission classes of Framework §32 as role permissions: WRITE_REPO_SCOPED = allowed_paths guard; PACKAGE_INSTALL/SYSTEM_INSTALL per DEC-083; SECRET_READ denied (DEC-074 Q9); READ_REPO, RUN_TESTS allowed; NETWORK_*, DB_*, CLOUD_*, CI_TRIGGER, DEPLOY_* denied unless the role definition grants them; a launched worker session's network grant comes from the launcher's network profile (`CAP-61.c`), which the role definition names

A covers item of CAP-58 (Path guards as default-deny allow-lists). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** Permission classes of Framework §32 as role permissions: WRITE_REPO_SCOPED = allowed_paths guard; PACKAGE_INSTALL/SYSTEM_INSTALL per DEC-083; SECRET_READ denied (DEC-074 Q9); READ_REPO, RUN_TESTS allowed; NETWORK_*, DB_*, CLOUD_*, CI_TRIGGER, DEPLOY_* denied unless the role definition grants them; a launched worker session's network grant comes from the launcher's network profile (`CAP-61.c`), which the role definition names
- **Wave:** W1

# Installers

Installer descriptors are executed by `gov tools install` only when every `auto_install_conditions` entry in
`TOOL_POLICY.yaml` holds; otherwise a Human Decision Gate is raised. Descriptors are declarative:

```yaml
tool_id: TOOL-XYZ-001
package: name
source: package-manager | vendored | system
version_pin: 1.2.3
license: MIT
install_command: [python3, -m, pip, install, "name==1.2.3"]
uninstall_command: [python3, -m, pip, uninstall, -y, name]
reversible: true
cost_usd: 0
```

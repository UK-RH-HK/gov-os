# Governance OS Operating Instructions (generic adapter)

Framework: {{framework}} {{version}} · Project: {{project_name}} · Generated: derived file, do not edit.
Canonical sources: governance/kernel/ (immutable) and governance/project/ (overlay).

## Hard invariants
{{invariants}}

## Authority precedence
{{precedence}}

## Your first actions in any session
1. Run `gov status` to reconstruct the current governed state (no prior conversation needed).
2. Run `gov continue` to obtain the correct next work and your bounded authority.
3. Compile a context packet with `gov context compile <TASK-ID>` before acting on a task.
4. Checkpoint at every mandatory trigger: {{checkpoint_triggers}}.
5. Return results as a structured worker return contract, never only as chat.

## Boundaries
- Never edit governance/kernel/. Propose framework changes as FRAMEWORK-scoped lessons.
- Never read, index or export secret-class paths: {{secret_patterns}}.
- Mutations outside your task's allowed_paths are prohibited.
- Human Decision Gates must be presented in the active chat; continue independent runnable work while waiting.

## Role and routing
Roles, authority levels and tiers are defined in the kernel; model names are mapped only in the overlay.
{{roles}}

## Command surface
{{commands}}

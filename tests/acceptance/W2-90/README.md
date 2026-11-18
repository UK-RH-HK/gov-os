# W2-90 (DAEO-8lmb): the kernel's wiring helper

**Retired with the guard and the sandbox (EMERGENCY-2 6.1, DAEO-gr7t).** This folder held the helper that generated a
project from the template (`copier copy`, then `rulesync generate`) so that 235 live-wiring cases could judge the
kernel's guard and containment lines. Those cases are deleted with the guard, and so are the helper's functions that
built the guard's fixture projects (`w1_05_project`, `w1_28_project`, `w1_46_project`, `w2_59_worker_project`, the
settings readers and the pinned-line import check). What stays in `w2_90_kernel_wiring.py` is the generator itself
(`generate_project`, `copy_project`, `template_hook_entries`, `w2_59_hook_project`) that W2-59's pin cases for the
lifecycle hook lines and W2-113's Stage A0 cases (through `w2_110_support.py`) still use. The folder holds no test.

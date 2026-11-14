# WITHDRAWN 2026-11-13 by the owner (DEC-1167 (7), SANDBOX-1 (b) B2)
The sandbox cache ACT (allowWrite ~/.cache/gov-os, approved under DEC-1163 (9)) is withdrawn: probe B showed it changes only the error text (EROFS -> EPERM on socket()), not ranking. Replaced by the reranker's log fix (w2/W2-145-cause) so the log names the true cause. Do not queue or apply anything from this folder.

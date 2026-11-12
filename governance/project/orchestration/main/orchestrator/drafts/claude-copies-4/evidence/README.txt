Window measurement logs (ACT-CLAUDE-COPIES-4). Each file is one pytest run per folder, one folder per line.
window-base0.log, window-base02.log : plain integrate (792b92923911), no ACT, no W2-175
window-win.log,   window-win2.log   : integrate with the ACT applied, W2-175 not merged (the window)
window-mrg0.log                     : integrate with W2-175 merged, no ACT (the other order's window)
window-fin.log,   window-fin2.log   : integrate with W2-175 merged and the ACT applied (the end state)
The first set of folders is in the *.log without a 2, the other 21 folders in the 2 files. window-mrg0 has the first set only.

P='import signal; print("in-slot SIGINT ignored:", int(signal.getsignal(signal.SIGINT) == signal.SIG_IGN))'
H=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
echo "fg: $(bash $H python3 -c "$P" 2>/dev/null)"
echo "bg: $(bash $H python3 -c "$P" 2>/dev/null & wait)"

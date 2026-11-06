#!/usr/bin/env bash
# W2-32 round 2 (9446d322): the clone with the pool on (w4_point.sh, setup only), then the product's own path on the
# 80 and the 60 against the harness's v456 on the control (w4_32_product.sh). One GPU job; counts only.
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b
bash $D/w4_point.sh w4-32b 1aeae78874d1 1 && bash $D/w4_32_product.sh w4-32b w4-32b-product

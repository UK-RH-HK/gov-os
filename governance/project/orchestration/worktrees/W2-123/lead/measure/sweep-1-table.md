| parallel | cap | runner -np | determinism (256, n in flight) | alone c/s | alone stage s | alone cores | alone GPU % | three total c/s | three per-rebuild c/s | three stage s | three cores | three GPU % | load |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | capped (12-19, nice 10) | 1 | accepted (0 differ) | 32.0 | 1585.6 | 3.61 | 62.0 | 25.8 | 9.0/8.6/8.8 | 5900.0 | 2.63 | 37.8 | 48.5 |
| 1 | uncapped (0-19, nice 0) | 1 | accepted (0 differ) | 31.3 | 1621.1 | 4.4 | 57.2 | 37.4 | 12.5/12.6/12.7 | 4059.2 | 4.49 | 52.3 | 38.0 |
| 2 | capped (12-19, nice 10) | 1 | accepted (0 differ) | 25.0 | 2029.6 | 3.05 | 52.9 | 21.3 | 7.5/7.2/7.1 | 7146.5 | 2.2 | 35.2 | 40.5 |
| 2 | uncapped (0-19, nice 0) | 1 | refused (1 differ) | 30.2 | 1680.1 | 4.15 | 51.7 | 34.3 | 11.5/11.4/11.7 | 4450.9 | 3.92 | 46.4 | 38.3 |
| 4 | capped (12-19, nice 10) | 1 | accepted (0 differ) | 16.9 | 3002.4 | 2.1 | 38.1 | 22.2 | 7.5/7.4/7.4 | 6856.8 | 2.3 | 38.1 | 34.7 |
| 4 | uncapped (0-19, nice 0) | 1 | refused (1 differ) | 33.7 | 1505.6 | 4.74 | 60.3 | 40.5 | 13.8/13.6/13.5 | 3758.5 | 4.93 | 57.3 | 28.7 |
| 8 | capped (12-19, nice 10) | 1 | refused (4 differ) | 24.2 | 2096.7 | 2.95 | 49.8 | 29.0 | 9.9/9.7/9.8 | 5230.9 | 3.01 | 47.1 | 32.7 |
| 8 | uncapped (0-19, nice 0) | 1 | accepted (0 differ) | 23.3 | 2177.7 | 2.99 | 38.5 | 29.5 | 9.8/9.9/10.0 | 5177.6 | 3.21 | 36.8 | 42.8 |

# 1) Make sure you're in the project root
# # cd C:\Users\Max\Desktop\TLG\Games\gamedev_challenges\day15

# # # 2) Remove any local file that could shadow the package
# # del -ea Ignore .\kcp.py
# # Remove-Item -Recurse -Force -ea Ignore .\kcp

# # # 3) Start fresh
# # python -m venv venv
# # .\venv\Scripts\Activate.ps1       # <-- correct way in PowerShell

# # 4) Confirm you're INSIDE the venv
# python -c "import sys, pathlib, site, os; print(sys.prefix)"

# # 5) Install only what we need
# pip install 'kcp==0.1.6' pygame-ce

# 6) Double-check which module will be imported
python - <<'PY'
import kcp, inspect, pathlib
print("kcp version:", kcp.__version__)
print("kcp path   :", pathlib.Path(kcp.__file__).resolve())
from kcp import KCPClientSync, server
print("client sig :", inspect.signature(KCPClientSync))
print("server sig :", inspect.signature(server.KCPServerAsync))
PY

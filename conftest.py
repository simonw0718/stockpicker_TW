# stockpicker_TW/conftest.py
import sys
import pathlib

# 把專案根 (stockpicker_TW) 加到 sys.path，確保能找到 backend/*
ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
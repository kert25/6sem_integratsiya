# -*- coding: utf-8 -*-
"""Запуск pytest для папки ЛРN: py run_pytest.py <N> [-- <аргументы pytest>].
Кириллический путь собирается внутри скрипта, командная строка остаётся ASCII."""
import sys, os
import pytest

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lab = os.path.join(root, "\u041b\u0420" + sys.argv[1])
args = sys.argv[3:] if len(sys.argv) > 2 and sys.argv[2] == "--" else []
os.chdir(lab)
sys.exit(pytest.main(["-v", "--tb=line"] + args))

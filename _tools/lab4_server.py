# -*- coding: utf-8 -*-
"""Запуск лабораторного сервера из ЛР2 (flask) для нужд ЛР4.
Кириллические сегменты пути зашиты \\u-эскейпами, командная строка остаётся ASCII.
Запуск: py _tools\\lab4_server.py  (из корня проекта)."""
import os
import runpy

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
server = os.path.join(
    root,
    "\u041c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u044b",  # Материалы
    "Lab 2",
    "lab2_api_server.py",
)
if not os.path.isfile(server):
    raise SystemExit("Server not found: " + server)
runpy.run_path(server, run_name="__main__")

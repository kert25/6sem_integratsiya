# -*- coding: utf-8 -*-
"""Раннер сборки отчёта: py build_report.py <корень_проекта> <номер_ЛР>.
Тема берётся из THEMES (файл UTF-8), поэтому командная строка остаётся ASCII."""
import os, sys, json

THEMES = {
    1: "Работа с требованиями и создание тестовой документации",
    2: "Тестирование API как основа интеграции (часть 1)",
    3: "Применение техник тест-дизайна",
    4: "Тестирование API (часть 2 — автоматизация)",
    5: "Автоматизация UI-тестирования",
    6: "Автоматизация тестирования мобильных приложений",
    7: "Интеграционное тестирование веб-приложения в Docker-окружении",
    8: "Сквозной проект",
}

root = sys.argv[1]
num = int(sys.argv[2])
sys.path.insert(0, os.path.join(root, "_tools"))
import make_docx

lab = os.path.join(root, "\u041b\u0420" + str(num))
content = os.path.join(lab, "content.json")
out = os.path.join(lab, "\u041e\u0442\u0447\u0435\u0442_\u041b\u0420" + str(num) + ".docx")
with open(content, encoding="utf-8-sig") as f:
    c = json.load(f)
make_docx.build(out, num, THEMES[num], c, lab)

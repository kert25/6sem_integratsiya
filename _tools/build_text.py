# -*- coding: utf-8 -*-
"""Собирает конспект text.docx по content_text.json без титульного листа."""
import json
import sys
from pathlib import Path

THEMES = {
    7: "Интеграционное тестирование веб-приложения в Docker-окружении",
}

root = Path(sys.argv[1])
number = int(sys.argv[2])
lab = root / f"ЛР{number}"
sys.path.insert(0, str(root / "_tools"))
import make_docx

content = json.loads((lab / "content_text.json").read_text(encoding="utf-8"))
make_docx.build(lab / "text.docx", number, THEMES[number], content, lab, title=False)

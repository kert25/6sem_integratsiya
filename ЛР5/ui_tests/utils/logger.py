# -*- coding: utf-8 -*-
"""Логирование UI-тестов: консоль + файл logs/ui_tests.log."""
import logging
import os
import sys


def setup_logger(level=logging.INFO):
    """Настройка корневого логгера: вывод в консоль и в файл."""
    os.makedirs("logs", exist_ok=True)

    root = logging.getLogger()
    if root.handlers:
        return root

    root.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    root.addHandler(console)

    file_handler = logging.FileHandler(
        os.path.join("logs", "ui_tests.log"), encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    root.info("Логирование настроено")
    return root

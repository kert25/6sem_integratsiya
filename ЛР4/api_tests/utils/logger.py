# -*- coding: utf-8 -*-
"""Настройка логирования тестового фреймворка."""
import logging
import sys

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Инициализация корневого логгера с выводом в stdout."""
    root = logging.getLogger()
    if root.handlers:
        return root
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(handler)
    root.setLevel(level)
    # urllib3 очень болтлив на INFO — глушим до WARNING
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    return root

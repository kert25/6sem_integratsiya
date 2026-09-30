# -*- coding: utf-8 -*-
"""Тестовые данные (вариант 9 — the-internet.herokuapp.com)."""


class TestData:
    """Данные для UI-тестов разделов Geolocation, Inputs, Notification Messages."""

    BASE_URL = "https://the-internet.herokuapp.com"

    # Inputs
    INPUT_NUMBER = "42"
    DECIMAL_NUMBER = "3.14"
    NEGATIVE_NUMBER = "-5"
    NON_NUMERIC_INPUT = "abc"

    # Notification Messages (тексты flash-сообщений сайта; «unsuccesful» —
    # опечатка на самом the-internet.herokuapp.com)
    NOTIFICATION_TEXTS = (
        "Action successful",
        "Action unsuccesful, please try again",
    )

    # Geolocation (стаб-координаты, подменяющие navigator.geolocation):
    # Москва, Кремль
    MOCK_LATITUDE = 55.75
    MOCK_LONGITUDE = 37.6167

# -*- coding: utf-8 -*-
"""ЛР3, вариант 9: тесты функции get_recommendations («Система рекомендации фильмов»).

Тест-кейсы TC-REC-01..26 спроектированы по техникам EP, BVA и таблица решений
(см. отчёт). Тесты фиксируют ожидаемое поведение ПО СПЕЦИФИКАЦИИ задания;
падение теста означает найденный дефект исходного кода (DEF-01..04 в отчёте).

Базовая генерация фильмов: по 3 фильма на жанр (i = 0, 1, 2),
рейтинги 7.5 / 7.8 / 8.1.
"""
import pytest

from recommendation_system import get_recommendations


def genres_of(result):
    return {m["genre"] for m in result}


def count_genre(result, genre):
    return sum(1 for m in result if m["genre"] == genre)


# TC-REC-01: базовый сценарий — взрослый, 2 жанра, без смягчающих правил
def test_base_case():
    result = get_recommendations(30, ["comedy", "action"], 10, 7.0, False)
    assert isinstance(result, list)
    assert len(result) == 6
    assert genres_of(result) == {"comedy", "action"}


# TC-REC-02: R1 — возраст < 12 исключает жанр horror
def test_child_horror_excluded():
    result = get_recommendations(8, ["horror", "comedy"], 10, 7.0, False)
    assert "horror" not in genres_of(result)
    assert count_genre(result, "comedy") == 3


# TC-REC-03: BVA правила R1 — граница возраста 11/12
@pytest.mark.parametrize("age,horror_expected", [(11, False), (12, True)],
                         ids=["age-11", "age-12"])
def test_horror_age_boundary(age, horror_expected):
    result = get_recommendations(age, ["horror", "comedy"], 10, 7.0, False)
    assert ("horror" in genres_of(result)) is horror_expected


# TC-REC-04: R2 — возраст > 60 даёт +20% приоритета drama (3 * 1.2 = 3.6 -> 4)
def test_senior_drama_boost():
    result = get_recommendations(65, ["drama"], 10, 7.0, False)
    assert len(result) == 4


# TC-REC-05: BVA правила R2 — граница возраста 60/61
@pytest.mark.parametrize("age,expected_count", [(60, 3), (61, 4)],
                         ids=["age-60", "age-61"])
def test_drama_boost_boundary(age, expected_count):
    result = get_recommendations(age, ["drama"], 10, 7.0, False)
    assert len(result) == expected_count


# TC-REC-06: BVA правила R3 — граница watched_recently 20/21 (снижение на 30%)
@pytest.mark.parametrize("watched,expected_count", [(20, 3), (21, 2)],
                         ids=["watched-20", "watched-21"])
def test_viewed_reduction_boundary(watched, expected_count):
    result = get_recommendations(30, ["comedy"], watched, 7.0, False)
    assert len(result) == expected_count


# TC-REC-07: BVA диапазона watched_recently 0–50 — обе границы валидны
@pytest.mark.parametrize("watched,expected_count", [(0, 3), (50, 2)],
                         ids=["watched-0", "watched-50"])
def test_viewed_range_bounds(watched, expected_count):
    result = get_recommendations(30, ["comedy"], watched, 7.0, False)
    assert len(result) == expected_count


# TC-REC-08: R4 — rating_preference > 8.5: строгий фильтр (в базе нет фильмов >= 8.5)
def test_strict_filter_high_pref():
    result = get_recommendations(30, ["comedy"], 10, 9.0, False)
    assert result == []


# TC-REC-09: BVA правила R4 — граница rating_preference 8.5/8.6
@pytest.mark.parametrize("pref,expected_count", [(8.5, 3), (8.6, 0)],
                         ids=["pref-8.5", "pref-8.6"])
def test_rating_filter_boundary(pref, expected_count):
    result = get_recommendations(30, ["comedy"], 10, pref, False)
    assert len(result) == expected_count


# TC-REC-10: R4 — при pref <= 8.5 строгого фильтра быть не должно
def test_moderate_pref_no_strict_filter():
    result = get_recommendations(30, ["comedy", "action"], 10, 8.0, False)
    assert len(result) == 6


# TC-REC-11: нижняя граница rating_preference = 0 (без фильтра)
def test_pref_zero_all_movies():
    result = get_recommendations(30, ["comedy", "action"], 10, 0.0, False)
    assert len(result) == 6


# TC-REC-12: верхняя граница rating_preference = 10 (строгий фильтр)
def test_pref_upper_bound():
    result = get_recommendations(30, ["comedy"], 10, 10.0, False)
    assert result == []


# TC-REC-13: R5 — is_premium добавляет 2 рекомендации premium (6 + 2 = 8)
def test_premium_adds_two():
    result = get_recommendations(30, ["comedy", "action"], 10, 7.0, True)
    assert len(result) == 8
    assert count_genre(result, "premium") == 2


# TC-REC-14: R5 + R6 — премиум ДОПОЛНИТЕЛЬНЫЕ, не отсекаются лимитом 10
def test_premium_not_cut_by_cap():
    result = get_recommendations(30, ["comedy", "action", "drama", "sci-fi"],
                                 10, 7.0, True)
    assert count_genre(result, "premium") == 2


# TC-REC-15: R6 — базовый лимит: не более 10 фильмов
def test_base_cap_ten():
    result = get_recommendations(30, ["comedy", "action", "drama", "sci-fi"],
                                 10, 7.0, False)
    assert len(result) == 10


# TC-REC-16: комбинация R1 + R3 (ребёнок + много просмотренного)
def test_child_heavy_watcher():
    result = get_recommendations(8, ["horror", "comedy"], 25, 7.0, False)
    assert "horror" not in genres_of(result)
    assert len(result) == 2  # comedy: 3 * 0.7 = 2.1 -> 2


# TC-REC-17: комбинация R2 + R3 (старший + много просмотренного)
def test_senior_heavy_watcher():
    result = get_recommendations(65, ["drama"], 25, 7.0, False)
    assert len(result) == 2  # 3 * 1.2 * 0.7 = 2.52 -> 2


# TC-REC-18..25: негативные сценарии — невалидные входные данные отвергаются
@pytest.mark.parametrize("args", [
    (-1, ["comedy"], 10, 7.0, False),      # TC-REC-18: age < 0
    (121, ["comedy"], 10, 7.0, False),     # TC-REC-19: age > 120
    (30, ["comedy"], -1, 7.0, False),      # TC-REC-20: watched_recently < 0
    (30, ["comedy"], 51, 7.0, False),      # TC-REC-21: watched_recently > 50
    (30, ["comedy"], 10, -0.5, False),     # TC-REC-22: rating_preference < 0
    (30, ["comedy"], 10, 10.5, False),     # TC-REC-23: rating_preference > 10
    (30, ["documentary"], 10, 7.0, False), # TC-REC-24: несуществующий жанр
    (30, [], 10, 7.0, False),              # TC-REC-25: пустой список жанров
], ids=["age<0", "age>120", "watched<0", "watched>50",
        "pref<0", "pref>10", "invalid-genre", "empty-genres"])
def test_invalid_input_rejected(args):
    result = get_recommendations(*args)
    assert isinstance(result, str)  # сообщение об ошибке, а не список


# TC-REC-26: BVA диапазона возраста 0–120 — валидные крайние значения
@pytest.mark.parametrize("age", [0, 120], ids=["age-0", "age-120"])
def test_age_range_bounds(age):
    result = get_recommendations(age, ["comedy"], 10, 7.0, False)
    assert len(result) == 3

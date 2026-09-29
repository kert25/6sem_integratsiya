# -*- coding: utf-8 -*-
"""Вариант 9: Система рекомендации фильмов (ЛР3).

Алгоритм подбора фильмов на основе предпочтений пользователя и истории
просмотров. Исходный код модуля взят из индивидуального задания (репозиторий
преподавателя, lab3/option9.md) и содержит преднамеренные ошибки, которые
требуется выявить тестированием.
"""


def get_recommendations(age, favorite_genres, watched_recently, rating_preference, is_premium):
    recommendations = []
    genre_weights = {genre: 1.0 for genre in favorite_genres}

    if age < 12:
        if "horror" in genre_weights:
            del genre_weights["horror"]

    if age > 60:
        if "drama" in genre_weights:
            genre_weights["drama"] *= 1.2

    view_factor = 1.0
    if watched_recently > 20:
        view_factor = 0.7

    for genre, weight in genre_weights.items():
        for i in range(int(3 * weight * view_factor)):
            movie = {
                "title": f"{genre} movie {i}",
                "rating": 7.5 + (i * 0.3),
                "genre": genre,
                "is_premium": i % 3 == 0
            }

            if movie["rating"] >= rating_preference:
                recommendations.append(movie)

    if is_premium:
        for i in range(2):
            recommendations.append({
                "title": f"Premium exclusive {i}",
                "rating": 9.0,
                "genre": "premium",
                "is_premium": True
            })

    return recommendations[:10]

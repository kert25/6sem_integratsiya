# -*- coding: utf-8 -*-
"""
Pydantic-схемы для валидации ответов API (pydantic 2.x)
"""
from typing import List, Optional
from pydantic import BaseModel, field_validator
from datetime import datetime


class Task(BaseModel):
    """Схема задачи"""
    id: int
    title: str
    completed: bool
    userId: int
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    @field_validator('createdAt', 'updatedAt')
    @classmethod
    def validate_datetime(cls, v):
        if v:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Invalid datetime format')
        return v


class TaskList(BaseModel):
    """Схема списка задач"""
    tasks: List[Task]
    count: int


class DeleteTaskResponse(BaseModel):
    """Схема ответа на удаление задачи"""
    message: str
    task: Task


class User(BaseModel):
    """Схема пользователя"""
    id: int
    email: str
    name: str
    registeredAt: Optional[str] = None


class AuthResponse(BaseModel):
    """Схема ответа на аутентификацию"""
    token: str
    user: User


class RegisterResponse(BaseModel):
    """Схема ответа на регистрацию"""
    message: str
    userId: int


class ErrorResponse(BaseModel):
    """Схема ошибки"""
    error: str


class Product(BaseModel):
    """Схема товара"""
    id: int
    name: str
    price: float
    category: str
    stock: int


class ProductList(BaseModel):
    """Схема списка товаров"""
    products: List[Product]
    count: int

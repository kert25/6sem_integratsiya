"""
Тесты для страницы задач
"""
import pytest
import time
from selenium.webdriver.common.keys import Keys
from pages.tasks_page import TasksPage
from data.test_data import TestData


class TestTasks:
    """Тесты управления задачами"""
    
    def test_create_task(self, logged_in_tasks_page):
        """Тест создания задачи"""
        initial_count = logged_in_tasks_page.get_task_count()
        
        # Создаем новую задачу
        task_text = "Новая тестовая задача"
        logged_in_tasks_page.create_task(task_text)
        
        # Проверяем увеличение счетчика
        new_count = logged_in_tasks_page.get_task_count()
        assert new_count == initial_count + 1, "Счетчик задач не увеличился"
        
        # Проверяем, что задача добавлена в список
        task_texts = logged_in_tasks_page.get_task_texts()
        assert task_text in task_texts, "Задача не отображается в списке"
    
    def test_create_empty_task(self, logged_in_tasks_page):
        """Тест создания пустой задачи"""
        initial_count = logged_in_tasks_page.get_task_count()
        
        # Пытаемся создать задачу без текста
        logged_in_tasks_page.create_task("")
        
        # Проверяем, что счетчик не изменился
        new_count = logged_in_tasks_page.get_task_count()
        assert new_count == initial_count, "Пустая задача была создана"
    
    def test_create_task_with_special_characters(self, logged_in_tasks_page):
        """Тест создания задачи со специальными символами"""
        task_texts = [
            "Задача с символами: !@#$%^&*()",
            "Задача с эмодзи 😊",
            "Задача с HTML: <script>alert('test')</script>",
            "Очень длинная задача " * 10,
        ]
        
        for task_text in task_texts:
            logged_in_tasks_page.create_task(task_text)
            
            # Проверяем, что задача добавлена
            assert task_text in logged_in_tasks_page.get_task_texts()
            
            # Удаляем задачу для чистоты теста
            logged_in_tasks_page.delete_task(task_text)
    
    def test_complete_task(self, logged_in_tasks_page, test_task):
        """Тест отметки задачи как выполненной"""
        # Отмечаем задачу как выполненную
        logged_in_tasks_page.complete_task(test_task)
        
        # Проверяем, что задача отмечена как выполненная
        assert logged_in_tasks_page.is_task_completed(test_task), \
            "Задача не отмечена как выполненная"
        
        # Проверяем стиль выполненной задачи (если есть)
        # Может быть зачеркивание или другой CSS класс
    
    def test_delete_task(self, logged_in_tasks_page):
        """Тест удаления задачи"""
        # Создаем задачу для удаления
        task_text = "Задача для удаления"
        logged_in_tasks_page.create_task(task_text)
        
        initial_count = logged_in_tasks_page.get_task_count()
        
        # Удаляем задачу
        logged_in_tasks_page.delete_task(task_text)
        
        # Проверяем уменьшение счетчика
        new_count = logged_in_tasks_page.get_task_count()
        assert new_count == initial_count - 1, "Счетчик задач не уменьшился"
        
        # Проверяем, что задачи нет в списке
        assert task_text not in logged_in_tasks_page.get_task_texts()
    
    def test_edit_task(self, logged_in_tasks_page, test_task):
        """Тест редактирования задачи"""
        new_text = "Отредактированная задача"
        
        # Редактируем задачу
        logged_in_tasks_page.edit_task(test_task, new_text)
        
        # Проверяем, что старая задача заменена новой
        task_texts = logged_in_tasks_page.get_task_texts()
        assert test_task not in task_texts, "Старая задача осталась в списке"
        assert new_text in task_texts, "Новая задача не отображается"
    
    @pytest.mark.parametrize("filter_type", ["all", "active", "completed"])
    def test_filter_tasks(self, logged_in_tasks_page, filter_type):
        """Тест фильтрации задач"""
        # Создаем несколько задач
        tasks = ["Задача 1", "Задача 2", "Задача 3"]
        for task in tasks:
            logged_in_tasks_page.create_task(task)
        
        # Отмечаем некоторые задачи как выполненные
        logged_in_tasks_page.complete_task("Задача 2")
        
        # Применяем фильтр
        logged_in_tasks_page.filter_tasks(filter_type)
        
        # Проверяем отображение задач в зависимости от фильтра
        visible_tasks = logged_in_tasks_page.get_task_texts()
        
        if filter_type == "active":
            assert "Задача 2" not in visible_tasks, "Выполненная задача отображается в активных"
            assert "Задача 1" in visible_tasks, "Активная задача не отображается"
        
        elif filter_type == "completed":
            assert "Задача 2" in visible_tasks, "Выполненная задача не отображается"
            assert "Задача 1" not in visible_tasks, "Активная задача отображается в выполненных"
    
    def test_clear_completed_tasks(self, logged_in_tasks_page):
        """Тест очистки выполненных задач"""
        # Создаем и выполняем несколько задач
        tasks_to_complete = ["Задача A", "Задача B"]
        tasks_active = ["Задача C", "Задача D"]
        
        all_tasks = tasks_to_complete + tasks_active
        
        for task in all_tasks:
            logged_in_tasks_page.create_task(task)
        
        for task in tasks_to_complete:
            logged_in_tasks_page.complete_task(task)
        
        # Очищаем выполненные задачи
        logged_in_tasks_page.clear_completed_tasks()
        
        # Проверяем, что выполненные задачи удалены
        remaining_tasks = logged_in_tasks_page.get_task_texts()
        
        for task in tasks_to_complete:
            assert task not in remaining_tasks, f"Выполненная задача '{task}' не удалена"
        
        for task in tasks_active:
            assert task in remaining_tasks, f"Активная задача '{task}' удалена"
    
    def test_task_counter(self, logged_in_tasks_page):
        """Тест счетчика задач"""
        # Очищаем все задачи
        while logged_in_tasks_page.get_task_count() > 0:
            tasks = logged_in_tasks_page.get_task_texts()
            if tasks:
                logged_in_tasks_page.delete_task(tasks[0])
        
        # Создаем несколько задач
        tasks_count = 3
        for i in range(tasks_count):
            logged_in_tasks_page.create_task(f"Задача {i}")
        
        # Проверяем счетчик
        counter_text = logged_in_tasks_page.get_task_counter_text()
        assert str(tasks_count) in counter_text, f"Счетчик не показывает {tasks_count} задач"
        
        # Отмечаем одну задачу как выполненную
        logged_in_tasks_page.complete_task("Задача 0")
        
        # Проверяем обновление счетчика
        new_counter_text = logged_in_tasks_page.get_task_counter_text()
        assert str(tasks_count - 1) in new_counter_text, "Счетчик не обновился после выполнения задачи"
    
    def test_no_tasks_message(self, logged_in_tasks_page):
        """Тест сообщения 'Нет задач'"""
        # Удаляем все задачи
        while logged_in_tasks_page.get_task_count() > 0:
            tasks = logged_in_tasks_page.get_task_texts()
            if tasks:
                logged_in_tasks_page.delete_task(tasks[0])
        
        # Проверяем сообщение
        assert logged_in_tasks_page.is_no_tasks_message_displayed(), \
            "Сообщение 'Нет задач' не отображается"
    
    @pytest.mark.integration
    def test_task_persistence_after_refresh(self, logged_in_tasks_page):
        """Тест сохранения задач после обновления страницы"""
        # Создаем задачу
        task_text = "Задача для проверки персистентности"
        logged_in_tasks_page.create_task(task_text)
        
        # Обновляем страницу
        logged_in_tasks_page.driver.refresh()
        
        # Проверяем, что задача сохранилась
        assert task_text in logged_in_tasks_page.get_task_texts(), \
            "Задача не сохранилась после обновления страницы"
    
    @pytest.mark.slow
    def test_performance_with_many_tasks(self, logged_in_tasks_page):
        """Тест производительности с большим количеством задач"""
        start_time = time.time()
        
        # Создаем много задач
        num_tasks = 50
        for i in range(num_tasks):
            logged_in_tasks_page.create_task(f"Задача производительности {i}")
        
        creation_time = time.time() - start_time
        
        # Проверяем, что создание не занимает слишком много времени
        assert creation_time < 30, f"Создание {num_tasks} задач заняло {creation_time} секунд"
        
        # Проверяем отображение всех задач
        assert logged_in_tasks_page.get_task_count() == num_tasks, \
            f"Создано {logged_in_tasks_page.get_task_count()} задач вместо {num_tasks}"
